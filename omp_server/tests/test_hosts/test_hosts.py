from unittest import mock

from rest_framework.reverse import reverse

from tests.base import AutoLoginTest
from hosts.tasks import deploy_agent
from db_models.models import Host
from utils.plugin.ssh import SSH
from utils.plugin.crypto import AESCryptor


class CreateHostTest(AutoLoginTest):
    """ 创建主机测试类 """

    def setUp(self):
        super(CreateHostTest, self).setUp()
        self.create_host_url = reverse("hosts-list")
        # 正确主机数据
        self.correct_host_data = {
            "instance_name": "mysql_instance_1",
            "ip": "120.100.80.60",
            "port": 36000,
            "username": "root",
            "password": "root_password",
            "data_folder": "/data",
            "operate_system": "centos",
        }

    @staticmethod
    def create_host():
        """ 创建主机，返回主机对象 """
        return Host.objects.create(
            instance_name="default_name",
            ip="130.110.90.70",
            port=36000,
            username="root",
            password="root_password",
            data_folder="/data",
            operate_system="centos",
        )

    def test_error_field_instance_name(self):
        """ 测试错误字段校验，instance_name """

        # 不提供 instance_name -> 创建失败
        data = self.correct_host_data.copy()
        data.pop("instance_name")
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "instance_name: 必须包含[instance_name]字段;",
            "data": None
        })

        # instance_name 超过长度 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"instance_name": "north_host_instance_name_mysql_node_one"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "instance_name: Ensure this field has no more than 16 characters.;",
            "data": None
        })

        # instance_name 含中文 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"instance_name": "mysql实例节点1"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "instance_name: 字段不可含有中文;",
            "data": None
        })

        # instance_name 含有表情 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"instance_name": "mysql😃1"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "instance_name: 字段不可含有表情;",
            "data": None
        })

        # instance_name 不以字母、数字、- 开头 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"instance_name": "$mysql-01"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "instance_name: 字段格式不合法;",
            "data": None
        })

        # instance_name 已存在 -> 创建失败
        host_obj = self.create_host()
        data = self.correct_host_data.copy()
        data.update({"instance_name": host_obj.instance_name})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "instance_name: 实例名已经存在;",
            "data": None
        })
        host_obj.delete(soft=False)

    def test_error_field_ip(self):
        """ 测试错误字段校验，ip """

        # 不提供 ip -> 创建失败
        data = self.correct_host_data.copy()
        data.pop("ip")
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "ip: 必须包含[ip]字段;",
            "data": None
        })

        # ip 格式不规范 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"ip": "120.100.80"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "ip: Enter a valid IPv4 or IPv6 address.;",
            "data": None
        })

        # ip 已存在 -> 创建失败
        host_obj = self.create_host()
        data = self.correct_host_data.copy()
        data.update({"ip": host_obj.ip})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "ip: IP已经存在;",
            "data": None
        })
        host_obj.delete(soft=False)

    def test_error_field_port(self):
        """ 测试错误字段校验，port """

        # 不提供 port -> 创建失败
        data = self.correct_host_data.copy()
        data.pop("port")
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "port: 必须包含[port]字段;",
            "data": None
        })

        # port 超过范围 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"port": 66666})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "port: Ensure this value is less than or equal to 65535.;",
            "data": None
        })

    def test_error_field_username(self):
        """ 测试错误字段校验，username """

        # 不提供 username -> 创建失败
        data = self.correct_host_data.copy()
        data.pop("username")
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "username: 必须包含[username]字段;",
            "data": None
        })

        # username 超过指定长度 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"username": "this_is_a_too_lang_username"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "username: Ensure this field has no more than 16 characters.;",
            "data": None
        })

        # username 不以数字、字母、_ 开头 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"username": "$my_username"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "username: 字段格式不合法;",
            "data": None
        })

    def test_error_field_password(self):
        """ 测试错误字段校验，password """

        # 不提供 password -> 创建失败
        data = self.correct_host_data.copy()
        data.pop("password")
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "password: 必须包含[password]字段;",
            "data": None
        })

        # password 超过指定长度 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"password": "this_is_a_too_lang_password"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "password: Ensure this field has no more than 16 characters.;",
            "data": None
        })

        # password 含有中文 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"password": "mysql节点密码"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "password: 字段不可含有中文;",
            "data": None
        })

        # password 含有表情 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"password": "password😊mysql"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "password: 字段不可含有表情;",
            "data": None
        })

    def test_error_field_data_folder(self):
        """ 测试错误字段校验，data_folder """

        # 不提供 data_folder -> 创建失败
        data = self.correct_host_data.copy()
        data.pop("data_folder")
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "data_folder: 必须包含[data_folder]字段;",
            "data": None
        })

        # data_folder 不以 / 开头 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"data_folder": "data"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "data_folder: 字段格式不合法;",
            "data": None
        })

    def test_error_field_operate_system(self):
        """ 测试错误字段校验，operate_system """

        # 不提供 operate_system -> 创建失败
        data = self.correct_host_data.copy()
        data.pop("operate_system")
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "operate_system: 必须包含[operate_system]字段;",
            "data": None
        })

    @mock.patch.object(SSH, "check", return_value=(False, "error message"))
    def test_wrong_ssh(self, ssh_mock):
        """ 测试创建主机，SSH 校验未通过"""

        print(f"== run test_wrong_ssh method ==\n"
              f"we mock the SSH.check "
              f"return_value as {ssh_mock.return_value}")

        # 正确字段，ssh 校验未通过 -> 创建失败
        resp = self.post(self.create_host_url, self.correct_host_data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "ip: 主机SSH连通性校验失败;",
            "data": None
        })

    @mock.patch.object(SSH, "check", return_value=(True, ""))
    @mock.patch.object(deploy_agent, "delay", return_value=None)
    def test_correct_field(self, deploy_agent_mock, ssh_mock):
        """ 测试正确字段 """

        print(f"== run test_correct_field method ==\n"
              f"we mock the SSH.check "
              f"return_value as {ssh_mock.return_value}\n"
              f"we mock the deploy_agent.delay "
              f"return_value as {deploy_agent_mock.return_value}")

        # 正确字段 -> 创建成功
        resp = self.post(self.create_host_url, self.correct_host_data).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        host_info = resp.get("data")
        self.assertTrue(host_info is not None)
        for k, v in self.correct_host_data.items():
            # 密码字段不展示
            if k == "password":
                self.assertTrue(k not in host_info)
                continue
            # 各字段值相等
            self.assertEqual(host_info.get(k), v)
        # 服务数和告警为 0
        self.assertEqual(host_info.get("service_num"), 0)
        self.assertEqual(host_info.get("alert_num"), 0)
        # 主机 Agent 和监控 Agent 默认为部署中
        self.assertEqual(
            host_info.get("host_agent"),
            Host.AGENT_DEPLOY_ING)
        self.assertEqual(
            host_info.get("monitor_agent"),
            Host.AGENT_DEPLOY_ING)
        # 维护模式默认不开启
        self.assertEqual(host_info.get("is_maintenance"), False)

        # 数据库 -> 主机存在
        host_obj = Host.objects.filter(id=host_info.get("id")).first()
        self.assertTrue(host_obj is not None)

        # 密码字段 -> 加密处理
        self.assertNotEqual(
            host_obj.password,
            self.correct_host_data.get("password")
        )
        aes = AESCryptor()
        self.assertEqual(
            aes.decode(host_obj.password),
            self.correct_host_data.get("password")
        )

        # 软删除字段 -> False
        self.assertEqual(host_obj.is_deleted, False)

        # 删除主机
        host_obj.delete(soft=False)


class ListHostTest(AutoLoginTest):
    """ 创建主机测试类 """

    def setUp(self):
        super(ListHostTest, self).setUp()
        self.create_host_url = reverse("hosts-list")
        self.list_host_url = reverse("hosts-list")

    @staticmethod
    def create_hosts():
        """ 创建多台主机 """
        host_obj_ls = []
        for i in range(50):
            host_obj = Host.objects.create(
                instance_name=f"host_name_{i + 1}",
                ip=f"130.110.90.{i + 1}",
                port=36000,
                username="root",
                password="root_password",
                data_folder="/data",
                operate_system="centos",
            )
            host_obj_ls.append(host_obj)
        return host_obj_ls

    def test_hosts_list(self):
        """ 测试主机列表 """

        host_obj_ls = self.create_hosts()

        # 查询主机列表 -> 展示所有主机
        resp = self.get(self.list_host_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)
        # 数据总量为所有主机数
        self.assertEqual(resp.get("data").get("count"), len(host_obj_ls))
        # 默认按照创建时间排序，第一条记录应为最后一个添加的主机
        first_host = resp.get("data").get("results")[0]
        last_host = host_obj_ls[-1]
        self.assertEqual(first_host.get("ip"), last_host.ip)

        # IP 过滤主机 -> 模糊展示匹配项
        target_host_obj = host_obj_ls[5]
        resp = self.get(self.list_host_url, {
            "ip": target_host_obj.ip
        }).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)
        self.assertEqual(resp.get("data").get("count"), 1)

        # 指定字段排序 -> 返回排序后的列表
        resp = self.get(self.list_host_url, {
            "ordering": "ip"
        }).json()
        # 按照 IP 排序，第一条记录应为第一个添加的主机
        first_host = resp.get("data").get("results")[0]
        last_host = host_obj_ls[0]
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertEqual(first_host.get("ip"), last_host.ip)

        # TODO 监控动态字段排序


class UpdateHostTest(AutoLoginTest):
    """ 更新主机测试类 """


class ListIPTest(AutoLoginTest):
    """ IP 列表测试类 """
    pass
