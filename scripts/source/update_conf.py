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

CURRENT_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_FOLDER = os.path.dirname(os.path.dirname(CURRENT_FILE_PATH))

config_path = os.path.join(PROJECT_FOLDER, "config/omp.yaml")


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
  - 'salt/presence/change':
    - salt://reactor/stop.sls
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
    print("Finish Update Conf!")


if __name__ == '__main__':
    local_ip = sys.argv[1]
    run_user = sys.argv[2]
    main(local_ip, run_user)
