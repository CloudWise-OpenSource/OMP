import { renderDisc } from "@/utils/utils";
import { Tooltip, Badge } from "antd";
import moment from "moment";

const renderStatus = (state) => {
  switch (state) {
    case 1:
      return (
        <span>
          {renderDisc("normal", 7, -1)}
          自愈成功
        </span>
      );
      break;
    case 0:
      return (
        <span>
          {renderDisc("critical", 7, -1)}
          自愈失败
        </span>
      );
      break;
    case 2:
      return (
        <span>
          {renderDisc("warning", 7, -1)}
          自愈中
        </span>
      );
      break;
    default:
      return "-";
      break;
  }
};

const getColumnsConfig = (
  queryRequest,
  setShowIframe,
  updateAlertRead,
  history
) => {
  return [
    {
      title: "实例名称",
      key: "instance_name",
      dataIndex: "instance_name",
      align: "center",
      width: 200,
      ellipsis: true,
      fixed: "left",
      sorter: (a, b) => a.instance_name - b.instance_name,
      sortDirections: ["descend", "ascend"],
      render: (text, record) => {
        return (
          <Tooltip title={text}>
            <Badge dot={record.is_read === 0} offset={[5, 2]}>
              <span style={{ fontSize: 12 }}>
                {record.instance_name ? record.instance_name : "-"}
              </span>
            </Badge>
          </Tooltip>
        );
      },
    },
    {
      title: "IP地址",
      key: "host_ip",
      width: 140,
      dataIndex: "host_ip",
      ellipsis: true,
      sorter: (a, b) => a.host_ip - b.host_ip,
      sortDirections: ["descend", "ascend"],
      align: "center",
    },
    {
      title: "自愈状态",
      key: "state",
      dataIndex: "state",
      align: "center",
      width: 120,
      // sorter: (a, b) => a.severity - b.severity,
      // sortDirections: ["descend", "ascend"],
      //ellipsis: true,
      //width:120,
      usefilter: true,
      queryRequest: queryRequest,
      filterMenuList: [
        {
          value: "1",
          text: "自愈成功",
        },
        {
          value: "0",
          text: "自愈失败",
        },
        {
          value: "2",
          text: "自愈中",
        },
      ],
      render: renderStatus,
    },
    {
      title: "重试次数",
      key: "healing_count",
      dataIndex: "healing_count",
      align: "center",
      //ellipsis: true,
      width: 80,
      render: (text) => {
        return text ? `${text}次` : "-";
      },
    },
    {
      title: "故障时间",
      width: 180,
      key: "alert_time",
      dataIndex: "alert_time",
      align: "center",
      //ellipsis: true,
      // sorter: (a, b) => a.alert_time - b.alert_time,
      // sortDirections: ["descend", "ascend"],
      render: (text) => {
        if (text) {
          let str = moment(text).format("YYYY-MM-DD HH:mm:ss");
          return str;
        }
        return "-";
      },
    },
    {
      title: "结束时间",
      width: 180,
      key: "end_time",
      dataIndex: "end_time",
      align: "center",
      //ellipsis: true,
      // sorter: (a, b) => a.create_time - b.create_time,
      // sortDirections: ["descend", "ascend"],
      render: (text) => {
        if (text) {
          let str = moment(text).format("YYYY-MM-DD HH:mm:ss");
          return str;
        }
        return "-";
      },
    },
    {
      title: "故障描述",
      key: "alert_content",
      dataIndex: "alert_content",
      align: "center",
      width: 300,
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
      title: "自愈日志",
      key: "healing_log",
      dataIndex: "healing_log",
      align: "center",
      width: 220,
      ellipsis: true,
      render: (text) => {
        return (
          <Tooltip title={text} placement="topLeft">
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
    },
    {
      title: "操作",
      width: 140,
      key: "",
      dataIndex: "",
      fixed: "right",
      align: "center",
      render: function renderFunc(text, record, index) {
        //console.log(record);
        return (
          <div style={{ display: "flex", justifyContent: "space-around" }}>
            <div style={{ margin: "auto" }}>
              {record.instance_name ? (
                <a
                  onClick={() => {
                    console.log(record);
                    history.push({
                      pathname: "/application-monitoring/alarm-log",
                      state: {
                        alert_instance_name: record.instance_name,
                        time: record.alert_time,
                      },
                    });
                  }}
                >
                  关联告警
                </a>
              ) : (
                <span style={{ color: "rgba(0, 0, 0, 0.25)" }}>关联告警</span>
              )}

              {record.monitor_log ? (
                <a
                  style={{ marginLeft: 10 }}
                  onClick={() => {
                    record.is_read == 0 && updateAlertRead([record.id]);
                    setShowIframe({
                      isOpen: true,
                      src: record.monitor_log,
                      record: {
                        ...record,
                        ip: record.host_ip,
                      },
                      isLog: true,
                    });
                  }}
                >
                  服务日志
                </a>
              ) : (
                <span style={{ color: "rgba(0, 0, 0, 0.25)", marginLeft: 10 }}>
                  服务日志
                </span>
              )}
            </div>
          </div>
        );
      },
    },
  ];
};

export default getColumnsConfig;
