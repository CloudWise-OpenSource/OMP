import random
from unittest import mock

from rest_framework.reverse import reverse

from tests.base import AutoLoginTest
from hosts.tasks import deploy_agent
from hosts.tasks import host_agent_restart
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
            "ip": "127.0.0.10",
            "port": 36000,
            "username": "root",
            "password": "root_password",
            "data_folder": "/data",
            "operate_system": "centos",
        }

    def create_host(self):
        """ 创建主机，返回主机对象 """
        return Host.objects.create(
            instance_name="default_name",
            ip="127.0.0.20",
            port=36000,
            username="root",
            password="root_password",
            data_folder="/data",
            operate_system="centos",
            env=self.default_env,
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
        data.update(
            {"instance_name": "north_host_instance_name_mysql_node_one"})
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

        # 正确字段 -> 创建成功
        resp = self.post(self.create_host_url, self.correct_host_data).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        host_info = resp.get("data")
        self.assertTrue(host_info is not None)
        for k, v in self.correct_host_data.items():
            # 密码字段不展示
            if k == "password":
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
    """ 主机列表测试类 """

    def setUp(self):
        super(ListHostTest, self).setUp()
        self.create_host_url = reverse("hosts-list")
        self.list_host_url = reverse("hosts-list")

    def create_hosts(self):
        """ 创建测试主机 """
        aes_crypto = AESCryptor()
        host_obj_ls = []
        for i in range(50):
            host_obj = Host.objects.create(
                instance_name=f"test_create_{i + 1}",
                ip=f"130.110.90.{i + 1}",
                port=36000,
                username="root",
                password=aes_crypto.encode("root_password"),
                data_folder="/data",
                operate_system="centos",
                env=self.default_env,
            )
            host_obj_ls.append(host_obj)
        return host_obj_ls

    @staticmethod
    def delete_hosts():
        """ 创建测试主机 """
        Host.objects.filter(instance_name__contains="test_create_").delete()

    def test_hosts_list(self):
        """ 测试主机列表 """
        host_obj_ls = self.create_hosts()

        # 查询主机列表 -> 展示所有主机
        resp = self.get(self.list_host_url).json()
        print(resp)
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

        # 删除主机
        self.delete_hosts()


class UpdateHostTest(AutoLoginTest):
    """ 更新主机测试类 """

    def create_hosts(self):
        """ 创建多台主机 """
        host_obj_ls = []
        for i in range(10):
            host_obj = Host.objects.create(
                instance_name=f"update_host_{i + 1}",
                ip=f"130.110.90.{i + 1}",
                port=36000,
                username="root",
                password="root_password",
                data_folder="/data",
                operate_system="centos",
                env=self.default_env,
            )
            host_obj_ls.append(host_obj)
        return host_obj_ls

    @staticmethod
    def delete_hosts():
        Host.objects.filter(instance_name__contains="update_host_").delete()

    @mock.patch.object(SSH, "check", return_value=(True, ""))
    def test_update_host(self, ssh_mock):
        """ 测试更新一个主机 """

        # 更新不存在主机 -> 更新失败
        resp = self.put(reverse("hosts-detail", [99]), {
            "instance_name": "mysql_instance_1",
            "ip": "120.100.80.60",
            "port": 36000,
            "username": "root",
            "password": "root_password",
            "data_folder": "/data",
            "operate_system": "centos",
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "Not found.",
            "data": None
        })

        host_obj_ls = self.create_hosts()
        # 更新已存在主机，修改主机 IP -> 更新失败
        host_obj = host_obj_ls[0]
        resp = self.put(reverse("hosts-detail", [host_obj.id]), {
            "instance_name": host_obj.instance_name,
            "ip": "120.100.80.60",
            "port": host_obj.port,
            "username": host_obj.username,
            "password": host_obj.password,
            "data_folder": host_obj.data_folder,
            "operate_system": host_obj.operate_system,
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "ip: 该字段不可修改;",
            "data": None
        })

        # 更新已存在主机，修改实例名为已存在 -> 更新失败
        resp = self.put(reverse("hosts-detail", [host_obj.id]), {
            "instance_name": host_obj_ls[1].instance_name,
            "ip": host_obj.ip,
            "port": host_obj.port,
            "username": host_obj.username,
            "password": host_obj.password,
            "data_folder": host_obj.data_folder,
            "operate_system": host_obj.operate_system,
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "instance_name: 实例名已经存在;",
            "data": None
        })

        # 正确修改数据 -> 修改成功
        resp = self.put(reverse("hosts-detail", [host_obj.id]), {
            "instance_name": "new_host_name",
            "ip": host_obj.ip,
            "port": host_obj.port,
            "username": "new_username",
            "password": "new_password",
            "data_folder": host_obj.data_folder,
            "operate_system": host_obj.operate_system,
        }).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        new_host_info = resp.get("data")
        # 数据已更新
        self.assertEqual(new_host_info.get("instance_name"), "new_host_name")
        # 更新时间变化
        self.assertNotEqual(
            host_obj.modified,
            Host.objects.filter(id=host_obj.id).first().modified)
        self.delete_hosts()

    @mock.patch.object(SSH, "check", return_value=(True, ""))
    def test_partial_update_host(self, ssh_mock):
        """ 更新一个现有主机的一个或多个字段 """

        # 更新不存在主机 -> 更新失败
        resp = self.patch(reverse("hosts-detail", [99]), {
            "instance_name": "new_host_name",
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "Not found.",
            "data": None
        })

        host_obj_ls = self.create_hosts()
        # 更新已存在主机，修改主机 IP -> 更新失败
        host_obj = host_obj_ls[0]
        resp = self.patch(reverse("hosts-detail", [host_obj.id]), {
            "ip": "120.100.80.60",
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "ip: 该字段不可修改;",
            "data": None
        })

        # 更新已存在主机，修改实例名为已存在 -> 更新失败
        resp = self.patch(reverse("hosts-detail", [host_obj.id]), {
            "instance_name": host_obj_ls[1].instance_name,
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "instance_name: 实例名已经存在;",
            "data": None
        })

        # 正确修改数据 -> 修改成功
        resp = self.patch(reverse("hosts-detail", [host_obj.id]), {
            "instance_name": "new_host_name",
            "username": "new_username",
            "password": "new_password",
        }).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        new_host_obj = resp.get("data")
        self.assertTrue(new_host_obj is not None)
        # 数据已更新
        self.assertEqual(new_host_obj.get("instance_name"), "new_host_name")
        # 更新时间变化
        self.assertNotEqual(
            host_obj.modified,
            Host.objects.filter(id=host_obj.id).first().modified)
        self.delete_hosts()


class HostFieldCheckTest(AutoLoginTest):
    """ 主机字段校验测试类 """

    def setUp(self):
        super(HostFieldCheckTest, self).setUp()
        self.field_check_url = reverse("fields-list")

    def create_hosts(self):
        """ 创建多台主机 """
        host_obj_ls = []
        for i in range(2):
            host_obj = Host.objects.create(
                instance_name=f"check_field_{i + 1}",
                ip=f"130.110.90.{i + 1}",
                port=36000,
                username="root",
                password="root_password",
                data_folder="/data",
                operate_system="centos",
                env=self.default_env,
            )
            host_obj_ls.append(host_obj)
        return host_obj_ls

    @staticmethod
    def delete_hosts():
        Host.objects.filter(instance_name__contains="check_field_").delete()

    def test_create_host_check(self):
        """ 测试创建主机场景 """
        host_obj_ls = self.create_hosts()
        host_obj = host_obj_ls[0]

        # instance_name 重复 -> 验证结果 False
        resp = self.post(self.field_check_url, {
            "instance_name": host_obj.instance_name
        }).json()
        self.assertDictEqual(resp, {
            "code": 0,
            "message": "success",
            "data": False
        })

        # instance_name 不重复 -> 验证结果 True
        resp = self.post(self.field_check_url, {
            "instance_name": "my_host_name"
        }).json()
        self.assertDictEqual(resp, {
            "code": 0,
            "message": "success",
            "data": True
        })

        # ip 重复 -> 验证结果 False
        resp = self.post(self.field_check_url, {
            "ip": host_obj.ip
        }).json()
        self.assertDictEqual(resp, {
            "code": 0,
            "message": "success",
            "data": False
        })

        # ip 不重复 -> 验证结果 True
        resp = self.post(self.field_check_url, {
            "ip": "127.0.0.20"
        }).json()
        self.assertDictEqual(resp, {
            "code": 0,
            "message": "success",
            "data": True
        })
        self.delete_hosts()

    def test_error_host_check(self):
        """ 测试更新主机场景 """
        host_obj_ls = self.create_hosts()
        host_obj_one = host_obj_ls[0]
        host_obj_two = host_obj_ls[1]

        # instance_name 重复 (为主机自身 instance_name) -> 验证结果 True
        resp = self.post(self.field_check_url, {
            "id": host_obj_one.id,
            "instance_name": host_obj_one.instance_name
        }).json()
        self.assertDictEqual(resp, {
            "code": 0,
            "message": "success",
            "data": True
        })

        # instance_name 重复 (为其他主机 instance_name) -> 验证结果 False
        resp = self.post(self.field_check_url, {
            "id": host_obj_one.id,
            "instance_name": host_obj_two.instance_name
        }).json()
        self.assertDictEqual(resp, {
            "code": 0,
            "message": "success",
            "data": False
        })

        # ip 重复 (为主机自身 ip) -> 验证结果 True
        resp = self.post(self.field_check_url, {
            "id": host_obj_one.id,
            "ip": host_obj_one.ip
        }).json()
        self.assertDictEqual(resp, {
            "code": 0,
            "message": "success",
            "data": True
        })

        # ip 重复 (为其他主机 ip) -> 验证结果 False
        resp = self.post(self.field_check_url, {
            "id": host_obj_one.id,
            "ip": host_obj_two.ip
        }).json()
        self.assertDictEqual(resp, {
            "code": 0,
            "message": "success",
            "data": False
        })
        self.delete_hosts()


class ListIPTest(AutoLoginTest):
    """ IP 列表测试类 """

    def setUp(self):
        super(ListIPTest, self).setUp()
        self.ip_list_url = reverse("ips-list")

    def create_hosts(self):
        """ 创建测试主机 """
        host_obj_ls = []
        for i in range(100):
            host_obj = Host.objects.create(
                instance_name=f"test_ip_ls_{i + 1}",
                ip=f"130.110.90.{i + 1}",
                port=36000,
                username="root",
                password="root_password",
                data_folder="/data",
                operate_system="centos",
                env=self.default_env,
            )
            host_obj_ls.append(host_obj)
        return host_obj_ls

    @staticmethod
    def delete_hosts():
        """ 创建测试主机 """
        Host.objects.filter(
            instance_name__contains="test_ip_ls_").delete()

    def test_ip_list(self):
        """ 测试 IP 列表 """

        self.create_hosts()
        # 查询主机列表 -> 返回所有主机列表数据
        resp = self.get(self.ip_list_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertEqual(
            set(resp.get("data")),
            set(Host.objects.all().values_list("ip", flat=True)))
        self.delete_hosts()


class HostMaintainTest(AutoLoginTest):
    """ 主机维护模式测试类 """

    def setUp(self):
        super(HostMaintainTest, self).setUp()
        self.host_maintain_url = reverse("maintain-list")

    def create_hosts(self):
        """ 创建测试主机 """
        host_obj_ls = []
        for i in range(20):
            host_obj = Host.objects.create(
                instance_name=f"maintain_{i + 1}",
                ip=f"10.20.30.{i + 1}",
                port=36000,
                username="root",
                password="root_password",
                data_folder="/data",
                operate_system="centos",
                env=self.default_env,
            )
            host_obj_ls.append(host_obj)
        return host_obj_ls

    @staticmethod
    def delete_hosts():
        """ 创建测试主机 """
        Host.objects.filter(
            instance_name__contains="maintain_").delete()

    def test_error_field(self):
        """ 测试错误字段校验 """

        host_obj_ls = self.create_hosts()
        host_obj_id_ls = list(map(lambda x: x.id, host_obj_ls))
        # host_ids 中含不存在的 ID -> 修改失败
        not_exists_id = 666
        random_host_ls = random.sample(host_obj_id_ls, 5)
        random_host_ls.append(not_exists_id)
        resp = self.post(self.host_maintain_url, {
            "is_maintenance": True,
            "host_ids": random_host_ls
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": f"host_ids: 有不存在的ID [{not_exists_id}];",
            "data": None
        })

        # host_ids 中存在已经处于 type 类型的主机 -> 创建失败
        random_host_ls = random.sample(host_obj_id_ls, 5)
        resp = self.post(self.host_maintain_url, {
            "is_maintenance": False,
            "host_ids": random_host_ls
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "host_ids: 存在已 '关闭' 维护模式的主机;",
            "data": None
        })
        self.delete_hosts()

    def test_correct_field(self):
        """ 正确字段校验 """
        # TODO 模拟调用进入维护模式函数
        host_obj_ls = self.create_hosts()
        host_obj_id_ls = list(map(lambda x: x.id, host_obj_ls))

        # 正确字段，开启维护模式 -> 操作成功
        random_host_ls = random.sample(host_obj_id_ls, 5)
        data = {
            "is_maintenance": True,
            "host_ids": random_host_ls
        }
        resp = self.post(self.host_maintain_url, data).json()
        self.assertDictEqual(resp, {
            "code": 0,
            "message": "success",
            "data": data
        })
        # host_ids中主机，is_maintenance 状态均为 True
        is_maintenance_ls = Host.objects.filter(
            id__in=random_host_ls
        ).values_list("is_maintenance", flat=True)
        self.assertTrue(all(is_maintenance_ls))

        # 关闭维护模式
        data = {
            "is_maintenance": False,
            "host_ids": random_host_ls
        }
        resp = self.post(self.host_maintain_url, data).json()
        self.assertDictEqual(resp, {
            "code": 0,
            "message": "success",
            "data": data
        })
        # host_ids中主机，is_maintenance 状态均为 False
        is_maintenance_ls = Host.objects.filter(
            id__in=random_host_ls
        ).values_list("is_maintenance", flat=True)
        self.assertTrue(not any(is_maintenance_ls))
        self.delete_hosts()


class HostAgentRestartTest(AutoLoginTest):
    """ 主机维护模式测试类 """

    def setUp(self):
        super(HostAgentRestartTest, self).setUp()
        self.host_restartHostAgent_url = reverse("restartHostAgent-list")

    def create_hosts(self):
        """ 创建测试主机 """
        host_obj_ls = []
        for i in range(2):
            host_obj = Host.objects.create(
                instance_name=f"restart_{i + 1}",
                ip=f"127.0.0.{i + 1}",
                port=36000,
                username="root",
                password="root_password",
                data_folder="/data",
                operate_system="centos",
                env=self.default_env,
            )
            host_obj_ls.append(host_obj)
        return host_obj_ls

    @mock.patch.object(host_agent_restart, "delay", return_value=None)
    def test_success(self, host_agent_restart_mock):
        """ 请求成功测试 """
        host_obj_ls = self.create_hosts()
        host_obj_id_ls = list(map(lambda x: x.id, host_obj_ls))
        resp = self.post(
            self.host_restartHostAgent_url,
            data={"host_ids": host_obj_id_ls}
        ).json()
        self.assertDictEqual(resp, {
            "code": 0,
            "message": "success",
            "data": {
                "host_ids": host_obj_id_ls
            }
        })

    @mock.patch.object(host_agent_restart, "delay", return_value=None)
    def test_failed(self, host_agent_restart_mock):
        """ 请求成功测试 """
        self.create_hosts()
        resp = self.post(
            self.host_restartHostAgent_url,
            data={"host_ids": [random.randint(10000, 20000)]}
        ).json()
        self.assertEqual(resp.get("code"), 1)
