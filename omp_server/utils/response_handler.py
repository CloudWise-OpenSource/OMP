# -*- coding: utf-8 -*- 
# Project: response_handler
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-10 21:36
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
重新封装的响应数据类
"""

from rest_framework.renderers import JSONRenderer


class APIRenderer(JSONRenderer):
    """自定义响应数据类"""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        自定义render返回数据
        :param data: 返回数据
        :param accepted_media_type:
        :param renderer_context:
        :return:
        """
        dic = {"code": 0, "message": "success", "data": None}
        if isinstance(data, dict):
            if data.get("code") == 1:
                dic = {"code": 1, "message": data.get("message"), "data": None}
            elif "non_field_errors" in data:
                if isinstance(data.get("non_field_errors"), list):
                    _message = ""
                    for item in data.get("non_field_errors"):
                        _message += f"{item} "
                    dic = {"code": 1, "message": _message, "data": None}
            else:
                dic = {"code": 0, "message": "success", "data": data}
        else:
            dic = {"code": 0, "message": "success", "data": data}
        return super().render(data=dic, accepted_media_type=accepted_media_type, renderer_context=renderer_context)
