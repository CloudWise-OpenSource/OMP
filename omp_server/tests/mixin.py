"""
单元测试资源模拟混入类
"""
import time
import json
import random
from db_models.models import (
    Host, Env, Labels, Service, ServiceHistory, GrafanaMainPage,
    ClusterInfo, ApplicationHub, ProductHub, UploadPackageHistory,
    MainInstallHistory, DetailInstallHistory
)
from utils.plugin.crypto import AESCryptor


class HostsResourceMixin:
    """ 主机资源混入类 """

    INSTANCE_NAME_START = "t_host"
    IP_START = "127"

    def get_hosts(self, number=20, env_id=None):
        """
        获取主机
        :param number: 创建数量
        :param env_id: 环境实例
        """
        # 获取环境信息
        env = None
        if env_id:
            env = Env.objects.filter(id=env_id).first()
        if not env:
            env = Env.objects.filter(id=1).first()
        # 创建主机
        aes_crypto = AESCryptor()
        host_ls = []
        agent_status_ls = list(map(lambda x: x[0], Host.AGENT_STATUS_CHOICES))
        for index in range(number):
            index += 1
            host_ls.append(Host(
                instance_name=f"{self.INSTANCE_NAME_START}_{index}",
                ip=f"{self.IP_START}.0.0.{index}",
                port=36000,
                username=f"root{index}",
                password=aes_crypto.encode(f"password_{index}"),
                data_folder="/data",
                operate_system="CentOS",
                env=env,
                service_num=random.randint(0, 100),
                alert_num=random.randint(0, 100),
                host_agent=random.choice(agent_status_ls),
                monitor_agent=random.choice(agent_status_ls),
            ))
        Host.objects.bulk_create(host_ls)
        return Host.objects.filter(
            instance_name__startswith=self.INSTANCE_NAME_START)

    def destroy_hosts(self):
        """ 销毁主机 """
        Host.objects.filter(
            instance_name__startswith=self.INSTANCE_NAME_START).delete()


class HostBatchRequestMixin:
    """ 主机批量请求混入类 """

    @staticmethod
    def get_host_batch_request(number, row=False):
        """ 模拟请求信息 """
        host_list = []
        for i in range(number):
            data = {
                "instance_name": f"host_new_{i}",
                "ip": f"10.10.10.{i}",
                "port": 36000,
                "username": "root",
                "password": "root_password",
                "data_folder": "/data",
                "operate_system": random.choice(("CentOS", "RedHat"))
            }
            if row:
                data["row"] = i + 1
            host_list.append(data)
        return {"host_list": host_list}


class GrafanaMainPageResourceMixin:
    """ Grafana 主面板资源混入类 """

    INSTANCE_NAME_TUPLE = ("node", "service", "log", "mysql")
    INSTANCE_URL_CONTAIN = "t_grafana"

    def get_grafana_main_pages(self):
        """ 获取面板信息 """
        grafana_main_page_ls = []
        for instance_name in self.INSTANCE_NAME_TUPLE:
            grafana_main_page_ls.append(GrafanaMainPage(
                instance_name=instance_name,
                instance_url=f"/proxy/v1/{self.INSTANCE_URL_CONTAIN}/d/{instance_name}-url"
            ))
        GrafanaMainPage.objects.bulk_create(grafana_main_page_ls)
        return GrafanaMainPage.objects.filter(
            instance_name__in=self.INSTANCE_NAME_TUPLE,
            instance_url__contains=self.INSTANCE_URL_CONTAIN)

    def destroy_grafana_main_pages(self):
        """ 销毁面板信息 """
        GrafanaMainPage.objects.filter(
            instance_name__in=self.INSTANCE_NAME_TUPLE,
            instance_url__contains=self.INSTANCE_URL_CONTAIN).delete()


class LabelsResourceMixin:
    """ 标签资源混入类 """

    LABEL_NAME_START = "t_label"

    def get_labels(self, number=10, label_type=None):
        """
        获取标签
        :param number: 创建数量
        :param label_type: 类型
        """
        label_ls = []
        for index in range(number):
            if label_type is None:
                label_type = random.choice(
                    Labels.LABELS_CHOICES)[0]
            index += 1
            label_ls.append(Labels(
                label_type=label_type,
                label_name=f"{self.LABEL_NAME_START}_{index}"
            ))
        Labels.objects.bulk_create(label_ls)
        return Labels.objects.filter(
            label_name__startswith=self.LABEL_NAME_START)

    def destroy_labels(self):
        """ 销毁标签 """
        Labels.objects.filter(
            label_name__startswith=self.LABEL_NAME_START).delete()


class UploadPackageHistoryMixin:
    """ 上传安装包记录资源混入类 """

    PACKAGE_NAME_START = "t_pkg"

    def get_upload_package_history(self, number=20, is_many=True):
        """
        获取上传安装包记录
        :param number: 创建数量
        :param is_many: 是否单次多个上传
        """
        history_ls = []
        for index in range(number):
            index += 1
            # 短暂休眠，避免毫秒级时间戳重复
            time.sleep(0.01)
            opera_uuid = str(int(round(time.time() * 1000)))
            # 模拟单次多个安装包数量
            pkg_number = 1
            if is_many:
                pkg_number = random.randint(3, 5)
            for package_number in range(pkg_number):
                package_number += 1
                history_ls.append(UploadPackageHistory(
                    operation_uuid=opera_uuid,
                    operation_user="admin",
                    package_name=f"{self.PACKAGE_NAME_START}_{index}_{package_number}",
                    package_md5=f"{self.PACKAGE_NAME_START}_{index}_{package_number}_md5",
                    package_path=f"/data/app/{package_number}"
                ))
        UploadPackageHistory.objects.bulk_create(history_ls)
        return UploadPackageHistory.objects.filter(
            package_name__startswith=self.PACKAGE_NAME_START)

    def destroy_upload_package_history(self):
        """ 销毁上传安装包记录 """
        UploadPackageHistory.objects.filter(
            package_name__startswith=self.PACKAGE_NAME_START).delete()


class ApplicationResourceMixin(LabelsResourceMixin, UploadPackageHistoryMixin):
    """ 应用资源混入类 """
    APP_NAME_START = "t_app"

    def _mock_install_info(self, index):
        """ 模拟应用安装信息 """
        install_info = []
        install_key_ls = ("base_dir", "log_dir", "data_dir",
                          "username", "password")
        for key in install_key_ls:
            default = f"/data/app/{self.APP_NAME_START}{index}"
            if key == "username":
                default = "root"
            if key == "password":
                default = "rootPassword"
            install_info.append({
                "name": "xxx",
                "key": key,
                "default": default,
            })
        return json.dumps(install_info)

    def _create_application(self, index, is_release, app_type, label_ls, app_package, app_version):
        """ 创建应用 """
        if app_type is None:
            app_type = random.choice(
                ApplicationHub.APP_TYPE_CHOICES)[0]
        if is_release is None:
            is_release = random.choice((True, False))
        # 随机模拟冗余字段
        extend_fields = {
            "base_env": random.choice((
                True, False, "True", "False"
            ))
        }
        app_obj = ApplicationHub(
            is_release=is_release,
            app_type=app_type,
            app_name=f"{self.APP_NAME_START}_{index}",
            app_version=app_version,
            app_description="应用描述，省略一万字...",
            app_logo="app log svg data...",
            app_install_args=self._mock_install_info(index),
            extend_fields=extend_fields,
            app_package=app_package,
        )
        app_obj.save()
        # 随机模拟属于多种标签情况
        label_obj_ls = random.sample(
            list(label_ls), random.randint(1, 2))
        for label in label_obj_ls:
            app_obj.app_labels.add(label.id)
            app_obj.save()
        return app_obj

    def get_application(self, number=20, app_type=None, is_release=None):
        """
        获取应用
        :param number: 创建数量
        :param app_type: 类型
        :param is_release: 是否发布
        """
        label_ls = self.get_labels(
            label_type=Labels.LABEL_TYPE_COMPONENT)
        # 创建上传包记录
        upload_history_ls = self.get_upload_package_history(
            number=number, is_many=False)
        for index in range(number):
            app_package = upload_history_ls[index]
            index += 1
            self._create_application(
                index, is_release, app_type, label_ls,
                app_package=app_package, app_version="1.0")
        # 随机模拟多个版本情况
        random_app_ls = random.sample(
            list(range(number)),
            random.randint(0, number // 2 + 1))
        # 创建上传包记录
        upload_history_ls = self.get_upload_package_history(
            number=len(random_app_ls), is_many=False)
        for index in random_app_ls:
            app_package = upload_history_ls[index]
            index += 1
            self._create_application(
                index, is_release, app_type, label_ls,
                app_package=app_package, app_version="2.0")
        return ApplicationHub.objects.filter(
            app_name__startswith=self.APP_NAME_START)

    def destroy_application(self):
        """ 销毁应用 """
        ApplicationHub.objects.filter(
            app_name__startswith=self.APP_NAME_START).delete()
        self.destroy_upload_package_history()
        self.destroy_labels()


class ProductResourceMixin(LabelsResourceMixin, UploadPackageHistoryMixin):
    """ 产品资源混入类 """
    PRO_NAME_START = "t_pro"

    def _create_product(self, index, is_release, label_ls, pro_package, pro_version):
        if is_release is None:
            is_release = random.choice((True, False))
        pro_obj = ProductHub(
            is_release=is_release,
            pro_name=f"{self.PRO_NAME_START}_{index}",
            pro_version=pro_version,
            pro_description="产品描述，省略一万字...",
            pro_logo="pro log svg data",
            pro_package=pro_package,
        )
        pro_obj.save()
        # 随机模拟属于多种标签情况
        label_obj_ls = random.sample(
            list(label_ls), random.randint(1, 2))
        for label in label_obj_ls:
            pro_obj.pro_labels.add(label.id)
            pro_obj.save()
        return pro_obj

    def get_product(self, number=20, is_release=None):
        """
        获取产品
        :param number: 创建数量
        :param is_release: 是否发布
        """
        label_ls = self.get_labels(
            label_type=Labels.LABEL_TYPE_COMPONENT)
        # 创建上传包记录
        upload_history_ls = self.get_upload_package_history(
            number=number, is_many=False)
        for index in range(number):
            pro_package = upload_history_ls[index]
            index += 1
            self._create_product(
                index, is_release, label_ls,
                pro_package=pro_package, pro_version="1.0")
        # 随机模拟多个版本情况
        random_pro_ls = random.sample(
            list(range(number)),
            random.randint(0, number // 2 + 1))
        # 创建上传包记录
        upload_history_ls = self.get_upload_package_history(
            number=len(random_pro_ls), is_many=False)
        for index in random_pro_ls:
            pro_package = upload_history_ls[index]
            index += 1
            self._create_product(
                index, is_release, label_ls,
                pro_package=pro_package, pro_version="2.0")
        return ProductHub.objects.filter(
            pro_name__startswith=self.PRO_NAME_START)

    def destroy_product(self):
        """ 销毁应用 """
        ProductHub.objects.filter(
            pro_name__startswith=self.PRO_NAME_START).delete()
        self.destroy_labels()


class ClusterResourceMixin:
    """ 集群资源混入类 """
    NAME_START = "t_cluster"

    def get_cluster(self, number=5, service_name="test_service"):
        """
        获取集群
        :param number: 创建数量
        :param service_name: 集群所属服务
        """
        cluster_type_ls = ("单实例", "主从", "哨兵", "集群")
        cluster_ls = []
        for index in range(number):
            index += 1
            cluster_ls.append(ClusterInfo(
                cluster_service_name=service_name,
                cluster_name=f"{self.NAME_START}_{index}",
                cluster_type=random.choice(cluster_type_ls),
            ))
        ClusterInfo.objects.bulk_create(cluster_ls)
        return ClusterInfo.objects.filter(
            cluster_name__startswith=self.NAME_START)

    def destroy_cluster(self):
        """ 销毁集群 """
        ClusterInfo.objects.filter(
            cluster_name__startswith=self.NAME_START).delete()


class ServicesResourceMixin(HostsResourceMixin, ClusterResourceMixin,
                            ApplicationResourceMixin, ProductResourceMixin):
    """ 服务资源混入类 """

    INSTANCE_NAME_START = "t_service"

    def get_services(self, number=20, env_id=None):
        """
        获取服务
        :param number: 创建数量
        :param env_id: 环境实例
        """
        # 创建主机、应用、集群
        host_ls = self.get_hosts(env_id=env_id)
        app_ls = self.get_application(is_release=True)
        cluster_ls = self.get_cluster()
        # 获取环境信息
        env = None
        if env_id:
            env = Env.objects.filter(id=env_id).first()
        if not env:
            env = Env.objects.filter(id=1).first()
        # 创建服务
        service_ls = []
        for index in range(number):
            index += 1
            # 随机构造端口字段
            service_port_ls = [{
                "service_port": 18080
            }]
            for port_index in range(random.randint(0, 2)):
                service_port_ls.append({
                    "key": f"http_port_{port_index}",
                    "port": 18090 + port_index,
                })
            # 随机分配集群
            cluster = None
            if random.choice((True, False)):
                cluster = random.choice(cluster_ls)
            service_ls.append(Service(
                ip=random.choice(host_ls).ip,
                service_instance_name=f"{self.INSTANCE_NAME_START}_{index}",
                service_port=json.dumps(service_port_ls),
                service_status=random.choice(
                    Service.SERVICE_STATUS_CHOICES)[0],
                alert_count=random.randint(1, 100),
                self_healing_count=random.randint(1, 100),
                service=random.choice(app_ls),
                env=env,
                cluster=cluster,
                service_controllers={
                    "start": "start_path",
                    "stop": "stop_path",
                    "restart": "restart_path",
                    "init": "init_path",
                    "install": "install_path",
                },
            ))
        Service.objects.bulk_create(service_ls)

        service_queryset = Service.objects.filter(
            service_instance_name__startswith=self.INSTANCE_NAME_START)
        # 创建服务历史记录
        history_ls = []
        for obj in service_queryset:
            history_ls.append(ServiceHistory(
                username="admin",
                description="安装实例",
                result="success",
                service=obj,
            ))
        ServiceHistory.objects.bulk_create(history_ls)
        return service_queryset

    def destroy_services(self):
        """ 销毁服务 """
        Service.objects.filter(
            service_instance_name__startswith=self.INSTANCE_NAME_START).delete()
        self.destroy_application()
        self.destroy_hosts()
        self.destroy_cluster()


class InstallHistoryResourceMixin(ServicesResourceMixin):
    """ 安装历史记录资源混入类 """
    UUID_START = "t_main"

    def get_install_history(self, number=5):
        """ 获取安装历史记录 """
        main_obj = MainInstallHistory.objects.create(
            operation_uuid=f"{self.UUID_START}_"
                           f"{int(round(time.time() * 1000))}")
        service_ls = self.get_services(number=number)
        detail_ls = []
        for index in range(number):
            service = service_ls[index]
            index += 1
            detail_ls.append(DetailInstallHistory(
                service=service,
                main_install_history=main_obj,
                install_detail_args={
                    "name": "t_name",
                    "app_install_args": [
                        {
                            "key": "base_dir",
                            "name": "安装目录",
                            "default": "/data/t_name",
                            "dir_key": "{data_path}",
                            "check_msg": "success",
                            "check_flag": True
                        }
                    ]
                }

            ))
        DetailInstallHistory.objects.bulk_create(detail_ls)
        detail_obj_ls = DetailInstallHistory.objects.filter(
            main_install_history=main_obj)
        return main_obj, detail_obj_ls

    def destroy_install_history(self):
        """ 销毁安装历史记录 """
        DetailInstallHistory.objects.filter(
            main_install_history__operation_uuid__startswith=self.UUID_START).delete()
        MainInstallHistory.objects.filter(
            operation_uuid__startswith=self.UUID_START).delete()
        self.destroy_services()
