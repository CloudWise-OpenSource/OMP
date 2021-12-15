import { OmpContentWrapper, OmpTable } from "@/components";
import { Button } from "antd";
import { useState, useEffect } from "react";
import {
  handleResponse,
  _idxInit,
  nonEmptyProcessing,
  renderDisc,
} from "@/utils/utils";
import { fetchGet, fetchPost } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import moment from "moment";
import ServiceUpgradeModal from "../config/ServiceUpgradeModal";

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
    case 4:
      return <span>{renderDisc("notMonitored", 7, -1)}正在注册</span>;
    default:
      return "-";
  }
};

const Upgrade = ({ history }) => {
  const [loading, setLoading] = useState(false);
  //table表格数据
  const [dataSource, setDataSource] = useState([]);

  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    ordering: "",
    searchParams: {},
  });

  const [vfModalVisibility, setVfModalVisibility] = useState(false);

  const [serviceList, setServiceList] = useState([]);

  const columns = [
    {
      title: "编号",
      width: 40,
      key: "_idx",
      dataIndex: "_idx",
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
      align: "center",
      render: nonEmptyProcessing,
    },
    {
      title: "服务数量",
      key: "operator",
      width: 60,
      dataIndex: "operator",
      align: "center",
      render: nonEmptyProcessing,
    },
    {
      title: "状态",
      key: "install_status",
      dataIndex: "install_status",
      width: 100,
      align: "center",
      render: (text) => {
        return renderStatus(text);
      },
    },
    {
      title: "升级时间",
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
    {
      title: "回滚时间",
      key: "modified",
      dataIndex: "modified",
      align: "center",
      width: 120,
      render: (text, record) => {
        if (record.install_status == 1) {
          return "-";
        }
        if (text) {
          return moment(text).format("YYYY-MM-DD HH:mm:ss");
        } else {
          return "-";
        }
      },
    },
    {
      title: "操作",
      key: "1",
      width: 50,
      dataIndex: "1",
      align: "center",
      fixed: "right",
      render: function renderFunc(text, record, index) {
        return (
          <div style={{ display: "flex", justifyContent: "space-around" }}>
            <div>
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
                查看
              </a>
              <a
                style={{ marginLeft: 10 }}
                onClick={() => {
                  setVfModalVisibility(true);
                }}
              >
                回滚
              </a>
            </div>
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
          noScroll={true}
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
      <ServiceUpgradeModal
        vfModalVisibility={vfModalVisibility}
        setVfModalVisibility={setVfModalVisibility}
        dataSource={serviceList}
        // installTitle={installTitle.current}
        initLoading={loading}
      />
    </OmpContentWrapper>
  );
};

export default Upgrade;
