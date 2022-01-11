# # -*- coding:utf-8 -*-
# # Project: backup_service
# # Author:lingyang.guo
# import logging
# import os
# import random
# import sys
# import pymysql
# import time
# import subprocess
#
# from utils.plugin.salt_client import SaltClient
# logger = logging.getLogger("server")
#
#
# class BackupDB(object):
#     def __init__(self, service_name_list, omp_backup_dir, env_id):
#         self.salt_client = SaltClient()
#         self.timeout = 300
#         self.service_name_list = service_name_list
#         self.omp_backup_dir = omp_backup_dir
#         self.env_id = env_id
#
#     @staticmethod
#     def select_data_from_database(sql):
#
#         return None  # TODO 补充逻辑
#
#     def cmd(self, command):
#         """执行shell 命令"""
#         logger.info("Exec command: {0}".format(command))
#         p = subprocess.Popen(
#             command,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             shell=True,
#         )
#         stdout, stderr = p.communicate()
#         _out, _err, _code = stdout, stderr, p.returncode
#         logger.error(
#             "Get command({0}) stdout: {1}; stderr: {2}; ret_code: {3}".format(
#                 command, _out, _err, _code
#             )
#         )
#         return _out, _err, _code
#
#     def backup_service(self, service_name):
#         tmp = time.strftime("%Y%m%d%H%M%S", time.localtime())+str(random.randint(1000, 9999))
#         service_dir = f"{self.omp_backup_dir}/{service_name}"
#         # 每个env_id进行备份
#         sql2 = """
#                 select
#                     ip
#                 from
#                     ruban_service
#                 where
#                     service_name = '{0}' and env_id = {1};
#                """.format(service_name, self.env_id)
#         ip_lists = []
#         data = self.select_data_from_database(sql2)
#         if not data:
#             logger.error(f"{sql2}执行后无数据")
#             return False, f"无法获取{service_name}关联的ip", ""
#         ip_lists = [i[0] for i in data if len(i) == 1]
#         # (ip, service_name）能唯一确定operation_uuid,所以2者组合唯一
#         # 获取每个(ip, service_name）的app_dir
#         logger(f"开始备份环境id为{self.env_id}中{service_name}")
#         count = 1
#         success = False
#         message = ""
#         for ip in ip_lists:
#             sql3 = """
#                     select
#                         app_dir, data_dir, run_user
#                     from
#                         ruban_install_info
#                     where
#                         env_id = '{}';
#                     """.format(self.env_id)
#
#             app_dir = ""
#             data = self.select_data_from_database(sql3)
#             if not data:
#                 logger.error(f"{sql3}执行后无数据")
#                 message += f"获取安装信息失败！"
#                 continue
#             app_dir, data_dir, run_user = [i for i in data if len(i) == 3][0]
#             if not all([app_dir, data_dir, run_user]):
#                 logger.error("app_dir, data_dir, run_user 未获取到")
#                 message += "获取安装信息失败！"
#                 continue
#             sql4 = """
#                     select
#                         username
#                     from
#                         ruban_host
#                     where
#                         ip = '{}';
#                     """.format(ip)
#             user_data = self.select_data_from_database(sql4)
#             if not user_data:
#                 logger.error(f"{sql4}执行后无数据")
#                 message += f"获取安装信息失败！"
#                 continue
#             username = user_data[0][0]
#             if username != "root":
#                 run_user = username
#             logger(f"开始备份环境id为:{self.env_id}中{ip}-{service_name}")
#             backup_dir = os.path.join(data_dir, "backupData")
#             # 循环利用salt查看每个ip服务进程是否存在，存在则开始备份；不存在则继续轮循
#             grep_key = f"{app_dir}/{service_name}"
#             if service_name == "arangodb" and len(ip_lists) > 1:
#                 grep_key = "arangodb/coordinator"
#             cmd_str = f"ps -ef | grep {grep_key} | grep -v 'grep' "
#             cmd_flag, cmd_msg = self.salt_client.cmd(
#                 target=ip, command=(cmd_str,), timeout=self.timeout
#             )
#             if not cmd_flag:
#                 logger.error(f"{ip}上的{service_name}进程不存在")
#                 message += f"{ip}上的{service_name}进程不存在！"
#                 logger(f"{ip}上的{service_name}进程不存在！")
#                 count += 1
#                 if count > len(ip_lists):
#                     message += f"{service_name}没有运行，无法备份!"
#                     logger(message, level="ERROR")
#                     logger.error(message)
#                     break
#                 continue
#             # 如果当前ip的服务进程存在，则获取当前服务的用户名、密码、端口
#             sql4 = """
#                     select
#                          service_user, service_pass, service_port
#                     from
#                         ruban_service
#                     where
#                         ip = '{0}' and service_name = '{1}';
#                    """.format(ip, service_name)
#             data = self.select_data_from_database(sql4)
#             if not data:
#                 logger.error(f"{sql4}执行后无数据")
#                 message += f"未找到ip为{ip}的服务{service_name}!"
#                 continue
#             data4 = data[0]
#             service_user, service_pass, service_port_dict = data4
#             file_name = ""
#             if service_name == 'arangodb':
#                 if not all(data4):
#                     message += f"{ip}上备份 arangodb,获取用户名、密码、端口数据不齐全!"
#                     logger(message)
#                     continue
#                 arangodb_port = eval(service_port_dict).get("endpoint")
#                 arangodb_port = arangodb_port
#                 arangodb_user = service_user
#                 arangodb_pwd = service_pass
#                 file_name = f"{service_name}-{ip}-{tmp}-{self.env_id}"
#                 cmd_str = f"test -d {backup_dir}/{file_name} || mkdir -p {backup_dir}/{file_name}&& chown -R {run_user}:{run_user} {backup_dir} && {app_dir}/arangodb/bin/arangodump --server.endpoint tcp://127.0.0.1:{arangodb_port} --server.username {arangodb_user} --server.password {arangodb_pwd} --all-databases true --output-directory {backup_dir}/{service_name}-{ip}-{tmp}-{self.env_id}"
#             elif service_name == "mysql":
#                 if not all([service_user, service_port_dict]):
#                     message += f"{ip}上备份 mysql,获取用户名、端口数据不齐全!"
#                     logger(message)
#                     continue
#                 service_port = eval(service_port_dict).get("service")
#                 file_name = f"{service_name}-{ip}-{tmp}-{self.env_id}.sql"
#                 cmd_str = f"test -d {backup_dir} || mkdir -p {backup_dir}&& chown -R {run_user}:{run_user} {backup_dir} && {app_dir}/mysql/bin/mysqldump --single-transaction -P{service_port} -u{service_user} -p{service_pass} -h'127.0.0.1' --all-databases > {backup_dir}/{service_name}-{ip}-{tmp}-{self.env_id}.sql"
#                 if not service_pass:
#                     cmd_str = f"test -d {backup_dir} || mkdir -p {backup_dir}&& chown -R {run_user}:{run_user} {backup_dir} && {app_dir}/mysql/bin/mysqldump --single-transaction -P{service_port} -u{service_user} -h'127.0.0.1' --all-databases  > {backup_dir}/{service_name}-{ip}-{tmp}-{self.env_id}.sql"
#             else:
#                 message += f"{service_name}暂不支持备份!"
#                 logger(message)
#                 logger.error(message)
#                 continue
#
#             backup_flag, backup_msg = self.salt_client.cmd(
#                 target=ip, command=(cmd_str,), timeout=self.timeout
#             )
#             if not backup_flag:
#                 message += f"{ip}上{service_name}备份失败!"
#                 logger(f"{message}, 详情为：{backup_msg}", level="ERROR")
#                 logger.error(f"{message},详情为：{backup_msg}")
#                 continue
#             time.sleep(1)
#             logger("开始同步节点备份数据到omp所在机器")
#             sync_flag, sync_msg = self.sync_data_with_omp(ip, backup_dir, file_name, service_dir,
#                                                           service_name, run_user)
#             if not sync_flag:
#                 logger.error(f"{sync_msg}")
#                 logger(f"同步节点备份数据到omp所在机器失败,{sync_flag}-{sync_msg}", level="ERROR")
#                 message += f"同步节点备份数据到omp所在机器失败!"
#                 continue
#             success = True
#             logger.info(f"{ip}上的{service_name}备份成功")
#             logger(f"{ip}上的{service_name}备份成功!")
#             break
#         if not success:
#             return False, message, ""
#         logger.info(f"备份服务{service_name}完成")
#         logger(f"备份服务{service_name}完成")
#         tar_name = f"{service_name}-{tmp}.tar.gz"
#         tar_flag, tar_msg = self.tar_c_dir(service_dir, tmp, service_name)
#         if not tar_flag:
#             logger.error(f"{tar_msg}")
#             return False, tar_msg, ""
#         logger(f"{service_name}完成备份")
#         return True, f"{service_name} of all env backup success ", tar_name
#
#     def sync_data_with_omp(self, ip, backup_dir, file_name, service_dir, service_name, run_user):
#         """同步节点备份数据到omp所在机器"""
#         # 1.先压缩备份目录中备份的数据
#         # file_name_real_path = os.path.join(backup_dir, file_name)
#         cmd_str = f"cd {backup_dir}; tar -zcf {file_name}.tar.gz {file_name} && chown -R {run_user}:{run_user} {file_name}.tar.gz && rm -rf {file_name}"
#         tar_flag, tar_msg = self.salt_client.cmd(
#             target=ip, command=(cmd_str,), timeout=self.timeout
#         )
#         if not tar_flag:
#             return False, tar_msg
#         logger("成功压缩备份目录中备份的数据")
#         # 2.将节点备份的数据同步到omp
#         source_path = os.path.join(backup_dir, f"{file_name}.tar.gz")
#         salt_data = self.salt_client.client.opts.get("root_dir")
#         upload_real_path = os.path.join(salt_data, f"var/cache/salt/master/minions/{ip}/files/*")
#         cp_flag, cp_msg = self.salt_client.cp_push(
#             target=ip, source_path=source_path, upload_path=f"{file_name}.tar.gz"
#         )
#         if not cp_flag:
#             return False, cp_msg
#         logger(f"成功将节点{source_path}备份的数据同步到omp {file_name}.tar.gz")
#         # 3.将主节点的备份数据同步到备份目录
#         # service_dir = f"{self.omp_backup_dir}/{self.service_name}"
#         _out, _err, _code = self.cmd(
#             f"test -d {service_dir} || mkdir -p {service_dir} && cp -rf {upload_real_path} {service_dir} && rm -rf {upload_real_path}")
#         if int(_code) != 0:
#             return False, _out
#         logger(f"{ip}下{service_name}备份完成")
#         return True, f"{ip}下{service_name}备份完成"
#
#     def tar_c_dir(self, dir_path, tmp, service_name):
#         # 将一种服务下的备份数据压缩为：服务名-时间.tar.gz
#         tar_dir_path = os.path.join(self.omp_backup_dir, f"{service_name}-{tmp}.tar.gz")
#         out, err, code = self.cmd(f"cd {dir_path} && tar -zcf {tar_dir_path} ./*")
#         if code != 0:
#             return False, err
#         return True, ""
#
#     def run(self):
#         for service_name in self.service_name_list:
#             backup_flag, back_msg, tar_name = self.backup_service(service_name)
#             if not backup_flag:
#                 return False, back_msg, ""
#
#         return True, "", tar_name
#
#
# if __name__ == '__main__':
#     args = sys.argv[1:]
#     if len(args) == 3:
#         backup_flag, back_msg, tar_name = BackupDB(service_name_list=eval(args[0]), omp_backup_dir=args[1], env_id=args[2]).run()
#         print(backup_flag, back_msg, tar_name)
#     else:
#         sys.exit(1)
