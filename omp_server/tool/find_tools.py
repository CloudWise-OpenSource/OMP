import os
import uuid
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, \
    ALL_COMPLETED

from django.conf import settings
from ruamel import yaml

from app_store.new_install_utils import RedisDB
from db_models.models import ToolInfo
from utils.parse_config import THREAD_POOL_MAX_WORKERS
from utils.plugin.public_utils import file_md5, local_cmd


logger = logging.getLogger(__name__)


base_tar_path = os.path.join(settings.PROJECT_DIR, "package_hub/tool")
verify_tar_path = os.path.join(base_tar_path, "verify_tar")
verified_folder_path = os.path.join(base_tar_path, "folder")
verified_tar_path = os.path.join(base_tar_path, "tar")


lock_key = "tool_package_verify"


class ValidForm:

    def __init__(self, form_list):
        self.form_list = form_list

    def base_valid(self, form):
        for k in ["key", "name"]:
            if not form.get(k):
                raise Exception(f"args中部分缺少{k}！")
            if not isinstance(form.get(k), str):
                raise Exception(f"args中{k}参数格式不正确！")
        if not form.get("required"):
            form["required"] = False
        else:
            form["required"] = True

    def valid_file(self, form):
        if form.get("default"):
            form.pop("default")

    def valid_select(self, form):
        options = form.get("options")
        if not options:
            raise Exception(f"args中单选缺少options参数！")
        if not isinstance(options, list):
            raise Exception(f"args中单选options参数类型不正确！")
        for option in options:
            if not isinstance(option, str):
                raise Exception(f"args中单选options选项类型只支持字符串！")
        if form.get("default") and form.get("default") not in options:
            raise Exception(f"args中单选default选项必须在options中！")

    def valid_input(self, form):
        if form.get("default") and not isinstance(form.get("default"), str):
            raise Exception(f"args中文本内容default只支持字符串")

    def __call__(self, *args, **kwargs):
        for form in self.form_list:
            form_type = form.get("type")
            if not hasattr(self, f"valid_{form_type}"):
                raise Exception(f"暂不支持{form_type}类型")
            self.base_valid(form)
            getattr(self, f"valid_{form_type}")(form)
        return self.form_list


class ValidToolTar:
    key_default = {
        "labels": "management",
        "spec": {"target": "host"},
        "args": [],
        "output": "terminal",
    }

    def __init__(self, tmp_package, tar_file):
        self.tmp_package = tmp_package
        self.tar_file = tar_file
        self.tool_info = {}

    def verify_args(self, script_args):
        ValidForm(script_args)
        self.tool_info["script_args"] = script_args
        return True
    verify_args._type = list

    def verify_name(self, name):
        if not bool(name):
            raise Exception("name不可为空！")
        self.tool_info["name"] = name
        return True
    verify_name._type = str

    def verify_desc(self, desc):
        if not bool(desc):
            raise Exception("desc不可为空！")
        self.tool_info["description"] = desc
        return True
    verify_desc._type = str

    def verify_labels(self, kind):
        if not hasattr(ToolInfo, f"KIND_{kind.upper()}"):
            raise Exception("yaml中labels类型不支持！")
        self.tool_info["kind"] = getattr(ToolInfo, f"KIND_{kind.upper()}")
        return True
    verify_labels._type = str

    def verify_spec(self, spec):
        target_name = spec.get("target", "host")
        if not isinstance(target_name, str):
            raise Exception("yaml中target参数类型错误！")
        self.tool_info["target_name"] = target_name
        templates = spec.get("templates", [])
        if not isinstance(templates, list):
            raise Exception("templates参数类型不正确！")
        for template in templates:
            if not os.path.isfile(os.path.join(self.folder_path, template)):
                raise Exception(f"模版文件{template}文件不存在！")
        self.tool_info["template_filepath"] = templates
        connection_args = spec.get("connection_args", [])
        if not isinstance(connection_args, list):
            raise Exception("connection_args参数类型不正确！")
        for connection_arg in connection_args:
            if not isinstance(connection_arg, str):
                raise Exception("connection_args参数类型不正确！")
        self.tool_info["obj_connection_args"] = connection_args
        return True
    verify_spec._type = dict

    def verify_output(self, output):
        if not hasattr(ToolInfo, f"OUTPUT_{output.upper()}"):
            raise Exception("output参数只能是terminal或file！")
        self.tool_info["output"] = getattr(
            ToolInfo, f"OUTPUT_{output.upper()}"
        )
        return True
    verify_output._type = str

    def verify_send_package(self, send_package):
        for package in send_package:
            if not os.path.isfile(os.path.join(self.folder_path, package)):
                raise Exception(f"需要发送的文件{package}文件不存在！")
        self.tool_info["send_package"] = send_package
        return True
    verify_send_package._type = list

    def verify_script_name(self, script_name):
        if not os.path.isfile(os.path.join(self.folder_path, script_name)):
            raise Exception(f"需要发送的文件{script_name}文件不存在！")
        self.tool_info["script_path"] = script_name
        return True
    verify_script_name._type = str

    def verify_script_type(self, script_type):
        if not hasattr(ToolInfo, f"SCRIPT_TYPE_{script_type.upper()}"):
            raise Exception("script_type参数只能是python3或shell！")
        self.tool_info["script_type"] = getattr(
            ToolInfo, f"SCRIPT_TYPE_{script_type.upper()}"
        )
        return True
    verify_script_type._type = str

    def verify_yaml_info(self, package_name):
        yaml_path = os.path.join(self.folder_path, f"{package_name}.yaml")
        with open(yaml_path, "r", encoding="utf8") as fp:
            content = yaml.load(fp.read(), yaml.Loader)
        for k, default in self.key_default.items():
            if not content.get(k):
                content[k] = default
        for k, v in content.items():
            verify_func = getattr(self, f"verify_{k}")
            if not isinstance(v, getattr(verify_func, "_type")):
                raise Exception(f"{k}参数类型不正确！")
            verify_func(v)
        return True

    def read_read_me(self):
        read_me_path = os.path.join(self.folder_path, "README.md")
        with open(read_me_path, "r", encoding="utf-8") as f:
            data = f.read()
        self.tool_info["readme_info"] = data

    def create_tool_info(self, package_name, md5):
        tar_save_name = self.tar_file.replace(".tar.gz", f"-{md5}.tar.gz")
        new_tar_path = os.path.join(verified_tar_path, tar_save_name)
        old_tar_path = os.path.join(self.tmp_package, self.tar_file)

        old_package_folder = os.path.join(
            self.tmp_package, f"{package_name}_{md5}/{package_name}")
        new_package_folder = os.path.join(
            verified_folder_path, f"{package_name}-{md5}")
        _out, _err, _code = local_cmd(
            f"mv {old_tar_path} {new_tar_path} && "
            f"mv {old_package_folder} {new_package_folder}"
        )
        if _code:
            return _out
        self.tool_info["source_package_md5"] = md5
        self.tool_info["tool_folder_path"] = f"tool/folder/{package_name}-{md5}"
        self.tool_info["source_package_path"] = f"tool/tar/{tar_save_name}"
        if self.tool_info["output"] == ToolInfo.OUTPUT_FILE:
            self.tool_info["script_args"].append(
                {'key': 'output', 'name': 'output',
                 'type': 'input', 'required': True}
            )
        ToolInfo(**self.tool_info).save()
        self.rm_tool_package()

    def rm_tool_package(self):
        local_cmd(f"/bin/rm -rf {self.tmp_package}")

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
        tar_folder = os.path.join(self.tmp_package, f"{package_name}_{md5}")
        _out, _err, _code = local_cmd(
            f"mkdir -p {tar_folder} && tar -xf {file_path} -C {tar_folder}"
        )
        if _code:
            self.rm_tool_package()
            return _out
        self.folder_path = os.path.join(tar_folder, package_name)
        if not os.path.isfile(
                os.path.join(self.folder_path, f"{package_name}.yaml")
        ):
            self.rm_tool_package()
            return f"{self.tar_file}中必须包含文件{package_name}.yaml！"
        try:
            self.verify_yaml_info(package_name)
        except Exception as e:
            self.rm_tool_package()
            return str(e)
        if os.path.isfile(os.path.join(self.folder_path, "README.md")):
            self.read_read_me()
        self.create_tool_info(package_name, md5)
        return ""


def verify_tar_files(tmp_package, tar_files):
    with ThreadPoolExecutor(THREAD_POOL_MAX_WORKERS) as executor:
        all_task = []
        for tar_file in tar_files:
            valid_obj = ValidToolTar(tmp_package, tar_file)
            future_obj = executor.submit(valid_obj)
            all_task.append(future_obj)
        wait(all_task, return_when=ALL_COMPLETED)
        for future in as_completed(all_task):
            if future.result():
                logger.info(future.result())


def load_verify_tar(tar_name=None):
    tmp_package = os.path.join(
        settings.PROJECT_DIR, "tmp", uuid.uuid4().hex)
    local_cmd(f'mkdir -p {tmp_package}')
    tar_files = []
    with RedisDB().conn.lock(lock_key):
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


def find_tools_package(tar_name=None):
    tmp_package, tar_files = load_verify_tar(tar_name)
    verify_tar_files(tmp_package, tar_files)
