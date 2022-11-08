"""
    公共异常
    注意 common_exception_handler 的优先级按照以下顺序进行：
        1. GeneralError 异常实例
        2. FORMAT_ERRORS 字典，自定义格式化函数处理的错误
        3. ERROR_MESSAGE 字典，含描述信息的错误
        4. CODE_MESSAGE 字典，含描述信息的状态码
    将返回的结果注入 response 的 message 字段中，缺省值为 "后端程序错误"
"""
from django.db import DatabaseError
from rest_framework.exceptions import ValidationError


class GeneralError(Exception):
    """ 通用错误 """

    def __init__(self, err="通用异常"):
        super(GeneralError, self).__init__(err)


class OperateError(GeneralError):
    """ 操作错误 """

    def __init__(self, err="操作发生错误"):
        super(OperateError, self).__init__(err)


def _validation_error_message(exc, response):
    """ ValidationError 错误数据格式化 """
    err_message = "数据校验错误"
    assert response.data is not None
    data = response.data

    if isinstance(data, list):
        err_message = "; ".join(data)
    if isinstance(data, dict):
        err_message_ls = []
        for k, v in data.items():
            if isinstance(v, list):
                ip_err = "Enter a valid IPv4 or IPv6 address."
                if ip_err in v:
                    v[v.index(ip_err)] = "IP格式不合法"
                err_message_ls.append("; ".join(v))
            else:
                err_message_ls.append(v)
        err_message = "; ".join(err_message_ls)
    return err_message


# 自定义格式化函数处理的错误
FORMAT_ERRORS = {
    ValidationError: _validation_error_message,
}

# 含描述信息的错误
ERROR_MESSAGE = {
    NameError: "变量未被定义或引用",
    DatabaseError: "数据库错误",
}

# 含描述信息的状态码
CODE_MESSAGE = {
    401: "未认证",
    403: "无访问权限",
    404: "未找到",
    405: "暂不支持此请求",
    500: "服务器错误",
}
