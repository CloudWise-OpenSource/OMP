import json
import os

from django.conf import settings

from db_models.models import DetailInstallHistory, Service, Host, UpgradeDetail


class DataJsonUpdate(object):
    """ 生成data.json数据 """

    def __init__(self, operation_uuid):
        """
        data.json数据生成方法
        :param operation_uuid: 唯一操作uuid
        :type operation_uuid: str
        """
        self.operation_uuid = operation_uuid

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

    def make_data_json(self, json_lst):
        """
        创建data.json数据文件
        :param json_lst: 服务及分布信息组成的列表
        :type json_lst: list
        :return:
        """
        _path = os.path.join(
            settings.PROJECT_DIR,
            "package_hub/data_files",
            f"{self.operation_uuid}.json"
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
        services = Service.objects.all()
        # 在json文件中标记该服务所在主机上的agent的地址
        ip_agent_dir_dir = {
            ip: agent_dir for ip, agent_dir in
            Host.objects.values_list("ip", "agent_dir")
        }
        json_lst = list()
        for service in services:
            tag_app = details.get(service.service_instance_name)
            _item = self.parse_single_service(service, tag_app)
            _item["agent_dir"] = ip_agent_dir_dir.get(_item.get("ip"))
            json_lst.append(_item)
        return json_lst

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
