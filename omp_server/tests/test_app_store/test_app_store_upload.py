import json

from rest_framework.reverse import reverse

from db_models.models import (
    ApplicationHub, ProductHub,
    UploadPackageHistory
)
from tests.base import AutoLoginTest
from unittest import mock
from app_store.tasks import front_end_verified
from utils.plugin import public_utils
from app_store.tasks import ExplainYml,PublicAction
from unittest.mock import patch, mock_open

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
"""
product_yml = {
    'kind': 'product', 'name': 'jenkins', 'version': '5.2.0',
    'description':
        'Jenkins是开源CI&CD软件领导者，提供超过1000个插件来支持构建、部署、自动化， 满足任何项目的需要。',
    'labels': ['CI&CD'],
    'dependencies': '', 'service': [{'name': 'jenkins', 'version': '2.303.2'}]}

service_yml = {'kind': 'service', 'name': 'jenkins', 'version': '2.303.2', 'description': 'jenkins服务',
               'auto_launch': 'true', 'base_env': 'false',
               'monitor': {'process_name': 'jenkins', 'metrics_port': {'service_port': ''}}, 'deploy': '',
               'ports': [{'name': '服务端', 'protocol': 'TCP', 'default': '8080', 'key': 'service_port'}],
               'dependencies': [{'name': 'jdk', 'version': '1.8'}], 'resources': {'cpu': '1000m', 'memory': '2000m'},
               'install': [{'name': '安装目录', 'key': 'base_dir', 'default': '{data_path}/jeknins'}],
               'control': {'start': './bin/start.sh', 'stop': './bin/stop.sh', 'restart': './bin/restart.sh',
                           'reload': './bin/reload.sh', 'install': './scripts/install.sh', 'init': './scripts/init.sh'}}
"""

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


class PackageUploadTest(AutoLoginTest):
    def setUp(self):
        super(PackageUploadTest, self).setUp()
        self.upload_url = reverse(
            "upload-list")
        self.upload_obj = UploadPackageHistory(
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
        # 正向校验
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
    def test_app_store_explain(self, with_open):
        # 正向解析
        upload_obj = UploadPackageHistory.objects.get(operation_uuid='test-uuid')
        public_action = PublicAction(upload_obj.package_md5)
        explain = ExplainYml(public_action, '/data/test').explain_yml()
        upload_obj.refresh_from_db()
        self.assertEqual(explain[0], True)
        self.assertEqual(explain[1].get('version'), "2.303.2")
