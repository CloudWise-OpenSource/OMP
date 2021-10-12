# -*- coding: utf-8 -*-
# Project: grafana_views
# Author: jon.liu@yunzhihui.com
# Create time: 2021-10-12 10:27
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
跳转grafana页面使用
"""

import re
import logging
import requests
import traceback
from urllib.parse import urlparse

from django.http import QueryDict
# from django.http import HttpRequest
from django.http import HttpResponse

from db_models.models import MonitorUrl

logger = logging.getLogger("server")


def grafana_proxy(request, url, requests_args=None):
    """
    跳转grafana使用的函数
    :type request HttpRequest
    :param request: http请求对象
    :type url str
    :param url: url
    :type requests_args dict
    :param requests_args: 请求参数
    :return:
    """
    requests_args = (requests_args or {}).copy()
    headers = {}
    for key, value in request.META.items():
        if key.startswith('HTTP_') and key != 'HTTP_HOST':
            headers[key[5:].replace('_', '-')] = value
        elif key in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            headers[key.replace('_', '-')] = value
    params = request.GET.copy()
    if 'headers' not in requests_args:
        requests_args['headers'] = {}
    if 'data' not in requests_args:
        requests_args['data'] = request.body
    if 'params' not in requests_args:
        requests_args['params'] = QueryDict('', mutable=True)
    headers.update(requests_args['headers'])
    params.update(requests_args['params'])
    for key in list(headers.keys()):
        if key.lower() == 'content-length':
            del headers[key]
    headers["X-CW-USER"] = "omp"
    requests_args['headers'] = headers
    requests_args['params'] = params
    response = requests.request(
        request.method, url, **requests_args)
    proxy_response = HttpResponse(
        response.content,
        status=response.status_code)

    excluded_headers = {
        'connection', 'keep-alive',
        'proxy-authenticate', 'proxy-authorization', 'te', 'trailers',
        'transfer-encoding', 'upgrade', 'content-encoding', 'content-length'
    }

    for key, value in response.headers.items():
        if key.lower() in excluded_headers:
            continue
        elif key.lower() == 'location':
            absolute_pattern = re.compile(r'^[a-zA-Z]+://.*$')
            if absolute_pattern.match(value):
                proxy_response[key] = value
            parsed_url = urlparse(response.url)
            if value.startswith('//'):
                proxy_response[key] = parsed_url.scheme + ':' + value
            elif value.startswith('/'):
                proxy_response[key] = parsed_url.scheme + \
                    '://' + parsed_url.netloc + value
            else:
                proxy_response[key] = \
                    parsed_url.scheme + '://' + \
                    parsed_url.netloc + \
                    parsed_url.path.rsplit('/', 1)[0] + '/' + value
        else:
            proxy_response[key] = value
    return proxy_response


def grafana_proxy_view(request, path):
    """
    获取grafana页面
    :type request HttpRequest
    :param request: 请求对象
    :type path str
    :param path: 请求路径
    :return:
    """
    grafana = "default"
    try:
        monitor_ip = MonitorUrl.objects.filter(name="grafana")
        grafana_ins = monitor_ip[0].monitor_url if len(
            monitor_ip) else "127.0.0.1:19014"
        grafana = f"http://{grafana_ins}"
        remote_url = f'{grafana}/' + path
        return grafana_proxy(request, remote_url)
    except Exception as e:
        logger.error(
            f"跳转grafana失败: {str(e)};\n详情为: {traceback.format_exc()}")
        return HttpResponse(
            content=f"请确认grafana配置[{grafana}]可用!", status=200)
