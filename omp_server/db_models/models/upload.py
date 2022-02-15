import os
import random
import string
from datetime import datetime

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models

from utils.plugin.public_utils import file_md5, format_location_size
from .user import UserProfile
from db_models.mixins import TimeStampMixin


class UploadFileHistory(TimeStampMixin):

    STORAGE_KLASS = {"location"}

    module = models.CharField("需要上传文件的model", max_length=32, default="")
    module_id = models.IntegerField("需要上传文件的model id", default=0)
    union_id = models.CharField("文件md5值", max_length=64, default="")
    user = models.ForeignKey(
        UserProfile, null=True,
        on_delete=models.SET_NULL,
        verbose_name="用户")
    # 目前只支持location
    storage_klass = models.CharField(
        "存储方式", max_length=64, default="location")
    # location时相对于omp目录
    relative_path = models.TextField("文件存储相对路径", default="")
    file_name = models.CharField("文件名称", max_length=64, default="")
    # 单位：K,M,G
    file_size = models.CharField("文件大小", max_length=16, default="0K")
    # location时除ip外url
    file_url = models.TextField("文件访问路径", default="")
    deleted = models.BooleanField("删除", default=False)

    class Meta:
        db_table = "omp_upload_file"
        verbose_name = verbose_name_plural = "上传文件记录"

    @classmethod
    def format_file_name(cls, file_name):
        _time = datetime.now().strftime('%Y%m%d%H%M%S')
        random_sub = ''.join(
            random.sample(string.digits+string.ascii_lowercase, 4))
        if len(file_name) > 10:
            file_name = file_name[-10:]
        return f"{_time}-{random_sub}-{file_name}"

    @classmethod
    def location(cls, file, module_obj=None, user=None, **kwargs):
        cls_kwargs = {"relative_path": 'tmp/', "user": user}
        if module_obj:
            cls_kwargs = {
                "module": module_obj.__class__.__name__,
                "module_id": module_obj.id,
            }
            relative_path = module_obj.valid_upload_file(file, **kwargs)
            cls_kwargs["relative_path"] = relative_path
        else:
            relative_path = 'tmp/'
        save_path = os.path.join(settings.PROJECT_DIR, relative_path)
        storage = FileSystemStorage(save_path)
        _time = datetime.now().strftime('%Y%m%d%H%M%S')
        file_name = cls.format_file_name(file.name)
        cls_kwargs["file_name"] = file_name
        if module_obj:
            cls_kwargs["file_url"] = module_obj.upload_file_url(file_name)
        else:
            cls_kwargs["file_url"] = f"download/{file_name}"
        storage.save(storage.generate_filename(file_name), file)
        # FileSystemStorage save 同时计算md5?
        md5 = file_md5(os.path.join(save_path, file_name))
        if md5:
            exists_obj = cls.objects.filter(union_id=md5).last()
            if exists_obj:
                old_file = os.path.join(
                    settings.PROJECT_DIR,
                    exists_obj.relative_path,
                    exists_obj.file_name
                )
                if os.path.exists(old_file):
                    os.remove(os.path.join(save_path, file_name))
                else:
                    exists_obj.file_name = file_name
                    exists_obj.relative_path = relative_path
                    exists_obj.save()
                return exists_obj
        cls_kwargs["file_size"] = format_location_size(file.size)
        return cls.objects.create(union_id=md5, **cls_kwargs)
