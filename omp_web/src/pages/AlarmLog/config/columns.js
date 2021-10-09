import { nonEmptyProcessing } from "@/utils/utils";
import { Tooltip } from "antd";

const getColumnsConfig = () => {
  return [
    {
      title: "实例名称",
      key: "instance_name",
      dataIndex: "instance_name",
      align: "center",
      width: 180,
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
      title: "IP地址",
      key: "ip",
      dataIndex: "ip",
      width:180,
      sorter: (a, b) => a.ip - b.ip,
      sortDirections: ["descend", "ascend"],
      align: "center",
      render: (text, record) => {
        let str = nonEmptyProcessing(text);
        if (str == "-") {
          return "-";
        } else {
          return (
            <a
              onClick={() => {
                fetchHistoryData(record.id);
                setIsShowIsframe({
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
      //fixed: "left"
    },
    {
      title: "级别",
      key: "cpu_usage",
      dataIndex: "cpu_usage",
      align: "center",
      sorter: (a, b) => a.cpu_usage - b.cpu_usage,
      sortDirections: ["descend", "ascend"],
      //ellipsis: true,
      width:120,
      render: (text) => {
        let str = nonEmptyProcessing(text);
        return str == "-" ? "-" : `${str}%`;
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
      width:150,
      render: (text) => {
        let str = nonEmptyProcessing(text);
        return str == "-" ? "-" : `${str}%`;
      },
    },
    {
      title: "告警描述",
      key: "root_disk_usage",
      dataIndex: "root_disk_usage",
      align: "center",
      //width:280,
      ellipsis: true,
      sorter: (a, b) => a.root_disk_usage - b.root_disk_usage,
      sortDirections: ["descend", "ascend"],
      render: (text) => {
        let str = nonEmptyProcessing(text);
        return str == "-" ? "-" : `${str}%`;
      },
    },
    {
      title: "告警时间",
      width:180,
      key: "data_disk_usag",
      dataIndex: "data_disk_usag",
      align: "center",
      //ellipsis: true,
      sorter: (a, b) => a.data_disk_usag - b.data_disk_usag,
      sortDirections: ["descend", "ascend"],
      render: (text) => {
        let str = nonEmptyProcessing(text);
        return str == "-" ? "-" : `${str}%`;
      },
    },
    {
      title: "操作",
    width: 140,
      key: "",
      dataIndex: "",
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
