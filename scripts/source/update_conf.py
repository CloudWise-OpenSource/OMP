# -*- coding: utf-8 -*-
# Project: update_conf
# Author: jon.liu@yunzhihui.com
# Create time: 2021-09-15 14:18
# IDE: PyCharm
# Version: 1.0
# Introduction:

"""
更新配置文件
"""

import os
import sys
import yaml
import socket
from ruamel.yaml import YAML
import shutil

CURRENT_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_FOLDER = os.path.dirname(os.path.dirname(CURRENT_FILE_PATH))

config_path = os.path.join(PROJECT_FOLDER, "config/omp.yaml")
PROJECT_DATA_PATH = os.path.join(PROJECT_FOLDER, "data")
PROJECT_LOG_PATH = os.path.join(PROJECT_FOLDER, "log")

sys.path.append(os.path.join(PROJECT_FOLDER, "omp_server"))
import django
# 加载Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omp_server.settings")
django.setup()

from utils.parse_config import MONITOR_PORT

def get_config_dic():
    """
    获取配置文件详细信息
    :return:
    """
    with open(config_path, "r", encoding="utf8") as fp:
        return yaml.load(fp, Loader=yaml.FullLoader)


def update_local_ip_run_user(local_ip, run_user):
    """
    更新用户为当前操作用户
    :param local_ip:
    :param run_user:
    :return:
    """
    with open(config_path, "r", encoding="utf8") as fp:
        content = fp.read()
    my_yaml = YAML()
    code = my_yaml.load(content)
    code["global_user"] = run_user
    code["local_ip"] = local_ip
    with open(config_path, "w", encoding="utf8") as fp:
        my_yaml.dump(code, fp)


master_config_content = f"""
interface: 0.0.0.0
publish_port: PUBLISH_PORT
ret_port: RET_PORT
user: RUN_USER
enable_ssh_minions: False
presence_events: True
auto_accept: True
timeout: TIMEOUT
root_dir: {os.path.join(PROJECT_FOLDER, 'data/salt')}
conf_file: {os.path.join(PROJECT_FOLDER, 'config/salt/master')}
file_roots:
  base:
    - {os.path.join(PROJECT_FOLDER, 'package_hub')}
file_recv: True
file_recv_max_size: 524288
reactor:
  - 'salt/auth':
    - salt://reactor/auth.sls
  - 'salt/minion/*/start':
    - salt://reactor/start.sls
runner_dirs:
  - {os.path.join(PROJECT_FOLDER, 'package_hub/runners')}
"""

uwsgi_content = f"""
[uwsgi]
socket = SOCKET
chdir = {os.path.join(PROJECT_FOLDER, 'omp_server')}
wsgi-file = {os.path.join(PROJECT_FOLDER, 'omp_server/omp_server/wsgi.py')}
module = omp_server.wsgi:application
master = true
processes = PROCESSES
threads = THREADS
chmod-socket = 664
buffer-size = 65536
vacuum = true
daemonize = {os.path.join(PROJECT_FOLDER, 'logs/uwsgi.log')}
pidfile = {os.path.join(PROJECT_FOLDER, 'logs/omp_uwsgi.pid')}
home = {os.path.join(PROJECT_FOLDER, 'component/env')}
enable-threads = true
preload=true
lazy-apps=true
"""

tengine_nginx_conf = """
# user RUN_USER RUN_USER;

error_log %s;
pid %s;

worker_rlimit_nofile 102400;

events {
    use epoll;
    worker_connections 102400;
}

http {
    include mime.types;
    default_type application/octet-stream;

    #access_log on;
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
    '$status $body_bytes_sent "$http_referer" '
    '"$http_user_agent" "$http_x_forwarded_for"';
    error_page 404 /404.html;

    server_names_hash_bucket_size 128;
    client_header_buffer_size 32k;
    large_client_header_buffers 4 32k;
    client_max_body_size 500m;
    sendfile on;
    tcp_nopush on;
    keepalive_timeout 30;
    underscores_in_headers on;

    limit_req_zone $binary_remote_addr zone=one:3m rate=1r/s;
    limit_req_zone $binary_remote_addr $uri zone=two:3m rate=1r/s;

    gzip on;
    gzip_min_length 1k;
    gzip_buffers 4 16k;
    gzip_http_version 1.0;
    gzip_comp_level 2;
    gzip_types text/plain application/x-javascript text/css application/xml text/javascript application/javascript;
    gzip_vary on;

    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_temp_path %s;
    proxy_cache_path %s levels=1:2 keys_zone=cache_one:128m inactive=30m max_size=256m;
    proxy_read_timeout 1200;
    proxy_hide_header X-Powered-By;
    proxy_hide_header Server;
    server_tokens off;
    autoindex off;

    log_format access '$remote_addr $remote_user [$time_local] "$request" $status '
    'Upstream: $upstream_addr '
    'ups_resp_time: $upstream_response_time '
    'request_time: $request_time';

    include pools/*.conf;
    include vhost/*.conf;
    include jkb/*.conf;
}
""" % (
    os.path.join(PROJECT_FOLDER, "logs/tengine-error.log"),
    os.path.join(PROJECT_FOLDER, "logs/tengine.pid"),
    os.path.join(PROJECT_FOLDER, "component/tengine/temp"),
    os.path.join(PROJECT_FOLDER, "component/tengine/cache")
)

tengine_vhost_content = """
server {
    listen ACCESS_PORT;
    server_name LOCAL_IP;
    location /download-backup/ {
        alias %s/data/backup/;
    }
    location /download/ {
        alias %s/tmp/;
    }
    location /api/ {
        uwsgi_pass SOCKET;
        include %s;
    }
    location /proxy/ {
        uwsgi_pass SOCKET;
        include %s;
    }
    location / {
        root %s;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
}
""" % (
    PROJECT_FOLDER,
    PROJECT_FOLDER,
    os.path.join(PROJECT_FOLDER, "component/tengine/conf/uwsgi_params"),
    os.path.join(PROJECT_FOLDER, "component/tengine/conf/uwsgi_params"),
    os.path.join(PROJECT_FOLDER, "omp_web/dist"),
)


def check_port_access(port):
    """
    检查端口联通性
    :param port:
    :return:
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex(("127.0.0.1", int(port)))
        sock.close()
        if not result:
            return True
        return False
    except Exception as e:
        print(f"{port} Check Error {str(e)}")
        return False


def update_salt_master():
    """
    更新salt-master的配置文件
    :return:
    """
    master_file_path = os.path.join(PROJECT_FOLDER, "config/salt/master")
    settings = get_config_dic()
    publish_port = settings.get("salt_master", {}).get("publish_port")
    if not publish_port:
        publish_port = 4505
    ret_port = settings.get("salt_master", {}).get("ret_port")
    if not ret_port:
        ret_port = 4506
    timeout = settings.get("salt_master", {}).get("timeout")
    if not timeout:
        timeout = 30
    run_user = settings.get("global_user", "commonuser")
    if not run_user:
        run_user = "commonuser"
    content = master_config_content.replace(
        "PUBLISH_PORT", str(publish_port),
    ).replace(
        "RET_PORT", str(ret_port)
    ).replace(
        "RUN_USER", str(run_user)
    ).replace(
        "TIMEOUT", str(timeout)
    ).lstrip()
    if not os.path.exists(os.path.dirname(master_file_path)):
        os.makedirs(os.path.dirname(master_file_path))
    with open(master_file_path, "w", encoding="utf8") as fp:
        fp.write(content)


def update_uwsgi():
    """
    更新uwsgi的配置文件
    :return:
    """
    uwsgi_file_path = os.path.join(PROJECT_FOLDER, "config/uwsgi.ini")
    settings = get_config_dic()
    uwsgi_socket = settings.get("uwsgi", {}).get("socket")
    if not uwsgi_socket:
        uwsgi_socket = "127.0.0.1:19003"
    processes = settings.get("uwsgi", {}).get("processes")
    if not processes:
        processes = 4
    threads = settings.get("uwsgi", {}).get("threads")
    if not threads:
        threads = 2
    content = uwsgi_content.replace(
        "SOCKET", str(uwsgi_socket),
    ).replace(
        "PROCESSES", str(processes)
    ).replace(
        "THREADS", str(threads)
    ).lstrip()
    with open(uwsgi_file_path, "w", encoding="utf8") as fp:
        fp.write(content)


def update_nginx():
    """
    更新tengine的配置文件
    :return:
    """
    nginx_conf_path = os.path.join(
        PROJECT_FOLDER, "component/tengine/conf/nginx.conf")
    settings = get_config_dic()
    # run_user = settings.get("tengine", {}).get("run_user")
    run_user = settings.get("global_user", "commonuser")
    if not run_user:
        # run_user = settings.get("global_user", "cloudwise")
        run_user = "commonuser"
    content = tengine_nginx_conf.replace("RUN_USER", run_user)
    with open(nginx_conf_path, "w", encoding="utf8") as fp:
        fp.write(content)
    vhost_path = os.path.join(
        PROJECT_FOLDER, "component/tengine/conf/vhost/omp.conf")
    access_port = settings.get("tengine", {}).get("access_port")
    if not access_port:
        access_port = "18888"
    local_ip = settings.get("local_ip")
    tengine_socket = settings.get("uwsgi", {}).get("socket")
    if not tengine_socket:
        tengine_socket = "127.0.0.1:8888"
    content = tengine_vhost_content.replace(
        "ACCESS_PORT", str(access_port)
    ).replace(
        "LOCAL_IP", str(local_ip)
    ).replace(
        "SOCKET", str(tengine_socket)
    ).lstrip()
    with open(vhost_path, "w", encoding="utf8") as fp:
        fp.write(content)


def check_port_is_used():
    """
    检查端口是否被使用
    :return:
    """
    settings = get_config_dic()
    port_dic = {
        "salt_publish_port": settings.get("salt_master", {}).get("publish_port"),
        "salt_ret_port": settings.get("salt_master", {}).get("ret_port"),
        "runserver_port": settings.get("tengine", {}).get("runserver_port"),
        "tengine_port": settings.get("tengine", {}).get("access_port"),
    }
    exit_flag = False
    for key, value in port_dic.items():
        if check_port_access(value):
            print(f"{key} is already in used, please check!")
            exit_flag = True
    if exit_flag is True:
        print("Port Is Already Used!")
        sys.exit(1)


def replace_placeholder(path, placeholder_list):
    """配置文件占位符替换
    参数: path 要替换的文件路径, 占位符字典列表 [{"key":"value"}]
    """
    try:
        if not os.path.isfile(path):
            print("No such file {}".format(path))
            sys.exit(1)

        if not os.path.isfile(f'{path}.template'):
            shutil.copyfile(path, f'{path}.template')
        os.remove(path)
        shutil.copyfile(f'{path}.template', path)
        with open(path, "r") as f:
            data = f.read()
            for item in placeholder_list:
                for k, v in item.items():
                    placeholder = "${{{}}}".format(k)
                    data = data.replace(placeholder, str(v))
        with open(path, "w") as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"Updata Conf Failed, Check Error {str(e)}")
        return False


def update_prometheus():
    """
    更新uwsgi的配置文件
    :return:
    """
    prometheus_path = os.path.join(
        PROJECT_FOLDER, "component/prometheus")

    """
    更新当前服务需要更改的配置
    :return:
    """

    # 修改 conf/prometheus.yml
    MONITOR_PORT.get("prometheus",'19011')
    CW_PROMETHEUS_PORT = MONITOR_PORT.get("prometheus")
    CW_ALERTMANAGER_PORT = MONITOR_PORT.get("alertmanager")
    prometheus_yml_file = os.path.join(prometheus_path, 'conf', 'prometheus.yml')
    omp_prometheus_data_path = os.path.join(PROJECT_DATA_PATH, "prometheus")
    omp_prometheus_log_path = os.path.join(PROJECT_LOG_PATH, "prometheus")

    cpy_placeholder_script = [
        {'CW_PROMETHEUS_PORT': CW_PROMETHEUS_PORT},
        {'CW_ALERTMANAGER_PORT': CW_ALERTMANAGER_PORT},
    ]

    replace_placeholder(prometheus_yml_file, cpy_placeholder_script)

    # 修改 scripts/prometheus
    sp_placeholder_script = [
        {'OMP_PROMETHEUS_DATA_PATH': omp_prometheus_data_path},
        {'OMP_PROMETHEUS_LOG_PATH': omp_prometheus_log_path},
        {'CW_PROMETHEUS_PORT': CW_PROMETHEUS_PORT}
    ]
    if not os.path.exists(omp_prometheus_data_path):
        os.makedirs(omp_prometheus_data_path)
    if not os.path.exists(omp_prometheus_log_path):
        os.makedirs(omp_prometheus_log_path)
    sl_file = os.path.join(prometheus_path, 'scripts', 'prometheus')
    replace_placeholder(sl_file, sp_placeholder_script)


def update_grafana():
    """
    更新当前服务需要更改的配置
    :return:
    """
    grafana_path = os.path.join(PROJECT_FOLDER, "component/grafana")
    omp_grafana_log_path = os.path.join(PROJECT_LOG_PATH, "grafana")

    # 修改 conf/defaults.ini
    cdi_file = os.path.join(grafana_path, 'conf', 'defaults.ini')
    CW_GRAFANA_PORT = MONITOR_PORT.get("alertmanager",'19014')
    cdi_placeholder_script = [
        {'CW-HTTP-PORT': CW_GRAFANA_PORT},
        {'OMP_GRAFANA_LOG_PATH': omp_grafana_log_path},
    ]
    replace_placeholder(cdi_file, cdi_placeholder_script)

    # 修改 scripts/grafana
    sa_placeholder_script = [
        {'OMP_GRAFANA_LOG_PATH': omp_grafana_log_path},
    ]
    if not os.path.exists(omp_grafana_log_path):
        os.makedirs(omp_grafana_log_path)
    sa_file = os.path.join(grafana_path, 'scripts', 'grafana')
    replace_placeholder(sa_file, sa_placeholder_script)


def update_alertmanager():
    """
    更新当前服务需要更改的配置
    :return:
    """
    alertmanager_path = os.path.join(PROJECT_FOLDER, "component/alertmanager")
    omp_alertmanager_log_path = os.path.join(PROJECT_LOG_PATH, "alertmanager")
    # 修改 conf/alertmanager.yml
    EMAIL_SEND = MONITOR_PORT.get('test', '123456789@qq.com')
    SMTP_SMARTHOST = MONITOR_PORT.get('test', '1smtp.qq.com:465')
    EMAIL_SEND_USER = MONITOR_PORT.get('test', '123456789@qq.com')
    EMAIL_SEND_PASSWORD = MONITOR_PORT.get('test', 'xxxxxxxx')
    SMTP_HELLO = MONITOR_PORT.get('test', 'qq.com')
    EMAIL_ADDRESS = MONITOR_PORT.get('test', '987654321@qq.com')
    RECEIVER = MONITOR_PORT.get('test', 'commonuser')
    EMAIL_SEND_INTERVAL = MONITOR_PORT.get('test', '30m')
    WEBHOOK_URL = MONITOR_PORT.get('test', 'http://127.0.0.1:19001/api/v1/scheduler/monitor/alert')

    alertmanager_yml_file = os.path.join(alertmanager_path, 'conf', 'alertmanager.yml')

    cay_placeholder_script = [
        {'EMAIL_SEND': EMAIL_SEND},
        {'SMTP_SMARTHOST': SMTP_SMARTHOST},
        {'EMAIL_SEND_USER': EMAIL_SEND_USER},
        {'EMAIL_SEND_PASSWORD': EMAIL_SEND_PASSWORD},
        {'SMTP_HELLO': SMTP_HELLO},
        {'EMAIL_ADDRESS': EMAIL_ADDRESS},
        {'RECEIVER': RECEIVER},
        {'EMAIL_SEND_INTERVAL': EMAIL_SEND_INTERVAL},
        {'WEBHOOK_URL': WEBHOOK_URL}
    ]
    replace_placeholder(alertmanager_yml_file, cay_placeholder_script)

    # 修改 scripts/alertmanager
    CW_ALERTMANAGER_PORT = MONITOR_PORT.get('alertmanager', '19013')
    sa_placeholder_script = [
        {'OMP_ALERTMANAGER_LOG_PATH': omp_alertmanager_log_path},
        {'CW_ALERTMANAGER_PORT': CW_ALERTMANAGER_PORT}
    ]
    if not os.path.exists(omp_alertmanager_log_path):
        os.makedirs(omp_alertmanager_log_path)
    sa_file = os.path.join(alertmanager_path, 'scripts', 'alertmanager')
    replace_placeholder(sa_file, sa_placeholder_script)


def update_loki():
    """
    更新当前服务需要更改的配置
    :return:
    """
    loki_path = os.path.join(PROJECT_FOLDER, "component/loki")
    omp_loki_log_path = os.path.join(PROJECT_LOG_PATH, "loki")
    omp_loki_data_path = os.path.join(PROJECT_DATA_PATH, "loki")
    loki_retention_period = MONITOR_PORT.get('test', '168h')

    # 修改 conf/loki.yml
    CW_LOKI_PORT = MONITOR_PORT.get('loki', 19012)
    loki_yml_file = os.path.join(loki_path, 'conf', 'loki.yml')

    cly_placeholder_script = [
        {'CW_LOKI_PORT': CW_LOKI_PORT},
        {'OMP_LOKI_DATA_PATH': omp_loki_data_path}
    ]
    if not os.path.exists(omp_loki_data_path):
        os.makedirs(omp_loki_data_path)
    replace_placeholder(loki_yml_file, cly_placeholder_script)

    # 修改 scripts/loki
    sa_placeholder_script = [
        {'OMP_LOKI_LOG_PATH': omp_loki_log_path},
        {'LOKI_RETENTION_PERIOD': loki_retention_period}
    ]
    if not os.path.exists(omp_loki_log_path):
        os.makedirs(omp_loki_log_path)
    sl_file = os.path.join(loki_path, 'scripts', 'loki')
    replace_placeholder(sl_file, sa_placeholder_script)


def main(local_ip, run_user):
    """
    更新配置文件主流程
    :param local_ip: 本机的ip地址
    :param run_user: 运行用户
    :return:
    """
    print("Start Update Conf!")
    update_local_ip_run_user(local_ip, run_user)
    # check_port_is_used()
    update_salt_master()
    update_uwsgi()
    update_nginx()
    update_prometheus()
    update_grafana()
    update_alertmanager()
    update_loki()

    print("Finish Update Conf!")


if __name__ == '__main__':
    local_ip = sys.argv[1]
    run_user = sys.argv[2]
    main(local_ip, run_user)
