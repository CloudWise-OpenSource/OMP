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
  renderDisc
} from "@/utils/utils";
import { fetchGet, fetchPost } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
//import updata from "@/store_global/globalStore";
import moment from "moment";
import { useHistory } from "react-router-dom";

// const renderStatus = {
//   0: "等待安装",
//   1: "安装中",
//   2: "安装成功",
//   3: <span style={{ color: "#da4e48" }}>安装失败</span>,
// };

const renderStatus = (text) => {
  switch (text) {
    case 0:
      return <span>{renderDisc("warning", 7, -1)}等待安装</span>;
    case 1:
      return <span>{renderDisc("warning", 7, -1)}正在安装</span>;
    case 2:
      return <span>{renderDisc("normal", 7, -1)}成功</span>;
    case 3:
      return <span>{renderDisc("critical", 7, -1)}失败</span>;
    default:
      return "-";
  }
};

const InstallationRecord = () => {
  const [loading, setLoading] = useState(false);
  const history = useHistory();
  //table表格数据
  const [dataSource, setDataSource] = useState([]);

  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    ordering: "",
    searchParams: {},
  });

  const columns = [
    {
      title: "编号",
      width: 80,
      key: "_idx",
      dataIndex: "_idx",
      //sorter: (a, b) => a.username - b.username,
      // sortDirections: ["descend", "ascend"],
      align: "center",
      fixed: "left",
      render: (text, record, idx) => {
        //history.push()
        return idx + 1 + (pagination.current - 1) * pagination.pageSize;
      },
    },
    {
      title: "执行用户",
      key: "operator",
      width: 100,
      dataIndex: "operator",
      //sorter: (a, b) => a.username - b.username,
      // sortDirections: ["descend", "ascend"],
      align: "center",
      render: nonEmptyProcessing,
    },
    {
      title: "状态",
      key: "install_status",
      dataIndex: "install_status",
      width: 100,
      //sorter: (a, b) => a.is_superuser - b.is_superuser,
      //sortDirections: ["descend", "ascend"],
      align: "center",
      render: (text) => {
        return renderStatus(text);
      },
      // render: (text) => {
      //   if (text) {
      //     return "普通管理员";
      //   } else {
      //     return "超级管理员";
      //   }
      // },
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
      title: "开始时间",
      key: "created",
      dataIndex: "created",
      align: "center",
      width: 120,
      render: (text) => {
        if (text) {
          return moment(text).format("YYYY-MM-DD HH:mm:ss");
        } else {
          return "-";
        }
      },
    },
    // {
    //   title: "描述",
    //   key: "describe",
    //   dataIndex: "describe",
    //   align: "center",
    //   render: nonEmptyProcessing,
    // },
    {
      title: "操作",
      key: "1",
      width: 80,
      dataIndex: "1",
      align: "center",
      fixed: "right",
      render: function renderFunc(text, record, index) {
        return (
          <div
            onClick={() => {
              history.push({
                pathname: "/application_management/app_store/installation",
                state: {
                  uniqueKey: record.operation_uuid,
                  step:3
                },
              });
            }}
            style={{ display: "flex", justifyContent: "space-around" }}
          >
            <a>查看</a>
          </div>
        );
      },
    },
  ];

  //auth/users
  function fetchData(pageParams = { current: 1, pageSize: 10 }) {
    setLoading(true);
    fetchGet(apiRequest.installHistoryPage.queryInstallHistoryList, {
      params: {
        page: pageParams.current,
        size: pageParams.pageSize,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          console.log(res);
          setDataSource(res.data.results);
          setPagination({
            ...pagination,
            total: res.data.count,
            pageSize: pageParams.pageSize,
            current: pageParams.current,
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
          <Button
            style={{ marginLeft: 10 }}
            onClick={() => {
              // console.log(pagination, "hosts/hosts/?page=1&size=10");
              fetchData({
                current: pagination.current,
                pageSize: pagination.pageSize,
              });
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
          loading={loading}
          onChange={(e, filters, sorter) => {
            setTimeout(() => {
              fetchData(e);
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

export default InstallationRecord;
