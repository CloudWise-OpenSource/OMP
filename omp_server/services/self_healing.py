import logging
from db_models.models import Service
from db_models.models import SelfHealingSetting
from db_models.models import SelfHealingHistory
from db_models.models import Alert
from utils.plugin.salt_client import SaltClient
logger = logging.getLogger('server')
from celery import shared_task
import time

@shared_task
def self_healing(alert_list):
    alert_list = Alert.objects.filter(id__in=alert_list)
    user_healing = SelfHealingSetting.objects.all().values_list("used", "max_healing_count", "env_id")
    healing_mode = user_healing[0][0]
    max_healing_count = user_healing[0][1]
    env_id = user_healing[0][2]
    instance_name_list = []
    logger.info("step0 配置文件返回信息:healing_mode:{},max_healing_count:{}".format(healing_mode, max_healing_count))
    if len(alert_list) >= 1 and healing_mode == 1:
        for i in range(len(alert_list)):
            if alert_list[i].alert_type == 'service':
                logger.info(
                    "step1 告警calert_servie_name：{},alert_host_ip:{},alert_time:{},create_time:{}".format(
                        alert_list[i].alert_service_name, alert_list[i].alert_host_ip,
                        alert_list[i].alert_time, alert_list[i].create_time))
                alert_ser = SelfHealingHistory.objects.filter(
                    service_name=alert_list[i].alert_service_name,
                    host_ip=alert_list[i].alert_host_ip,
                    start_time=alert_list[i].create_time)
                # alert_time=datetime.datetime.strptime(alert_list[i].alert_time, "%Y-%m-%d %H:%M:%S"))
                logger.info("hi step1.3需要重启服务列表alert_ser {}".format(alert_ser.count()))
                if alert_ser.count() == 0:
                    try:
                        SelfHealingHistory.objects.create(
                            is_read=0, host_ip=alert_list[i].alert_host_ip,
                            service_name=alert_list[i].alert_service_name, state=2,
                            # alert_time=datetime.datetime.strptime(alert_list[i].alert_time, "%Y-%m-%d %H:%M:%S"),
                            alert_time=alert_list[i].alert_time,
                            fingerprint=alert_list[i].fingerprint,
                            env_id=env_id,
                            monitor_log=alert_list[i].monitor_log,
                            service_en_type=alert_list[i].alert_service_type,
                            instance_name=alert_list[i].alert_instance_name,
                            start_time=alert_list[i].create_time,
                            alert_content=alert_list[i].alert_describe)
                    except Exception as e:
                        logger.error("自愈数据输入失败".format(e))
                    instance_name_list.append(alert_list[i].alert_instance_name)
            logger.info("step2需要重启服务列表instance_name_list: {}".format(instance_name_list))
        if len(instance_name_list) > 0:
            service_queryset = Service.objects.filter(
                service_instance_name__in=instance_name_list).values_list(
                "ip", "service_controllers", "service_instance_name")
            service_replace_list = []
            for i in service_queryset:
                res_dist = {}
                res_dist['ip'] = i[0]
                res_dist['start'] = i[1].get('start')
                res_dist['service_instance_name'] = i[2].split('-')[0]
                service_replace_list.append(res_dist)
            info = 'not  running'
            salt_client = SaltClient()
            count = 0
            logger.info("step3需要重启服务列表service_replace_list: {}".format(service_replace_list))
            while (count < max_healing_count):  # 变量
                count = count + 1
                logger.info("step4 第{}自愈输出列表{},列表长度为:{}".format(
                    count, service_replace_list, len(service_replace_list)))
                """ 需要修改"""
                for i in range(len(service_replace_list)):
                    cmd_flag, cmd_msg = salt_client.cmd(
                        target=service_replace_list[i].get("ip"),
                        command=service_replace_list[i].get("start"),
                        timeout=60)
                    logger.info("服务自愈过程-服务启动之后状态码: {}".format(cmd_flag))
                    logger.info("服务自愈过程-服务启动之后返回值: {}".format(cmd_msg))
                    if cmd_flag:  # 重试逻辑
                        cmd_flag, cmd_msg = salt_client.cmd(
                            target=service_replace_list[i].get("ip"),
                            command=service_replace_list[i].get("start").replace('start', 'status'),
                            timeout=60)
                        logger.info("服务自愈过程-状态信息查看: {}".format(cmd_flag))
                        logger.info("服务自愈过程-状态信息查看: {}".format(cmd_msg))
                        if cmd_flag == True and info not in cmd_msg:  # 重试逻辑
                            """ 修改表中数据的时间状态"""
                            SelfHealingHistory.objects.filter(
                                host_ip=service_replace_list[i].get("ip"),
                                service_name=service_replace_list[i].get("service_instance_name")) \
                                .update(state=1, healing_count=count,
                                        end_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                            service_replace_list.remove(service_replace_list[i])
                            break
            if len(service_replace_list) > 0:
                logger.info("step5 到达循环条件之后依然有问题列表: {}".format(service_replace_list))
                for i in range(len(service_replace_list)):
                    SelfHealingHistory.objects.filter(
                        host_ip=service_replace_list[i].get("ip"), service_name
                        =service_replace_list[i].get("service_instance_name")) \
                        .update(state=0, healing_count=max_healing_count,
                                end_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    return True
