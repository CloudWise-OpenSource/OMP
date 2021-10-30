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
  setInstallationRecordModal
}) => {
  // 视口宽度
  const viewHeight = useSelector((state) => state.layouts.viewSize.height);
  const wrapperRef = useRef(null);
  return (
    <Drawer
      title={
        <div style={{ display: "flex" }}>
          <DesktopOutlined style={{ position: "relative", top: 3, left: -5 }} />
          服务信息面板
          <span style={{ paddingLeft: 30, fontWeight: 400, fontSize: 15 }}>
            服务名称: {isShowDrawer.record?.service_instance_name}
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
        <div style={{ flex: 4 }}>
          <div
            style={{
              height: "calc(50%)",
              width: "100%",
              //border: "solid 1px rgb(220,220,220)",
              borderRadius: "5px",
              backgroundColor: "#fff",
              //flex: 4,
              padding: 20,
            }}
          >
            <div style={{ paddingBottom: 15, fontSize: 15, fontWeight: 500 }}>
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
              <div style={{ flex: 1 }}>{isShowDrawer.record?.app_name}</div>
            </div>
            <div
              style={{
                display: "flex",
                paddingTop: 15,
                paddingBottom: 5,
                borderBottom: "solid 1px rgb(220,220,220)",
              }}
            >
              <div style={{ flex: 1 }}>服务名称</div>
              <div style={{ flex: 1 }}>
                {nonEmptyProcessing(isShowDrawer.record?.service_instance_name)}
              </div>
            </div>
            {/* <div
            style={{
              display: "flex",
              paddingTop: 15,
              paddingBottom: 5,
              borderBottom: "solid 1px rgb(220,220,220)",
            }}
          >
            <div style={{ flex: 1 }}>IP地址</div>
            <div style={{ flex: 1 }}>{isShowDrawer.record.ip}</div>
          </div> */}
            <div
              style={{
                display: "flex",
                paddingTop: 15,
                paddingBottom: 5,
                borderBottom: "solid 1px rgb(220,220,220)",
              }}
            >
              <div style={{ flex: 1 }}>版本</div>
              <div style={{ flex: 1 }}>{isShowDrawer.record?.app_version}</div>
            </div>
            <div
              style={{
                display: "flex",
                paddingTop: 15,
                paddingBottom: 5,
                borderBottom: "solid 1px rgb(220,220,220)",
              }}
            >
              <div style={{ flex: 1 }}>服务分类</div>
              <div style={{ flex: 1 }}>{isShowDrawer.record?.label_name}</div>
            </div>
            <div
              style={{
                display: "flex",
                paddingTop: 15,
                paddingBottom: 5,
                borderBottom: "solid 1px rgb(220,220,220)",
              }}
            >
              <div style={{ flex: 1 }}>集群模式</div>
              <div style={{ flex: 1 }}>{isShowDrawer.record?.cluster_type}</div>
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
              <div style={{ flex: 1 }}>{isShowDrawer.record?.ip}</div>
            </div>
          </div>
          <div
            style={{
              marginTop: "3%",
              height: "calc(48%)",
              width: "100%",
              //border: "solid 1px rgb(220,220,220)",
              borderRadius: "5px",
              backgroundColor: "#fff",
              //flex: 4,
              padding: 20,
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                paddingBottom: 15,
                fontSize: 15,
                fontWeight: 500,
              }}
            >
              安装信息
              <a onClick={()=>{
                setInstallationRecordModal(true)
              }} style={{ fontSize: 13, fontWeight: 400 }}>查看安装记录</a>
            </div>
            <div
              style={{
                display: "flex",
                //paddingTop: 15,
                paddingBottom: 5,
                borderBottom: "solid 1px rgb(220,220,220)",
              }}
            >
              <div style={{ flex: 1 }}>安装目录</div>
              <div style={{ flex: 1 }}>{data.install_info?.base_dir}</div>
            </div>
            <div
              style={{
                display: "flex",
                paddingTop: 15,
                paddingBottom: 5,
                borderBottom: "solid 1px rgb(220,220,220)",
              }}
            >
              <div style={{ flex: 1 }}>数据目录</div>
              <div style={{ flex: 1 }}>{data.install_info?.data_dir}</div>
            </div>
            <div
              style={{
                display: "flex",
                paddingTop: 15,
                paddingBottom: 5,
                borderBottom: "solid 1px rgb(220,220,220)",
              }}
            >
              <div style={{ flex: 1 }}>日志目录</div>
              <div style={{ flex: 1 }}>{data.install_info?.log_dir}</div>
            </div>
            <div
              style={{
                display: "flex",
                paddingTop: 15,
                paddingBottom: 5,
                borderBottom: "solid 1px rgb(220,220,220)",
              }}
            >
              <div style={{ flex: 1 }}>端口号</div>
              <div style={{ flex: 1 }}>{data.install_info?.service_port}</div>
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
              <div style={{ flex: 1 }}>{data.install_info?.username}</div>
            </div>
            <div
              style={{
                display: "flex",
                paddingTop: 15,
                paddingBottom: 5,
                borderBottom: "solid 1px rgb(220,220,220)",
              }}
            >
              <div style={{ flex: 1 }}>密码</div>
              <div style={{ flex: 1 }}>{data.install_info?.password}</div>
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
            ref={wrapperRef}
            style={{
              height: "calc(100%)",
              marginTop: 0,
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
                  height: "100%",
                  // height: wrapperRef.current
                  //   ? wrapperRef.current?.offsetHeight - 100
                  //   : 100,
                }}
              >
                {data.history?.map((item) => {
                  return (
                    <Timeline.Item key={item.created}>
                      <p style={{ color: "#595959" }}>
                        {item.username} {item.description}
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
  // setUpdateMoadlVisible,
  // setCloseMaintainModal,
  // setOpenMaintainModal,
  
  record,
  setOperateAciton,
  setServiceAcitonModal
) => {
  return (
    <Menu>
      <Menu.Item
        disabled={!record.operable}
        style={{ textAlign: "center" }}
        key="start"
        onClick={() => {
          setOperateAciton(1);
          setServiceAcitonModal(true);
        }}
      >
        <span style={{ fontSize: 12, paddingLeft: 5, paddingRight: 5 }}>
          启动
        </span>
      </Menu.Item>
      <Menu.Item
        disabled={!record.operable}
        key="close"
        onClick={() => {
          setOperateAciton(2);
          setServiceAcitonModal(true);
        }}
      >
        <span style={{ fontSize: 12, paddingLeft: 5, paddingRight: 5 }}>
          停止
        </span>
      </Menu.Item>
      <Menu.Item
        disabled={!record.operable}
        key="reStart"
        onClick={() => {
          setOperateAciton(3);
          setServiceAcitonModal(true);
        }}
      >
        <span style={{ fontSize: 12, paddingLeft: 5, paddingRight: 5 }}>
          重启
        </span>
      </Menu.Item>
      <Menu.Item
        disabled={!record.operable}
        key="delete"
        onClick={() => {
          setOperateAciton(4);
          setServiceAcitonModal(true);
        }}
      >
        <span style={{ fontSize: 12, paddingLeft: 5, paddingRight: 5 }}>
          删除
        </span>
      </Menu.Item>
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

const getColumnsConfig = (
  setIsShowDrawer,
  setRow,
  //setUpdateMoadlVisible,
  fetchHistoryData,
  // setCloseMaintainModal,
  // setOpenMaintainModal,
  //setShowIframe,
  history,
  labelsData,
  queryRequest,
  initfilterAppType,
  initfilterLabelName,
  setShowIframe,
  setOperateAciton,
  setServiceAcitonModal
) => {
  return [
    {
      title: "实例名称",
      key: "service_instance_name",
      dataIndex: "service_instance_name",
      sorter: (a, b) => a.service_instance_name - b.service_instance_name,
      sortDirections: ["descend", "ascend"],
      align: "center",
      ellipsis: true,
      fixed: "left",
      render: (text, record) => {
        return (
          <Tooltip title={text}>
            <a
              onClick={() => {
                fetchHistoryData(record.id);
                setIsShowDrawer({
                  isOpen: true,
                  record: record,
                });
              }}
            >
              {text ? text : "-"}
            </a>
          </Tooltip>
        );
      },
    },
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
          return <span>{str}</span>;
        }
      },
      //ellipsis: true,
    },
    {
      title: "端口",
      key: "port",
      dataIndex: "port",
      align: "center",
      ellipsis: true,
      render: (text) => {
        return <Tooltip title={text}>{text ? text : "-"}</Tooltip>;
      },
    },
    {
      title: "功能模块",
      key: "label_name",
      dataIndex: "label_name",
      align: "center",
      usefilter: true,
      queryRequest: queryRequest,
      ellipsis: true,
      initfilter: initfilterLabelName,
      filterMenuList: labelsData.map((item) => ({ value: item, text: item })),
      align: "center",
      render: (text) => {
        return <Tooltip title={text}>{text ? text : "-"}</Tooltip>;
      },
    },
    {
      title: "服务类型",
      key: "app_type",
      dataIndex: "app_type",
      align: "center",
      usefilter: true,
      queryRequest: queryRequest,
      initfilter: initfilterAppType,
      filterMenuList: [
        {
          value: 0,
          text: "基础组件",
        },
        {
          value: 1,
          text: "应用服务",
        },
      ],
      render: (text) => {
        return text ? "应用服务" : "基础组件";
      },
      //ellipsis: true,
    },
    {
      title: "服务名称",
      key: "app_name",
      dataIndex: "app_name",
      align: "center",
      ellipsis: true,
    },
    {
      title: "版本",
      key: "app_version",
      dataIndex: "app_version",
      align: "center",
      ellipsis: true,
    },
    {
      title: "状态",
      key: "service_status",
      dataIndex: "service_status",
      align: "center",
      //ellipsis: true,
      render: (text) => {
        let level = "normal";
        if (
          text == "启动中" ||
          text == "停止中" ||
          text == "重启中" ||
          text == "未知" ||
          text == "安装中"
        ) {
          level = "warning";
        } else if (text == "停止" || text == "安装失败") {
          level = "critical";
        }
        return <span style={{ color: colorConfig[level] }}>{text}</span>;
      },
    },
    {
      title: "告警次数",
      key: "alert_count",
      dataIndex: "alert_count",
      align: "center",
      render: (text, record) => {
        if (text == "-" || text == "0次") {
          return text;
        } else {
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
              {text}
            </a>
          );
        }
      },
      //ellipsis: true,
    },
    {
      title: "集群模式",
      key: "cluster_type",
      dataIndex: "cluster_type",
      align: "center",
      //ellipsis: true,
    },
    {
      title: "操作",
      //width: 100,
      width: 140,
      key: "",
      dataIndex: "",
      align: "center",
      fixed: "right",
      render: function renderFunc(text, record, index) {
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

            {record.log_url ? (
              <a
                onClick={() => {
                  setShowIframe({
                    isOpen: true,
                    src: record.log_url,
                    record: record,
                    isLog: true,
                  });
                }}
              >
                日志
              </a>
            ) : (
              <span style={{ color: "rgba(0, 0, 0, 0.25)" }}>日志</span>
            )}

            <Dropdown
              arrow
              overlay={renderMenu(
                // setUpdateMoadlVisible,
                // setCloseMaintainModal,
                // setOpenMaintainModal,
                record,
                setOperateAciton,
                setServiceAcitonModal
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
