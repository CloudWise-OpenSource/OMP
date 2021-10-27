import { apiRequest } from "@/config/requestApi";
import { fetchGet } from "@/utils/request";
import { handleResponse } from "@/utils/utils";
import { Progress, Spin, message, Anchor } from "antd";
import React, { useEffect, useState } from "react";
import { useHistory } from "react-router-dom";
import styles from "./index.module.less";
import OmpStateBlock from "@/components/OmpStateBlock";
import { OmpProgress } from "@/components";
//import { context } from "@/Root";
import WarningList from "./warningList";
import { useSelector, useDispatch } from "react-redux";
import { OmpContentWrapper } from "@/components";

function calcPercentage(normal = 0, total = 1) {
  const percent = ((normal / total) * 100).toFixed(0);
  return isNaN(Number(percent)) ? 100 : Number(percent);
}

const Homepage = () => {
  const history = useHistory();

  const [isLoading, setLoading] = useState(false);

  const [dataSource, setDataSource] = useState({});

  const queryData = () => {
    setDataSource({
      host: {
        host_info_all_count: 2,
        host_info_exc_count: 0,
        host_info_no_monitor_count: 0,
        host_info_list: [
          {
            ip: "192.168.0.1",
            instance_name: "dosm1",
            severity: "warning",
            data: "2021-09-03 12:34:56",
            describe: "cpu崩了",
            monitor_url: "/grafana/v1/xxx",
            log_url: "/grafana/v1/xxx",
          },
          {
            ip: "192.168.0.2",
            instance_name: "dosm2",
            severity: "warning",
            data: "2021-09-03 12:34:56",
            describe: "cpu崩了",
            monitor_url: "/grafana/v1/xxx",
            log_url: "/grafana/v1/xxx",
          },
        ],
      },
      database: {
        database_info_all_count: 0,
        database_info_exc_count: 0,
        database_info_no_monitor_count: 0,
        database_info_list: [
          {
            ip: "192.168.0.3",
            instance_name: "mysql1",
            severity: "critical",
            data: "2021-09-03 12:34:56",
            describe: "mysql 挂了",
            monitor_url: "/grafana/v1/xxx",
            log_url: "/grafana/v1/xxx",
          },
          {
            ip: "192.168.0.4",
            instance_name: "redis2",
            severity: "critical",
            data: "2021-09-03 12:34:56",
            describe: "redis 挂了",
            monitor_url: "/grafana/v1/xxx",
            log_url: "/grafana/v1/xxx",
          },
        ],
      },
      service: {
        service_info_all_count: 0,
        service_info_exc_count: 0,
        service_info_no_monitor_count: 0,
        service_info_list: [],
      },
      component: {
        component_info_all_count: 0,
        component_info_exc_count: 0,
        component_info_no_monitor_count: 0,
        component_info_list: [],
      },
      third: {
        third_info_all_count: 0,
        third_info_exc_count: 0,
        third_info_no_monitor_count: 0,
        third_info_list: [],
      },
    });
    return;
    setLoading(true);
    fetchGet(apiRequest.machineManagement.hosts)
      .then((res) => {
        handleResponse(res, (res) => {
          setDataSource(res.data.results);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    queryData();
  }, []);
  console.log();
  return (
    <OmpContentWrapper
      wrapperStyle={{ width: "100%", height: "calc(100% - 40px)",backgroundColor:"#edf0f3" }}
    >
      <div className={styles.homepageWrapper}>
        {/* <OmpProgress /> */}
        <Spin spinning={isLoading}>
          <div
            className={styles.pageBlock}
            style={{
              borderRadius: 4,
              //border:"1px solid  #DCDEE5",
              marginBottom: "15px",
              backgroundColor: "white",
            }}
          >
            <div className={styles.blockTitle}>状态概览</div>
            <div
              style={{
                display: "flex",
                flexFlow: "row wrap",
                justifyContent: "space-around",
                //border: "1px solid  #DCDEE5"
              }}
              className={styles.blockContent}
            >
              {/* 主机状态 */}
              <div className={styles.blockOverviewItem}>
                <OmpProgress
                  percent={calcPercentage(
                    dataSource.host?.host_info_all_count -
                      dataSource.host?.host_info_exc_count -
                      dataSource.host?.host_info_no_monitor_count,
                    dataSource.host?.host_info_all_count
                  )}
                  trafficWay={[
                    {
                      name: "异常",
                      value: dataSource.host?.host_info_exc_count,
                    },
                    {
                      name: "未监控",
                      value: dataSource.host?.host_info_no_monitor_count,
                    },
                    {
                      name: "正常",
                      value:
                        dataSource.host?.host_info_all_count -
                        dataSource.host?.host_info_exc_count -
                        dataSource.host?.host_info_no_monitor_count,
                    },
                  ]}
                />
                <div className={styles.progressInfo}>
                  <div>主机状态</div>
                  <div
                    onClick={() =>
                      dataSource.host?.host_info_all_count &&
                      history.push({
                        pathname: "/resource-management/machine-management",
                      })
                    }
                    style={
                      dataSource.host?.host_info_all_count
                        ? { cursor: "pointer" }
                        : {}
                    }
                  >
                    主机总数：
                    <span
                      style={
                        dataSource.host?.host_info_all_count
                          ? { color: "#1890ff" }
                          : {}
                      }
                    >
                      {dataSource.host?.host_info_all_count}个
                    </span>
                  </div>
                  <div
                    style={
                      dataSource.host?.host_info_exc_count > 0
                        ? { cursor: "pointer" }
                        : {}
                    }
                    onClick={() =>
                      dataSource.host?.host_info_exc_count &&
                      history.push({
                        pathname: "/application-monitoring/exception-list",
                      })
                    }
                  >
                    异常主机：
                    <span
                      style={
                        dataSource.host?.host_info_exc_count > 0
                          ? { color: "#cf1322" }
                          : {}
                      }
                    >
                      {dataSource.host?.host_info_exc_count}个
                    </span>
                  </div>
                </div>
              </div>

              {/* 应用服务 */}
              <div className={styles.blockOverviewItem}>
                <OmpProgress
                  percent={calcPercentage(
                    dataSource.service?.service_info_all_count -
                      dataSource.service?.service_info_exc_count -
                      dataSource.service?.service_info_no_monitor_count,
                    dataSource.service?.service_info_all_count
                  )}
                  trafficWay={[
                    {
                      name: "异常",
                      value: dataSource.service?.service_info_exc_count,
                    },
                    {
                      name: "未监控",
                      value: dataSource.service?.service_info_no_monitor_count,
                    },
                    {
                      name: "正常",
                      value:
                        dataSource.service?.service_info_all_count -
                        dataSource.service?.service_info_exc_count -
                        dataSource.service?.service_info_no_monitor_count,
                    },
                  ]}
                />
                <div className={styles.progressInfo}>
                  <div style={{ marginBottom: 8 }}>应用服务状态</div>
                  <div
                    onClick={() =>
                      dataSource.service?.service_info_all_count &&
                      history.push({
                        pathname: "/application_management/service_management",
                      })
                    }
                    style={
                      dataSource.service?.service_info_all_count
                        ? { cursor: "pointer", marginBottom: 2 }
                        : { marginBottom: 2 }
                    }
                  >
                    服务总数：
                    <span
                      style={
                        dataSource.service?.service_info_all_count
                          ? { color: "#1890ff" }
                          : {}
                      }
                    >
                      {dataSource.service?.service_info_all_count}个
                    </span>
                  </div>
                  <div style={{ marginBottom: 2 }}>
                    未监控数：
                    <span>
                      {dataSource.service?.service_info_no_monitor_count}个
                    </span>
                  </div>
                  <div
                    style={
                      dataSource.service?.service_info_exc_count > 0
                        ? { cursor: "pointer" }
                        : {}
                    }
                    onClick={() =>
                      dataSource.service?.service_info_exc_count &&
                      history.push({
                        pathname: "/application-monitoring/exception-list",
                      })
                    }
                  >
                    异常服务：
                    <span
                      style={
                        dataSource.service?.service_info_exc_count > 0
                          ? { color: "#cf1322" }
                          : {}
                      }
                    >
                      {dataSource.service?.service_info_exc_count}个
                    </span>
                  </div>
                </div>
              </div>

               {/* 基础组件 */}
               <div className={styles.blockOverviewItem}>
                <OmpProgress
                  percent={calcPercentage(
                    dataSource.database?.database_info_all_count -
                      dataSource.database?.database_info_exc_count -
                      dataSource.database?.database_info_no_monitor_count,
                    dataSource.database?.database_info_all_count
                  )}
                  trafficWay={[
                    {
                      name: "异常",
                      value: dataSource.database?.database_info_exc_count,
                    },
                    {
                      name: "未监控",
                      value: dataSource.database?.database_info_no_monitor_count,
                    },
                    {
                      name: "正常",
                      value:
                        dataSource.database?.database_info_all_count -
                        dataSource.database?.database_info_exc_count -
                        dataSource.database?.database_info_no_monitor_count,
                    },
                  ]}
                />
                <div className={styles.progressInfo}>
                  <div style={{ marginBottom: 8 }}>基础组件状态</div>
                  <div
                    onClick={() =>
                      dataSource.database?.database_info_all_count &&
                      history.push({
                        pathname: "/application_management/service_management",
                      })
                    }
                    style={
                      dataSource.database?.database_info_all_count
                        ? { cursor: "pointer", marginBottom: 2 }
                        : { marginBottom: 2 }
                    }
                  >
                    组件实例：
                    <span
                      style={
                        dataSource.database?.database_info_all_count
                          ? { color: "#1890ff" }
                          : {}
                      }
                    >
                      {dataSource.database?.database_info_all_count}个
                    </span>
                  </div>
                  <div style={{ marginBottom: 2 }}>
                    未监控数：
                    <span>
                      {dataSource.database?.database_info_no_monitor_count}个
                    </span>
                  </div>
                  <div
                    style={
                      dataSource.database?.database_info_exc_count > 0
                        ? { cursor: "pointer" }
                        : {}
                    }
                    onClick={() =>
                      dataSource.database?.database_info_exc_count &&
                      history.push({
                        pathname: "/application-monitoring/exception-list",
                      })
                    }
                  >
                    异常组件：
                    <span
                      style={
                        dataSource.database?.database_info_exc_count > 0
                          ? { color: "#cf1322" }
                          : {}
                      }
                    >
                      {dataSource.database?.database_info_exc_count}个
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* <div style={{marginBottom:10,backgroundColor:"#fff",paddingBottom:10}}>
          <p style={{padding:10,paddingTop:10,margin:0,fontWeight:500}}>异常清单</p>
          <WarningList />
        </div>
        
        <div className={styles.pageBlock}>
          <OmpStateBlock
            key={"serviceData"}
            tag={"all"}
            title={"自有服务状态"}
            data={serviceData.service_detail}
          />
        </div>

        <div className={styles.pageBlock}>
          <OmpStateBlock
            key={"componentData"}
            tag={"basic"}
            title={"自有组件状态"}
            data={componentData.service_detail}
          />
        </div>

        <div className={styles.pageBlock}>
          <OmpStateBlock
            key={"externalData"}
            tag={"thirdParty"}
            title={"三方组件状态"}
            data={externalData.service_detail}
          />
        </div>

        <div className={styles.pageBlock}>
          <OmpStateBlock
            key={"databaseData"}
            tag={"database"}
            title={"数据库状态"}
            data={databaseData.service_detail}
          />
        </div>

        <div className={styles.pageBlock} >
          <OmpStateBlock
            key={"hostData"}
            tag={"hostData"}
            title={"主机状态"}
            data={hostData.host_detail}
          />
        </div> */}
        </Spin>
      </div>
    </OmpContentWrapper>
  );
};

export default React.memo(Homepage);
