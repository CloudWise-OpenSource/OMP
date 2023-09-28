import { renderDisc } from "@/utils/utils";
import { Tooltip } from "antd";
import moment from "moment";

const getColumnsConfig = (
  setStrategyRow,
  setDeleteStrategyModal,
  setStrategyModalType,
  setStrategyModalVisibility,
  setExecuteVisible,
  strategyForm,
  queryCustom,
  setKeyArr,
  weekData,
  setFrequency
) => {
  return [
    {
      title: "序号",
      key: "_idx",
      dataIndex: "_idx",
      align: "center",
      width: 40,
      fixed: "left",
    },
    {
      title: "备份实例",
      key: "backup_instances",
      dataIndex: "backup_instances",
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
      title: "是否生效",
      key: "is_on",
      dataIndex: "is_on",
      align: "center",
      width: 60,
      ellipsis: true,
      render: (text) => {
        if (text) {
          return <span>{renderDisc("normal", 7, -1)}是</span>;
        } else {
          return <span>{renderDisc("critical", 7, -1)}否</span>;
        }
      },
    },
    {
      title: "定时策略",
      key: "crontab_detail",
      dataIndex: "crontab_detail",
      align: "center",
      width: 150,
      ellipsis: true,
      render: (text) => {
        if (text.day_of_month !== "*") {
          return (
            <span>
              每月 {text.day_of_month} 日 {text.hour}:{text.minute}
            </span>
          );
        } else if (text.day_of_week !== "*") {
          return (
            <span>
              每周 {weekData[text.day_of_week]} {text.hour}:{text.minute}
            </span>
          );
        } else {
          return (
            <span>
              每天 {text.hour}:{text.minute}
            </span>
          );
        }
      },
    },
    {
      title: "保留路径",
      key: "retain_path",
      dataIndex: "retain_path",
      align: "center",
      width: 150,
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
      title: "保留时间",
      key: "retain_day",
      dataIndex: "retain_day",
      align: "center",
      width: 100,
      ellipsis: true,
      render: (text) => {
        if (text === -1) return <span>永久保留</span>;
        return <span>{text} 天</span>;
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
            style={{ margin: "auto" }}
            onClick={() => setStrategyRow(record)}
          >
            <a onClick={() => setExecuteVisible(true)}>执行</a>
            <a
              style={{ marginLeft: 10 }}
              onClick={() => {
                queryCustom();
                setStrategyModalType("update");
                setStrategyModalVisibility(true);
                const customInfo = record.backup_custom.map((i) => {
                  return {
                    key: i.id,
                    value: i.id,
                    label: [
                      <span
                        style={{
                          color: "#096dd9",
                          fontWeight: 600,
                          marginRight: 10,
                        }}
                      >
                        [{i.field_k}]
                      </span>,
                      i.field_v,
                    ],
                  };
                });
                setKeyArr(
                  customInfo.map((i) => {
                    return i.label[0].props.children[1];
                  })
                );
                const frType =
                  record.crontab_detail.day_of_month !== "*"
                    ? "month"
                    : record.crontab_detail.day_of_week !== "*"
                    ? "week"
                    : "day";
                const stRes = {
                  frequency: frType,
                  time: moment(
                    `${record.crontab_detail.hour}:${record.crontab_detail.minute}`,
                    "HH:mm"
                  ),
                };
                setFrequency(frType);
                if (frType === "month")
                  stRes["month"] = record.crontab_detail.day_of_month;
                if (frType === "week")
                  stRes["week"] = record.crontab_detail.day_of_week;
                strategyForm.setFieldsValue({
                  backup_instances: record.backup_instances,
                  backup_custom: customInfo,
                  retain_path: record.retain_path,
                  retain_day: record.retain_day,
                  is_on: record.is_on,
                  strategy: stRes,
                });
              }}
            >
              编辑
            </a>

            <a
              style={{ marginLeft: 10 }}
              onClick={() => setDeleteStrategyModal(true)}
            >
              删除
            </a>
          </div>
        );
      },
    },
  ];
};

export default getColumnsConfig;
