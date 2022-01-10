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
  setInstallationRecordModal,
  queryServiceInstallHistoryDetail,
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
            实例名称: {isShowDrawer.record?.service_instance_name}
          </span>
        </div>
      }
      headerStyle={{
        padding:"19px 24px"
      }}
      placement="right"
      closable={true}
      width={`calc(100% - 200px)`}
      style={{
        height: "calc(100%)",
        // paddingTop: "60px",
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
        style={{ height: "calc(100% - 15px)", width: "100%", display: "flex" }}
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
              <div style={{ flex: 1 }}>
                {isShowDrawer.record?.service_instance_name}
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
              <div style={{ flex: 1 }}>服务名称</div>
              <div style={{ flex: 1 }}>
                {nonEmptyProcessing(isShowDrawer.record?.app_name)}
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
              <a
                onClick={() => {
                  setInstallationRecordModal(true);
                  queryServiceInstallHistoryDetail(data.id);
                }}
                style={{ fontSize: 13, fontWeight: 400 }}
              >
                查看安装记录
              </a>
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
                paddingTop: 8,
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
                paddingTop: 8,
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
                paddingTop: 8,
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
                paddingTop: 8,
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
                paddingTop: 8,
                paddingBottom: 5,
                borderBottom: "solid 1px rgb(220,220,220)",
              }}
            >
              <div style={{ flex: 1 }}>密码</div>
              <div style={{ flex: 1 }}>{data.install_info?.password}</div>
            </div>
            <div
              style={{
                display: "flex",
                paddingTop: 8,
                paddingBottom: 5,
                borderBottom: "solid 1px rgb(220,220,220)",
              }}
            >
              <div style={{ flex: 1 }}>安装时间</div>
              <div style={{ flex: 1 }}>
                {data?.created
                  ? moment(data?.created).format("YYYY-MM-DD HH:mm:ss")
                  : "-"}
              </div>
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
                  //height: "100%",
                  height: wrapperRef.current
                    ? wrapperRef.current?.offsetHeight - 100
                    : 100,
                }}
              >
                {data.history?.map((item) => {
                  return (
                    <Timeline.Item key={item.created}>
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
  // setUpdateMoadlVisible,
  // setCloseMaintainModal,
  // setOpenMaintainModal,

  record,
  setOperateAciton,
  setServiceAcitonModal,
  queryDeleteMsg,
  deleteConditionReset
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
        //disabled={!record.operable}
        key="delete"
        onClick={() => {
          queryDeleteMsg([record]);
          setOperateAciton(4);
          setServiceAcitonModal(true);
          deleteConditionReset();
        }}
      >
        <span style={{ fontSize: 12, paddingLeft: 5, paddingRight: 5 }}>
          卸载
        </span>
      </Menu.Item>
    </Menu>
  );
};

const renderStatus = (text) => {
  switch (text) {
    case "未监控":
      return (
        <span>
          {renderDisc("notMonitored", 7, -1)}
          {text}
        </span>
      );
    case "启动中":
      return (
        <span>
          {renderDisc("warning", 7, -1)}
          {text}
        </span>
      );
    case "停止中":
      return (
        <span>
          {renderDisc("warning", 7, -1)}
          {text}
        </span>
      );
    case "重启中":
      return (
        <span>
          {renderDisc("warning", 7, -1)}
          {text}
        </span>
      );
    case "未知":
      return (
        <span>
          {renderDisc("warning", 7, -1)}
          {text}
        </span>
      );
    case "安装中":
      return (
        <span>
          {renderDisc("warning", 7, -1)}
          {text}
        </span>
      );
    case "待安装":
      return (
        <span>
          {renderDisc("warning", 7, -1)}
          {text}
        </span>
      );
    case "停止":
      return (
        <span>
          {renderDisc("critical", 7, -1)}
          {text}
        </span>
      );
    case "安装失败":
      return (
        <span>
          {renderDisc("critical", 7, -1)}
          {text}
        </span>
      );
    default:
      return (
        <span>
          {renderDisc("normal", 7, -1)}
          {text}
        </span>
      );
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
  setServiceAcitonModal,
  queryDeleteMsg,
  // 删除的前置条件重置
  deleteConditionReset
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
      title: "状态",
      key: "service_status",
      dataIndex: "service_status",
      align: "center",
      //ellipsis: true,
      render: (text) => {
        return renderStatus(text);
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
                setServiceAcitonModal,
                queryDeleteMsg,
                deleteConditionReset
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
