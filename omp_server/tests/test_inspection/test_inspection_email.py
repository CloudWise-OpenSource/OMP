import json
from rest_framework.reverse import reverse

from tests.base import AutoLoginTest
from tests.test_inspection.inspection_mixin import InspectionHistoryMixin


class MockResponse:
    """
    自定义mock response类
    """
    status = 200

    def __init__(self, data):
        self.text = json.dumps(data)
        self.status_code = self.status

    def json(self):
        return json.loads(self.text)


class InspectionEmail(AutoLoginTest, InspectionHistoryMixin):

    def setUp(self):
        super(InspectionEmail, self).setUp()
        self.inspection_email_config_url = reverse(
            "inspectionSendEmailSetting-list")
        self.inspection_send_email_url = reverse("inspectionSendEmail-list")

    def tearDown(self):
        super(InspectionEmail, self).tearDown()

    def test_get_inspection_email_config(self):
        resp = self.get(self.inspection_email_config_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)

    def test_update_inspection_email_config(self):
        post_data = {
            "env_id": 1,
            "send_email": True,
            "to_users": "123@qq.com"
        }
        resp = self.post(self.inspection_email_config_url,
                         data=post_data).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data") is not None)

    # def test_inspection_send_email(self):
    #     from db_models.models import Env
    #     Env.objects.get_or_create(name="default")
    #     env = Env.objects.get(id=1)
    #     inspection_history_objs = InspectionHistoryMixin.get_inspection_history(
    #         env=env)
    #     inspection_report_objs = InspectionReportMixin.create_inspection_report(
    #         env=env)
    #     post_data = {
    #         "id": 1,
    #         "module": "deep",
    #         "to_users": "123@qq.com"
    #     }
    #     resp = self.post(self.inspection_send_email_url, data=post_data).json()
    #     print(resp)
    #     self.assertEqual(resp.get("code"), 0)
    #     self.assertEqual(resp.get("message"), "success")
    #     self.assertTrue(resp.get("data") is not None)
    #     for ih_obj in inspection_history_objs:
    #         ih_obj.delete()
    #     Env.objects.filter(name="default").delete()
