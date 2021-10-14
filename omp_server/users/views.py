"""
用户视图相关函数
"""
import re
import datetime
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin, RetrieveModelMixin,
    DestroyModelMixin, UpdateModelMixin
)
from rest_framework_jwt.views import JSONWebTokenAPIView
from rest_framework_jwt.settings import api_settings

from django_filters.rest_framework.backends import DjangoFilterBackend

from db_models.models import (UserProfile, OperateLog)
from users.users_filters import UserFilter
from utils.common.paginations import PageNumberPager
from users.users_serializers import (
    UserSerializer, JwtSerializer,
    OperateLogSerializer, UserUpdatePasswordSerializer
)


class UsersView(ListModelMixin, RetrieveModelMixin, CreateModelMixin,
                DestroyModelMixin, UpdateModelMixin, GenericViewSet):
    """
        list:
        查询用户列表

        retrieve:
        查询一个用户

        create:
        创建一个新用户

        delete:
        删除一个现有用户

        update:
        更新一个现有用户

        partial_update:
        更新一个现有用户的一个或多个字段
    """
    queryset = UserProfile.objects.all().order_by("id")
    serializer_class = UserSerializer
    pagination_class = PageNumberPager
    # 过滤字段
    filter_backends = (DjangoFilterBackend,)
    filter_class = UserFilter
    # 操作描述信息
    get_description = "获取用户"
    post_description = "新建用户"
    put_description = "更新用户"
    delete_description = "删除用户"


class OperateLogView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
        list:
        查询操作记录列表

        retrieve:
        查询一条操作记录
    """
    queryset = OperateLog.objects.all()
    serializer_class = OperateLogSerializer
    # 操作描述信息
    get_description = "获取用户操作记录"


class JwtAPIView(JSONWebTokenAPIView):
    """
        post:
        登录，签发 JwtToken 令牌
    """
    serializer_class = JwtSerializer

    def post(self, request, *args, **kwargs):
        # django authenticate 缺陷
        # 验证 username 大小写不敏感, 忽略两边空格
        # 验证 password 忽略两边空格
        username_ls = list(
            UserProfile.objects.values_list(
                "username", flat=True))
        if request.data.get("username", "") not in username_ls or \
                re.search(r"\s", request.data.get("password", "")):
            raise ValidationError(
                "Unable to log in with provided credentials.")

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            raise ValidationError(
                "Unable to log in with provided credentials.")
        user = serializer.object.get("user") or request.user
        token = serializer.object.get("token")
        response_data = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER(
            token, user, request)
        response = Response(response_data)
        if api_settings.JWT_AUTH_COOKIE:
            # remember 取值 True，则 cookie 过期时间为 7 天
            expiration_time = api_settings.JWT_EXPIRATION_DELTA
            if serializer.validated_data.get("remember"):
                expiration_time = datetime.timedelta(days=7)
            expiration = (datetime.datetime.utcnow() + expiration_time)
            response.set_cookie(
                api_settings.JWT_AUTH_COOKIE,
                token,
                expires=expiration,
            )
        return response


class UserUpdatePasswordView(GenericViewSet, CreateModelMixin):
    """
        create:
        修改用户密码
    """

    queryset = UserProfile.objects.all()
    serializer_class = UserUpdatePasswordSerializer
    # 操作描述
    post_description = "更新用户密码"
