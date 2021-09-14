"""
用户视图相关函数
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, \
    RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from django.contrib.auth import authenticate

from db_models.models import UserProfile
from db_models.models import OperateLog
from users.users_serializers import UserSerializer
from users.users_serializers import OperateLogSerializer


class UsersView(
    ListModelMixin, RetrieveModelMixin, CreateModelMixin,
        DestroyModelMixin, UpdateModelMixin, GenericViewSet):
    """用户视图"""
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer
    get_description = "获取用户"
    post_description = "新建用户"
    put_description = "更新用户"
    delete_description = "删除用户"


class OperateLogView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """用户操作记录视图"""
    queryset = OperateLog.objects.all()
    serializer_class = OperateLogSerializer
    get_description = "获取用户操作记录"


class UpdatePasswordView(APIView):
    """更新密码视图"""
    post_description = "更新密码"

    def post(self, request):
        """
        更新密码视图
        :param request:
        :return:
        """
        data = request.data
        username = data.get("username")
        old_password = data.get("old_password")
        user = authenticate(username=username, password=old_password)
        if not user:
            return Response({"code": 1, "message": "用户名或免密错误"})
        new_password = data.get("new_password")
        re_password = data.pop("re_password")
        if new_password != re_password:
            return Response({"code": 1, "message": "两次密码不一致"})
        user.set_password(data.get("new_password"))
        user.save()
        return Response({"code": 0, "message": "success"})
