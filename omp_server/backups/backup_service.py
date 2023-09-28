# # -*- coding:utf-8 -*-
# # Project: backup_service
import logging
import random
import time
import json

"""
if __name__ == '__main__':
    import django

    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_DIR = os.path.dirname(CURRENT_DIR)
    PYTHON_PATH = os.path.join(PROJECT_DIR, "component/env/bin/python3")
    MANAGE_PATH = os.path.join(PROJECT_DIR, "omp_server/manage.py")
    sys.path.append(os.path.join(PROJECT_DIR, "omp_server"))

    # 加载Django环境
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omp_server.settings")
    django.setup()


from db_models.models.install import DetailInstallHistory
from utils.plugin.salt_client import SaltClient

logger = logging.getLogger("server")


class BackupDB(object):
    def __init__(self):
        self.salt_client = SaltClient()
        self.timeout = 300
        self.service_names = []
        self.upload_real_paths = []

    @staticmethod
    def get_backup_info(service_obj):
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



    def backup_service(self, back_id):
        back_obj = BackupHistory.objects.filter(id=back_id).first()
        service_instances = back_obj.content
        omp_backup_dir = back_obj.retain_path
        for si in service_instances:
            service_obj = Service.objects.filter(
                service_instance_name=si).first()

            service_dict = self.get_backup_info(service_obj)
            cmd_str = {}
            if isinstance(service_dict, dict):
                if service_obj.service.app_name == "mysql":
                    cmd_str = "test -d {backup_dir} || mkdir -p {backup_dir}&& " \
                              "chown -R {run_user}:{run_user} {backup_dir} &&" \
                              " {app_dir}/bin/mysqldump --single-transaction " \
                              "-P{service_port} -u{service_user} {service_pass} -h'127.0.0.1' --all-databases > " \
                              "{backup_dir}/{service_name}-{ip}-{tmp}.sql".format(
                        **service_dict)
                    service_dict["file_name"] = "{service_name}-{ip}-{tmp}.sql".format(
                        **service_dict)

                elif service_obj.service.app_name == "arangodb":
                    cmd_str = "test -d {backup_dir}/{service_name}-{ip}-{tmp} || " \
                              "mkdir -p {backup_dir}/{service_name}-{ip}-{tmp}&& " \
                              "chown -R {run_user}:{run_user} {backup_dir} " \
                              "&& {app_dir}/bin/arangodump --server.endpoint " \
                              "tcp://127.0.0.1:{service_port} --server.username {service_user}" \
                              " --server.password {arangodb_pwd} --all-databases true " \
                              "--output-directory {backup_dir}/{service_name}-{ip}-{tmp}".format(
                        **service_dict)
                    service_dict["file_name"] = "{service_name}-{ip}-{tmp}".format(
                        **service_dict)
                elif service_obj.service.app_name == "postgreSql":
                    cmd_str = "test -d {backup_dir} || mkdir -p {backup_dir}&& " \
                              "chown -R {run_user}:{run_user} {backup_dir} &&" \
                              " {app_dir}/bin/pg_dumpall -U {run_user} -h'127.0.0.1' -p{service_port} > " \
                              "{backup_dir}/{service_name}-{ip}-{tmp}.sql".format(
                        **service_dict)
                    service_dict["file_name"] = "{service_name}-{ip}-{tmp}.sql".format(
                        **service_dict)
                else:
                    # TODO 应用不合法
                    pass
            backup_flag, backup_msg = self.salt_client.cmd(
                target=service_dict.get("ip"), command=(cmd_str,), timeout=self.timeout
            )
            if not backup_flag:
                message = f'{service_dict.get("ip")}上{service_dict.get("service_name")}备份失败!'
                logger.error(f"{message}, 详情为：{backup_msg}")
                return False, message
            # 同步数据
            sync_flag, sync_msg = self.sync_data_with_omp(service_dict)
            # print(cmd_str)
            if not sync_flag:
                message = f'{service_dict.get("ip")}上{service_dict.get("service_name")}备份失败!'
                logger.error(f"{message}, 详情为：{sync_msg}")
                return False, message

        # 3.将主节点的备份数据同步到备份目录
        file_name = back_obj.file_name
        name = file_name.replace(".tar.gz", "")
        template_dir = os.path.join(
            omp_backup_dir, name)
        upload_real_paths = " ".join(self.upload_real_paths)
        if len(template_dir) <= 5 or len(upload_real_paths) <= 5:
            return False, "目录异常，防止保护文件丢失触发熔断." \
                          "template_dir:template_dir:{0},upload_real_paths:{1}".format(
                template_dir, upload_real_paths
            )
        cmd_str = "test -d {0} || mkdir -p {0} && cp -rf {1} {0} && rm -rf {1} && cd {2}" \
                  " && tar -zcf {3} {4} && rm -rf {0}".format(
            template_dir, upload_real_paths, omp_backup_dir, file_name, name)
        _out, _err, _code = cmd(
            cmd_str
        )
        logger.info(f"执行合并备份文件命令{cmd_str}")
        if int(_code) != 0:
            return False, _out
        logger.info(f"{''.join(self.service_names)}备份完成")
        return True, "Success"
"""
