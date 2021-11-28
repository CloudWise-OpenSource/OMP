import { Breadcrumb, Icon, message } from "antd";
import React, { useState, useEffect, useContext, useLayoutEffect } from "react";
import { Link, withRouter } from "react-router-dom";
import styles from "./index.module.less";
import OmpMaintenanceModal from "@/components/OmpMaintenanceModal";
//import { context } from "@/layouts";
import { fetchGet, fetchPost } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { handleResponse, refreshTime } from "@/utils/utils";
import { useSelector, useDispatch } from "react-redux";
import { AlertFilled } from "@ant-design/icons";
import { OmpMessageModal } from "@/components";
import { ExclamationCircleOutlined } from "@ant-design/icons";
import { getMaintenanceChangeAction } from "@/pages/SystemManagement/store/actionsCreators";
/*eslint-disable*/
//跟路由路径保持一致
const breadcrumbNameMap = {
  404: "404",
  //"/":"仪表盘",
  homepage: "仪表盘",
  "resource-management": "资源管理",
  "machine-management": "主机管理",
  "system-settings": "系统管理",
  "user-management": "用户管理",
  "monitoring-settings": "监控设置",
  "system-management": "系统管理",
  "alarm-log": "告警记录",
  "exception-list": "异常清单",
  "application-monitoring": "应用监控",
  application_management: "应用管理",
  app_store: "应用商店",
  "app-service-detail": "服务详情",
  "app-component-detail": "组件详情",
  "status-patrol": "状态巡检",
  "patrol-inspection-record": "巡检记录",
  "patrol-strategy": "巡检策略",
  "status-patrol-detail": "分析报告",
  service_management: "服务管理",
  application_installation: "应用安装",
  component_installation: "组件安装",
  installation: "批量安装",
  "email-settings": "邮件管理",
  "rule-center": "指标中心",
  "default-rule": "默认指标",
  "installation-record": "安装记录",
};

// 基于面包屑组件的一层封装，用于匹配当前路由地址，动态展示页面路径
const CustomBreadcrumb = withRouter(({ location }) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  //是否展示维护模式提示词
  const time = useSelector((state) => state.customBreadcrumb.time);

  const isMaintenance = useSelector(
    (state) => state.systemManagement.isMaintenance
  );

  const [closeMaintenanceModal, setCloseMaintenanceModal] = useState(false);

  //const appContext = useContext(context);

  //定义在首页时当前组件展示的时间
  const [curentTime, setCurentTime] = useState("");

  const pathSnippets = location.pathname;

  const extraBreadcrumbItems = (_, index) => {
    //console.log(pathSnippets);
    const url = pathSnippets.split("/"); //`/${pathSnippets.slice(0, index + 1).join("/")}`

    return (
      <>
        {url.map((i, idx) => {
          if (idx == url.length - 3) {
            if (!breadcrumbNameMap[url[url.length - 2]]) {
              return (
                <Breadcrumb.Item
                  style={{
                    color: "#2e7cee",
                    fontSize: 14,
                  }}
                  key={i}
                >
                  {breadcrumbNameMap[i]}
                </Breadcrumb.Item>
              );
            }
          }

          if (idx == url.length - 2) {
            // 动态路由的时候url的最后一项不一定能体现当前页面，也有可能是动态参数
            if (!breadcrumbNameMap[url[url.length - 1]]) {
              return (
                <Breadcrumb.Item
                  style={{
                    color: "#2e7cee",
                    fontSize: 14,
                  }}
                  key={i}
                >
                  {breadcrumbNameMap[i]}
                </Breadcrumb.Item>
              );
            }
          }

          if (idx == url.length - 1) {
            return (
              <Breadcrumb.Item
                style={{
                  color: "#2e7cee",
                  fontSize: 14,
                }}
                key={i}
              >
                {breadcrumbNameMap[i]}
              </Breadcrumb.Item>
            );
          } else {
            return (
              <Breadcrumb.Item
                style={{
                  color: "#8b8b8b",
                  fontSize: 14,
                }}
                key={i}
              >
                {breadcrumbNameMap[i]}
              </Breadcrumb.Item>
            );
          }
        })}
      </>
    );
  };

  //在组件初始化时获取当前时间
  useEffect(() => {
    //console.log(extraBreadcrumbItems);
    //因为在首页才会有时间展示，添加判断
    dispatch(refreshTime());
  }, []);

  // 更改维护模式
  const changeMaintain = (e) => {
    setLoading(true);
    fetchPost(apiRequest.environment.queryMaintainState, {
      body: {
        matcher_name: "env",
        matcher_value: "default",
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          //console.log(res)
          if (res.code == 0) {
            if (e) {
              message.success("已进入全局维护模式");
              dispatch(getMaintenanceChangeAction(true));
            } else {
              message.success("已退出全局维护模式");
              dispatch(getMaintenanceChangeAction(false));
            }
          }
          if (res.code == 1) {
            message.warning(res.message);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
        setCloseMaintenanceModal(false);
      });
  };

  return (
    <div className={styles.customNav}>
      {/* <div> */}
      <Breadcrumb>{extraBreadcrumbItems()}</Breadcrumb>
      {/* </div> */}
      {isMaintenance ? (
        <span className={styles.timeStampContainer}>
          <AlertFilled
            style={{ fontSize: "14px", color: "rgba(247, 207, 54)" }}
            type="alert"
            theme="filled"
          />{" "}
          当前处于维护模式, 退出维护模式请点击
          <span
            onClick={() => {
              setCloseMaintenanceModal(true);
            }}
            style={{ color: "#2e7cee", cursor: "pointer" }}
          >
            {" "}
            这里
          </span>
        </span>
      ) : (
        <span />
      )}
      {/* <span /> */}
      {/* <span className={styles.timeStampContainer} style={{ paddingRight: 0 }}>
        刷新时间: {time}
      </span> */}
      <OmpMessageModal
        visibleHandle={[closeMaintenanceModal, setCloseMaintenanceModal]}
        title={
          <span>
            <ExclamationCircleOutlined
              style={{
                fontSize: 20,
                color: "#f0a441",
                paddingRight: "10px",
                position: "relative",
                top: 2,
              }}
            />
            提示
          </span>
        }
        loading={loading}
        onFinish={() => {
          changeMaintain(false);
        }}
      >
        <div style={{ padding: "20px" }}>确定退出全局维护模式 ？</div>
      </OmpMessageModal>
    </div>
  );
});
export default React.memo(CustomBreadcrumb);
/*eslint-disable*/
