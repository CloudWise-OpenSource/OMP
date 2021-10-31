"""
安装执行器
"""
import os
import time
import logging
from concurrent.futures import (
    ThreadPoolExecutor, as_completed
)

from db_models.models import (
    Host, Service,
    MainInstallHistory, DetailInstallHistory
)
from utils.plugin.salt_client import SaltClient
from utils.parse_config import THREAD_POOL_MAX_WORKERS

logger = logging.getLogger("server")


class InstallServiceExecutor:
    """ 安装服务执行器 """
    ACTION_LS = ("send", "unzip", "install", "init", "start")

    def __init__(self, main_id, timeout=300):
        self.main_id = main_id
        self.timeout = timeout
        # 安装中是否发生错误，用于流程控制
        self.is_error = False

    @staticmethod
    def now_time():
        return time.strftime(time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime()))

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
                raise Exception(f"发送 json 文件失败: {message}")

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
                raise Exception(message)

        except Exception as err:
            logger.error(f"Send Failed -> [{service_name}]: {err}")
            detail_obj.send_flag = 3
            detail_obj.send_msg += f"{self.now_time()} {service_name} " \
                                   f"发送服务包失败: {err}\n"
            detail_obj.install_step_status = DetailInstallHistory.INSTALL_STATUS_FAILED
            detail_obj.save()
            detail_obj.service.service_status = Service.SERVICE_STATUS_INSTALL_FAILED
            detail_obj.service.save()
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
        salt_client = SaltClient()
        target_ip = detail_obj.service.ip
        service_name = detail_obj.service.service_instance_name
        package_name = detail_obj.service.service.app_package.package_name

        # 更新状态为 '解压中'，记录日志
        logger.info(
            f"Unzip Begin -> [{service_name}] package [{package_name}]")
        detail_obj.unzip_flag = 1
        detail_obj.unzip_msg += f"{self.now_time()} {service_name} 开始解压服务包\n"
        detail_obj.save()

        try:
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
            for info in detail_args.get("app_install_args", []):
                if info.get("key", "") == "base_dir":
                    target_path = info.get("default")
                    break
            if target_path is None:
                raise Exception("未获取到解压目标路径")
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
                raise Exception(message)

        except Exception as err:
            logger.error(f"Unzip Failed -> [{service_name}]: {err}")
            detail_obj.unzip_flag = 3
            detail_obj.unzip_msg += f"{self.now_time()} {service_name} " \
                                    f"解压服务包失败: {err}\n"
            detail_obj.install_step_status = DetailInstallHistory.INSTALL_STATUS_FAILED
            detail_obj.save()
            detail_obj.service.service_status = Service.SERVICE_STATUS_INSTALL_FAILED
            detail_obj.service.save()
            return False, err
        # 解压成功
        logger.info(
            f"Unzip Success -> [{service_name}] package [{package_name}]")
        detail_obj.unzip_flag = 2
        detail_obj.unzip_msg += f"{self.now_time()} {service_name} 成功解压服务包\n"
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
        detail_obj.install_msg += f"{self.now_time()} {service_name} 开始安装服务\n"
        detail_obj.save()

        try:
            # 获取服务安装脚本绝对路径
            install_script_path = service_controllers_dict.get("install", "")
            if install_script_path == "":
                raise Exception("未找到安装脚本路径")

            # 获取 json 文件路径
            target_host = Host.objects.filter(ip=target_ip).first()
            assert target_host is not None
            json_path = os.path.join(
                target_host.data_folder, "omp_packages",
                f"{detail_obj.main_install_history.operation_uuid}.json")

            cmd_str = f"python {install_script_path} --local_ip {target_ip} --data_json {json_path}"

            # 执行安装
            is_success, message = salt_client.cmd(
                target=target_ip,
                command=cmd_str,
                timeout=self.timeout)
            if not is_success:
                raise Exception(message)
            # 执行成功且 message 有值，则补充至服务日志中
            if is_success and bool(message):
                detail_obj.install_msg += f"{self.now_time()} 安装脚本执行成功，脚本输出如下:\n" \
                                          f"{message}\n"
                detail_obj.save()
        except Exception as err:
            logger.error(f"Install Failed -> [{service_name}]: {err}")
            detail_obj.install_flag = 3
            detail_obj.install_msg += f"{self.now_time()} {service_name} " \
                                      f"安装服务失败: {err}\n"
            detail_obj.install_step_status = DetailInstallHistory.INSTALL_STATUS_FAILED
            detail_obj.save()
            detail_obj.service.service_status = Service.SERVICE_STATUS_INSTALL_FAILED
            detail_obj.service.save()
            return False, err
        # 安装成功
        logger.info(f"Install Success -> [{service_name}]")
        detail_obj.install_flag = 2
        detail_obj.install_msg += f"{self.now_time()} {service_name} 成功安装服务\n"
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
                detail_obj.init_msg += f"{self.now_time()} {service_name} 无需执行初始化\n"
                detail_obj.save()
                return True, "Init Un Do"

            # 获取 json 文件路径
            target_host = Host.objects.filter(ip=target_ip).first()
            assert target_host is not None
            json_path = os.path.join(
                target_host.data_folder, "omp_packages",
                f"{detail_obj.main_install_history.operation_uuid}.json")

            cmd_str = f"python {init_script_path} --local_ip {target_ip} --data_json {json_path}"
            # 执行初始化
            is_success, message = salt_client.cmd(
                target=target_ip,
                command=cmd_str,
                timeout=self.timeout)
            if not is_success:
                raise Exception(message)
            # 执行成功且 message 有值，则补充至服务日志中
            if is_success and bool(message):
                detail_obj.install_msg += f"{self.now_time()} 初始化脚本执行成功，脚本输出如下:\n" \
                                          f"{message}\n"
                detail_obj.save()
        except Exception as err:
            logger.error(f"Init Failed -> [{service_name}]: {err}")
            detail_obj.init_flag = 3
            detail_obj.init_msg += f"{self.now_time()} {service_name} " \
                                   f"初始化服务失败: {err}\n"
            detail_obj.install_step_status = DetailInstallHistory.INSTALL_STATUS_FAILED
            detail_obj.save()
            detail_obj.service.service_status = Service.SERVICE_STATUS_INSTALL_FAILED
            detail_obj.service.save()
            return False, err
        # 安装成功
        logger.info(f"Init Success -> [{service_name}]")
        detail_obj.init_flag = 2
        detail_obj.init_msg += f"{self.now_time()} {service_name} 成功初始化服务\n"
        detail_obj.save()
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
                detail_obj.start_msg += f"{self.now_time()} {service_name} 无需执行启动\n"
                # 完成安装流程，更新状态为 '安装成功'，服务状态为 '正常'
                detail_obj.install_step_status = \
                    DetailInstallHistory.INSTALL_STATUS_SUCCESS
                detail_obj.service.service_status = Service.SERVICE_STATUS_NORMAL
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
                raise Exception(message)
            result_str = message.upper()
            if "FAILED" in result_str or \
                    "NO RUNNING" in result_str or \
                    "NOT RUNNING" in result_str:
                raise Exception(message)
            # 执行成功且 message 有值，则补充至服务日志中
            if is_success and bool(message):
                detail_obj.install_msg += f"{self.now_time()} 启动脚本执行成功，脚本输出如下:\n" \
                                          f"{message}\n"
            detail_obj.save()
        except Exception as err:
            logger.error(f"Start Failed -> [{service_name}]: {err}")
            detail_obj.start_flag = 3
            detail_obj.start_msg += f"{self.now_time()} {service_name} " \
                                    f"启动服务失败: {err}\n"
            detail_obj.install_step_status = DetailInstallHistory.INSTALL_STATUS_FAILED
            detail_obj.save()
            detail_obj.service.service_status = Service.SERVICE_STATUS_INSTALL_FAILED
            detail_obj.service.save()
            return False, err
        # 安装成功
        logger.info(f"Start Success -> [{service_name}]")
        detail_obj.start_flag = 2
        detail_obj.start_msg += f"{self.now_time()} {service_name} 成功启动服务\n"
        # 完成安装流程，更新状态为 '安装成功'，服务状态为 '正常'
        detail_obj.install_step_status = \
            DetailInstallHistory.INSTALL_STATUS_SUCCESS
        detail_obj.service.service_status = Service.SERVICE_STATUS_NORMAL
        detail_obj.service.save()
        detail_obj.save()
        return True, "Start Success"

    @staticmethod
    def _is_base_env(detail_obj):
        """ 是否为依赖项，优先执行 """
        is_base_env = False
        try:
            base_env = detail_obj.service.service.extend_fields.get(
                "base_env", "")
            if isinstance(base_env, str):
                base_env = base_env.lower()
            if base_env in (True, "true"):
                is_base_env = True
        except Exception:
            pass
        return is_base_env

    @staticmethod
    def _is_dependency(detail_obj):
        """ 是否为依赖项，优先执行 """
        return False

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

        # 获取所有安装细节表
        queryset = DetailInstallHistory.objects.select_related(
            "service", "service__service", "service__service__app_package"
        ).filter(main_install_history_id=self.main_id)
        assert queryset.exists()

        # 所有子流程状态更新为 '安装中'
        queryset.update(
            install_step_status=DetailInstallHistory.INSTALL_STATUS_INSTALLING)

        # 区分服务列表切分
        base_env_ls = []
        dependency_ls = []
        no_dependency_ls = []
        for detail_obj in queryset:
            if self._is_base_env(detail_obj):
                base_env_ls.append(detail_obj)
            elif self._is_dependency(detail_obj):
                dependency_ls.append(detail_obj)
            else:
                no_dependency_ls.append(detail_obj)
        logger.info(f"基础环境列表 [base_env_ls] -- {base_env_ls}")
        logger.info(f"含依赖列表 [dependency_ls] -- {dependency_ls}")
        logger.info(f"非依赖列表 [no_dependency_ls] -- {no_dependency_ls}")
        # TODO 含依赖项列表 -> 安装顺序排序？

        # 先执行 base_env 基础环境列表安装流程
        with ThreadPoolExecutor(THREAD_POOL_MAX_WORKERS) as executor:
            logger.info("Begin base_env install")
            for action in self.ACTION_LS:
                # ---- 基础环境列表并发 ----
                _future_list_env = []
                for detail_obj in base_env_ls:
                    future_obj = executor.submit(
                        getattr(self, action), detail_obj)
                    _future_list_env.append(future_obj)
                for future in as_completed(_future_list_env):
                    is_success, message = future.result()
                    if not is_success:
                        self.is_error = True
                        break
            logger.info("End base_env install")

        with ThreadPoolExecutor(THREAD_POOL_MAX_WORKERS) as executor:
            # 轮询流程列表，进行安装
            logger.info("Begin else install")
            for action in self.ACTION_LS:
                logger.info(f"Enter [{action}]")
                # ---- 含依赖项列表轮询 ----
                if self.is_error:
                    break
                for detail_obj in dependency_ls:
                    is_success, message = getattr(self, action)(detail_obj)
                    if not is_success:
                        self.is_error = True
                        break
                # ---- 非依赖项列表并发 ----
                if self.is_error:
                    break
                _future_list = []
                for detail_obj in no_dependency_ls:
                    future_obj = executor.submit(
                        getattr(self, action), detail_obj)
                    _future_list.append(future_obj)
                for future in as_completed(_future_list):
                    is_success, message = future.result()
                    if not is_success:
                        self.is_error = True
                        break
            logger.info("End else install")

        if self.is_error:
            # 步骤失败，主流程失败
            main_obj.install_status = \
                MainInstallHistory.INSTALL_STATUS_FAILED
            main_obj.save()
            # 状态为 '待安装'/'安装中' 的记录，则记为 '失败'
            queryset.filter(install_step_status__in=(
                DetailInstallHistory.INSTALL_STATUS_READY,
                DetailInstallHistory.INSTALL_STATUS_INSTALLING
            )).update(install_step_status=DetailInstallHistory.INSTALL_STATUS_FAILED)
            logger.info(f"Main Install Failed, id[{self.main_id}]")
            return self.is_error

        # 流程执行完整，主流程成功
        main_obj.install_status = \
            MainInstallHistory.INSTALL_STATUS_SUCCESS
        main_obj.save()
        # TODO 注册监控
        logger.info(f"Main Install Success, id[{self.main_id}]")
        return self.is_error
