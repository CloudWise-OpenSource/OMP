import json
import os
import copy
import logging
import time
from django.db import transaction
from db_models.models import (
    MainInstallHistory, DetailInstallHistory,
    Service, ServiceConnectInfo,
    ApplicationHub, ClusterInfo, Env,
    ServiceHistory, Host
)
import random
from app_store.new_install_utils import RedisDB
from app_store.tasks import add_prometheus

logger = logging.getLogger('server')


class ManagerService:
    def __init__(self, info, is_extend=False):
        self.info = info
        self.is_extend = is_extend
        self.redis_obj = RedisDB()
        self.redis_key = "extend_" + str(int(time.time())) if is_extend else info.get("uuid", "")
        self.data = self.check_redis()[1]
        self.service_cluster_ip, self.app_instance_dc = self._get_cluster_ip()
        self.env = None
        self.is_base_env = ApplicationHub.objects.filter(
            is_base_env=True).values_list("app_name", flat=True)

    @staticmethod
    def _get_cluster_ip():
        """
        "jdk:{1:["192.168.0.1","192.168.0.2"]}"
        """
        app_dc = {}
        app_instance_dc = {}
        service_all = Service.objects.all().values_list("ip", "cluster", "cluster__cluster_service_name",
                                                        "service_instance_name")
        for app in service_all:
            # 新纳管专属逻辑通过服务实例名匹配
            app_instance_dc[app[3]] = app[1]
            if app[1]:
                app_dc.setdefault(app[2], {}).setdefault(app[1], []).append(app[0])
        return app_dc, app_instance_dc

    def check_redis(self):
        if self.is_extend:
            return True, self.info
        res, redis_data = self.redis_obj.get(self.redis_key)
        if not res:
            return False, {"is_error": True,
                           "message": "redis中不存在需要纳管的数据或超时"}
        # 兼容新版本纳管
        for rd in redis_data:
            app_name = rd["app_name"]
            for i in self.info["ser_info"]:
                if i["name"] == app_name:
                    rd.update({
                        "exist_instance": i["exist_instance"],
                        "is_use_exist": i["is_use_exist"]
                    })
        return True, redis_data

    def check_service(self):
        for i in self.info["ser_info"]:
            if len(i["exist_instance"]) > 1:
                return False, {
                    "is_error": True,
                    "message": f"{i['name']}仅可勾选单个实例"}
            if i["is_use_exist"] and len(i["exist_instance"]) == 0:
                return False, {
                    "is_error": True,
                    "message": f"{i['name']}选择与现有实例组成集群，但未选择集群实例"}
        for data in self.data:
            if data.get("error_msg"):
                return False, {
                    "is_error": True,
                    "message": "存在有扫描异常的服务"}
        return True, ""

    @staticmethod
    def update_port(app_obj, app_data):
        service_ports = json.loads(app_obj.app_port) if app_obj.app_port else []
        for service_port in service_ports:
            if service_port.get('key') == 'service_port':
                service_port['default'] = app_data['install_args'].get('service_port')
        return json.dumps(service_ports)

    @staticmethod
    def update_service_controllers(app_obj, app_data):
        _app_controllers = json.loads(app_obj.app_controllers) if app_obj.app_controllers else []
        real_home = app_data['install_args'].get('base_dir')
        _new_controller = dict()
        for key, value in _app_controllers.items():
            if not value:
                continue
            _new_controller[key] = os.path.join(real_home, value)
        return _new_controller

    @staticmethod
    def update_install_args(app_obj, install_detail_args):
        install_detail_keys = ["base_dir", "data_dir", "log_dir", "run_user"]
        json_install_args = json.loads(app_obj.app_install_args)
        for install_args in json_install_args:
            if install_args.get('key') in install_detail_keys:
                install_args['default'] = install_detail_args.get(install_args.get('key'), "")
        return json_install_args

    def create_install_detail(self, main_obj, install_detail_args, ser_obj, copy_data, app_obj):

        data_dir = Host.objects.filter(ip=ser_obj.ip).first().data_folder
        cluster_name = ""
        if ser_obj.cluster:
            cluster_name = ser_obj.cluster.cluster_service_name
        install_detail = {
            "ip": ser_obj.ip,
            "name": app_obj.app_name,
            "ports": json.loads(copy_data['service_port']),
            "version": app_obj.app_version,
            "install_args": self.update_install_args(app_obj, install_detail_args),
            "instance_name": ser_obj.service_instance_name,
            "data_folder": data_dir,
            "cluster_name": cluster_name
        }
        now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        install_status = DetailInstallHistory.INSTALL_STATUS_INSTALLING
        msg = "开始扩容"
        if not self.is_extend:
            install_status = DetailInstallHistory.INSTALL_STATUS_SUCCESS
            ServiceHistory.objects.create(
                username="admin",
                description=f"执行 纳管 操作",
                result="success",
                created=now_time,
                service=ser_obj
            )
            msg = "纳管成功"

        DetailInstallHistory.objects.create(
            service=ser_obj,
            main_install_history=main_obj,
            install_step_status=install_status,
            send_msg=f"{now_time} {app_obj.app_name} {msg}",
            install_detail_args=install_detail
        )

    def get_service_dependence(self, dependence, ip):
        dependence_json = []
        for de in dependence:
            for app, hosts_name in de.items():
                ser_obj = Service.objects.filter(service_instance_name=hosts_name[0]).first()
                # 是集群
                if ser_obj.cluster:
                    dependence_json.append({"name": app,
                                            "cluster_name": ser_obj.cluster.cluster_name,
                                            "instance_name": None
                                            })
                # 基础组件本地
                elif app in self.is_base_env:
                    dependence_json.append({"name": app,
                                            "cluster_name": None,
                                            "instance_name": f"{app}-{ip.split('.')[2]}-{ip.split('.')[3]}"
                                            })
                else:
                    dependence_json.append({"name": app,
                                            "cluster_name": None,
                                            "instance_name": hosts_name[0]
                                            })
        return json.dumps(dependence_json)

    @staticmethod
    def get_or_create_service_connect_info(app_name, app_obj):
        # ToDo 多环境连接信息问题
        infos = {"username", "password", "username_enc", "password_enc"}
        connect_infos = {}
        for app_info in json.loads(app_obj.app_install_args):
            key = app_info.get("key")
            if key in infos:
                connect_infos[f"service_{key}"] = app_info.get("default")
        conn_obj = None
        if connect_infos:
            # ToDO 判断同同样连接信息时，当前服务归属哪个集群
            conn_obj = ServiceConnectInfo.objects.filter(
                service_name=app_name, **connect_infos).first()
            if not conn_obj:
                conn_obj = ServiceConnectInfo.objects.create(
                    service_name=app_name,
                    **connect_infos
                )
        return conn_obj

    def create_cluster_new(self, app_obj, app_data, app_name, real_ip_ls):
        # real_ip_ls 1 单机不考虑
        # real_ip_ls 1 exist_instance 1 单机转集群合并 需创建集群
        # real_ip_ls >1 exist_instance 0 集群
        # real_ip_ls >1 exist_instance >0 集群合并
        is_use_exist = app_data.pop("is_use_exist")
        exist_instance = app_data.pop("exist_instance")
        if is_use_exist or len(real_ip_ls) > 1:
            # 判断当前需要融合的实例是否存在集群,无则创建,必返回集群
            exist_instance = exist_instance[0] if exist_instance else 0
            cluster_id = self.app_instance_dc.get(exist_instance)
            # 没有集群需要创建，或者确定集群并且不合并集群的但数量大于1。
            if not cluster_id or not is_use_exist:
                cluster_obj = ClusterInfo.objects.create(
                    cluster_service_name=app_name,
                    cluster_name=f"{app_name}-cluster-{''.join(random.sample('ABCDEFGHIJKLMNQPQRSTUVWXYZ1234567890', 10))}",
                    service_connect_info=self.get_or_create_service_connect_info(app_name, app_obj)
                )
                # 实例存在但不存在集群
                if exist_instance:
                    Service.objects.filter(
                        service_instance_name=exist_instance).update(cluster=cluster_obj)
            else:
                cluster_obj = ClusterInfo.objects.filter(id=cluster_id).first()
            return True, cluster_obj
        # 看大小返回
        else:
            return False, [f"{app_name}-{real_ip_ls[0].split('.')[2]}-{real_ip_ls[0].split('.')[3]}"]

    def create_cluster(self, app_obj, app_data, app_name, real_ip_ls):
        cluster_instance_name = []
        for key, v in app_data.items():
            if key.startswith(f'{app_name}'):
                cluster_instance_name = [key, v]
        if cluster_instance_name:
            app_data.pop(cluster_instance_name[0])
        if not app_data.get("is_use_exist") is None:
            return self.create_cluster_new(app_obj, app_data, app_name, real_ip_ls)
        # 此为纳管集群
        cluster_obj = None
        if set(cluster_instance_name[1]) & set(real_ip_ls) != set(cluster_instance_name[1]):
            for c_id, ips in self.service_cluster_ip.get(app_name, {}).items():
                if list(set(cluster_instance_name[1]) - set(real_ip_ls))[0] in ips:
                    cluster_obj = ClusterInfo.objects.filter(id=c_id).first()
        elif len(cluster_instance_name[1]) > 1:
            cluster_obj = ClusterInfo.objects.create(
                cluster_service_name=app_name,
                cluster_name=cluster_instance_name[0],
                service_connect_info=self.get_or_create_service_connect_info(app_name, app_obj)
            )
        else:
            return False, cluster_instance_name
        return True, cluster_obj

    def get_or_create_env(self):
        if self.env:
            return self.env
        queryset = Env.objects.filter(id=1)
        if queryset.exists():
            return queryset.first()
        return Env.objects.create(id=1, name="default")

    def create_database_one(self, data, main_obj):
        app_name = data.pop("app_name")
        app_version = data.pop("app_version")
        real_ip_ls = data.pop("app_ip", [])
        dependence = data.pop("dependence_instance")
        app_obj = ApplicationHub.objects.filter(
            app_name=app_name, app_version=app_version).first()
        data['service_port'] = self.update_port(app_obj, data)
        data['service_controllers'] = self.update_service_controllers(app_obj, data)
        data['env'] = self.get_or_create_env()
        res, cls_obj = self.create_cluster(app_obj, data, app_name, real_ip_ls)
        if res:
            data["cluster"] = cls_obj
        else:
            data["service_instance_name"] = cls_obj[0]
        data["service_connect_info"] = self.get_or_create_service_connect_info(app_name, app_obj)
        data["service_status"] = Service.SERVICE_STATUS_INSTALLING \
            if self.is_extend else Service.SERVICE_STATUS_NORMAL
        for ip in real_ip_ls:
            # ToDo 未设置vip的选项
            copy_data = copy.deepcopy(data)
            if not copy_data.get("service_instance_name"):
                copy_data["service_instance_name"] = f"{app_name}-{ip.split('.')[2]}-{ip.split('.')[3]}"
            copy_data["service_dependence"] = self.get_service_dependence(dependence, ip)
            copy_data['service'] = app_obj
            copy_data["ip"] = ip
            # ToDo Role 和 vip的
            copy_data["service_role"] = ""
            install_detail_args = copy_data.pop("install_args")
            ser_obj = Service.objects.create(
                **copy_data
            )
            # 创建detail表
            self.create_install_detail(main_obj, install_detail_args, ser_obj, copy_data, app_obj)

    def create_database_all(self):
        # main表 相关联的服务表 信息集群表，然后detail表
        with transaction.atomic():
            main_obj = MainInstallHistory.objects.create(
                operator="admin",
                operation_uuid=self.redis_key,
                install_status=MainInstallHistory.INSTALL_STATUS_INSTALLING
            )
            #                "dependence_instance": de_dc,
            #    "app_name": app,
            #    "app_version": version,
            #    "app_ip": [ip],
            #    "install_args": install_args
            for data in self.data:
                data.pop("error_msg")
                self.create_database_one(data, main_obj)
            if not self.is_extend:
                main_obj.install_status = MainInstallHistory.INSTALL_STATUS_SUCCESS
            main_obj.save()
        try:
            add_prometheus(main_obj.id)
        except Exception as e:
            logger.error(f"纳管服务注册失败:{e}")
        return main_obj.id

    def run(self):
        res, data = self.check_redis()
        if res:
            res, data = self.check_service()
        if not res:
            return data
        main_id = self.create_database_all()
        if self.is_extend:
            return main_id
        self.redis_obj.delete_keys(self.redis_key)
        return {"is_error": False,
                "message": "服务纳管成功"}
