from db_models.models import Service
from db_models.models import DetailInstallHistory
from db_models.models import Host
import json
import logging
from utils.plugin.salt_client import SaltClient
logger = logging.getLogger('server')

def service_splitting():
    name = 'doim'
    cw_id=''
    obj_name = 'all'
    add_service_list = ['ProcessWatcher', 'TSManager']
    base_name = 'bluesky'
    portal_name = 'portalServer'
    gateway_name = 'gatewayServer'
    filter_service_name = 'Server'
    gateway_name_api = 'gatewayServerApi'
    service_replace_list = []
    service_id_history=100000
    queryset = Service.objects.filter(service_instance_name__contains=name)
    for i in queryset:
        if name in i.service_instance_name:
            cw_id=i.id
            created = (i.created)
            modified = (i.modified)
            ip = (i.ip)
            service_controllers = (i.service_controllers)
            service_role = (i.service_role)
            service_status = (i.service_status)
            alert_count = (i.alert_count)
            self_healing_count = (i.self_healing_count)
            service_dependence = (i.service_dependence)
            cluster_id = (i.cluster_id)
            env_id = (i.env_id)
            service_id = (i.service_id)
            service_connect_info_id = (i.service_connect_info_id)
            service_port = (i.service_port)
        service_port_ = json.loads(service_port)
        service_controllers_ = str(service_controllers)
        for j, k in enumerate(service_port_):
            service_instance_name_ = k.get('name')
            id=service_id_history+j
            if service_instance_name_ != base_name:
                service_controllers_obj = service_controllers_.replace(obj_name, service_instance_name_)
                try:
                    Service.objects.create(id=id,created=created, modified=modified, ip=ip,
                                           service_instance_name=k.get('name'),
                                           service_port=json.dumps([service_port_[j]]),
                                           service_controllers=eval(service_controllers_obj),
                                           service_role=service_role, service_status=service_status,
                                           alert_count=alert_count,
                                           self_healing_count=self_healing_count,
                                           service_dependence=service_dependence,
                                           cluster_id=cluster_id, env_id=env_id, service_id=service_id,
                                           service_connect_info_id=service_connect_info_id)
                except Exception as e:
                    logger.error('有端口服务拆分入库报错 {}'.format(e))
                    return False
            if service_instance_name_ == base_name:
                for i in add_service_list:
                    if i == 'ProcessWatcher':
                        id=service_id_history+4
                        service_controllers_obj = service_controllers_.replace(obj_name, add_service_list[0])
                    if i == 'TSManager':
                        id = service_id_history + 5
                        service_controllers_obj = service_controllers_.replace(obj_name, add_service_list[1])
                    try:
                        Service.objects.create(id=id,created=created, modified=modified, ip=ip, service_instance_name=i,
                                               service_controllers=eval(service_controllers_obj),
                                               service_role=service_role, service_status=service_status,
                                               alert_count=alert_count,
                                               self_healing_count=self_healing_count,
                                               service_dependence=service_dependence,
                                               cluster_id=cluster_id, env_id=env_id, service_id=service_id,
                                               service_connect_info_id=service_connect_info_id)
                    except Exception as e:
                        logger.error('无端口服务拆分入库报错1 {}'.format(e))
                        return False
        try:
            Service.objects.filter(service_instance_name__contains=name).update(service_instance_name=base_name)
            querysetser = Host.objects.get(ip=ip)
            querysetser.service_num = querysetser.service_num + 5
            querysetser.save()
        except Exception as e:
            logger.error('服务名称替换报错 {}'.format(e))
            return False
    # """ 获取表中数据"""
    service_res=service_log_splitting(cw_id,service_id_history)
    logger.info('日志拆分返回值 {}'.format(service_res))
    logger.info('进入第二步')

    if service_res == True:
        res_queryset = Service.objects.filter(service_instance_name__contains=filter_service_name
                                              ).values_list("service_instance_name", 'ip', 'service_controllers')
        for i in res_queryset:
            logger.info('需要重启服务的对象 {}'.format(i))
            res_dist = {}
            if portal_name in i[0]:
                res_dist[i[1]] = i[2].get('start')
                service_replace_list.append(res_dist)
            if gateway_name in i[0] and gateway_name_api not in i[0]:
                res_dist[i[1]] = i[2].get('start')
                service_replace_list.append(res_dist)
        logger.error('需要重启服务集合 {}'.format(service_replace_list))
        salt_client = SaltClient()
        for i in service_replace_list:
            for j, k in i.items():
                cmd_flag, cmd_msg = salt_client.cmd(
                    target=j,
                    command=k,
                    timeout=60
                )
                logger.info('服务返回值cmd_flag {}'.format(cmd_flag))
                logger.info('服务返回值cmd_msg {}'.format(cmd_msg))
                if not cmd_flag:
                    logger.error('错误信息 {}'.format(cmd_msg))
                    return False
    else:
        logger.error('日志写入失败 {}'.format(service_res))
        return False
    return True


def service_log_splitting(id,service_id_history):
    try:
        queryset_log = DetailInstallHistory.objects.filter(service_id=id)
    except Exception as e:
        logger.error('omp_detail_install_history 数据获取失败 {}'.format(e))
        return False
    for i in queryset_log:
        log_created = i.created
        log_modified = i.modified
        log_install_step_status = i.install_step_status
        log_send_flag = i.send_flag
        log_send_msg = i.send_msg
        log_unzip_flag = i.unzip_flag
        log_unzip_msg = i.unzip_msg
        log_install_flag = i.install_flag
        log_install_msg = i.install_msg
        log_init_flag = i.init_flag
        log_init_msg = i.init_msg
        log_start_flag = i.start_flag
        log_start_msg = i.start_msg
        log_install_detail_args = i.install_detail_args
        log_post_action_flag = i.post_action_flag
        log_post_action_msg = i.post_action_msg
        log_main_install_history_id = i.main_install_history_id
    count = 0
    service_id=service_id_history
    while (count < 5):
        count = count + 1
        service_id = service_id + 1
        try:
            DetailInstallHistory.objects.create(created=log_created,modified=log_modified,install_step_status=log_install_step_status,
                                                send_flag=log_send_flag,unzip_flag=log_unzip_flag,unzip_msg=log_unzip_msg,install_flag
                                                =log_install_flag,install_msg=log_install_msg,init_flag=log_init_flag,init_msg=log_init_msg,
                                                start_flag=log_start_flag,start_msg=log_start_msg,install_detail_args=
                                                log_install_detail_args,post_action_flag=log_post_action_flag,post_action_msg=
                                                log_post_action_msg,main_install_history_id=log_main_install_history_id,send_msg
                                                =log_send_msg,service_id=service_id)
        except Exception as e:
            logger.error('omp_detail_install_history 输入写入失败 {}'.format(e))
            return False
    return True