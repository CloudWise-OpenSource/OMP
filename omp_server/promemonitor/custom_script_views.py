# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author:' Lingyang.guo'
# CreateDate: 14:08
import json
import logging
import os.path
import traceback

import requests
import yaml
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from rest_framework.mixins import ListModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

# from db_models.models import UploadFileHistory
from db_models.models.custom_metric import CustomScript
from promemonitor.custom_script_serializers import CustomScriptSerializer
from promemonitor.promemonitor_filters import CustomScriptFilter
from utils.common.paginations import PageNumberPager
from promemonitor.prometheus_utils import PrometheusUtils
from utils.parse_config import MONITOR_PORT
from promemonitor.prometheus_utils import CW_TOKEN

logger = logging.getLogger('server')


class CustomScriptViewSet(GenericViewSet, ListModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin):
    """
    list:
    查询自定义脚本列表

    create:
    新增自定义脚本记录

    update:
    更新自定义脚本模型字段

    delete:
    删除指定自定义脚本
    """
    get_description = "读取自定义脚本记录"
    post_description = "更新自定义脚本记录"
    serializer_class = CustomScriptSerializer
    pagination_class = PageNumberPager
    # 过滤，排序字段
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    queryset = CustomScript.objects.all().order_by("-created")
    filter_class = CustomScriptFilter

    prometheus_util = PrometheusUtils()

    def list(self, request, *args, **kwargs):
        """
        获取自定义脚本列表信息
        """
        queryset = self.filter_queryset(self.get_queryset())  # 分页，过滤，排序

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        新增一条自定义脚本记录
        """

        file_obj = request.FILES.get('file')

        script_name = file_obj.name
        if CustomScript.objects.filter(script_name=script_name).exists():
            return Response(data={"code": 1, "message": "该脚本已存在，请重新上传！"})
        scrape_interval = request.data.get("scrape_interval", 60)
        enabled = request.data.get("enabled", 1)

        script_content = file_obj.read()
        script_content = str(script_content, encoding="utf8")
        metrics = list()
        for line in script_content.split("\n"):
            if "def get_" in line and ":" in line:
                metric = line.split("def get_")[1].split("(")[0].strip()
                metrics.append(metric)
        metric_num = len(metrics)
        description = script_content.split("\n")[0]

        try:
            custom_script = CustomScript(
                script_name=script_name,
                script_content=script_content,
                metrics=metrics,
                metric_num=metric_num,
                scrape_interval=scrape_interval,
                enabled=enabled,
                description=description,
                bound_hosts=json.dumps([])
            )
            custom_script.save()
            # UploadFileHistory.location(file=file_obj, module_obj=custom_script, user=request.user)
            script_job_str = script_name.split('.', 1)[0]
            prom_job_dict = {
                "job_name": f"{script_job_str}Exporter",
                "metrics_path": f"/metrics/monitor/{script_job_str}",
                "file_sd_configs": [
                    {
                        "refresh_interval": f"{scrape_interval}s",
                        "files": [
                            f"targets/{script_job_str}Exporter_all.json"
                        ]
                    }
                ]
            }
            with open(self.prometheus_util.prometheus_conf_path, "r") as fr:
                content = yaml.load(fr.read(), yaml.Loader)
            content.get("scrape_configs").append(prom_job_dict)
            with open(self.prometheus_util.prometheus_conf_path, "w", encoding="utf8") as fw:
                yaml.dump(data=content, stream=fw,
                          allow_unicode=True, sort_keys=False)
            job_target_json = os.path.join(self.prometheus_util.prometheus_targets_path,
                                           f"{script_job_str}Exporter_all.json")
            if not os.path.exists(job_target_json):
                with open(job_target_json, "w") as target_fw:
                    json.dump([], target_fw)
            reload_prometheus_url = "http://localhost:19011/-/reload"
            requests.post(reload_prometheus_url,
                          auth=self.prometheus_util.basic_auth)
            return Response({})
        except Exception as e:
            logger.error(traceback.format_exc(e))
            return Response(data={"code": 1, "message": "新增自定义脚本失败！"})

    def update(self, request, *args, **kwargs):
        """
        只可以更改绑定主机列表，启用状态和探测周期
        """
        instance = self.get_object()
        new_scrape_interval = request.data.get("scrape_interval")
        new_enabled = request.data.get("enabled", 1)
        new_bound_host_list = request.data.get("bound_hosts")
        new_description = request.data.get("description", instance.description)

        instance.scrape_interval = new_scrape_interval
        instance.enabled = new_enabled
        instance.bound_hosts = new_bound_host_list
        instance.description = new_description
        instance.save()
        headers = {"Content-Type": "application/json"}
        headers.update(CW_TOKEN)

        try:
            script_job_str = instance.script_name.split('.', 1)[0]
            prom_target_list = list()
            monitor_agent_port = MONITOR_PORT.get('monitorAgent', 19031)
            for host in instance.bound_hosts:
                agent_add_custom_script_url = f"http://{host}:{monitor_agent_port}/update/custom_scripts/add"  # NOQA
                payload = {
                    "custom_scripts":
                        [{
                            "script_name": script_job_str,
                            "script_content": instance.script_content,
                            "script_metrics": instance.metrics
                        }]
                }
                payload = json.dumps(payload)
                res = requests.post(
                    url=agent_add_custom_script_url, headers=headers, data=payload)
                if res.status_code != 200:
                    logger.error(f"向主机{host}agent发送添加自定义脚本信息失败！")
                    return Response(data={"code": 1, "message": f"向主机{host}agent发送添加自定义脚本信息失败！"})
                prom_target_list.append({
                    "targets": [
                        f"{host}:{monitor_agent_port}"
                    ],
                    "labels": {
                        "instance": f"{host}",
                        "service_type": "service",
                        "env": "default"
                    }
                })

            job_target_json = os.path.join(self.prometheus_util.prometheus_targets_path,
                                           f"{script_job_str}Exporter_all.json")
            with open(job_target_json, "w") as jtj_fw:
                json.dump(prom_target_list, jtj_fw, indent=4)
        except Exception as e:
            logger.error(traceback.format_exc(e))
            logger.error("向agent发送添加自定义脚本信息失败！")
            return Response(data={"code": 1, "message": "添加自定义脚本信息失败！"})

        return Response()

    def destroy(self, request, *args, **kwargs):
        """
        向agent发送删除该自定义脚本信息；删除prometheus任务；删除库记录
        """
        instance = self.get_object()
        script_job_str = instance.script_name.split('.', 1)[0]
        with open(self.prometheus_util.prometheus_conf_path, "r") as fr:
            content = yaml.load(fr.read(), yaml.Loader)
        for i in content.get("scrape_configs"):
            if i.get("job_name") == f"{script_job_str}Exporter":
                content.get("scrape_configs").remove(i)
        with open(self.prometheus_util.prometheus_conf_path, "w", encoding="utf8") as fw:
            yaml.dump(data=content, stream=fw,
                      allow_unicode=True, sort_keys=False)
        job_target_json = os.path.join(self.prometheus_util.prometheus_targets_path,
                                       f"{script_job_str}Exporter_all.json")

        if os.path.exists(job_target_json):
            os.remove(job_target_json)
        monitor_agent_port = MONITOR_PORT.get('monitorAgent', 19031)
        for host in instance.bound_hosts:
            agent_delete_custom_script_url = f"http://{host}:{monitor_agent_port}/update/custom_scripts/delete"  # NOQA
            payload = {
                "custom_scripts":
                    [{
                        "script_name": script_job_str,
                    }]
            }
            payload = json.dumps(payload)
            res = requests.post(
                url=agent_delete_custom_script_url, data=payload)
            if res.status_code != 200:
                logger.error(f"向主机{host}agent发送删除自定义脚本信息失败！")
                return Response(data={"code": 1, "message": f"向主机{host}agent发送删除自定义脚本信息失败！"})
        instance.delete()
        return Response({})


class CustomScriptJobInfoView(GenericViewSet, ListModelMixin):
    get_description = "读取自定义脚本任务信息"
    # queryset = CustomScript.objects.all().order_by("-created")
    serializer_class = Serializer

    prometheus_util = PrometheusUtils()

    def list(self, request, *args, **kwargs):
        """
        读取自定义脚本任务信息
        """
        cs_id = request.query_params.get("id")
        instance = CustomScript.objects.get(id=cs_id)
        script_job_str = instance.script_name.split('.', 1)[0]
        job_str = f"{script_job_str}Exporter"
        prometheus_targets_url = f"http://127.0.0.1:{MONITOR_PORT.get('prometheus', '19011')}/api/v1/targets"
        try:
            res = requests.get(url=prometheus_targets_url,
                               auth=self.prometheus_util.basic_auth)
            if res.status_code != 200:
                return Response(data={"code": 1, "message": "获取自定义脚本任务信息失败！"})
            active_targets_list = res.json().get("data").get("activeTargets")
            custom_script_job_list = list()
            for active_target in active_targets_list:
                if active_target.get("scrapePool") == job_str:
                    custom_script_job_info = {
                        "scrape_url": active_target.get("scrapeUrl"),
                        "status": active_target.get("health"),
                        "last_scrape_duration": active_target.get("lastScrapeDuration"),
                        "last_error": active_target.get("lastError")
                    }
                    custom_script_job_list.append(custom_script_job_info)
            return Response(custom_script_job_list)
            # return Response(data={"code": 1, "message": "获取自定义脚本任务信息失败！"})
        except Exception as e:
            logger.error(traceback.format_exc(e))
            return Response(data={"code": 1, "message": "获取自定义脚本任务信息失败！"})
