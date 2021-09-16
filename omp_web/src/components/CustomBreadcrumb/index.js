import { Breadcrumb, Icon } from "antd";
import React, { useState, useEffect, useContext, useLayoutEffect } from "react";
import { Link, withRouter } from "react-router-dom";
import styles from "./index.module.less";
import moment from "moment";
import OmpMaintenanceModal from "@/components/OmpMaintenanceModal";
import { context } from "@/layouts";
import { fetchGet } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { handleResponse } from "@/utils/utils";
import { useSelector, useDispatch } from "react-redux";
import { getMaintenanceChangeAction } from "./store/actionsCreators";
/*eslint-disable*/
//跟路由路径保持一致
const breadcrumbNameMap = {
  "/404": "404",
  //"/":"仪表盘",
  "/homepage": "仪表盘",
  "/machine-management": "主机管理",
  "/machine-management/list": "主机列表",
  // "/machine-management/used": "已使用",
  // "/machine-management/unused": "未使用",

  "/products-management": "产品管理",
  "/products-management/service": "服务管理",
  "/products-management/version": "版本管理",
  "/products-management/version/upload": "环境纳管",
  "/products-management/version/rapidDeployment": "快速部署",
  "/products-management/ProductWarehouse": "产品仓库",

  "/operation-management": "运维管理",
  "/operation-management/warnings": "异常清单",
  "/operation-management/waring-records": "告警记录",
  "/operation-management/self-healing": "自愈记录",
  "/operation-management/trend-analyze": "趋势分析",
  "/operation-management/report": "巡检报告",
  "/operation-management/report/deep": "深度分析",
  "/operation-management/report/business": "业务巡检",
  "/operation-management/report/overall": "综合巡检",
  "/operation-management/report/machine": "主机巡检",
  "/operation-management/report/component": "组件巡检",

  "/actions-record": "操作记录",
  "/actions-record/login": "登录日志",
  "/actions-record/system": "系统记录",

  "/product-settings": "产品设置",
  "/product-settings/upload": "数据上传",

  "/system-settings": "系统设置",
  "/system-settings/users": "用户管理",
  "/system-settings/users/users": "用户管理",
  "/system-settings/users/roles": "角色管理",

  "/system-settings/system": "系统设置",
  "/system-settings/system/patrol": "巡检设置",
  "/system-settings/system/warnings": "告警阀值",
};

// 基于面包屑组件的一层封装，用于匹配当前路由地址，动态展示页面路径
const CustomBreadcrumb = withRouter(({ location }) => {
  const dispatch = useDispatch();

  //是否展示维护模式提示词
  const isMaintenance = useSelector(state => state.customBreadcrumb.isMaintenance);

  const appContext = useContext(context);

  //定义在首页时当前组件展示的时间
  const [curentTime, setCurentTime] = useState("");

  //维护模式modal显示隐藏state
  const [maintainModal, setMaintainModal] = useState(false);

  const pathSnippets = location.pathname//location.pathname.split("/").filter((i) => i);

  // 之前的面包屑显示逻辑
  // const extraBreadcrumbItems = pathSnippets.map((_, index) => {
  //   const url = `/${pathSnippets.slice(0, index + 1).join("/")}`;
  //   return (
  //     <Breadcrumb.Item
  //       style={
  //         index === pathSnippets.length - 1
  //           ? { color: "#1A90FF" }
  //           : { color: "#555A79" }
  //       }
  //       key={url}
  //     >
  //       {breadcrumbNameMap[url]}
  //     </Breadcrumb.Item>
  //   );
  // });

  const extraBreadcrumbItems = (_,index) => {
    //console.log(pathSnippets);
    const url = pathSnippets//`/${pathSnippets.slice(0, index + 1).join("/")}`
    return (
      <Breadcrumb.Item
        style={{
          color:"black",
          fontSize:14
        }
          // index === pathSnippets.length - 1
          //   ? { color: "#1A90FF" }
          //   : { color: "#555A79" }
        }
        key={url}
      >
        {breadcrumbNameMap[url]}
      </Breadcrumb.Item>
    );
  };

  //在组件初始化时获取当前时间
  useEffect(() => {
    //console.log(extraBreadcrumbItems);
    //因为在首页才会有时间展示，添加判断
    setCurentTime(moment().format("YYYY-MM-DD HH:mm:ss"));
  }, []);

  // useLayoutEffect(() => {
  //   if(appContext.state.value){
  //   fetchGet(apiRequest.systemSettings.modeInfoChange).then((res) => {
  //     res = res.data
  //     handleResponse(res, () => {
  //       if (res.code === 0) {
  //         dispatch(getMaintenanceChangeAction(res.data.used))
  //       }
  //     });
  //   });
  //   }
  // }, [appContext.state.value]);

  return (
    <div className={styles.customNav}>
      <Breadcrumb>{extraBreadcrumbItems()}</Breadcrumb>
      <div />
      {location.pathname?.includes("/homepage") ? (
        <>
          {isMaintenance && (
            <span
              className={styles.timeStampContainer}
              style={{ paddingRight: 20, position: "relative", left: -75 }}
            >
              <Icon style={{ fontSize: "14px" }} type="alert" theme="filled" />{" "}
              当前处于维护模式, 退出维护模式请点击
              <span
                onClick={() => {
                  setMaintainModal(true);
                }}
                style={{ color: "#3e91f7", cursor: "pointer" }}
              >
                {" "}
                这里
              </span>
            </span>
          )}
          <span
            className={styles.timeStampContainer}
            style={{ paddingRight: 20 }}
          >
            刷新时间: {curentTime}
          </span>
        </>
      ) : (
        isMaintenance && (
          <span
            className={styles.timeStampContainer}
            style={{ paddingRight: 20 }}
          >
            <Icon style={{ fontSize: "14px" }} type="alert" theme="filled" />{" "}
            当前处于维护模式, 退出维护模式请点击
            <span
              onClick={() => {
                setMaintainModal(true);
              }}
              style={{ color: "#3e91f7", cursor: "pointer" }}
            >
              {" "}
              这里
            </span>
          </span>
        )
      )}
      {/* <OmpMaintenanceModal
        control={[maintainModal, setMaintainModal]}
        used = {false}
      /> */}
    </div>
  );
});
export default React.memo(CustomBreadcrumb);
/*eslint-disable*/
