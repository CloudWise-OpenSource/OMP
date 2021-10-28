import json

from rest_framework.reverse import reverse

from db_models.models import (
    ApplicationHub, ProductHub,
    UploadPackageHistory, Labels
)
from tests.base import AutoLoginTest
from unittest import mock
from app_store.tasks import front_end_verified
from utils.plugin import public_utils
from app_store.tasks import (
    ExplainYml, PublicAction,
    publish_bak_end, publish_entry,
    exec_clear
)
from unittest.mock import patch, mock_open
from app_store.tmp_exec_back_task import back_end_verified_init

test_product = {
    "kind": "product",
    "name": "jenkins",
    "version": "5.2.0",
    "description": "这是jenkins",
    "labels": ["CI&CD"],
    "dependencies": None,
    "service": [{"name": "jenkins", "version": "2.303.2"}],
    "extend_fields": {}
}

test_service = {
    "kind": "service",
    "name": "jenkins",
    "version": "2.303.2",
    "description": "这是jenkins服务",
    "ports": [{"name": "服务端口", "protocol": "TCP", "key": "service_port", "default": 8080}],
    "dependencies": [{"name": "jdk", "version": "1.8.0"}],
    "install": [{"name": "安装目录", "key": "base_dir", "default": "path/jenkins"}],
    "control": [
        {
            "start": "./bin/start.sh",
            "stop": "./bin/stop.sh",
            "restart": "./bin/restart.sh",
            "reload": "./bin/reload.sh",
            "install": "./scripts/install.sh",
            "init": "./scripts/init.sh"
        }
    ],
    "extend_fields": {
        "auto_launch": True,
        "base_env": False,
        "monitor": {
            "process_name": "jenkins",
            "metrics_port": "service_port"
        },
        "deploy": None,
        "resources": {"cpu": "2c", "memory": "2g"}
    }
}

service_yml = """
kind: service
name: jenkins
version: 2.303.2
description: "jenkins服务"
auto_launch: true
base_env: false
monitor:
  process_name: "jenkins"
  metrics_port: {service_port}
deploy:
ports:
  - name: 服务端
    protocol: TCP
    default: 8080
    key: service_port
dependencies:
  - name: jdk
    version: 1.8
resources:
  cpu: 1000m
  memory: 2000m
install:
  - name: "安装目录"
    key: base_dir
    default: "{data_path}/jeknins"
control:
  start: "./bin/start.sh"
  stop: "./bin/stop.sh"
  restart: "./bin/restart.sh"
  reload: "./bin/reload.sh"
  install: "./scripts/install.sh"
  init: "./scripts/init.sh"
"""

component_yml = """
kind: component
name: tengine  
version: 2.3.3
description: "服务tengine" 
labels:          
  - WEB服务
auto_launch: true 
base_env: false
monitor:
  process_name: "nginx"  
  metrics_port: {service_port}
ports:
  - name: 服务端口      
    protocol: TCP     
    key: service_port 
    default: 80 
deploy:    
dependencies:
resources:
  cpu: 1000m
  memory: 500m      
install:        
  - name: "安装目录"
    key: base_dir
    default: "{data_path}/tengine"
  - name: "日志目录"
    key: log_dir
    default: "{data_path}/tengine/logs"
  - name: "vhosts"
    key: vhosts_dir
    default: "{data_path}/tengine/vhosts"
control: 
  start: "./bin/start.sh"
  stop: "./bin/stop.sh"
  restart: "./bin/restart.sh"
  reload: "./bin/reload.sh"
  install: "./scripts/install.sh"
  init:  "./scripts/init.sh"
"""

product_yml = """
kind: product
name: jenkins
version: 5.2.0
description: "Jenkins开源"
labels:
  - CI&CD
dependencies:
service:
  - name: jenkins
    version: 2.303.2
"""


class PackageUploadTest(AutoLoginTest):
    # 上传逻辑
    def setUp(self):
        super(PackageUploadTest, self).setUp()
        self.upload_url = reverse(
            "upload-list")
        UploadPackageHistory(
            operation_uuid='test-uuid',
            operation_user='admin',
            package_name='jenkins-1.0.0-test-md5.tar.gz',
            package_md5='test-md5',
            package_path="verified"
        ).save()

    @mock.patch.object(public_utils, "local_cmd", return_value="")
    @mock.patch(
        "os.mkdir",
        return_value=None)
    @mock.patch(
        "os.path.exists",
        return_value="")
    @mock.patch(
        "app_store.tasks.ExplainYml.explain_yml",
        return_value=""
    )
    @mock.patch(
        "os.listdir",
        return_value=["jenkins-2.303.2.tar.gz"]
    )
    @mock.patch(
        "os.path.isfile",
        return_value=True
    )
    def test_app_store_upload(self, isfile, listdir, explain, exists, mkdir, local_cmd):
        # 正向前端发布
        upload_obj = UploadPackageHistory.objects.get(operation_uuid='test-uuid')
        local_cmd.side_effect = [
            ("test-md5 jenkins-1.0.0-test-md5.tar.gz", "", 0),
            ("success", "", 0),
            ("test-md6 jenkins01-1.0.0.tar.gz", "", 0)
        ]
        exists.side_effect = [
            True, False, True
        ]
        explain.side_effect = [(True, test_product), (True, test_service)]
        front_end_verified(upload_obj.operation_uuid,
                           upload_obj.operation_user,
                           upload_obj.package_name,
                           upload_obj.package_md5,
                           "RandomStr",
                           "front_end_verified",
                           upload_obj.id)
        upload_obj.refresh_from_db()
        res = upload_obj.package_status
        self.assertEqual(res, 0)

    @patch("builtins.open", new_callable=mock_open, read_data=service_yml)
    def test_app_store_explain_service(self, with_open):
        # 正向解析服务
        upload_obj = UploadPackageHistory.objects.get(operation_uuid='test-uuid')
        public_action = PublicAction(upload_obj.package_md5)
        explain = ExplainYml(public_action, '/data/test').explain_yml()
        upload_obj.refresh_from_db()
        self.assertEqual(explain[0], True)
        self.assertEqual(explain[1].get('version'), "2.303.2")

    @patch("builtins.open", new_callable=mock_open, read_data=component_yml)
    def test_app_store_explain_component(self, with_open):
        # 正向解析组件
        upload_obj = UploadPackageHistory.objects.get(operation_uuid='test-uuid')
        public_action = PublicAction(upload_obj.package_md5)
        explain = ExplainYml(public_action, '/data/test').explain_yml()
        upload_obj.refresh_from_db()
        self.assertEqual(explain[0], True)
        self.assertEqual(explain[1].get('version'), "2.3.3")

    @patch("builtins.open", new_callable=mock_open, read_data=product_yml)
    def test_app_store_explain_product(self, with_open):
        # 正向解析产品
        upload_obj = UploadPackageHistory.objects.get(operation_uuid='test-uuid')
        public_action = PublicAction(upload_obj.package_md5)
        explain = ExplainYml(public_action, '/data/test').explain_yml()
        upload_obj.refresh_from_db()
        self.assertEqual(explain[0], True)
        self.assertEqual(explain[1].get('version'), "5.2.0")


class SimulationRedis(object):
    def exists(self, key):
        return 0

    def lpush(self, key, *args):
        return True

    def expire(self, key, expire):
        return True

    def lindex(self, key, index):
        return 'test_redis'


publish_info = """\
{"kind": "product", "name": "jenkins", "version": "1.0.0", "description": "描述",\
"dependencies": [{"name": "jdk1.88", "version": "1.88"},\
{"name": "tomcat1.88", "version": "1.88"},\
{"name": "home1.99", "version": "1.99"}],\
"extend_fields": {},\
"service": [{"name": "jenkinss01", "version": "010101"},\
{"name": "jenkinsss01", "version": "010101-01.01"},\
{"name": "jenkinssss01", "version": "01010101"},\
{"name": "qqqqqqqqqq01", "version": "11011"},\
{"name": "jenkins", "version": "111111111"}],\
"labels": ["mysql_db"],\
"product_service":\
[{"kind": "service", "name": "jenkins", "version": "123", "description": "jenkins服务",\
"dependencies": [{"name": "jdk", "version": "8u211"}],\
"extend_fields": {"auto_launch": "true", "base_env": "false",\
"monitor": {"process_name": "jenkins"},\
"resources": {"cpu": "1000m", "memory": "2000m"}},\
"ports": [{"name": "服务端口", "protocol": "TCP", "key": "service_port", "port": "8080"}],\
"control": {"start": "./bin/start.sh", "stop": "./bin/stop.sh",\
"restart": "./bin/restart.sh", "reload": "./bin/reload.sh", "install": "./scripts/install.sh",\
"init": "./scripts/init.sh"},\
"install": [{"name": "安装目录", "key": "base_dir", "default": "{data_path}/jeknins"}],\
"package_name": "jenkins-1.0.0-service.tar.gz"}],\
"image": null, "package_name": "jenkins-1.0.0-test-md5.tar.gz",\
"tmp_dir": ["/data/omp/package_hub/front_end_verified/jenkins-test40yp18cfwbz/jenkins", "00011123"]}\
"""


class PackagePublishTest(AutoLoginTest):
    # 发布逻辑
    def setUp(self):
        super(PackagePublishTest, self).setUp()
        self.publish_url = reverse(
            "publish-list")
        upload_obj = UploadPackageHistory(
            operation_uuid='test-uuid',
            operation_user='admin',
            package_name='jenkins-1.0.0-test-md5.tar.gz',
            package_md5='test-md5',
            package_path="verified",
            package_status=0
        )
        upload_obj.save()
        UploadPackageHistory.objects.create(
            operation_uuid='test-uuid',
            operation_user='admin',
            package_name='jenkins-1.0.0-service.tar.gz',
            package_md5='test-md5-service',
            package_path="verified/jenkins-1.0.0",
            package_status=0,
            package_parent=upload_obj
        )

    @patch("builtins.open", new_callable=mock_open, read_data=publish_info)
    @mock.patch(
        "app_store.tasks.exec_clear",
        return_value=""
    )
    @mock.patch.object(
        public_utils,
        "local_cmd",
        return_value=("", "", 0)
    )
    @mock.patch(
        "os.path.isfile",
        return_value=False
    )
    def test_app_store_publish(self, isfile, local_cmd, exe_clear, with_open):
        # 正向发布产品，包含服务，前端
        upload_obj = UploadPackageHistory.objects.get(operation_uuid='test-uuid',
                                                      package_parent__isnull=True
                                                      )
        publish_entry(upload_obj.operation_uuid)
        upload_obj.refresh_from_db()
        app_count = ApplicationHub.objects.filter(
            app_name="jenkins",
            app_version="123"
        ).count()
        pro_count = ProductHub.objects.filter(
            pro_name="jenkins",
            pro_version="1.0.0"
        ).count()
        label_count = Labels.objects.filter(
            label_name="mysql_db"
        ).count()
        self.assertEqual(app_count, 1)
        self.assertEqual(pro_count, 1)
        self.assertEqual(label_count, 1)

    @mock.patch(
        "redis.Redis.delete",
        return_value=""
    )
    @mock.patch(
        "app_store.tasks.publish_entry",
        return_value=""
    )
    def test_app_store_publish_back_true(self, publish, redis):
        # 正向后端发布等待

        res = publish_bak_end('test-uuid', 1)
        self.assertEqual(res, None)

    @mock.patch(
        "app_store.tasks.exec_clear",
        return_value=""
    )
    @mock.patch(
        "redis.Redis.delete",
        return_value=""
    )
    def test_app_store_publish_back(self, redis, exe_clear):
        # 反向后端发布等待
        upload_obj = UploadPackageHistory.objects.get(operation_uuid='test-uuid',
                                                      package_parent__isnull=True
                                                      )
        upload_obj.package_status = 1
        upload_obj.save()
        res = publish_bak_end('test-uuid', 1)
        self.assertEqual(res, None)

    @mock.patch(
        "app_store.tasks.publish_entry.delay",
        return_value=""
    )
    def test_app_store_publish_api(self, delay):
        # 正向post发布接口
        resp = self.post(self.publish_url, {
            "uuid": 'test-uuid',
        }).json()
        self.assertDictEqual(resp.get('data'), {
            "status": "发布任务下发成功"
        })

        # 正向get请求,过滤状态3，4，5
        upload_obj1 = UploadPackageHistory.objects.get(operation_uuid='test-uuid',
                                                       package_parent__isnull=True
                                                       )
        upload_obj1.package_status = 0
        upload_obj1.save()
        resp = self.get(self.publish_url, data={
            "operation_uuid": 'test-uuid',
        }).json()
        self.assertDictEqual(
            resp, {
                'code': 0,
                'message': 'success',
                'data': []
            }
        )

    @mock.patch.object(
        public_utils,
        "local_cmd",
        return_value=("", "", 0)
    )
    def test_app_store_publish_clear(self, local_cmd):
        # 正向删除
        upload_obj1 = UploadPackageHistory.objects.get(operation_uuid='test-uuid',
                                                       package_parent__isnull=True
                                                       )
        upload_obj1.package_status = 3
        upload_obj1.save()
        resp = exec_clear('/data/omp/package_hub/front_end_verified')
        self.assertEqual(resp, None)

    @mock.patch(
        "redis.Redis",
        return_value=SimulationRedis())
    @mock.patch(
        "os.listdir",
        return_value=["jdk-1.8.1.tar.gz"])
    @mock.patch(
        "os.path.isfile",
        return_value=True)
    @mock.patch(
        "app_store.tasks.front_end_verified.delay",
        return_value="")
    @mock.patch(
        "app_store.tasks.publish_bak_end.delay",
        return_value="")
    def test_app_store_scan(self, bak, front, isfile, listdir, redis):
        uuid, exec_name = back_end_verified_init('admin')
        count = UploadPackageHistory.objects.filter(operation_uuid=uuid).count()
        self.assertEqual(count, 1)
        self.assertEqual(exec_name[0], "jdk-1.8.1.tar.gz")
