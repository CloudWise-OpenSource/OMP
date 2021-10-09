import { nonEmptyProcessing, colorConfig } from "@/utils/utils";
import { Tooltip, Badge, Menu, Dropdown } from "antd";
import { FilterFilled } from "@ant-design/icons";
import OmpTableFilter from "@/components/OmpTable/components/OmpTableFilter"

const getColumnsConfig = () => {
  return [
    {
      title: "实例名称",
      key: "instance_name",
      dataIndex: "instance_name",
      align: "center",
      //width: 180,
      ellipsis: true,
      fixed: "left",
      render: (text) => {
        return (
          <Tooltip title={text}>
            <Badge dot offset={[5, 2]}>
              {text ? text : "-"}
            </Badge>
          </Tooltip>
        );
      },
    },
    {
      title: "IP地址",
      key: "ip",
      dataIndex: "ip",
      //width:180,
      sorter: (a, b) => a.ip - b.ip,
      sortDirections: ["descend", "ascend"],
      align: "center",
    },
    {
      title: "级别",
      key: "severity",
      dataIndex: "severity",
      align: "center",
      // sorter: (a, b) => a.severity - b.severity,
      // sortDirections: ["descend", "ascend"],
      //ellipsis: true,
      //width:120,
      usefilter:true,
      // filterIcon: () => {
      //   return <OmpTableFilter />
      // },
      // filters: [{ text: "mock", value: "mock" }],
      // filterDropdown: () => {
      //   return <span key="mock_"></span>;
      // },
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
      title: "监控类型",
      key: "mem_usage",
      dataIndex: "mem_usage",
      sorter: (a, b) => a.mem_usage - b.mem_usage,
      sortDirections: ["descend", "ascend"],
      align: "center",
      //ellipsis: true,
      //width:150,
      render: (text) => {
        let str = nonEmptyProcessing(text);
        return str == "-" ? "-" : `${str}%`;
      },
    },
    {
      title: "告警描述",
      key: "description",
      dataIndex: "description",
      align: "center",
      width: 420,
      ellipsis: true,
      sorter: (a, b) => a.description - b.description,
      sortDirections: ["descend", "ascend"],
      render: (text) => {
        let str = nonEmptyProcessing(text);
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
        let str = nonEmptyProcessing(text);
        return str == "-" ? "-" : `${str}`;
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
