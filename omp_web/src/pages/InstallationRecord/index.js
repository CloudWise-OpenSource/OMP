import { OmpContentWrapper, OmpTable } from "@/components";
import { useState, useEffect } from "react";
import { useHistory } from "react-router-dom";
import { fetchGet } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { Button } from "antd";
import {
  handleResponse,
  _idxInit,
  nonEmptyProcessing,
  renderDisc,
} from "@/utils/utils";
import moment from "moment";
import ServiceRollbackModal from "../AppStore/config/ServiceRollbackModal";

const renderStatus = (record) => {
  let text = record.state;
  if (text.includes("SUCCESS")) {
    return (
      <span>
        {renderDisc("normal", 7, -1)}
        {record.state_display}
      </span>
    );
  }
  if (text.includes("FAIL")) {
    return (
      <span>
        {renderDisc("critical", 7, -1)}
        {record.state_display}
      </span>
    );
  }
  if (text.includes("WAIT") || text.includes("ING")) {
    return (
      <span>
        {renderDisc("warning", 7, -1)}
        {record.state_display}
      </span>
    );
  }
  return "-";
};

const typeMap = {
  MainInstallHistory: "安装",
  RollbackHistory: "回滚",
  UpgradeHistory: "升级",
};

const notProhibit = {
  cursor: "not-allowed",
  color: "#bbbbbb",
};

const InstallationRecord = () => {
  const history = useHistory();

  const [loading, setLoading] = useState(false);
  //table表格数据
  const [dataSource, setDataSource] = useState([]);

  const [vfModalVisibility, setVfModalVisibility] = useState(false);

  const [rowId, setRowId] = useState("");

  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    ordering: "",
    searchParams: {},
  });

  const columns = [
    {
      title: "类型",
      width: 80,
      key: "module",
      dataIndex: "module",
      //sorter: (a, b) => a.username - b.username,
      // sortDirections: ["descend", "ascend"],
      usefilter: true,
      queryRequest: (params) => {
        fetchData(
          { current: 1, pageSize: pagination.pageSize },
          pagination.ordering,
          { ...pagination.searchParams, ...params }
        );
      },
      // initfilter: initfilterAppType,
      filterMenuList: Object.keys(typeMap).map((k) => {
        return {
          value: k,
          text: typeMap[k],
        };
      }),
      align: "center",
      fixed: "left",
      render: (text, record, idx) => {
        //history.push()
        return typeMap[text];
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
      render: (text, record) => {
        return renderStatus(record);
      },
    },
    {
      title: "服务数量",
      key: "count",
      dataIndex: "count",
      width: 60,
      align: "center",
      render: nonEmptyProcessing,
    },
    {
      title: "开始时间",
      key: "created",
      dataIndex: "created",
      align: "center",
      width: 120,
      sorter: (a, b) => a.created - b.created,
      sortDirections: ["descend", "ascend"],
      render: (text) => {
        if (text) {
          return moment(text).format("YYYY-MM-DD HH:mm:ss");
        } else {
          return "-";
        }
      },
    },
    {
      title: "结束时间",
      key: "end_time",
      dataIndex: "end_time",
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
      title: "用时",
      key: "duration",
      dataIndex: "duration",
      align: "center",
      width: 120,
      render: nonEmptyProcessing,
    },
    {
      title: "操作",
      key: "1",
      width: 58,
      dataIndex: "1",
      align: "center",
      fixed: "right",
      render: function renderFunc(text, record, index) {
        switch (record.module) {
          case "MainInstallHistory":
            return (
              <div style={{ display: "flex", justifyContent: "space-around" }}>
                <div
                  onClick={() => {
                    history.push({
                      pathname:
                        "/application_management/app_store/installation",
                      state: {
                        uniqueKey: record.module_id,
                        step: 3,
                      },
                    });
                  }}
                  style={{ display: "flex", justifyContent: "space-around" }}
                >
                  <a>查看</a>
                </div>
              </div>
            );
            break;
          case "RollbackHistory":
            return (
              <div style={{ display: "flex", justifyContent: "space-around" }}>
                <div
                  onClick={() => {
                    history.push({
                      pathname:
                        "/application_management/app_store/service_rollback",
                      state: {
                        history: record.module_id,
                      },
                    });
                  }}
                >
                  <a>查看</a>
                </div>
              </div>
            );
            break;
          case "UpgradeHistory":
            return (
              <div style={{ display: "flex", justifyContent: "space-around" }}>
                <div style={{ margin: "auto" }}>
                  <a
                    onClick={() => {
                      history.push({
                        pathname:
                          "/application_management/app_store/service_upgrade",
                        state: {
                          history: record.module_id,
                        },
                      });
                    }}
                  >
                    查看
                  </a>
                  <a
                    style={
                      record.can_rollback
                        ? { marginLeft: 10 }
                        : {
                            marginLeft: 10,
                            ...notProhibit,
                          }
                    }
                    onClick={() => {
                      if (record.can_rollback) {
                        setRowId(record.module_id);
                        setVfModalVisibility(true);
                      }
                    }}
                  >
                    回滚
                  </a>
                </div>
              </div>
            );
            break;
          default:
            return "-";
            break;
        }
      },
    },
  ];

  function fetchData(
    pageParams = { current: 1, pageSize: 10 },
    ordering,
    searchParams
  ) {
    console.log(searchParams);
    setLoading(true);
    fetchGet(apiRequest.installHistoryPage.queryAllList, {
      params: {
        page: pageParams.current,
        size: pageParams.pageSize,
        ordering: ordering ? ordering : null,
        search: searchParams?.module,
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
    <OmpContentWrapper wrapperStyle={{ paddingBottom: 0 }}>
      <div style={{ display: "flex" }}>
        <div style={{ display: "flex", marginLeft: "auto" }}>
          <Button
            style={{ marginLeft: 10 }}
            onClick={() => {
              // console.log(pagination, "hosts/hosts/?page=1&size=10");
              fetchData(
                {
                  current: pagination.current,
                  pageSize: pagination.pageSize,
                },
                pagination.ordering,
                pagination.searchParams
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
              fetchData(e, ordering, pagination.searchParams);
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
      <ServiceRollbackModal
        sRModalVisibility={vfModalVisibility}
        setSRModalVisibility={setVfModalVisibility}
        initLoading={loading}
        fixedParams={`?history_id=${rowId}`}
      />
    </OmpContentWrapper>
  );
};

export default InstallationRecord;
