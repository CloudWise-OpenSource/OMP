import { nonEmptyProcessing, colorConfig } from "@/utils/utils";
import { Tooltip, Badge, Menu, Dropdown } from "antd";
import { FilterFilled } from "@ant-design/icons";
import OmpTableFilter from "@/components/OmpTable/components/OmpTableFilter";
import moment from "moment";

const getColumnsConfig = (queryRequest) => {
  return [
    {
      title: "实例名称",
      key: "alert_instance_name",
      dataIndex: "alert_instance_name",
      align: "center",
      width: 200,
      ellipsis: true,
      fixed: "left",
      sorter: (a, b) => a.alert_instance_name - b.alert_instance_name,
      sortDirections: ["descend", "ascend"],
      render: (text, record) => {
          return (
            <Tooltip title={text}>
              <Badge dot={record.is_read === 0} offset={[5, 2]}>
                {record.alert_instance_name
                  ? record.alert_instance_name
                  : "-"}
              </Badge>
            </Tooltip>
          );
      },
    },
    {
      title: "IP地址",
      key: "alert_host_ip",
      dataIndex: "alert_host_ip",
      ellipsis: true,
      sorter: (a, b) => a.alert_host_ip - b.alert_host_ip,
      sortDirections: ["descend", "ascend"],
      align: "center",
    },
    {
      title: "级别",
      key: "alert_level",
      dataIndex: "alert_level",
      align: "center",
      width: 120,
      // sorter: (a, b) => a.severity - b.severity,
      // sortDirections: ["descend", "ascend"],
      //ellipsis: true,
      //width:120,
      usefilter: true,
      queryRequest:queryRequest,
      filterMenuList: [{
        value:"critical",
        text:"严重"
      },{
        value:"warning",
        text:"警告"
      }],
      render: (text) => {
        switch (text) {
          case "critical":
            return <span style={{ color: colorConfig[text] }}>严重</span>;
          case "warning":
            return <span style={{ color: colorConfig[text] }}>警告</span>;
          default:
            return "-";
        }
      },
    },
    {
      title: "告警类型",
      key: "alert_type",
      dataIndex: "alert_type",
      usefilter: true,
      queryRequest:queryRequest,
      filterMenuList: [{
        value:"service",
        text:"服务"
      },{
        value:"host",
        text:"主机"
      }],
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
      key: "alert_describe",
      dataIndex: "alert_describe",
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
      key: "alert_time",
      dataIndex: "alert_time",
      align: "center",
      //ellipsis: true,
      sorter: (a, b) => a.alert_time - b.alert_time,
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
            <a>监控</a>
            <a>日志</a>
          </div>
        );
      },
    },
  ];
};

export default getColumnsConfig;
