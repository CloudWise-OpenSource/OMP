import { Breadcrumb, Icon } from "antd";
import React, { useState, useEffect, useContext, useLayoutEffect } from "react";
import { Link, withRouter } from "react-router-dom";
import styles from "./index.module.less";
import OmpMaintenanceModal from "@/components/OmpMaintenanceModal";
//import { context } from "@/layouts";
import { fetchGet } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { handleResponse, refreshTime } from "@/utils/utils";
import { useSelector, useDispatch } from "react-redux";
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
  "system-management": "系统管理"
};

// 基于面包屑组件的一层封装，用于匹配当前路由地址，动态展示页面路径
const CustomBreadcrumb = withRouter(({ location }) => {
  const dispatch = useDispatch();

  //是否展示维护模式提示词
  const time = useSelector(
    (state) => state.customBreadcrumb.time
  );

  //const appContext = useContext(context);

  //定义在首页时当前组件展示的时间
  const [curentTime, setCurentTime] = useState("");

  //维护模式modal显示隐藏state
  const [maintainModal, setMaintainModal] = useState(false);

  const pathSnippets = location.pathname;

  const extraBreadcrumbItems = (_, index) => {
    //console.log(pathSnippets);
    const url = pathSnippets.split("/"); //`/${pathSnippets.slice(0, index + 1).join("/")}`

    return (
      <>
        {url.map((i, idx) => {
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
    dispatch(refreshTime())
  }, []);

  return (
    <div className={styles.customNav}>
      <Breadcrumb>{extraBreadcrumbItems()}</Breadcrumb>
      <div />
      <span className={styles.timeStampContainer} style={{ paddingRight: 0 }}>
        刷新时间: {time}
      </span>
    </div>
  );
});
export default React.memo(CustomBreadcrumb);
/*eslint-disable*/
