import json
import logging
from datetime import datetime, timedelta
from db_models.models import MonitorUrl
from utils.parse_config import MONITOR_PORT

import pytz
import requests

logger = logging.getLogger('server')


class Alertmanager:
    """
    定义alertmanager的参数及动作
    """

    def __init__(self):
        self.ip, self.port = self.get_alertmanager_config()
        self.headers = {'Content-Type': 'application/json'}
        self.add_url = f'http://{self.ip}:{self.port}/api/v1/silences'
        self.delete_url = f'http://{self.ip}:{self.port}/api/v1/silence'

    @staticmethod
    def get_alertmanager_config():
        alertmanager_url_config = MonitorUrl.objects.filter(
            name='alertmanager').first()
        if not alertmanager_url_config:
            return '127.0.0.1', MONITOR_PORT.get('alertmanager', 19013)  # 默认值

        ip = alertmanager_url_config.monitor_url.split(':')[0]
        port = alertmanager_url_config.monitor_url.split(':')[1]
        if ip and port:
            return ip, port
        return '127.0.0.1', MONITOR_PORT.get('alertmanager', 19013)  # 默认值

    @staticmethod
    def format_time(_time):
        """
        时区转换
        """
        if not _time:
            return (datetime.now(tz=pytz.UTC)).strftime(
                "%Y-%m-%dT%H:%M:%SZ")
        if isinstance(_time, datetime):
            return _time.astimezone(tz=pytz.UTC).strftime(
                "%Y-%m-%dT%H:%M:%SZ")
        return None

    def add_setting(self, value, name="env", start_time=None, ends_time=None):
        """
        设置维护模式
        :param value: 值 instance 对应ip， env对应env_name
        :param name: 值的key：instance, env
        :param start_time: startsAt：type: datetime
        :param ends_time: endsAt：type: datetime
        :return: 成功返回： "25b1ea3e-73db-43cd-ae81-a397f9e1bc88" (silenceId)
                失败：None
        """
        start_time_str = self.format_time(start_time)
        if not start_time_str:
            return None
        if not ends_time:
            ends_time = datetime.now() + timedelta(days=30)
        ends_time_str = self.format_time(ends_time)
        if not ends_time_str:
            return None
        data = {
            "matchers": [
                {"name": name, "value": value}
            ],
            "startsAt": start_time_str,
            "endsAt": ends_time_str,
            "createdBy": "api",
            "comment": "Silence",
            "status": {"state": "active"}
        }
        try:
            logger.info(data)
            resp = requests.post(
                self.add_url, data=json.dumps(data),
                headers=self.headers, timeout=5
            ).json()
            if resp.get("status") == "success":
                logger.info(resp)
                return resp.get("data").get("silenceId", None)
        except Exception as e:
            logger.error(str(e))
        return None

    def delete_setting(self, silence_id):
        """
        删除告警屏蔽规则
        :param silence_id: 规则id
        :return: 成功 True， 失败 False
        """
        try:
            resp = requests.delete(
                f"{self.delete_url}/{silence_id}", timeout=5).json()
        except Exception as e:
            logger.error(str(e))
            return False
        logger.info(resp)
        return resp.get("status") == "success"
