import { renderDisc } from "@/utils/utils";
import { Tooltip } from "antd";

const getColumnsConfig = (
  setStrategyRow,
  setDeleteStrategyModal,
  setStrategyModalType,
  setStrategyModalVisibility,
  strategyForm,
  queryCanHealing
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
      title: "自愈实例",
      key: "repair_instance",
      dataIndex: "repair_instance",
      align: "center",
      width: 200,
      ellipsis: true,
      render: (text) => {
        // if (text.length > 0 && text[0] === "all") return "所有服务";
        const textMap = {
          host: "主机监控Agent",
          component: "基础组件",
          service: "自研服务",
        };
        const resText = text.map((e) => textMap[e]);
        return (
          <Tooltip title={resText.join(", ")}>
            <span>{resText.join(", ")}</span>
          </Tooltip>
        );
      },
    },
    {
      title: "自愈类型",
      key: "instance_tp",
      dataIndex: "instance_tp",
      align: "center",
      width: 60,
      ellipsis: true,
      render: (text) => {
        if (text === 0) {
          return "启动 [start]";
        } else {
          return "重启 [restart]";
        }
      },
    },
    {
      title: "探测周期",
      key: "fresh_rate",
      dataIndex: "fresh_rate",
      align: "center",
      width: 100,
      ellipsis: true,
      render: (text) => {
        return `${text} min`;
      },
    },
    {
      title: "重试次数",
      key: "max_healing_count",
      dataIndex: "max_healing_count",
      align: "center",
      width: 100,
      ellipsis: true,
    },
    {
      title: "是否生效",
      key: "used",
      dataIndex: "used",
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
            <a
              style={{ marginLeft: 10 }}
              onClick={() => {
                queryCanHealing();
                setStrategyModalType("update");
                setStrategyModalVisibility(true);
                strategyForm.setFieldsValue({
                  repair_instance: record.repair_instance,
                  fresh_rate: record.fresh_rate,
                  instance_tp: record.instance_tp,
                  max_healing_count: record.max_healing_count,
                  used: record.used,
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
