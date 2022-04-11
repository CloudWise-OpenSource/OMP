import json
import logging

from django.db.models import F

from db_models.models import Service, DetailInstallHistory, Host
from utils.plugin.salt_client import SaltClient


logger = logging.getLogger('server')


def service_log_splitting(obj_id, split_service_ids):
    install_logs = list(
        DetailInstallHistory.objects.filter(
            service_id=obj_id
        ).values()
    )
    if not install_logs:
        return False
    install_log = install_logs[0]
    install_log.pop("id")
    install_log.pop("service_id")
    for _id in split_service_ids:
        try:
            DetailInstallHistory.objects.create(
                **install_log,
                service_id=_id
            )
        except Exception as e:
            logger.error('omp_detail_install_history 输入写入失败 {}'.format(e))
            return False
    return True


# todo:抽出hadoop、doim等存在子服务或进程的服务，增加服务下属子服务进程, the end
def service_splitting(doim_ids):
    name = 'doim'
    obj_name = 'all'
    add_service_list = ['ProcessWatcher', 'TSManager', 'bluesky']
    base_name = 'bluesky'
    restart_services = ['portalServer', 'gatewayServer']
    service_restart = True
    queryset_info = list(
        Service.objects.filter(
            service_instance_name__contains=name,
            id__in=doim_ids
        ).values()
    )
    for _obj_info in queryset_info:
        _obj_id = _obj_info.pop("id")
        ip = _obj_info.get("ip")
        sub_name = "-" + "-".join(ip.split(".")[-2:])
        _obj_info.pop("service_instance_name")
        service_port = _obj_info.pop("service_port")
        service_controllers_ = json.dumps(_obj_info.pop("service_controllers"))
        service_port_ = json.loads(service_port)
        split_service_ids = []
        for port_info in service_port_:
            service_instance_name_ = port_info.get('name')
            if service_instance_name_ != base_name:
                service_controllers_obj = service_controllers_.replace(
                    obj_name, service_instance_name_
                )
                try:
                    service = Service.objects.create(
                        service_instance_name=port_info.get('name') + sub_name,
                        service_port=json.dumps([port_info]),
                        service_controllers=eval(service_controllers_obj),
                        **_obj_info
                    )
                    split_service_ids.append(service.id)
                except Exception as e:
                    logger.error('有端口服务拆分入库报错 {}'.format(e))
                    return False
            else:
                for add_service in add_service_list:
                    service_controllers_obj = service_controllers_.replace(
                        obj_name, add_service)
                    try:
                        service = Service.objects.create(
                            service_instance_name=add_service + sub_name,
                            service_controllers=eval(service_controllers_obj),
                            service_port=json.dumps([]),
                            **_obj_info
                        )
                        split_service_ids.append(service.id)
                    except Exception as e:
                        logger.error('无端口服务拆分入库报错1 {}'.format(e))
                        return False
        try:
            Service.objects.filter(
                service_instance_name=f"{name}{sub_name}"
            ).update(service_instance_name=f"{base_name}{sub_name}")
            Host.objects.filter(ip=ip).update(
                service_num=F("service_num") + len(split_service_ids)
            )
        except Exception as e:
            logger.error('服务名称替换报错 {}'.format(e))
            return False
        # """ 获取表中数据"""
        service_restart = service_log_splitting(_obj_id, split_service_ids)
        logger.info('日志拆分返回值 {}'.format(service_restart))
        logger.info('进入第二步')

    if service_restart:
        service_replace_list = []
        res_queryset = Service.objects.filter(
            service__app_name__in=restart_services
        ).values('ip', 'service_controllers')
        for restart_service in res_queryset:
            logger.info('需要重启服务的对象 {}'.format(restart_service))
            service_replace_list.append(
                {
                    restart_service["ip"]:
                        restart_service["service_controllers"].get('start')
                }
            )
        logger.info('需要重启服务集合 {}'.format(service_replace_list))
        salt_client = SaltClient()
        for service_info in service_replace_list:
            for _ip, start_cmd in service_info.items():
                cmd_flag, cmd_msg = salt_client.cmd(
                    target=_ip,
                    command=start_cmd,
                    timeout=60
                )
                logger.info('服务返回值cmd_flag {}'.format(cmd_flag))
                logger.info('服务返回值cmd_msg {}'.format(cmd_msg))
                if not cmd_flag:
                    logger.error('错误信息 {}'.format(cmd_msg))
                    return False
    else:
        logger.error('日志写入失败 {}'.format(service_restart))
        return False
    return True
