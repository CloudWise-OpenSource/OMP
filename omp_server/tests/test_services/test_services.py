import random
from rest_framework.reverse import reverse

from db_models.models import Service
from tests.base import AutoLoginTest
from tests.mixin import (
    LabelsResourceMixin, ServicesResourceMixin
)


class ListServiceTest(AutoLoginTest, ServicesResourceMixin):
    """ 服务列表测试类 """

    def setUp(self):
        super(ListServiceTest, self).setUp()
        self.list_service_url = reverse("services-list")
        self.service_ls = self.get_services()

    def tearDown(self):
        super(ListServiceTest, self).tearDown()
        self.destroy_services()

    def test_services_list_filter(self):
        """ 测试服务列表过滤 """

        # 查询服务列表 -> 展示所有非基础环境服务
        resp = self.get(self.list_service_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertEqual(
            resp.get("data").get("count"),
            self.service_ls.filter(
                service__is_base_env=False).count()
        )
        # 所有服务冗余字段 '亲和力' 为 tengine 的字段，视为前端服务，状态设置为 '正常'
        res_ls = resp.get("data").get("results")
        for service in res_ls:
            if service.get("is_web"):
                self.assertNotEqual(service.get("service_status"), "未监控")

        # IP 过滤 -> 模糊匹配
        ip_field = str(random.randint(1, 20))
        resp = self.get(self.list_service_url, {
            "ip": ip_field
        }).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertEqual(
            resp.get("data").get("count"),
            Service.objects.filter(
                service__is_base_env=False,
                ip__contains=ip_field).count()
        )

        # 服务实例名称过滤 -> 模糊匹配
        name_field = str(random.randint(1, 20))
        resp = self.get(self.list_service_url, {
            "service_instance_name": name_field
        }).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertEqual(
            resp.get("data").get("count"),
            self.service_ls.filter(
                service__is_base_env=False,
                service_instance_name__contains=name_field).count()
        )

        # 功能模块过滤 -> 精确匹配
        label_field = f"{LabelsResourceMixin.LABEL_NAME_START}_{random.randint(1, 10)}"
        resp = self.get(self.list_service_url, {
            "label_name": label_field
        }).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertEqual(
            resp.get("data").get("count"),
            Service.objects.filter(
                service__is_base_env=False,
                service__app_labels__label_name=label_field).count()
        )

        # 服务类型过滤 -> 精确匹配
        app_type = random.choice((0, 1))
        resp = self.get(self.list_service_url, {
            "app_type": app_type
        }).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertEqual(
            resp.get("data").get("count"),
            Service.objects.filter(
                service__is_base_env=False,
                service__app_type=app_type).count()
        )

    def test_services_list_order(self):
        """ 测试服务列表排序 """

        # 不传递排序字段 -> 默认按照创建时间倒序
        resp = self.get(self.list_service_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertIsNotNone(resp.get("data"))

        # # 传递排序字段，按照指定字段排序
        reverse_flag = random.choice(("", "-"))
        order_field = "service_instance_name"
        ordering = f"{reverse_flag}{order_field}"
        resp = self.get(self.list_service_url, {
            "ordering": ordering
        }).json()
        instance_name_ls = list(map(
            lambda x: x.get("service_instance_name"),
            resp.get("data").get("results"))
        )
        target_instance_name_ls = list(
            self.service_ls.filter(
                service__is_base_env=False).order_by(
                ordering).values_list(
                "service_instance_name", flat=True))[:10]
        self.assertEqual(instance_name_ls, target_instance_name_ls)


class ServiceDetailTest(AutoLoginTest, ServicesResourceMixin):
    """ 服务详情测试类 """

    def setUp(self):
        super(ServiceDetailTest, self).setUp()
        self.service_ls = self.get_services()

    def tearDown(self):
        super(ServiceDetailTest, self).tearDown()
        self.destroy_services()

    def test_service_detail(self):
        """ 测试服务详情 """

        # 使用不存在 id -> 未找到
        resp = self.get(reverse("services-detail", [9999])).json()
        self.assertDictEqual(resp, {
            'code': 1,
            'message': '未找到',
            'data': None
        })

        # 使用存在 id -> 查询成功
        resp = self.get(reverse("services-detail", [
            random.choice(self.service_ls).id
        ])).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)
