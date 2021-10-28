import random
from unittest import mock
from django.test import TestCase

from app_store.install_executor import InstallServiceExecutor
from tests.mixin import InstallHistoryResourceMixin
from utils.plugin.salt_client import SaltClient


class TestInstallExecutor(TestCase, InstallHistoryResourceMixin):
    """ 测试安装执行器 """

    @mock.patch.object(SaltClient, "cp_file", return_value=(True, ""))
    def test_send(self, cp_file):
        """ 测试发送服务包 """
        main_obj, detail_obj_ls = self.get_install_history()

        executor = InstallServiceExecutor(main_obj.id)
        executor.send(random.choice(detail_obj_ls))

    @mock.patch.object(SaltClient, "cmd", return_value=(True, ""))
    def test_unzip(self, cmd):
        """ 测试解压服务包 """
        main_obj, detail_obj_ls = self.get_install_history()

        executor = InstallServiceExecutor(main_obj.id)
        executor.unzip(random.choice(detail_obj_ls))

    @mock.patch.object(SaltClient, "cmd", return_value=(True, ""))
    def test_install(self, cmd):
        """ 测试安装 """
        main_obj, detail_obj_ls = self.get_install_history()

        executor = InstallServiceExecutor(main_obj.id)
        executor.install(random.choice(detail_obj_ls))

    @mock.patch.object(SaltClient, "cmd", return_value=(True, ""))
    def test_init(self, cmd):
        """ 测试初始化 """
        main_obj, detail_obj_ls = self.get_install_history()

        executor = InstallServiceExecutor(main_obj.id)
        executor.init(random.choice(detail_obj_ls))

    @mock.patch.object(SaltClient, "cmd", return_value=(True, ""))
    def test_start(self, cmd):
        """ 测试启动 """
        main_obj, detail_obj_ls = self.get_install_history()

        executor = InstallServiceExecutor(main_obj.id)
        executor.start(random.choice(detail_obj_ls))
