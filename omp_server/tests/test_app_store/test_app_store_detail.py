from rest_framework.reverse import reverse

from tests.base import AutoLoginTest

from db_models.models import Labels, ApplicationHub, ProductHub, UploadPackageHistory


class AppStoreDetailTest(AutoLoginTest):
    """ 应用商店组件和产品测试类 """

    def setUp(self):
        super(AppStoreDetailTest, self).setUp()
        Labels.objects.create(label_type=0, label_name='数据库')
        Labels.objects.create(label_type=1, label_name='自有组件')

        UploadPackageHistory.objects.create(
            operation_uuid='12',
            package_name='mysql.tar.gz',
            package_md5='12md5',
            package_path='/data/mysql',
            package_status=0,
        )
        UploadPackageHistory.objects.create(
            operation_uuid='123',
            package_name='dosm.tar.gz',
            package_md5='123md5',
            package_path='/data/dosm',
            package_status=0,
        )

        ApplicationHub.objects.create(
            is_release=True, app_type=0,
            app_name='mysql',
            # labels
            app_version='5.1', app_description='mysql描述',
            app_port='3306', app_package=UploadPackageHistory.objects.get(operation_uuid=12)
        )
        ProductHub.objects.create(
            is_release=True, pro_name='dosm',
            pro_version='5.2',
            # labels
            pro_description='dosm描述', pro_dependence='',
            pro_services='dosmH5, dosmWeb',
            pro_package=UploadPackageHistory.objects.get(operation_uuid=123)
        )

    def test_application_detail(self):
        """ 测试应用详情 """

        # 查询应用表 -> 返回所指定应用名符合的数据
        app = ApplicationHub.objects.get(app_name='mysql', app_version='5.1')
        application_detail_url = reverse(
            "ApplicationDetail-detail", args=[app.id])
        resp = self.get(application_detail_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertIsNotNone(resp.get('data'))

    def test_product_detail(self):
        """
        测试产品详情
        """
        pro = ProductHub.objects.get(pro_name='dosm', pro_version='5.2')
        product_detail_url = reverse("ProductDetail-detail", args=[pro.id])
        resp = self.get(product_detail_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertIsNotNone(resp.get('data'))

    def tearDown(self):
        ProductHub.objects.filter(pro_name='dosm', pro_version='5.2').delete()
        ApplicationHub.objects.filter(
            app_name='mysql', app_version='5.1').delete()
        UploadPackageHistory.objects.filter(
            operation_uuid='12', package_name='mysql.tar.gz').delete()
        UploadPackageHistory.objects.filter(
            operation_uuid='123', package_name='dosm.tar.gz').delete()
        Labels.objects.filter(label_type=0, label_name='数据库').delete()
        Labels.objects.filter(label_type=1, label_name='自有组件').delete()
