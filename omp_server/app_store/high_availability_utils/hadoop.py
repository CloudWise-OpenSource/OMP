import logging
import os
from utils.common.exceptions import GeneralError
from db_models.models import (
    Service, DetailInstallHistory,
    Host
)

from concurrent.futures import (
    ThreadPoolExecutor, as_completed
)
from utils.plugin.salt_client import SaltClient

THREAD_POOL_MAX_WORKERS = 20
logger = logging.getLogger("server")


# send unzip install3个节点并行顺序执行

# 3个节点并行顺序执行 但每个动作必须有前一个动作为基础一个失败全体失败


class Hadoop(object):
    ACTION_LS = ("send", "unzip", "install")
    hadoop_init = [
        ("init", "zkfc"), ("start", "journalnode"),
        ("format", "namenode"), ("sync", "namenode"),
        ("start", "zkfc"), ("start", "datanode"),
        ("start", "resourcemanager"), ("start", "nodemanager")
    ]

    def __init__(self, install_exec_obj, detail_list_obj):
        """
        解析数据
        :param install_exec_obj InstallServiceExecutor对象实例
        :parm detail_list_obj detail的orm对象列表
        :return:
        """
        self.install_obj = install_exec_obj
        self.detail_list = detail_list_obj
        self.timeout = 100
        self.salt_client = SaltClient()
        self.error = False
        self.target_set = set()
        self.count = 0
        self.detail_dict = {}  # 中间结果，任意一个hadoop_init失败所有的detail对象全部失败

    def check_result(self, future_list):
        for future in as_completed(future_list):
            is_success, message = future.result()
            if not is_success:
                self.install_obj.is_error = True
                self.error = True
                break
        self.count += 1

    def init_hadoop(self, detail_obj, target_ip, service_controllers_dict, action):
        try:
            # 获取服务初始化脚本绝对路径
            init_script_path = service_controllers_dict.get("init", "")
            # 获取 json 文件路径
            target_host = Host.objects.filter(ip=target_ip).first()
            assert target_host is not None
            json_path = os.path.join(
                target_host.data_folder, "omp_packages",
                f"{detail_obj.main_install_history.operation_uuid}.json")

            cmd_str = f"python {init_script_path} --local_ip {target_ip} " \
                      f"--data_json {json_path} --action_type {action[0]} --action_object {action[1]}"
            # 执行初始化
            is_success, message = self.salt_client.cmd(
                target=target_ip,
                command=cmd_str,
                timeout=self.timeout)
            if not is_success:
                raise GeneralError(message)
            # 执行成功且 message 有值，则补充至服务日志中
            if is_success and bool(message):
                detail_obj.install_msg += \
                    f"{self.install_obj.now_time()} 初始化脚本执行成功，脚本输出如下:\n" \
                    f"{message}\n"
                detail_obj.save()
        except Exception as err:
            for obj, name in self.detail_dict.items():
                logger.error(f"Init Failed -> [{name}]: {err}")
                obj.init_flag = 3
                obj.init_msg += f"{self.install_obj.now_time()} {name} " \
                                f"初始化服务失败: {err}\n"
                # 更新安装流程状态为 '失败'，服务状态为 '安装失败'
                obj.install_step_status = \
                    DetailInstallHistory.INSTALL_STATUS_FAILED
                obj.save()
                obj.service.service_status = \
                    Service.SERVICE_STATUS_INSTALL_FAILED
                obj.service.save()
                # 创建历史记录
                self.install_obj.create_history(obj, is_success=False)
            return False, err

    def init(self, action, detail_obj_list):
        """ 初始化服务 """
        # 获取初始化使用参数
        with ThreadPoolExecutor(THREAD_POOL_MAX_WORKERS) as executor:
            future_list = []
            for detail_obj in detail_obj_list:
                target_ip = detail_obj.service.ip
                service_name = detail_obj.service.service_instance_name
                service_controllers_dict = detail_obj.service.service_controllers
                if target_ip not in self.target_set:
                    # 中间结果，全部成功后更新状态
                    self.detail_dict[detail_obj] = service_name
                    self.target_set.add(target_ip)
                    logger.info(f"Init Begin -> [{service_name}]")
                    detail_obj.init_flag = 1
                    detail_obj.init_msg += f"{self.install_obj.now_time()} {service_name} 开始初始化服务\n"
                    detail_obj.save()
                future_obj = executor.submit(
                    self.init_hadoop, detail_obj,
                    target_ip, service_controllers_dict,
                    action
                )
                future_list.append(future_obj)
            self.check_result(future_list)
        # 安装成功
        if self.count == 9:
            for obj, name in self.detail_dict.items():
                logger.info(f"Init Success -> [{name}]")
                obj.init_flag = 2
                obj.init_msg += f"{self.install_obj.now_time()} {name} 成功初始化服务\n"
                # 完成安装流程，更新状态为 '安装成功'
                obj.install_step_status = \
                    DetailInstallHistory.INSTALL_STATUS_SUCCESS
                # 创建历史记录
                self.install_obj.create_history(obj, is_success=True)
            return True, "Init Success"

    def single_service_executor(self, detail_obj):
        """
        单独服务的安装执行器
        :param detail_obj:
        :type detail_obj: DetailInstallHistory
        :return:
        """
        # 更改服务状态为安装中状态
        detail_obj.service.service_status = Service.SERVICE_STATUS_INSTALLING
        detail_obj.service.save()
        # 跳过单个服务的已经成功的单个步骤不再重复执行
        for action in self.ACTION_LS:
            if getattr(detail_obj, f"{action}_flag") == 2:
                continue
            _flag, _msg = getattr(self.install_obj, action)(detail_obj)
            if not _flag:
                return _flag, _msg
        return True, "success"

    def thread_poll_executor(self):
        """
        多线程执行器
        """
        logger.info(f"Start thread poll executor for {self.detail_list}")
        with ThreadPoolExecutor(THREAD_POOL_MAX_WORKERS) as executor:
            _future_list = []
            for detail_obj in self.detail_list:
                # 更新单条安装记录的状态
                detail_obj.install_step_status = \
                    DetailInstallHistory.INSTALL_STATUS_INSTALLING
                detail_obj.save()
                future_obj = executor.submit(
                    self.single_service_executor, detail_obj
                )
                _future_list.append(future_obj)
            self.check_result(_future_list)
            for action in self.hadoop_init:
                if not self.error:
                    self.init(action, self.detail_list)

        logger.info("Finish thread poll executor!")
