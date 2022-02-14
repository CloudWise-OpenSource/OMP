# -*- coding:utf-8 -*-
import os
import sys

import django

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
sys.path.append(os.path.join(PROJECT_DIR, 'omp_server'))
# 加载django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omp_server.settings")
django.setup()

from services.tasks import exec_action
from db_models.models import Service


def service_actions(actions, ip=None):
    choice = {
        "start": "1",
        "stop": "2",
        "restart": "3"
    }
    action = choice.get(actions)
    service_obj = Service.objects.filter(service_controllers__has_key=actions).exclude(
        service_status__in=[Service.SERVICE_STATUS_INSTALLING,
                            Service.SERVICE_STATUS_UPGRADE,
                            Service.SERVICE_STATUS_ROLLBACK,
                            Service.SERVICE_STATUS_DELETING
                            ]
    )
    if ip:
        service_obj = service_obj.filter(ip=ip)
    service_ids = service_obj.values("id", "service_instance_name")
    service_obj.update(service_status=Service.SERVICE_STATUS_DELETING)
    print("涉及到的实例名如下:")
    for i in service_ids:
        print(i.get("service_instance_name"))
        exec_action.delay(action, i.get("id"), "admin")


if __name__ == '__main__':
    try:
        actions = sys.argv[1:]
        if actions[0] not in ["start", "stop", "restart"]:
            print("请输入正确的(start,stop,restart)参数")
            sys.exit(1)
        service_actions(*actions)
    except Exception as err:
        print(f"请输入参数(start,stop,restart):{err}")
