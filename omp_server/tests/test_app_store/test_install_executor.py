import random
from unittest import mock
from django.test import TestCase

from app_store.install_executor import InstallServiceExecutor
from db_models.models import MainInstallHistory
from utils.plugin.salt_client import SaltClient
from tests.mixin import InstallHistoryResourceMixin


class TestInstallExecutor(TestCase, InstallHistoryResourceMixin):
    """ 安装执行器测试类 """

    def test_action(self):
        """ 测试动作 """
        main_obj, detail_obj_ls = self.get_install_history()
        executor = InstallServiceExecutor(main_obj.id, "admin")

        # 发送执行正常
        with mock.patch.object(SaltClient, "cp_file") as mock_cp_file:
            mock_cp_file.return_value = True, "success"
            # 发送服务包
            detail_obj = random.choice(detail_obj_ls)
            is_success, _ = executor.send(detail_obj)
            self.assertTrue(is_success)
            self.assertEqual(detail_obj.send_flag, 2)

        # 发送执行异常
        with mock.patch.object(SaltClient, "cp_file") as mock_cp_file:
            mock_cp_file.return_value = False, "failed"
            # 发送服务包
            detail_obj = random.choice(detail_obj_ls)
            is_success, _ = executor.send(detail_obj)
            self.assertFalse(is_success)
            self.assertEqual(detail_obj.send_flag, 3)

        # 命令执行正常
        with mock.patch.object(SaltClient, "cmd") as mock_cmd:
            mock_cmd.return_value = True, "success"
            detail_obj = random.choice(detail_obj_ls)
            # 解压服务包
            is_success, _ = executor.unzip(detail_obj)
            self.assertTrue(is_success)
            self.assertEqual(detail_obj.unzip_flag, 2)
            # 安装
            is_success, _ = executor.install(detail_obj)
            self.assertTrue(is_success)
            self.assertEqual(detail_obj.install_flag, 2)
            # 初始化
            is_success, _ = executor.init(detail_obj)
            self.assertTrue(is_success)
            self.assertEqual(detail_obj.init_flag, 2)
            # 启动
            is_success, _ = executor.start(detail_obj)
            self.assertTrue(is_success)
            self.assertEqual(detail_obj.start_flag, 2)

        # 命令执行异常
        with mock.patch.object(SaltClient, "cmd") as mock_cmd:
            mock_cmd.return_value = False, "failed"
            detail_obj = random.choice(detail_obj_ls)
            # 解压服务包
            is_success, _ = executor.unzip(detail_obj)
            self.assertFalse(is_success)
            self.assertEqual(detail_obj.unzip_flag, 3)
            # 安装
            is_success, _ = executor.install(detail_obj)
            self.assertFalse(is_success)
            self.assertEqual(detail_obj.install_flag, 3)
            # 初始化
            is_success, _ = executor.init(detail_obj)
            self.assertFalse(is_success)
            self.assertEqual(detail_obj.init_flag, 3)
            # 启动
            is_success, _ = executor.start(detail_obj)
            self.assertFalse(is_success)
            self.assertEqual(detail_obj.start_flag, 3)

        # 服务无 init、start 脚本
        detail_obj = random.choice(detail_obj_ls)
        detail_obj.service.service_controllers.pop("init")
        detail_obj.service.service_controllers.pop("start")
        detail_obj.service.save()
        # 初始化 -> 成功 (跳过)
        is_success, _ = executor.init(detail_obj)
        self.assertTrue(is_success)
        self.assertEqual(detail_obj.init_flag, 2)
        # 启动 -> 成功 (跳过)
        is_success, _ = executor.start(detail_obj)
        self.assertTrue(is_success)
        self.assertEqual(detail_obj.start_flag, 2)

    @mock.patch.object(InstallServiceExecutor, "start", return_value=(True, ""))
    @mock.patch.object(InstallServiceExecutor, "init", return_value=(True, ""))
    @mock.patch.object(InstallServiceExecutor, "install", return_value=(True, ""))
    @mock.patch.object(InstallServiceExecutor, "unzip", return_value=(True, ""))
    @mock.patch.object(InstallServiceExecutor, "send", return_value=(True, ""))
    def test_main(self, mock_send, mock_unzip, mock_install, mock_init, mock_start):
        """ 测试主流程函数 """
        main_obj, detail_obj_ls = self.get_install_history()
        action_ls = (mock_send, mock_unzip,
                     mock_install, mock_init, mock_start)

        executor = InstallServiceExecutor(main_obj.id, "admin")
        # 所有动作执行成功 -> 主流程执行成功
        executor.main()
        main_obj.refresh_from_db()
        self.assertEqual(
            main_obj.install_status,
            MainInstallHistory.INSTALL_STATUS_SUCCESS)

        # 任意动作执行失败 -> 主流程执行失败
        action = random.choice(action_ls)
        action.return_value = False, "failed"
        executor.main()
        main_obj.refresh_from_db()
        self.assertEqual(
            main_obj.install_status,
            MainInstallHistory.INSTALL_STATUS_FAILED)
