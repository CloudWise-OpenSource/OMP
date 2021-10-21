# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: len chen
# CreateDate: 2021/10/14 4:01 下午
# Description:
import json
import requests
import traceback


class Prometheus:
    # prometheus 的 ip:port
    address = None

    def query(self, expr):
        url = 'http://' + self.address + '/api/v1/query?query=' + expr
        try:
            rsp = json.loads(requests.get(url=url, timeout=0.5
                                          ).content.decode('utf8', 'ignore'))
            if rsp.get('status') == 'success':
                return True, rsp.get('data'), 'success'
            else:
                return False, {}, 'fail'
        except Exception as e:
            return False, {}, traceback.format_exc(e)
