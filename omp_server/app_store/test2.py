import os
import sys

import django

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR)))
PYTHON_PATH = os.path.join(PROJECT_DIR, "component/env/bin/python3")
MANAGE_PATH = os.path.join(PROJECT_DIR, "omp_server/manage.py")
sys.path.append(os.path.join(PROJECT_DIR, "omp_server"))

# 加载Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omp_server.settings")
django.setup()

from db_models.models import UploadPackageHistory

upload_obj = UploadPackageHistory(
    operation_uuid='dasdasd',
    operation_user='admin',
    package_name='dasdsadad.tar.gz',
    package_md5='dasd',
    package_path='dsad')
upload_obj.save()
print(upload_obj.id)
