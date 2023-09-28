import { renderDisc } from "@/utils/utils";
import { Tooltip } from "antd";
import moment from "moment";

const renderResult = (text) => {
  switch (text) {
    case 0:
      return <span>{renderDisc("critical", 7, -1)}失败</span>;
    case 1:
      return <span>{renderDisc("normal", 7, -1)}成功</span>;
    case 2:
      return <span>{renderDisc("warning", 7, -1)}执行中</span>;
  }
};

const getColumnsConfig = (setRow, setDeleteOneModal) => {
  // 推送邮件相关数据

  return [
    {
      title: "任务名称",
      key: "backup_name",
      dataIndex: "backup_name",
      align: "center",
      width: 240,
      ellipsis: true,
      fixed: "left",
      render: (text) => {
        return (
          <Tooltip title={text || "-"} placement="topLeft">
            <span>{text || "-"}</span>
          </Tooltip>
        );
      },
    },
    {
      title: "状态",
      key: "result",
      dataIndex: "result",
      align: "center",
      width: 100,
      render: (text) => {
        return renderResult(text);
      },
    },
    {
      title: "备份实例",
      key: "content",
      dataIndex: "content",
      align: "center",
      width: 140,
      ellipsis: true,
    },
    {
      title: "备份文件",
      key: "file_name",
      dataIndex: "file_name",
      align: "center",
      width: 180,
      ellipsis: true,
      render: (text, record) => {
        if (record?.file_deleted) {
          return "-";
        }
        return (
          <Tooltip title={text || "-"} placement="topLeft">
            <span>{text || "-"}</span>
          </Tooltip>
        );
      },
    },
    {
      title: "文件大小",
      key: "file_size",
      dataIndex: "file_size",
      align: "center",
      width: 80,
      ellipsis: true,
      // render: (text) => {
      //   return <span>{text ? `${text} M` : "-"}</span>;
      // },
    },
    {
      title: "备份路径",
      key: "retain_path",
      dataIndex: "retain_path",
      width: 160,
      align: "center",
      ellipsis: true,
      render: (text) => {
        return (
          <Tooltip title={text || "-"} placement="topLeft">
            <span>{text || "-"}</span>
          </Tooltip>
        );
      },
    },
    {
      title: "远程路径",
      key: "remote_path",
      dataIndex: "remote_path",
      width: 160,
      align: "center",
      ellipsis: true,
      render: (text) => {
        return (
          <Tooltip title={text || "-"} placement="topLeft">
            <span>{text || "-"}</span>
          </Tooltip>
        );
      },
    },
    {
      title: "过期时间",
      key: "expire_time",
      dataIndex: "expire_time",
      width: 180,
      align: "center",
      ellipsis: true,
      render: (text) => {
        if (text) {
          return moment(text).format("YYYY-MM-DD HH:mm:ss");
        }
        return "-";
      },
    },
    {
      title: "信息",
      key: "message",
      dataIndex: "message",
      align: "center",
      width: 180,
      ellipsis: true,
      render: (text) => {
        return (
          <Tooltip title={text || "-"} placement="topLeft">
            <span>{text || "-"}</span>
          </Tooltip>
        );
      },
    },
    {
      title: "操作",
      width: 100,
      key: "",
      dataIndex: "",
      align: "center",
      fixed: "right",
      render: (text, record, index) => {
        return (
          <div
            onClick={() => {
              setRow(record);
            }}
            style={{ display: "flex", justifyContent: "space-around" }}
          >
            <div style={{ margin: "auto" }}>
              {record.result === 2 ? (
                <>
                  {/* <span style={{ color: "rgba(0, 0, 0, 0.25)" }}>下载</span> */}
                  <span
                    style={{ color: "rgba(0, 0, 0, 0.25)", marginLeft: 10 }}
                  >
                    删除
                  </span>
                </>
              ) : (
                <>
                  {/* <a
                    onClick={() => {
                      if (record.file_name || record.result === 1) {
                        let a = document.createElement("a");
                        a.href = `/download-backup/${record.file_name}`;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                      } else {
                        message.warning("该任务文件不支持下载");
                      }
                    }}
                  >
                    下载
                  </a> */}
                  <a
                    style={{ marginLeft: 10 }}
                    onClick={() => setDeleteOneModal(true)}
                  >
                    删除
                  </a>
                </>
              )}
            </div>
          </div>
        );
      },
    },
  ];
};

export default getColumnsConfig;
