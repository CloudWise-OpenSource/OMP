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

from rest_framework.mixins import ListModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

# from db_models.models import UploadFileHistory
from db_models.models.custom_metric import CustomScript
from promemonitor.custom_script_serializers import CustomScriptSerializer
from utils.common.paginations import PageNumberPager
from promemonitor.prometheus_utils import PrometheusUtils
from utils.parse_config import MONITOR_PORT

logger = logging.getLogger('server')


class CustomScriptViewSet(GenericViewSet, ListModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin):
    """
    list:
    查询自定义脚本列表

    create:
    新增自定义脚本记录

    update:
    更新自定义脚本模型字段
    """
    get_description = "读取自定义脚本记录"
    post_description = "更新自定义脚本记录"
    serializer_class = CustomScriptSerializer
    pagination_class = PageNumberPager

    prometheus_util = PrometheusUtils()

    def list(self, request, *args, **kwargs):
        """
        获取自定义脚本列表信息
        """
        queryset = CustomScript.objects.all().order_by("-created")  # 分页，过滤，排序

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
        scrape_interval = request.data.get("scrape_interval")
        enabled = request.data.get("enabled")

        script_content = file_obj.read()
        script_content = str(script_content, encoding="utf8")
        metrics = json.dumps(["get_demo_metric"])  # TODO
        metric_num = 1  # TODO
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
                bound_hosts=""
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
        new_enabled = request.data.get("enabled")
        new_bound_host_list = json.loads(request.data.get("bound_hosts"))

        instance.scrape_interval = new_scrape_interval
        instance.enabled = new_enabled
        instance.bound_hosts = json.dumps(json.loads(
            instance.bound_hosts).extend(new_bound_host_list))
        instance.save()

        try:
            script_job_str = instance.script_name.split('.', 1)[0]
            prom_target_list = list()
            monitor_agent_port = MONITOR_PORT.get('monitorAgent', 19031)
            for host in json.loads(instance.bound_hosts):
                agent_add_custom_script_url = f"http://{host}:{monitor_agent_port}/update/custom_scripts/add"  # NOQA
                payload = {
                    "custom_scripts":
                        [{
                            "script_name": script_job_str,
                            "script_content": instance.script_content,
                            "script_metrics": json.loads(instance.metrics)
                        }]
                }
                payload = json.dumps(payload)
                res = requests.post(
                    url=agent_add_custom_script_url, data=payload)
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
                json.dump(prom_target_list, jtj_fw)
        except Exception as e:
            logger.error(e)
            logger.error("向agent发送添加自定义脚本信息失败！")

        return Response()

    def destroy(self, request, *args, **kwargs):
        """
        向agent发送删除该自定义脚本信息；删除prometheus任务；删除库记录
        """
        instance = self.get_object()
        script_job_str = instance.script_name.split('.', 1)[0]
        with open(self.prometheus_util.prometheus_conf_path, "r") as fr:
            content = yaml.load(fr.read(), yaml.Loader)
        prom_job_dict = {
            "job_name": f"{script_job_str}Exporter",
            "metrics_path": f"/metrics/monitor/{script_job_str}",
            "file_sd_configs": [
                {
                    "refresh_interval": f"{instance.scrape_interval}s",
                    "files": [
                        f"targets/{script_job_str}Exporter_all.json"
                    ]
                }
            ]
        }
        content.get("scrape_configs").remove(prom_job_dict)
        with open(self.prometheus_util.prometheus_conf_path, "w", encoding="utf8") as fw:
            yaml.dump(data=content, stream=fw,
                      allow_unicode=True, sort_keys=False)
        job_target_json = os.path.join(self.prometheus_util.prometheus_targets_path,
                                       f"{script_job_str}Exporter_all.json")

        if os.path.exists(job_target_json):
            os.remove(job_target_json)
        # TODO 向agent发送删除自定义脚本的信息
        for host in json.loads(instance.bound_hosts):
            agent_delete_custom_script_url = f"http://{host}:{monitor_agent_port}/update/custom_scripts/delete"  # NOQA
            payload = {
                "custom_scripts":
                    [{
                        "script_name": script_job_str,
                    }]
            }
            res = requests.post(
                url=agent_delete_custom_script_url, data=payload)
            if res.status_code != 200:
                logger.error(f"向主机{host}agent发送删除自定义脚本信息失败！")
                return Response(data={"code": 1, "message": f"向主机{host}agent发送删除自定义脚本信息失败！"})
        instance.delete()
        return Response({})
