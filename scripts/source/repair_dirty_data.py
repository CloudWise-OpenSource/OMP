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

from db_models.models import DetailInstallHistory, Host, Service

if __name__ == '__main__':
    detail_objs = DetailInstallHistory.objects.all()
    for obj in detail_objs:
        run_user = Host.objects.filter(ip=obj.service.ip).first().username
        if run_user != 'root':
            obj.install_detail_args['run_user'] = run_user
            for i in obj.install_detail_args.get('install_args', []):
                if i.get('key', '') == 'run_user':
                    i['default'] = run_user
            obj.save()
        else:
            continue
    service_obj = Service.split_objects.all()
    for ser in service_obj:
        if ser.service.app_name == "hadoop":
            ser.service_status = Service.SERVICE_STATUS_NORMAL
            ser.save()
