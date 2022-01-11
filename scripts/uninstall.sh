#!/bin/bash

CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
THIS_SCRIPT="${CURRENT_DIR}/$(basename $0)"
PROJECT_FOLDER="$(dirname ${CURRENT_DIR})"

#解决openssl依赖的问题
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${PROJECT_FOLDER}/component/env/lib/

PYTHON3="${PROJECT_FOLDER}/component/env/bin/python3"
OMP_SCRIPT="${PROJECT_FOLDER}/scripts/omp"
UNINSTALL_SERVICE_PATH="${PROJECT_FOLDER}/scripts/source/uninstall_services.py"

function uninstall_service() {
  for i in $(seq 1 3)
  do
    read -p "删除已部署的服务?确认请第${i}请再次输入delete or DELETE > " ask
    if [[ "$ask" == "delete" ]] || [[ "$ask" == "DELETE" ]];then
      continue
    fi
    exit 1
  done
  $PYTHON3 $UNINSTALL_SERVICE_PATH
  if [[ $? -ne 0 ]];then
    echo "卸载已部署的服务失败"
    exit 1
  fi
  echo "卸载已部署的服务成功"
}

uninstall_service "$@"
