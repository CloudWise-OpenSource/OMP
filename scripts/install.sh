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
  bash $OMP_SCRIPT start
}

# 监控端安装逻辑
function install_monitor_server() {
  echo ""
}

if [[ $# -eq 0 ]]; then
  echo "Please use: 'bash install.sh local_ip'"
  exit 1
else
  install_omp "$@"
  install_monitor_server "$@"
fi
