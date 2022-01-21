"""
主机相关异步任务
"""

import os
import yaml
import time
import json
import redis
import logging

from celery import shared_task
from celery.utils.log import get_task_logger
from utils.plugin import public_utils
from utils.parse_config import (
    OMP_REDIS_PORT, OMP_REDIS_PASSWORD, OMP_REDIS_HOST
)

from db_models.models import (
    UploadPackageHistory, ApplicationHub, ProductHub,
    MainInstallHistory, DetailInstallHistory
)
from app_store.upload_task import CreateDatabase
from app_store.install_exec import InstallServiceExecutor
# from app_store.install_executor import InstallServiceExecutor
from promemonitor.prometheus_utils import PrometheusUtils

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
     is_weak 强校验一定包含弱校验。值为True，简化代码量。
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
            # 以field为基准,settings多出的也不会显示,只要满足field即可
            status = field - set(settings.keys())
            if status:
                self.db_obj.update_package_status(
                    1,
                    f"yml{str(status)}字段和预期不符，检查yml文件{self.yaml_dir}")
                return False
            return True
        elif isinstance(settings, list):
            for i in settings:
                status = field - set(i.keys())
                if status:
                    self.db_obj.update_package_status(
                        1,
                        f"yml{str(status)}字段和预期不符，检查yml文件{self.yaml_dir}")
                    return False
            return True
        else:
            return False


@shared_task
def front_end_verified(uuid, operation_user, package_name, random_str, ver_dir, upload_obj):
    """
     前端发布界面校验逻辑及后端校验逻辑公共类
     params
     uuid 操作唯一id
     operation_user 执行用户
     package_name 上传的安装包
     md5 md5值，暂时不用，现为后端自己生成
     random_str 随机字符串，用于拼接临时校验目录
     ver_dir 区分前后端校验临时存储路径
     upload_obj 上传记录表的id
    """
    upload_obj = UploadPackageHistory.objects.get(id=upload_obj)
    package_path = os.path.join(package_hub, ver_dir)
    file_name = os.path.join(package_path, package_name)
    # md5校验生成
    md5_out = public_utils.local_cmd(f'md5sum {file_name}')
    if md5_out[2] != 0:
        upload_obj.package_status = 1
        upload_obj.error_msg = "md5sum命令执行失败"
        upload_obj.save()
        return None
    md5sum = md5_out[0].split()[0]
    md5 = md5sum
    upload_obj.package_md5 = md5
    upload_obj.save()
    # 实例化状态更新公共类对象
    public_action = PublicAction(md5)
    touch_name = file_name[:-7] if \
        file_name[-7:] == ".tar.gz" else file_name[:-3]
    tmp_dir = os.path.join(package_path, touch_name + random_str)
    # 创建临时校验路径
    os.mkdir(tmp_dir)
    tar_out = public_utils.local_cmd(f'tar -xvf {file_name} -C {tmp_dir}')
    if tar_out[2] != 0:
        return public_action.update_package_status(
            1,
            f"安装包{package_name}解压失败或者压缩包格式不合规")
    app_name = package_name.split('-', 1)[0]
    tmp_dir = os.path.join(tmp_dir, app_name)
    # 查询临时路径下符合规范的yaml
    check_file = os.path.join(tmp_dir, f'{app_name}.yaml')
    if not os.path.exists(check_file):
        return public_action.update_package_status(
            1,
            f"安装包{package_name}:{app_name}.yaml文件不存在")
    # yaml内容进行标准校验
    explain_yml = ExplainYml(public_action, check_file).explain_yml()
    # 这个校验可能用不到
    if isinstance(explain_yml, bool):
        return None
    kind = explain_yml[1].get("kind")
    versions = explain_yml[1].get("version")
    name = explain_yml[1].get("name")
    pro_name = f"{name}-{versions}"
    # 校验图片
    image = None
    if kind == 'product' or kind == 'component':
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
    # yaml分为产品，组建，和服务逻辑。产品必须包含服务。因此需对产品类型做子级服务校验
    if kind == 'product':
        service = explain_yml[1].get("service")
        count = ProductHub.objects.filter(pro_version=versions,
                                          pro_name=name).count()
        if count != 0:
            return public_action.update_package_status(
                1,
                f"安装包{package_name}已存在:请确保name联合version唯一")
        explain_service_list = []
        yml_dirs = os.path.join(tmp_dir, app_name)
        # 查找产品包路径下符合规则的tar与产品字段内service字段进行比对，
        # 成功的将会入库，未匹配到的则跳过逻辑。
        service_name = [os.path.join(tmp_dir, i) for i in os.listdir(tmp_dir)]
        service_packages_value = [
            p for p in service_name if
            os.path.isfile(p) and 'tar' in p]
        service_packages_key = [service_package.rsplit("/", 1)[1].split("-")[0]
                                for service_package in
                                service_packages_value]
        service_package = dict(
            zip(service_packages_key, service_packages_value))
        # 对匹配到的yaml进行yaml校验，此时逻辑产品下服务包没有合法，
        # 但产品内service字段存在的service必须有对应的yaml文件。
        name_version = []
        for i in service:
            service_dir = os.path.join(yml_dirs, f"{i.get('name')}.yaml")
            if not os.path.exists(service_dir):
                return public_action.update_package_status(
                    1,
                    f"安装包{package_name}:{i.get('name')}.yaml文件不存在")
            # 子集服务进行yaml标准校验
            explain_service_yml = ExplainYml(public_action,
                                             service_dir).explain_yml()
            if isinstance(explain_service_yml, bool):
                return None
            ser_name = i.get('name')
            name_version.append(
                {'name': ser_name, 'version': explain_service_yml[1].get('version')})
            service_pk = service_package.get(ser_name)
            if not service_pk:
                continue
            # 校验服务是否唯一,无安装包跳过逻辑后
            count = ApplicationHub.objects.filter(app_version=ser_name,
                                                  app_name=i.get("version")).count()
            if count != 0:
                return public_action.update_package_status(
                    1,
                    f"安装包{package_name}服务{ser_name}已存在:请确保name联合version唯一")
            # 校验md5
            service_pk_name = service_pk.rsplit("/", 1)[1]
            md5_ser = public_utils.local_cmd(f'md5sum {service_pk}')
            if md5_ser[2] != 0:
                return public_action.update_package_status(
                    1, "md5sum命令执行失败")
            md5_service = md5_ser[0].split()[0]
            # 对合法服务的记录进行创建操作，
            # 信息会追加入"product_service"字段并归入所属产品yaml，组件则不会有此值。
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
        explain_yml[1]['service'] = name_version
        tmp_dir = [tmp_dir, versions]
    elif kind == 'service':
        dependence_product = explain_yml[1].get(
            "extend_fields", {}).get("product")
        if not dependence_product:
            return public_action.update_package_status(
                1,
                f"安装包{package_name}不能无依赖产品上传")
        product_version = dependence_product.get("version", "")
        if not product_version:
            product_obj = ProductHub.objects.filter(pro_name=dependence_product.get("name")
                                                    ).last()

        else:
            product_obj = ProductHub.objects.filter(pro_name=dependence_product.get("name"),
                                                    pro_version=product_version).last()
        if not product_obj:
            return public_action.update_package_status(
                1,
                f"安装包{package_name}依赖的产品包不存在")
        # 将版本追加至最新版本
        dependence_product["version"] = product_obj.pro_version
        app_obj = ApplicationHub.objects.filter(product=product_obj)
        for obj in app_obj:
            if obj.app_name == explain_yml[1]['name'] and \
                    obj.app_version == explain_yml[1]['version']:
                return public_action.update_package_status(
                    1,
                    f"安装包{package_name}依赖的产品包存在同服务同版本的服务包")
        upload_obj.package_status = 0
        upload_obj.package_path = os.path.join(
            package_dir.get("verified"),
            f"{product_obj.pro_name}-{product_obj.pro_version}"
        )
        upload_obj.save()
        tmp_dir = [file_name]
    else:
        count = ApplicationHub.objects.filter(app_version=versions,
                                              app_name=name).count()
        if count != 0:
            return public_action.update_package_status(
                1,
                f"安装包{package_name}已存在:请确保name联合version唯一")
        tmp_dir = [file_name]
    explain_yml[1]['image'] = image
    explain_yml[1]['package_name'] = package_name
    explain_yml[1]['tmp_dir'] = tmp_dir
    # 开启写入中间结果，包含发布入库所有的信息
    middle_data = os.path.join(project_dir, 'data', f'middle_data-{uuid}.json')
    with open(middle_data, mode='a', encoding='utf-8') as f:
        f.write(json.dumps(explain_yml[1], ensure_ascii=False) + '\n')
    # 提示存在逻辑注释，改存在校验失败逻辑
    # name = explain_yml[1]['name']
    # version = explain_yml[1]['version']
    # if explain_yml[1]['kind'] == 'product':
    #    count = ProductHub.objects.filter(pro_version=version,
    #                                      pro_name=name).count()
    # else:
    #    count = ApplicationHub.objects.filter(app_version=version,
    #                                          app_name=name).count()
    # if count:
    #    count = "已存在,将覆盖"
    # else:
    #    count = None
    # 无校验失败则会更新数据库状态为校验成功
    return public_action.update_package_status(0)


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
        self.yaml_exc = yaml_dir
        self.yaml_dir = yaml_dir.rsplit("/", 1)[1]
        self.check_obj = FiledCheck(self.yaml_dir, self.db_obj)

    def check_book_tools(self, key, value):
        """
        校验值bool类型，前置条件，需强校验通过
        后期根据需求进行扩展
        params:
        key输出错误日志的key
        value需要判断的值
        """
        if value.lower() == "false" or value.lower() == "true":
            return False
        self.db_obj.update_package_status(
            1,
            f"yml校验{key}非bool值，检查yml文件{self.yaml_dir}")
        return True

    def explain_yml(self):
        """
        各种kind类型公共字段
        """
        kinds = ['product', 'service', 'upgrade', 'component']
        try:
            with open(self.yaml_exc, "r", encoding="utf8") as fp:
                settings = yaml.load(fp, Loader=yaml.BaseLoader)
            if not settings:
                self.db_obj.update_package_status(
                    1,
                    f"yml文件为空，检查yml文件{self.yaml_dir}")
        except Exception as e:
            self.db_obj.update_package_status(
                1,
                f"yml包格式错误，检查yml文件{self.yaml_dir}:{e}")
            return False
        # 将公共字段抽出校验，生成中间结果
        kind = settings.pop('kind', None)
        name = settings.pop('name', None)
        version = settings.pop('version', None)
        dependencies = settings.pop('dependencies', "-1")
        if dependencies == "-1":
            self.db_obj.update_package_status(
                1,
                f"yml校验dependencies校验失败，检查yml文件{self.yaml_dir}")
            return False
        if dependencies:
            for i in dependencies:
                if not i.get("name") or not i.get("version"):
                    self.db_obj.update_package_status(
                        1,
                        f"yml校验dependencies校验失败，检查yml文件{self.yaml_dir}")
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
        # 对剩余字段进行自定义校验
        yml = getattr(self, kind)(settings)
        if isinstance(yml, bool):
            return False
        db_filed = {
            "kind": kind,
            "name": name,
            "version": version,
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
            if not i.get("name"):
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
        description = settings.pop('description', "-1")
        if description == "-1":
            self.db_obj.update_package_status(
                1,
                f"yml校验description校验失败，检查yml文件{self.yaml_dir}")
            return False
        if description is not None and len(description) > 200:
            self.db_obj.update_package_status(
                1,
                f"yml校验description长度过长，检查yml文件{self.yaml_dir}")
            return False
        db_filed['description'] = description
        return True, db_filed

    def service_component(self, settings):
        """校验kind为service"""
        # service骨架弱校验
        db_filed = {}
        # post_action affinity base_env auto_launch不再校验
        # level 默认0 monitor不做校验
        first_check = {"ports", "install",
                       "control"}
        if not self.check_obj.weak_check(settings, first_check):
            return False
        # auto_launch 校验 不填写默认给true
        settings["auto_launch"] = settings.get("auto_launch", "true")
        # base_env 校验 不填写True true 全部按照false处理
        db_filed['base_env'] = settings.pop('base_env', "")
        # ports 校验
        ports = settings.pop('ports')
        ports_strong_check = {"name", "protocol", "default", "key"}
        port = self.check_obj.strong_check(
            ports, ports_strong_check,
            is_weak=True,
            ignore={"key"}) if ports else 1
        if not port:
            return False
        db_filed['ports'] = ports
        #  control校验
        control = settings.pop('control')
        control_weak_check = {"start", "stop", "restart", "install",
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
        monitor = settings.pop('monitor', None)
        monitor_weak_check = {"process_name", "metric_port", "type"}
        monitor_check = self.check_obj.weak_check(
            monitor, monitor_weak_check) if monitor else 1
        if not monitor_check:
            return False
        db_filed['monitor'] = monitor
        return True, db_filed

    def service(self, settings):
        """
        创建服务校验类，原服务类变为基类
        """
        level = settings.pop('level', -1)
        if level == -1:
            level = 0
        result = self.service_component(settings)
        if isinstance(result, bool):
            return False
        settings['level'] = level
        return True, result[1]

    def upgrade(self, settings):
        return self.service_component(settings)

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
        description = settings.pop('description', "-1")
        if description == "-1":
            self.db_obj.update_package_status(
                1,
                f"yml校验description校验失败，检查yml文件{self.yaml_dir}")
            return False
        if description is not None and len(description) > 200:
            self.db_obj.update_package_status(
                1,
                f"yml校验description长度过长，检查yml文件{self.yaml_dir}")
            return False
        db_filed['description'] = description
        result = self.service_component(settings)
        if isinstance(result, bool):
            return False
        db_filed.update(result[1])
        return True, db_filed


def exec_clear(clear_dir):
    # 清理逻辑，当发布完成时对临时路径进行清空处理，
    # 此逻辑会考虑状态为正在校验和正在发布状态的情况
    # 存在清理跳过，后期会考虑只选择一段时间内状态非中间态不做清理逻辑。，
    online = UploadPackageHistory.objects.filter(
        is_deleted=False,
        package_status__in=[2,
                            5]).count()
    if len(clear_dir) <= 28:
        logger.error(f'{clear_dir}路径异常')
        return None
    if online == 0 or 'back_end_verified' in clear_dir:
        clear_out = public_utils.local_cmd(
            f'rm -rf {clear_dir} && mkdir {clear_dir}')
        if clear_out[2] != 0:
            logger.error('清理环境失败')


@shared_task
def publish_bak_end(uuid, exc_len):
    """
    后台扫描同步等待发布函数
    params:
    uuid 当前唯一操作id
    exc_len 合法安装包个数
    """

    # 增加try，并增加超时机制释放锁
    exc_task = True
    time_count = 0
    try:
        while exc_task and time_count <= 600:
            # 当所有安装包的状态均不为正在校验，
            # 并和扫描出得包的个数相同且不为0，进行发布逻辑。
            valid_uuids = UploadPackageHistory.objects.filter(
                operation_uuid=uuid,
                package_parent__isnull=True,
            ).exclude(
                package_status=2)
            valid_success = valid_uuids.exclude(
                package_status=1).count()
            if valid_uuids.count() != exc_len:
                time_count += 1
                time.sleep(5)
            else:
                if valid_uuids.count() != 0 and valid_success != 0:
                    publish_entry(uuid)
                else:
                    exec_clear(os.path.join(
                        package_hub, package_dir.get('back_end_verified')))
                exc_task = False
    finally:
        re = redis.Redis(host=OMP_REDIS_HOST, port=OMP_REDIS_PORT, db=9,
                         password=OMP_REDIS_PASSWORD)
        re.delete('back_end_verified')


@shared_task
def publish_entry(uuid):
    """
    前台发扫描台发布函数公共类
    params:
    uuid 当前唯一操作id
    注：此异步任务的调用的前提必须是校验已完成状态
    """
    # 修改校验无误的安装包的状态为正在发布状态。
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
    # 从库获取校验合法的安装包名称
    if valid_uuids:
        for j in valid_uuids:
            valid_packages[j.package_name] = j

    json_data = os.path.join(project_dir, 'data', f'middle_data-{uuid}.json')
    with open(json_data, "r", encoding="utf8") as fp:
        lines = fp.readlines()
    valid_info = []
    # 将匹配到的安装包和中间结果的安装包比对，将安装包名替换成历史记录表的model对象
    for line in lines:
        json_line = json.loads(line)
        valid_obj = valid_packages.get(json_line.get('package_name'))
        if json_line.get("extend_fields").get("product"):
            valid_info.append(json_line)
        # 升级包单独逻辑
        elif valid_obj:
            json_line['package_name'] = valid_obj
            valid_info.append(json_line)
    valid_packages_obj = []
    valid_dir = None
    # 中间结果转入创表函数
    product_obj = None
    tmp_dir = []
    for line in valid_info:
        if line.get('kind') == 'product':
            CreateDatabase(line).create_product()
        elif line.get('kind') == 'service':
            product = line.get("extend_fields").get("product")
            product_obj = ProductHub.objects.filter(pro_name=product.get("name"),
                                                    pro_version=product.get(
                                                        "version")
                                                    ).last()
            upload_history_obj = None
            for j in valid_uuids:
                if j.package_name == line.get('package_name'):
                    upload_history_obj = j
            # 更新服务的upload历史状态和已有服务关联
            upload_history_obj.package_parent = product_obj.pro_package
            upload_history_obj.save()
            CreateDatabase(line).create_service([line], product_obj)
            line['package_name'] = upload_history_obj
        else:
            CreateDatabase(line).create_component()
        tmp_dir = line.get('tmp_dir')
        if len(tmp_dir[0]) <= 28:
            line['package_name'].package_status = 4
            line['package_name'].save()
            logger.error(f'{tmp_dir[0]}路径异常')
            return None
        # 匹配到的安装包移动至对应路径
        # 产品包路径 package_hub/xxx/random/product_name/xxx
        # 组件路径   package_hub/xxx/app.tar.gz
        # 产品目标路径   verified/product_name-version/xxx
        # 组件目标路径   verified/app.tar.gz

        valid_name = tmp_dir[0].rsplit('/', 1)
        valid_pk = f"{valid_name[1]}-{tmp_dir[1]}" if len(
            tmp_dir) == 2 else valid_name[1]
        if product_obj:
            valid_pk = f"{product_obj.pro_name}-{product_obj.pro_version}/{valid_name[1]}"

        valid_dir = os.path.join(project_dir, 'package_hub',
                                 'verified', valid_pk)
        move_tmp = "/".join(valid_name)
        move_out = public_utils.local_cmd(
            f'rm -rf {valid_dir} && mv {move_tmp} {valid_dir}')
        if move_out[2] != 0:
            line['package_name'].package_status = 4
            line['package_name'].save()
            logger.error('移动或删除失败')
            return None
        valid_packages_obj.append(line['package_name'].id)
    clear_dir = os.path.dirname(tmp_dir[0]) if os.path.isfile(valid_dir) else \
        os.path.dirname(os.path.dirname(tmp_dir[0]))
    UploadPackageHistory.objects.filter(id__in=valid_packages_obj).update(
        package_status=3)
    exec_clear(clear_dir)


def check_monitor_data(detail_obj):
    """
    根据部署详情信息，确认该服务的要监控的方式，并返回监控处理结果
    {
        "type": "JavaSpringBoot",
        "metric_port": "{service_port}",
        "process_name": ""
    }
    :param detail_obj: 部署详情对象
    :type detail_obj: DetailInstallHistory
    :return: (bool, _ret_dic)
    """

    def get_port(keyword):
        """
        根据关键字获取端口值
        :param keyword:
        :return:
        """
        service_port_ls = json.loads(detail_obj.service.service_port)
        for item in service_port_ls:
            if item.get("key") == keyword:
                return item.get("default")
        return None

    _ret_dic = {
        "listen_port": get_port("service_port"),
        "metric_port": None,
        "only_process": False,
        "process_key_word": None,
        "type": None
    }
    app_monitor = detail_obj.service.service.app_monitor
    if not app_monitor:
        return False, _ret_dic
    _ret_dic["type"] = app_monitor.get("type")
    _ret_dic["process_key_word"] = app_monitor.get("process_name")

    if isinstance(app_monitor.get("metric_port"), str):
        _metric_port_key = app_monitor.get(
            "metric_port", "").replace("{", "").replace("}", "")
    elif isinstance(app_monitor.get("metric_port"), dict):
        _metric_port_key = list(app_monitor.get("metric_port", {}).keys())[0]
    else:
        _metric_port_key = None
    if detail_obj.service.service_port is not None:
        _ret_dic["listen_port"] = get_port("service_port")
        _ret_dic["metric_port"] = get_port(_metric_port_key)
    if _ret_dic["metric_port"]:
        return True, _ret_dic
    if _ret_dic["process_key_word"]:
        _ret_dic["only_process"] = True
        return True, _ret_dic
    return False, _ret_dic


def add_prometheus(main_history_id, queryset=None):
    """ 添加服务到 Prometheus """
    logger.info("Add Prometheus Begin")
    prometheus = PrometheusUtils()
    # TODO 不同类型服务添加监控方式不同，后续版本优化
    # 仅更新已经安装完成的最新服务
    # 给monitor_agent刷新使用，提供detail_obj list。
    queryset = queryset if queryset else DetailInstallHistory.objects.filter(
        main_install_history_id=main_history_id,
        install_step_status=DetailInstallHistory.INSTALL_STATUS_SUCCESS
    )
    for detail_obj in queryset:
        try:
            _flag, _monitor_dic = check_monitor_data(detail_obj=detail_obj)
            logger.info(
                f"Add Prometheus get monitor_dic for "
                f"{detail_obj}: {_monitor_dic}")
        except Exception as e:
            logger.info(
                f"Add Prometheus get monitor_dic Failed: "
                f"{detail_obj}; {str(e)}")
            continue
        if not _flag:
            continue
        # TODO 已是否具有端口作为是否需要添加监控的依据，后续版本优化
        instance_name = detail_obj.service.service_instance_name
        service_port = _monitor_dic.get("listen_port")
        # 获取数据目录、日志目录
        app_install_args = detail_obj.install_detail_args.get(
            "install_args", [])
        data_dir = log_dir = ""
        username = password = ""
        for info in app_install_args:
            if info.get("key", "") == "data_dir":
                data_dir = info.get("default", "")
            if info.get("key", "") == "log_dir":
                log_dir = info.get("default", "")
            if info.get("key", "") == "username":
                username = info.get("default", "")
            if info.get("key", "") == "password":
                password = info.get("default", "")
        # TODO 后期优化
        ser_name = detail_obj.service.service.app_name
        if ser_name == "hadoop":
            ser_name = instance_name.split("_", 1)[0]
        # 添加服务到 prometheus
        is_success, message = prometheus.add_service({
            "service_name": ser_name,
            "instance_name": instance_name,
            "data_path": data_dir,
            "log_path": log_dir,
            "env": "default",
            "ip": detail_obj.service.ip,
            "listen_port": service_port,
            "metric_port": _monitor_dic.get("metric_port"),
            "only_process": _monitor_dic.get("only_process"),
            "process_key_word": _monitor_dic.get("process_key_word"),
            "username": username,
            "password": password,
        })
        if not is_success:
            logger.error(
                f"Add Prometheus Failed {instance_name}, error: {message}")
            continue
        logger.info(f"Add Prometheus Success {instance_name}")
    logger.info("Add Prometheus End")


def make_inspection(username):
    """
    触发巡检任务
    :param username:
    :return:
    """
    logger.info("安装成功后触发巡检任务")
    from rest_framework.test import APIClient
    from rest_framework.reverse import reverse
    from db_models.models import UserProfile
    from db_models.models import Env
    data = {
        "inspection_name": "mock", "inspection_type": "deep",
        "inspection_status": "1", "execute_type": "man",
        "inspection_operator": username, "env": Env.objects.last().id
    }
    user = UserProfile.objects.filter(username=username).last()
    client = APIClient()
    client.force_authenticate(user)
    res = client.post(
        path=reverse("history-list"),
        data=json.dumps(data),
        content_type="application/json"
    ).json()
    logger.info(f"安装成功后触发巡检任务的结果为: {res}")
    return res


@shared_task
def install_service(main_history_id, username="admin"):
    """
    安装服务
    :param main_history_id: MainInstallHistory 主表 id
    :param username: 执行用户
    :return:
    """
    try:
        # 为防止批量安装时数据库写入数据过多，这里采用循环的方式判断main_history_id
        try_times = 0
        while try_times < 3:
            if MainInstallHistory.objects.filter(id=main_history_id).exists():
                break
            time.sleep(5)
        else:
            logger.error(
                "Install Service Task Failed: can not find {main_history_id}")
        executor = InstallServiceExecutor(main_history_id, username)
        executor.main()
        logger.error(f"Install Service Task Success [{main_history_id}]")
    except Exception as err:
        import traceback
        logger.error(f"Install Service Task Failed [{main_history_id}], "
                     f"err: {err}")
        logger.error(traceback.format_exc())
        # 更新主表记录为失败
        MainInstallHistory.objects.filter(
            id=main_history_id).update(
            install_status=MainInstallHistory.INSTALL_STATUS_FAILED)

    # 安装成功，则注册服务至监控
    add_prometheus(main_history_id)

    # 安装成功，触发巡检任务
    if MainInstallHistory.objects.filter(
            id=main_history_id,
            install_status=MainInstallHistory.INSTALL_STATUS_SUCCESS
    ).exists():
        make_inspection(username=username)
