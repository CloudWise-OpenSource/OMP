import json
import os
import random
import string

from django.db import transaction
from rest_framework import serializers
from db_models.models import ToolExecuteMainHistory, ToolInfo, Host, Service, \
    ToolExecuteDetailHistory, UploadFileHistory
from tool.tasks import exec_tools_main


class ToolInfoSerializer(serializers.ModelSerializer):
    class Meta:
        """ 元数据 """
        model = ToolInfo
        fields = ("target_name",)


class ToolDetailSerializer(serializers.ModelSerializer):
    tool = ToolInfoSerializer()
    duration = serializers.SerializerMethodField()
    tool_detail = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    tool_args = serializers.SerializerMethodField()

    class Meta:
        """ 元数据 """
        model = ToolExecuteMainHistory
        fields = "__all__"

    def get_duration(self, obj):
        return obj.duration

    def tools_boj_ls(self, obj):
        if hasattr(self, "tools_obj"):
            return self.tools_obj
        tools_obj = ToolExecuteDetailHistory.objects.filter(main_history=obj)
        setattr(self, "tools_obj", tools_obj)
        return tools_obj

    def get_count(self, obj):
        return self.tools_boj_ls(obj).count()

    def get_tool_detail(self, obj):
        """
        获取detail详情
        """
        tool_list = []
        for obj in self.tools_boj_ls(obj):
            url = ""
            if obj.output:
                url = f"tool/download_data/{obj.output.get('file')[0]}"
            tool_list.append(
                {
                    "ip": obj.target_ip,
                    "status": obj.status,
                    "log": obj.execute_log,
                    "url": url
                }
            )
        return tool_list

    def get_tool_args(self, obj):
        tool_args = []
        detail_args = obj.toolexecutedetailhistory_set.first().execute_args
        for args in obj.tool.script_args:
            value = detail_args.get(args.get('key'), "")
            if value:
                tool_args.append({
                    "name": args.get('name'),
                    "value": value
                })
        return tool_args


class ToolFormDetailSerializer(serializers.ModelSerializer):
    default_form = serializers.DictField(source="load_default_form")

    class Meta:
        """ 元数据 """
        model = ToolInfo
        fields = ("id", "name", "default_form", "script_args")


class ToolListSerializer(serializers.ModelSerializer):
    """工具列表序列化"""
    used_number = serializers.SerializerMethodField()

    def get_used_number(self, obj):
        return ToolExecuteMainHistory.objects.filter(tool=obj).count()

    class Meta:
        model = ToolInfo
        fields = ("id", "logo", "name", "kind", "used_number", "description")


class ToolInfoDetailSerializer(serializers.ModelSerializer):
    """工具详情序列化"""

    class Meta:
        model = ToolInfo
        fields = ("name", "description", "logo", "tar_url", "kind",
                  "target_name", "script_path", "script_args", "templates",
                  "readme_info")


class ToolTargetObjectHostSerializer(serializers.ModelSerializer):
    host_agent_state = serializers.SerializerMethodField()

    def get_host_agent_state(self, obj):
        if obj.host_agent == str(obj.AGENT_RUNNING):
            return "正常"
        return "异常"

    class Meta:
        """ 元数据 """
        model = Host
        fields = ("id", "instance_name", "ip", "host_agent_state")


class ToolTargetObjectServiceSerializer(serializers.ModelSerializer):
    instance_name = serializers.CharField(source="service_instance_name")
    host_agent_state = serializers.SerializerMethodField()
    modifiable_kwargs = serializers.SerializerMethodField()

    def get_host_agent_state(self, obj):
        host = Host.objects.filter(ip=obj.ip).first()
        if host and host.host_agent == str(host.AGENT_RUNNING):
            return "正常"
        return "异常"

    def get_modifiable_kwargs(self, obj):
        modifiable_kwargs = {}
        tool = self.context.get("view").kwargs["tool"]
        connection_args = tool.obj_connection_args
        connect_obj = obj.service_connect_info
        port_infos = json.loads(obj.service_port)
        port_dict = {}
        for port_info in port_infos:
            port_dict.update({port_info.get("key"): port_info.get("default")})
        for arg_key in connection_args:
            if arg_key in port_dict:
                modifiable_kwargs[arg_key] = port_dict[arg_key]
            elif connect_obj and hasattr(connect_obj, arg_key):
                modifiable_kwargs[arg_key] = getattr(connect_obj, arg_key)
            else:
                modifiable_kwargs[arg_key] = ""
        return modifiable_kwargs

    class Meta:
        """ 元数据 """
        model = Service
        fields = ("id", "instance_name", "ip", "host_agent_state",
                  "modifiable_kwargs")


class ValidFormAnswer:

    def __init__(self, questions, answers):
        self.questions = questions
        self.answers = answers

    def valid_file(self, question):
        if not question.get("default", {}):
            return True
        file_union_id = question.get("default", {}).get("union_id")
        file = UploadFileHistory.objects.filter(union_id=file_union_id).last()
        if not file:
            raise ValueError(f"表单{question.get('name')}提交的文件不存在！")
        question["default"].update(
            file_name=file.file_name,
            file_url=file.file_url
        )
        return True

    def valid_select(self, question):
        options = question.get("options")
        answer = question.get("default")
        if answer and answer not in options:
            raise Exception(f"表单{question.get('name')}提交的选项不正确！")
        return True

    def valid_input(self, question):
        return True

    def is_valid(self):
        for question in self.questions:
            form_type = question.get("type")
            if not hasattr(self, f"valid_{form_type}"):
                raise Exception(f"暂不支持{form_type}类型")
            answer = self.answers.get(question.get("key"))
            if question.get("required") and not answer:
                raise Exception(f"{question.get('name')}为必填！")
            question.update(default=answer)
            getattr(self, f"valid_{form_type}")(question)
        return self.questions


class ToolFormAnswerSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True, default=0)

    default_form = serializers.DictField(
        help_text="默认表单",
        required=True,
        error_messages={"required": "默认表单为必填"}
    )
    script_args = serializers.ListField(help_text="自定义参数", required=False)

    def verify_task_name(self, value):
        if not value:
            raise ValueError("任务名称为必填字段")
        return str(value)

    def verify_host_info(self, values):
        target_ips = Host.objects.filter(
            id__in=[value.get("id") for value in values],
            host_agent=str(Host.AGENT_RUNNING)
        ).values("ip", "data_folder")
        assert len(target_ips) == len(values), "主机数据异常，请重新选择执行对象！"
        data_folders = {}
        for target_ip in target_ips:
            data_folders[target_ip["ip"]] = target_ip["data_folder"]
        self.context.get("view").kwargs["data_folders"] = data_folders

    def verify_service_info(self, values, tool):
        ids = []
        for value in values:
            ids.append(value.get("id"))
            modifiable_kwargs = value.get("modifiable_kwargs", {})
            for _arg in tool.obj_connection_args:
                assert _arg in modifiable_kwargs, \
                    f"服务{value.get('instance_name')}的参数{_arg}必填！"
        target_ips = list(
            Service.objects.filter(
                service__app_name=tool.target_name,
                id__in=ids
            ).values_list("ip", flat=True)
        )
        assert len(target_ips) == len(values), "服务数据异常，请重新选择执行对象！"
        ips = set(target_ips)
        hosts = Host.objects.filter(ip__in=ips).values("ip", "data_folder")
        data_folders = {}
        for host in hosts:
            data_folders[host["ip"]] = host["data_folder"]
        self.context.get("view").kwargs["data_folders"] = data_folders

    def verify_target_objs(self, values):
        tool = self.context.get("view").kwargs["tool"]
        if tool.target_name == "host":
            self.verify_host_info(values)
        else:
            self.verify_service_info(values, tool)
        return True

    def verify_runuser(self, value):
        return True

    def verify_timeout(self, value):
        if not value:
            raise ValueError("超时时间不可以等于0！")
        return True

    def validate_default_form(self, value):
        tool = self.context.get("view").kwargs["tool"]
        for k in tool.load_default_form().keys():
            getattr(self, f"verify_{k}")(value.get(k))
        return value

    def validate_script_args(self, value):
        tool = self.context.get("view").kwargs["tool"]
        if not tool.script_args:
            return []
        answers = {}
        for script_arg in value:
            answers[script_arg.get("key")] = script_arg.get("default")
        form_answers = ValidFormAnswer(tool.script_args, answers).is_valid()
        return form_answers

    @transaction.atomic
    def create(self, validated_data):
        view_kwargs = self.context.get("view").kwargs
        tool = view_kwargs["tool"]
        request = self.context.get("request")
        default_form = validated_data.get("default_form")
        script_args = validated_data.get("script_args", [])

        history = ToolExecuteMainHistory.objects.create(
            tool=tool,
            task_name=default_form.get("task_name"),
            operator=request.user,
            form_answer=validated_data
        )
        common_args = {}
        file_args = {}
        for script_arg in script_args:
            if script_arg.get("type") == "file":
                file_name = script_arg.get("default", {}).get("file_name")
                file_args[script_arg.get("key")] = os.path.join(
                    tool.tool_folder_path,
                    file_name
                )
            else:
                common_args[script_arg.get("key")] = script_arg.get("default")
        execute_details = []
        for target_obj in default_form.get("target_objs"):
            target_detail = {
                "target_ip": target_obj.get("ip"),
                "main_history": history,
                "time_out": default_form.get("timeout"),
                "run_user": default_form.get("runuser")
            }
            execute_args = {
                "ip": target_obj.get("ip"),
                **target_obj.get("modifiable_kwargs", {}),
                **common_args
            }
            remote_folder = os.path.join(
                view_kwargs["data_folders"].get(target_obj.get("ip"), "/tmp"),
                "omp_packages"
            )
            # output file
            if "output" in execute_args:
                random_str = ''.join(
                    random.sample(string.digits + string.ascii_lowercase, 6))
                file_name = f"{random_str}-{execute_args.get('output')}"
                execute_args["output"] = os.path.join(
                    remote_folder,
                    tool.tool_folder_path,
                    f"{file_name}"
                )
                target_detail["output"] = {"file": [file_name]}
            # input file
            for k, file_url in file_args.items():
                execute_args[k] = os.path.join(remote_folder, file_url)
            execute_details.append(
                ToolExecuteDetailHistory(
                    **target_detail,
                    execute_args=execute_args,
                )
            )
        ToolExecuteDetailHistory.objects.bulk_create(execute_details)
        exec_tools_main.delay(history.id)
        validated_data.update(id=history.id)
        return validated_data
