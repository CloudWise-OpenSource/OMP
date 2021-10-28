from unittest import mock
from django.test import TestCase

from tests.mixin import InstallHistoryResourceMixin

from utils.plugin.salt_client import SaltClient


class TestInstallExecutor(TestCase, InstallHistoryResourceMixin):
    """ 测试安装执行器 """

    @mock.patch.object(SaltClient, "cp_file", return_value=(True, ""))
    @mock.patch.object(SaltClient, "cmd", return_value=(True, ""))
    def test_main(self, cmd, cp_file):
        """ 测试主函数 """
        # main_obj = self.get_install_history()
        # executor = InstallServiceExecutor(main_obj.id)
        # executor.main()
        pass
