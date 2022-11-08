import moment from "moment";
import { nonEmptyProcessing } from "@/utils/utils";

const getColumnsConfig = (history) => {
  return [
    {
      title: "编号",
      width: 140,
      key: "_idx",
      dataIndex: "_idx",
      align: "center",
      render: nonEmptyProcessing,
      fixed: "left",
    },
    {
      title: "模板名称",
      width: 280,
      key: "plan_name",
      dataIndex: "plan_name",
      align: "center",
    },
    {
      title: "主机数量",
      key: "host_num",
      width: 150,
      dataIndex: "host_num",
      align: "center",
    },
    {
      title: "产品数量",
      key: "product_num",
      width: 150,
      dataIndex: "product_num",
      align: "center",
    },
    {
      title: "服务数量",
      key: "service_num",
      width: 150,
      dataIndex: "service_num",
      align: "center",
    },
    {
      title: "创建时间",
      key: "created",
      dataIndex: "created",
      align: "center",
      width: 280,
      render: (text) => {
        if (text) {
          return moment(text).format("YYYY-MM-DD HH:mm:ss");
        } else {
          return "-";
        }
      },
    },
    {
      title: "创建用户",
      key: "create_user",
      dataIndex: "create_user",
      align: "center",
      width: 200,
      render: (text) => {
        return "Admin";
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
        return (
          <div style={{ display: "flex", justifyContent: "space-around" }}>
            <a
              onClick={() => {
                history.push({
                  pathname: "/application_management/app_store/installation",
                  state: {
                    uniqueKey: record.operation_uuid,
                    step: 3,
                  },
                });
              }}
            >
              安装记录
            </a>
          </div>
        );
      },
    },
  ];
};

export default getColumnsConfig;
