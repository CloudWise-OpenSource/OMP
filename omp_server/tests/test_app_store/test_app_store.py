import random
from django.db.models import Max
from rest_framework.reverse import reverse

from tests.base import AutoLoginTest
from tests.mixin import (
    LabelsResourceMixin, ApplicationResourceMixin,
    ProductResourceMixin
)
from db_models.models import Labels, ApplicationHub


class LabelListTest(AutoLoginTest, LabelsResourceMixin):
    """ 标签列表测试类 """

    def setUp(self):
        super(LabelListTest, self).setUp()
        self.label_list_url = reverse("labels-list")

    def test_label_list(self):
        """ 测试标签列表 """

        self.get_labels()

        # 查询标签列表 -> 返回所有标签列表数据
        resp = self.get(self.label_list_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertEqual(
            set(resp.get("data")),
            set(Labels.objects.values_list("label_name", flat=True))
        )

        # 查询指定类型标签 -> 返回指定类型标签列表数据
        choice = random.choice(Labels.LABELS_CHOICES)
        resp = self.get(self.label_list_url, {
            "label_type": choice[0]
        }).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertEqual(
            set(resp.get("data")),
            set(Labels.objects.filter(
                label_type=choice[0]
            ).values_list("label_name", flat=True))
        )

        self.destroy_labels()


class ComponentListTest(AutoLoginTest, ApplicationResourceMixin):
    """ 基础组件列表测试类 """

    def setUp(self):
        super(ComponentListTest, self).setUp()
        self.component_list_url = reverse("components-list")

    def test_component_list_filter(self):
        """ 测试基础组件列表过滤 """
        app_obj_ls = self.get_application()

        # 查询组件列表 -> 按名称合并展示所有已发布组件
        resp = self.get(self.component_list_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        comp_set = set(app_obj_ls.filter(
            is_release=True,
            app_type=ApplicationHub.APP_TYPE_COMPONENT
        ).values_list("app_name"))
        self.assertEqual(resp.get("data").get("count"), len(comp_set))

        # 组件名过滤 -> 展示组件名模糊匹配项
        resp = self.get(self.component_list_url, {
            "app_name": "app_1"
        }).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        comp_set = set(app_obj_ls.filter(
            is_release=True,
            app_type=ApplicationHub.APP_TYPE_COMPONENT,
            app_name__contains="app_1",
        ).values_list("app_name"))
        self.assertEqual(resp.get("data").get("count"), len(comp_set))

        # 标签类型过滤 -> 展示标签名匹配项
        label_name = random.choice(Labels.LABELS_CHOICES)[1]
        resp = self.get(self.component_list_url, {
            "type": label_name
        }).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        comp_set = set(app_obj_ls.filter(
            is_release=True,
            app_type=ApplicationHub.APP_TYPE_COMPONENT,
            app_labels__label_name=label_name,
        ).values_list("app_name"))
        self.assertEqual(resp.get("data").get("count"), len(comp_set))

        self.destroy_application()

    def test_component_list_order(self):
        """ 测试基础组建列表排序 """
        app_obj_ls = self.get_application()

        # 查询组件列表 -> 各组件返回最新数据，按照创建时间排序
        resp = self.get(self.component_list_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        obj_ls = list(app_obj_ls.filter(
            is_release=True,
            app_type=ApplicationHub.APP_TYPE_COMPONENT
        ).values("app_name").annotate(c=Max("created")).order_by(
            "-created").values_list("app_name", flat=True))
        target_ls = []
        for obj in obj_ls:
            if obj not in target_ls:
                target_ls.append(obj)
        result_ls = list(map(
            lambda x: x.get("app_name"),
            resp.get("data").get("results")))
        self.assertEqual(result_ls, target_ls)

        self.destroy_application()


class ServiceListTest(AutoLoginTest, ProductResourceMixin):
    """ 产品列表测试类 """

    def setUp(self):
        super(ServiceListTest, self).setUp()
        self.service_list_url = reverse("services-list")

    def test_service_list_filter(self):
        """ 测试应用服务列表过滤 """
        service_obj_ls = self.get_product()

        # 查询服务列表 -> 按名称合并展示所有已发布服务
        resp = self.get(self.service_list_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        service_set = set(service_obj_ls.filter(
            is_release=True
        ).values_list("pro_name"))
        self.assertEqual(resp.get("data").get("count"), len(service_set))

        # 服务名过滤 -> 展示服务名模糊匹配项
        resp = self.get(self.service_list_url, {
            "pro_name": "pro_1"
        }).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        service_set = set(service_obj_ls.filter(
            is_release=True,
            pro_name__contains="pro_1",
        ).values_list("pro_name"))
        self.assertEqual(resp.get("data").get("count"), len(service_set))

        self.destroy_product()

    def test_service_list_order(self):
        """ 测试应用服务列表排序 """
        service_obj_ls = self.get_product()

        # 查询应用服务列表 -> 各组件返回最新数据，按照创建时间排序
        resp = self.get(self.service_list_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        obj_ls = list(service_obj_ls.filter(
            is_release=True,
        ).values("pro_name").annotate(c=Max("created")).order_by(
            "-created").values_list("pro_name", flat=True))
        target_ls = []
        for obj in obj_ls:
            if obj not in target_ls:
                target_ls.append(obj)
        result_ls = list(map(
            lambda x: x.get("pro_name"),
            resp.get("data").get("results")))
        self.assertEqual(result_ls, target_ls[:10])

        self.destroy_product()
