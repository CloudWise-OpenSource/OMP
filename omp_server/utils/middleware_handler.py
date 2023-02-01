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
import logging

from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

from rest_framework.reverse import reverse
from rest_framework_jwt.utils import jwt_decode_handler

from jwt import DecodeError

from db_models.models import (
    OperateLog, UserLoginLog, UserProfile
)
from django.utils import timezone
from omp_server.settings import INTERFACE_KINDS

logger = logging.getLogger("server")


def get_username_of_token(token):
    """通过jwt token 解析username"""
    _token_user = jwt_decode_handler(token)
    _username = _token_user.get("username")
    return _username


USER_TO_ROLE_EN_DICT = {
    "superuser": "普通管理员",
    "readonlyuser": "只读用户"
}


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
        if _url.startswith("/proxy/v1/grafana"):
            return response
        view_class = resolve(_url).func.cls
        if hasattr(view_class, f"{_method}_description"):
            _desc = getattr(view_class, f"{_method}_description")
        else:
            _desc = "无法确定用户行为"
        _ip, _ = ipware.get_client_ip(request)
        try:
            token = request.COOKIES.get("jwtToken", "toke")
            _username = get_username_of_token(token)
        except DecodeError:
            _username = "匿名用户"
        if _url == reverse("login"):
            _desc = "用户登录"
            request_result = ""
            _token = None
            if "token" in response.data:
                request_result = "登录成功"
                _token = response.data.get("token", "")
                _username = get_username_of_token(_token)
            else:
                return response
            _token_user = UserProfile.objects.filter(username=_username).first()
            data = {
                'username': _username,
                'login_time': timezone.now(),
                'role': USER_TO_ROLE_EN_DICT.get(_token_user.role.lower(), ""),
                'ip': _ip,
                'request_result': request_result
            }
            UserLoginLog.objects.create(**data)
        else:
            # 读取已封装响应数据
            try:
                res_data = json.loads(response.rendered_content)
            except Exception as e:
                return response
            method_dc = {
                'put': '修改',
                'get': '查看',
                'delete': '删除',
                'trace': '查看',
                'patch': '修改'
            }
            method_st = method_dc.get(_method)
            if not method_st:
                method_st = INTERFACE_KINDS.get(_url, "修改")
            if _username != "匿名用户":
                OperateLog(
                    username=_username, request_ip=_ip, request_method=method_st,
                    request_url=_url, description=_desc,
                    response_code=res_data.get("code", 0),
                    request_result=res_data.get("message", "")
                ).save()
        return response


class RoleAuthenticationMiddleware(MiddlewareMixin):
    """用户角色访问限制"""

    def process_view(self, request, func, *args, **kwargs):
        _method = request.method.lower()
        if _method == "get":
            return None
        _url = request.path
        if _url.startswith("/proxy/v1/grafana") or _url.startswith("/api/login/"):
            return None
        try:
            token = request.COOKIES.get("jwtToken", "toke")
            _token_user = jwt_decode_handler(token)
            _username = _token_user.get("username")
        except DecodeError:
            _username = "匿名用户"
        _token_user = UserProfile.objects.filter(username=_username).first()
        if not _token_user:
            # 非页面访问omp接口，放行
            return None
        if _token_user.role.lower() == "superuser":
            return None
        logger.error(f"{_token_user} prohibited this action")
        return JsonResponse({"code": 1, "data": None, "message": f"该{_token_user.username}用户无权限"})
