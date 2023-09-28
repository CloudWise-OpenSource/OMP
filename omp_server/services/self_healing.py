import logging
import copy
import time
import paramiko
import requests
import json
import datetime
from db_models.models import Service, SelfHealingSetting, \
    SelfHealingHistory, Host, WaitSelfHealing, ApplicationHub
from celery import shared_task
from promemonitor.prometheus_utils import CW_TOKEN
from utils.plugin.salt_client import SaltClient
from utils.plugin.crypto import AESCryptor
from concurrent.futures import (
    ThreadPoolExecutor, as_completed
)
from utils.parse_config import MONITOR_PORT, BASIC_ORDER, \
    THREAD_POOL_MAX_WORKERS, HEALTH_REDIS_TIMEOUT, HEALTH_REQUEST_COUNT, HEALTH_REQUEST_SLEEP
from app_store.new_install_utils import RedisDB
from utils.plugin.crontab_utils import maintain

logger = logging.getLogger('server')


class SelfHealing:
    def __init__(self, instance_tp, max_healing_count):
        # 需要起停信息ip等操作
        self.instance_tp = instance_tp
        self.max_healing_count = max_healing_count
        self.redis = RedisDB()
        self.service_info = set()
        self.host_info = set()

    def merge_and_filter_ser(self, alert_info):
        """
        初始化用，过滤服务（主机），及服务初始化信息
        """
        data_dict = {}
        host_ls = []
        for d in alert_info:
            if d.get("alert_service_name") and d.get("alert_instance_name") and \
                    d['alert_instance_name'] not in self.service_info:
                data_dict.setdefault(d['alert_service_name'], []).append(d)
                self.service_info.add(d['alert_instance_name'])
            if not d.get("alert_service_name") and \
                    d['alert_host_ip'] not in self.host_info:
                self.host_info.add(d['alert_host_ip'])
                host_ls.append(d)
        # 初始化主机和服务信息
        self.host_info = dict(Host.objects.filter(
            ip__in=list(self.host_info)).values_list("ip", "agent_dir"))
        self.service_info = dict(Service.objects.filter(
            service_instance_name__in=list(self.service_info)
        ).values_list("service_instance_name", "service_controllers"))
        return data_dict, host_ls

    def sort_service(self, alert_info):
        """
        初始化用，提供排序
        """
        sort_dict = copy.copy(BASIC_ORDER)
        # 赋值并过滤 存在问题 过滤需要过滤会过滤到同服务不同实例名的例
        data_dict, host_ls = self.merge_and_filter_ser(alert_info)
        sort_ser = []
        for key in sort_dict:
            temp = []
            for item in sort_dict[key]:
                temp.extend(data_dict.pop(item, []))
            if temp:
                sort_ser.append(temp)
        other_ser = data_dict.values()
        if other_ser:
            other_ser = [service for app in other_ser for service in app]
            sort_ser.append(other_ser)
        if host_ls:
            sort_ser.insert(0, host_ls)
        return sort_ser

    def exec_salt_cmd(self, ip, command, his_obj):
        """
        进行启动，请求接口查询状态，日志追加，状态变更
        """
        salt_obj = SaltClient()
        cmd_flag, cmd_msg = salt_obj.cmd(
            target=ip,
            command=command,
            timeout=60)
        healing_log = f"执行ip:{ip},执行cmd:{command},执行结果:{cmd_flag},执行详情:{cmd_msg},"
        if not cmd_flag:
            his_obj.healing_log = healing_log
            his_obj.save()
            return False
        # 循环检测，超出检测时常后退出
        for _ in range(HEALTH_REQUEST_COUNT):
            res = self.check_health(ip, command, his_obj, healing_log)
            if res:
                return True
            time.sleep(HEALTH_REQUEST_SLEEP)
        return False

    @staticmethod
    def check_health(ip, command, his_obj, healing_log):
        request_monitor = {"service_name": his_obj.service_name, "ip": ip}
        if "omp_monitor_agent" in command:
            request_monitor["service_name"] = "node"
        try:
            monitor_agent_res = get_service_status_direct([request_monitor])
        except Exception as e:
            his_obj.healing_log = healing_log + ",请求监控报错"
            his_obj.save()
            logger.info("monitor_agent_res_error 监控报错信息{}".format(e))
            return False
        if monitor_agent_res[0].get("status") == 1:
            his_obj.healing_log = healing_log + "monitor_agent_res 服务状态查看正常更新服务状态"
            his_obj.save()
            return True
        return False

    def get_command(self, instance_name):
        """
        获取cmd ，通过策略类型选择启动或重启
        """
        action_dc = {
            0: "start",
            1: "restart"
        }
        action = action_dc[self.instance_tp]
        service_action = self.service_info.get(instance_name)
        host_action = self.host_info.get(instance_name)
        if service_action:
            command = service_action.get(action) if service_action.get(action) \
                else service_action.get("start", "").replace("start", action)
        else:
            command = f"bash {host_action}/omp_monitor_agent/monitor_agent.sh {action}"
        return command

    @staticmethod
    def write_db(data, healing_count):
        """
        合法后创建记录表用
        """

        initial_v = {
            "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "is_read": 0,
            "state": 2,
            "healing_log": "",
            "healing_count": healing_count
        }
        compare_dc = {
            "alert_host_ip": "host_ip",
            "alert_service_name": "service_name",
            "alert_time": "alert_time",
            # "fingerprint": "fingerprint",
            # "monitor_log": "monitor_log",
            "alert_describe": "alert_content",
            "alert_instance_name": "instance_name",
        }
        write_db_dc = {}
        for field, value in data.items():
            compare_v = compare_dc.get(field)
            if compare_v:
                write_db_dc[compare_v] = value
        write_db_dc.update(initial_v)
        return SelfHealingHistory.objects.create(**write_db_dc)

    def get_redis_count(self, instance_name):
        """
        缓存校验用，周期内自愈次数最大限制
        """
        _flag, _data = self.redis.get(f"heal{instance_name}")
        if not _flag:
            count = 1
        else:
            count = int(_data) + 1
        self.redis.update(
            name=f"heal{instance_name}",
            data=count,
            timeout=HEALTH_REDIS_TIMEOUT
        )
        return count

    def host(self, hosts_info):
        identify_des = "monitor_agent进程丢失"
        ip = hosts_info["alert_host_ip"]
        if identify_des not in hosts_info.get('alert_describe'):
            # 暂不支持的模式
            logger.info(f"暂不支持的模式{ip}")
            return True
        ip = hosts_info["alert_host_ip"]
        host_ip = "".join(ip.split("."))
        healing_count = self.get_redis_count(host_ip)
        if healing_count > self.max_healing_count:
            # 自愈实例超出限制个数
            return True
        # 写库
        his_obj = self.write_db(hosts_info, healing_count)
        res = self.exec_salt_cmd(ip, self.get_command(ip), his_obj)
        if not res:
            return self.exec_salt_cmd(ip, self.get_command(ip), his_obj)
        his_obj.state = SelfHealingHistory.HEALING_SUCCESS if res else SelfHealingHistory.HEALING_FAIL
        his_obj.end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        his_obj.save()

    def service(self, service_info):
        # 获取service的redis的key HEALTH_REDIS_TIMEOUT
        identify_des = "been down for more than a minute"
        if identify_des not in service_info.get('alert_describe'):
            logger.info(f"暂不支持的模式{service_info['alert_instance_name']}")
            # 暂不支持的模式
            return True
        healing_count = self.get_redis_count(service_info['alert_instance_name'])
        if healing_count > self.max_healing_count:
            # 自愈实例超出限制个数
            logger.info(f"自愈实例超出限制个数{service_info['alert_instance_name']}")
            return True
        # 写库
        his_obj = self.write_db(service_info, healing_count)
        command = self.get_command(service_info['alert_instance_name'])
        res = self.exec_salt_cmd(service_info['alert_host_ip'], command, his_obj)
        if not res:
            # 二次重复不再进行其余操作
            res = self.exec_salt_cmd(service_info['alert_host_ip'], command, his_obj)
        his_obj.state = SelfHealingHistory.HEALING_SUCCESS if res else SelfHealingHistory.HEALING_FAIL
        his_obj.end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        his_obj.save()


def get_enable_health(repairs):
    h_ls = set(Host.objects.all().values_list("ip", flat=True))
    for app in ApplicationHub.objects.filter(is_base_env=False):
        if not app.extend_fields.get("affinity", "") == "tengine":
            h_ls.add(app.app_name)
    return list(h_ls - set(repairs))


@shared_task
@maintain
def self_healing(task_id):
    # 校验是否需要自愈
    self_obj = SelfHealingSetting.objects.get(id=task_id)
    if not self_obj.used:
        return "该策略并未启用"
    if "all" in self_obj.repair_instance:
        data = self_obj.get_enable_health(list())
    else:
        data = list(self_obj.repair_instance)
    wait_ser = WaitSelfHealing.objects.filter(service_name__in=data)
    if not wait_ser or wait_ser.filter(repair_status=1):
        return "存在正在自愈的服务或无需自愈的服务"
    wait_ser.update(repair_status=1)
    repair_ser_dc = dict(wait_ser.values_list("id", "repair_ser"))

    repair_info = []
    for ser in repair_ser_dc.values():
        repair_info.append(ser)
    logger.info(f"需要自愈的服务:{repair_info}")
    # 排序 先主机 - 基础组件 -自研服务
    try:
        health_obj = SelfHealing(self_obj.instance_tp, self_obj.max_healing_count)
        ser = health_obj.sort_service(repair_info)
        logger.info(f"等待自愈的服务信息:{ser}")
        # 开启修复
        for service_ls in ser:
            with ThreadPoolExecutor(THREAD_POOL_MAX_WORKERS) as executor:
                future_list = []
                for service in service_ls:
                    future_obj = executor.submit(
                        getattr(health_obj,
                                "service" if service['alert_type'] == "component" else service['alert_type']), service)
                    future_list.append(future_obj)
                for future in as_completed(future_list):
                    future.result()
    except Exception as e:
        logger.info(f"未知异常，需保护释放锁 {e}")
        # 释放锁 ,防止惰性查询再次筛选
    WaitSelfHealing.objects.filter(id__in=list(repair_ser_dc)).delete()


def self_healing_ssh_verification(host_self_healing_list, sudo_check_cmd):
    """
        先留着吧暂时没啥用。
        """

    host_self_healing_list = host_self_healing_list
    aes_crypto = AESCryptor()
    host_list = Host.objects.filter(ip=host_self_healing_list).values_list("ip", "port", "username", "password")
    for i in range(len(host_list)):
        try:
            if len(host_list[i][2]) != 0 and len(host_list[i][3]) != 0:
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
                return False, 0
        except Exception as e:
            logger.info("监控重启失败,报错信息为：{}".format(e))
            """ ssh 连接超时"""
            return False, 1
    return True, 2


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
