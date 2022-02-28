import {
  OmpContentWrapper,
  OmpTable,
  OmpModal,
  OmpMessageModal,
} from "@/components";
import {
  Button,
  Input,
  Form,
  message,
  Menu,
  Dropdown,
  Select,
  Radio,
  Cascader,
  Tooltip,
  InputNumber,
  Switch,
  Modal,
  Table,
} from "antd";
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
import { fetchGet, fetchPost, fetchDelete } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import moment from "moment";
import {
  SearchOutlined,
  SettingFilled,
  DownOutlined,
  PlusSquareOutlined,
  QuestionCircleOutlined,
  ExclamationCircleOutlined,
} from "@ant-design/icons";
import { useHistory, useLocation } from "react-router-dom";

const RuleIndicator = () => {
  const [loading, setLoading] = useState(false);
  const [modalForm] = Form.useForm();

  const [upDateForm] = Form.useForm();
  const history = useHistory();
  //选中的数据
  const [checkedList, setCheckedList] = useState([]);

  const [row, setRow] = useState({});

  // 测试展示数据
  const [testQueryResults, setTestQueryResults] = useState([]);
  // 测试弹框控制器
  const [testVisible, setTestVisible] = useState(false);

  // 批量停用弹框控制器
  const [stopVisible, setStopVisible] = useState(false);
  // 单独停用弹框控制器
  const [stopRowVisible, setStopRowVisible] = useState(false);

  // 批量启用弹框控制器
  const [startVisible, setStartVisible] = useState(false);
  // 单独启用弹框控制器
  const [startRowVisible, setStartRowVisible] = useState(false);

  //table表格数据
  const [dataSource, setDataSource] = useState([]);
  const [selectValue, setSelectValue] = useState();

  // 添加规则控制器
  const [addMoadlVisible, setAddMoadlVisible] = useState(false);

  // 修改规则控制器
  const [upDateVisible, setUpDateVisible] = useState(false);

  // 删除规则控制器
  const [deleteMoadlVisible, setDeleteMoadlVisible] = useState(false);

  // 规则类型
  const [ruleType, setRuleType] = useState("0");

  // 持续时长单位
  const [forTimeCompany, setForTimeCompany] = useState("s");

  // 选择内置规则联级数据
  const [cascaderOption, setCascaderOption] = useState([]);

  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    ordering: "",
    searchParams: {},
  });

  const columns = [
    {
      title: "规则名称",
      // width: 60,
      key: "alert",
      dataIndex: "alert",
      //sorter: (a, b) => a.username - b.username,
      // sortDirections: ["descend", "ascend"],
      align: "center",
      width: 250,
      fixed: "left",
      ellipsis: true,
    },
    {
      title: "对比规则",
      key: "compare_str",
      width: 120,
      dataIndex: "compare_str",
      align: "center",
    },
    {
      title: "阈值",
      key: "threshold_value",
      dataIndex: "threshold_value",
      width: 120,
      align: "center",
    },
    {
      title: "持续时长(s)",
      key: "for_time",
      dataIndex: "for_time",
      width: 120,
      align: "center",
    },
    {
      title: "级别",
      key: "severity",
      dataIndex: "severity",
      align: "center",
      width: 120,
      render: (text) => {
        const map = {
          warning: "警告",
          critical: "严重",
        };
        return map[text];
      },
    },
    {
      title: "状态",
      key: "status",
      dataIndex: "status",
      align: "center",
      width: 120,
      render: (text) => {
        const map = ["已停用", "已启用"];
        return map[text];
      },
    },
    {
      title: "指标类型",
      key: "quota_type",
      dataIndex: "quota_type",
      align: "center",
      width: 120,
      render: (text) => {
        const map = ["内置指标", "自定义promsql"];
        return map[text];
      },
    },
    {
      title: "操作",
      width: 150,
      key: "",
      dataIndex: "",
      align: "center",
      fixed: "right",
      render: function renderFunc(text, record, index) {
        return (
          <div
            style={{ display: "flex", justifyContent: "space-around" }}
            onClick={() => {
              console.log(record);
              setRow(record);
            }}
          >
            <div style={{ margin: "auto" }}>
              <a
                onClick={() => {
                  // // 持续时长单位
                  // setForTimeCompany("s");
                  queryBuiltinsQuota();
                  setUpDateVisible(true);

                  setForTimeCompany(
                    record.for_time[record.for_time.length - 1]
                  );

                  if (record.quota_type == 0) {
                    setRuleType("0");
                    upDateForm.setFieldsValue({
                      quota_type: "0",
                      alert: record.alert,
                      builtins_quota: [record.service, record.name],
                      compare_str: record.compare_str,
                      threshold_value: record.threshold_value,
                      for_time: record.for_time.substring(
                        0,
                        record.for_time.length - 1
                      ),
                      severity: record.severity,
                      status: record.status,
                    });
                  } else if (record.quota_type == 1) {
                    setRuleType("1");
                    upDateForm.setFieldsValue({
                      quota_type: "1",
                      alert: record.alert,
                      expr: record.expr,
                      compare_str: record.compare_str,
                      threshold_value: record.threshold_value,
                      for_time: record.for_time.substring(
                        0,
                        record.for_time.length - 1
                      ),
                      service: record.service,
                      severity: record.severity,
                      status: record.status,
                      summary: record.summary,
                      description: record.description,
                    });
                  }
                }}
              >
                修改
              </a>
              <a
                style={{
                  marginLeft: 10,
                }}
                onClick={() => {
                  if (record.status == 1) {
                    setStopRowVisible(true);
                  } else {
                    setStartRowVisible(true);
                  }
                }}
              >
                {record.status == 1 ? "停用" : "启用"}
              </a>
              <a
                style={{
                  marginLeft: 10,
                  color:
                    record.forbidden && record.forbidden == 1
                      ? null
                      : "rgba(0, 0, 0, 0.25)",
                  cursor:
                    record.forbidden && record.forbidden == 1
                      ? "pointer"
                      : "not-allowed",
                }}
                onClick={() => {
                  if (record.forbidden && record.forbidden == 1) {
                    setDeleteMoadlVisible(true);
                  }
                }}
              >
                删除
              </a>
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
    fetchGet(apiRequest.ruleCenter.queryPromemonitor, {
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

  const dictionaries = useRef(null);

  // 请求内置规则的选择指标联级配置
  const queryBuiltinsQuota = () => {
    fetchGet(apiRequest.ruleCenter.queryBuiltinsQuota)
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.data) {
            dictionaries.current = res.data;
            let data = res.data;
            setCascaderOption(() => {
              return Object.keys(data).map((key) => {
                let children = data[key].map((item) => {
                  console.log(item);
                  return {
                    label: item.name,
                    value: item.name,
                    disabled:item.name == "数据分区使用率" ? true :false
                    // JSON.stringify({
                    //   description: item.description,
                    //   name: item.name,
                    //   expr: item.expr,
                    //   service: item.service,
                    // }),
                  };
                });
                return {
                  value: key,
                  label: key,
                  children,
                };
              });
            });
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {});
  };

  const addQuota = (data) => {
    let queryData = {};
    if (data.quota_type === "0") {
      let builtins_quota = data.builtins_quota;
      let result = dictionaries.current[builtins_quota[0]].filter(
        (f) => f.name == builtins_quota[1]
      )[0];

      queryData = {
        threshold_value: data.threshold_value,
        compare_str: data.compare_str,
        for_time: `${data.for_time}${forTimeCompany}`,
        severity: data.severity,
        alert: data.alert,
        status: data.status ? 1 : 0,
        quota_type: Number(data.quota_type),
        builtins_quota: {
          description: result.description,
          name: result.name,
          expr: result.expr,
          service: result.service,
        },
      };
    } else if (data.quota_type === "1") {
      queryData = {
        summary: data.summary,
        description: data.description,
        expr: data.expr,
        service: data.service,
        threshold_value: data.threshold_value,
        compare_str: data.compare_str,
        for_time: `${data.for_time}${forTimeCompany}`,
        severity: data.severity,
        alert: data.alert,
        status: data.status ? 1 : 0,
        quota_type: Number(data.quota_type),
      };
    }

    setLoading(true);
    fetchPost(apiRequest.ruleCenter.addQuota, {
      body: {
        env_id: 1,
        ...queryData,
      },
    })
      .then((res) => {
        //console.log(operateObj[operateAciton])
        handleResponse(res, (res) => {
          message.success(`添加操作下发成功`);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
        setAddMoadlVisible(false);
        fetchData(
          {
            current: 1,
            pageSize: pagination.pageSize,
          },
          {
            ...pagination.searchParams,
          }
        );
      });
  };

  // 测试promsql规则
  function fetchTestData(str) {
    setLoading(true);
    fetchPost(apiRequest.ruleCenter.testPromSql, {
      body: {
        expr: str,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          setTestQueryResults(
            res.data.map((e) => {
              let name = e.metric.__name__;
              delete e.metric.__name__;
              let str = JSON.stringify(e.metric).replace(/:/, "=");
              return {
                metric: `${name}${str}`,
                value: e.value[1],
              };
            })
          );
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  }

  // 修改
  const uploadQuota = (data) => {
    let queryData = {};
    if (data.quota_type === "0") {
      let builtins_quota = data.builtins_quota;
      // let result = dictionaries.current[builtins_quota[0]].filter(
      //   (f) => f.name == builtins_quota[1]
      // )[0];

      queryData = {
        threshold_value: data.threshold_value,
        compare_str: data.compare_str,
        for_time: `${data.for_time}${forTimeCompany}`,
        severity: data.severity,
        alert: data.alert,
        // status: data.status ? 1 : 0,
        status: row.status,
        quota_type: Number(data.quota_type),
        builtins_quota: {
          description: row?.description,
          name: row?.name,
          expr: row?.expr,
          service: row?.service,
        },
      };
    } else if (data.quota_type === "1") {
      queryData = {
        summary: data.summary,
        description: data.description,
        expr: data.expr,
        service: data.service,
        threshold_value: data.threshold_value,
        compare_str: data.compare_str,
        for_time: `${data.for_time}${forTimeCompany}`,
        severity: data.severity,
        alert: data.alert,
        status: data.status ? 1 : 0,
        quota_type: Number(data.quota_type),
      };
    }

    setLoading(true);
    fetchPost(apiRequest.ruleCenter.addQuota, {
      body: {
        env_id: 1,
        ...queryData,
        id: row.id,
      },
    })
      .then((res) => {
        //console.log(operateObj[operateAciton])
        handleResponse(res, (res) => {
          message.success(`修改操作下发成功`);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
        setUpDateVisible(false);
        fetchData(
          {
            current: 1,
            pageSize: pagination.pageSize,
          },
          {
            ...pagination.searchParams,
          }
        );
      });
  };

  // 删除接口
  const deleteQuota = (data) => {
    setLoading(true);
    fetchDelete(apiRequest.ruleCenter.deleteQuota, {
      params: {
        id: data.id,
      },
    })
      .then((res) => {
        //console.log(operateObj[operateAciton])
        handleResponse(res, (res) => {
          message.success(`删除操作下发成功`);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
        setDeleteMoadlVisible(false);
        fetchData(
          {
            current: 1,
            pageSize: pagination.pageSize,
          },
          {
            ...pagination.searchParams,
          }
        );
      });
  };

  // 停用或者启用操作
  const statusUpdate = (ids, status) => {
    setLoading(true);
    fetchPost(apiRequest.ruleCenter.batchUpdateRule, {
      body: {
        ids,
        status,
      },
    })
      .then((res) => {
        //console.log(operateObj[operateAciton])
        handleResponse(res, (res) => {
          if (status == 1) {
            message.success(`启用操作下发成功`);
          } else {
            message.success(`停用操作下发成功`);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
        // 批量停用弹框控制器
        setStopVisible(false);
        // 单独停用弹框控制器
        setStopRowVisible(false);

        // 批量启用弹框控制器
        setStartVisible(false);
        // 单独启用弹框控制器
        setStartRowVisible(false);
        fetchData(
          {
            current: 1,
            pageSize: pagination.pageSize,
          },
          {
            ...pagination.searchParams,
          }
        );
      });
  };

  useEffect(() => {
    fetchData(pagination);
  }, []);

  return (
    <OmpContentWrapper>
      <div style={{ display: "flex" }}>
        <Button
          type="primary"
          onClick={() => {
            setRuleType("0");
            // 持续时长单位
            setForTimeCompany("s");
            queryBuiltinsQuota();
            setAddMoadlVisible(true);
          }}
        >
          添加
        </Button>
        <Dropdown
          //placement="bottomLeft"
          overlay={
            <Menu>
              <Menu.Item
                key="openMaintain"
                style={{ textAlign: "center" }}
                onClick={() => setStartVisible(true)}
                disabled={checkedList.map((item) => item.id).length == 0}
              >
                启用规则
              </Menu.Item>
              <Menu.Item
                key="closeMaintain"
                style={{ textAlign: "center" }}
                disabled={checkedList.length == 0}
                onClick={() => {
                  setStopVisible(true);
                }}
              >
                停用规则
              </Menu.Item>
            </Menu>
          }
          placement="bottomCenter"
        >
          <Button style={{ marginLeft: 10, paddingRight: 10, paddingLeft: 15 }}>
            更多
            <DownOutlined />
          </Button>
        </Dropdown>
        <div style={{ display: "flex", marginLeft: "auto" }}>
          <span style={{ width: 80, display: "flex", alignItems: "center" }}>
            规则名称:
          </span>
          <Input
            placeholder="请输入规则名称"
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
                    alert: null,
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
                  alert: selectValue,
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
                  alert: selectValue,
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
                { search: selectValue },
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
          rowKey={(record) => record.id}
          checkedState={[checkedList, setCheckedList]}
          pagination={{
            showSizeChanger: true,
            pageSizeOptions: ["10", "20", "50", "100"],
            showTotal: () => (
              <div
                style={{
                  display: "flex",
                  width: "200px",
                  lineHeight: 2.8,
                  justifyContent: "space-between",
                }}
              >
                <p>已选中 {checkedList.length} 条</p>
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
      <OmpModal
        loading={loading}
        formLabelCol={{ span: 5 }}
        formWrapperCol={{ span: 18 }}
        width={800}
        setLoading={setLoading}
        visibleHandle={[addMoadlVisible, setAddMoadlVisible]}
        okBtnText={"确定"}
        title={
          <span>
            <span style={{ position: "relative", left: "-10px" }}>
              <PlusSquareOutlined />
            </span>
            <span>添加指标规则</span>
          </span>
        }
        form={modalForm}
        onFinish={(data) => {
          addQuota(data);
        }}
        initialValues={{
          compare_str: ">=",
          threshold_value: 30,
          quota_type: "0",
          for_time: 60,
          severity: "warning",
          status: true,
        }}
      >
        <div
          style={{
            transition: "all .2s ease-in",
            position: "relative",
            left: -10,
          }}
        >
          <Form.Item
            label="规则名称"
            name="alert"
            key="alert"
            rules={[
              {
                required: true,
                message: "请输入规则名称",
              },
            ]}
          >
            <Form.Item noStyle name="alert">
              <Input style={{ width: 520 }} placeholder={"请输入规则名称"} />
            </Form.Item>
            <span
              name="tishi"
              style={{
                paddingLeft: 20,
                position: "relative",
                top: 1,
              }}
            >
              {" "}
              <Tooltip title="指标规则的名称，方便识别">
                <QuestionCircleOutlined />
              </Tooltip>
            </span>
          </Form.Item>

          <Form.Item
            label="规则类型"
            name="quota_type"
            key="quota_type"
            rules={[
              {
                required: true,
                message: "请选择规则类型",
              },
            ]}
          >
            <Form.Item noStyle name="quota_type">
              <Radio.Group
                value={ruleType}
                onChange={(e) => {
                  setRuleType(e.target.value);
                }}
              >
                <Radio.Button value="0">内置指标</Radio.Button>
                <Radio.Button value="1">自定义PromSQL</Radio.Button>
              </Radio.Group>
            </Form.Item>
            <span
              name="tishi"
              style={{
                paddingLeft: 20,
                position: "relative",
                top: 1,
              }}
            >
              {" "}
              <Tooltip title="内置PromSQL指标方便使用，也可以添加自定义PromSQL规则">
                <QuestionCircleOutlined />
              </Tooltip>
            </span>
          </Form.Item>

          {ruleType === "0" && (
            <>
              <Form.Item
                label="选择指标"
                name="builtins_quota"
                key="builtins_quota"
                rules={[
                  {
                    required: true,
                    message: "请选择指标",
                  },
                ]}
              >
                <Form.Item noStyle name="builtins_quota">
                  <Cascader
                    style={{ width: 520 }}
                    options={cascaderOption}
                    placeholder="请选择指标"
                  />
                </Form.Item>
                <span
                  name="tishi"
                  style={{
                    paddingLeft: 20,
                    position: "relative",
                    top: 1,
                  }}
                >
                  {" "}
                  <Tooltip title="选择需要监控的指标">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </span>
              </Form.Item>
              <Form.Item
                label="触发条件"
                name="compare_str"
                key="compare_str"
                rules={[
                  {
                    required: true,
                    message: "请选择触发条件",
                  },
                ]}
              >
                <Select placeholder="请选择触发条件" style={{ width: 520 }}>
                  <Select.Option value=">=">{`${">="}`}</Select.Option>
                  <Select.Option value=">">{`${">"}`}</Select.Option>
                  <Select.Option value="==">{`${"=="}`}</Select.Option>
                  <Select.Option value="!=">{`${"!="}`}</Select.Option>
                  <Select.Option value="<=">{`${"<="}`}</Select.Option>
                  <Select.Option value="<">{`${"<"}`}</Select.Option>
                </Select>
              </Form.Item>
              <Form.Item
                label="触发阈值"
                name="threshold_value"
                key="threshold_value"
                rules={[
                  {
                    required: true,
                    message: "请选择触发阈值",
                  },
                  // {
                  //   validator: (rule, value, callback) => {
                  //     if (value == 0) {
                  //       return Promise.reject(`只支持大于等于0的数字`);
                  //     } else {
                  //       return Promise.resolve("success");
                  //     }
                  //   },
                  // },
                ]}
              >
                <Form.Item noStyle name="threshold_value">
                  <InputNumber style={{ width: 520 }} min={0} />
                </Form.Item>
                <span
                  name="tishi"
                  style={{
                    paddingLeft: 20,
                    position: "relative",
                    top: 1,
                  }}
                >
                  {" "}
                  <Tooltip title="只支持大于等于0的数字">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </span>
              </Form.Item>
              <Form.Item
                label="持续时长"
                name="for_time"
                key="for_time"
                rules={[
                  {
                    required: true,
                    message: "请选择持续时长",
                  },
                  {
                    validator: (rule, value, callback) => {
                      if (value == 0) {
                        return Promise.reject(`只支持大于0的数字`);
                      } else {
                        return Promise.resolve("success");
                      }
                    },
                  },
                ]}
              >
                <Form.Item noStyle name="for_time">
                  <InputNumber
                    style={{ width: 520 }}
                    addonAfter={
                      <Select
                        style={{ width: 80 }}
                        value={forTimeCompany}
                        onChange={(e) => {
                          setForTimeCompany(e);
                        }}
                      >
                        <Select.Option value="s">秒</Select.Option>
                        <Select.Option value="m">分</Select.Option>
                        <Select.Option value="h">时</Select.Option>
                      </Select>
                    }
                  />
                </Form.Item>
                <span
                  name="tishi"
                  style={{
                    paddingLeft: 20,
                    position: "relative",
                    top: 5,
                  }}
                >
                  {" "}
                  <Tooltip title="通在持续时长内均匹配规则后会触发告警">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </span>
              </Form.Item>

              <Form.Item
                label="告警等级"
                name="severity"
                key="severity"
                rules={[
                  {
                    required: true,
                    message: "请选择告警等级",
                  },
                ]}
              >
                <Radio.Group>
                  <Radio value="warning">警告</Radio>
                  <Radio value="critical">严重</Radio>
                </Radio.Group>
              </Form.Item>

              <Form.Item
                label="启用状态"
                name="status"
                key="status"
                rules={[
                  {
                    required: true,
                    message: "请选择启用状态",
                  },
                ]}
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </>
          )}

          {ruleType === "1" && (
            <>
              <Form.Item
                label="PromSQL"
                name="expr"
                key="expr"
                rules={[
                  {
                    required: true,
                    message: "请输入PromSQL",
                  },
                ]}
              >
                <Form.Item noStyle name="expr">
                  <Input style={{ width: 400 }} placeholder={"请输入PromSQL"} />
                </Form.Item>
                <span
                  name="tishi"
                  style={{
                    paddingLeft: 20,
                    position: "relative",
                    // top: 1,
                  }}
                >
                  {" "}
                  <Button
                    type="primary"
                    onClick={() => {
                      fetchTestData(modalForm.getFieldValue("expr"));
                      setTestVisible(true);
                    }}
                  >
                    测试查询
                  </Button>
                </span>
              </Form.Item>
              <Form.Item
                label="触发条件"
                name="compare_str"
                key="compare_str"
                rules={[
                  {
                    required: true,
                    message: "请选择触发条件",
                  },
                ]}
              >
                <Select placeholder="请选择触发条件" style={{ width: 520 }}>
                  <Select.Option value=">=">{`${">="}`}</Select.Option>
                  <Select.Option value=">">{`${">"}`}</Select.Option>
                  <Select.Option value="==">{`${"=="}`}</Select.Option>
                  <Select.Option value="!=">{`${"!="}`}</Select.Option>
                  <Select.Option value="<=">{`${"<="}`}</Select.Option>
                  <Select.Option value="<">{`${"<"}`}</Select.Option>
                </Select>
              </Form.Item>
              <Form.Item
                label="触发阈值"
                name="threshold_value"
                key="threshold_value"
                rules={[
                  {
                    required: true,
                    message: "请选择触发阈值",
                  },
                  // {
                  //   validator: (rule, value, callback) => {
                  //     if (value == 0) {
                  //       return Promise.reject(`只支持大于等于0的数字`);
                  //     } else {
                  //       return Promise.resolve("success");
                  //     }
                  //   },
                  // },
                ]}
              >
                <Form.Item noStyle name="threshold_value">
                  <InputNumber style={{ width: 520 }} min={0} />
                </Form.Item>
                <span
                  name="tishi"
                  style={{
                    paddingLeft: 20,
                    position: "relative",
                    top: 1,
                  }}
                >
                  {" "}
                  <Tooltip title="只支持大于等于0的数字">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </span>
              </Form.Item>
              <Form.Item
                label="持续时长"
                name="for_time"
                key="for_time"
                rules={[
                  {
                    required: true,
                    message: "请选择持续时长",
                  },
                  {
                    validator: (rule, value, callback) => {
                      if (value == 0) {
                        return Promise.reject(`只支持大于0的数字`);
                      } else {
                        return Promise.resolve("success");
                      }
                    },
                  },
                ]}
              >
                <Form.Item noStyle name="for_time">
                  <InputNumber
                    style={{ width: 520 }}
                    addonAfter={
                      <Select
                        style={{ width: 80 }}
                        value={forTimeCompany}
                        onChange={(e) => {
                          setForTimeCompany(e);
                        }}
                      >
                        <Select.Option value="s">秒</Select.Option>
                        <Select.Option value="m">分</Select.Option>
                        <Select.Option value="h">时</Select.Option>
                      </Select>
                    }
                  />
                </Form.Item>
                <span
                  name="tishi"
                  style={{
                    paddingLeft: 20,
                    position: "relative",
                    top: 5,
                  }}
                >
                  {" "}
                  <Tooltip title="通在持续时长内均匹配规则后会触发告警">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </span>
              </Form.Item>
              <Form.Item label="关联服务" name="service" key="service">
                <Form.Item noStyle name="service">
                  <Input
                    style={{ width: 520 }}
                    placeholder={"请输入关联服务"}
                  />
                </Form.Item>
                <span
                  name="tishi"
                  style={{
                    paddingLeft: 20,
                    position: "relative",
                    top: 1,
                  }}
                >
                  {" "}
                  <Tooltip title="输入关联服务后，该指标的告警会归类于该服务名，如“mysql”，如需关联到主机，请填写“node”">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </span>
              </Form.Item>
              <Form.Item
                label="告警等级"
                name="severity"
                key="severity"
                rules={[
                  {
                    required: true,
                    message: "请选择告警等级",
                  },
                ]}
              >
                <Radio.Group>
                  <Radio value="warning">警告</Radio>
                  <Radio value="critical">严重</Radio>
                </Radio.Group>
              </Form.Item>

              <Form.Item
                label="启用状态"
                name="status"
                key="status"
                rules={[
                  {
                    required: true,
                    message: "请选择启用状态",
                  },
                ]}
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>

              <Form.Item
                label="告警标题"
                name="summary"
                key="summary"
                rules={[
                  {
                    required: true,
                    message: "选择规则名称",
                  },
                ]}
              >
                <Form.Item noStyle name="summary">
                  <Input style={{ width: 520 }} placeholder={"选择规则名称"} />
                </Form.Item>
                <span
                  name="tishi"
                  style={{
                    paddingLeft: 20,
                    position: "relative",
                    top: 1,
                  }}
                >
                  {" "}
                  <Tooltip title="标题中可配置Prometheus中的标签，如 {{ $labels.instance }}">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </span>
              </Form.Item>

              <Form.Item
                label="告警消息"
                name="description"
                key="description"
                rules={[
                  {
                    required: true,
                    message: "选择告警消息",
                  },
                ]}
              >
                <Form.Item noStyle name="description">
                  <Input.TextArea
                    rows={4}
                    style={{ width: 520 }}
                    placeholder={"输入告警消息"}
                  />
                </Form.Item>
                <span
                  name="tishi"
                  style={{
                    paddingLeft: 20,
                    position: "relative",
                    top: -70,
                  }}
                >
                  {" "}
                  <Tooltip title="消息中可配Prometheus中的标签，如 {{ $labels.instance }}">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </span>
              </Form.Item>
            </>
          )}
        </div>
      </OmpModal>

      {/* 删除操作 */}
      <OmpMessageModal
        visibleHandle={[deleteMoadlVisible, setDeleteMoadlVisible]}
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
          deleteQuota(row);
        }}
      >
        <div style={{ padding: "20px" }}>
          确定要对 <span style={{ fontWeight: 500 }}>{row.alert}</span> 规则{" "}
          <span style={{ fontWeight: 500 }}>下发删除命令</span> ？
        </div>
      </OmpMessageModal>

      <OmpMessageModal
        width={900}
        visibleHandle={[testVisible, setTestVisible]}
        noFooter
        style={{ position: "relative", top: 180 }}
        title={<span>PromSQL查询结果</span>}
        loading={loading}
      >
        <div style={{ border: "1px solid #d6d6d6" }}>
          <Table
            showHeader={false}
            scroll={{ x: 1200 }}
            columns={[
              {
                title: "内存使用率",
                key: "metric",
                dataIndex: "metric",
                align: "center",
              },
              {
                title: "内存使用率12",
                key: "value",
                dataIndex: "value",
                align: "center",
                width: 120,
                fixed: "right",
              },
            ]}
            dataSource={testQueryResults.map((i, idx) => ({ ...i, key: idx }))}
          />
        </div>
      </OmpMessageModal>

      {/* 修改规则 */}
      <OmpModal
        loading={loading}
        width={800}
        formLabelCol={{ span: 5 }}
        formWrapperCol={{ span: 18 }}
        setLoading={setLoading}
        visibleHandle={[upDateVisible, setUpDateVisible]}
        okBtnText={"确定"}
        title={
          <span>
            <span style={{ position: "relative", left: "-10px" }}>
              <PlusSquareOutlined />
            </span>
            <span>修改指标规则</span>
          </span>
        }
        form={upDateForm}
        onFinish={(data) => {
          uploadQuota(data);
          // console.log(upDateForm.getFieldValue());
        }}
        initialValues={{
          compare_str: ">=",
          threshold_value: 30,
          quota_type: "0",
          for_time: 60,
          severity: "warning",
          status: true,
        }}
      >
        <div
          style={{
            transition: "all .2s ease-in",
            position: "relative",
            left: -10,
          }}
        >
          <Form.Item
            label="规则名称"
            name="alert"
            key="alert"
            rules={[
              {
                required: true,
                message: "请输入规则名称",
              },
            ]}
          >
            <Form.Item noStyle name="alert">
              <Input style={{ width: 520 }} placeholder={"请输入规则名称"} />
            </Form.Item>
            <span
              name="tishi"
              style={{
                paddingLeft: 20,
                position: "relative",
                top: 1,
              }}
            >
              {" "}
              <Tooltip title="指标规则的名称，方便识别">
                <QuestionCircleOutlined />
              </Tooltip>
            </span>
          </Form.Item>

          <Form.Item
            label="规则类型"
            name="quota_type"
            key="quota_type"
            rules={[
              {
                required: true,
                message: "请选择规则类型",
              },
            ]}
          >
            <Form.Item noStyle name="quota_type">
              <Radio.Group
                disabled={true}
                value={ruleType}
                onChange={(e) => {
                  setRuleType(e.target.value);
                }}
              >
                <Radio.Button value="0">内置指标</Radio.Button>
                <Radio.Button value="1">自定义PromSQL</Radio.Button>
              </Radio.Group>
            </Form.Item>
            <span
              name="tishi"
              style={{
                paddingLeft: 20,
                position: "relative",
                top: 1,
              }}
            >
              {" "}
              <Tooltip title="内置PromSQL指标方便使用，也可以添加自定义PromSQL规则">
                <QuestionCircleOutlined />
              </Tooltip>
            </span>
          </Form.Item>

          {ruleType === "0" && (
            <>
              <Form.Item
                label="选择指标"
                name="builtins_quota"
                key="builtins_quota"
                rules={[
                  {
                    required: true,
                    message: "请选择指标",
                  },
                ]}
              >
                <Form.Item noStyle name="builtins_quota">
                  <Cascader
                    disabled={true}
                    style={{ width: 520 }}
                    options={cascaderOption}
                    placeholder="请选择指标"
                  />
                </Form.Item>
                <span
                  name="tishi"
                  style={{
                    paddingLeft: 20,
                    position: "relative",
                    top: 1,
                  }}
                >
                  {" "}
                  <Tooltip title="选择需要监控的指标">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </span>
              </Form.Item>
              <Form.Item
                label="触发条件"
                name="compare_str"
                key="compare_str"
                rules={[
                  {
                    required: true,
                    message: "请选择触发条件",
                  },
                ]}
              >
                <Select placeholder="请选择触发条件" style={{ width: 520 }}>
                  <Select.Option value=">=">{`${">="}`}</Select.Option>
                  <Select.Option value=">">{`${">"}`}</Select.Option>
                  <Select.Option value="==">{`${"=="}`}</Select.Option>
                  <Select.Option value="!=">{`${"!="}`}</Select.Option>
                  <Select.Option value="<=">{`${"<="}`}</Select.Option>
                  <Select.Option value="<">{`${"<"}`}</Select.Option>
                </Select>
              </Form.Item>
              <Form.Item
                label="触发阈值"
                name="threshold_value"
                key="threshold_value"
                rules={[
                  {
                    required: true,
                    message: "请选择触发阈值",
                  },
                  // {
                  //   validator: (rule, value, callback) => {
                  //     if (value == 0) {
                  //       return Promise.reject(`只支持大于等于0的数字`);
                  //     } else {
                  //       return Promise.resolve("success");
                  //     }
                  //   },
                  // },
                ]}
              >
                <Form.Item noStyle name="threshold_value">
                  <InputNumber style={{ width: 520 }} min={0} />
                </Form.Item>
                <span
                  name="tishi"
                  style={{
                    paddingLeft: 20,
                    position: "relative",
                    top: 1,
                  }}
                >
                  {" "}
                  <Tooltip title="只支持大于等于0的数字">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </span>
              </Form.Item>
              <Form.Item
                label="持续时长"
                name="for_time"
                key="for_time"
                rules={[
                  {
                    required: true,
                    message: "请选择持续时长",
                  },
                  {
                    validator: (rule, value, callback) => {
                      if (value == 0) {
                        return Promise.reject(`只支持大于0的数字`);
                      } else {
                        return Promise.resolve("success");
                      }
                    },
                  },
                ]}
              >
                <Form.Item noStyle name="for_time">
                  <InputNumber
                    style={{ width: 520 }}
                    addonAfter={
                      <Select
                        style={{ width: 80 }}
                        value={forTimeCompany}
                        onChange={(e) => {
                          setForTimeCompany(e);
                        }}
                      >
                        <Select.Option value="s">秒</Select.Option>
                        <Select.Option value="m">分</Select.Option>
                        <Select.Option value="h">时</Select.Option>
                      </Select>
                    }
                  />
                </Form.Item>
                <span
                  name="tishi"
                  style={{
                    paddingLeft: 20,
                    position: "relative",
                    top: 5,
                  }}
                >
                  {" "}
                  <Tooltip title="通在持续时长内均匹配规则后会触发告警">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </span>
              </Form.Item>

              <Form.Item
                label="告警等级"
                name="severity"
                key="severity"
                rules={[
                  {
                    required: true,
                    message: "请选择告警等级",
                  },
                ]}
              >
                <Radio.Group>
                  <Radio value="warning">警告</Radio>
                  <Radio value="critical">严重</Radio>
                </Radio.Group>
              </Form.Item>

              {/* <Form.Item
                label="启用状态"
                name="status"
                key="status"
                rules={[
                  {
                    required: true,
                    message: "请选择启用状态",
                  },
                ]}
                valuePropName="checked"
              >
                <Switch disabled={true} />
              </Form.Item> */}
            </>
          )}

          {ruleType === "1" && (
            <>
              <Form.Item
                label="PromSQL"
                name="expr"
                key="expr"
                rules={[
                  {
                    required: true,
                    message: "请输入PromSQL",
                  },
                ]}
              >
                <Form.Item noStyle name="expr">
                  <Input style={{ width: 400 }} placeholder={"请输入PromSQL"} />
                </Form.Item>
                <span
                  name="tishi"
                  style={{
                    paddingLeft: 20,
                    position: "relative",
                    // top: 1,
                  }}
                >
                  {" "}
                  <Button
                    type="primary"
                    onClick={() => {
                      fetchTestData(modalForm.getFieldValue("expr"));
                      setTestVisible(true);
                    }}
                  >
                    测试查询
                  </Button>
                </span>
              </Form.Item>
              <Form.Item
                label="触发条件"
                name="compare_str"
                key="compare_str"
                rules={[
                  {
                    required: true,
                    message: "请选择触发条件",
                  },
                ]}
              >
                <Select placeholder="请选择触发条件" style={{ width: 520 }}>
                  <Select.Option value=">=">{`${">="}`}</Select.Option>
                  <Select.Option value=">">{`${">"}`}</Select.Option>
                  <Select.Option value="==">{`${"=="}`}</Select.Option>
                  <Select.Option value="!=">{`${"!="}`}</Select.Option>
                  <Select.Option value="<=">{`${"<="}`}</Select.Option>
                  <Select.Option value="<">{`${"<"}`}</Select.Option>
                </Select>
              </Form.Item>
              <Form.Item
                label="触发阈值"
                name="threshold_value"
                key="threshold_value"
                rules={[
                  {
                    required: true,
                    message: "请选择触发阈值",
                  },
                  // {
                  //   validator: (rule, value, callback) => {
                  //     if (value == 0) {
                  //       return Promise.reject(`只支持大于等于0的数字`);
                  //     } else {
                  //       return Promise.resolve("success");
                  //     }
                  //   },
                  // },
                ]}
              >
                <Form.Item noStyle name="threshold_value">
                  <InputNumber style={{ width: 520 }} min={0} />
                </Form.Item>
                <span
                  name="tishi"
                  style={{
                    paddingLeft: 20,
                    position: "relative",
                    top: 1,
                  }}
                >
                  {" "}
                  <Tooltip title="只支持大于等于0的数字">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </span>
              </Form.Item>
              <Form.Item
                label="持续时长"
                name="for_time"
                key="for_time"
                rules={[
                  {
                    required: true,
                    message: "请选择持续时长",
                  },
                  {
                    validator: (rule, value, callback) => {
                      if (value == 0) {
                        return Promise.reject(`只支持大于0的数字`);
                      } else {
                        return Promise.resolve("success");
                      }
                    },
                  },
                ]}
              >
                <Form.Item noStyle name="for_time">
                  <InputNumber
                    style={{ width: 520 }}
                    addonAfter={
                      <Select
                        style={{ width: 80 }}
                        value={forTimeCompany}
                        onChange={(e) => {
                          setForTimeCompany(e);
                        }}
                      >
                        <Select.Option value="s">秒</Select.Option>
                        <Select.Option value="m">分</Select.Option>
                        <Select.Option value="h">时</Select.Option>
                      </Select>
                    }
                  />
                </Form.Item>
                <span
                  name="tishi"
                  style={{
                    paddingLeft: 20,
                    position: "relative",
                    top: 5,
                  }}
                >
                  {" "}
                  <Tooltip title="通在持续时长内均匹配规则后会触发告警">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </span>
              </Form.Item>
              <Form.Item label="关联服务" name="service" key="service">
                <Form.Item noStyle name="service">
                  <Input
                    style={{ width: 520 }}
                    placeholder={"请输入关联服务"}
                  />
                </Form.Item>
                <span
                  name="tishi"
                  style={{
                    paddingLeft: 20,
                    position: "relative",
                    top: 1,
                  }}
                >
                  {" "}
                  <Tooltip title="输入关联服务后，该指标的告警会归类于该服务名，如“mysql”，如需关联到主机，请填写“node”">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </span>
              </Form.Item>
              <Form.Item
                label="告警等级"
                name="severity"
                key="severity"
                rules={[
                  {
                    required: true,
                    message: "请选择告警等级",
                  },
                ]}
              >
                <Radio.Group>
                  <Radio value="warning">警告</Radio>
                  <Radio value="critical">严重</Radio>
                </Radio.Group>
              </Form.Item>

              <Form.Item
                label="启用状态"
                name="status"
                key="status"
                rules={[
                  {
                    required: true,
                    message: "请选择启用状态",
                  },
                ]}
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>

              <Form.Item
                label="告警标题"
                name="summary"
                key="summary"
                rules={[
                  {
                    required: true,
                    message: "选择规则名称",
                  },
                ]}
              >
                <Form.Item noStyle name="summary">
                  <Input style={{ width: 520 }} placeholder={"选择规则名称"} />
                </Form.Item>
                <span
                  name="tishi"
                  style={{
                    paddingLeft: 20,
                    position: "relative",
                    top: 1,
                  }}
                >
                  {" "}
                  <Tooltip title="标题中可配置Prometheus中的标签，如 {{ $labels.instance }}">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </span>
              </Form.Item>

              <Form.Item
                label="告警消息"
                name="description"
                key="description"
                rules={[
                  {
                    required: true,
                    message: "选择告警消息",
                  },
                ]}
              >
                <Form.Item noStyle name="description">
                  <Input.TextArea
                    rows={4}
                    style={{ width: 520 }}
                    placeholder={"输入告警消息"}
                  />
                </Form.Item>
                <span
                  name="tishi"
                  style={{
                    paddingLeft: 20,
                    position: "relative",
                    top: -70,
                  }}
                >
                  {" "}
                  <Tooltip title="消息中可配Prometheus中的标签，如 {{ $labels.instance }}">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </span>
              </Form.Item>
            </>
          )}
        </div>
      </OmpModal>

      {/* 批量停用操作 */}
      <OmpMessageModal
        visibleHandle={[stopVisible, setStopVisible]}
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
          // deleteQuota(row);
          statusUpdate(
            checkedList.map((i) => i.id),
            0
          );
          setCheckedList([]);
        }}
      >
        <div style={{ padding: "20px" }}>
          确定要对 <span style={{ fontWeight: 500 }}>{checkedList.length}</span>{" "}
          条规则 <span style={{ fontWeight: 500 }}>下发停用命令</span> ？
        </div>
      </OmpMessageModal>

      {/* 单独停用操作 */}
      <OmpMessageModal
        visibleHandle={[stopRowVisible, setStopRowVisible]}
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
          statusUpdate([row.id], 0);
        }}
      >
        <div style={{ padding: "20px" }}>
          确定要对 <span style={{ fontWeight: 500 }}>{row.alert}</span> 规则{" "}
          <span style={{ fontWeight: 500 }}>下发停用命令</span> ？
        </div>
      </OmpMessageModal>

      {/* 批量启用操作 */}
      <OmpMessageModal
        visibleHandle={[startVisible, setStartVisible]}
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
          statusUpdate(
            checkedList.map((i) => i.id),
            1
          );
          setCheckedList([]);
          // deleteQuota(row);
        }}
      >
        <div style={{ padding: "20px" }}>
          确定要对 <span style={{ fontWeight: 500 }}>{checkedList.length}</span>{" "}
          条规则 <span style={{ fontWeight: 500 }}>下发启用命令</span> ？
        </div>
      </OmpMessageModal>

      {/* 单独启用操作 */}
      <OmpMessageModal
        visibleHandle={[startRowVisible, setStartRowVisible]}
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
          statusUpdate([row.id], 1);
          // deleteQuota(row);
        }}
      >
        <div style={{ padding: "20px" }}>
          确定要对 <span style={{ fontWeight: 500 }}>{row.alert}</span> 规则{" "}
          <span style={{ fontWeight: 500 }}>下发启用命令</span> ？
        </div>
      </OmpMessageModal>
    </OmpContentWrapper>
  );
};

export default RuleIndicator;
