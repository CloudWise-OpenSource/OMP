import os
from utils.parse_config import (
    OMP_REDIS_PORT, OMP_REDIS_PASSWORD, OMP_REDIS_HOST
)
import time
from app_store.tasks import front_end_verified, publish_bak_end
import redis

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
        self.rdcon = self.argsinit(host, port, db, kwargs)

    def argsinit(self, host, port, db, kwwargs):
        if kwwargs:
            if kwwargs.get('password'):
                return redis.Redis(host, port, db, kwwargs['password'])
        return redis.Redis(host, port, db)

    def get_lock(self):
        if self.rdcon.exists('back_end_verified') == 0:
            return False, self.rdcon
        return True, self.rdcon


def back_end_verified_init(operation_user):
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
        p for p in service_name if
        os.path.isfile(os.path.join(back_verified, p)) and
        (p.endswith('.tar') or p.endswith('.tar.gz'))]
    redis_key.lpush("back_end_verified", uuid, ",".join(exec_name))
    redis_key.expire("back_end_verified", 600)
    for j in exec_name:
        front_end_verified.delay(uuid, operation_user, j)
    publish_bak_end.delay(uuid, len(exec_name))
    return uuid, exec_name
