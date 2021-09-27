# -*- coding: utf-8 -*-
# Project: exception_handler
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-10 16:32
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
整个项目内的异常处理方法
"""
from django.db import DatabaseError
from rest_framework.views import exception_handler
from rest_framework.response import Response

from utils.exceptions import GeneralError


def res_is_none(exc, context):
    """
    当响应是None时
    :param exc:
    :param context:
    :return:
    """
    response = Response()
    response.data = dict()
    response.data["code"] = 1
    if isinstance(exc, DatabaseError):
        response.data["message"] = "数据库错误"
    elif isinstance(exc, NameError):
        response.data["message"] = "变量未定义被引用"
    elif isinstance(exc, GeneralError) \
            or issubclass(exc, GeneralError):
        response.data["message"] = str(exc)
    else:
        response.data["message"] = "后端程序错误"
    return response


def res_is_not_none(exc, context, response):
    """
    当响应有值时
    :param exc:
    :param context:
    :param response:
    :return:
    """
    response.data["code"] = 1
    if response.status_code == 404:
        try:
            response.data["message"] = response.data.pop("detail")
        except KeyError:
            response.data["message"] = "未找到"
    elif response.status_code == 400:
        error_message = ""
        for key, value in response.data.items():
            if not isinstance(value, list):
                continue
            error_message += f"{key}: "
            for el in value:
                error_message += f"{str(el)};"
            error_message += " "
        response.data["message"] = error_message.strip()
        response.data["data"] = None
    elif response.status_code == 401:
        response.data["message"] = "未认证"
    elif response.status_code >= 500:
        response.data["message"] = "服务器错误"
    elif response.status_code == 403:
        response.data["message"] = "无访问权限"
    elif response.status_code == 405:
        response.data["message"] = "暂不支持此请求"
    else:
        response.data["data"] = None
        response.data["message"] = "未知错误"
    response.status_code = 200
    return response


def common_exception_handler(exc, context):
    """
    异常处理函数
    :param exc:
    :param context:
    :return:
    """
    response = exception_handler(exc, context)
    # 在此处补充自定义的异常处理
    if response is None:
        return res_is_none(exc, context)
    return res_is_not_none(exc, context, response)
