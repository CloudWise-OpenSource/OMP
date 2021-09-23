# -*- coding: utf-8 -*-
# Project: middleware_handler
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-11 16:48
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
公共中间件
"""

import json
import ipware

from django.urls import resolve
# from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin

from rest_framework.reverse import reverse
from rest_framework_jwt.utils import jwt_decode_handler

from jwt import DecodeError

from db_models.models import OperateLog


class OperationLogMiddleware(MiddlewareMixin):
    """用于处理操作日志的中间件"""

    def process_response(self, request, response):
        """
        拦截请求的中间件
        :param request: 请求对象
        :type request HttpRequest
        :param response: 响应对象
        :return:
        """
        _method = request.method.lower()
        if _method == "get":
            return response
        _url = request.path
        view_class = resolve(_url).func.cls
        if hasattr(view_class, f"{_method}_description"):
            _desc = getattr(view_class, f"{_method}_description")
        else:
            _desc = "无法确定用户行为"
        _ip, _ = ipware.get_client_ip(request)
        try:
            token = request.COOKIES.get("jwtToken", "toke")
            _token_user = jwt_decode_handler(token)
            _username = _token_user.get("username")
        except DecodeError:
            _username = "匿名用户"
        if _url == reverse("login"):
            _desc = "用户登录"
            if "token" in response.data:
                response_code = 0
                request_result = "success"
            else:
                response_code = 1
                request_result = "登录失败"
            OperateLog(
                username=_username, request_ip=_ip, request_method=_method,
                request_url=_url, description=_desc,
                response_code=response_code, request_result=request_result
            ).save()
        else:
            # 读取已封装响应数据
            res_data = json.loads(response.rendered_content)
            OperateLog(
                username=_username, request_ip=_ip, request_method=_method,
                request_url=_url, description=_desc,
                response_code=res_data.get("code", 0),
                request_result=res_data.get("message", "")
            ).save()
        return response
