#!/bin/bash

# 项目卸载

CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
PROJECT_FOLDER="$(dirname ${CURRENT_DIR})"

# 解决openssl依赖的问题
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${PROJECT_FOLDER}/component/env/lib/

OMP_SCRIPT="${PROJECT_FOLDER}/scripts/omp"


# 清除omp server端保活定时任务
function clear_omp_keep_alive() {
  crontab -l|grep -v "omp all start" 2>/dev/null | crontab -
}


function uninstall() {
  ack="N"
  while [[ "$ack" == "N" ]] || [[ "$ack" == "n" ]]; do
    read -p "继续卸载请输入 Y, 中断卸载请输入N > " ack
  done
  if [[ "$ack" -ne "Y" ]]; then
   echo "卸载程序已中断，即将退出！"
   exit 1
  fi
  clear_omp_keep_alive
  bash $OMP_SCRIPT all stop
  sleep 5
  /bin/rm -rf ${PROJECT_FOLDER}
}

uninstall