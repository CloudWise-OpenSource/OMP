import { nonEmptyProcessing, colorConfig } from "@/utils/utils";
import { Tooltip, Badge, Menu, Dropdown } from "antd";
import { FilterFilled } from "@ant-design/icons";
import OmpTableFilter from "@/components/OmpTable/components/OmpTableFilter";
import moment from "moment";

const getColumnsConfig = (
  queryRequest,
  setShowIframe,
  //updateAlertRead,
  history,
  initfilter
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
              <span style={{fontSize:12}}>{record.instance_name ? record.instance_name : "-"}</span>
            </Badge>
          </Tooltip>
        );
      },
    },
    {
      title: "IP地址",
      key: "ip",
      dataIndex: "ip",
      //width: 180,
      ellipsis: true,
      sorter: (a, b) => a.ip - b.ip,
      sortDirections: ["descend", "ascend"],
      align: "center",
      render: (text, record) => {
        return (
          <a
            onClick={() => {
              text &&
                history.push({
                  pathname: "/resource-management/machine-management",
                  state: {
                    ip: text,
                  },
                });
            }}
          >
            {text}
          </a>
        );
      },
    },
    {
      title: "级别",
      key: "severity",
      dataIndex: "severity",
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
          value: "critical",
          text: "严重",
        },
        {
          value: "warning",
          text: "警告",
        },
      ],
      render: (text) => {
        switch (text) {
          case "critical":
            return <span style={{ color: colorConfig[text] }}>严重</span>;
          case "warning":
            return <span style={{ color: colorConfig[text] }}>警告</span>;
          case "info":
            return <span style={{ color: colorConfig[text] }}>警告</span>;
          default:
            return "-";
        }
      },
    },
    {
      title: "告警类型",
      key: "type",
      dataIndex: "type",
      usefilter: true,
      queryRequest: queryRequest,
      initfilter:initfilter,
      filterMenuList: [
        {
          value: "service",
          text: "服务",
        },
        {
          value: "host",
          text: "主机",
        },
      ],
      align: "center",
      //ellipsis: true,
      width: 150,
      render: (text) => {
        if (text == "host") {
          return "主机";
        } else if (text == "service") {
          return "服务";
        }
      },
    },
    {
      title: "告警描述",
      key: "description",
      dataIndex: "description",
      align: "center",
      width: 420,
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
      title: "告警时间",
      //width:180,
      key: "date",
      dataIndex: "date",
      align: "center",
      //ellipsis: true,
      sorter: (a, b) => a.date - b.date,
      sortDirections: ["descend", "ascend"],
      render: (text) => {
        let str = moment(text).format("YYYY-MM-DD HH:mm:ss");
        return str;
      },
    },
    {
      title: "操作",
      width: 100,
      key: "",
      dataIndex: "",
      fixed: "right",
      align: "center",
      render: function renderFunc(text, record, index) {
        return (
          <div style={{ display: "flex", justifyContent: "space-around" }}>
            {record.monitor_url ? (
              <a
                onClick={() => {
                  //record.is_read == 0 && updateAlertRead([record.id]);
                  setShowIframe({
                    isOpen: true,
                    src: record.monitor_url,
                    record: {
                      ...record,
                      ip: record.ip,
                    },
                    isLog: false,
                  });
                }}
              >
                监控
              </a>
            ) : (
              <span style={{ color: "rgba(0, 0, 0, 0.25)" }}>监控</span>
            )}

            {record.type == "host" ? (
              ""
            ) : record.log_url ? (
              <a
                onClick={() => {
                  //record.is_read == 0 && updateAlertRead([record.id]);
                  setShowIframe({
                    isOpen: true,
                    src: record.log_url,
                    record: {
                      ...record,
                      ip: record.ip,
                    },
                    isLog: true,
                  });
                }}
              >
                日志
              </a>
            ) : (
              <span style={{ color: "rgba(0, 0, 0, 0.25)" }}>日志</span>
            )}
          </div>
        );
      },
    },
  ];
};

export default getColumnsConfig;
