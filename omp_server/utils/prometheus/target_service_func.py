# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/31 7:28 下午
# Description:
import json
from utils.plugin.salt_client import SaltClient


def salt_json(instance, func):
    """
    salt执行脚本，获取返回值
    """
    ret = {}
    try:
        _obj = SaltClient()
        _obj.salt_module_update()
        ret = _obj.fun(instance, func)
        if ret and ret[0]:
            ret = json.loads(ret[1])
        else:
            ret = {}
    except:
        pass

    return ret


if __name__ == '__main__':
    salt_json('10.0.7.194', 'tomcat_check.main')
