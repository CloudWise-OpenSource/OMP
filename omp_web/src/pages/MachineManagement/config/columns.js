import { nonEmptyProcessing, renderDisc } from "@/utils/utils";
import { DownOutlined, DesktopOutlined } from "@ant-design/icons";
import { Dropdown, Menu, Drawer, Tooltip, Spin, Timeline } from "antd";
import moment from "moment";
import styles from "../index.module.less";
import { useSelector } from "react-redux";
import { useRef } from "react";

const colorConfig = {
  normal: null,
  warning: "#ffbf00",
  critical: "#f04134",
};

export const DetailHost = ({
  isShowDrawer,
  setIsShowDrawer,
  loading,
  data,
  baseEnv,
}) => {
  // 视口宽度
  const viewHeight = useSelector((state) => state.layouts.viewSize.height);
  // 组件图片字符串
  const componentImgStr = `<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"><svg t="1634633143436" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="2388" xmlns:xlink="http://www.w3.org/1999/xlink" width="200" height="200"><defs><style type="text/css"></style></defs><path d="M882.521 282.988L527.534 78.127c-8.98-5.219-20.146-5.219-29.127 0L143.42 282.988c-8.98 5.219-14.563 14.806-14.563 25.244v409.842c0 10.437 5.583 20.025 14.563 25.244L498.407 948.3c4.491 2.548 9.588 3.884 14.563 3.884s10.073-1.334 14.563-3.884L882.52 743.318c8.98-5.219 14.563-14.806 14.563-25.244V308.232c0-10.437-5.583-20.025-14.563-25.244zM838.83 701.326L512.971 889.438 187.112 701.326V325.101l325.859-188.112L838.83 325.101v376.225z" p-id="2389"></path><path d="M270.124 383.476c-8.01 13.957-3.277 31.797 10.681 39.807l202.676 116.994v231.439c0 16.142 12.986 29.127 29.127 29.127s29.127-12.986 29.127-29.127V540.641l203.404-117.479c13.957-8.01 18.69-25.851 10.681-39.807s-25.851-18.69-39.807-10.681L512.973 489.91l-203.04-117.236c-13.957-8.01-31.676-3.155-39.807 10.801z" p-id="2390"></path></svg>`;

  const wrapperRef = useRef(null);
  return (
    <Drawer
      title={
        <div style={{ display: "flex" }}>
          <DesktopOutlined style={{ position: "relative", top: 3, left: -5 }} />
          主机详细信息面板
          <span style={{ paddingLeft: 30, fontWeight: 400, fontSize: 15 }}>
            IP: {isShowDrawer.record.ip}
          </span>
        </div>
      }
      placement="right"
      closable={true}
      width={`calc(100% - 200px)`}
      style={{
        height: "calc(100%)",
        paddingTop: "60px",
      }}
      onClose={() => {
        setIsShowDrawer({
          ...isShowDrawer,
          isOpen: false,
        });
      }}
      visible={isShowDrawer.isOpen}
      bodyStyle={{
        padding: 10,
        //paddingLeft:10,
        backgroundColor: "#e7e9f0", //"#f4f6f8"
        height: "calc(100%)",
      }}
      destroyOnClose={true}
    >
      <div
        style={{ height: "calc(100% - 65px)", width: "100%", display: "flex" }}
      >
        <div
          style={{
            height: "100%",
            width: "100%",
            //border: "solid 1px rgb(220,220,220)",
            borderRadius: "5px",
            backgroundColor: "#fff",
            flex: 4,
            padding: 20,
          }}
        >
          <div style={{ paddingBottom: 35, fontSize: 15, fontWeight: 500 }}>
            基本信息
          </div>
          <div
            style={{
              display: "flex",
              //paddingTop: 15,
              paddingBottom: 5,
              borderBottom: "solid 1px rgb(220,220,220)",
            }}
          >
            <div style={{ flex: 1 }}>实例名称</div>
            <div style={{ flex: 1 }}>{isShowDrawer.record.instance_name}</div>
          </div>
          <div
            style={{
              display: "flex",
              paddingTop: 15,
              paddingBottom: 5,
              borderBottom: "solid 1px rgb(220,220,220)",
            }}
          >
            <div style={{ flex: 1 }}>HOSTNAME</div>
            <div style={{ flex: 1 }}>
              {nonEmptyProcessing(isShowDrawer.record.host_name)}
            </div>
          </div>
          <div
            style={{
              display: "flex",
              paddingTop: 15,
              paddingBottom: 5,
              borderBottom: "solid 1px rgb(220,220,220)",
            }}
          >
            <div style={{ flex: 1 }}>IP地址</div>
            <div style={{ flex: 1 }}>{isShowDrawer.record.ip}</div>
          </div>
          <div
            style={{
              display: "flex",
              paddingTop: 15,
              paddingBottom: 5,
              borderBottom: "solid 1px rgb(220,220,220)",
            }}
          >
            <div style={{ flex: 1 }}>SSH端口</div>
            <div style={{ flex: 1 }}>{isShowDrawer.record.port}</div>
          </div>
          <div
            style={{
              display: "flex",
              paddingTop: 15,
              paddingBottom: 5,
              borderBottom: "solid 1px rgb(220,220,220)",
            }}
          >
            <div style={{ flex: 1 }}>用户名</div>
            <div style={{ flex: 1 }}>{isShowDrawer.record.username}</div>
          </div>
          <div
            style={{
              display: "flex",
              paddingTop: 15,
              paddingBottom: 5,
              borderBottom: "solid 1px rgb(220,220,220)",
            }}
          >
            <div style={{ flex: 1 }}>系统</div>
            <div style={{ flex: 1 }}>{isShowDrawer.record.operate_system}</div>
          </div>
          <div
            style={{
              display: "flex",
              paddingTop: 15,
              paddingBottom: 5,
              borderBottom: "solid 1px rgb(220,220,220)",
            }}
          >
            <div style={{ flex: 1 }}>CPU</div>
            <div style={{ flex: 1 }}>
              {nonEmptyProcessing(isShowDrawer.record.cpu)} c
            </div>
          </div>
          <div
            style={{
              display: "flex",
              paddingTop: 15,
              paddingBottom: 5,
              borderBottom: "solid 1px rgb(220,220,220)",
            }}
          >
            <div style={{ flex: 1 }}>内存</div>
            <div style={{ flex: 1 }}>
              {nonEmptyProcessing(isShowDrawer.record.memory)} G
            </div>
          </div>
          <div
            style={{
              display: "flex",
              paddingTop: 15,
              paddingBottom: 5,
              borderBottom: "solid 1px rgb(220,220,220)",
            }}
          >
            <div style={{ flex: 1 }}>硬盘</div>
            <div style={{ flex: 1 }}>
              {isShowDrawer.record.disk
                ? Object.keys(isShowDrawer.record.disk).map((item) => (
                    <div
                      key={item}
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                      }}
                    >
                      <span style={{ width: "65%" }}>{item}</span>
                      <span style={{ width: "35%" }}>
                        {isShowDrawer.record.disk[item]} G
                      </span>
                    </div>
                  ))
                : "-"}
            </div>
          </div>
          <div
            style={{
              display: "flex",
              paddingTop: 15,
              paddingBottom: 5,
              borderBottom: "solid 1px rgb(220,220,220)",
            }}
          >
            <div style={{ flex: 1 }}>创建时间</div>
            <div style={{ flex: 1 }}>
              {moment(isShowDrawer.record.created).format(
                "YYYY-MM-DD HH:mm:ss"
              )}
            </div>
          </div>
          <div
            style={{
              display: "flex",
              paddingTop: 15,
              paddingBottom: 5,
              borderBottom: "solid 1px rgb(220,220,220)",
            }}
          >
            <div style={{ flex: 1 }}>维护模式</div>
            <div style={{ flex: 1 }}>
              {isShowDrawer.record.is_maintenance ? "是" : "否"}
            </div>
          </div>
          <div
            style={{
              display: "flex",
              paddingTop: 15,
              paddingBottom: 5,
              borderBottom: "solid 1px rgb(220,220,220)",
            }}
          >
            <div style={{ flex: 1 }}>主机初始化</div>
            <div style={{ flex: 1 }}>
              {renderInitStatue(isShowDrawer.record.init_status)}
            </div>
          </div>
        </div>
        <div
          style={{
            height: "100%",
            width: "100%",
            flex: 7,
            marginLeft: 20,
            display: "flex",
            flexWrap: "wrap",
          }}
        >
          <div
            style={{
              height: "100%",
              width: "49%",
              //border: "solid 1px rgb(220,220,220)",
              borderRadius: "5px",
              backgroundColor: "#fff",
              height: 200,
              padding: 20,
            }}
          >
            <div style={{ paddingBottom: 35, fontSize: 15, fontWeight: 500 }}>
              Agent状态
            </div>
            <div style={{ display: "flex", paddingTop: 15, paddingBottom: 15 }}>
              <div style={{ flex: 1 }}>主机Agent</div>
              <div style={{ flex: 1 }}>
                {renderStatus(isShowDrawer.record.host_agent)}
              </div>
            </div>
            <div style={{ display: "flex", paddingTop: 15, paddingBottom: 15 }}>
              <div style={{ flex: 1 }}>监控Agent</div>
              <div style={{ flex: 1 }}>
                {renderStatus(isShowDrawer.record.monitor_agent)}
              </div>
            </div>
          </div>
          <div
            style={{
              height: "100%",
              width: "48%",
              //border: "solid 1px rgb(220,220,220)",
              borderRadius: "5px",
              backgroundColor: "#fff",
              marginLeft: "2%",
              height: 200,
              padding: 20,
            }}
          >
            <Spin spinning={loading} wrapperClassName={styles.omp_spin_wrapper}>
              <div style={{ paddingBottom: 35, fontSize: 15, fontWeight: 500 }}>
                部署组件信息
              </div>
              <div
                style={{ display: "flex", paddingTop: 15, paddingBottom: 15 }}
              >
                <div style={{ flex: 1 }}>部署组件</div>
                <div style={{ flex: 1 }}>
                  {isShowDrawer.record.service_num} 个
                </div>
              </div>
              <div
                style={{ display: "flex", paddingTop: 15, paddingBottom: 15 }}
              >
                <div style={{ flex: 1 }}>基础环境</div>
                <div
                  style={{
                    flex: 1,
                    display: "flex",
                    marginLeft: -20,
                  }}
                >
                  {baseEnv.length > 0 ? (
                    baseEnv.map((item) => {
                      return (
                        <Tooltip
                          title={`${item.service__app_name} ${item.service__app_version}`}
                        >
                          <div
                            style={{
                              width: 32,
                              height: 32,
                              borderRadius: "50%",
                              border: "1px solid #a8d0f8",
                              display: "flex",
                              justifyContent: "center",
                              alignItems: "center",
                              marginLeft: 4,
                              marginRight: 4,
                              overflow: "hidden",
                            }}
                            dangerouslySetInnerHTML={{
                              __html: item.service__app_logo || componentImgStr,
                            }}
                            key={item.service__app_name}
                          ></div>
                        </Tooltip>
                      );
                    })
                  ) : (
                    <div style={{ marginLeft: 10 }}>无</div>
                  )}
                </div>
              </div>
            </Spin>
          </div>

          <div
            ref={wrapperRef}
            style={{
              height: "calc(100% - 220px)",
              marginTop: 20,
              width: "99%",
              //border: "solid 1px rgb(220,220,220)",
              borderRadius: "5px",
              backgroundColor: "#fff",
              //height:200
              padding: 20,
              //overflow:"hidden"
            }}
          >
            <div style={{ paddingBottom: 20, fontSize: 15, fontWeight: 500 }}>
              历史记录
            </div>
            <Spin spinning={loading} wrapperClassName={styles.omp_spin_wrapper}>
              <Timeline
                style={{
                  overflowY: "scroll",
                  paddingTop: 10,
                  height: wrapperRef.current
                    ? wrapperRef.current?.offsetHeight - 100
                    : 100,
                }}
              >
                {data.map((item) => {
                  return (
                    <Timeline.Item key={item.id}>
                      <p style={{ color: "#595959" }}>
                        [{item.username}] {item.description}
                      </p>
                      <p style={{ color: "#595959" }}>
                        {moment(item.created).format("YYYY-MM-DD HH:mm:ss")}
                      </p>
                    </Timeline.Item>
                  );
                })}
              </Timeline>
            </Spin>
          </div>
        </div>
      </div>
    </Drawer>
  );
};

//操作
const renderMenu = (
  setUpdateMoadlVisible,
  setCloseMaintainModal,
  setOpenMaintainModal,
  record
) => {
  return (
    <Menu>
      <Menu.Item key="changge" onClick={() => setUpdateMoadlVisible(true)}>
        <span style={{ fontSize: 12 }}>修改主机信息</span>
      </Menu.Item>
      {record.is_maintenance ? (
        <Menu.Item key="close" onClick={() => setCloseMaintainModal(true)}>
          <span style={{ fontSize: 12 }}>关闭维护模式</span>
        </Menu.Item>
      ) : (
        <Menu.Item key="open" onClick={() => setOpenMaintainModal(true)}>
          <span style={{ fontSize: 12 }}>开启维护模式</span>
        </Menu.Item>
      )}
    </Menu>
  );
};

const renderStatus = (text) => {
  switch (text) {
    case 0:
      return <span>{renderDisc("normal", 7, -1)}正常</span>;
    case 1:
      return <span>{renderDisc("warning", 7, -1)}重启中</span>;
    case 2:
      return <span>{renderDisc("critical", 7, -1)}启动失败</span>;
    case 3:
      return <span>{renderDisc("warning", 7, -1)}部署中</span>;
    case 4:
      return <span>{renderDisc("critical", 7, -1)}部署失败</span>;
    default:
      return "-";
  }
};

const renderInitStatue = (text) => {
  switch (text) {
    case 0:
      return <span>{renderDisc("normal", 7, -1)}成功</span>;
    case 1:
      return <span>{renderDisc("notMonitored", 7, -1)}未执行</span>;
    case 2:
      return <span>{renderDisc("warning", 7, -1)}执行中</span>;
    case 3:
      return <span>{renderDisc("critical", 7, -1)}失败</span>;
  }
};

const getColumnsConfig = (
  setIsShowDrawer,
  setRow,
  setUpdateMoadlVisible,
  fetchHostDetail,
  setCloseMaintainModal,
  setOpenMaintainModal,
  setShowIframe,
  history
) => {
  return [
    {
      title: "IP地址",
      key: "ip",
      dataIndex: "ip",
      sorter: (a, b) => a.ip - b.ip,
      sortDirections: ["descend", "ascend"],
      align: "center",
      //width: 140,
      render: (text, record) => {
        let str = nonEmptyProcessing(text);
        if (str == "-") {
          return "-";
        } else {
          return (
            <a
              onClick={() => {
                fetchHostDetail(record.id);
                setIsShowDrawer({
                  isOpen: true,
                  record: record,
                });
              }}
            >
              {str}
            </a>
          );
        }
      },
      //ellipsis: true,
      fixed: "left",
    },
    {
      title: "实例名称",
      key: "instance_name",
      dataIndex: "instance_name",
      align: "center",
      ellipsis: true,
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
    },
    {
      title: "CPU使用率",
      key: "cpu_usage",
      dataIndex: "cpu_usage",
      align: "center",
      sorter: (a, b) => a.cpu_usage - b.cpu_usage,
      sortDirections: ["descend", "ascend"],
      render: (text, record) => {
        let str = nonEmptyProcessing(text);
        return str == "-" ? (
          "-"
        ) : (
          <span
            style={{ color: colorConfig[record.cpu_status], fontWeight: 500 }}
          >
            {str}%
          </span>
        );
      },
    },
    {
      title: "内存使用率",
      key: "mem_usage",
      dataIndex: "mem_usage",
      sorter: (a, b) => a.mem_usage - b.mem_usage,
      sortDirections: ["descend", "ascend"],
      align: "center",
      render: (text, record) => {
        let str = nonEmptyProcessing(text);
        return str == "-" ? (
          "-"
        ) : (
          <span
            style={{ color: colorConfig[record.mem_status], fontWeight: 500 }}
          >
            {str}%
          </span>
        );
      },
    },
    {
      title: "根分区使用率",
      key: "root_disk_usage",
      //width:120,
      dataIndex: "root_disk_usage",
      align: "center",
      //ellipsis: true,
      sorter: (a, b) => a.root_disk_usage - b.root_disk_usage,
      sortDirections: ["descend", "ascend"],
      render: (text, record) => {
        let str = nonEmptyProcessing(text);
        return str == "-" ? (
          "-"
        ) : (
          <span
            style={{
              color: colorConfig[record.root_disk_status],
              fontWeight: 500,
            }}
          >
            {str}%
          </span>
        );
      },
      // width:120
    },
    {
      title: "数据分区使用率",
      width: 130,
      key: "data_disk_usage",
      dataIndex: "data_disk_usage",
      align: "center",
      //ellipsis: true,
      sorter: (a, b) => a.data_disk_usage - b.data_disk_usage,
      sortDirections: ["descend", "ascend"],
      render: (text, record) => {
        let str = nonEmptyProcessing(text);
        return str == "-" ? (
          "-"
        ) : (
          <span
            style={{
              color: colorConfig[record.data_disk_status],
              fontWeight: 500,
            }}
          >
            {str}%
          </span>
        );
      },
    },
    {
      title: "维护模式",
      key: "is_maintenance",
      dataIndex: "is_maintenance",
      align: "center",
      //ellipsis: true,
      render: (text) => {
        if (nonEmptyProcessing(text) == "-") return "-";
        return text ? "是" : "否";
      },
    },
    {
      title: "主机初始化",
      key: "init_status",
      dataIndex: "init_status",
      align: "center",
      //ellipsis: true,
      render: (text) => {
        return renderInitStatue(text);
      },
    },
    {
      title: "主机Agent",
      key: "host_agent",
      dataIndex: "host_agent",
      align: "center",
      //ellipsis: true,
      sorter: (a, b) => a.host_agent - b.host_agent,
      sortDirections: ["descend", "ascend"],
      render: (text) => {
        return renderStatus(text);
      },
    },
    {
      title: "监控Agent",
      key: "monitor_agent",
      dataIndex: "monitor_agent",
      sorter: (a, b) => a.monitor_agent - b.monitor_agent,
      sortDirections: ["descend", "ascend"],
      align: "center",
      //ellipsis: true,
      render: (text) => {
        return renderStatus(text);
      },
    },
    {
      title: "服务总数",
      key: "service_num",
      dataIndex: "service_num",
      align: "center",
      // ellipsis: true,
      sorter: (a, b) => a.service_num - b.service_num,
      sortDirections: ["descend", "ascend"],
      render: (text, record) => {
        if (text && text !== 0 && text !== "-") {
          return (
            <a
              onClick={() => {
                text &&
                  history.push({
                    pathname: "/application_management/service_management",
                    state: {
                      ip: record.ip,
                    },
                  });
              }}
            >
              {text}个
            </a>
          );
        } else {
          if ((!text || text == "-") && text !== 0) {
            return "-";
          }
          return `${text}个`;
        }
      },
    },
    {
      title: "告警总数",
      key: "alert_num",
      dataIndex: "alert_num",
      align: "center",
      //ellipsis: true,
      sorter: (a, b) => a.alert_num - b.alert_num,
      sortDirections: ["descend", "ascend"],
      render: (text, record) => {
        if (text && text !== 0 && text !== "-") {
          return (
            <a
              onClick={() => {
                text &&
                  history.push({
                    pathname: "/application-monitoring/alarm-log",
                    state: {
                      ip: record.ip,
                    },
                  });
              }}
            >
              {text}次
            </a>
          );
        } else {
          if ((!text || text == "-") && text !== 0) {
            return "-";
          }
          return `${text}次`;
        }
      },
    },
    {
      title: "操作",
      //width: 100,
      width: 100,
      key: "",
      dataIndex: "",
      align: "center",
      fixed: "right",
      render: function renderFunc(text, record, index) {
        if (record?.host_agent == 3 || record?.monitor_agent == 3) {
          return (
            <div
              onClick={() => {
                setRow(record);
              }}
              style={{ display: "flex", justifyContent: "space-around" }}
            >
              <span style={{ color: "rgba(0, 0, 0, 0.25)" }}>监控</span>
              <span style={{ color: "rgba(0, 0, 0, 0.25)" }}>
                更多 <DownOutlined style={{ position: "relative", top: 1 }} />
              </span>
            </div>
          );
        }
        return (
          <div
            onClick={() => {
              setRow(record);
            }}
            style={{ display: "flex", justifyContent: "space-around" }}
          >
            {record.monitor_url ? (
              <a
                onClick={() => {
                  setShowIframe({
                    isOpen: true,
                    src: record.monitor_url,
                    record: record,
                    isLog: false,
                  });
                }}
              >
                监控
              </a>
            ) : (
              <span style={{ color: "rgba(0, 0, 0, 0.25)" }}>监控</span>
            )}

            <Dropdown
              arrow
              overlay={renderMenu(
                setUpdateMoadlVisible,
                setCloseMaintainModal,
                setOpenMaintainModal,
                record
              )}
            >
              <a>
                更多 <DownOutlined style={{ position: "relative", top: 1 }} />
              </a>
            </Dropdown>
          </div>
        );
      },
    },
  ];
};

export default getColumnsConfig;
