"""
验证器
"""
import re
import emoji

from rest_framework.exceptions import ValidationError


class ReValidator:
    """ 正则表达式验证器 """

    def __init__(self, regex, message="字段格式不合法"):
        self.regex = regex
        self.message = message

    def __call__(self, value):
        if re.match(self.regex, value) is None:
            raise ValidationError(self.message)


class NoEmojiValidator:
    """ 表情验证器 """

    def __init__(self, message="字段不可含有表情"):
        self.message = message

    def __call__(self, value):
        if emoji.emoji_count(value) > 0:
            raise ValidationError(self.message)


class NoChineseValidator:
    """ 中文验证器 """

    def __init__(self, message="字段不可含有中文"):
        self.message = message

    def __call__(self, value):
        if any(re.findall(r"[\u4e00-\u9fa5]?", value)):
            raise ValidationError(self.message)


class UserPasswordValidator:
    """ 用户密码验证器 """

    def __init__(self, message="字段格式不合法"):
        self.char_list = ("`", "~", "!", "?", "@", "#", "$", "%", "^",
                          "&", ",", "(", ")", "[", "]", "{", "}", "_",
                          "+", "-", "*", "/", ".", ";", ":")
        self.message = message

    def __call__(self, value):
        for e in value:
            if re.match(r"[a-zA-Z0-9]", str(e)) is not None:
                continue
            if str(e) not in self.char_list:
                raise ValidationError(self.message)
