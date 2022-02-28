#!/bin/bash

# 项目初始化、安装

CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
THIS_SCRIPT="${CURRENT_DIR}/$(basename $0)"
PROJECT_FOLDER="$(dirname ${CURRENT_DIR})"

# 解决openssl依赖的问题
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${PROJECT_FOLDER}/component/env/lib/

PYTHON3="${PROJECT_FOLDER}/component/env/bin/python3"
OMP_SCRIPT="${PROJECT_FOLDER}/scripts/omp"
TMP_LOG_PATH="${PROJECT_FOLDER}/tmp/install_omp.log"
TMP_CRONTAB_TXT_PATH="${PROJECT_FOLDER}/tmp/crontab.txt"

test -d "${PROJECT_FOLDER}/tmp" || mkdir "${PROJECT_FOLDER}/tmp"

get_local_ip() {
  ips=$(ip a | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v "127.0.0.1")
  k=0
  echo "通过命令获取本机ip如下："
  for ip in $ips; do
    ip_list[k]=$ip
    echo "若选择ip: $ip 请输入id: $k"
    (( k++ ))
  done
  echo ""
  read -p "请选择本机ip对应的id，如果ip不在上述输出中请输入N > " index
  if [[ $index == "N" ]] || [[ $index == "n" ]]; then
    read -p "请输入本机ip:" local_ip
    local_ip_grep=$(echo "$local_ip" | grep -oP "([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})")
    if [ "$local_ip_grep" != "$local_ip" ]; then
      echo "ip: $local_ip 格式不正确！"
      exit 1
    fi
  elif [ -z "$(echo $index| sed -n "/^[0-9]\+$/p")" ];then
    echo "输入的id: $index 非法,请重新执行命令选择！"
    exit 1
  else
    local_ip=${ip_list[$index]}
    if [ ! -n "$local_ip" ]; then
      echo "选择的ip不存在!"
      exit 1
    fi
  fi

}

function echo_omp_url() {
    echo " "
    echo "=========OMP平台访问信息================"
    echo "平台访问地址：http://$local_ip:19001"
    echo "平台默认用户：admin"
    echo "平台默认密码：Common@123"
    echo "======================================="
    echo " "
}

# 平台端安装逻辑
function install_omp() {
  ack="N"
  while [[ "$ack" == "N" ]] || [[ "$ack" == "n" ]]; do
    get_local_ip
    read -p "确认当前主机ip为【$local_ip】请输入 Y, 重新选择请输入N > " ack
  done
  update_conf_path="${PROJECT_FOLDER}/scripts/source/update_conf.py"
  run_user=$(whoami)
  $PYTHON3 $update_conf_path $local_ip $run_user
  if [[ $? -ne 0 ]]; then
    echo "OMP配置更新失败"
    exit 1
  fi
  install_mysql_redis_path="${PROJECT_FOLDER}/scripts/source/install_mysql_redis.py"
  $PYTHON3 $install_mysql_redis_path
  if [[ $? -ne 0 ]]; then
   echo "mysql+redis安装失败"
   exit 1
  fi
  MANAGE_PATH="${PROJECT_FOLDER}/omp_server/manage.py"
  $PYTHON3 $MANAGE_PATH migrate >> $TMP_LOG_PATH
  UPDATE_DATA_PATH="${PROJECT_FOLDER}/scripts/source/update_data.py"
  $PYTHON3 $UPDATE_DATA_PATH
  bash $OMP_SCRIPT all start
}

function check_grafana_up() {
  CONF_PATH="${PROJECT_FOLDER}/config/omp.yaml"
  port_flag=$(cat ${CONF_PATH} |grep 'grafana: ' | tr "grafana:" " ")
  port=${port_flag// /}
  grafana_url="http://127.0.0.1:${port}/proxy/v1/grafana/login"
  # 等待grafana在5分钟内启动成功
  i=0
  while [ $i -le 10 ]
  do
    curl -s -H "Content-Type: application/json" -X POST -d '{"user": "admin", "password": "admin"}' "${grafana_url}" |grep 'Logged in'
    if [[ $? -eq 0 ]]; then
      return 0
    fi
    sleep 30
    if [[ $i -eq 5 ]]; then
      bash $OMP_SCRIPT grafana start
    fi
    let i++
  done
  echo "Grafana start failed in 300s, please check!"
  exit 1
}

# 监控端安装逻辑
function install_monitor_server() {
  bash $OMP_SCRIPT grafana start
  # 确认grafana能够成功启动后，再更新grafana的数据
  check_grafana_up
  update_grafana_path="${PROJECT_FOLDER}/scripts/source/update_grafana.py"
  $PYTHON3 $update_grafana_path $local_ip
  if [[ $? -ne 0 ]]; then
    echo "Grafana配置更新失败"
    exit 1
  fi
}

# 添加omp server端保活定时任务
function omp_keep_alive() {
  crontab -l 2>/dev/null > $TMP_CRONTAB_TXT_PATH
  echo "*/5 * * * * bash $OMP_SCRIPT all start &>/dev/null" >> $TMP_CRONTAB_TXT_PATH
  oka_crontab=$(crontab -l | grep "omp all start")
  if test -z "$oka_crontab"
  then
    crontab < $TMP_CRONTAB_TXT_PATH
    echo "omp server端保活任务添加成功"
  else
    echo "omp server端保活任务添加成功"
  fi
}


install_omp "$@"
install_monitor_server "$@"
omp_keep_alive
echo_omp_url
