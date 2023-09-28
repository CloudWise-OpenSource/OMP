# !/usr/bin/python3
# -*-coding:utf-8-*-
import logging
import os
import subprocess
import tarfile
import json
import time
import random

from db_models.models import Service, Host, BackupHistory, DetailInstallHistory
from omp_server.settings import PROJECT_DIR
from concurrent.futures import (
    ThreadPoolExecutor, as_completed
)
from utils.plugin.salt_client import SaltClient
from utils.parse_config import \
    THREAD_POOL_MAX_WORKERS, LOCAL_IP, TENGINE_PORT

logger = logging.getLogger("server")


def cmd(command):
    """执行本地shell命令"""
    p = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = p.communicate()
    _out, _err, _code = \
        stdout.decode("utf8"), stderr.decode("utf8"), p.returncode
    return _out, _err, _code


def tar_files(source_path, target_path):
    """
    压缩文件
    可以压缩多个文件或者单个目录
    source_path：源文件路径 list [a.tar.gz, b.tar.gz]
    target_path： 目标文件路径
    """
    success = True
    try:
        with tarfile.open(target_path, "w:gz") as tar:
            for file_path in source_path:
                if not os.path.exists(file_path):
                    success = False
                tar.add(file_path)
        logging.info(f"{source_path}文件打包成功,压缩文件为{target_path}")
    except Exception as e:
        logging.error(f"{source_path}文件打包错误,error={e}")
        os.remove(target_path)
        return False
    if not success:
        os.remove(target_path)
        return False
    for file_path in source_path:
        os.remove(file_path)
    return True


def transfer_week(day_of_week):
    """
    适配前端day_of_week参数传递
    """
    if day_of_week == '6':
        day_of_week = '0'
    elif day_of_week == '*':
        pass
    else:
        day_of_week = str(int(day_of_week) + 1)

    return day_of_week


def exec_scripts(exec_json, host_i_d, his_id):
    # ToDo 考虑并发场景
    tar_name = f"{exec_json['cw_o_app_name']}_bak.sh"
    scripts_path = os.path.join(
        PROJECT_DIR,
        f"package_hub/_modules/{tar_name}"
    )
    try:
        salt_client = SaltClient()
        his_tmp = f"{scripts_path}{his_id}"
        cmd(f"cp {scripts_path}.tmp {his_tmp}")
        # 占位符替换
        with open(his_tmp, 'r+') as f:
            t = f.read()
            for before, after in exec_json.items():
                t = t.replace(("${%s}" % str(before)), str(after))
            f.seek(0, 0)
            f.write(t)
            f.truncate()
        # 发送脚本
        tar_ip = exec_json['cw_o_ip']
        tar_package = f"{host_i_d[tar_ip]}/omp_packages/{tar_name}"
        is_success, message = salt_client.cp_file(
            target=tar_ip,
            source_path=f"_modules/{tar_name}{his_id}",
            target_path=tar_package
        )
        if not is_success:
            return False, message
        # 执行脚本
        cmd_str = f"nohup bash {tar_package} >" \
                  f" {host_i_d[tar_ip]}/omp_packages/logs" \
                  f"/{exec_json['cw_o_app_name']}{exec_json['tmp']}.log  2>&1 &"
        return salt_client.cmd(tar_ip, cmd_str, timeout=30)
    except Exception as e:
        return False, f"执行异常{e}"


def change_status(obj, result, message=""):
    if result:
        obj.result = BackupHistory.SUCCESS
    else:
        obj.result = BackupHistory.FAIL
    obj.message = message
    obj.save()


def check_result(future_list, his_ls):
    for index, future in enumerate(as_completed(future_list)):
        is_success, message = future.result()
        if not is_success:
            change_status(his_ls[index], False, message)


def get_backup_info(service_obj):
    """
    获取备份配置所需变量,内置变量命名 cw_o_xxx
    """
    try:
        service_dict = {
            "cw_o_app_name": service_obj.service.app_name,
            "cw_o_ip": service_obj.ip,
            "tmp": time.strftime("%Y%m%d%H%M%S", time.localtime()) + str(random.randint(1000, 9999)),
        }
        # 连接信息
        service_connect_info = service_obj.service_connect_info
        if service_connect_info:
            service_dict.update(
                {
                    "cw_o_username": service_connect_info.service_username,
                    "cw_o_password": service_connect_info.service_password,
                }
            )
        # 端口
        port_json = json.loads(service_obj.service_port)
        for k_port in port_json:
            service_dict.update({
                f"cw_o_{k_port.get('key', '')}": k_port.get("default", "")
            })

        # 安装参数
        obj = DetailInstallHistory.objects.filter(service_id=service_obj.id).first()
        install_args = obj.install_detail_args.get("install_args", {})
        for args in install_args:
            service_dict.update({
                f"cw_o_{args.get('key', '')}": args.get("default", "")
            })
        return service_dict
    except Exception as e:
        logger.error(f"获取信息失败请查看service或其账号密码端口是否存在{e}")


def backup_service_data(his_ls):
    """
    备份服务
    :param his_ls: his表列表
    :return:
    """
    master_url = f"{LOCAL_IP}:{TENGINE_PORT.get('access_port', '19001')}" \
                 f"/api/backups/backupHistory"

    host_i_d = dict(Host.objects.all().values_list("ip", "data_folder"))

    with ThreadPoolExecutor(THREAD_POOL_MAX_WORKERS) as executor:
        check_ls = []
        for his in his_ls:
            service_obj = Service.objects.filter(
                service_instance_name=his.content).first()
            if not service_obj:
                logger.info(f"{his.content}服务已被卸载或不可用")
                continue
            backup_script_args = get_backup_info(service_obj)
            backup_script_args.update(his.extend_field)
            backup_script_args.update({
                "cw_o_master_url": f"{master_url}/{his.id}/"
            })
            future_obj = executor.submit(
                exec_scripts,
                backup_script_args, host_i_d, his.id)
            check_ls.append(future_obj)
        check_result(check_ls, his_ls)


def rm_backend_file(his_objs):
    """
    删除过期文件
    :param his_objs: BackupHistory his_objs
    :return:
    """
    fail_files = []
    for history in his_objs:
        if history.file_deleted or history.result == BackupHistory.FAIL:
            history.delete()
            continue
        expire_file = os.path.join(history.retain_path, history.file_name)
        try:
            os.remove(expire_file)
        except Exception as e:
            logger.error(f"删除备份文件{expire_file}失败: {str(e)}")
            fail_files.append(history.file_name)
        history.delete()

    return fail_files


def check_ing(obj):
    if not obj:
        return True
    back_instance = BackupHistory.objects.filter(
        result=BackupHistory.ING).values_list("content", flat=True)
    ing_instance = set(obj.backup_instances) & set(back_instance)
    if ing_instance:
        logger.info(f"当前实例正在备份：{','.join(ing_instance)}")
        return True
    return False
