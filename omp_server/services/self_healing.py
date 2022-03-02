import logging
from db_models.models import Service
from db_models.models import SelfHealingSetting
from db_models.models import SelfHealingHistory
from db_models.models import Alert
from db_models.models import Host
from db_models.models import GrafanaMainPage
from utils.plugin.salt_client import SaltClient
from utils.plugin.crypto import AESCryptor
logger = logging.getLogger('server')
from celery import shared_task
import time
import paramiko
import sys
import requests
import json
from utils.parse_config import MONITOR_PORT
from promemonitor.prometheus_utils import CW_TOKEN
@shared_task
def self_healing(alert_list):
    """ 添加数据入库校验逻辑 添加定时任务"""
    alert_list = Alert.objects.filter(id__in=alert_list)
    logger.info("传入id 信息{}".format(alert_list))
    user_healing = SelfHealingSetting.objects.all().values_list("used", "max_healing_count", "env_id")
    healing_mode = user_healing[0][0]
    max_healing_count = user_healing[0][1]
    env_id = user_healing[0][2]
    host_service_healing = 'monitor_agent进程丢失'
    sudo_check_cmd = "bash /data/omp_monitor_agent/monitor_agent.sh start"
    grafana_url = GrafanaMainPage.objects.filter(instance_name='log').values("instance_url")
    grafana_url_log = (grafana_url[0].get("instance_url"))
    # 监控服务集合
    instance_name_list = []
    # 服务查看时间间隔
    self_healing_interval=50
    # 循环自愈服务间隔
    loop_interval=5
    if len(alert_list) >= 1 and healing_mode == 1:
        time.sleep(loop_interval)
        for i in range(len(alert_list)):
            host_alert_time = alert_list[i].alert_time
            if alert_list[i].alert_type == 'service':
                logger.info("service:service_step_0 进入服务级别的自愈")
                alert_ser = SelfHealingHistory.objects.filter(
                    service_name=alert_list[i].alert_service_name,
                    host_ip=alert_list[i].alert_host_ip,
                    # state=2,
                    alert_time=host_alert_time)
                logger.info("service_step_1 需要入库信息集合长度: {} ".format(alert_ser.count()))
                instance_name_list.append(alert_list[i].alert_instance_name)
                logger.info("service_step_2 需要入库信息集合列表: {} ".format(instance_name_list))
                if alert_ser.count() == 0:
                    service_queryset = Service.objects.filter(service_instance_name__in=instance_name_list).values_list(
                        "ip", "service_controllers", "service_instance_name","id").order_by("id")
                    logger.info("service_step_3 Service表返回结合: {} ".format(service_queryset))
                    for j in service_queryset:
                        try:
                            res_dist = {}
                            res_dist['ip'] = j[0]
                            res_dist['start'] = j[1].get('start')
                            res_dist['service_instance_name'] = j[2].split('-')[0]
                            logger.info("service_step_4 服务启动脚本入库信息".format(res_dist))
                            SelfHealingHistory.objects.create(
                                is_read=0, host_ip=alert_list[i].alert_host_ip,
                                service_name=alert_list[i].alert_service_name, state=2,
                                alert_time=alert_list[i].alert_time,
                                fingerprint=alert_list[i].fingerprint,
                                env_id=env_id,
                                monitor_log=alert_list[i].monitor_log,
                                service_en_type=0,
                                instance_name=alert_list[i].alert_instance_name,
                                start_time=alert_list[i].create_time,
                                healing_log=res_dist,
                                alert_content=alert_list[i].alert_describe)
                        except Exception as e:
                            logger.info("service_step_4 服务级别入库失败,报错信息为:{}".format(e))
            if alert_list[i].alert_type == 'host' and host_service_healing in alert_list[i].alert_describe:
                logger.info("host:host_step_0 进入主机级别的自愈")
                ssh_res = self_healing_ssh_verification(alert_list[i].alert_host_ip, sudo_check_cmd)
                logger.info("host_step_1 主机ssh校验对象:{},校验结果:{}".format(alert_list[i].alert_host_ip,ssh_res))
                """ ssh 正常  监控启动完成 """
                if ssh_res[0] == True and ssh_res[1] == 1:
                    """ 查询所有主机"""
                    service_queryset_1 = Service.objects.filter(ip=alert_list[i].alert_host_ip).values_list\
                        ( "ip","service_controllers","service_instance_name","id").order_by("id")
                    logger.info("host_step_2 Service表返回结合{} ".format(service_queryset_1))
                    """ 批量请求接口"""
                    req_monitor_agent = []
                    req_monitor_agent_ = []
                    for h1 in service_queryset_1:
                        if h1[1].get('start') is not None:
                            req_dist = {}
                            req_dist['ip'] = h1[0]
                            req_dist['service_name'] = h1[2].split('-')[0]
                            req_monitor_agent_.append(req_dist)
                    req_monitor_agent.append(req_monitor_agent_[0])
                    logger.info("monitor_agent_res_请求数据类型{} 请求数据内容"
                                "".format(type(req_monitor_agent),req_monitor_agent))
                    try:
                        monitor_agent_res_batch = get_service_status_direct(req_monitor_agent)
                    except Exception as e:
                        logger.info("monitor_agent_res_error 监控报错信息{}".format(e))
                    """ 服务状态查看"""
                    if monitor_agent_res_batch[0].get("status") ==0:
                        for w in service_queryset_1:
                            logger.info("host_step_3 服务状态异常逻辑 ")
                            if w[1].get('start') is not None:
                                try:
                                    logger.info("host_step_4 需要入库信息:{},host_ip:{},alert_time:{}"
                                                "".format(w[2].split('-')[0],w[0],host_alert_time))
                                    alert_ser_0 = SelfHealingHistory.objects.filter(
                                        service_name=w[2].split('-')[0],
                                        host_ip=w[0],
                                        alert_time=host_alert_time)
                                    logger.info("host_step_5 需要入库信息集合列表:{}".format(alert_ser_0))
                                    if alert_ser_0.count() == 0:
                                        res_dist = {}
                                        res_dist['ip'] = w[0]
                                        res_dist['start'] = w[1].get('start')
                                        res_dist['service_instance_name'] =w[2].split('-')[0]
                                        logger.info("host_step_5 服务启动脚本入库信息".format(res_dist))
                                        instance_name_list.append(w[2])
                                        SelfHealingHistory.objects.create(
                                            is_read=0, host_ip=w[0],
                                            service_name=w[2].split('-')[0],
                                            state=2,
                                            alert_time=host_alert_time,
                                            env_id=env_id,
                                            instance_name=w[2],
                                            service_en_type=1,
                                            healing_log=res_dist,
                                            alert_content=alert_list[i].alert_describe,
                                            monitor_log=grafana_url_log+"?var-app={}".format(w[2].split('-')[0]),
                                            start_time=host_alert_time)
                                except Exception as e:
                                    logger.info("host_step_6 服务级别入库失败,报错信息".format(e))
                                    return False
                                    sys.exit()
                if ssh_res[0]==False:
                    logger.info("host_step_2 主机ssh 校验失败退出")
                    break
        history_queryset = SelfHealingHistory.objects.filter(
            instance_name__in=instance_name_list, state=2).values("id","healing_log").order_by( "id")
        logger.info("self_healing_0 需要自愈对象集合 {}".format(history_queryset))
        if len(history_queryset) > 0:
            logger.info("self_healing_1 进入自愈逻辑 {}".format(len(history_queryset)))
            service_replace_list_0 = []
            for z in history_queryset:
                healing_dist = {}
                healing_dist['ip'] = z.get("healing_log").get("ip")
                healing_dist['start'] = z.get("healing_log").get("start")
                healing_dist['id'] = z.get("id")
                healing_dist['service_name'] = z.get("healing_log").get("service_instance_name")
                service_replace_list_0.append(healing_dist)
            logger.info("self_healing_2 需要自愈服务列表: {}".format(service_replace_list_0))
            salt_client = SaltClient()
            count = 0
            while (count < max_healing_count):  # 变量
                logger.info("self_healing_3 进入循环自愈流程")
                count = count + 1
                logger.info("self_healing_4  第{}次自愈输出列表{},列表长度为:{}".format(
                    count, service_replace_list_0, len(service_replace_list_0)))
                """ 需要修改"""
                for k in range(len(service_replace_list_0)):
                    cmd_flag, cmd_msg = salt_client.cmd(
                        target=service_replace_list_0[k].get("ip"),
                        command=service_replace_list_0[k].get("start").replace("start","restart"),
                        timeout=60)
                    logger.info("self_healing_5 循环自愈服务IP: {}".format(service_replace_list_0[k].get("ip")))
                    logger.info("self_healing_5 循环自愈服务start :{}".format(service_replace_list_0[k].get("start")))
                    logger.info("self_healing_5 自愈执行返回状态码:{}".format(cmd_flag))
                    logger.info("self_healing_5 自愈执行返回结果:{}".format(cmd_msg))
                    if cmd_flag == True:  # 重试逻辑
                        """ 查看服务状态   """
                        time.sleep(self_healing_interval)
                        loop_request_monitor_agent = []
                        req_dist = {}
                        req_dist['ip'] = service_replace_list_0[k].get("ip")
                        req_dist['service_name'] = service_replace_list_0[k].get("service_name")
                        loop_request_monitor_agent.append(req_dist)
                        logger.info("loop_0 第{}次自愈,服务自愈过程-服务状态查看请求数据: {}"
                                    "".format(count, loop_request_monitor_agent))
                        try:
                            monitor_agent_res=get_service_status_direct(loop_request_monitor_agent)
                        except Exception as e:
                            logger.info("monitor_agent_res_error 监控报错信息{}".format(e))
                            break
                        logger.info("monitor_agent_res 监控返回数据{},数据类型{}"
                                    "".format(monitor_agent_res, type(monitor_agent_res)))
                        if monitor_agent_res[0].get("status")==1:
                            logger.info("monitor_agent_res 服务状态查看正常更新服务状态")
                            SelfHealingHistory.objects.filter(
                                id=service_replace_list_0[k].get("id")).update(
                                state=1, healing_count=count,end_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                            service_replace_list_0.remove(service_replace_list_0[k])
                            break
                    if cmd_flag == False:
                        SelfHealingHistory.objects.filter(
                            id=service_replace_list_0[k].get("id")) \
                            .update(healing_count=count,state=0,
                                    end_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                        service_replace_list_0.remove(service_replace_list_0[k])
                        break
                    if len(service_replace_list_0)==0:
                        break
            logger.info("self_healing_4 到达循环条件之后仍未自愈服务 : {}".format(service_replace_list_0))
            if len(service_replace_list_0)!=0:
                for k1 in range(len(service_replace_list_0)):
                    SelfHealingHistory.objects.filter(
                        id=service_replace_list_0[k].get("id")).update(
                        state=0, healing_count=max_healing_count,
                        end_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
def self_healing_ssh_verification(host_self_healing_list,sudo_check_cmd):
    host_self_healing_list=host_self_healing_list
    aes_crypto = AESCryptor()
    host_list = Host.objects.filter(ip=host_self_healing_list).values_list("ip", "port", "username", "password")
    for i in range(len(host_list)):
        try:
            if len(host_list[i][2])!=0 and  len(host_list[i][3])!=0:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(hostname=host_list[i][0], port=host_list[i][1],
                               username=host_list[i][2], password=aes_crypto.decode(host_list[i][3]),
                               timeout=60)
                """ 监控启动脚本 是否需要重启多次？"""
                sudo_check_cmd = sudo_check_cmd
                stdin, stdout, stderr = client.exec_command(sudo_check_cmd)
                stdout = stdout.read().decode('utf-8')
                stderr = stderr.read().decode('utf-8')
                """ 输出信息需要修改"""
                if "dead" in stdout:
                    """ 监控未 启动 """
                    logger.info("monitor_agent 启动失败,输出信息:{} ".format(stdout))
                    return True, 0
                if "running" in stdout:
                    """ 监控启动"""
                    return True, 1
            else:
                logger.info("监控重启失败 无ssh")
                """ 无ssh的情况"""
                return False,0
        except Exception as e:
            logger.info("监控重启失败,报错信息为：{}".format(e))
            """ ssh 连接超时"""
            return False,1
    return True,2
    transport.close()

def get_service_status_direct(service_obj_list):
    """
    直接从monitor_agent获取服务状态
    param: [{"ip": "127.0.0.1", "service_name": "mysql"}, {"ip": "127.0.0.1", "service_name": "redis"}]
    """
    service_obj_result = list()
    monitor_agent_port = MONITOR_PORT.get('monitorAgent', 19031)
    headers_type = {"Content-Type": "application/json"}
    headers_authentication = CW_TOKEN
    headers = dict(headers_type, **headers_authentication)
    ip_item_list = list()
    ip_list = list()
    for ele in service_obj_list:
        ip_list.append(ele.get("ip"))
    ip_list = list(set(ip_list))
    for ip in ip_list:
        ip_service_list = list()
        for item in service_obj_list:
            if ip == item.get("ip"):
                ip_service_list.append(item)
        ip_item_list.append(ip_service_list)
    try:
        for ii in ip_item_list:
            status_url = f"http://{ii[0].get('ip')}:{monitor_agent_port}/service_status"  # NOQA
            response = requests.request(
                "POST", status_url, headers=headers, data=json.dumps(ii))
            logger.info("interface_monitor_agent监控接口返回数据:{}".format(response))
            logger.info("interface_monitor_agent请求地址 {}".format(status_url))
            if response.status_code != 200:
                continue
            logger.info("interface_monitor_agent 接口返回:{}".format(response.json()))
            service_obj_result.extend(response.json().get("beans"))
        return service_obj_result
    except Exception as e:
        logger.error(f"interface_monitor_agent 获取制定服务列表状态失败，详情为：{e}")
        return service_obj_list