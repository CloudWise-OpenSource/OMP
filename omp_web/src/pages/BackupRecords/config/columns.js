import { nonEmptyProcessing, renderDisc, handleResponse } from "@/utils/utils";
import { Tooltip, message } from "antd";
import moment from "moment";
import { apiRequest } from "src/config/requestApi";
import { fetchGet } from "@/utils/request";

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

const renderPushResult = (text) => {
  switch (text) {
    case 0:
      return <span>{renderDisc("critical", 7, -1)}失败</span>;
    case 1:
      return <span>{renderDisc("normal", 7, -1)}成功</span>;
    case 2:
      return <span>{renderDisc("warning", 7, -1)}推送中</span>;
    case 3:
      return <span>{renderDisc("warning", 7, -1)}未推送</span>;
  }
};

const getColumnsConfig = (setRow, setDeleteOneModal, pushData) => {
  // 推送邮件相关数据
  const { pushForm, setPushLoading, setPushAnalysisModal, setPushInfo } =
    pushData;

  // 查询推送数据
  const fetchPushDate = (record) => {
    setPushLoading(true);
    fetchGet(apiRequest.dataBackup.queryBackupSettingData)
      .then((res) => {
        handleResponse(res, (res) => {
          if (res && res.data) {
            let backup_setting = res.data.backup_setting;
            const to_users = backup_setting.to_users;
            pushForm.setFieldsValue({
              email: to_users,
            });
            setPushInfo({
              id: record.id,
              to_users: to_users,
            });
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setPushLoading(false);
      });
  };

  // 点击推送
  const clickPush = (record) => {
    setPushAnalysisModal(true);
    fetchPushDate(record);
  };
  return [
    {
      title: "任务名称",
      key: "ip",
      dataIndex: "backup_name",
      align: "center",
      width: 140,
      //ellipsis: true,
      fixed: "left",
    },
    {
      title: "备份实例",
      key: "content",
      dataIndex: "content",
      align: "center",
      width: 200,
      ellipsis: true,
      render: (text) => {
        return (
          <Tooltip title={text.join(",")}>
            <span>{text.join(",")}</span>
          </Tooltip>
        );
      },
    },
    {
      title: "备份结果",
      key: "result",
      dataIndex: "result",
      align: "center",
      width: 90,
      render: (text) => {
        return renderResult(text);
      },
    },
    {
      title: "备份方式",
      key: "operation",
      dataIndex: "operation",
      width: 100,
      align: "center",
    },
    {
      title: "备份文件",
      key: "file_name",
      dataIndex: "file_name",
      align: "center",
      width: 180,
      ellipsis: true,
      render: (text) => {
        return (
          <Tooltip title={text || "-"}>
            <span>{text || "-"}</span>
          </Tooltip>
        );
      },
    },
    {
      title: "备份大小",
      key: "file_size",
      dataIndex: "file_size",
      align: "center",
      width: 80,
      ellipsis: true,
      render: (text) => {
        return <span>{text ? `${text} M` : "-"}</span>;
      },
    },
    {
      title: "过期时间",
      key: "expire_time",
      dataIndex: "expire_time",
      align: "center",
      width: 120,
      ellipsis: true,
      render: (text) => {
        return text ? moment(text).format("YYYY-MM-DD HH:mm:ss") : "-";
      },
    },
    {
      title: "推送结果",
      key: "send_email_result",
      dataIndex: "send_email_result",
      align: "center",
      width: 90,
      render: (text) => {
        return renderPushResult(text);
      },
    },
    {
      title: "操作",
      width: 100,
      key: "",
      dataIndex: "",
      align: "center",
      fixed: "right",
      render: function renderFunc(text, record, index) {
        if (record?.file_deleted) {
          return (
            <div style={{ display: "flex", justifyContent: "space-around" }}>
              <span style={{ color: "rgba(0, 0, 0, 0.25)" }}>已删除</span>
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
            <div style={{ margin: "auto" }}>
              {record.result === 0 || record.result === 2 ? (
                <>
                  <span style={{ color: "rgba(0, 0, 0, 0.25)" }}>下载</span>
                  <span
                    style={{ color: "rgba(0, 0, 0, 0.25)", marginLeft: 10 }}
                  >
                    推送
                  </span>
                  <span
                    style={{ color: "rgba(0, 0, 0, 0.25)", marginLeft: 10 }}
                  >
                    删除
                  </span>
                </>
              ) : (
                <>
                  <a
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
                  </a>
                  <a
                    style={{ marginLeft: 10 }}
                    onClick={() => clickPush(record)}
                  >
                    推送
                  </a>
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
