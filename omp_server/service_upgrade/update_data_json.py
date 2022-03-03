import json
import os

from django.conf import settings

from db_models.models import DetailInstallHistory, Service, Host, UpgradeDetail
from utils.plugin.salt_client import SaltClient


class DataJsonUpdate(object):
    """ 生成data.json数据 """

    def __init__(self, operation_uuid):
        """
        data.json数据生成方法
        :param operation_uuid: 唯一操作uuid
        :type operation_uuid: str
        """
        self.json_name = f"{operation_uuid}.json"
        self.data_path = os.path.join("data_files", self.json_name)

    def get_ser_install_args(self, obj, app_install_args=None):
        """
        获取服务的安装参数
        :param obj: Service obj
        :param app_install_args: app_install_args, list
        :return:
        """
        deploy_detail = DetailInstallHistory.objects.get(service=obj)
        install_args = \
            deploy_detail.install_detail_args.get("install_args")
        old_arg_dict = {}
        for old_arg in install_args:
            old_arg_dict[old_arg["key"]] = old_arg
        if app_install_args:
            for new_arg in app_install_args:
                if new_arg.get("key") not in old_arg_dict:
                    install_args.append(new_arg)
        deploy_mode = \
            deploy_detail.install_detail_args.get("deploy_mode")
        return {
            "install_args": install_args,
            "deploy_mode": deploy_mode
        }

    def parse_single_service(self, service, tag_app=None):
        """
        解析单个服务数据
        :param server: Service
        :param tag_app: Service
        :return:
        """
        _ser_dic = {
            "ip": service.ip,
            "name": service.service.app_name,
            "role": service.service_role if service.service_role else "master",
            "instance_name": service.service_instance_name,
            "cluster_name": service.cluster.cluster_name if service.cluster else None,
            "vip": service.vip,
            "ports": json.loads(service.service_port or '[]'),
            "dependence": json.loads(service.service_dependence or '[]'),
        }
        if service.service.app_name == "hadoop":
            _ser_dic["instance_name"] = \
                "hadoop-" + "-".join(service.ip.split(".")[-2:])
        if tag_app:
            _ser_dic["ports"] = service.update_port(
                json.loads(tag_app.app_port or '[]')
            )
            _ser_dic["dependence"] = service.update_dependence(
                service.service_dependence,
                json.loads(tag_app.app_dependence or '[]')
            )
            _others = self.get_ser_install_args(
                service, json.loads(tag_app.app_install_args or '[]'))
        else:
            _others = self.get_ser_install_args(service)
        _ser_dic.update(_others)
        return _ser_dic

    def parse_hadoop_service(self, service, role, ports, tag_app=None):
        _ser_dic = self.parse_single_service(service, tag_app)
        _ser_dic.update(role=role)
        _ser_dic.update(ports=ports)
        return _ser_dic

    def make_data_json(self, json_lst):
        """
        创建data.json数据文件
        :param json_lst: 服务及分布信息组成的列表
        :type json_lst: list
        :return:
        """
        _path = os.path.join(
            settings.PROJECT_DIR,
            "package_hub",
            self.data_path
        )
        if not os.path.exists(os.path.dirname(_path)):
            os.makedirs(os.path.dirname(_path))
        with open(_path, "w", encoding="utf8") as fp:
            json.dump(json_lst, fp, ensure_ascii=False, indent=2)

    def decompose_detail(self, details):
        _dic = {}
        if not details:
            return _dic
        for detail in details:
            if isinstance(detail, UpgradeDetail):
                _dic[detail.service.service_instance_name] = detail.target_app
            else:
                _dic[detail.upgrade.service.service_instance_name] = \
                    detail.current_app
        return _dic

    def load_json_lst(self, details):
        # 在json文件中标记该服务所在主机上的agent的地址
        ip_agent_dir_dir = {
            ip: agent_dir for ip, agent_dir in
            Host.objects.values_list("ip", "agent_dir")
        }
        json_lst = list()
        services = Service.objects.exclude(service__app_name="hadoop")
        for service in services:
            tag_app = details.get(service.service_instance_name)
            _item = self.parse_single_service(service, tag_app)
            _item["agent_dir"] = ip_agent_dir_dir.get(_item.get("ip"))
            json_lst.append(_item)
        hadoop_services = Service.objects.filter(service__app_name="hadoop")
        hadoop_info = {}
        for hadoop_service in hadoop_services:
            role = hadoop_service.service_instance_name.split("_")[0]
            port = json.loads(hadoop_service.service_port or '[]')
            if not hadoop_info.get(hadoop_service.ip):
                hadoop_info[hadoop_service.ip] = {
                    "role": role, "ports": port, "service": hadoop_service}
            else:
                hadoop_info[hadoop_service.ip]["role"] += f",{role}"
                hadoop_info[hadoop_service.ip]["ports"].extend(port)
        for ip, service_info in hadoop_info.items():
            service = service_info.get("service")
            hadoop_app = details.get(service.service_instance_name)
            _item = self.parse_hadoop_service(
                **service_info, tag_app=hadoop_app)
            _item["agent_dir"] = ip_agent_dir_dir.get(_item.get("ip"))
            json_lst.append(_item)
        return json_lst

    def send_data_json_target(self, salt_obj, target_ip):
        host = Host.objects.get(ip=target_ip)
        json_target_path = os.path.join(
            host.data_folder, "omp_packages", self.json_name)
        return salt_obj.cp_file(
            target=target_ip,
            source_path=self.data_path,
            target_path=json_target_path
        )

    def send_data_json_all(self):
        hosts = Host.objects.all().values_list("ip", "data_folder")
        fail_message = []
        salt_obj = SaltClient()
        for host in hosts:
            json_target_path = os.path.join(
                host[1], "omp_packages", self.json_name)
            state, message = salt_obj.cp_file(
                target=host[0],
                source_path=self.data_path,
                target_path=json_target_path
            )
            if not state:
                fail_message.append(
                    f"ip:{host[1]}更新data.json失败，错误：{message}")
        return fail_message

    def run(self, details=None):
        """
        更新data.json
        :param details: 升级details
        :return:
        """
        details = self.decompose_detail(details)
        current_json_lst = self.load_json_lst(details)
        # step2: 生成data.json
        self.make_data_json(json_lst=current_json_lst)
