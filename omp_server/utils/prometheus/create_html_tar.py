# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/26 9:45 上午
# Description:
import os
import json
import subprocess
from django.conf import settings


def cmd(command):
    """执行本地shell命令"""
    p = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = p.communicate()
    _out, _err, _code = \
        stdout.decode("utf8"), stderr.decode("utf8"), p.returncode
    return _out, _err, _code


def create_html_tar(new_html_dir_name, report_data):
    """
    生成巡检报告tar.gz包
    :param new_html_dir_name: 包名
    :param report_data: 报告数据
    :return:
    """
    # 拷贝目录
    inspection_file = os.path.join(
        settings.PROJECT_DIR, f"data/inspection_file/{new_html_dir_name}")
    old_file_dir = os.path.join(
        settings.PROJECT_DIR, "package_hub/template/inspection_html")
    _out, _err, _code = cmd(f"cp -r {old_file_dir} {inspection_file}")
    if _code:
        return False, "拷贝文件失败！"
    # 修改源数据
    js_path = os.path.join(inspection_file, "static/js/main.e4ade54a.chunk.js")
    with open(js_path, "r") as f:
        content = f.read()
    content = content.replace("'!@#$'", json.dumps(report_data))
    with open(js_path, "w") as f:
        f.write(content)
    # 打包
    inspection_dir = os.path.join(settings.PROJECT_DIR, f"data/inspection_file")
    tar_file = f"{new_html_dir_name}.tar.gz"
    _out, _err, _code = cmd(
        f"cd {inspection_dir} && tar -cvf {tar_file} {new_html_dir_name}")
    # 删除源文件
    cmd(f"rm -rf {inspection_file}")
    if _code:
        return False, "打包巡检报告失败"
    return True, tar_file
