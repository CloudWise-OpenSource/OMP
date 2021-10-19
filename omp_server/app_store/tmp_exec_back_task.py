import os
from app_store.lockredis import *
from utils.parse_config import OMP_REDIS_PORT, OMP_REDIS_PASSWORD, OMP_REDIS_HOST
import time
from app_store.tasks import front_end_verified, publish_bak_end

current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(os.path.dirname(current_dir))
package_hub = os.path.join(project_dir, "package_hub")

package_dir = {"back_end_verified": "back_end_verified", "front_end_verified": "front_end_verified",
               "verified": "verified"}


def back_end_verified_init(operation_user):
    uuid = str(round(time.time() * 1000))

    @deco(RedisLock("back_end_verified", uuid, host=OMP_REDIS_HOST, port=OMP_REDIS_PORT, password=OMP_REDIS_PASSWORD))
    def back_end_verified(lock=None):
        """后端校验"""
        if lock:
            return str(lock, encoding="utf-8")
        back_verified = os.path.join(package_hub, package_dir.get('back_end_verified'))
        service_name = os.listdir(back_verified)
        exec_name = [p for p in service_name if os.path.isfile(os.path.join(back_verified, p)) and 'tar' in p]
        for j in exec_name:
            front_end_verified.delay(uuid, operation_user, j)
        publish_bak_end.delay(uuid, len(exec_name))
        return uuid

    return back_end_verified()
