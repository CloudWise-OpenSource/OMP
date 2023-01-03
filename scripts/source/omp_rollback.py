#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
import time
import sys
import logging
from abc import abstractmethod, ABCMeta

CURRENT_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
# 升级包路径
PROJECT_FOLDER = os.path.dirname(os.path.dirname(CURRENT_FILE_PATH))


class Logging:

    @staticmethod
    def log_new(app_name, path_log):
        logger = logging.getLogger(app_name)
        formatter = logging.Formatter('[%(asctime)s-%(levelname)s]: %(message)s')
        logger.setLevel(level=logging.INFO)
        file_handler = logging.FileHandler(path_log)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger


# 流程 检查状态 关闭进程前准备 关闭进程 备份 升级 升级整体恢复
class Common(metaclass=ABCMeta):

    def __init__(self, target_dir):
        """
        target_dir 目标跟路径
        base_dir 目标安装路径
        backup_dir 升级备份路径
        """
        self.base_dir = None
        self.bin = None
        self.target_dir = target_dir
        self.check_target_dir()
        self.target_data = os.path.join(self.target_dir, "data")
        self.target_log = os.path.join(self.target_dir, "logs")
        self.omp_conf = os.path.join(self.target_dir, "config/omp.yaml")
        self.backup_dir = os.path.join(PROJECT_FOLDER, 'backup', self.get_class_name())
        self.target_backup = os.path.join(self.target_dir, "back_new")
        _name = f"omp_rollback_{self.get_class_name()}"
        self.logger = Logging.log_new(_name,
                                      os.path.join(PROJECT_FOLDER, f"logs/{_name}.log"))
        if not os.path.exists(self.target_backup):
            self.sys_cmd('mkdir -p {0}'.format(self.target_backup))
        if not os.path.exists(self.backup_dir) and \
                self.backup_dir.rsplit("/", 1)[1] not in ["PreUpdate", "PostUpdate"]:
            print(f"备份路径不存在:{self.backup_dir},无法恢复")
            sys.exit(1)

    @abstractmethod
    def get_class_name(self):
        raise NotImplementedError("Must override get_class_name")

    def sys_cmd(self, cmd):
        """
        shell脚本输出
        :param cmd: linux命令
        :return:
        """
        shell = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = shell.communicate()
        stdout, stderr = bytes.decode(stdout), bytes.decode(stderr)
        exit_code = shell.poll()
        self.logger.info("执行cmd命令:{0},结果退出码:{1},执行详情:{2}".format(cmd, shell.poll(), stdout))
        if str(exit_code) != "0":
            print(f"{stderr},退出码:{exit_code}")
            sys.exit(1)
        return stdout

    def check_target_dir(self):
        try:
            dirs = os.listdir(self.target_dir)
            if 'omp_server' not in dirs or 'omp_web' not in dirs:
                print("此目标路径非标准安装路径")
                sys.exit(1)
        except Exception as e:
            print(f"路径异常，请检查路径，标准路径如/data/omp/ :{e}")

    def rollback(self):
        return

    def run(self):
        self.rollback()


class PreUpdate(Common):
    """
    检查前置条件
    """

    def __init__(self, target_dir):
        super().__init__(target_dir)
        self.target_dir = self.target_dir + "/" if self.target_dir[-1] != '/' else self.target_dir

    def get_class_name(self):
        return self.__class__.__name__

    def check_process(self):
        """
        检查进程是否存在，存在返回false 不存在返回true
        """
        cmd_str = f'ps -ef | grep {self.target_dir}|grep -v grep|wc -l'
        stdout = self.sys_cmd(cmd_str)
        if str(stdout).strip() == "0":
            return True
        return False

    def crontab_stop(self):
        cmd_str = f'crontab -l | grep -v "{self.target_dir}scripts/omp all start" 2>/dev/null | crontab -;'
        self.sys_cmd(cmd_str)

    def process_stop(self):
        cmd_str = f'bash {self.target_dir}scripts/omp all stop'
        self.sys_cmd(cmd_str)
        # ToDo 需要各个停止脚本完全输出停止时不存在延迟停止进程
        time.sleep(5)
        if self.check_process():
            return
        print("服务未停止成功，请检查服务并尝试手动停止进程")
        sys.exit(1)

    def run(self):
        self.crontab_stop()
        self.process_stop()


class Mysql(Common):
    def __init__(self, target_dir):
        super().__init__(target_dir)
        self.target_data = os.path.join(self.target_data, 'mysql')
        self.target_log = os.path.join(self.target_log, 'mysql')
        self.base_dir = os.path.join(self.target_dir, 'component/mysql')

    def get_class_name(self):
        return self.__class__.__name__

    def rollback(self):
        self.sys_cmd(
            "mv {0} {3}/mysqlbase  && mv {1} {3}/mysqldata   && mv {2} {3}/mysqllog".format(
                self.base_dir,
                self.target_data,
                self.target_log,
                self.target_backup
            ))
        self.sys_cmd(
            "mv {3}/mysqldata {0}  && mv {3}/mysqllogs {1}  && mv {3}/mysqlbase {2}".format(
                self.target_data, self.target_log, self.base_dir, self.backup_dir))


class OmpWeb(Common):
    def __init__(self, target_dir):
        super().__init__(target_dir)
        self.base_dir = os.path.join(self.target_dir, 'omp_web')

    def get_class_name(self):
        return self.__class__.__name__

    def rollback(self):
        self.sys_cmd(
            "mv {0} {1}/omp_web_base".format(
                self.base_dir,
                self.target_backup
            ))
        self.sys_cmd("mv {0}/omp_web_base {1}".format(self.backup_dir, self.base_dir))


class Tengine(Common):
    def __init__(self, target_dir):
        super().__init__(target_dir)
        self.base_dir = os.path.join(self.target_dir, 'component/tengine')

    def get_class_name(self):
        return self.__class__.__name__

    def rollback(self):
        self.sys_cmd("mv -f {0}/nginx {1}/sbin".format(self.backup_dir, self.base_dir))


class Redis(Common):
    def __init__(self, target_dir):
        super().__init__(target_dir)
        self.base_dir = os.path.join(self.target_dir, 'component/redis')

    def get_class_name(self):
        return self.__class__.__name__

    def rollback(self):
        self.sys_cmd(f"mv -f {self.backup_dir}/redis_base/bin_bak/redis* {self.base_dir}/bin")


class OmpServer(Common):
    def __init__(self, target_dir):
        super().__init__(target_dir)
        self.base_dir = os.path.join(self.target_dir, 'omp_server')

    def get_class_name(self):
        return self.__class__.__name__

    def rollback(self):
        self.sys_cmd(
            "mv {0} {1}/omp_server_base".format(
                self.base_dir,
                self.target_backup
            ))
        self.sys_cmd("mv {0}/omp_server_base {1}".format(self.backup_dir, self.base_dir))
        print(f"1. 请手动备份 mv {self.target_dir}/scripts {self.target_backup}/omp_scripts_bak")
        print(f"2. 请手动移动 mv {os.path.dirname(self.backup_dir)}/omp_scripts_bak {self.target_dir}/scripts")
        print(f"3. 请手动执行 bash {self.target_dir}/scripts/omp all restart")


class PostUpdate(Common):

    def get_class_name(self):
        return self.__class__.__name__

    def rollback(self):
        tmp_dir = f'{PROJECT_FOLDER}/crontab.txt'
        cmd_str = f'crontab -l > {tmp_dir} && echo "*/5 * * * * bash ' \
                  f'{self.target_dir}/scripts/omp &>/dev/null" >> {tmp_dir}'
        self.sys_cmd(cmd_str)
        self.sys_cmd(f'crontab {tmp_dir}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("参数异常，请提供正确的安装路径")
        sys.exit(1)
    t_dir = sys.argv[1]
    position = 0
    if len(sys.argv) >= 3:
        try:
            position = int(sys.argv[2])
        except Exception as e:
            print(f"请输入正确下标:{e}")
    exec_cls = [PreUpdate, Mysql, Redis, Tengine, OmpWeb, OmpServer, PostUpdate]
    exec_cls = exec_cls[position:]
    obj_ls = [cls(t_dir) for cls in exec_cls]
    [obj.run() for obj in obj_ls]
