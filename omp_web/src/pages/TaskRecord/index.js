import { OmpContentWrapper, OmpTable, OmpModal } from "@/components";
import { Button, Input, Form, message, Menu } from "antd";
import { useState, useEffect, useRef } from "react";
import {
  handleResponse,
  _idxInit,
  refreshTime,
  MessageTip,
  nonEmptyProcessing,
  logout,
  isPassword,
  renderDisc,
} from "@/utils/utils";
import { fetchGet, fetchPost } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import moment from "moment";
import { SearchOutlined, SettingFilled } from "@ant-design/icons";
import { useHistory, useLocation } from "react-router-dom";

const kindMap = ["管理工具", "检查工具", "安全工具", "其他工具"];

const TaskRecord = () => {
  const [loading, setLoading] = useState(false);

  const history = useHistory();

  //table表格数据
  const [dataSource, setDataSource] = useState([]);
  const [selectValue, setSelectValue] = useState();

  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    ordering: "",
    searchParams: {},
  });

  const columns = [
    {
      title: "任务标题",
      width: 100,
      key: "task_name",
      dataIndex: "task_name",
      //sorter: (a, b) => a.username - b.username,
      // sortDirections: ["descend", "ascend"],
      align: "center",
      fixed: "left",
      render:(text, record)=>{
        if(!text){
          return "-"
        }
        return <a onClick={()=>{
          history.push(
            `/utilitie/tool-management/tool-execution-results/${
              record.id
            }`
          );
        }}>{text}</a>
      }
    },
    {
      title: "分类",
      key: "kind",
      width: 100,
      dataIndex: "kind",
      align: "center",
      usefilter: true,
      queryRequest: (params) => {
        fetchData(
          { current: 1, pageSize: pagination.pageSize },
          { ...pagination.searchParams, ...params },
          pagination.ordering
        );
      },
      filterMenuList: [
        {
          value: 0,
          text: "管理工具",
        },
        {
          value: 1,
          text: "检查工具",
        },
        {
          value: 2,
          text: "安全工具",
        },
        {
          value: 3,
          text: "其他工具",
        },
      ],
      render: (text) => {
        return kindMap[text];
      },
    },
    {
      title: "执行时间",
      key: "start_time",
      dataIndex: "start_time",
      width: 100,
      sorter: (a, b) => a.start_time - b.start_time,
      sortDirections: ["descend", "ascend"],
      align: "center",
      render: (text)=>{
        return text ? moment(text).format("YYYY-MM-DD HH:mm:ss") : "-";
      },
    },
    {
      title: "状态",
      key: "status",
      dataIndex: "status",
      width: 100,
      align: "center",
      render: (text, record, index) => {
        if (!text && text !== 0) {
          return "-";
        } else if (text === 0) {
          return <div>{renderDisc("warning", 7, -1)}待执行</div>;
        } else if (text === 1) {
          return <div>{renderDisc("warning", 7, -1)}执行中</div>;
        } else if (text === 2) {
          return <div>{renderDisc("normal", 7, -1)}执行成功</div>;
        } else if (text === 3) {
          return <div>{renderDisc("critical", 7, -1)}执行失败</div>;
        } else {
          return text;
        }
      },
    },
    {
      title: "执行用时",
      key: "duration",
      dataIndex: "duration",
      align: "center",
      width: 100,
      render: nonEmptyProcessing,
    },
    {
      title: "操作",
      width: 60,
      key: "",
      dataIndex: "",
      align: "center",
      fixed: "right",
      render: function renderFunc(text, record, index) {
        return (
          <div style={{ display: "flex", justifyContent: "space-around" }}>
            <div style={{ margin: "auto" }}>
              <a onClick={() => {
                 history.push(
                  `/utilitie/tool-management/tool-execution-results/${
                    record.id
                  }`
                );
              }}>查看</a>
            </div>
          </div>
        );
      },
    },
  ];

  function fetchData(
    pageParams = { current: 1, pageSize: 10 },
    searchParams,
    ordering
  ) {
    setLoading(true);
    fetchGet(apiRequest.utilitie.queryHistory, {
      params: {
        page: pageParams.current,
        size: pageParams.pageSize,
        ordering: ordering ? ordering : null,
        ...searchParams,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          setDataSource(
            res.data.results.map((item, idx) => {
              return {
                ...item,
                _idx: idx + 1 + (pageParams.current - 1) * pageParams.pageSize,
              };
            })
          );
          setPagination({
            ...pagination,
            total: res.data.count,
            pageSize: pageParams.pageSize,
            current: pageParams.current,
            ordering: ordering,
            searchParams: searchParams,
          });
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  }

  useEffect(() => {
    fetchData(pagination);
  }, []);

  return (
    <OmpContentWrapper>
      <div style={{ display: "flex" }}>
        <div style={{ display: "flex", marginLeft: "auto" }}>
          <span style={{ width: 50, display: "flex", alignItems: "center" }}>
            名称:
          </span>
          <Input
            placeholder="搜索名称"
            style={{ width: 200 }}
            allowClear
            value={selectValue}
            onChange={(e) => {
              setSelectValue(e.target.value);
              if (!e.target.value) {
                fetchData(
                  {
                    current: 1,
                    pageSize: pagination.pageSize,
                  },
                  {
                    ...pagination.searchParams,
                    search: null,
                  }
                );
              }
            }}
            onBlur={() => {
              fetchData(
                {
                  current: 1,
                  pageSize: pagination.pageSize,
                },
                {
                  ...pagination.searchParams,
                  search: selectValue,
                }
              );
            }}
            onPressEnter={() => {
              fetchData(
                {
                  current: 1,
                  pageSize: pagination.pageSize,
                },
                {
                  ...pagination.searchParams,
                  search: selectValue,
                },
                pagination.ordering
              );
            }}
            suffix={
              !selectValue && (
                <SearchOutlined style={{ fontSize: 12, color: "#b6b6b6" }} />
              )
            }
          />
          <Button
            style={{ marginLeft: 10 }}
            onClick={() => {
              fetchData(
                { current: pagination.current, pageSize: pagination.pageSize },
                {  search: selectValue },
                pagination.ordering
              );
            }}
          >
            刷新
          </Button>
        </div>
      </div>
      <div
        style={{
          border: "1px solid #ebeef2",
          backgroundColor: "white",
          marginTop: 10,
        }}
      >
        <OmpTable
          noScroll={true}
          loading={loading}
          onChange={(e, filters, sorter) => {
            let ordering = sorter.order
              ? `${sorter.order == "descend" ? "" : "-"}${sorter.columnKey}`
              : null;
            setTimeout(() => {
              fetchData(e, pagination.searchParams, ordering);
            }, 200);
          }}
          columns={columns}
          dataSource={dataSource}
          pagination={{
            showSizeChanger: true,
            pageSizeOptions: ["10", "20", "50", "100"],
            showTotal: () => (
              <div
                style={{
                  display: "flex",
                  width: "200px",
                  lineHeight: 2.8,
                  flexDirection: "row-reverse",
                }}
              >
                <p style={{ color: "rgb(152, 157, 171)" }}>
                  共计{" "}
                  <span style={{ color: "rgb(63, 64, 70)" }}>
                    {pagination.total}
                  </span>{" "}
                  条
                </p>
              </div>
            ),
            ...pagination,
          }}
          rowKey={(record) => record.id}
        />
      </div>
    </OmpContentWrapper>
  );
};

export default TaskRecord;
