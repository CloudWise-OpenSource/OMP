import os
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, \
    ALL_COMPLETED

from django.conf import settings
from ruamel import yaml

from app_store.new_install_utils import RedisDB
from db_models.models import ToolInfo
from utils.parse_config import THREAD_POOL_MAX_WORKERS
from utils.plugin.public_utils import file_md5, local_cmd

verify_tar_path = os.path.join(
    settings.PROJECT_DIR,
    "package_hub/tool/verify_tar/"
)

lock_key = "tool_package_verify"


def load_verify_tar(tar_name=None):
    tmp_package = os.path.join(
        settings.PROJECT_DIR, "tmp", uuid.uuid4().hex)
    local_cmd(f'mkdir -p {tmp_package}')
    tar_files = []
    with RedisDB().conn.lock(lock_key, timeout=10):
        if tar_name:
            file_path = os.path.join(verify_tar_path, tar_name)
            if os.path.exists(file_path):
                local_cmd(f'mv {file_path} {tmp_package}')
                tar_files.append(tar_name)
            return tmp_package, tar_files
        tar_packages = os.listdir(verify_tar_path)
        for tar_package in tar_packages:
            file_path = os.path.join(verify_tar_path, tar_package)
            if not tar_package.endswith(".tar.gz"):
                local_cmd(f'rm -rf {file_path}')
                continue
            local_cmd(f'mv {file_path} {tmp_package}')
            tar_files.append(tar_package)
    return tmp_package, tar_files


class ValidToolTar:
    key_type = {"labels": str, "spec": dict, "args": list, "output": str}

    def __init__(self, tar_file, tmp_package):
        self.tar_file = tar_file
        self.tmp_package = tmp_package
        self.tool_info = {}

    def valid_file(self, script_arg):
        pass

    def valid_select(self, script_arg):
        pass

    def valid_select_multiple(self, script_arg):
        pass

    def valid_input(self, script_arg):
        pass

    def verify_args(self, script_args):
        for script_arg in script_args:
            form_type = script_arg.get("type")
            if not hasattr(self, f"valid_{form_type}"):
                raise Exception(f"暂不支持{form_type}类型")
            getattr(self, f"valid_{form_type}")(script_arg)
        return True

    def verify_name(self, name):
        if not bool(name):
            raise Exception("name不可为空！")
        self.tool_info["name"] = name
        return True

    def verify_desc(self, desc):
        if not bool(desc):
            raise Exception("desc不可为空！")
        self.tool_info["desc"] = desc
        return True

    def verify_labels(self, kind):
        if not hasattr(ToolInfo, f"KIND_{kind.upper()}"):
            raise Exception("yaml中labels类型不支持！")
        self.tool_info["kind"] = getattr(ToolInfo, f"KIND_{kind.upper()}")
        return True

    def verify_spec(self, spec):
        if not bool(spec):
            raise Exception("spec不可为空！")
        target_name = spec.get("target")
        if not target_name:
            raise Exception("yaml中未指明执行对象！")
        templates = spec.get("templates", [])
        if not isinstance(templates, list):
            raise Exception("templates参数类型不正确！")
        for template in templates:
            if not os.path.isfile(os.path.join(self.folder_path, template)):
                raise Exception(f"模版文件{template}文件不存在！")
        connection_args = spec.get("connection_args", [])
        if not isinstance(connection_args, list):
            raise Exception("connection_args参数类型不正确！")
        for connection_arg in connection_args:
            if not isinstance(connection_arg, str):
                raise Exception("connection_args参数类型不正确！")
        return True

    def verify_output(self, output):
        if not hasattr(ToolInfo, f"OUTPUT_{output.upper()}"):
            raise Exception("output参数只能是terminal或file！")
        self.tool_info["output"] = getattr(
            ToolInfo, f"OUTPUT_{output.upper()}"
        )
        return True

    def verify_send_package(self, send_package):
        for package in send_package:
            if not os.path.isfile(os.path.join(self.folder_path, package)):
                raise Exception(f"需要发送的文件{package}文件不存在！")
        self.tool_info["send_package"] = send_package
        return True

    def verify_yaml_info(self, package_name):
        yaml_path = os.path.join(self.folder_path, f"{package_name}.yaml")
        with open(yaml_path, "r", encoding="utf8") as fp:
            content = yaml.load(fp.read(), yaml.Loader)
        for k, v in content.items():
            if not v:
                v = content.get(k, self.key_type.get(k)())
            if not isinstance(v, self.key_type.get(k)):
                raise Exception(f"{k}参数类型不正确！")
            getattr(self, f"verify_{k}")(v)
        return True

    def __call__(self, *args, **kwargs):
        package_name = self.tar_file.split("-")[0]
        if not package_name:
            return f"{self.tar_file}名称不符合要求！"
        file_path = os.path.join(self.tmp_package, self.tar_file)
        md5 = file_md5(file_path)
        if not md5:
            local_cmd(f'rm -rf {file_path}')
            return f"获取{self.tar_file}的md5值失败！"
        if ToolInfo.objects.filter(source_package_md5=md5).exists():
            return f"{self.tar_file}已存在！"
        tar_folder = os.path.join(
            self.tmp_package, f"{self.tar_file}_{uuid.uuid4().hex}")
        _out, _err, _code = local_cmd(
            f"mkdir -p {tar_folder} && tar -xf {file_path} -C {tar_folder}"
        )
        if _code:
            return _out
        self.folder_path = os.path.join(tar_folder, package_name)
        files = os.listdir(self.folder_path)
        for file_name in [f"{package_name}.py", f"{package_name}.yaml"]:
            if file_name not in files:
                return f"{self.tar_file}中必须包含文件{file_name}！"
        try:
            self.verify_yaml_info(package_name)
        except Exception as e:
            return str(e)
        return ""


def verify_tar_files(tmp_package, tar_files):
    with ThreadPoolExecutor(THREAD_POOL_MAX_WORKERS) as executor:
        all_task = []
        for tar_file in tar_files:
            valid_obj = ValidToolTar(tmp_package, tar_file)
            future_obj = executor.submit(valid_obj)
            all_task.append(future_obj)
        wait(all_task, return_when=ALL_COMPLETED)
