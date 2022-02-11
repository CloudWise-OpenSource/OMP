"""
服务相关异步任务
"""

import logging

from celery import shared_task
from celery.utils.log import get_task_logger
from db_models.models import (
    ToolExecuteMainHistory,
    ToolExecuteDetailHistory
)
from utils.plugin.salt_client import SaltClient
from django.utils import timezone
import os
from utils.plugin import public_utils
from concurrent.futures import (
    ThreadPoolExecutor, as_completed
)

THREAD_POOL_MAX_WORKERS = 20
# 屏蔽celery任务日志中的paramiko日志
logging.getLogger("paramiko").setLevel(logging.WARNING)
logger = get_task_logger("celery_log")


class ThreadUtils:
    def __init__(self):
        self.error = False
        self.timeout = 10
        self.salt = SaltClient()
        self.salt_data = self.salt.client.opts.get("root_dir")
        self.count = 0

    def check_result(self, future_list):
        """
        查看线程结果
        """
        for future in as_completed(future_list):
            is_success, message = future.result()
            if not is_success:
                self.error = True
            self.count += 1

    @staticmethod
    def send_message(tool_detail_obj, index=None, message=None):
        """
        标准打印日志
        """
        message_info = ["开始发送工具包", "开始执行工具包", "开始获取输出文件", "工具执行成功"]
        if index:
            message = message_info[index]
        tool_detail_obj.execute_log += "{1} {0}\n".format(
            message, timezone.now())
        tool_detail_obj.save()

    def receive_file(self, tool_detail_obj, receive_files, ip):
        """
        接收文件
        """
        self.send_message(tool_detail_obj, 2)
        pull_dc = receive_files.get("output_files", [])
        receive_to = receive_files.get("receive_to", "/tmp")
        upload_real_paths = []
        for file in pull_dc:
            status, message = self.salt.cp_push(
                target=ip,
                source_path=file,
                upload_path=file.rsplit("/", 1))
            upload_real_paths.append(
                os.path.join(self.salt_data, f"var/cache/salt/master/minions/{ip}/files/*"))
            if not status:
                tool_detail_obj.status = ToolExecuteDetailHistory.STATUS_FAILED
                self.send_message(tool_detail_obj, message)
                return False
        if upload_real_paths:
            _out, _err, _code = public_utils.local_cmd(
                f'mv {" ".join(upload_real_paths)} {receive_to}')
            if _code != 0:
                tool_detail_obj.status = ToolExecuteDetailHistory.STATUS_FAILED
                self.send_message(tool_detail_obj, _out)
                return False
        return True

    def single_tool_executor(self, tool_detail_obj):
        """
        执行单个工具任务函数
        """
        tool_detail_obj.status = ToolExecuteDetailHistory.STATUS_RUNNING
        # 发送文件
        ip = tool_detail_obj.ip
        self.send_message(tool_detail_obj, 0)
        send_dc = tool_detail_obj.get_send_files()
        send_to = send_dc.get("send_to", "/tmp")
        for file in send_dc.get("local_files", []):
            status, message = self.salt.cp_file(target=ip,
                                                source_path=file,
                                                target_path=send_to)
            if not status:
                tool_detail_obj.status = ToolExecuteDetailHistory.STATUS_FAILED
                self.send_message(tool_detail_obj, message)
                return status, message
        # 执行脚本
        self.send_message(tool_detail_obj, 1)
        cmd_str = tool_detail_obj.get_cmd_str()
        if tool_detail_obj.run_user:
            cmd_str = 'su -s /bin/bash {1} -c "{0}"'.format(
                cmd_str, tool_detail_obj.run_user
            )
        status, message = self.salt.cmd(
            target=ip,
            command=cmd_str,
            timeout=self.timeout,
            real_timeout=tool_detail_obj.time_out
        )
        if not status:
            tool_detail_obj.status = ToolExecuteDetailHistory.STATUS_FAILED
            self.send_message(tool_detail_obj, message)
            return status, message
        self.send_message(tool_detail_obj, message)
        # 获取目标输出文件
        receive_files = tool_detail_obj.get_receive_files()
        if receive_files:
            status = self.receive_file(tool_detail_obj, receive_files, ip)
        if not status:
            return False, "执行失败"
        self.send_message(tool_detail_obj, 3)
        return True, "执行成功"


@shared_task
def exec_tools_main(tool_main_id):
    """
    工具执行类
    """
    # ToolExecuteMainHistory ToolExecuteDetailHistory
    tool_main_obj = ToolExecuteMainHistory.objects.filter(id=tool_main_id)
    exec_ing_dc = {
        "status": ToolExecuteMainHistory.STATUS_RUNNING,
        "start_time": timezone.now()
    }
    if tool_main_obj.exists():
        tool_main_obj.update(**exec_ing_dc)
    else:
        logger.error(f"主工具执行id不存在{tool_main_id}")
        raise ValueError(f"主工具执行id不存在{tool_main_id}")
    # 开始下发各个目标节点任务
    tool_detail_objs = ToolExecuteMainHistory.objects.filter(
        tool=tool_main_obj)
    thread_obj = ThreadUtils()
    with ThreadPoolExecutor(THREAD_POOL_MAX_WORKERS) as executor:
        future_list = []
        for obj in tool_detail_objs:
            future_obj = executor.submit(
                thread_obj.single_tool_executor, obj
            )
            future_list.append(future_obj)
        thread_obj.check_result(future_list)
    # 查看各个任务执行状态，修改主状态页。
    exec_ed_status = ToolExecuteMainHistory.STATUS_FAILED if thread_obj.error \
        else ToolExecuteMainHistory.STATUS_SUCCESS
    exec_ed_dc = {
        "status": exec_ed_status,
        "end_time": timezone.now()
    }
    tool_main_obj.update(**exec_ed_dc)
