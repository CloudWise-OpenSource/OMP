import random
from unittest import mock
from django.test import TestCase

from app_store.install_executor import InstallServiceExecutor
from app_store.tasks import install_service
from db_models.models import MainInstallHistory
from utils.plugin.salt_client import SaltClient
from promemonitor.prometheus_utils import PrometheusUtils
from tests.mixin import InstallHistoryResourceMixin


class TestInstallExecutor(TestCase, InstallHistoryResourceMixin):
    """ 安装执行器测试类 """

    @mock.patch.object(SaltClient, "cp_file", return_value=(True, ""))
    def test_action(self, cp_file):
        """ 测试动作 """
        main_obj, detail_obj_ls = self.get_install_history()

        executor = InstallServiceExecutor(main_obj.id)
        # 测试发送服务包
        executor.send(random.choice(detail_obj_ls))
        # 测试解压服务包
        executor.unzip(random.choice(detail_obj_ls))
        # 测试安装
        executor.install(random.choice(detail_obj_ls))
        # 测试初始化
        executor.init(random.choice(detail_obj_ls))
        # 测试启动
        executor.start(random.choice(detail_obj_ls))

    @mock.patch.object(InstallServiceExecutor, "start", return_value=(True, ""))
    @mock.patch.object(InstallServiceExecutor, "init", return_value=(True, ""))
    @mock.patch.object(InstallServiceExecutor, "install", return_value=(True, ""))
    @mock.patch.object(InstallServiceExecutor, "unzip", return_value=(True, ""))
    @mock.patch.object(InstallServiceExecutor, "send", return_value=(True, ""))
    def test_main(self, mock_send, mock_unzip, mock_install, mock_init, mock_start):
        """ 测试入口函数 """
        main_obj, detail_obj_ls = self.get_install_history()

        executor = InstallServiceExecutor(main_obj.id)
        executor.main()


class TestInstallServiceTask(TestCase, InstallHistoryResourceMixin):
    """ 安装服务任务测试类 """

    @mock.patch.object(PrometheusUtils, "add_service", return_value=(True, "success"))
    def test_executor_success(self, mock_add_service):
        """ 测试执行成功 """
        main_obj, detail_obj_ls = self.get_install_history()

        with mock.patch.object(InstallServiceExecutor, "main") as mock_executor:
            mock_executor.return_value = random.choice((True, False))
            # 正常状态
            install_service(main_obj.id)

        with mock.patch.object(InstallServiceExecutor, "main") as mock_executor:
            mock_executor.side_effect = Exception("install err")
            # 异常状态状态
            install_service(main_obj.id)
            main_obj.refresh_from_db()
            self.assertEqual(
                main_obj.install_status,
                MainInstallHistory.INSTALL_STATUS_FAILED)
