import time
import logging
import json
import random

from concurrent.futures import (
    ThreadPoolExecutor, as_completed
)
from utils.parse_config import THREAD_POOL_MAX_WORKERS
from app_store.new_install_utils import RedisDB
from utils.plugin.salt_client import SaltClient
from utils.parse_config import SERVICE_DISCOVERY
from db_models.models import (
    ApplicationHub, Service
)

logger = logging.getLogger('server')


# 存在ip的筛选
class ConfCheck:

    def __init__(self, app_data):
        self.app_data = app_data
        self.redis_obj = RedisDB()
        self.need_key = {'base_dir', 'run_user', 'service_port', 'data_dir', 'log_dir'}
        self.app_dc = {}
        self.ips = {}
        self.response_ls = []
        self.redis_save = []
        # self.cluster_dc = {}
        self.app_ser = {}
        self.is_common_dc = {}
        self.is_base_env = ApplicationHub.objects.filter(
            is_base_env=True
        ).values_list("app_name", flat=True)
        self.is_common = ApplicationHub.objects.filter(
            is_base_env=False, app_type=ApplicationHub.APP_TYPE_COMPONENT).values_list("app_name", flat=True)
        self.service_ip_name = self._get_service_k_v()
        # self.service_cluster_ip = self._get_cluster_ip()
        self.error_ser = set()

    @staticmethod
    def _get_service_k_v():
        service_dc = {}
        service_in_ip = {}
        service_ls = Service.objects.all().values_list("ip", "service__app_name", "service_instance_name")
        for k in service_ls:
            service_dc.setdefault(k[1], []).append(k[0])
            service_in_ip.setdefault(k[1], {}).update({k[0]: k[2]})
        return service_dc, service_in_ip

    @staticmethod
    def _get_cluster_ip():
        """
        "jdk:{1:["192.168.0.1","192.168.0.2"]}"
        """
        app_dc = {}
        service_all = Service.objects.all().values_list("ip", "cluster", "cluster__cluster_service_name")
        for app in service_all:
            if app[1]:
                app_dc.setdefault(app[2], {}).setdefault(app[1], []).append(app[0])
        return app_dc

    @staticmethod
    def explain_json(text):
        if text:
            return json.loads(text)
        return []

    def fix_service(self):
        """
        整理格式
        {
        app_name1:{
        version:"xxx",
        base_dir:"xx",
        run_user:"xx",
        service_port:"xx"
        },
        app_name2:{
        .....
        }
        }
        """
        self.ips = self.app_data.pop("ips", [])
        for info in self.app_data.get("service", []):
            if info.get("child"):
                pro_ser_ls = list(info.get("child").values())[0]
                for app in pro_ser_ls:
                    app_install_dc = {}
                    name = app.pop("name")
                    app_install_dc["version"] = app.pop("version")
                    app_install_dc.update(app)
                    self.app_dc[name] = app_install_dc
            else:
                version = {"version": info.pop("version")[0]}
                name = info.pop("name")
                info.update(version)
                self.app_dc[name] = info

    def fix_dependence(self):
        """
        整理依赖
        app_name:{
        version:"xxx",
        base_dir:"xx",
        run_user:"xx",
        service_port:"xx",
        de_app_id:[
        "1","2"
        ]
        }
        """
        app_ls = ApplicationHub.objects.filter(app_name__in=list(self.app_dc)). \
            values_list("app_name", "app_dependence", "app_version")
        app_all_dc = {}
        # 前缀匹配多版本时使用最新版本,版本需要有已安装的服务.
        # "id", "app_name", "app_version", "service"
        app_all = ApplicationHub.objects.all().values_list(
            "id", "app_name", "app_version", "service__service_instance_name"
        )
        for app in app_all:
            if app[3]:
                app_all_dc[f"{app[1]}:{app[2].split('.')[0]}"] = app[0]
                self.app_ser.setdefault(f"{app[1]}:{app[2]}", []).append(app[3])
        # 前期校验完依赖存在，因此认定当前依赖的一定会在服务列表中找寻到
        for new in app_ls:
            if self.app_dc[new[0]].get("version") != new[2]:
                continue
            for dependence in self.explain_json(new[1]):
                dependence_key = f'{dependence.get("name")}:{dependence.get("version")}'
                if app_all_dc.get(dependence_key):
                    self.app_dc[new[0]].setdefault("de_app_id", []).append(app_all_dc.get(dependence_key))

    def produce_cmd_and_exec(self, ip, agent_dir, install_args, app):
        """
        校验基本信息
        1.目录 必须
        2.用户 必须
        3.端口存在 可选
        """
        # 过滤已经纳管的
        if ip in self.service_ip_name[0].get(app, []):
            return True, ""
        salt_client = SaltClient()
        base_dir, is_success, message = \
            install_args.get("base_dir").replace('{data_path}', agent_dir), False, ""
        if base_dir:
            cmd = []
            dir_name = ["base_dir", "data_dir", "log_dir"]
            for _ in dir_name:
                dir_path = install_args.get(_).replace('{data_path}', agent_dir)
                install_args[_] = dir_path
                if dir_path:
                    cmd.append(f"test -d {dir_path}||echo {dir_path}")
            cmd = "&&".join(cmd)
            is_success, message = salt_client.cmd(target=ip, command=cmd, timeout=10)
            if message:
                return False, f"{ip}:{app}:{message}目录不存在"
        if is_success and install_args.get("run_user"):
            f_dir, c_dir = base_dir.rsplit("/", 1)
            cmd = f"ls -l {f_dir} | grep {c_dir} | head -1 | awk '{{print $3}}'"
            is_success, message = salt_client.cmd(target=ip, command=cmd, timeout=10)
            if not is_success and message != install_args.get("run_user"):
                return False, f"{ip}:{app}:{install_args.get('run_user')}与当前用户{message}不匹配"
        if is_success and install_args.get("service_port"):
            cmd = f"</dev/tcp/{ip}/{install_args.get('service_port')}"
            is_success, message = salt_client.cmd(target=ip, command=cmd, timeout=10)
            if not is_success:
                is_success, message = True, f"{ip}:{app}:{install_args.get('service_port')}" \
                                            f"端口不存在，建议判断下服务状态再纳管"
        # 合法的ip加上
        self.app_dc[app].setdefault("ip", []).append(ip)
        return is_success, message

    def get_dependence(self, app, ip):
        """
        返回依赖信息
        {
        "zookeeper_cluster1": ["zookeeper_0_1", "zookeeper_0_2"],
        "jdk_172_1": ["jdk_172_1"]
        }
        """

        dc_all = []
        de_app_id = self.app_dc[app].get("de_app_id", [])
        # 存在同一个版本多套集群的情况。
        dependence_info = Service.objects.filter(
            service__id__in=list(set(de_app_id))).values_list("service_instance_name", "cluster__cluster_name",
                                                   "service__app_name", "ip")
        alone_ser = {}
        de_dc = {}
        cluster_ser = {}
        for de in dependence_info:
            # 基础组件要求必须在同节点上
            if de[2] in self.is_base_env and de[3] != ip:
                continue
            # 多个集群取其中一个集群
            if de[1]:
                cluster_name = cluster_ser.get(de[2])
                if cluster_name and cluster_name != de[1]:
                    continue
                cluster_ser[de[2]] = de[1]
                de_dc.setdefault(de[2], []).append(de[0])
            # 多个单节点拿最新的 {"jdk":"jdk-0-1"}
            else:
                alone_ser[de[2]] = de[0]
        if alone_ser:
            for name, instance in alone_ser.items():
                dc_all.append({name: [instance]})
        for cluster_name, instance_ls in de_dc.items():
            dc_all.append({cluster_name: instance_ls})
        # 基础组件没匹配上(jdk).
        if len(set(de_app_id)) != len(dc_all):
            return False, dc_all
        return True, dc_all

    # def explain_scripts_de(self, ser_info):
    #    """
    #    检查依赖的ip是否在已纳管的服务中
    #    """
    #    for app_name, ip in ser_info["dependence"].items():
    #        app_ips = self.service_ip_name[0].get(app_name, [])
    #        if set(ip) - set(app_ips):
    #            return False, f"当前依赖{app_name}在节点处不存在{set(ip) - set(app_ips)}"
    #        if len(ip) > 1 and app_name not in self.is_base_env:
    #            is_mach = False
    #            for ip_c in self.service_cluster_ip.get(app_name, {}).values():
    #                if set(ip_c) & set(ip) == set(ip):
    #                    is_mach = True
    #            if not is_mach:
    #                return False, f"当前依赖{app_name}节点处{ip}在数据库中不存在"
    #    return True, ""

    # def dumps_scripts_args(self, instance_ls, ser_info, install_args, version, app):
    #    """
    #    校验成功数据录入
    #    """
    #    random_str = random.sample('ABCDEFGHIJKLMNQPQRSTUVWXYZ1234567890', 10)
    #    first_ip = list(instance_ls)[0]
    #    instance_name = f"{app}_{first_ip.split('.')[2]}_{first_ip.split('.')[3]}" if \
    #        len(instance_ls) == 1 else f"{list(ser_info['instance'])[0]}-cluster-{''.join(random_str)}"
    #    dependence_name = []
    #    for a_p, ip in ser_info["dependence"].items():
    #        app_dc = {a_p: []}
    #        app_all_dc = self.service_ip_name[1].get(a_p, {})
    #        for ip_d in ip:
    #            app_dc[a_p].append(app_all_dc.get(ip_d, ""))
    #        dependence_name.append(app_dc)

    #    # 类似扩容逻辑
    #    app_ips = set(self.service_ip_name[0].get(list(ser_info['instance'])[0], []))
    #    finally_ip = list(instance_ls - app_ips)
    #    self.response_ls.append({"name": app,
    #                             "ip": finally_ip,
    #                             "error": ""})
    #    self.redis_save.append({instance_name: list(instance_ls),
    #                            "dependence_instance": dependence_name,
    #                            "app_name": list(ser_info['instance'])[0],
    #                            "app_version": version,
    #                            "app_ip": finally_ip,
    #                            "error_msg": "",
    #                            "install_args": install_args})

    # @staticmethod
    # def check_dump_de(new_de, old_de):
    #    diff = set(new_de.keys()) & set(old_de.keys())
    #    if diff != set(new_de.keys()):
    #        return f"服务同集群下不同节点采集到的依赖存在不同{','.join(diff)}"
    #    for app_name, ip_list in new_de.items():
    #        # ToDo 临时修改
    #        if app_name == "zookeeper":
    #            continue
    #        if set(old_de[app_name]) & set(ip_list) != set(ip_list):
    #            return f"相同集群下下不同节点采集到的依赖服务{app_name}地址存在差异"

    # def check_cluster(self, instance_ls, instance_list_set, dependence):
    #    error_message = ""
    #    for _ in instance_list_set:
    #        if instance_ls == _[0]:
    #            error_message = self.check_dump_de(dependence, _[1])
    #            return True, error_message
    #    return False, error_message

    # def explain_scripts_res(self, message, app, install_args, ips, version, ip_list):
    #    """
    #    zookeeper:[{"ip1","ip2"},{"ip3","ip4"}]
    #    message:
    #    {"instance": {"zookeeper": ["10.0.9.33"]}, "dependence": {"jdk": ["10.0.9.33"]}}
    #    """
    #    ser_info = json.loads(message)
    # 代理节点，不存在配置文件中，但发现了安装路径的ip
    #    instance_ls = set(ser_info["instance"].get(app, [])) | set(ips)
    # 期望纳管节点不在agent节点中
    #    app_db_all_ip = set(self.service_ip_name[0].get(app, []))
    #    if len((set(ip_list) | app_db_all_ip) & instance_ls) != len(instance_ls):
    #        self.append_error(app, f"当前{app}存在问题:选择纳管节点{str(ip_list)}"
    #                               f"与期望纳管节点{instance_ls}不一致", instance_ls)
    #        return
    #    instance_list_set = self.cluster_dc.get(app, [])
    #    error_message = None
    #    if not instance_list_set:
    #        instance_list_set = self.cluster_dc[app] = [[set(instance_ls), ser_info["dependence"]]]
    #        res, message = self.explain_scripts_de(ser_info)
    #        if not res:
    #            error_message = f"当前{app}存在问题:{message}"
    #        else:
    #            self.dumps_scripts_args(instance_ls, ser_info, install_args, version, app)
    #    # 首先我们查的是其中一个。那么我们应该在收集所有信息之后再进行增减。其余应该只做校验
    #    for index, instance in enumerate(instance_list_set):
    #        # 过滤重复 查看重复依赖有无问题
    #        is_repeat, message = self.check_cluster(instance_ls, instance_list_set, ser_info["dependence"])
    #        if is_repeat:
    #            if message:
    #                error_message = message
    #            continue
    # 非重复且无交叉
    #        intersection = instance_ls & instance[0]
    #        if len(intersection) == 0:
    #            instance_list_set.append([set(instance_ls), ser_info["dependence"]])
    #            res, message = self.explain_scripts_de(ser_info)
    #            if not res:
    #                error_message = message
    #        else:
    #            error_message = f"{app}集群存在交叉现象{intersection}"
    #        # 已存在正确的要追加错误信息。
    #        if not error_message:
    #            self.dumps_scripts_args(instance_ls, ser_info, install_args, version, app)
    #    if error_message:
    #        self.append_error(app, f"当前{app}存在问题:{error_message}", instance_ls)

    def explain_common_res(self, ips_ls, app, version, install_args):
        """
        通用自研和lib纳管
        """
        for ip in ips_ls:
            # instance_name = f"{app}_{ip.split('.')[2]}_{ip.split('.')[3]}"
            # instance_name: ip,
            res, de_dc = self.get_dependence(app, ip)
            error_msg = "" if res else f"{ip}缺少基础组件如jdk，comlib等"
            redis_dc = {
                "dependence_instance": de_dc,
                "app_name": app,
                "app_version": version,
                "app_ip": [ip],
                "error_msg": error_msg,
                "install_args": install_args
            }
            if app in self.is_common:
                if self.is_common_dc.get(app):
                    self.is_common_dc[app]["app_ip"].append(ip)
                else:
                    self.is_common_dc[app] = redis_dc
                continue

            self.response_ls.append({"name": app,
                                     "ip": [ip],
                                     "error": error_msg,
                                     "exist_instance": [],
                                     "is_use_exist": False})
            self.redis_save.append(redis_dc)

    def append_error(self, app, message, ip_ls=None):
        if ip_ls:
            for k in self.response_ls:
                if list(ip_ls)[0] in k["ip"]:
                    k["error"] = message
                    return
        self.response_ls.append({"name": app,
                                 "ip": [],
                                 "error": message,
                                 "exist_instance": [],
                                 "is_use_exist": False
                                 })

    def check_component_cmd(self, install_args, app):
        """
        进一步检查，并获取依赖信息
        """
        if not install_args.get("ip") and app in self.error_ser:
            self.append_error(app, f"当前{app}组件未发现,或所发现的节点都已存在服务列表中"
                                   f"，请检查安装路径是否存在或取消扫描此服务")
            # 或需纳管的服务已全部纳管
            return True, f"当前{app}组件不支持纳管"
        ips_ls = install_args.pop("ip", [])
        version = install_args.pop("version")
        # if app in SERVICE_DISCOVERY:
        #    salt_client = SaltClient()
        #    for ip in ips_ls:
        #        cmd = f"{self.ips[ip]}/omp_salt_agent/env/bin/python3.8 " \
        #              f"{self.ips[ip]}/omp_salt_agent/scripts/{app}.py " \
        #              f"--base_dir {install_args.get('base_dir')} --local_ip {ip}"
        #        is_success, message = salt_client.cmd(target=ip, command=cmd, timeout=10)
        # mysql需要每个节点都执行完后再验证。
        #        if is_success:
        #            self.explain_scripts_res(message, app, install_args, [ip], version, ips_ls)
        #        else:
        #            self.append_error(app, f"当前{app}组件执行脚本获取参数失败{message}")
        #            return False, message
        # 此处添加结果
        #    return True, ""
        # elif app in self.is_common:
        #    self.append_error(app, f"当前{app}组件不支持纳管")
        #    return False, f"当前{app}组件不支持纳管"
        # else:
        # 查找自研组件依赖,此时的ip一定是我们需要的ip
        self.explain_common_res(ips_ls, app, version, install_args)

        # 存一下redis 生成key
        return True, ""

    def run(self):
        """
        入口函数
        """
        self.fix_service()
        self.fix_dependence()
        # 初次校验
        with ThreadPoolExecutor(THREAD_POOL_MAX_WORKERS) as executor:
            _check_list_env = []
            for ip, agent_dir in self.ips.items():
                for app, install_args in self.app_dc.items():
                    future_obj = executor.submit(
                        self.produce_cmd_and_exec, ip, agent_dir, install_args, app)
                    _check_list_env.append(future_obj)
            for future in as_completed(_check_list_env):
                is_success, message = future.result()
                if not is_success:
                    self.error_ser.add(message.split(":")[1])
                    logger.info(message)

        # 脚本和格式化校验
        with ThreadPoolExecutor(THREAD_POOL_MAX_WORKERS) as executor:
            _check_component_env = []
            for app, install_args in self.app_dc.items():
                future_obj = executor.submit(
                    self.check_component_cmd, install_args, app)
                _check_component_env.append(future_obj)
            for future in as_completed(_check_component_env):
                is_success, message = future.result()
                if not is_success:
                    logger.info(message)

        for app, info in self.is_common_dc.items():
            exist_instance = self.app_ser.get(f"{app}:{info.get('app_version', '')}", [])

            self.response_ls.append({"name": app,
                                     "ip": info.get("app_ip", []),
                                     "error": info.get("error_msg", ""),
                                     "exist_instance": exist_instance,
                                     "is_use_exist": False if len(exist_instance) == 0 else True})
            self.redis_save.append(info)

        self.redis_obj.set(
            name=str(int(time.time())),
            data=self.redis_save
        )
        is_continue = True
        for ser in self.response_ls:
            if ser.get("error", None):
                is_continue = False
        return {"ser_info": self.response_ls,
                "uuid": str(int(time.time())),
                "is_continue": is_continue}
