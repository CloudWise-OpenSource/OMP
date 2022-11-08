import os
from utils.parse_config import (
    OMP_REDIS_PORT, OMP_REDIS_PASSWORD, OMP_REDIS_HOST
)
import time
from app_store.tasks import front_end_verified, publish_bak_end
import redis
from db_models.models import UploadPackageHistory
import random

current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(os.path.dirname(current_dir))
package_hub = os.path.join(project_dir, "package_hub")

package_dir = {
    "back_end_verified": "back_end_verified",
    "front_end_verified": "front_end_verified",
    "verified": "verified"
}


class RedisLock(object):
    def __init__(self, host='127.0.0.1', port='6379', db=9, **kwargs):
        self.rdcon = self.args_init(host, port, db, kwargs)

    @staticmethod
    def args_init(host, port, db, kwargs):
        if kwargs and kwargs.get('password'):
            return redis.Redis(host, port, db, kwargs['password'])
        return redis.Redis(host, port, db)

    def get_lock(self, key='back_end_verified'):
        if self.rdcon.exists(key) == 0:
            return False, self.rdcon
        return True, self.rdcon


def back_end_verified_init(operation_user):
    """
    后台扫描接口
    :param operation_user: 操作用户
    :return:
    """
    # uuid 自己生成，上redis锁，如果存在则返回当前锁及包名
    uuid = str(round(time.time() * 1000))
    redis_obj = RedisLock(
        host=OMP_REDIS_HOST, port=OMP_REDIS_PORT,
        password=OMP_REDIS_PASSWORD)
    lock, redis_key = redis_obj.get_lock()
    if lock:
        return redis_key.lindex("back_end_verified", 1).decode("utf-8"), redis_key. \
            lindex("back_end_verified", 0).decode("utf-8").split(",")
    back_verified = os.path.join(
        package_hub, package_dir.get('back_end_verified'))
    service_name = os.listdir(back_verified)
    exec_name = [
        p for p in service_name
        if os.path.isfile(os.path.join(back_verified, p)) and (p.endswith('.tar') or p.endswith('.tar.gz'))
    ]
    redis_key.lpush("back_end_verified", uuid, ",".join(exec_name))
    # 设置过期时间，同时创建异步校验任务及发布任务
    redis_key.expire("back_end_verified", 3600)
    for j in exec_name:
        upload_obj = UploadPackageHistory(
            operation_uuid=uuid,
            operation_user=operation_user,
            package_name=j,
            package_md5='1',
            package_path="verified")
        upload_obj.save()
        front_end_verified_init(uuid, operation_user, j, upload_obj.id)
    publish_bak_end.delay(uuid, len(exec_name))
    return uuid, exec_name


def front_end_verified_init(uuid, operation_user, package_name, obj_id, md5=None):
    # 前端发布校验接口
    random_str = ''.join(
        random.sample('abcdefghijklmnopqrstuvwxyz1234567890', 10))
    if md5:
        ver_dir = package_dir.get("front_end_verified")
    else:
        ver_dir = package_dir.get("back_end_verified")
    front_end_verified.delay(uuid, operation_user, package_name,
                             random_str, ver_dir, obj_id)
