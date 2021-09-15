#!/bin/bash

# 项目初始化、安装

CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
THIS_SCRIPT="${CURRENT_DIR}/$(basename $0)"
PROJECT_FOLDER="$(dirname ${CURRENT_DIR})"

# 解决openssl依赖的问题
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${PROJECT_FOLDER}/component/env/lib/

# 平台端安装逻辑
function install_omp() {

}

# 监控端安装逻辑
function install_monitor_server() {

}

install_omp
install_monitor_server
