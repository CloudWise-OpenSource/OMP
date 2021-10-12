from unittest import mock
from promemonitor.grafana_url import CurlPrometheus
from tests.base import AutoLoginTest
from rest_framework.reverse import reverse
from db_models.models import GrafanaMainPage

# 正确prometheus数据
correct_prometheus_data = {
    "status": "success",
    "data": {
        "alerts": [
            {
                "labels": {
                    "alertname": "instance down",
                    "instance": "10.0.3.72",
                    "job": "nodeExporter",
                    "severity": "critical"
                },
                "annotations": {
                    "consignee": "987654321@qq.com",
                    "description": "实例 10.0.3.72 已宕机超过1分钟",
                    "summary": "instance down alert(10.0.3.72)"
                },
                "state": "firing",
                "activeAt": "2021-09-27T07:08:05.68330499Z",
                "value": "0e+00"
            },
            {
                "labels": {
                    "alertname": "instance down",
                    "instance": "10.0.3.73",
                    "job": "nodeExporter",
                    "severity": "critical"
                },
                "annotations": {
                    "consignee": "987654321@qq.com",
                    "description": "实例 10.0.3.71 已宕机超过1分钟",
                    "summary": "instance down alert(10.0.3.71)"
                },
                "state": "firing",
                "activeAt": "2021-09-27T07:07:24.495164774Z",
                "value": "0e+00"
            },
            {'status': 'firing',
             'labels': {
                 'alertname': 'app state',
                 'app': 'dolaLogMonitorServer',
                 'env': '118',
                 'instance': '10.0.7.164',
                 'job': 'dolaLogMonitorServerExporter',
                 'severity': 'critical'
             },
             'annotations': {
                 'consignee': 'cw-email-address',
                 'description': '主机 10.0.7.164 中的 服务 dolaLogMonitorServer 已经down掉超过一分钟.',
                 'summary': 'app state(instance 10.0.7.164)'},
             'startsAt': '2021-06-26T07:23:42.479972051Z',
             'endsAt': '2021-06-26T07:38:01.343952065Z',
             'generatorURL': 'https://centos7:19011/graph?g0.expr=probe_success+%3D%3D+0&g0.tab=1',
             'fingerprint': '29a070a620efa300'}
        ]
    }
}


class GrafanaUrlTest(AutoLoginTest):
    def setUp(self):
        super(GrafanaUrlTest, self).setUp()
        self.list_grafanaurl_url = reverse("grafanaurl-list")
        grafana_list = [
            GrafanaMainPage(id="1", instance_name="node",
                            instance_url="/proxy/v1/grafana/d/9CWBz0bik/zhu-ji-xin-xi-mian-ban"),
            GrafanaMainPage(id="2", instance_name="service",
                            instance_url="/proxy/v1/grafana/d/9CSxoPAGz/fu-wu-zhuang-tai-xin-xi-mian-ban"),
            GrafanaMainPage(id="3", instance_name="log",
                            instance_url="/proxy/v1/grafana/d/liz0yRCZz/applogs"),
            GrafanaMainPage(id="4", instance_name="mysql",
                            instance_url="/proxy/v1/grafana/d/MQWgroiiz/mysql-xin-xi-mian-ban")
        ]
        GrafanaMainPage.objects.bulk_create(grafana_list)

    @mock.patch.object(CurlPrometheus, "curl_prometheus", return_value=correct_prometheus_data)
    def test_exception_list(self, curl_prometheus):
        """请求全列表"""
        resp = self.get(self.list_grafanaurl_url).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")

    @mock.patch.object(CurlPrometheus, "curl_prometheus", return_value=correct_prometheus_data)
    def test_exception_list_filter(self, curl_prometheus):
        """"多字段筛选并以单一字段排序"""
        data = {"ip": "10.0", "instance_name": "dola", "ordering": "ip"}
        resp = self.get(self.list_grafanaurl_url, data=data).json()
        self.assertEqual(resp.get("code"), 0)
        self.assertEqual(resp.get("message"), "success")
        self.assertTrue(resp.get("data", None) is not None)
