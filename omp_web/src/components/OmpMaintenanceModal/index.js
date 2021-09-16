/*
 * @Author: your name
 * @Date: 2021-06-21 11:41:47
 * @LastEditTime: 2021-06-22 19:50:32
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: /ompWeb/src/components/OmpMaintenanceModal/OmpMaintenanceModal.js
 */
import React, { useState } from "react";
import OmpModal from "@/components/OmpModal";
import { useDispatch } from "react-redux";
import { handleResponse } from "@/utils/utils";
//import { getMaintenanceChangeAction } from "@/layouts/CustomBreadcrumb/store/actionsCreators";
import { fetchPut } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
//import updata from "@/stores/globalStore";

const OmpMaintenanceModal = ({ control, used }) => {
  const dispatch = useDispatch();
  const [isModalLoading, setIsModalLoading] = useState(false);
  const changeMaintenance = () => {
    setIsModalLoading(true);
    fetchPut(apiRequest.systemSettings.modeInfoChange, {
      body: {
        used: used,
        //env_id: Number(updata()().value),
      },
    })
      .then((res) => {
        res = res.data
        handleResponse(res, () => {
          if (res.code === 0) {
            //dispatch(getMaintenanceChangeAction(res.data.used));
            control[1](false);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setIsModalLoading(false);
      });
  };
  return (
    <div>omp</div>
    // <OmpModal
    //   visibleHandle={control}
    //   title={used?"进入维护模式":"退出维护模式"}
    //   loading = {isModalLoading}
    //   onOk={() => {
    //     changeMaintenance();
    //   }}
    // >
    //   <span>{used?"当该环境处于维护模式时,该环境发出的警报将会被抑制。":"该环境退出维护模式,则从该环境内发出的警报将不会再被抑制。"}</span>
    // </OmpModal>
  );
};

export default OmpMaintenanceModal;
