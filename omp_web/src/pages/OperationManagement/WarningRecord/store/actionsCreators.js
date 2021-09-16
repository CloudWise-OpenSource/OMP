/*
 * @Author: your name
 * @Date: 2021-06-13 16:00:50
 * @LastEditTime: 2021-06-21 15:47:47
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: /omp_fontend/src/pages/ProductsManagement/VersionManagement/InstallationDetails/store/actionsCreators.js
 */
import * as actionTypes from "./constants";
import { fetchGet } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";

export const getAbnormalHostNumberChangeAction = async () => {
    //为了获得服务总数用于展示
    //return (dispatch)=>{
    let res = await fetchGet(apiRequest.operationManagement.alertRecord, {
      params: {
        query_type: "normal",
        alert_type: "host",
        page_num: 1,
        page_size: 10,
      },
    });
    //console.log(res.data.data,"red")
    if(res)
    return {
      type: actionTypes.CHANGE_ABNORMALHOSTNUMBER,
      payload: {
        host: res.data.data.total,
      },
    };
  };

export const getAbnormalServiceNumberChangeAsyncAction = async () => {
  //为了获得服务总数用于展示
  //return (dispatch)=>{
  let res = await fetchGet(apiRequest.operationManagement.alertRecord, {
    params: {
      query_type: "normal",
      alert_type: "service",
      page_num: 1,
      page_size: 10,
    },
  });
  //console.log(res.data.data,"red")
  if(res)
  return {
    type: actionTypes.CHANGE_ABNORMALSERVICENUMBER,
    payload: {
      service: res.data.data.total,
    },
  };
};
