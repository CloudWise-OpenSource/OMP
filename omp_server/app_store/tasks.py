"""
主机相关异步任务
"""

import os
import random
import yaml
import logging
import json

import redis
from celery import shared_task
from celery.utils.log import get_task_logger
from utils.plugin import public_utils
from utils.parse_config import OMP_REDIS_PORT, OMP_REDIS_PASSWORD, \
    OMP_REDIS_HOST
from db_models.models import UploadPackageHistory, ApplicationHub, ProductHub
from app_store.upload_task import CreateDatabase
import time

# 屏蔽celery任务日志中的paramiko日志
logging.getLogger("paramiko").setLevel(logging.WARNING)
logger = get_task_logger("celery_log")

current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(os.path.dirname(current_dir))
package_hub = os.path.join(project_dir, "package_hub")

package_dir = {"back_end_verified": "back_end_verified",
               "front_end_verified": "front_end_verified",
               "verified": "verified"}


class PublicAction(object):
    def __init__(self, md5):
        self.md5_obj = UploadPackageHistory.objects.filter(package_md5=md5)

    def update_package_status(self, status, msg=None):
        self.md5_obj.update(package_status=status, error_msg=msg)
        logger.info(msg)

    def update_fail_status(self, msg=None):
        self.md5_obj.update(package_status=1, error_msg=msg)


class FiledCheck(object):
    """
     弱校验 只校验key
     强校验 在弱校验key存在的情况下校验value值
     params is_weak强校验前执行弱校验
     ignore 强校验中去除一些必要字段的强校验
     settings 待校验文本
     field 需要校验的字段，如果为空则强校验文本所有字段是否value为空
     is_weak 暂时不支持is_weak = True
    """

    def __init__(self, yaml_dir, db_obj):
        self.db_obj = db_obj
        self.yaml_dir = yaml_dir

    def strong_check(self, settings, field=None, is_weak=False, ignore=None):
        if is_weak:
            if not self.weak_check(settings, field):
                return False
        if ignore:
            field = field - ignore
        if isinstance(settings, dict):
            if not field:
                field = set(settings.keys())
            for i in field:
                if settings.get(i) is None:
                    self.db_obj.update_package_status(
                        1,
                        f"yml{i}缺乏值，检查yml文件{self.yaml_dir}")
                    return False
            return True
        elif isinstance(settings, list):
            if not field:
                field = set(settings[0].keys())
            for i in settings:
                for j in field:
                    if i.get(j) is None:
                        self.db_obj.update_package_status(
                            1,
                            f"yml{i}缺乏值，检查yml文件{self.yaml_dir}")
                        return False
            return True
        else:
            return False

    def weak_check(self, settings, field):
        if isinstance(settings, dict):
            status = set(settings.keys()) - field
            if status:
                self.db_obj.update_package_status(
                    1,
                    f"yml{str(status)}字段和预期不符，检查yml文件{self.yaml_dir}")
                return False
            return True
        elif isinstance(settings, list):
            for i in settings:
                status = set(i.keys()) - field
                if status:
                    self.db_obj.update_package_status(
                        1,
                        f"yml{str(status)}字段和预期不符，检查yml文件{self.yaml_dir}")
                    return False
            return True
        else:
            return False


@shared_task
def front_end_verified(uuid, operation_user, package_name, md5, random_str, ver_dir, upload_obj):
    upload_obj = UploadPackageHistory.objects.get(id=upload_obj)
    package_path = os.path.join(package_hub, ver_dir)
    file_name = os.path.join(package_path, package_name)
    md5_out = public_utils.local_cmd(f'md5sum {file_name}')
    if md5_out[2] != 0:
        upload_obj.package_status = 1
        upload_obj.error_msg = "md5sum命令执行失败"
        upload_obj.save()
    md5sum = md5_out[0].split()[0]
    md5 = md5sum
    upload_obj.package_md5 = md5
    upload_obj.save()
    public_action = PublicAction(md5)
    touch_name = file_name[:-7] if file_name[-7:] == ".tar.gz" else file_name[
                                                                    :-3]
    tmp_dir = os.path.join(package_path, touch_name + random_str)
    os.mkdir(tmp_dir)
    tar_out = public_utils.local_cmd(f'tar -xvf {file_name} -C {tmp_dir}')
    if tar_out[2] != 0:
        return public_action.update_package_status(
            1,
            f"安装包{package_name}解压失败或者压缩包格式不合规")
    app_name = package_name.split('-', 1)[0]
    tmp_dir = os.path.join(tmp_dir, app_name)
    check_file = os.path.join(tmp_dir, f'{app_name}.yaml')
    if not os.path.exists(check_file):
        return public_action.update_package_status(
            1,
            f"安装包{package_name}:{app_name}.yaml文件不存在")
    explain_yml = ExplainYml(public_action, check_file).explain_yml()
    # 这个校验可能用不到
    if isinstance(explain_yml, bool):
        return None
    kind = explain_yml[1].get("kind")
    versions = explain_yml[1].get("version")
    pro_name = explain_yml[1]['name'] + "-" + explain_yml[1]['version']
    # 校验图片
    image = None
    if kind == 'product' or 'component':
        try:
            image_dir = os.path.join(tmp_dir, f'{app_name}.svg')
            if os.path.exists(image_dir):
                with open(image_dir, 'r') as fp:
                    image = fp.read()
        except UnicodeDecodeError as e:
            logger.error(f'{package_name}:图片格式异常{e}')
            return public_action.update_package_status(
                1,
                f"{package_name}图片格式异常")
    # 校验产品yml
    if kind == 'product':
        service = explain_yml[1].get("service")
        explain_service_list = []
        yml_dirs = os.path.join(tmp_dir, app_name)
        service_name = [os.path.join(tmp_dir, i) for i in os.listdir(tmp_dir)]
        service_packages_value = [
            p for p in service_name if
            os.path.isfile(p) and 'tar' in p]
        service_packages_key = [service_package.split("-")[0].rsplit("/", 1)[1]
                                for service_package in
                                service_packages_value]
        service_package = dict(
            zip(service_packages_key, service_packages_value))
        for i in service:
            service_dir = os.path.join(yml_dirs, f"{i.get('name')}.yaml")
            if not os.path.exists(service_dir):
                return public_action.update_package_status(
                    1,
                    f"安装包{file_name}:{service_dir}文件不存在")
            explain_service_yml = ExplainYml(public_action,
                                             service_dir).explain_yml()
            if isinstance(explain_service_yml, bool):
                return None
            name = i.get('name')
            service_pk = service_package.get(name)
            if not service_pk:
                continue
            service_pk_name = service_pk.rsplit("/", 1)[1]
            md5_ser = public_utils.local_cmd(f'md5sum {service_pk}')
            if md5_ser[2] != 0:
                return public_action.update_package_status(
                    1,
                    f"md5sum命令执行失败")
            md5_service = md5_ser[0].split()[0]
            UploadPackageHistory.objects.create(
                operation_uuid=uuid,
                operation_user=operation_user,
                package_name=service_pk_name,
                package_md5=md5_service,
                package_path=os.path.join(
                    package_dir.get(
                        "verified"), pro_name
                ),
                package_status=0,
                package_parent=upload_obj
            )
            explain_service_yml[1]['package_name'] = service_pk_name
            explain_service_list.append(explain_service_yml[1])
        explain_yml[1]['product_service'] = explain_service_list
        tmp_dir = tmp_dir + "-" + versions
    else:
        tmp_dir = file_name
    explain_yml[1]['image'] = image
    explain_yml[1]['package_name'] = package_name
    explain_yml[1]['tmp_dir'] = tmp_dir
    # 开启写入中间结果  包含入库所有的信息
    middle_data = os.path.join(project_dir, 'data', f'middle_data-{uuid}.json')
    with open(middle_data, mode='a', encoding='utf-8') as f:
        f.write(json.dumps(explain_yml[1], ensure_ascii=False) + '\n')
    name = explain_yml[1]['name']
    version = explain_yml[1]['version']
    if explain_yml[1]['kind'] == 'product':
        count = ProductHub.objects.filter(pro_version=version,
                                          pro_name=name).count()
    else:
        count = ApplicationHub.objects.filter(app_version=version,
                                              app_name=name).count()
    if count:
        count = "已存在,将覆盖"
    else:
        count = None
    return public_action.update_package_status(0, count)


class ExplainYml:
    """
    校验yml文件总类
    params:
    db_obj 更新记录表obj
    yaml_dir yaml文件路径
    """

    def __init__(self, db_obj, yaml_dir):
        # md5 的
        self.db_obj = db_obj
        self.yaml_dir = yaml_dir
        self.check_obj = FiledCheck(self.yaml_dir, self.db_obj)

    def explain_yml(self):
        """
        各种kind类型公共字段
        """
        kinds = ['product', 'service', 'upgrade', 'component']
        try:
            with open(self.yaml_dir, "r", encoding="utf8") as fp:
                settings = yaml.load(fp, Loader=yaml.FullLoader)
        except Exception as e:
            self.db_obj.update_package_status(
                1,
                f"yml包格式错误，检查yml文件{self.yaml_dir}:{e}")
            return False
        kind = settings.pop('kind', None)
        name = settings.pop('name', None)
        version = settings.pop('version', None)
        description = settings.pop('description', -1)
        dependencies = settings.pop('dependencies', -1)

        if dependencies:
            for i in dependencies:
                if not i.get("name") or not i.get("version"):
                    self.db_obj.update_package_status(
                        1,
                        f"yml校验dependecies校验失败，检查yml文件{self.yaml_dir}")
                    return False
        if description == "-1" or dependencies == "-1":
            self.db_obj.update_package_status(
                1,
                f"yml校验description或dependencies校验失败，检查yml文件{self.yaml_dir}")
            return False
        if kind not in kinds:
            self.db_obj.update_package_status(
                1,
                f"yml校验kind校验失败，检查yml文件{self.yaml_dir}")
            return False
        if not name or not version:
            self.db_obj.update_package_status(
                1,
                f"yml校验name或version校验失败，检查yml文件{self.yaml_dir}")
            return False
        yml = getattr(self, kind)(settings)
        if isinstance(yml, bool):
            if not yml:
                return False
        db_filed = {
            "kind": kind,
            "name": name,
            "version": version,
            "description": description,
            "dependencies": dependencies,
            "extend_fields": settings
        }
        db_filed.update(yml[1])
        return True, db_filed

    def product(self, settings):
        """产品级校验"""
        db_filed = {}
        service = settings.pop('service', None)
        if not service:
            self.db_obj.update_package_status(
                1,
                f"yml校验service校验失败，检查yml文件{self.yaml_dir}")
            return False
        for i in service:
            if not i.get("name") or not i.get("version"):
                self.db_obj.update_package_status(
                    1,
                    f"yml校验service校验失败，检查yml文件{self.yaml_dir}")
                return False
        db_filed['service'] = service
        label = settings.pop('labels', None)
        if not label:
            self.db_obj.update_package_status(
                1,
                f"yml校验labels失败，检查yml文件{self.yaml_dir}")
            return False
        db_filed['labels'] = label
        return True, db_filed

    def service(self, settings):
        """校验kind为service"""
        db_filed = {}
        first_check = {"auto_launch", "monitor", "ports", "resources",
                       "install", "control", "deploy", "base_env"}
        if not self.check_obj.weak_check(settings, first_check):
            return False
        # auto_launch 校验
        first_strong_check = {"auto_launch"}
        if not self.check_obj.strong_check(settings, first_strong_check):
            return False
        # ports 校验
        ports = settings.pop('ports')
        ports_strong_check = {"name", "protocol", "port", "key"}
        port = self.check_obj.strong_check(
            ports, ports_strong_check,
            is_weak=True,
            ignore={"key"}) if ports else 1
        if not port:
            return False
        db_filed['ports'] = ports
        #  control校验
        control = settings.pop('control')
        control_weak_check = {"start", "stop", "restart", "reload", "install",
                              "init"}
        control_check = self.check_obj.weak_check(
            control,
            control_weak_check) if control else 1
        if not control_check:
            return False
        control_strong_check = self.check_obj.strong_check(
            control,
            {"install"})
        if not control_strong_check:
            return False
        db_filed['control'] = control
        # deploy校验
        deploy = settings.get('deploy')
        deploy_weak_check = {"single", "complex"}
        deploy_check = self.check_obj.weak_check(
            deploy,
            deploy_weak_check) if deploy else 1
        if not deploy_check:
            return False
        if deploy_check != 1:
            single = deploy.get('single')
            single_strong_check = {"name", "key"}
            single_check = self.check_obj.strong_check(
                single,
                single_strong_check,
                is_weak=True)
            if not single_check:
                return False
            complex_list = deploy.get('complex')
            complex_strong_check = {'name', 'key', 'nodes'}
            complex_check = self.check_obj.strong_check(
                complex_list,
                complex_strong_check,
                is_weak=True)
            if not complex_check:
                return False
        # resources 校验
        deploy = settings.get('resources')
        deploy_check = self.check_obj.strong_check(deploy) if deploy else 1
        if not deploy_check:
            return False
        # install 校验
        install = settings.pop('install')
        single_strong_install = {"name", "key", "default"}
        install_check = self.check_obj.strong_check(
            install,
            single_strong_install,
            is_weak=True) if install else 1
        if not install_check:
            return False
        db_filed['install'] = install
        # monitor 校验
        monitor = settings.get('monitor')
        monitor_check = self.check_obj.strong_check(monitor) if deploy else 1
        if not monitor_check:
            return False
        return True, db_filed

    def upgrade(self, settings):
        return self.service(settings)

    def component(self, settings):
        # 校验label,继承service
        db_filed = {}
        label = settings.pop('labels', None)
        if not label:
            self.db_obj.update_package_status(
                1,
                f"yml校验labels失败，检查yml文件{self.yaml_dir}")
            return False
        db_filed['labels'] = label
        result = self.service(settings)
        if isinstance(result, bool):
            return False
        db_filed.update(result[1])
        return True, db_filed


@shared_task
def publish_bak_end(uuid, exc_len):
    # 增加try，并增加超时机制释放锁
    exc_task = True
    time_count = 0
    try:
        while exc_task and time_count <= 60:
            valid_uuids = UploadPackageHistory.objects.filter(
                operation_uuid=uuid,
                package_parent__isnull=True,
            ).exclude(
                package_status=2).count()
            if valid_uuids != exc_len:
                time_count += 1
                time.sleep(5)
            else:
                if valid_uuids != 0:
                    publish_entry(uuid)
                exc_task = False
    finally:
        re = redis.Redis(host=OMP_REDIS_HOST, port=OMP_REDIS_PORT, db=9,
                         password=OMP_REDIS_PASSWORD)
        re.delete('back_end_verified')


@shared_task
def publish_entry(uuid):
    valid_uuids = UploadPackageHistory.objects.filter(
        is_deleted=False,
        operation_uuid=uuid,
        package_parent__isnull=True,
        package_status=0)
    valid_uuids.update(package_status=5)
    valid_uuids = UploadPackageHistory.objects.filter(
        is_deleted=False,
        operation_uuid=uuid,
        package_parent__isnull=True,
        package_status=5)
    valid_packages = {}
    if valid_uuids:
        for j in valid_uuids:
            valid_packages[j.package_name] = j

    json_data = os.path.join(project_dir, 'data', f'middle_data-{uuid}.json')
    with open(json_data, "r", encoding="utf8") as fp:
        lines = fp.readlines()
    valid_info = []
    for line in lines:
        json_line = json.loads(line)
        valid_obj = valid_packages.get(json_line.get('package_name'))

        if valid_obj:
            json_line['package_name'] = valid_obj
            valid_info.append(json_line)
    valid_packages_obj = []
    valid_dir = None
    for line in valid_info:
        if line.get('kind') == 'product':
            CreateDatabase(line).create_product()
        else:
            CreateDatabase(line).create_component()
        tmp_dir = line.get('tmp_dir')
        if len(tmp_dir) <= 28:
            line['package_name'].package_status = 4
            line['package_name'].save()
            logger.error('{tmp_dir}路径异常')
            return None
        valid_dir = os.path.join(project_dir, 'package_hub',
                                 'verified', tmp_dir.rsplit('/', 1)[1])
        move_tmp = tmp_dir if os.path.isfile(tmp_dir) else tmp_dir.rsplit("-", 1)[0]
        move_out = public_utils.local_cmd(
            f'rm -rf {valid_dir} && mv {move_tmp} {valid_dir}')
        if move_out[2] != 0:
            line['package_name'].package_status = 4
            line['package_name'].save()
            logger.error('移动或删除失败')
            return None
        valid_packages_obj.append(line['package_name'].id)
    clear_dir = os.path.dirname(tmp_dir) if os.path.isfile(valid_dir) else \
        os.path.dirname(os.path.dirname(tmp_dir))
    UploadPackageHistory.objects.filter(id__in=valid_packages_obj).update(
        package_status=3)
    online = UploadPackageHistory.objects.filter(
        is_deleted=False,
        package_status__in=[2,
                            5]).count()
    if len(clear_dir) <= 28:
        logger.error('{clear_dir}路径异常')
        return None
    if online == 0:
        clear_out = public_utils.local_cmd(
            f'rm -rf {clear_dir} && mkdir {clear_dir}')
        if clear_out[2] != 0:
            logger.error('清理环境失败')
