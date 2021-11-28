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
//import updata from "@/store_global/globalStore";
import { useDispatch } from "react-redux";
import moment from "moment";
import { SearchOutlined, SettingFilled } from "@ant-design/icons";

const InstallationRecord = () => {
  const dispatch = useDispatch();

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
      title: "编号",
      width: 80,
      key: "_idx",
      dataIndex: "_idx",
      //sorter: (a, b) => a.username - b.username,
      // sortDirections: ["descend", "ascend"],
      align: "center",
      render: nonEmptyProcessing,
      fixed: "left",
    },
    {
      title: "执行用户",
      key: "username",
      width: 120,
      dataIndex: "username",
      //sorter: (a, b) => a.username - b.username,
      // sortDirections: ["descend", "ascend"],
      align: "center",
      render: nonEmptyProcessing,
    },
    {
      title: "状态",
      key: "is_superuser",
      dataIndex: "is_superuser",
      width: 100,
      //sorter: (a, b) => a.is_superuser - b.is_superuser,
      //sortDirections: ["descend", "ascend"],
      align: "center",
      render: (text) => {
        if (text) {
          return "普通管理员";
        } else {
          return "超级管理员";
        }
      },
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
      key: "date_joined",
      dataIndex: "date_joined",
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
            // onClick={() => {
            //   setRow(record);
            //   setShowModal(true);
            // }}
            style={{ display: "flex", justifyContent: "space-around" }}
          >
            <a>查看</a>
          </div>
        );
      },
    },
  ];

  //auth/users
  function fetchData(
    pageParams = { current: 1, pageSize: 10 },
  ) {
    setLoading(true);
    fetchGet(apiRequest.installHistoryPage.queryInstallHistoryList, {
      params: {
        page: pageParams.current,
        size: pageParams.pageSize,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          console.log(res)
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
              fetchData(
                { current: pagination.current, pageSize: pagination.pageSize },
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
