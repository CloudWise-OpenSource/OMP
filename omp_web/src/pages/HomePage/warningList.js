import {
  OmpContentWrapper,
  OmpTable,
  OmpMessageModal,
  OmpSelect,
  OmpDatePicker,
  OmpDrawer,
} from "@/components";
import {
  Button,
  Select,
  message,
  Menu,
  Dropdown,
  Modal,
  Input,
  Tooltip,
  Badge,
} from "antd";
import { useState, useEffect, useRef } from "react";
import {
  handleResponse,
  _idxInit,
  refreshTime,
  colorConfig,
} from "@/utils/utils";
import { fetchGet, fetchPost, fetchPatch } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { SearchOutlined } from "@ant-design/icons";
import moment from "moment";
import { useHistory } from "react-router-dom";

const ExceptionList = () => {
  const history = useHistory();
  const [loading, setLoading] = useState(false);
  //table表格数据
  const [dataSource, setDataSource] = useState([]);

  const [searchParams, setSearchParams] = useState({});

  const [showIframe, setShowIframe] = useState({});

  const [pageSize, setPageSize] = useState(5);

  function fetchData(searchParams = {}, noLoading) {
    !noLoading && setLoading(true);
    fetchGet(apiRequest.ExceptionList.exceptionList, {
      params: {
        ...searchParams,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          setSearchParams(searchParams);
          setDataSource(
            res.data.map((item, idx) => ({
              ...item,
              key: idx + item.ip,
            }))
          );
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  }

  useEffect(() => {
    fetchData(null, true);
  }, []);

  return (
    <OmpContentWrapper>
      <div
        style={{
          border: "1px solid #ebeef2",
          backgroundColor: "white",
          marginTop: 10,
          //fontSize:12
        }}
      >
        <OmpTable
          size="small"
          loading={loading}
          //scroll={{ x: 1400 }}
          onChange={(e, filters, sorter) => {
            setPageSize(e.pageSize);
            if (sorter.columnKey) {
              let sort = sorter.order == "descend" ? 0 : 1;
              setTimeout(() => {
                fetchData({
                  ...searchParams,
                  ordering: sorter.column ? sorter.columnKey : null,
                  asc: sorter.column ? sort : null,
                });
              }, 200);
            }
          }}
          columns={getColumnsConfig(
            (params) => {
              fetchData({ ...searchParams, ...params });
            },
            setShowIframe,
            history
          )}
          dataSource={dataSource}
          pagination={{
            showSizeChanger: true,
            pageSizeOptions: ["5", "10", "20", "50"],
            showTotal: () => (
              <div
                style={{
                  display: "flex",
                  width: "200px",
                  //justifyContent: "space-between",
                  flexDirection: "row-reverse",
                  lineHeight: 2.8,
                }}
              >
                <p
                  style={{
                    color: "rgb(152, 157, 171)",
                    position: "relative",
                    top: -4,
                  }}
                >
                  共计{" "}
                  <span style={{ color: "rgb(63, 64, 70)" }}>
                    {dataSource?.length}
                  </span>{" "}
                  条
                </p>
              </div>
            ),
            pageSize: pageSize,
          }}
          //rowKey={(record) => record.ip}
          //checkedState={[checkedList, setCheckedList]}
        />
      </div>
      <OmpDrawer showIframe={showIframe} setShowIframe={setShowIframe} />
    </OmpContentWrapper>
  );
};

const getColumnsConfig = (
  queryRequest,
  setShowIframe,
  //updateAlertRead,
  history
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
              <span style={{ fontSize: 12 }}>
                {record.instance_name ? record.instance_name : "-"}
              </span>
            </Badge>
          </Tooltip>
        );
      },
    },
    {
      title: "IP地址",
      key: "ip",
      dataIndex: "ip",
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
            <div style={{ margin: "auto" }}>
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
                <a
                  style={{ marginLeft: 10 }}
                  onClick={() =>
                    history.push({
                      pathname: "/status-patrol/patrol-inspection-record",
                    })
                  }
                >
                  分析
                </a>
              ) : record.log_url ? (
                <a
                  style={{ marginLeft: 10 }}
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
                <span style={{ color: "rgba(0, 0, 0, 0.25)", marginLeft: 10 }}>
                  日志
                </span>
              )}
            </div>
          </div>
        );
      },
    },
  ];
};

export default ExceptionList;
