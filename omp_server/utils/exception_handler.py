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
from rest_framework.views import exception_handler
from rest_framework.response import Response

from utils.exceptions import (
    GeneralError,
    FORMAT_ERRORS, ERROR_MESSAGE, CODE_MESSAGE
)


class ExceptionResponse:
    def __init__(self, exc, context):
        self.exc = exc
        self.context = context

    def err_response(self):
        response = exception_handler(self.exc, self.context)

        response_status_code = 200
        if response:
            response_status_code = response.status_code
        message = "后端程序错误"
        error_response = Response(
            status=response_status_code,
            data={
                "code": 1,
                "data": None
            })
        # GeneralError 异常实例
        if isinstance(self.exc, GeneralError):
            message = str(self.exc)
        # 自定义格式化函数处理的错误
        elif type(self.exc) in FORMAT_ERRORS:
            error_format_fun = FORMAT_ERRORS.get(type(self.exc))
            message = error_format_fun(self.exc, response)
        # 含描述信息的错误
        elif type(self.exc) in ERROR_MESSAGE:
            message = ERROR_MESSAGE.get(type(self.exc))
        # 含描述信息的状态码
        elif response_status_code in CODE_MESSAGE:
            message = CODE_MESSAGE.get(response_status_code)
        error_response.data["message"] = message
        return error_response


def common_exception_handler(exc, context):
    """
    异常处理函数
    :param exc:
    :param context:
    :return:
    """
    return ExceptionResponse(exc, context).err_response()
