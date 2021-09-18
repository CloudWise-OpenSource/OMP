# -*- coding: utf-8 -*-
# Project: install_or_update
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-17 17:01
# IDE: PyCharm
# Version: 1.0
# Introduction:

import os
import sys
import subprocess


OMP_HOME = "/data/omp"
UPDATE_HOME = "/data/omp_update"
OMP_PYTHON_PATH = os.path.join(OMP_HOME, "component/env/bin/python3")
OMP_MANAGE_PATH = os.path.join(OMP_HOME, "omp_server/manage.py")
OMP_SHELL_PATH = os.path.join(OMP_HOME, "scripts/omp")
OMP_UPDATE_DATA_PATH = os.path.join(OMP_HOME, "scripts/source/update_data.py")


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
    print("Execute Command: {0}\nRETCODE: {1}\nSTDOUT: {2}\nSTDERR: {3}\n".format(
        command, _code, _out, _err
    ))
    return _out, _err, _code


def install(pack_path, ip_address):
    """
    omp安装流程
    :param pack_path: 包路径
    :param ip_address: ip地址
    :return:
    """
    # 解压源码包
    cmd("tar -xf {0} -C {1}".format(pack_path, os.path.dirname(OMP_HOME)))
    # 执行安装脚本
    cmd("bash {0} {1}".format(os.path.join(
        OMP_HOME, 'scripts/install.sh'), ip_address))
    # 执行数据库迁移
    cmd("{0} {1} migrate".format(OMP_PYTHON_PATH, OMP_MANAGE_PATH))
    # 启动OMP服务
    cmd("bash {0} all start".format(OMP_SHELL_PATH))


def update_omp_platform(pack_path, update_file_folder):
    """
    更新omp平台端文件
    :param pack_path: omp包路径
    :param update_file_folder: 更新文件路径
    :return:
    """
    # 解压安装包
    cmd("tar -xf {0} -C {1}".format(pack_path, update_file_folder))
    # 备份服务端文件
    omp_server_old = os.path.join(OMP_HOME, 'omp_server')
    omp_server_bak = os.path.join(update_file_folder, 'omp_server')
    cmd("test -d {0} || cp -rf {1} {2}".format(omp_server_bak,
                                               omp_server_old, update_file_folder))
    omp_scripts_old = os.path.join(OMP_HOME, 'scripts')
    omp_scripts_bak = os.path.join(update_file_folder, 'scripts')
    cmd("test -d {0} || cp -rf {1} {2}".format(omp_scripts_bak,
                                               omp_scripts_old, update_file_folder))
    omp_web_old = os.path.join(OMP_HOME, 'omp_web')
    omp_web_bak = os.path.join(update_file_folder, 'omp_web')
    cmd("test -d {0} || cp -rf {1} {2}".format(omp_web_bak,
                                               omp_web_old, update_file_folder))
    # 更新服务端文件
    _new_server = os.path.join(update_file_folder, "omp/omp_server")
    cmd("rm -rf {0} && cp -rf {1} {2}".format(omp_server_old,
                                              _new_server, omp_server_old))
    _new_web = os.path.join(update_file_folder, "omp/omp_web")
    cmd("rm -rf {0} && cp -rf {1} {2}".format(omp_web_old, _new_web, omp_web_old))
    _new_scripts = os.path.join(update_file_folder, "omp/scripts")
    cmd("rm -rf {0} && cp -rf {1} {2}".format(omp_scripts_old,
                                              _new_scripts, omp_scripts_old))


def update_config(update_file_folder):
    """
    更新配置文件
    :param update_file_folder:
    :return:
    """
    from ruamel.yaml import YAML
    # 复制配置文件
    config_old = os.path.join(OMP_HOME, "config")
    config_bak = os.path.join(update_file_folder, "config")
    config_new = os.path.join(update_file_folder, "omp/config/omp.yaml")
    cmd("test -d {0} || cp -rf {1} {2}".format(config_bak,
                                               config_old, config_bak))

    # 提取原有配置
    with open(os.path.join(config_old, "omp.yaml"), "r", encoding="utf8") as fp:
        content_old = fp.read()
    my_yaml = YAML()
    old_config_dic = my_yaml.load(content_old)

    # 提取最新配置
    with open(config_new, "r", encoding="utf8") as fp:
        content_new = fp.read()
    my_yaml = YAML()
    new_config_dic = my_yaml.load(content_new)

    # 合并并重写配置
    new_config_dic.update(old_config_dic)
    with open(os.path.join(config_old, "omp.yaml"), "w", encoding="utf8") as fp:
        my_yaml.dump(new_config_dic, fp)


def update(pack_path, ip_address):
    """
    omp更新流程
    :param pack_path: 包路径
    :param ip_address: ip地址
    :return:
    """
    # 创建升级文件夹
    cmd("mkdir -p {0}".format(UPDATE_HOME))
    # 获取安装包md5值
    _out, _, _ = cmd("md5sum {0}".format(pack_path))
    package_md5 = _out.strip().split()[0].strip().decode()
    update_file_folder = os.path.join(UPDATE_HOME, "{0}".format(package_md5))
    cmd("test -d {0} && rm -rf {0}".format(update_file_folder))
    cmd("mkdir -p {0}".format(update_file_folder))
    # 更新平台端文件
    update_omp_platform(pack_path, update_file_folder)
    # 更新配置文件
    update_config(update_file_folder)
    # 执行数据库迁移
    cmd("{0} {1} migrate".format(OMP_PYTHON_PATH, OMP_MANAGE_PATH))
    # 重启相关服务
    cmd("bash {0} all restart".format(OMP_SHELL_PATH))


def main(pack_path, ip_address):
    """
    运行主方法
    :param pack_path: 包路径
    :param ip_address: 本机ip地址
    :return:
    """
    if os.path.exists(OMP_HOME):
        update(pack_path, ip_address)
    else:
        install(pack_path, ip_address)
    # 更新默认数据
    cmd("{0} {1}".format(OMP_PYTHON_PATH, OMP_UPDATE_DATA_PATH))
    print("All Process Finish")


if __name__ == '__main__':
    sys_args = sys.argv[1:]
    if len(sys_args) != 2:
        print("Please use: python install_or_update.py package_path local_ip")
    package_path, local_ip = sys_args
    if not os.path.exists(package_path):
        print("{0} Package Not Exist!".format(package_path))
    main(pack_path=package_path, ip_address=local_ip)
