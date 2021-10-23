from rest_framework.reverse import reverse

from tests.base import AutoLoginTest
from tests.mixin import ServicesResourceMixin


class ListServiceTest(AutoLoginTest, ServicesResourceMixin):
    """ 服务列表测试类 """

    def setUp(self):
        super(ListServiceTest, self).setUp()
        self.list_service_url = reverse("services-list")

    def test_services_list(self):
        """ 测试服务列表 """
        service_ls = self.get_services()
        print(service_ls)

        resp = self.get(self.list_service_url).json()
        print(resp)
