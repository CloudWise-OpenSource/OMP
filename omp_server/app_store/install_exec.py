"""
安装执行器
前提：所有的公共组件都由OMP进行安装处理
目标：根据数据库中给出的安装记录进行服务安装
"""
import os
import time
import queue
import logging
from concurrent.futures import (
    ThreadPoolExecutor, as_completed
)
from django.db.models import F

from db_models.models import (
    Host, Service, HostOperateLog, ServiceHistory,
    MainInstallHistory, DetailInstallHistory, ApplicationHub
)
from utils.plugin.salt_client import SaltClient
from utils.parse_config import BASIC_ORDER
from utils.parse_config import THREAD_POOL_MAX_WORKERS
from utils.common.exceptions import GeneralError

UNZIP_CONCURRENT_ONE_HOST = 3
logger = logging.getLogger("server")


class InstallServiceExecutor:
    """ 安装服务执行器 """
    ACTION_LS = ("send", "unzip", "install", "init", "start")

    def __init__(self, main_id, username, timeout=300):
        self.main_id = main_id
        self.username = username
        self.timeout = timeout
        # 安装中是否发生错误，用于流程控制
        self.is_error = False
        # 控制安装过程中单主机上的安装包解压并发数 TODO 暂时使用阻塞等待方式进行处理！！
        self.unzip_concurrent_controller = dict()

    @staticmethod
    def now_time():
        """ 当前时间格式 """
        return time.strftime(time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime()))

    def create_history(self, detail_obj, is_success=True):
        """ 创建历史记录 """
        target_ip = detail_obj.service.ip
        service_name = detail_obj.service.service_instance_name
        # 写入主机历史记录、服务历史记录
        target_host = Host.objects.filter(ip=target_ip).first()
        HostOperateLog.objects.create(
            username=self.username,
            description=f"安装服务 [{service_name}]",
            result="success" if is_success else "failed",
            host=target_host)
        ServiceHistory.objects.create(
            username=self.username,
            description="安装服务",
            result="success" if is_success else "failed",
            service=detail_obj.service)
        # 主机服务数量+1
        if is_success:
            Host.objects.filter(ip=target_ip).update(
                service_num=F("service_num") + 1)

    def send(self, detail_obj):
        """ 发送服务包 """
        # 获取发送使用参数
        salt_client = SaltClient()
        target_ip = detail_obj.service.ip
        service_name = detail_obj.service.service_instance_name
        package_name = detail_obj.service.service.app_package.package_name

        # 更新状态为 '发送中'，记录日志
        logger.info(f"Send Begin -> [{service_name}] package [{package_name}]")
        detail_obj.send_flag = 1
        detail_obj.send_msg += f"{self.now_time()} {service_name} 开始发送服务包\n"
        detail_obj.save()

        try:
            # 获取目标路径
            target_host = Host.objects.filter(ip=target_ip).first()
            assert target_host is not None

            # 获取 json 文件路径
            json_source_path = os.path.join(
                "data_files",
                f"{detail_obj.main_install_history.operation_uuid}.json")
            json_target_path = os.path.join(
                target_host.data_folder, "omp_packages",
                f"{detail_obj.main_install_history.operation_uuid}.json")

            # 发送 json 文件
            is_success, message = salt_client.cp_file(
                target=target_ip,
                source_path=json_source_path,
                target_path=json_target_path)
            if not is_success:
                raise GeneralError(f"发送 json 文件失败: {message}")

            # 获取服务包路径
            source_path = os.path.join(
                detail_obj.service.service.app_package.package_path,
                package_name)
            target_path = os.path.join(
                target_host.data_folder, "omp_packages",
                package_name)

            # 发送服务包
            is_success, message = salt_client.cp_file(
                target=target_ip,
                source_path=source_path,
                target_path=target_path)
            if not is_success:
                raise GeneralError(message)

        except Exception as err:
            logger.error(f"Send Failed -> [{service_name}]: {err}")
            detail_obj.send_flag = 3
            detail_obj.send_msg += f"{self.now_time()} {service_name} " \
                                   f"发送服务包失败: {err}\n"
            detail_obj.install_step_status = \
                DetailInstallHistory.INSTALL_STATUS_FAILED
            detail_obj.save()
            detail_obj.service.service_status = \
                Service.SERVICE_STATUS_INSTALL_FAILED
            detail_obj.service.save()
            # 创建历史记录
            self.create_history(detail_obj, is_success=False)
            return False, err
        # 发送成功
        logger.info(
            f"Send Success -> [{service_name}] package [{package_name}]")
        detail_obj.send_flag = 2
        detail_obj.send_msg += f"{self.now_time()} {service_name} 成功发送服务包\n"
        detail_obj.save()
        return True, "Send Success"

    def unzip(self, detail_obj):
        """ 解压服务包 """
        # 获取解压使用参数
        target_ip = detail_obj.service.ip
        service_name = detail_obj.service.service_instance_name
        package_name = detail_obj.service.service.app_package.package_name
        salt_client = SaltClient()

        # 更新状态为 '解压中'，记录日志
        logger.info(
            f"Unzip Begin -> [{service_name}] package [{package_name}]")
        detail_obj.unzip_flag = 1
        detail_obj.unzip_msg += f"{self.now_time()} {service_name} 开始解压服务包\n"
        detail_obj.save()

        try:
            # 控制单主机上的服务包解压操作，向控制队列中添加一项
            # 如果能加入成功则继续，否则等待其加入成功
            self.unzip_concurrent_controller[target_ip].put(service_name)
            # 解析获取目录
            target_host = Host.objects.filter(ip=target_ip).first()
            assert target_host is not None
            package_path = os.path.join(
                target_host.data_folder, "omp_packages",
                package_name)
            # 获取解压目标路径
            detail_args = detail_obj.install_detail_args
            assert detail_args is not None
            app_name = detail_args.get("name", None)
            assert app_name is not None
            target_path = None
            for info in detail_args.get("install_args", []):
                if info.get("key", "") == "base_dir":
                    target_path = info.get("default")
                    break
            if target_path is None:
                raise GeneralError("未获取到解压目标路径")
            # 切分判断路径
            path_ls = os.path.split(target_path)
            # 创建服务目录，解压服务包
            if path_ls[1] == app_name:
                _target_path = path_ls[0]
                test_path_cmd_str = f"(test -d {_target_path} || mkdir -p {_target_path}) && " \
                                    f"tar -xf {package_path} -C {_target_path}"
            else:
                # 当路径结尾与服务名不一致时
                _target_path = path_ls[0]
                real_path = os.path.join(_target_path, app_name)
                test_path_cmd_str = f"(test -d {_target_path} || mkdir -p {_target_path}) && " \
                                    f"tar -xf {package_path} -C {_target_path} && mv {real_path} {target_path}/"
            is_success, message = salt_client.cmd(
                target=target_ip,
                command=test_path_cmd_str,
                timeout=self.timeout)
            if not is_success:
                raise GeneralError(message)

        except Exception as err:
            # 解压流程运行完成后报错，释放资源
            self.unzip_concurrent_controller[target_ip].get()
            logger.error(f"Unzip Failed -> [{service_name}]: {err}")
            detail_obj.unzip_flag = 3
            detail_obj.unzip_msg += \
                f"{self.now_time()} {service_name} " \
                f"解压服务包失败: {err}\n"
            detail_obj.install_step_status = \
                DetailInstallHistory.INSTALL_STATUS_FAILED
            detail_obj.save()
            detail_obj.service.service_status = \
                Service.SERVICE_STATUS_INSTALL_FAILED
            detail_obj.service.save()
            # 创建历史记录
            self.create_history(detail_obj, is_success=False)
            return False, err
        # 解压流程运行完成后报错，释放资源
        self.unzip_concurrent_controller[target_ip].get()
        # 解压成功
        logger.info(
            f"Unzip Success -> [{service_name}] package [{package_name}]")
        detail_obj.unzip_flag = 2
        detail_obj.unzip_msg += \
            f"{self.now_time()} {service_name} 成功解压服务包\n"
        detail_obj.save()
        return True, "Unzip Success"

    def install(self, detail_obj):
        """ 安装服务 """
        # 获取安装使用参数
        salt_client = SaltClient()
        target_ip = detail_obj.service.ip
        service_name = detail_obj.service.service_instance_name
        # edit by jon.liu service_controllers 为json字段，无需json.loads
        service_controllers_dict = detail_obj.service.service_controllers

        # 更新状态为 '安装中'，记录日志
        logger.info(f"Install Begin -> [{service_name}]")
        detail_obj.install_flag = 1
        detail_obj.install_msg += \
            f"{self.now_time()} {service_name} 开始安装服务\n"
        detail_obj.save()

        try:
            # 获取服务安装脚本绝对路径
            install_script_path = service_controllers_dict.get("install", "")
            if install_script_path == "":
                raise GeneralError("未找到安装脚本路径")

            # 获取 json 文件路径
            target_host = Host.objects.filter(ip=target_ip).first()
            assert target_host is not None
            json_path = os.path.join(
                target_host.data_folder, "omp_packages",
                f"{detail_obj.main_install_history.operation_uuid}.json")

            cmd_str = f"python {install_script_path} --local_ip {target_ip} " \
                      f"--data_json {json_path}"

            # 执行安装
            is_success, message = salt_client.cmd(
                target=target_ip,
                command=cmd_str,
                timeout=self.timeout)
            if not is_success:
                raise GeneralError(message)
            # 执行成功且 message 有值，则补充至服务日志中
            if is_success and bool(message):
                detail_obj.install_msg += \
                    f"{self.now_time()} 安装脚本执行成功，脚本输出如下:\n" \
                    f"{message}\n"
                detail_obj.save()
        except Exception as err:
            logger.error(f"Install Failed -> [{service_name}]: {err}")
            detail_obj.install_flag = 3
            detail_obj.install_msg += f"{self.now_time()} {service_name} " \
                                      f"安装服务失败: {err}\n"
            detail_obj.install_step_status = \
                DetailInstallHistory.INSTALL_STATUS_FAILED
            detail_obj.save()
            detail_obj.service.service_status = \
                Service.SERVICE_STATUS_INSTALL_FAILED
            detail_obj.service.save()
            # 创建历史记录
            self.create_history(detail_obj, is_success=False)
            return False, err
        # 安装成功
        logger.info(f"Install Success -> [{service_name}]")
        detail_obj.install_flag = 2
        detail_obj.install_msg += \
            f"{self.now_time()} {service_name} 成功安装服务\n"
        detail_obj.save()
        return True, "Install Success"

    def init(self, detail_obj):
        """ 初始化服务 """
        # 获取初始化使用参数
        salt_client = SaltClient()
        target_ip = detail_obj.service.ip
        service_name = detail_obj.service.service_instance_name
        service_controllers_dict = detail_obj.service.service_controllers

        # 更新状态为 '初始化中'，记录日志
        logger.info(f"Init Begin -> [{service_name}]")
        detail_obj.init_flag = 1
        detail_obj.init_msg += f"{self.now_time()} {service_name} 开始初始化服务\n"
        detail_obj.save()

        try:
            # 获取服务初始化脚本绝对路径
            init_script_path = service_controllers_dict.get("init", "")
            if init_script_path == "":
                logger.info(f"Init Un Do -> [{service_name}]")
                detail_obj.init_flag = 2
                detail_obj.init_msg += \
                    f"{self.now_time()} {service_name} 无需执行初始化\n"
                # 完成安装流程，更新状态为 '安装成功'
                detail_obj.install_step_status = \
                    DetailInstallHistory.INSTALL_STATUS_SUCCESS
                detail_obj.save()
                # 创建历史记录
                self.create_history(detail_obj, is_success=True)
                return True, "Init Un Do"

            # 获取 json 文件路径
            target_host = Host.objects.filter(ip=target_ip).first()
            assert target_host is not None
            json_path = os.path.join(
                target_host.data_folder, "omp_packages",
                f"{detail_obj.main_install_history.operation_uuid}.json")

            cmd_str = f"python {init_script_path} --local_ip {target_ip} " \
                      f"--data_json {json_path}"
            # 执行初始化
            is_success, message = salt_client.cmd(
                target=target_ip,
                command=cmd_str,
                timeout=self.timeout)
            if not is_success:
                raise GeneralError(message)
            # 执行成功且 message 有值，则补充至服务日志中
            if is_success and bool(message):
                detail_obj.install_msg += \
                    f"{self.now_time()} 初始化脚本执行成功，脚本输出如下:\n" \
                    f"{message}\n"
                detail_obj.save()
        except Exception as err:
            logger.error(f"Init Failed -> [{service_name}]: {err}")
            detail_obj.init_flag = 3
            detail_obj.init_msg += f"{self.now_time()} {service_name} " \
                                   f"初始化服务失败: {err}\n"
            # 更新安装流程状态为 '失败'，服务状态为 '安装失败'
            detail_obj.install_step_status = \
                DetailInstallHistory.INSTALL_STATUS_FAILED
            detail_obj.save()
            detail_obj.service.service_status = \
                Service.SERVICE_STATUS_INSTALL_FAILED
            detail_obj.service.save()
            # 创建历史记录
            self.create_history(detail_obj, is_success=False)
            return False, err
        # 安装成功
        logger.info(f"Init Success -> [{service_name}]")
        detail_obj.init_flag = 2
        detail_obj.init_msg += f"{self.now_time()} {service_name} 成功初始化服务\n"
        # 完成安装流程，更新状态为 '安装成功'
        # 如果是自研服务，初始化完成即认为其安装成功
        if detail_obj.service.service.app_type == \
                ApplicationHub.APP_TYPE_SERVICE:
            detail_obj.install_step_status = \
                DetailInstallHistory.INSTALL_STATUS_SUCCESS
            detail_obj.save()
        # 创建历史记录
        self.create_history(detail_obj, is_success=True)
        return True, "Init Success"

    def start(self, detail_obj):
        """ 启动服务 """
        # 获取启动使用参数
        salt_client = SaltClient()
        target_ip = detail_obj.service.ip
        service_name = detail_obj.service.service_instance_name
        service_controllers_dict = detail_obj.service.service_controllers

        # 更新状态为 '启动中'，记录日志
        logger.info(f"Start Begin -> [{service_name}]")
        detail_obj.start_flag = 1
        detail_obj.start_msg += f"{self.now_time()} {service_name} 开始启动服务\n"
        detail_obj.save()

        try:
            # 获取服务启动脚本绝对路径
            start_script_path = service_controllers_dict.get("start", "")
            if start_script_path == "":
                logger.info(f"Start Un Do -> [{service_name}]")
                detail_obj.start_flag = 2
                detail_obj.start_msg += \
                    f"{self.now_time()} {service_name} 无需执行启动\n"
                # 如果服务无需启动，则认可其为安装成功
                detail_obj.install_step_status = \
                    DetailInstallHistory.INSTALL_STATUS_SUCCESS
                # 服务状态更新为 '正常'
                detail_obj.service.service_status = \
                    Service.SERVICE_STATUS_NORMAL
                detail_obj.service.save()
                detail_obj.save()
                return True, "Start Un Do"

            cmd_str = f"bash {start_script_path} start"

            # 执行启动
            is_success, message = salt_client.cmd(
                target=target_ip,
                command=cmd_str,
                timeout=self.timeout)
            if not is_success:
                raise GeneralError(message)
            result_str = message.upper()
            if "FAILED" in result_str or \
                    "NO RUNNING" in result_str or \
                    "NOT RUNNING" in result_str:
                raise GeneralError(message)
            # 执行成功且 message 有值，则补充至服务日志中
            if is_success and bool(message):
                detail_obj.install_msg += \
                    f"{self.now_time()} 启动脚本执行成功，脚本输出如下:\n" \
                    f"{message}\n"
                detail_obj.save()
        except Exception as err:
            logger.error(f"Start Failed -> [{service_name}]: {err}")
            detail_obj.start_flag = 3
            detail_obj.start_msg += f"{self.now_time()} {service_name} " \
                                    f"启动服务失败: {err}\n"
            # 如果是基础组件服务的启动步骤，如果启动失败则认为其启动失败
            if detail_obj.service.service.app_type == \
                    ApplicationHub.APP_TYPE_COMPONENT:
                detail_obj.install_step_status = \
                    DetailInstallHistory.INSTALL_STATUS_FAILED
            detail_obj.save()
            # 服务状态更新为 '停止'
            detail_obj.service.service_status = \
                Service.SERVICE_STATUS_STOP
            detail_obj.service.save()
            return False, err
        # 安装成功
        logger.info(f"Start Success -> [{service_name}]")
        detail_obj.start_flag = 2
        detail_obj.start_msg += f"{self.now_time()} {service_name} 成功启动服务\n"
        detail_obj.save()
        # 服务状态更新为 '正常'
        detail_obj.service.service_status = \
            Service.SERVICE_STATUS_NORMAL
        # 服务启动成功，则认为其已经安装成功
        detail_obj.install_step_status = \
            DetailInstallHistory.INSTALL_STATUS_SUCCESS
        detail_obj.save()
        detail_obj.service.save()
        return True, "Start Success"

    def execute_post_action(self, queryset):    # NOQA
        """
        执行安装后的操作，所有服务安装完成后，针对不同服务的个性化配置执行
        目前仅支持shell脚本方式
        :param queryset: 包含部署详情表的列表
        :type queryset: [DetailInstallHistory]
        :return:
        """
        try:
            salt_client = SaltClient()
            for detail_obj in queryset:
                target_ip = detail_obj.service.ip
                _script = detail_obj.service.service_controllers.get(
                    "post_action")
                flag, msg = salt_client.cmd(
                    target=target_ip,
                    command=f"chmod +x {_script.split()[0]} && {_script}",
                    timeout=60
                )
                logger.info(f"Execute {_script}, flag: {flag}; msg: {msg}")
                detail_obj.post_action_msg += str(msg)
                if not flag:
                    self.is_error = True
                    detail_obj.post_action_flag = 3
                    detail_obj.save()
                    break
                detail_obj.post_action_flag = 2
                detail_obj.save()
        except Exception as e:
            logger.error(f"Error while execute post_action: {str(e)}")
            self.is_error = True

    def single_service_executor(self, detail_obj):
        """
        单独服务的安装执行器
        :param detail_obj:
        :type detail_obj: DetailInstallHistory
        :return:
        """
        # 针对单个服务执行循环("send", "unzip", "install", "init", "start")
        # 跳过单个服务的已经成功的单个步骤不再重复执行
        for action in self.ACTION_LS:
            if getattr(detail_obj, f"{action}_flag") == 2:
                continue
            _flag, _msg = getattr(self, action)(detail_obj)
            if not _flag:
                return _flag, _msg
        return True, "success"

    def thread_poll_executor(self, detail_obj_lst):
        """
        多线程执行器
        :param detail_obj_lst: [detail_obj, detail_obj]
        :return:
        """
        logger.info(f"Start thread poll executor for {detail_obj_lst}")
        with ThreadPoolExecutor(THREAD_POOL_MAX_WORKERS) as executor:
            _future_list = []
            for detail_obj in detail_obj_lst:
                future_obj = executor.submit(
                    self.single_service_executor, detail_obj
                )
                _future_list.append(future_obj)
            for future in as_completed(_future_list):
                is_success, message = future.result()
                if not is_success:
                    self.is_error = True
                    break
        logger.info("Finish thread poll executor!")

    @staticmethod
    def make_install_order(queryset):
        """
        对所有的安装对象进行排序处理，控制其安装顺序
        :param queryset: 即将部署的详情对象组成的列表
        :return:
        """
        # 安装顺序的二维数组
        execute_lst = list()
        # 对基础组件进行排序处理，其中基础配置中的 BASIC_ORDER 为基础组件的排序等级
        # 如果有其他组件需要安装，怎需要在配置中进行额外的配置
        for i in range(10):
            if i not in BASIC_ORDER:
                break
            _lst = [
                el for el in queryset
                if el.service.service.app_name in BASIC_ORDER[i]
            ]
            execute_lst.append(_lst)
        # 对自研服务进行排序处理，先过滤出自研服务的列表
        _ser = [
            el for el in queryset
            if el.service.service.app_type == ApplicationHub.APP_TYPE_SERVICE
        ]
        # 自研服务level级别为0的服务，仅依赖于基础组件，无其他依赖
        execute_lst.append(
            [
                el for el in _ser if
                str(el.service.service.extend_fields.get("level")) == "0"]
        )
        # 自研服务level级别为1或其他的服务
        # 可依赖基础组件，也可依赖其他自研服务，文件级别位置依赖
        execute_lst.append(
            [
                el for el in _ser if
                str(el.service.service.extend_fields.get("level")) != "0"]
        )
        return execute_lst

    def main(self):
        """ 主函数 """
        logger.info(f"Main Install Begin, id[{self.main_id}]")
        # 获取主表对象，更新状态为 '安装中'
        main_obj = MainInstallHistory.objects.filter(
            id=self.main_id).first()
        assert main_obj is not None
        main_obj.install_status = \
            MainInstallHistory.INSTALL_STATUS_INSTALLING
        main_obj.save()

        # 获取所有安装细节表，排除已经安装成功的记录，不再重复安装
        queryset = DetailInstallHistory.objects.select_related(
            "service", "service__service", "service__service__app_package"
        ).filter(main_install_history_id=self.main_id).exclude(
            install_step_status=DetailInstallHistory.INSTALL_STATUS_SUCCESS)
        # assert queryset.exists()

        # 构建 unzip_concurrent_controller 用于控制解压安装包时单主机的并发数量
        ips = set([el.service.ip for el in queryset])
        self.unzip_concurrent_controller = {
            el: queue.Queue(maxsize=UNZIP_CONCURRENT_ONE_HOST) for el in ips
        }

        # 所有子流程状态更新为 '安装中'
        queryset.update(
            install_step_status=DetailInstallHistory.INSTALL_STATUS_INSTALLING
        )

        # 对要执行安装的列表进行排序处理
        tobe_execute_lst = self.make_install_order(queryset)
        logger.info(f"Tobe_execute_lst: {tobe_execute_lst}")
        for item in tobe_execute_lst:
            if not item:
                continue
            # 根据安装顺序每层并发执行
            self.thread_poll_executor(detail_obj_lst=item)
            # 如果哪层的服务有安装失败的情况，那么直接退出循环
            if self.is_error:
                break

        # 安装后执行动作范围过滤，排除无需执行操作以及排除已经执行成功的服务对象
        # 判断整体执行安装完成后才执行
        if not DetailInstallHistory.objects.filter(
                install_step_status=DetailInstallHistory.INSTALL_STATUS_FAILED,
                main_install_history_id=self.main_id
        ).exists():
            post_action_queryset = DetailInstallHistory.objects.select_related(
                "service", "service__service", "service__service__app_package"
            ).filter(main_install_history_id=self.main_id).exclude(
                post_action_flag__in=[2, 4]
            )
            self.execute_post_action(post_action_queryset)

        if self.is_error:
            # 步骤失败，主流程失败
            main_obj.install_status = \
                MainInstallHistory.INSTALL_STATUS_FAILED
            main_obj.save()
            # 状态为 '待安装'/'安装中' 的记录，则记为 '失败'
            queryset.filter(install_step_status__in=(
                DetailInstallHistory.INSTALL_STATUS_READY,
                DetailInstallHistory.INSTALL_STATUS_INSTALLING
            )).update(
                install_step_status=DetailInstallHistory.INSTALL_STATUS_FAILED
            )
            logger.info(f"Main Install Failed, id[{self.main_id}]")
            return self.is_error

        # 流程执行完整，主流程成功
        main_obj.install_status = \
            MainInstallHistory.INSTALL_STATUS_SUCCESS
        main_obj.save()
        logger.info(f"Main Install Success, id[{self.main_id}]")
        return self.is_error
