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
} from "@/utils/utils";
import { fetchGet, fetchPost } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import moment from "moment";
import { SearchOutlined, SettingFilled } from "@ant-design/icons";

const TaskRecord = () => {
  const [loading, setLoading] = useState(false);

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
      width: 40,
      key: "_idx",
      dataIndex: "_idx",
      //sorter: (a, b) => a.username - b.username,
      // sortDirections: ["descend", "ascend"],
      align: "center",
      render: nonEmptyProcessing,
      fixed: "left",
    },
    {
      title: "分类",
      key: "username",
      width: 100,
      dataIndex: "username",
      sorter: (a, b) => a.username - b.username,
      sortDirections: ["descend", "ascend"],
      align: "center",
      render: nonEmptyProcessing,
    },
    {
      title: "执行时间",
      key: "ip",
      dataIndex: "ip",
      width: 100,
      sorter: (a, b) => a.ip - b.ip,
      sortDirections: ["descend", "ascend"],
      align: "center",
      render: nonEmptyProcessing,
    },
    {
      title: "状态",
      key: "role",
      dataIndex: "role",
      width: 100,
      sorter: (a, b) => a.role - b.role,
      sortDirections: ["descend", "ascend"],
      align: "center",
      render: nonEmptyProcessing,
    },
    // {
    //   title: "用户状态",
    //   key: "is_active",
    //   dataIndex: "is_active",
    //   align: "center",
    //   width: 100,
    //   render: (text) => {
    //     if (text) {
    //       return "正常";
    //     } else {
    //       return "停用";
    //     }
    //   },
    // },
    {
      title: "执行用时",
      key: "login_time",
      dataIndex: "login_time",
      align: "center",
      width: 100,
      sorter: (a, b) => a.login_time - b.login_time,
      sortDirections: ["descend", "ascend"],
      // render: (text) => {
      //   if (text) {
      //     return moment(text).format("YYYY-MM-DD HH:mm:ss");
      //   } else {
      //     return "-";
      //   }
      // },
      render: nonEmptyProcessing,
    },
  ];

  function fetchData(
    pageParams = { current: 1, pageSize: 10 },
    searchParams,
    ordering
  ) {
    setLoading(true);
    fetchGet(apiRequest.operationRecord.queryLoginLog, {
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
          <span style={{ width: 60, display: "flex", alignItems: "center" }}>
            用户名:
          </span>
          <Input
            placeholder="请输入用户名"
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
                    username: null,
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
                  username: selectValue,
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
                  username: selectValue,
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
                { username: selectValue },
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
