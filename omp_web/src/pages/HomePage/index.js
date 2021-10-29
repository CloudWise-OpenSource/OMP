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
import ExceptionList from "./warningList";
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

  // data数据源，key聚合数据的唯一值
  const dataAggregation = (data, key)=>{
    let arr = []
    data?.map((i,d)=>{
      let isExistenceArr = arr.filter(e=>e[key] == i[key])
      console.log(isExistenceArr)
      if(isExistenceArr.length == 0){
        arr.push({
          [key]:i[key],
          severity:i.severity,
          info:[
            {
              ...i
            }
          ]
        })
      }else{
        let m = data[d]
        console.log(m)
      let idx = arr.indexOf(isExistenceArr[0])
       arr[idx] = {
        [key]:i[key],
        severity:i.severity,
        info:[
          ...arr[idx].info,
          {
            ...m,
          }
        ]
       }
      }
    })
    return arr
  }

  const queryData = () => {
    setLoading(true);
    fetchGet(apiRequest.homepage.instrumentPanel)
      .then((res) => {
        handleResponse(res, (res) => {
          setDataSource(res.data);
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
      wrapperStyle={{
        width: "100%",
        height: "calc(100% - 40px)",
        backgroundColor: "#edf0f3",
        padding: 0,
      }}
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
                        state: {
                          app_type: "1",
                        },
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
                    dataSource.component?.component_info_all_count -
                      dataSource.component?.component_info_exc_count -
                      dataSource.component?.component_info_no_monitor_count,
                    dataSource.component?.component_info_all_count
                  )}
                  trafficWay={[
                    {
                      name: "异常",
                      value: dataSource.component?.component_info_exc_count,
                    },
                    {
                      name: "未监控",
                      value:
                        dataSource.component?.component_info_no_monitor_count,
                    },
                    {
                      name: "正常",
                      value:
                        dataSource.component?.component_info_all_count -
                        dataSource.component?.component_info_exc_count -
                        dataSource.component?.component_info_no_monitor_count,
                    },
                  ]}
                />
                <div className={styles.progressInfo}>
                  <div style={{ marginBottom: 8 }}>基础组件状态</div>
                  <div
                    onClick={() =>
                      dataSource.component?.component_info_all_count &&
                      history.push({
                        pathname: "/application_management/service_management",
                        state: {
                          app_type: "0",
                        },
                      })
                    }
                    style={
                      dataSource.component?.component_info_all_count
                        ? { cursor: "pointer", marginBottom: 2 }
                        : { marginBottom: 2 }
                    }
                  >
                    组件实例：
                    <span
                      style={
                        dataSource.component?.component_info_all_count
                          ? { color: "#1890ff" }
                          : {}
                      }
                    >
                      {dataSource.component?.component_info_all_count}个
                    </span>
                  </div>
                  <div style={{ marginBottom: 2 }}>
                    未监控数：
                    <span>
                      {dataSource.component?.component_info_no_monitor_count}个
                    </span>
                  </div>
                  <div
                    style={
                      dataSource.component?.component_info_exc_count > 0
                        ? { cursor: "pointer" }
                        : {}
                    }
                    onClick={() =>
                      dataSource.component?.component_info_exc_count &&
                      history.push({
                        pathname: "/application-monitoring/exception-list",
                      })
                    }
                  >
                    异常组件：
                    <span
                      style={
                        dataSource.component?.component_info_exc_count > 0
                          ? { color: "#cf1322" }
                          : {}
                      }
                    >
                      {dataSource.component?.component_info_exc_count}个
                    </span>
                  </div>
                </div>
              </div>

              {/* 数据库 */}
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
                      value:
                        dataSource.database?.database_info_no_monitor_count,
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
                  <div style={{ marginBottom: 8 }}>数据库状态</div>
                  <div
                    onClick={() =>
                      dataSource.database?.database_info_all_count &&
                      history.push({
                        pathname: "/application_management/service_management",
                        state:{
                          label_name:"数据库"
                        }
                      })
                    }
                    style={
                      dataSource.database?.database_info_all_count
                        ? { cursor: "pointer", marginBottom: 2 }
                        : { marginBottom: 2 }
                    }
                  >
                    数据库实例：
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
                    异常实例：
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

              {/* 三方组件 */}
              {/* <div className={styles.blockOverviewItem}>
                <OmpProgress
                  percent={calcPercentage(
                    dataSource.third?.third_info_all_count -
                      dataSource.third?.third_info_exc_count -
                      dataSource.third?.third_info_no_monitor_count,
                    dataSource.third?.third_info_all_count
                  )}
                  trafficWay={[
                    {
                      name: "异常",
                      value: dataSource.third?.third_info_exc_count,
                    },
                    {
                      name: "未监控",
                      value: dataSource.third?.third_info_no_monitor_count,
                    },
                    {
                      name: "正常",
                      value:
                        dataSource.third?.third_info_all_count -
                        dataSource.third?.third_info_exc_count -
                        dataSource.third?.third_info_no_monitor_count,
                    },
                  ]}
                />
                <div className={styles.progressInfo}>
                  <div style={{ marginBottom: 8 }}>三方组件状态</div>
                  <div
                    onClick={() =>
                      dataSource.third?.third_info_all_count &&
                      history.push({
                        pathname: "/application_management/service_management",
                      })
                    }
                    style={
                      dataSource.third?.third_info_all_count
                        ? { cursor: "pointer", marginBottom: 2 }
                        : { marginBottom: 2 }
                    }
                  >
                    组件实例：
                    <span
                      style={
                        dataSource.third?.third_info_all_count
                          ? { color: "#1890ff" }
                          : {}
                      }
                    >
                      {dataSource.third?.third_info_all_count}个
                    </span>
                  </div>
                  <div style={{ marginBottom: 2 }}>
                    未监控数：
                    <span>
                      {dataSource.third?.third_info_no_monitor_count}个
                    </span>
                  </div>
                  <div
                    style={
                      dataSource.third?.third_info_exc_count > 0
                        ? { cursor: "pointer" }
                        : {}
                    }
                    onClick={() =>
                      dataSource.third?.third_info_exc_count &&
                      history.push({
                        pathname: "/application-monitoring/exception-list",
                      })
                    }
                  >
                    异常实例：
                    <span
                      style={
                        dataSource.third?.third_info_exc_count > 0
                          ? { color: "#cf1322" }
                          : {}
                      }
                    >
                      {dataSource.third?.third_info_exc_count}个
                    </span>
                  </div>
                </div>
              </div> */}
            </div>
          </div>

          <div
            style={{
              marginBottom: 10,
              backgroundColor: "#fff",
              paddingBottom: 10,
            }}
          >
            <p
              style={{
                padding: 10,
                paddingBottom: 0,
                paddingTop: 10,
                margin: 0,
                fontWeight: 500,
              }}
            >
              异常清单
            </p>
            <ExceptionList />
          </div>
          <div className={styles.pageBlock}>
            <OmpStateBlock
              // key={"serviceData"}
              // tag={"all"}
              title={"主机运行状态"}
              link={(data) => {
                history.push({
                  pathname: "/resource-management/machine-management",
                  state: {
                    ip: data.ip,
                  },
                });
              }}
              criticalLink={(data) => {
                history.push({
                  pathname: "/application-monitoring/exception-list",
                  state: {
                    ip: data.ip,
                    type: "host",
                  },
                });
              }}
              data={dataAggregation(dataSource.host?.host_info_list,"ip")}
            />
          </div>

          <div className={styles.pageBlock}>
            <OmpStateBlock
              // key={"serviceData"}
              // tag={"all"}
              link={(data) => {
                history.push({
                  pathname: "/application_management/service_management",
                  state: {
                    ip: data.ip,
                    app_type: "1",
                  },
                });
              }}
              criticalLink={(data) => {
                history.push({
                  pathname: "/application-monitoring/exception-list",
                  state: {
                    ip: data.ip,
                    type: "service",
                  },
                });
              }}
              title={"应用服务状态"}
              hasNotMonitored
              data={dataAggregation(dataSource.service?.service_info_list,"instance_name")}
            />
          </div>

          <div className={styles.pageBlock}>
            <OmpStateBlock
              // key={"serviceData"}
              // tag={"all"}
              link={(data) => {
                history.push({
                  pathname: "/application_management/service_management",
                  state: {
                    ip: data.ip,
                    app_type: "0",
                  },
                });
              }}
              criticalLink={(data) => {
                history.push({
                  pathname: "/application-monitoring/exception-list",
                  state: {
                    ip: data.ip,
                    type: "service",
                  },
                });
              }}
              hasNotMonitored
              title={"基础组件状态"}
              data={dataAggregation(dataSource.component?.component_info_list,"instance_name")}
            />
          </div>

          <div className={styles.pageBlock}>
            <OmpStateBlock
              // key={"serviceData"}
              // tag={"all"}
              link={(data) => {
                history.push({
                  pathname: "/application_management/service_management",
                  state: {
                    ip: data.ip,
                    label_name:"数据库"
                  },
                });
              }}
              criticalLink={(data) => {
                history.push({
                  pathname: "/application-monitoring/exception-list",
                  state: {
                    ip: data.ip,
                    type: "service",
                  },
                });
              }}
              hasNotMonitored
              title={"数据库状态"}
              data={dataAggregation(dataSource.database?.database_info_list,"instance_name")}
            />
          </div>

          {/* <div className={styles.pageBlock}>
            <OmpStateBlock
              // key={"serviceData"}
              // tag={"all"}
              link={(data) => {
                history.push({
                  pathname: "/application_management/service_management",
                  state: {
                    ip: data.ip,
                  },
                });
              }}
              criticalLink={(data) => {
                history.push({
                  pathname: "/application-monitoring/exception-list",
                  state: {
                    ip: data.ip,
                    type: "service",
                  },
                });
              }}
              hasNotMonitored
              title={"三方组件状态"}
              data={dataSource.third?.third_info_list}
            />
          </div> */}
        </Spin>
      </div>
    </OmpContentWrapper>
  );
};

export default React.memo(Homepage);
