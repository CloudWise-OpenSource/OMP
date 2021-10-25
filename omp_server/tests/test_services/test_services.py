import random
from rest_framework.reverse import reverse

from db_models.models import Service
from services.views import ServiceListView

from tests.base import AutoLoginTest
from tests.mixin import (
    LabelsResourceMixin, ServicesResourceMixin
)


class ListServiceTest(AutoLoginTest, ServicesResourceMixin):
    """ 服务列表测试类 """

    def setUp(self):
        super(ListServiceTest, self).setUp()
        self.list_service_url = reverse("services-list")

    def test_services_list_filter(self):
        """ 测试服务列表过滤 """
        service_ls = self.get_services()

        # 查询服务列表 -> 展示所用服务
        resp = self.get(self.list_service_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertEqual(resp.get("data").get("count"), len(service_ls))

        # IP 过滤 -> 模糊匹配
        ip_field = str(random.randint(1, 20))
        resp = self.get(self.list_service_url, {
            "ip": ip_field
        }).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertEqual(
            resp.get("data").get("count"),
            Service.objects.filter(ip__contains=ip_field).count()
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
            Service.objects.filter(
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
                service__app_type=app_type).count()
        )

        self.destroy_services()

    def test_services_list_order(self):
        """ 测试服务列表排序 """
        self.get_services()

        # 不传递排序字段 -> 默认按照创建时间倒序
        resp = self.get(self.list_service_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        instance_name_ls = list(map(
            lambda x: x.get("service_instance_name"),
            resp.get("data").get("results"))
        )
        target_instance_name_ls = list(Service.objects.order_by(
            "-created").values_list("service_instance_name", flat=True))[:10]
        self.assertEqual(instance_name_ls, target_instance_name_ls)

        # 传递排序字段，按照指定字段排序
        reverse_flag = random.choice(("", "-"))
        order_field = random.choice(ServiceListView.ordering_fields)
        ordering = f"{reverse_flag}{order_field}"
        resp = self.get(self.list_service_url, {
            "ordering": ordering
        }).json()
        instance_name_ls = list(map(
            lambda x: x.get("service_instance_name"),
            resp.get("data").get("results"))
        )
        target_instance_name_ls = list(Service.objects.order_by(
            ordering).values_list("service_instance_name", flat=True))[:10]
        self.assertEqual(instance_name_ls, target_instance_name_ls)

        self.destroy_services()
