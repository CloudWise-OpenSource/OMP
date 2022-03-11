#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import sys
import logging
import time
import logging.config
import subprocess

PYTHON_VERSION = sys.version_info.major
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

if PYTHON_VERSION == 2:
    reload(sys)
    sys.setdefaultencoding('utf-8')

# ---- 日志定义部分 ----
# 日志配置 建议输入绝对路径,默认生成日志会添加 时间字段
LOG_PATH = "/tmp/init_host_standalone.log"
# 屏幕输出日志级别
CONSOLE_LOG_LEVEL = logging.INFO
# 文件日志级别
FILE_LOG_LEVEL = logging.DEBUG


def generate_log_filepath(log_path):
    """生成日志名称"""
    time_str = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    dirname = os.path.dirname(log_path)
    name_split = os.path.basename(log_path).split('.')
    if len(name_split) == 1:
        name = "{0}_{1}".format(name_split[0], time_str)
        file_path = os.path.join(dirname, name)
    else:
        name_split.insert(-1, time_str)
        file_path = os.path.join(dirname, '.'.join(name_split))
    return file_path


# 日志配置
log_path = generate_log_filepath(LOG_PATH)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename=log_path,
    filemode='a')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
console.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(console)

KERNEL_PARAM = """# Disable IPv6
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
# ARP
net.ipv4.conf.default.rp_filter = 0
net.ipv4.conf.all.rp_filter = 0
net.ipv4.neigh.default.gc_stale_time = 120
net.ipv4.conf.default.arp_announce = 2
net.ipv4.conf.all.arp_announce = 2
net.ipv4.conf.lo.arp_announce = 2
# TCP Memory
net.core.rmem_default = 2097152
net.core.wmem_default = 2097152
net.core.rmem_max = 4194304
net.core.wmem_max = 4194304
net.ipv4.tcp_rmem = 4096 8192 4194304
net.ipv4.tcp_wmem = 4096 8192 4194304
net.ipv4.tcp_mem = 524288 699050 1048576
# TCP SYN
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_synack_retries = 1
net.ipv4.tcp_syn_retries = 1
net.ipv4.tcp_max_syn_backlog = 16384
net.core.netdev_max_backlog = 16384
# TIME_WAIT
net.ipv4.route.gc_timeout = 100
net.ipv4.tcp_max_tw_buckets = 5000
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_timestamps = 0
net.ipv4.tcp_fin_timeout = 2
net.ipv4.ip_local_port_range = 20000 50000
# TCP keepalive
net.ipv4.tcp_keepalive_probes = 3
net.ipv4.tcp_keepalive_time = 60
net.ipv4.tcp_keepalive_intvl = 10
# Other TCP
net.ipv4.tcp_max_orphans = 65535
net.core.somaxconn = 16384
net.ipv4.tcp_sack = 1
net.ipv4.tcp_window_scaling = 1
vm.max_map_count=262144
vm.min_free_kbytes=512000
vm.swappiness = 0"""

KERNEL_KEYWORD = [
    "net.ipv6.conf.all.disable_ipv6",
    "net.ipv6.conf.default.disable_ipv6",
    "net.ipv4.conf.default.rp_filter",
    "net.ipv4.conf.all.rp_filter",
    "net.ipv4.neigh.default.gc_stale_time",
    "net.ipv4.conf.default.arp_announce",
    "net.ipv4.conf.all.arp_announce",
    "net.ipv4.conf.lo.arp_announce",
    "net.core.rmem_default",
    "net.core.wmem_default",
    "net.core.rmem_max",
    "net.core.wmem_max",
    "net.ipv4.tcp_rmem",
    "net.ipv4.tcp_wmem",
    "net.ipv4.tcp_mem",
    "net.ipv4.tcp_syncookies",
    "net.ipv4.tcp_synack_retries",
    "net.ipv4.tcp_syn_retries",
    "net.ipv4.tcp_max_syn_backlog",
    "net.core.netdev_max_backlog",
    "net.ipv4.route.gc_timeout",
    "net.ipv4.tcp_max_tw_buckets",
    "net.ipv4.tcp_tw_reuse",
    "net.ipv4.tcp_timestamps",
    "net.ipv4.tcp_fin_timeout",
    "net.ipv4.ip_local_port_range",
    "net.ipv4.tcp_keepalive_probes",
    "net.ipv4.tcp_keepalive_time",
    "net.ipv4.tcp_keepalive_intvl",
    "net.ipv4.tcp_max_orphans",
    "net.core.somaxconn",
    "net.ipv4.tcp_sack",
    "net.ipv4.tcp_window_scaling",
    "vm.max_map_count",
    "vm.swappiness",
    "vm.min_free_kbytes"
]
TO_MODIFY_HOST_NAME = [
    "localhost",
    "localhost.localhost",
    "localhost.domain",
]


class BaseInit(object):
    """ Base class 检查权限 / 执行命令方法 """

    def check_permission(self):
        """ 检查权限 """
        logger.info("开始检查当前用户执行权限")
        if not os.getuid() == 0:
            self.__check_is_sodu()
            if not self.is_sudo:
                logging.error('当前执行用户不是root，且此用户没有sudo NOPASSWD 权限，无法初始化！')
                exit(1)
        logger.info('当前用户权限正常，开始执行脚本')

    def __check_is_sodu(self):
        """ 是否具有 sodu 权限 """
        logger.info("检查是否具有sodu免密码权限")
        _cmd = "sudo -n 'whoami' &>/dev/null"
        _, _, _code = self.cmd(_cmd)
        self.is_sudo = _code == 0
        logger.info("是否具有sodu免密码权限: {}".format(self.is_sudo))

    def cmd(self, command):
        """ 执行shell 命令 """
        if hasattr(self, 'is_sudo'):
            if command.lstrip().startswith("echo"):
                command = "sudo sh -c '{0}'".format(command)
            else:
                command = "sudo {0}".format(command)
        logger.debug("Exec command: {0}".format(command))
        p = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )
        stdout, stderr = p.communicate()
        _out, _err, _code = stdout, stderr, p.returncode
        logger.debug(
            "Get command({0}) stdout: {1}; stderr: {2}; ret_code: {3}".format(
                command, _out, _err, _code
            )
        )
        return _out, _err, _code

    @staticmethod
    def read_file(path, mode='r', res='str'):
        """
        :param path 路径
        :param mode 模式
        :param res 返回数据类型 str/list
        """
        if not os.path.exists(path):
            logger.error('读取文件失败，文件路径错误:{}'.format(path))
            exit(1)
        with open(path, mode) as f:
            data = f.read() if res == 'str' else f.readlines()
        return data

    def __get_os_version(self):
        logging.debug('开始获取系统版本信息')
        # match = False
        _, _, _code = self.cmd('systemctl --version')
        if _code != 0:
            logger.error("执行失败，当前操作系统不支持本脚本")
            exit(1)
        self.os_version = 7
        logging.debug('获取系统版本信息完成')

    def set_opts(self, **kwargs):
        """ 根据kwargs 设置参数"""
        raise Exception("程序错误，需实现set_opts方法")

    def run(self):
        # 检查权限
        if sys.argv[1] != 'valid':
            self.check_permission()
        self.__get_os_version()
        logging.info("开始执行脚本")

        self.run_methods()

    def run_methods(self):
        try:
            assert isinstance(self.m_list, list), "m_list 类型错误 方法错误，请检查脚本"
            assert len(self.m_list) > 0, "m_list 为空，请检查脚本"
            for func_info in self.m_list:
                assert isinstance(func_info, tuple) and len(
                    func_info) == 2, "todo_list 方法错误，请检查脚本:{}".format(func_info)
                method_name, method_note = func_info
                if hasattr(self, method_name):
                    f = getattr(self, method_name)
                    logger.info("开始 执行: {}".format(method_note))
                    f()
                    logger.info("执行 完成: {}".format(method_note))
                else:
                    logger.warn("安装方法列表错误，{} 方法不存在".format(method_note))
            else:
                logging.info("执行结束, 完整日志保存在 {}".format(log_path))
        except TypeError:
            logger.error("脚本配置错误，TypeError:")
        except Exception as e:
            logger.error(e)
            logging.info("执行结束, 完整日志保存在 {}".format(log_path))
            exit(1)


class InitHost(BaseInit):
    """ 初始化节点信息 """

    def __init__(self, host_name, local_ip):
        self.m_list = [
            ('env_set_timezone', '设置时区'),
            ('env_set_firewall', '关闭防火墙'),
            ('env_set_disable_ipv6', '设置关闭ipv6'),
            ('env_set_language', '设置语言'),
            ('env_set_file_limit', '设置文件句柄数'),
            ('env_set_kernel', '设置内核参数'),
            ('env_set_disable_selinux', '关闭selinux'),
            ('set_hostname', '设置主机名'),
        ]
        # TODO
        self.hostname = host_name
        self.local_ip = local_ip

    def env_set_timezone(self):
        """ 设置时区 """
        timezone = "PRC"
        self.cmd("test -f /etc/timezone && rm -f /etc/timezone")
        self.cmd("rm -f /etc/localtimze")
        self.cmd(
            "ln -sf /usr/share/zoneinfo/{0} /etc/localtime".format(timezone))

    def env_set_firewall(self):
        """ 关闭 firewall """
        _, _, _code = self.cmd(
            "systemctl status firewalld.service | egrep -q 'Active: .*(dead)'"
        )
        if _code != 0:
            self.cmd("systemctl stop firewalld.service >/dev/null 2>&1")
            self.cmd("systemctl disable firewalld.service >/dev/null 2>&1")

    def env_set_disable_ipv6(self):
        """ 关闭ipv6 """
        _, _, _code = self.cmd("grep -q 'ipv6.disable' /etc/default/grub")
        if _code == 0:
            self.cmd(
                "sed -i 's/ipv6.disable=[0-9]/ipv6.disable=1/g' /etc/default/grub"
            )
        else:
            self.cmd(
                """sed -i '/GRUB_CMDLINE_LINUX/ s/="/="ipv6.disable=1 /' /etc/default/grub"""
            )
        self.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")

    def env_set_language(self):
        """ 设置语言 """
        self.cmd("localectl set-locale LANG=en_US.UTF-8")

    def env_set_file_limit(self):
        """ 设置打开的文件句柄数 """
        _file_max_out, _, _ = self.cmd("cat /proc/sys/fs/file-max")
        file_max = int(_file_max_out)
        _nr_open_out, _, _ = self.cmd("cat /proc/sys/fs/nr_open")
        nr_open = int(_nr_open_out)
        if file_max < 655350:
            self.cmd("sed -i '/fs.file-max/d' /etc/sysctl.conf")
            self.cmd("echo 'fs.file-max = 655350' >>/etc/sysctl.conf")
            self.cmd("sysctl -p 1>/dev/null")
            file_max = 655350
        elif file_max > nr_open:
            file_max = nr_open - 5000

        self.cmd("sed -i '/nofile/d' /etc/security/limits.conf")
        self.cmd(
            'echo "*               -       nofile          {0}" >>/etc/security/limits.conf'.format(
                file_max
            )
        )
        if os.path.exists("/etc/security/limits.d/20-nproc.conf"):
            self.cmd(
                "sed -i 's#4096#unlimited#g' /etc/security/limits.d/20-nproc.conf"
            )
        self.cmd("sed -i '/^DefaultLimitCORE/d' /etc/systemd/system.conf")
        self.cmd("sed -i '/^DefaultLimitNOFILE/d' /etc/systemd/system.conf")
        self.cmd("sed -i '/^DefaultLimitNPROC/d' /etc/systemd/system.conf")
        c = 'echo -e "DefaultLimitCORE=infinity\\nDefaultLimitNOFILE={0}\\nDefaultLimitNPROC={0}" >>/etc/systemd/system.conf'.format(
            file_max)
        self.cmd(
            c
        )
        self.cmd("ulimit -SHn {0}".format(file_max))

    def env_set_kernel(self):
        """ 设置内核参数 """
        for item in KERNEL_KEYWORD:
            self.cmd('sed -i "/{0}/d" /etc/sysctl.conf'.format(item.strip()))
        self.cmd('sed -i "/tables/d" /etc/sysctl.conf')
        self.cmd('echo "{0}" >>/etc/sysctl.conf'.format(KERNEL_PARAM))
        self.cmd("sysctl -p 1>/dev/null")

    def env_set_disable_selinux(self):
        """ 禁用 selinux """
        if os.path.exists("/etc/selinux/config"):
            self.cmd(
                "sed -i 's#^SELINUX=.*#SELINUX=disabled#g' /etc/selinux/config")
            self.cmd("setenforce 0")

    def set_hostname(self):
        """设置主机名"""
        _out, _err, _code = self.cmd("echo $(hostname)")
        if _out.strip().lower() in TO_MODIFY_HOST_NAME or _out.strip().isdigit():
            self.cmd('echo "{0}" >/etc/hostname'.format(self.hostname))
            self.cmd('echo "{0}" > /proc/sys/kernel/hostname'.format(self.hostname))
            self.cmd("hostname {0}".format(self.hostname))
            self.cmd('echo "{0}    {1}" >> /etc/hosts'.format(self.local_ip, self.hostname))


class ValidInit(BaseInit):
    def __init__(self):
        self.m_list = [
            ('valid_env_timezone', '校验时区'),
            ('valid_env_firewall', '校验防火墙'),
            ('valid_env_language', '校验语言'),
            ('valid_env_file_limit', '校验文件具柄数'),
            ('valid_env_kernel', '校验内核参数'),
            ('valid_env_disable_selinux', '校验selinux'),
            ('valid_host_name', '校验host_name'),
        ]

    def valid_env_timezone(self):
        """ 校验时区 """
        assert os.readlink(
            '/etc/localtime') == "/usr/share/zoneinfo/PRC", "时区校验失败"

    def valid_env_firewall(self):
        """ 校验防火墙 """
        _, _, _code = self.cmd(
            "systemctl status firewalld.service | egrep -q 'Active: .*(dead)'"
        )
        assert _code == 0, "防火墙校验失败"

    def valid_env_language(self):
        """ 校验语言 """
        assert self.cmd(
            "localectl status |grep LANG=en_US.UTF-8")[2] == 0, "语言环境校验失败"

    def valid_env_file_limit(self):
        """ 校验文件具柄数 """
        _err = ""
        _file_max_out, _, _ = self.cmd("cat /proc/sys/fs/file-max")
        file_max = int(_file_max_out)
        _nr_open_out, _, _ = self.cmd("cat /proc/sys/fs/nr_open")
        nr_open = int(_nr_open_out)
        if file_max < 655350:
            _err = "文件句柄数校验失败"
        elif file_max > nr_open:
            file_max = nr_open - 5000

        if self.cmd(
                'grep "*               -       nofile          {0}" /etc/security/limits.conf'.format(
                    file_max
                )
        )[2] != 0:
            _err = "文件 /etc/security/limits.conf 校验失败"

        if os.path.exists("/etc/security/limits.d/20-nproc.conf"):
            if self.cmd(
                    "grep unlimited /etc/security/limits.d/20-nproc.conf"
            )[2] != 0:
                _err = "文件 /etc/security/limits.d/20-nproc.conf 校验失败"
        if self.cmd('grep "DefaultLimitCORE=infinity" /etc/systemd/system.conf')[2] != 0:
            _err = "文件 /etc/systemd/system.conf DefaultLimitCORE 校验失败"
        if self.cmd('grep DefaultLimitNOFILE={0} /etc/systemd/system.conf'.format(file_max))[2] != 0:
            _err = "文件 /etc/systemd/system.conf DefaultLimitNOFILE 校验失败"
        if self.cmd('grep DefaultLimitNPROC={0} /etc/systemd/system.conf'.format(file_max))[2] != 0:
            _err = "文件 /etc/systemd/system.conf DefaultLimitNPROC 校验失败"

        assert _err == '', _err

    def valid_env_kernel(self):
        """ 校验内核参数 """
        _list = [i.strip() for i in self.read_file('/etc/sysctl.conf',
                                                   res='list') if not i.strip().startswith('#')]
        for i in KERNEL_PARAM.split('\n'):
            if i.startswith('#'):
                continue
            assert i.strip() in _list, "内核参数校验失败: {}".format(i)

    def valid_env_disable_selinux(self):
        """ 校验selinux """
        assert "SELINUX=disabled" in [
            i.strip() for i in self.read_file('/etc/selinux/config', res='list') if
            not i.strip().startswith('#')
        ], "selinux 校验失败"

    def valid_host_name(self):
        """校验host_name不含localhost"""
        _out, _err, _code = self.cmd("echo $(hostname)")
        assert _out.strip().lower() not in TO_MODIFY_HOST_NAME and not _out.strip().isdigit(), "校验主机名失败"


def add_hostname_analysis(hostname_str):
    logger.debug("传入主机信息：\n{}".format(hostname_str))
    hostnames = json.loads(hostname_str or '[]')
    with open("/etc/hosts", "r") as f:
        hosts = f.read()
    logger.debug("获取主机解析：\n{}".format(hosts))
    hosts_analysis_dict = {}
    for analysis_str in hosts.split("\n"):
        if analysis_str.lstrip().startswith("#"):
            continue
        analysis_list = list(
            filter(
                lambda x: x,
                analysis_str.strip().replace("\t", " ").split(" ")
            )
        )
        if not analysis_list:
            continue
        hosts_analysis_dict[analysis_list[0]] = analysis_str
    for hostname_dict in hostnames:
        ip = hostname_dict.get("ip")
        hostname = hostname_dict.get("hostname")
        host_analysis_str = hosts_analysis_dict.get(ip, "")
        if not host_analysis_str:
            hosts += "{} {}\n".format(ip, hostname)
        elif hostname in host_analysis_str:
            continue
        else:
            host_analysis_str_new = "{} {}".format(host_analysis_str, hostname)
            hosts = hosts.replace(host_analysis_str, host_analysis_str_new)
    logger.debug("对比获得最新主机信息：\n{}".format(hosts))
    with open("/etc/hosts", "w") as f:
        f.write(hosts)
    logger.debug("写入最新主机信息成功！")


def usage(error=None):
    script_full_path = os.path.join(CURRENT_DIR, os.path.basename(__file__))
    print("""{0} 脚本 功能为初始化节点，职能包括: 设置时区、关闭防火墙、设置文件具柄和内核参数等
    Command:
            init        <host_name>  <local_ip>  初始化节点
            valid                                校验初始化结果
            init_valid  <host_name>  <local_ip>  初始化节点，在完成初始化后执行校验

    Use "python {0} <command>" for more information about a given command.
    """.format(script_full_path))
    if error is not None:
        print("Error: {}".format(error))
        exit(1)
    exit(0)


def main():
    command_list = ('init', 'valid', 'init_valid', 'help', 'write_hostname')
    try:
        if sys.argv[1] not in command_list:
            usage(error='参数错误: {}'.format(sys.argv[1:]))
        if sys.argv[1] in ['init', 'init_valid']:
            if len(sys.argv) != 4:
                usage(error='参数错误: {}'.format(sys.argv[1:]))
            host_name = sys.argv[2]
            local_ip = sys.argv[3]
            init = InitHost(host_name, local_ip)
            init.run()
            if sys.argv[1] == 'init_valid':
                check = ValidInit()
                check.run()
                logger.info("valid success")
        elif sys.argv[1] == 'valid':
            check = ValidInit()
            check.run()
            logger.info("valid success")
        elif sys.argv[1] == "write_hostname":
            hosts_info = sys.argv[2]
            # '[{"ip":"10.0.9.18","hostname":"docp-9-18"}]'
            add_hostname_analysis(hosts_info)
        else:
            usage()
    except Exception as e:
        usage(error="参数错误, {}".format(e))


if __name__ == '__main__':
    main()
