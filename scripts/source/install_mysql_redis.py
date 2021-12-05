# -*- coding: utf-8 -*-
# Project: install_mysql_redis
# Author: jon.liu@yunzhihui.com
# Create time: 2021-12-04 18:42
# IDE: PyCharm
# Version: 1.0
# Introduction:

import os
import sys
import yaml
import time
import shutil
import subprocess


CURRENT_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_FOLDER = os.path.dirname(os.path.dirname(CURRENT_FILE_PATH))

config_path = os.path.join(PROJECT_FOLDER, "config/omp.yaml")
PROJECT_DATA_PATH = os.path.join(PROJECT_FOLDER, "data")
PROJECT_LOG_PATH = os.path.join(PROJECT_FOLDER, "logs")


def cmd(command):
    """执行shell 命令"""
    p = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    stdout, stderr = p.communicate()
    _out, _err, _code = stdout, stderr, p.returncode
    return _out.decode(), _err.decode(), _code


def get_config_dic():
    """
    获取配置文件详细信息
    :return:
    """
    with open(config_path, "r", encoding="utf8") as fp:
        return yaml.load(fp, Loader=yaml.FullLoader)


def replace_placeholder(file_path, data):
    """
    替换占位符
    :param file_path: 文件路径
    :param data: 占位符映射关系
    :type data: dict
    :return:
    """
    if not os.path.exists(file_path):
        print(f"无法找到文件{file_path}")
        sys.exit(1)
    with open(file_path, "r", encoding="utf8") as fp:
        content = fp.read()
    for key, value in data.items():
        content = content.replace(key, str(value))
    with open(file_path, "w", encoding="utf8") as fp:
        fp.write(content)


def get_run_user():
    """
    获取程序运行用户
    :return:
    """
    global_user = get_config_dic().get("global_user")
    if global_user != "root":
        return global_user
    default_user = "omp"
    cmd(f"id {default_user} || useradd -s /bin/bash {default_user}")
    return default_user


def install_mysql():
    """
    安装 mysql 逻辑
    :return:
    """
    mysql_config = get_config_dic().get("mysql")
    _dic = {
        "CW_MYSQL_USERNAME": mysql_config.get("username"),
        "CW_MYSQL_PASSWORD": mysql_config.get("password"),
        "CW_MYSQL_PORT": mysql_config.get("port"),
        "CW_MYSQL_RUN_USER": get_run_user(),
        "CW_MYSQL_DATA_DIR": os.path.join(PROJECT_DATA_PATH, "mysql"),
        "CW_MYSQL_ERROR_LOG_DIR": os.path.join(PROJECT_LOG_PATH, "mysql"),
        "CW_MYSQL_BASE_DIR": os.path.join(PROJECT_FOLDER, "component/mysql")
    }
    # 创建日志目录
    if not os.path.exists(_dic["CW_MYSQL_ERROR_LOG_DIR"]):
        cmd(f"mkdir -p {_dic['CW_MYSQL_ERROR_LOG_DIR']}")
    # 复制数据到目标目录
    shutil.copytree(
        os.path.join(_dic["CW_MYSQL_BASE_DIR"], "data"),
        os.path.join(PROJECT_DATA_PATH, "mysql")
    )
    # 替换占位符
    # my.cnf
    replace_placeholder(
        os.path.join(_dic["CW_MYSQL_BASE_DIR"], "my.cnf"), _dic)
    # scripts/mysql
    _mysql_path = os.path.join(_dic["CW_MYSQL_BASE_DIR"], "scripts/mysql")
    replace_placeholder(_mysql_path, _dic)
    # 启动服务
    out, _, code = cmd(f"bash {_mysql_path} start")
    if "mysql  [running]" not in out:
        print(f"mysql启动失败: {out}")
        sys.exit(1)
    time.sleep(30)
    # 确保mysql启动成功并可用
    _mysql_cli = os.path.join(_dic["CW_MYSQL_BASE_DIR"], "bin/mysql")
    _mysql_cli = f"{_mysql_cli} -S {os.path.join(_dic['CW_MYSQL_DATA_DIR'], 'mysql.sock')}"
    try_times = 0
    while try_times < 10:
        out, _, _ = cmd(f"{_mysql_cli} -e 'SHOW DATABASES;'")
        if "information_schema" in out:
            break
        try_times += 1
        time.sleep(10)
    else:
        print("mysql启动失败")
        sys.exit(1)
    # 创建数据库
    create = "create database omp default charset utf8 collate utf8_general_ci;"
    cmd(f"{_mysql_cli} -e '{create}'")
    _u = _dic["CW_MYSQL_USERNAME"]
    _p = _dic["CW_MYSQL_PASSWORD"]
    cmd(f""" {_mysql_cli} -e 'grant all privileges on `omp`.* to "{_u}"@"%" identified by "{_p}" with grant option;' """)
    flush = "flush privileges;"
    cmd(f"{_mysql_cli} -e '{flush}'")


def install_redis():
    """
    安装 redis 逻辑
    :return:
    """
    redis_config = get_config_dic().get("redis")
    _dic = {
        "CW_REDIS_PORT": redis_config.get("port"),
        "CW_REDIS_PASSWORD": redis_config.get("password"),
        "CW_REDIS_BASE_DIR": os.path.join(PROJECT_FOLDER, "component/redis"),
        "CW_REDIS_LOG_DIR": os.path.join(PROJECT_LOG_PATH, "redis"),
        "CW_REDIS_DATA_DIR": os.path.join(PROJECT_DATA_PATH, "redis"),
        "CW_LOCAL_IP": get_config_dic().get("local_ip"),
        "CW_REDIS_RUN_USER": get_run_user()
    }
    cmd(f"mkdir -p {_dic['CW_REDIS_LOG_DIR']}")
    cmd(f"mkdir -p {_dic['CW_REDIS_DATA_DIR']}")
    _redis_path = os.path.join(_dic["CW_REDIS_BASE_DIR"], "scripts/redis")
    _redis_conf = os.path.join(_dic["CW_REDIS_BASE_DIR"], "redis.conf")
    replace_placeholder(_redis_path, _dic)
    replace_placeholder(_redis_conf, _dic)
    cmd(f"bash {_redis_path} start")


if __name__ == '__main__':
    install_mysql()
    install_redis()
