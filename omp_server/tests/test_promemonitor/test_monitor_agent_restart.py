# -*- coding: utf-8 -*-
# Project: test_monitor_agent_restart
# Author: jon.liu@yunzhihui.com
# Create time: 2021-10-09 11:42
# IDE: PyCharm
# Version: 1.0
# Introduction:

import random
from unittest import mock

from rest_framework.reverse import reverse

from tests.base import AutoLoginTest
from tests.mixin import HostsResourceMixin
from promemonitor.tasks import monitor_agent_restart


class MonitorAgentRestartTest(AutoLoginTest, HostsResourceMixin):
    """ 监控Agent重启测试类 """

    def setUp(self):
        super(MonitorAgentRestartTest, self).setUp()
        self.restartMonitorAgent_url = reverse("restartMonitorAgent-list")

    @mock.patch.object(monitor_agent_restart, "delay", return_value=None)
    def test_success(self, monitor_agent_restart_obj):
        """ 请求成功测试 """
        host_obj_ls = self.get_hosts(2)

        host_obj_id_ls = list(map(lambda x: x.id, host_obj_ls))
        resp = self.post(
            self.restartMonitorAgent_url,
            data={"host_ids": host_obj_id_ls}
        ).json()
        self.assertDictEqual(resp, {
            "code": 0,
            "message": "success",
            "data": {
                "host_ids": host_obj_id_ls
            }
        })

        self.destroy_hosts()

    @mock.patch.object(monitor_agent_restart, "delay", return_value=None)
    def test_failed(self, monitor_agent_restart_obj):
        """ 请求失败测试 """
        self.get_hosts(2)

        resp = self.post(
            self.restartMonitorAgent_url,
            data={"host_ids": [random.randint(10000, 20000)]}
        ).json()
        self.assertEqual(resp.get("code"), 1)

        self.destroy_hosts()
