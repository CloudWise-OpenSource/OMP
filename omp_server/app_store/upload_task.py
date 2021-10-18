import os
from db_models.models import ApplicationHub, ProductHub, UploadPackageHistory, Labels
from utils.plugin import public_utils
import logging
from celery.utils.log import get_task_logger
from celery import shared_task
import time
import json
import redis
from utils.parse_config import OMP_REDIS_PORT, OMP_REDIS_PASSWORD, OMP_REDIS_HOST

logging.getLogger("paramiko").setLevel(logging.WARNING)
logger = get_task_logger("celery_log")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))


@shared_task
def publish_bak_end(uuid, exc_len):
    exc_task = True
    while exc_task:
        valid_uuids = UploadPackageHistory.objects.filter(operation_uuid=uuid,
                                                          package_parent__isnull=True,
                                                          ).exclude(package_status=2).count()
        print(valid_uuids)
        if valid_uuids != exc_len:
            time.sleep(5)
        else:
            publish_entry(uuid)
            exc_task = False
    re = redis.Redis(host=OMP_REDIS_HOST, port=OMP_REDIS_PORT, db=9, password=OMP_REDIS_PASSWORD)
    re.delete('back_end_verified')


@shared_task
def publish_entry(uuid):
    valid_uuids = UploadPackageHistory.objects.filter(is_deleted=False, operation_uuid=uuid,
                                                      package_parent__isnull=True,
                                                      package_status=0)
    valid_uuids.update(package_status=5)
    valid_packages = {}
    if valid_uuids:
        for j in valid_uuids:
            valid_packages[j.package_name] = j

    json_data = os.path.join(PROJECT_DIR, 'data', f'middle_data-{uuid}.json')
    with open(json_data, "r", encoding="utf8") as fp:
        lines = fp.readlines()
    valid_info = []
    for line in lines:
        json_line = json.loads(line)
        valid_obj = valid_packages.get(json_line.get('package_name'))
        if valid_obj:
            json_line['package_name'] = valid_obj
            valid_info.append(json_line)
        continue
    tmp_dir = '1'
    for line in valid_info:
        if line.get('kind') == 'product':
            CreateDatabase(line).create_product()
        else:
            CreateDatabase(line).create_component()
        tmp_dir = line.get('tmp_dir')
        valid_dir = os.path.join(PROJECT_DIR, 'package_hub', line.get('package_name').package_path)
        move_out = public_utils.local_cmd(f'rm -rf {valid_dir} && mv {tmp_dir} {valid_dir}')
        if move_out[2] != 0:
            line['package_name'].update(package_status=4)
            logger.error('移动或删除失败')
            return None
    clear_dir = os.path.dirname(tmp_dir)
    clear_out = public_utils.local_cmd(f'rm -rf {clear_dir}/*')
    if clear_out[2] != 0:
        valid_uuids.update(package_status=4)
        logger.error('清理环境失败')
        return None
    valid_uuids.update(package_status=3)


class CreateDatabase(object):
    def __init__(self, json_data):
        self.json_data = json_data
        self.label_type = None

    def explain(self, data):
        data_info = self.json_data.get(data)
        if data_info:
            if isinstance(data_info, dict) or isinstance(data_info, list):
                data_info = json.dumps(data_info, ensure_ascii=False)
        else:
            data_info = None
        return data_info

    def create_product(self):
        self.label_type = 1
        self.create_lab()
        app_obj = ProductHub(is_release=True, pro_name=self.json_data.get('name'),
                             pro_version=self.json_data.get('version'),
                             pro_description=self.json_data.get('description'),
                             pro_dependence=self.explain('dependencies'),
                             pro_services=self.explain('service'),
                             pro_package=self.json_data.get('package_name'),
                             pro_logo=self.json_data.get('image'),
                             extend_fields=self.json_data.get("extend_fields")
                             )
        app_obj.save()
        self.create_pro_app_lab(app_obj)
        service = self.json_data.pop('product_service')
        self._create_service(service, app_obj)
        pass

    def _create_service(self, service, app_obj):
        pro_history = app_obj.pro_package
        service_obj = UploadPackageHistory.objects.filter(package_parent=pro_history)
        valid_packages = {}
        for j in service_obj:
            valid_packages[j.package_name] = j
        valid_info = []
        for line in service:
            valid_obj = valid_packages.get(line.get('package_name'))
            if valid_obj:
                line['package_name'] = valid_obj
                valid_info.append(line)
            continue
        for info in valid_info:
            self.json_data = info
            ApplicationHub.objects.create(
                is_release=True, app_type=1, app_name=self.json_data.get("name"),
                app_version=self.json_data.get("version"),
                app_description=self.json_data.get("name"),
                app_port=self.explain("ports"),
                app_dependence=self.explain("dependencies"),
                app_install_args=self.explain("install"),
                app_controllers=self.explain("control"),
                app_package=self.json_data.get("package_name"),
                product=app_obj,
                extend_fields=self.json_data.get("extend_fields")
            )

    def create_component(self):
        self.label_type = 0
        self.create_lab()
        app_obj = ApplicationHub.objects.create(
            is_release=True, app_type=1, app_name=self.json_data.get("name"), app_version=self.json_data.get("version"),
            app_description=self.json_data.get("name"),
            app_port=self.explain("ports"),
            app_dependence=self.explain("dependencies"),
            app_install_args=self.explain("install"),
            app_controllers=self.explain("control"),
            app_package=self.json_data.get("package_name"),
            extend_fields=self.json_data.get("extend_fields"),
            app_logo=self.json_data.get("image")
        )
        app_obj.save()
        self.create_pro_app_lab(app_obj)
        pass

    def create_pro_app_lab(self, obj):
        labels = self.json_data.get('labels')
        for i in labels:
            label_obj = Labels.objects.get(label_name=i, label_type=self.label_type)
            if self.label_type == 1:
                obj.pro_labels.add(label_obj)
            else:
                obj.app_labels.add(label_obj)

    def create_lab(self):
        labels_obj = Labels.objects.filter(label_type=self.label_type)
        labels = [i.label_name for i in labels_obj]
        compare_labels = set(self.json_data.get('labels')) - set(labels)
        compare_list = []
        if compare_labels:
            for compare_label in compare_labels:
                label_obj = Labels(label_name=compare_label, label_type=self.label_type)
                compare_list.append(label_obj)
            Labels.objects.bulk_create(compare_list)
