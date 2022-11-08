import random
import string
from datetime import datetime
from unittest import mock

from django.http.response import FileResponse
from rest_framework.reverse import reverse

from tests.base import AutoLoginTest
from tests.mixin import (
    HostsResourceMixin, HostBatchRequestMixin,
    GrafanaMainPageResourceMixin
)
from hosts.views import HostListView
from hosts.tasks import (
    host_agent_restart, insert_host_celery_task
)
from hosts.hosts_serializers import HostSerializer
from db_models.models import (
    Host, HostOperateLog
)
from utils.plugin.ssh import SSH
from utils.plugin.crypto import AESCryptor
from promemonitor.prometheus import Prometheus
from promemonitor.alertmanager import Alertmanager


class CreateHostTest(AutoLoginTest, HostsResourceMixin):
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
            "operate_system": "CentOS",
        }

    def test_error_field_instance_name(self):
        """ 测试错误字段校验，instance_name """

        # 不提供 instance_name -> 创建失败
        data = self.correct_host_data.copy()
        data.pop("instance_name")
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "必须包含[instance_name]字段",
            "data": None
        })

        # instance_name 超过长度 -> 创建失败
        data = self.correct_host_data.copy()
        data.update(
            {"instance_name": "north_host_instance_name_mysql_node_one"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "实例名长度需小于16",
            "data": None
        })

        # instance_name 含中文 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"instance_name": "mysql实例节点1"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "实例名不可含有中文",
            "data": None
        })

        # instance_name 含有表情 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"instance_name": "mysql😃1"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "实例名不可含有表情",
            "data": None
        })

        # instance_name 不以字母、数字、- 开头 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"instance_name": "$mysql-01"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "实例名格式不合法",
            "data": None
        })

        # instance_name 已存在 -> 创建失败
        host_obj = self.get_hosts(1)[0]
        data = self.correct_host_data.copy()
        data.update({"instance_name": host_obj.instance_name})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "实例名已经存在",
            "data": None
        })
        self.destroy_hosts()

    def test_error_field_ip(self):
        """ 测试错误字段校验，ip """

        # 不提供 ip -> 创建失败
        data = self.correct_host_data.copy()
        data.pop("ip")
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "必须包含[ip]字段",
            "data": None
        })

        # ip 格式不规范 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"ip": "120.100.80"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "IP格式不合法",
            "data": None
        })

        # ip 已存在 -> 创建失败
        host_obj = self.get_hosts(1)[0]
        data = self.correct_host_data.copy()
        data.update({"ip": host_obj.ip})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "IP已经存在",
            "data": None
        })
        self.destroy_hosts()

    def test_error_field_port(self):
        """ 测试错误字段校验，port """

        # 不提供 port -> 创建失败
        data = self.correct_host_data.copy()
        data.pop("port")
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "必须包含[port]字段",
            "data": None
        })

        # port 超过范围 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"port": 66666})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "端口超出指定范围",
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
            "message": "必须包含[username]字段",
            "data": None
        })

        # username 超过指定长度 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"username": "this_is_a_too_lang_username"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "用户名长度需小于16",
            "data": None
        })

        # username 不以数字、字母、_ 开头 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"username": "$my_username"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "用户名格式不合法",
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
            "message": "必须包含[password]字段",
            "data": None
        })

        # password 小于指定长度 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"password": "pass11"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "密码长度需大于8",
            "data": None
        })

        # password 超过指定长度 -> 创建失败
        data = self.correct_host_data.copy()
        to_long_password = ''.join(random.choice(
            string.ascii_letters) for _ in range(70))
        data.update({"password": to_long_password})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "密码长度需小于64",
            "data": None
        })

        # password 含有中文 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"password": "mysql节点密码"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "密码不可含有中文",
            "data": None
        })

        # password 含有表情 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"password": "password😊mysql"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "密码不可含有表情",
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
            "message": "必须包含[data_folder]字段",
            "data": None
        })

        # data_folder 不以 '/' 开头 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"data_folder": "data"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "数据分区格式不合法",
            "data": None
        })

        # data_folder 目录以 '-' 开头 -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"data_folder": "/data/-myDir"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "数据分区目录不能以'-'开头",
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
            "message": "必须包含[operate_system]字段",
            "data": None
        })

        # 不支持的 operate_system -> 创建失败
        data = self.correct_host_data.copy()
        data.update({"operate_system": "SUSE"})
        resp = self.post(self.create_host_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "操作系统支持CentOS/RedHat",
            "data": None
        })

    @mock.patch.object(SSH, "check", return_value=(False, "error message"))
    def test_wrong_ssh(self, ssh_mock):
        """ 测试创建主机，SSH 校验未通过"""

        # 正确字段，ssh 校验未通过 -> 创建失败
        resp = self.post(self.create_host_url, self.correct_host_data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "SSH登录失败",
            "data": None
        })

    # @mock.patch.object(SSH, "check", return_value=(True, ""))
    # @mock.patch.object(SSH, "is_sudo", return_value=(False, "is sudo"))
    # def test_wrong_username(self, si_sudo, ssh_mock):
    #     """ 测试创建主机，SSH 用户 sudo 权限未通过 """
    #
    #     # 正确字段，ssh 校验未通过 -> 创建失败
    #     resp = self.post(self.create_host_url, self.correct_host_data).json()
    #     self.assertDictEqual(resp, {
    #         "code": 1,
    #         "message": "用户权限错误，请使用root或具备sudo免密用户",
    #         "data": None
    #     })

    @mock.patch.object(SSH, "check", return_value=(True, ""))
    @mock.patch.object(SSH, "is_sudo", return_value=(True, "is sudo"))
    @mock.patch.object(SSH, "cmd", return_value=(True, ""))
    @mock.patch.object(insert_host_celery_task, "delay", return_value=None)
    def test_correct_field(self, celery_task_mock, cmd_mock, is_sudo, ssh_mock):
        """ 测试正确字段 """

        # 正确字段 -> 创建成功
        resp = self.post(self.create_host_url, self.correct_host_data).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        host_info = resp.get("data")
        self.assertIsNotNone(host_info)
        for k, v in self.correct_host_data.items():
            # 密码字段加密处理，不相等
            if k == "password":
                self.assertNotEqual(host_info.get(k), v)
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
        self.assertIsNotNone(host_obj)
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


class ListHostTest(AutoLoginTest, HostsResourceMixin, GrafanaMainPageResourceMixin):
    """ 主机列表测试类 """

    def setUp(self):
        super(ListHostTest, self).setUp()
        self.create_host_url = reverse("hosts-list")
        self.list_host_url = reverse("hosts-list")
        self.get_grafana_main_pages()
        self.host_obj_ls = self.get_hosts(50)

    def tearDown(self):
        super(ListHostTest, self).tearDown()
        self.destroy_hosts()

    @staticmethod
    def mock_prometheus_info(host_obj_ls):
        """ 模拟 prometheus 返回数据 """
        for host in host_obj_ls:
            host.update({
                "cpu_usage": random.choice(
                    [None, random.randint(0, 100)]),
                "mem_usage": random.choice(
                    [None, random.randint(0, 100)]),
                "root_disk_usage": random.choice(
                    [None, random.randint(0, 100)]),
                "data_disk_status": random.choice(
                    [None, random.randint(0, 100)]),
                "cpu_status": random.choice(
                    [None, random.choice(Prometheus.STATUS)]),
                "mem_status": random.choice(
                    [None, random.choice(Prometheus.STATUS)]),
                "data_disk_usage": random.choice(
                    [None, random.choice(Prometheus.STATUS)]),
                "root_disk_status": random.choice(
                    [None, random.choice(Prometheus.STATUS)]),
            })
        return host_obj_ls

    def test_hosts_list_filter(self):
        """ 测试主机列表过滤 """

        # 查询主机列表 -> 展示所有主机
        resp = self.get(self.list_host_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertIsNotNone(resp.get("data"))
        # 数据总量为所有主机数
        self.assertEqual(resp.get("data").get("count"), len(self.host_obj_ls))

        # IP 过滤主机 -> 展示 IP 模糊匹配项
        ip_field = str(random.randint(1, 50))
        resp = self.get(self.list_host_url, {
            "ip": ip_field
        }).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertIsNotNone(resp.get("data"))
        count_number = Host.objects.filter(ip__contains=ip_field).count()
        self.assertEqual(resp.get("data").get("count"), count_number)

    def test_hosts_list_order(self):
        """ 测试主机列表排序 """

        # 不传递排序字段 -> 默认按照主机创建时间排序
        resp = self.get(self.list_host_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        res_ls = resp.get("data").get("results")
        sorted_res_ls = res_ls[:]
        random.shuffle(sorted_res_ls)
        sorted_res_ls = sorted(
            sorted_res_ls,
            key=lambda x: datetime.strptime(
                x.get("created"), "%Y-%m-%dT%H:%M:%S.%f"),
            reverse=True)
        self.assertEqual(res_ls, sorted_res_ls)

        # 指定字段排序 -> 返回排序后的列表
        reverse_flag = random.choice(("", "-"))
        order_field = random.choice(HostListView.ordering_fields)
        resp = self.get(self.list_host_url, {
            "ordering": f"{reverse_flag}{order_field}"
        }).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        res_ls = list(map(lambda x: x.get(order_field),
                          resp.get("data").get("results")))
        sorted_res_ls = res_ls[:]
        random.shuffle(sorted_res_ls)
        sorted_res_ls = sorted(
            sorted_res_ls,
            reverse=True if reverse_flag else False)
        self.assertEqual(res_ls, sorted_res_ls)

        # 指定动态排序字段 -> 返回值为None的不参与排序
        reverse_flag = random.choice(("", "-"))
        order_field = random.choice(HostListView.dynamic_fields)
        host_obj_ls = HostSerializer(Host.objects.all(), many=True).data
        with mock.patch.object(Prometheus, "get_host_info") as mock_prometheus_info:
            mock_prometheus_info.return_value = self.mock_prometheus_info(
                host_obj_ls)
            resp = self.get(self.list_host_url, {
                "ordering": f"{reverse_flag}{order_field}"
            }).json()
            # 返回值为 None 的数据不参与排序，排在末尾位置
            res_ls = list(map(lambda x: x.get(order_field),
                              resp.get("data").get("results")))
            none_number = res_ls.count(None)
            self.assertTrue(not any(res_ls[-none_number:]))
            res_ls = list(filter(lambda x: x is not None, res_ls))
            sorted_res_ls = res_ls[:]
            random.shuffle(sorted_res_ls)
            sorted_res_ls = sorted(
                sorted_res_ls,
                reverse=True if reverse_flag else False)
            self.assertEqual(res_ls, sorted_res_ls)


class HostDetailTest(AutoLoginTest, HostsResourceMixin):
    """ 主机详情测试类 """

    def setUp(self):
        super(HostDetailTest, self).setUp()
        self.host_obj_ls = self.get_hosts()

    def tearDown(self):
        super(HostDetailTest, self).tearDown()
        self.destroy_hosts()

    def test_host_detail(self):
        """ 测试主机详情 """
        resp = self.get(reverse("hostsDetail-detail", [
            random.choice(self.host_obj_ls).id
        ])).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertIsNotNone(resp.get("data"))


class UpdateHostTest(AutoLoginTest, HostsResourceMixin):
    """ 更新主机测试类 """

    def setUp(self):
        super(UpdateHostTest, self).setUp()
        self.host_obj_ls = self.get_hosts()

    def tearDown(self):
        super(UpdateHostTest, self).tearDown()
        self.destroy_hosts()

    @mock.patch.object(SSH, "check", return_value=(True, ""))
    @mock.patch.object(SSH, "is_sudo", return_value=(True, "is sudo"))
    @mock.patch.object(SSH, "cmd", return_value=(True, ""))
    def test_update_host(self, cmd_mock, is_sudo, ssh_mock):
        """ 测试更新一个主机 """
        # 更新不存在主机 -> 更新失败
        resp = self.put(reverse("hosts-detail", [9999]), {
            "instance_name": "mysql_instance_1",
            "ip": "127.0.0.255",
            "port": 36000,
            "username": "root",
            "password": "root_password",
            "data_folder": "/data",
            "operate_system": "CentOS",
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "未找到",
            "data": None
        })

        # 更新已存在主机，修改主机 IP -> 更新失败
        host_obj = random.choice(self.host_obj_ls)
        resp = self.put(reverse("hosts-detail", [host_obj.id]), {
            "instance_name": host_obj.instance_name,
            "ip": "127.0.0.255",
            "port": host_obj.port,
            "username": host_obj.username,
            "password": AESCryptor().decode(host_obj.password),
            "data_folder": host_obj.data_folder,
            "operate_system": host_obj.operate_system,
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "IP不可修改",
            "data": None
        })

        # 更新已存在主机，修改实例名为已存在 -> 更新失败
        host_obj = random.choice(self.host_obj_ls)
        host_queryset = Host.objects.exclude(
            instance_name=host_obj.instance_name)
        exists_name = random.choice(host_queryset).instance_name
        resp = self.put(reverse("hosts-detail", [host_obj.id]), {
            "instance_name": exists_name,
            "ip": host_obj.ip,
            "port": host_obj.port,
            "username": host_obj.username,
            "password": AESCryptor().decode(host_obj.password),
            "data_folder": host_obj.data_folder,
            "operate_system": host_obj.operate_system,
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "实例名已经存在",
            "data": None
        })

        # 正确修改数据 -> 修改成功
        host_obj = random.choice(self.host_obj_ls)
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

    @mock.patch.object(SSH, "check", return_value=(True, ""))
    @mock.patch.object(SSH, "is_sudo", return_value=(True, "is sudo"))
    @mock.patch.object(SSH, "cmd", return_value=(True, ""))
    def test_partial_update_host(self, cmd, is_sudo, ssh_mock):
        """ 更新一个现有主机的一个或多个字段 """

        # 更新不存在主机 -> 更新失败
        resp = self.patch(reverse("hosts-detail", [9999]), {
            "instance_name": "new_host_name",
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "未找到",
            "data": None
        })

        # 更新已存在主机，修改主机 IP -> 更新失败
        host_obj = random.choice(self.host_obj_ls)
        resp = self.patch(reverse("hosts-detail", [host_obj.id]), {
            "ip": "120.100.80.60",
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "IP不可修改",
            "data": None
        })

        # 更新已存在主机，修改实例名为已存在 -> 更新失败
        host_obj = random.choice(self.host_obj_ls)
        host_queryset = Host.objects.exclude(
            instance_name=host_obj.instance_name)
        exists_name = random.choice(host_queryset).instance_name
        resp = self.patch(reverse("hosts-detail", [host_obj.id]), {
            "instance_name": exists_name,
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "实例名已经存在",
            "data": None
        })

        # 正确修改数据 -> 修改成功
        host_obj = random.choice(self.host_obj_ls)
        resp = self.patch(reverse("hosts-detail", [host_obj.id]), {
            "instance_name": "new_host_name",
            "username": "new_username",
            "password": "new_password",
        }).json()
        # self.assertEqual(resp.get("code"), 0)
        # self.assertEqual(resp.get("message"), "success")
        # new_host_obj = resp.get("data")
        # self.assertIsNotNone(new_host_obj)
        # # 数据已更新
        # self.assertEqual(new_host_obj.get("instance_name"), "new_host_name")
        # # 更新时间变化
        # self.assertNotEqual(
        #     host_obj.modified,
        #     Host.objects.filter(id=host_obj.id).first().modified)


class HostFieldCheckTest(AutoLoginTest, HostsResourceMixin):
    """ 主机字段校验测试类 """

    def setUp(self):
        super(HostFieldCheckTest, self).setUp()
        self.field_check_url = reverse("fields-list")
        self.host_obj_ls = self.get_hosts()

    def tearDown(self):
        self.destroy_hosts()

    def test_create_host_check(self):
        """ 测试创建主机场景 """

        # instance_name 重复 -> 验证结果 False
        resp = self.post(self.field_check_url, {
            "instance_name": random.choice(self.host_obj_ls).instance_name
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
            "ip": random.choice(self.host_obj_ls).ip
        }).json()
        self.assertDictEqual(resp, {
            "code": 0,
            "message": "success",
            "data": False
        })

        # ip 不重复 -> 验证结果 True
        resp = self.post(self.field_check_url, {
            "ip": "123.1.2.3"
        }).json()
        self.assertDictEqual(resp, {
            "code": 0,
            "message": "success",
            "data": True
        })

    def test_error_host_check(self):
        """ 测试更新主机场景 """
        host_obj_one = random.choice(self.host_obj_ls)
        host_queryset = Host.objects.exclude(
            instance_name=host_obj_one.instance_name)
        host_obj_two = random.choice(host_queryset)

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


class ListIPTest(AutoLoginTest, HostsResourceMixin):
    """ IP 列表测试类 """

    def setUp(self):
        super(ListIPTest, self).setUp()
        self.ip_list_url = reverse("ips-list")
        self.get_hosts()

    def tearDown(self):
        super(ListIPTest, self).tearDown()
        self.destroy_hosts()

    def test_ip_list(self):
        """ 测试 IP 列表 """

        # 查询主机列表 -> 返回所有主机列表数据
        resp = self.get(self.ip_list_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertEqual(
            set(resp.get("data")),
            set(Host.objects.all().values_list("ip", flat=True)))


class HostMaintainTest(AutoLoginTest, HostsResourceMixin):
    """ 主机维护模式测试类 """

    def setUp(self):
        super(HostMaintainTest, self).setUp()
        self.host_maintain_url = reverse("maintain-list")
        self.host_obj_ls = self.get_hosts()

    def tearDown(self):
        super(HostMaintainTest, self).tearDown()
        self.destroy_hosts()

    def test_error_field(self):
        """ 测试错误字段校验 """
        host_obj_id_ls = list(map(lambda x: x.id, self.host_obj_ls))

        # host_ids 中含不存在的 ID -> 修改失败
        not_exists_id = 9999
        random_host_ls = random.sample(host_obj_id_ls, 5)
        random_host_ls.append(not_exists_id)
        resp = self.post(self.host_maintain_url, {
            "is_maintenance": True,
            "host_ids": random_host_ls
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": f"主机列表中有不存在的ID [{not_exists_id}]",
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
            "message": "主机列表中存在已 '关闭' 维护模式的主机",
            "data": None
        })

    @mock.patch.object(Alertmanager, "set_maintain_by_host_list", return_value=[1, 2, 3])
    @mock.patch.object(Alertmanager, "revoke_maintain_by_host_list", return_value=[1, 2, 3])
    def test_correct_field(self, mock_down, mock_up):
        """ 正确字段校验 """
        random_host_ls = random.sample(list(self.host_obj_ls), 5)
        random_host_id_ls = list(map(lambda x: x.id, random_host_ls))

        # 开启维护模式 -> 开启成功，记录操作
        data = {
            "is_maintenance": True,
            "host_ids": random_host_id_ls
        }
        resp = self.post(self.host_maintain_url, data).json()
        self.assertDictEqual(resp, {
            "code": 0,
            "message": "success",
            "data": data
        })
        # host_ids中主机，is_maintenance 状态均为 True
        is_maintenance_ls = Host.objects.filter(
            id__in=random_host_id_ls
        ).values_list("is_maintenance", flat=True)
        self.assertTrue(all(is_maintenance_ls))
        # 主机操作日志含有操作记录
        operate_log_ls = HostOperateLog.objects.filter(
            host__in=random_host_ls,
            description="开启[维护模式]")
        self.assertEqual(len(random_host_id_ls), len(operate_log_ls))
        self.assertEqual(
            len(operate_log_ls),
            len(operate_log_ls.filter(result="success")))

        # 关闭维护模式
        data = {
            "is_maintenance": False,
            "host_ids": random_host_id_ls
        }
        resp = self.post(self.host_maintain_url, data).json()
        self.assertDictEqual(resp, {
            "code": 0,
            "message": "success",
            "data": data
        })
        # host_ids中主机，is_maintenance 状态均为 False
        is_maintenance_ls = Host.objects.filter(
            id__in=random_host_id_ls
        ).values_list("is_maintenance", flat=True)
        self.assertTrue(not any(is_maintenance_ls))
        # 主机操作日志含有操作记录
        operate_log_ls = HostOperateLog.objects.filter(
            host__in=random_host_ls,
            description="关闭[维护模式]")
        self.assertEqual(len(random_host_id_ls), len(operate_log_ls))
        self.assertEqual(
            len(operate_log_ls),
            len(operate_log_ls.filter(result="success")))

    @mock.patch.object(Alertmanager, "set_maintain_by_host_list", return_value=None)
    @mock.patch.object(Alertmanager, "revoke_maintain_by_host_list", return_value=None)
    def test_alert_manager_error(self, mock_down, mock_up):
        """ alert manage 返回值异常 """

        random_host_ls = random.sample(list(self.host_obj_ls), 5)
        random_host_id_ls = list(map(lambda x: x.id, random_host_ls))

        # 开始维护模式 -> 开启失败，记录操作
        resp = self.post(self.host_maintain_url, {
            "is_maintenance": True,
            "host_ids": random_host_id_ls
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "主机'开启'维护模式失败",
            "data": None
        })
        # host_ids中主机，is_maintenance 状态均为 False
        is_maintenance_ls = Host.objects.filter(
            id__in=random_host_id_ls
        ).values_list("is_maintenance", flat=True)
        self.assertTrue(not any(is_maintenance_ls))
        # 主机操作日志含有操作记录
        operate_log_ls = HostOperateLog.objects.filter(
            host__in=random_host_ls,
            description="开启[维护模式]")
        self.assertEqual(len(random_host_id_ls), len(operate_log_ls))
        self.assertEqual(
            len(operate_log_ls),
            len(operate_log_ls.filter(result="failed")))

        # 关闭维护模式 -> 关闭失败，记录操作
        random_host_ls = random.sample(list(self.host_obj_ls), 5)
        random_host_id_ls = list(map(lambda x: x.id, random_host_ls))
        Host.objects.filter(
            id__in=random_host_id_ls
        ).update(is_maintenance=True)
        resp = self.post(self.host_maintain_url, {
            "is_maintenance": False,
            "host_ids": random_host_id_ls
        }).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "主机'关闭'维护模式失败",
            "data": None
        })
        # host_ids中主机，is_maintenance 状态均为 True
        is_maintenance_ls = Host.objects.filter(
            id__in=random_host_id_ls
        ).values_list("is_maintenance", flat=True)
        self.assertTrue(all(is_maintenance_ls))
        # 主机操作日志含有操作记录
        operate_log_ls = HostOperateLog.objects.filter(
            host__in=random_host_ls,
            description="关闭[维护模式]")
        self.assertEqual(len(random_host_id_ls), len(operate_log_ls))
        self.assertEqual(
            len(operate_log_ls),
            len(operate_log_ls.filter(result="failed")))


class HostAgentRestartTest(AutoLoginTest, HostsResourceMixin):
    """ 主机 agent 重启测试类 """

    def setUp(self):
        super(HostAgentRestartTest, self).setUp()
        self.host_restartHostAgent_url = reverse("restartHostAgent-list")
        self.host_obj_ls = self.get_hosts(2)

    def tearDown(self):
        super(HostAgentRestartTest, self).tearDown()
        self.destroy_hosts()

    @mock.patch.object(host_agent_restart, "delay", return_value=None)
    def test_success(self, host_agent_restart_mock):
        """ 请求成功测试 """

        host_obj_id_ls = list(map(lambda x: x.id, self.host_obj_ls))
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
        """ 请求失败测试 """

        resp = self.post(
            self.host_restartHostAgent_url,
            data={"host_ids": [random.randint(10000, 20000)]}
        ).json()
        self.assertEqual(resp.get("code"), 1)


class HostBatchValidateTest(AutoLoginTest, HostsResourceMixin, HostBatchRequestMixin):
    """ 主机批量校验测试类 """

    def setUp(self):
        super(HostBatchValidateTest, self).setUp()
        self.get_template_url = reverse("batchValidate-list")
        self.batch_validate_url = reverse("batchValidate-list")

    @staticmethod
    def create_repeat_data(host_list, field_name):
        """ 创建重复数据 """
        instance_name = "mysql_{}"
        ip = "10.0.0.{}"
        repeat_number = random.randint(2, 5)
        if field_name == "instance_name" or field_name == "all":
            instance_name = host_list[repeat_number].get("instance_name")
        if field_name == "ip" or field_name == "all":
            ip = host_list[repeat_number].get("ip")
        for i in range(repeat_number):
            host_list.append({
                "instance_name": instance_name.format(i),
                "ip": ip.format(i),
                "port": 36000,
                "username": "root",
                "password": "root_password",
                "data_folder": "/data",
                "operate_system": random.choice(("CentOS", "RedHat")),
                # "row": i * 100
            })
        return host_list, repeat_number

    def test_get_host_batch_template(self):
        """ 获取主机批量导入模板 """

        # 获取主机批量导入模板 -> 返回文件
        resp = self.get(self.get_template_url)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(isinstance(resp, FileResponse))
        self.assertTrue(resp.streaming)
        self.assertIsNotNone(resp.streaming_content)

    @mock.patch.object(SSH, "check", return_value=(True, ""))
    @mock.patch.object(SSH, "is_sudo", return_value=(True, "is sudo"))
    @mock.patch.object(SSH, "cmd", return_value=(True, ""))
    @mock.patch.object(insert_host_celery_task, "delay", return_value=None)
    def test_error_format(self, celery_task_mock, cmd_mock, is_sudo, ssh_mock):
        """ 测试错误格式 """

        # 格式错误 -> 添加失败
        data = self.get_host_batch_request(10, row=True)
        data["host_list"].append(12345)
        resp = self.post(self.batch_validate_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "数据格式错误",
            "data": None
        })

    @mock.patch.object(SSH, "check", return_value=(True, ""))
    @mock.patch.object(SSH, "is_sudo", return_value=(True, "is sudo"))
    @mock.patch.object(SSH, "cmd", return_value=(True, ""))
    @mock.patch.object(insert_host_celery_task, "delay", return_value=None)
    def test_batch_validate_error_field(self, celery_task_mock, cmd_mock, is_sudo, ssh_mock):
        """ 测试批量校验错误字段 """

        host_number = 10
        # 存在实例名重复 -> 返回值 error 中包含错误信息
        data = self.get_host_batch_request(host_number, row=True)
        data["host_list"], repeat_number = self.create_repeat_data(
            data.get("host_list"), "instance_name")
        resp = self.post(self.batch_validate_url, data).json()
        error_ls = resp.get("data").get("error", [])
        self.assertEqual(len(error_ls), repeat_number + 1)
        for error_host_info in error_ls:
            self.assertEqual(
                error_host_info.get("validate_error"),
                "实例名在表格中重复"
            )

        #  存在IP重复 -> 返回值 error 中包含错误信息
        data = self.get_host_batch_request(host_number, row=True)
        data["host_list"], repeat_number = self.create_repeat_data(
            data.get("host_list"), "ip")
        resp = self.post(self.batch_validate_url, data).json()
        error_ls = resp.get("data").get("error", [])
        self.assertEqual(len(error_ls), repeat_number + 1)
        for error_host_info in error_ls:
            self.assertEqual(
                error_host_info.get("validate_error"),
                "IP在表格中重复"
            )

        # 存在实例名、IP混合重复 -> 返回值 error 中包含错误信息
        data = self.get_host_batch_request(host_number, row=True)
        data["host_list"], repeat_number = self.create_repeat_data(
            data.get("host_list"), "all")
        resp = self.post(self.batch_validate_url, data).json()
        error_ls = resp.get("data").get("error", [])
        self.assertEqual(len(error_ls), repeat_number + 1)
        for error_host_info in error_ls:
            self.assertEqual(
                error_host_info.get("validate_error"),
                "实例名、IP在表格中重复"
            )

        # 测试主机数据信息不合法 -> 返回值 error 中包含错误信息
        data = self.get_host_batch_request(host_number, row=True)
        error_index = random.randint(0, host_number - 1)
        data.get("host_list")[error_index]["instance_name"] = "中文实例名"
        resp = self.post(self.batch_validate_url, data).json()
        error_ls = resp.get("data").get("error", [])
        self.assertEqual(len(error_ls), 1)
        self.assertEqual(
            error_ls[0].get("validate_error"),
            "实例名不可含有中文; 实例名格式不合法")

    @mock.patch.object(SSH, "check", return_value=(True, ""))
    @mock.patch.object(SSH, "is_sudo", return_value=(True, "is sudo"))
    @mock.patch.object(SSH, "cmd", return_value=(True, ""))
    @mock.patch.object(insert_host_celery_task, "delay", return_value=None)
    def test_batch_validate_correct_field(self, celery_task_mock, cmd_mock, is_sudo, ssh_mock):
        """ 测试批量校验正确字段 """

        # 正确字段 -> 返回值全部包含于 correct ，error 中无数据
        host_number = 10
        data = self.get_host_batch_request(host_number, row=True)
        resp = self.post(self.batch_validate_url, data).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        correct_ls = resp.get("data").get("correct", [])
        error_ls = resp.get("data").get("error", [])
        self.assertEqual(len(correct_ls), host_number)
        self.assertEqual(len(error_ls), 0)
        # 返回结果按照 row 进行排序
        self.assertEqual(
            correct_ls,
            list(sorted(correct_ls, key=lambda x: x.get("row")))
        )


class HostBatchImportTest(AutoLoginTest, HostsResourceMixin, HostBatchRequestMixin):
    """ 主机批量导入测试类 """

    def setUp(self):
        super(HostBatchImportTest, self).setUp()
        self.batch_import_url = reverse("batchImport-list")

    @mock.patch.object(SSH, "check", return_value=(True, ""))
    @mock.patch.object(SSH, "is_sudo", return_value=(True, "is sudo"))
    @mock.patch.object(SSH, "cmd", return_value=(True, ""))
    @mock.patch.object(insert_host_celery_task, "delay", return_value=None)
    def test_error_format(self, celery_task_mock, cmd_mock, is_sudo, ssh_mock):
        """ 测试错误格式 """

        # 格式错误 -> 添加失败
        data = self.get_host_batch_request(10, row=True)
        data["host_list"].append(12345)
        resp = self.post(self.batch_import_url, data).json()
        self.assertDictEqual(resp, {
            "code": 1,
            "message": "数据格式错误",
            "data": None
        })

    @mock.patch.object(SSH, "check", return_value=(True, ""))
    @mock.patch.object(SSH, "is_sudo", return_value=(True, "is sudo"))
    @mock.patch.object(SSH, "cmd", return_value=(True, ""))
    @mock.patch.object(insert_host_celery_task, "delay", return_value=None)
    def test_batch_import(self, celery_task_mock, cmd_mock, is_sudo, ssh_mock):
        """ 测试批量添加主机 """

        # 批量添加主机 -> 添加成功
        data = self.get_host_batch_request(10, row=True)
        resp = self.post(self.batch_import_url, data).json()
        self.assertDictEqual(resp, {
            "code": 0,
            "message": "success",
            "data": "添加成功"
        })
