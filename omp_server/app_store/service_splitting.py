
from db_models.models import  Service
import json
import logging
logger = logging.getLogger('server')

def service_splitting():
    name = 'doim'
    obj_name = 'all'
    add_service_list = ['ProcessWatcher', 'TSManager']
    base_service_port = ''
    base_name = 'bluesky'
    base_name_port=''
    queryset = Service.objects.filter(service_instance_name__contains=name)
    for i in queryset:
        if name in i.service_instance_name:
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
        service_port_ = eval(service_port)
        service_controllers_ = str(service_controllers)
        for j, k in enumerate(service_port_):
            service_instance_name_ = k.get('name')
            service_controllers_obj = service_controllers_.replace(obj_name, service_instance_name_)
            try:
                Service.objects.create(created=created, modified=modified, ip=ip,
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
                logger.error(e)
            if base_name == service_instance_name_:
                base_service_port = json.dumps([service_port_[j]])
                base_name_port=k.get('default')
        for i in add_service_list:
            if i == 'ProcessWatcher':
                service_port1 = base_service_port.replace(base_name_port, ' ').replace(base_name, 'ProcessWatcher')
                service_controllers_obj = service_controllers_.replace(obj_name, 'ProcessWatcher')
            if i == 'TSManager':
                service_port1 = base_service_port.replace(base_name_port, ' ').replace(base_name, 'TSManager')
                service_controllers_obj = service_controllers_.replace(obj_name, 'TSManager')
            try:
                Service.objects.create(created=created, modified=modified, ip=ip, service_instance_name=i,
                                                 service_port=service_port1,
                                                 service_controllers=eval(service_controllers_obj),
                                                 service_role=service_role, service_status=service_status,
                                                 alert_count=alert_count,
                                                 self_healing_count=self_healing_count,
                                                 service_dependence=service_dependence,
                                                 cluster_id=cluster_id, env_id=env_id, service_id=service_id,
                                                 service_connect_info_id=service_connect_info_id)
            except Exception as e:
                logger.error(e)
        try:
            Service.objects.filter(service_instance_name__contains=name).delete()
        except Exception as e:
            logger(e)
    return None