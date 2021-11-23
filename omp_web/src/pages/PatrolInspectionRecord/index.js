import {
  OmpContentWrapper,
  OmpTable,
  OmpMessageModal,
  OmpSelect,
  OmpDrawer,
} from "@/components";
import { Button, message, Menu, Dropdown, Input, Checkbox, Form } from "antd";
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
  QuestionCircleOutlined,
} from "@ant-design/icons";
import { useHistory, useLocation } from "react-router-dom";
import PatrolInspectionDetail from "@/pages/PatrolInspectionRecord/config/detail";
const PatrolInspectionRecord = () => {
  const history = useHistory();
  const [loading, setLoading] = useState(false);
  const [pushLoading, setPushLoading] = useState(false);
  const [instanceSelectValue, setInstanceSelectValue] = useState("");

  // 深度分析modal弹框
  const [deepAnalysisModal, setDeepAnalysisModal] = useState(false);
  // 主机巡检modal弹框
  const [hostAnalysisModal, setHostAnalysisModal] = useState(false);
  // 组件巡检modal弹框
  const [componenetAnalysisModal, setComponenetAnalysisModal] = useState(false);
  // 邮件推送modal弹框
  const [pushAnalysisModal, setPushAnalysisModal] = useState(false);

  const [checkboxGroupData, setcheckboxGroupData] = useState([]);

  // ip列表
  const [ipListSource, setIpListSource] = useState([]);
  // service列表
  const [serviceListSource, setServiceListSource] = useState([]);

  const [dataSource, setDataSource] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    ordering: "",
    searchParams: {},
  });

  // 详情数据
  const [showDetail, setShowDetail] = useState({
    isShow: false,
    data: {},
  });

  // 推送表单数据
  const [pushForm] = Form.useForm();
  // 点击推送按钮数据
  const [pushInfo, setPushInfo] = useState();

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
            res.data.results.map((i, idx) => {
              return {
                ...i,
                idx: idx + 1 + (pageParams.current - 1) * pageParams.pageSize,
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

  const taskDistribution = (type, data) => {
    setLoading(true);
    fetchPost(apiRequest.inspection.taskDistribution, {
      body: {
        inspection_name: "mock",
        inspection_type: type,
        inspection_status: "1",
        execute_type: "man",
        inspection_operator: localStorage.getItem("username"),
        env: 1,
        ...data,
      },
    })
      .then((res) => {
        if (res && res.data) {
          if (res.data.code == 1) {
            message.warning(res.data.message);
          }
          if (res.data.code == 0) {
            message.success("任务已下发");
            fetchData(
              { current: pagination.current, pageSize: pagination.pageSize },
              { inspection_name: instanceSelectValue },
              pagination.ordering
            );
          }
        }
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
        setDeepAnalysisModal(false);
        setHostAnalysisModal(false);
        setComponenetAnalysisModal(false);
      });
  };

  // 巡检的主机ip列表
  const fetchIPlist = () => {
    fetchGet(apiRequest.machineManagement.ipList)
      .then((res) => {
        handleResponse(res, (res) => {
          setIpListSource(res.data);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {});
  };

  // 巡检的组件列表
  const fetchServicelist = () => {
    fetchGet(apiRequest.inspection.servicesList)
      .then((res) => {
        handleResponse(res, (res) => {
          setServiceListSource(res.data);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {});
  };

  useEffect(() => {
    fetchData();
    fetchIPlist();
    fetchServicelist();
  }, []);

  const pushEmail = () => {
    setPushLoading(true);
    fetchPost(apiRequest.inspection.pushEmail, {
      body: {
        ...pushInfo,
        to_users: pushForm.getFieldValue("email"),
      },
    })
      .then((res) => {
        console.log(res);
        if (res && res.data) {
          if (res.data.code == 1) {
            message.warning(res.data.message);
          }
          if (res.data.code == 0) {
            message.success("推送成功");
          }
        }
      })
      .catch((e) => console.log(e))
      .finally(() => setPushLoading(false));
  };

  if (showDetail.isShow) {
    return <PatrolInspectionDetail data={showDetail.data} />;
  }

  return (
    <OmpContentWrapper>
      <div style={{ display: "flex" }}>
        <Button type="primary" onClick={() => setDeepAnalysisModal(true)}>
          深度分析
        </Button>

        <Button
          type="primary"
          onClick={() => setHostAnalysisModal(true)}
          style={{ marginLeft: 10 }}
        >
          主机巡检
        </Button>

        <Button
          type="primary"
          onClick={() => setComponenetAnalysisModal(true)}
          style={{ marginLeft: 10 }}
        >
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
            { pushForm, setPushLoading, setPushAnalysisModal, setPushInfo }
            //fetchDetailData
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
        visibleHandle={[deepAnalysisModal, setDeepAnalysisModal]}
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
          taskDistribution("deep");
        }}
      >
        <div style={{ padding: "20px" }}>
          确定要执行 <span style={{ fontWeight: 500 }}>深度分析</span> 操作 ？
        </div>
      </OmpMessageModal>

      <OmpMessageModal
        afterClose={() => {
          setcheckboxGroupData([]);
        }}
        visibleHandle={[hostAnalysisModal, setHostAnalysisModal]}
        disabled={checkboxGroupData.length == 0}
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
            主机巡检
          </span>
        }
        loading={loading}
        onFinish={() => {
          taskDistribution("host", {
            hosts: checkboxGroupData,
          });
        }}
      >
        <>
          <div
            style={{
              borderBottom: "1px solid #E9E9E9",
              paddingBottom: 10,
              marginBottom: 10,
            }}
          >
            <Checkbox
              indeterminate={
                checkboxGroupData.length !== 0 &&
                checkboxGroupData.length !== ipListSource.length
              }
              // onChange={this.onCheckAllChange}
              checked={checkboxGroupData.length == ipListSource.length}
              onChange={(e) => {
                //console.log(e.target.checked)
                if (e.target.checked) {
                  setcheckboxGroupData(ipListSource);
                } else {
                  setcheckboxGroupData([]);
                }
              }}
            >
              全选
            </Checkbox>
          </div>
          <Checkbox.Group
            style={{ width: "100%" }}
            onChange={(e) => {
              setcheckboxGroupData(e);
            }}
            value={checkboxGroupData}
          >
            <div style={{ display: "flex", flexWrap: "wrap" }}>
              {ipListSource.map((item) => {
                return (
                  <div key={item} style={{ padding: "0 10px 15px 0" }}>
                    <Checkbox key={item} value={item}>
                      {item}
                    </Checkbox>
                  </div>
                );
              })}
            </div>
          </Checkbox.Group>
        </>
      </OmpMessageModal>

      <OmpMessageModal
        afterClose={() => {
          setcheckboxGroupData([]);
        }}
        visibleHandle={[componenetAnalysisModal, setComponenetAnalysisModal]}
        disabled={checkboxGroupData.length == 0}
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
            组件巡检
          </span>
        }
        loading={loading}
        onFinish={() => {
          taskDistribution("service", {
            services: checkboxGroupData,
          });
        }}
      >
        <>
          <div
            style={{
              borderBottom: "1px solid #E9E9E9",
              paddingBottom: 10,
              marginBottom: 10,
            }}
          >
            <Checkbox
              indeterminate={
                checkboxGroupData.length !== 0 &&
                checkboxGroupData.length !== serviceListSource.length
              }
              // onChange={this.onCheckAllChange}
              checked={checkboxGroupData.length == serviceListSource.length}
              onChange={(e) => {
                //console.log(e.target.checked)
                if (e.target.checked) {
                  setcheckboxGroupData(
                    serviceListSource.map((i) => i.service__id)
                  );
                } else {
                  setcheckboxGroupData([]);
                }
              }}
            >
              全选
            </Checkbox>
          </div>
          <Checkbox.Group
            style={{ width: "100%" }}
            onChange={(e) => {
              setcheckboxGroupData(e);
            }}
            value={checkboxGroupData}
          >
            <div style={{ display: "flex", flexWrap: "wrap" }}>
              {serviceListSource.map((item) => {
                return (
                  <div
                    key={item.service__id}
                    style={{ padding: "0 10px 15px 0" }}
                  >
                    <Checkbox key={item.service__id} value={item.service__id}>
                      {item.service__app_name}
                    </Checkbox>
                  </div>
                );
              })}
            </div>
          </Checkbox.Group>
        </>
      </OmpMessageModal>

      <OmpMessageModal
        visibleHandle={[pushAnalysisModal, setPushAnalysisModal]}
        title={<span>邮件推送</span>}
        loading={pushLoading}
        onFinish={() => pushEmail()}
      >
        <Form style={{ marginLeft: 40 }} form={pushForm}>
          <Form.Item
            name="email"
            label="接收人"
            rules={[
              {
                type: "email",
                message: "请输入正确格式的邮箱",
              },
            ]}
          >
            <Input
              placeholder="例如: emailname@163.com"
              style={{
                width: 320,
              }}
            />
          </Form.Item>
          <p
            style={{
              marginTop: 30,
              paddingLeft: 40,
              fontSize: 13,
            }}
          >
            <ExclamationCircleOutlined style={{ paddingRight: 10 }} />
            如果需要配置默认的巡检报告接收人，请点击
            <a
              onClick={() =>
                history.push({
                  pathname: "/status-patrol/patrol-strategy",
                })
              }
              style={{ marginLeft: 4 }}
            >
              这里
            </a>
          </p>
        </Form>
      </OmpMessageModal>
    </OmpContentWrapper>
  );
};

export default PatrolInspectionRecord;
