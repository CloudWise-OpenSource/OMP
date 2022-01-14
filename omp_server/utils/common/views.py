import os
import logging

from django.conf import settings
from django.http import FileResponse

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin

from utils.common.exceptions import OperateError

logger = logging.getLogger("server")


class BaseDownLoadTemplateView(GenericViewSet, ListModelMixin):
    """
        list:
        获取模板文件
    """
    # 操作描述信息
    get_description = "获取模板文件"

    def list(self, request, *args, **kwargs):
        template_file_name = kwargs.get("template_file_name")
        assert template_file_name is not None
        parent_path = kwargs.get("parent_path", "template")
        template_path = os.path.join(
            settings.BASE_DIR.parent,
            "package_hub", parent_path, template_file_name)
        try:
            file = open(template_path, 'rb')
            response = FileResponse(file)
            response["Content-Type"] = "application/octet-stream"
            response["Content-Disposition"] = \
                f"attachment;filename={template_file_name}"
        except FileNotFoundError:
            logger.error(f"{template_path} not found")
            raise OperateError("组件模板文件缺失")
        return response
