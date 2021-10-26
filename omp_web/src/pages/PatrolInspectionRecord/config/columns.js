import { nonEmptyProcessing, renderDisc, downloadFile, handleResponse } from "@/utils/utils";
import { Tooltip, Badge, Menu, Dropdown, message } from "antd";
import moment from "moment";
import { apiRequest } from "src/config/requestApi";
import { fetchGet } from "@/utils/request";

const getColumnsConfig = (queryRequest, history, queryData) => {
  const fetchDetailData = (id) => {
    //setLoading(true);
    fetchGet(`${apiRequest.inspection.reportDetail}/${id}/`)
      .then((res) => {
        handleResponse(res, (res) => {
          console.log(res.data.file_name)
          downloadFile(`/download-inspection/${res.data.file_name}`);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
       // setLoading(false);
      });
  };

  return [
    {
      title: "报告名称",
      width: 120,
      key: "inspection_name",
      dataIndex: "inspection_name",
      align: "center",
      fixed: "left",
      render: (text, record, index) => {
        return (
          <a
            style={{
              fontSize: 12,
            }}
            onClick={() => {
              //queryData(record.id)
              history?.push({
                pathname: `/status-patrol/patrol-inspection-record/status-patrol-detail/${record.id}`,
              });
            }}
          >
            {text}
          </a>
        );
      },
    },
    {
      title: "报告类型",
      width: 80,
      key: "inspection_type",
      align: "center",
      dataIndex: "inspection_type",
      usefilter: true,
      queryRequest: queryRequest,
      filterMenuList: [
        {
          value: "service",
          text: "组件巡检",
        },
        {
          value: "host",
          text: "主机巡检",
        },
        {
          value: "deep",
          text: "深度分析",
        },
      ],
      render: (text, record, index) => {
        if (text == "service") {
          return "组件巡检";
        }
        if (text == "host") {
          return "主机巡检";
        }
        if (text == "deep") {
          return "深度分析";
        }
      },
    },
    {
      title: "巡检结果",
      width: 150,
      key: "inspection_status",
      dataIndex: "inspection_status",
      usefilter: true,
      queryRequest: queryRequest,
      filterMenuList: [
        {
          value: "1",
          text: "进行中",
        },
        {
          value: "2",
          text: "成功",
        },
        {
          value: "3",
          text: "失败",
        },
      ],
      align: "center",
      render: (text, record, index) => {
        if (!text && text !== 0) {
          return "-";
        } else if (text === 2) {
          return <div>{renderDisc("normal", 7, -1)}成功</div>;
        } else if (text === 1) {
          return <div>{renderDisc("normal", 7, -1)}进行中</div>;
        } else if (text === 3) {
          return <div>{renderDisc("critical", 7, -1)}失败</div>;
        } else {
          return text;
        }
      },
    },
    {
      title: "执行方式",
      align: "center",
      dataIndex: "execute_type",
      key: "execute_type",
      usefilter: true,
      queryRequest: queryRequest,
      filterMenuList: [
        {
          value: "man",
          text: "手动",
        },
        {
          value: "auto",
          text: "定时",
        },
      ],
      render: (text) => {
        if (text == "man") {
          return "手动执行";
        } else if (text == "auto") {
          return "定时执行";
        } else {
          return "-";
        }
      },
      width: 80,
    },
    {
      title: "巡检时间",
      width: 200,
      key: "start_time",
      dataIndex: "start_time",
      ellipsis: true,
      sorter: (a, b) =>
        moment(a.start_time).valueOf() - moment(b.start_time).valueOf(),
      sortDirections: ["descend", "ascend"],
      align: "center",
      render: (text) => {
        if (!text) return "-";
        return moment(text).format("YYYY-MM-DD HH:mm:ss");
      },
    },
    {
      title: "巡检用时",
      key: "duration",
      dataIndex: "duration",
      render: (text) => {
        if (text && text !== "-") {
          let timer = moment.duration(text, "seconds");

          let hours = timer.hours();
          let hoursResult = hours ? `${hours}小时` : "";

          let minutes = timer.minutes();
          let minutesResult = minutes % 60 ? `${minutes % 60}分钟` : "";

          let seconds = timer.seconds();
          let secondsResult = seconds % 60 ? `${seconds % 60}秒` : "";

          return `${hoursResult} ${minutesResult} ${secondsResult}`;
        } else {
          return "-";
        }
      },
      align: "center",
      width: 60,
    },
    {
      title: "操作",
      width: 60,
      key: "",
      dataIndex: "",
      fixed: "right",
      align: "center",
      render: function renderFunc(text, record, index) {
        return (
          <div style={{ display: "flex", justifyContent: "space-around" }}>
            <a
              onClick={() => {
                message.success(
                  `正在下载巡检报告，双击文件夹中index.html查看报告`
                );
                //downloadFile(`/download-inspection/${record.inspection_name}`)
                fetchDetailData(record.id);
              }}
            >
              导出
            </a>
          </div>
        );
      },
    },
  ];
};

export default getColumnsConfig;
