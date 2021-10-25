import {
  OmpContentWrapper,
  OmpTable,
  OmpMessageModal,
  OmpSelect,
  OmpDrawer,
} from "@/components";
import { Button, message, Menu, Dropdown, Input } from "antd";
import { useState, useEffect, useRef } from "react";
import { handleResponse, _idxInit } from "@/utils/utils";
import { fetchGet, fetchPost, fetchPatch } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { useDispatch } from "react-redux";
import getColumnsConfig from "./config/columns";
import {
  DownOutlined,
  ExclamationCircleOutlined,
  SearchOutlined,
  QuestionCircleOutlined
} from "@ant-design/icons";
import { useHistory, useLocation } from "react-router-dom";
const PatrolInspectionRecord = () => {
  const history = useHistory();
  const [loading, setLoading] = useState(false);
  const [instanceSelectValue, setInstanceSelectValue] = useState("");

  // 深度分析modal弹框
  const [deepAnalysisModal, setDeepAnalysisModal] = useState(false);
  // 主机巡检modal弹框
  const [hostAnalysisModal, setHostAnalysisModal] = useState(false);
  // 组件巡检modal弹框
  const [componenetAnalysisModal, setComponenetAnalysisModal] = useState(false);

  const [dataSource, setDataSource] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    ordering: "",
    searchParams: {},
  });
  function fetchData(
    pageParams = { current: 1, pageSize: 10 },
    searchParams = {},
    ordering
  ) {
    setLoading(true);
    fetchGet(apiRequest.inspection.inspectionList, {
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
            res.data.results.map((i) => {
              return {
                ...i,
                key: i.id,
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

  const fetchDetailData = (id, setData) => {
    fetchGet(`${apiRequest.inspection.reportDetail}/${id}/`, {
      // params: {
      //   page: pageParams.current,
      //   size: pageParams.pageSize,
      //   ordering: ordering ? ordering : null,
      //   ...searchParams,
      // },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          console.log(res);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        //setLoading(false);
      });
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <OmpContentWrapper>
      <div style={{ display: "flex" }}>
        <Button type="primary" onClick={()=>setDeepAnalysisModal(true)}>深度分析</Button>

        <Button type="primary" style={{ marginLeft: 10 }}>
          主机巡检
        </Button>

        <Button type="primary" style={{ marginLeft: 10 }}>
          组件巡检
        </Button>

        <div style={{ display: "flex", marginLeft: "auto" }}>
          <span style={{ width: 80, display: "flex", alignItems: "center" }}>
            报告名称:
          </span>
          <Input
            placeholder="输入报告名称"
            style={{ width: 200 }}
            allowClear
            value={instanceSelectValue}
            onChange={(e) => {
              setInstanceSelectValue(e.target.value);
              if (!e.target.value) {
                fetchData(
                  { current: 1, pageSize: pagination.pageSize },
                  {
                    ...pagination.searchParams,
                    inspection_name: null,
                  }
                );
              }
            }}
            onBlur={() => {
              if (instanceSelectValue) {
                fetchData(
                  { current: 1, pageSize: pagination.pageSize },
                  {
                    ...pagination.searchParams,
                    inspection_name: instanceSelectValue,
                  }
                );
              }
            }}
            onPressEnter={() => {
              fetchData(
                { current: 1, pageSize: pagination.pageSize },
                {
                  ...pagination.searchParams,
                  inspection_name: instanceSelectValue,
                }
              );
            }}
            suffix={
              !instanceSelectValue && (
                <SearchOutlined style={{ fontSize: 12, color: "#b6b6b6" }} />
              )
            }
          />
          <Button
            style={{ marginLeft: 10 }}
            onClick={() => {
              fetchData(
                { current: pagination.current, pageSize: pagination.pageSize },
                { inspection_name: instanceSelectValue },
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
          loading={loading}
          //   /scroll={{ x: 1900 }}
          onChange={(e, filters, sorter) => {
            console.log("ui");
            let ordering = sorter.order
              ? `${sorter.order == "descend" ? "" : "-"}${sorter.columnKey}`
              : null;
            setTimeout(() => {
              fetchData(e, pagination.searchParams, ordering);
            }, 200);
          }}
          columns={getColumnsConfig(
            (params) => {
              // console.log(pagination.searchParams)
              fetchData(
                { current: 1, pageSize: pagination.pageSize },
                { ...pagination.searchParams, ...params },
                pagination.ordering
              );
            },
            history,
            fetchDetailData
          )}
          dataSource={dataSource}
          pagination={{
            showSizeChanger: true,
            pageSizeOptions: ["10", "20", "50", "100"],
            showTotal: () => (
              <div
                style={{
                  display: "flex",
                  width: "200px",
                  flexDirection: "row-reverse",
                  lineHeight: 2.8,
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
        />
      </div>
      <OmpMessageModal
        visibleHandle={[deepAnalysisModal, setDeepAnalysisModal] }
        title={
          <span>
            <ExclamationCircleOutlined
              style={{
                fontSize: 20,
                color: "#f0a441",
                paddingRight: "10px",
                position: "relative",
                top: 2,
              }}
            />
            提示
          </span>
        }
        loading={loading}
        onFinish={() => {
          //fetchRestartMonitorAgent();
        }}
      >
        <div style={{ padding: "20px" }}>
          确定要执行 <span style={{ fontWeight: 500 }}>深度分析</span> 操作 ？
        </div>
      </OmpMessageModal>
    </OmpContentWrapper>
  );
};

export default PatrolInspectionRecord;