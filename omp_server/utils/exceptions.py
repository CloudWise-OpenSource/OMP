"""
异常类
"""


class GeneralError(Exception):
    """ 通用错误 """

    def __init__(self, err="通用异常"):
        self.err = err
        super(GeneralError, self).__init__(err)


class OperateError(GeneralError):
    """ 操作错误 """

    def __init__(self, err="操作错误"):
        super(OperateError, self).__init__(err)
