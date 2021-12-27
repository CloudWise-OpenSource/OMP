#!/bin/bash

# 项目初始化、安装

CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
THIS_SCRIPT="${CURRENT_DIR}/$(basename $0)"
PROJECT_FOLDER="$(dirname ${CURRENT_DIR})"

# 解决openssl依赖的问题
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${PROJECT_FOLDER}/component/env/lib/

PYTHON3="${PROJECT_FOLDER}/component/env/bin/python3"
OMP_SCRIPT="${PROJECT_FOLDER}/scripts/omp"

# 平台端安装逻辑
function install_omp() {
  update_conf_path="${PROJECT_FOLDER}/scripts/source/update_conf.py"
  run_user=$(whoami)
  $PYTHON3 $update_conf_path $1 $run_user
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
  $PYTHON3 $MANAGE_PATH migrate
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
    curl -H "Content-Type: application/json" -X POST -d '{"user": "admin", "password": "admin"}' "${grafana_url}" |grep 'Logged in'
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
  $PYTHON3 $update_grafana_path $1
  if [[ $? -ne 0 ]]; then
    echo "Grafana配置更新失败"
    exit 1
  fi
}

if [[ $# -eq 0 ]]; then
  echo "Please use: 'bash install.sh local_ip'"
  exit 1
else
  install_omp "$@"
  install_monitor_server "$@"
fi
