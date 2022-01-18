import logging
import os

import requests
from django.db import models
from ruamel import yaml

from .monitor import AlertSendWaySetting


logger = logging.getLogger('server')


class EmailSMTPSetting(models.Model):
    email_host = models.EmailField("邮箱SMTP主机地址:smtp.163.com", null=True)
    email_port = models.IntegerField("邮箱SMTP端口:465", null=True)
    email_host_user = models.CharField(
        "邮箱SMTP服务器用户名:a@163.com", max_length=128, null=True)
    email_host_password = models.CharField(
        "邮箱SMTP服务器秘钥", max_length=128, null=True)

    class Meta:
        db_table = 'omp_email_smtp_setting'
        verbose_name = verbose_name_plural = '平台邮件服务器配置'

    alert_manage_key = {
        "EMAIL_SEND": "email_host_user",
        "smtp_auth_username": "email_host_user",
        "EMAIL_SEND_PASSWORD": "email_host_password",
        "smtp_auth_password": "email_host_password",
        "EMAIL_ADDRESS": "email_url",
    }

    def get_dict(self):
        return {
            "host": self.email_host,
            "port": self.email_port,
            "username": self.email_host_user,
            "password": self.email_host_password
        }

    @property
    def email_url(self):
        if hasattr(self, "email"):
            return self.email
        email_send = AlertSendWaySetting.objects.filter(
            way_name="email").first()
        email = ""
        if email_send and email_send.used:
            email = email_send.server_url.split(",")[0]
        setattr(self, "email", email)
        return email

    def update_config(self, key):
        if key in {"EMAIL_SEND_USER", "smtp_from"}:
            value = self.email_host_user
        elif key in {"SMTP_SMARTHOST", "smtp_smarthost"}:
            value = f"{self.email_host}:{self.email_port}"
        elif key in self.alert_manage_key:
            value = getattr(self, self.alert_manage_key.get(key))
        elif key in {"smtp_hello", "SMTP_HELLO"}:
            value = ".".join(self.email_host.split(".")[-2:])
        elif key == "RECEIVER":
            value = "cloudwise"
        else:
            value = None
        return value

    @staticmethod
    def reload_alert_manage():
        from promemonitor.alertmanager import Alertmanager
        alertmanager_url = Alertmanager.get_alertmanager_config()
        try:
            response = requests.post(f"http://{alertmanager_url}/-/reload")  # NOQA
        except Exception as e:
            logger.error(f"重载alertmanager配置出错！错误信息：{str(e)}")
            return False
        if response.status_code == 200:
            return True
        return False

    def set_omp_conf(self):
        # 更新omp.yaml
        from utils.parse_config import config_file_path
        with open(config_file_path, "r", encoding="utf8") as fp:
            content = fp.read()
        my_yaml = yaml.YAML()
        code = my_yaml.load(content)
        for key, value in code.get("alert_manager", {}).items():
            if key == "send_email":
                value = bool(self.email_url)
            else:
                value = self.update_config(key)
            if value is None:
                continue
            code["alert_manager"][key] = value
        with open(config_file_path, "w", encoding="utf8") as fp:
            my_yaml.dump(code, fp)

    def set_alert_manage_config(self):
        # 更新alert manage配置
        from omp_server.settings import PROJECT_DIR
        config_path = os.path.join(
            PROJECT_DIR, "component/alertmanager/conf/alertmanager.yml")
        with open(config_path, "r", encoding="utf8") as fp:
            code = yaml.load(fp.read(), yaml.Loader)
        for key, value in code.get("global", {}).items():
            value = self.update_config(key)
            if value is None:
                continue
            code["global"][key] = value

        if not self.email_url:
            for receiver in code.get("receivers"):
                if "email_configs" in receiver:
                    code.get("receivers")[0].pop("email_configs", {})
        else:
            email_configs = [
                {
                    "send_resolved": bool(self.email_url),
                    "to": self.email_url,
                    "headers": {"Subject": "OMP ALERT"},
                    "html": '{{ template \"email.to.html\" . }}'
                }
            ]
            code.get("receivers")[0]["email_configs"] = email_configs
        code["templates"] = [
            f"{PROJECT_DIR}/component/alertmanager/templates/*tmpl"]
        with open(config_path, "w", encoding="utf8") as fp:
            yaml.dump(code, fp, Dumper=yaml.RoundTripDumper)
        return self.reload_alert_manage()

    def update_setting_config(self):
        """
        更新配置文件
        :return:
        """
        self.set_omp_conf()
        return self.set_alert_manage_config(), self.email_url


class ModuleSendEmailSetting(models.Model):
    module = models.CharField(
        "功能模块:BackupSetting,JobSetting", max_length=64)
    send_email = models.BooleanField("是否开启邮件推送", default=False)
    to_users = models.TextField("邮箱接收用户", default="")
    env_id = models.IntegerField("环境id", default=1)

    class Meta:
        db_table = 'omp_module_email_send_setting'
        verbose_name = verbose_name_plural = '平台邮件发送账号配置'

    @classmethod
    def get_email_settings(cls, env_id, module):
        try:
            _obj = cls.objects.get(env_id=env_id, module=module)
        except Exception as e:
            logger.error(e)
            logger.error(f"module: {module}, env_id:{env_id}邮箱配置不存在")
            return None
        return _obj

    @classmethod
    def update_email_settings(cls, env_id, module, send_email, to_users):
        _obj, _ = cls.objects.get_or_create(env_id=env_id, module=module)
        _obj.send_email = send_email
        _obj.to_users = to_users
        _obj.save()
