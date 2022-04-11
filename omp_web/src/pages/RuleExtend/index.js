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
  Upload,
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
  downloadFile,
} from "@/utils/utils";
import { fetchGet, fetchPost, fetchDelete, fetchPut } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import moment from "moment";
import {
  SearchOutlined,
  SettingFilled,
  DownOutlined,
  PlusSquareOutlined,
  QuestionCircleOutlined,
  ExclamationCircleOutlined,
  ImportOutlined,
  UploadOutlined,
  FormOutlined,
  CloseOutlined,
  DownloadOutlined,
} from "@ant-design/icons";
import { useHistory, useLocation } from "react-router-dom";
import axios from "axios";
import star from "./asterisk.svg";

const RuleExtend = () => {
  const [loading, setLoading] = useState(false);
  const [modalForm] = Form.useForm();

  const [upDateForm] = Form.useForm();

  const history = useHistory();
  //选中的数据
  const [checkedList, setCheckedList] = useState([]);

  const [row, setRow] = useState({});

  // 删除操作
  const [deleteVisible, setDeleteVisible] = useState(false);

  // 行内删除操作
  const [deleteRowVisible, setDeleteRowVisible] = useState(false);

  // 添加操作控制器
  const [addVisible, setAddVisible] = useState(false);

  // 修改操作控制器
  const [upDateVisible, setUpDateVisible] = useState(false);

  // 查询操作控制器
  const [statusVisible, setStatusVisible] = useState(false);

  //table表格数据
  const [dataSource, setDataSource] = useState([]);
  const [selectValue, setSelectValue] = useState();

  // detail数据
  const [detailList, setDetailList] = useState([]);

  // 选中的绑定主机
  const [executionData, setExecutionData] = useState([]);

  // 绑定主机控制器
  const [hostListVisible, setHostListVisible] = useState(false);

  // 是否展示执行绑定主机校验信息
  const [isShowErrMsg, setIsShowErrMsg] = useState(false);

  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    ordering: "",
    searchParams: {},
  });

  // 主机翻页数据
  const [hostPagination, setHostPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  });

  // 主机列表
  const [hostList, setHostList] = useState([]);

  const renderStatus = (text) => {
    switch (text) {
      case 0:
        return <span>{renderDisc("normal", 7, -1)}正常</span>;
      case 1:
        return <span>{renderDisc("warning", 7, -1)}重启中</span>;
      case 2:
        return <span>{renderDisc("critical", 7, -1)}启动失败</span>;
      case 3:
        return <span>{renderDisc("warning", 7, -1)}部署中</span>;
      case 4:
        return <span>{renderDisc("critical", 7, -1)}部署失败</span>;
      default:
        return "-";
    }
  };

  const columns = [
    {
      title: "描述",
      // width: 60,
      key: "description",
      dataIndex: "description",
      //sorter: (a, b) => a.username - b.username,
      // sortDirections: ["descend", "ascend"],
      align: "center",
      width: 220,
      fixed: "left",
      ellipsis: true,
    },
    {
      title: (
        <span>
          绑定主机
          <span
            name="tishi"
            style={{
              position: "relative",
              top: 0,
              left: 2,
            }}
          >
            {" "}
            <Tooltip title="脚本绑定主机数量，绑定主机后会在该主机上采集指标">
              <QuestionCircleOutlined />
            </Tooltip>
          </span>
        </span>
      ),
      key: "bound_hosts_num",
      width: 120,
      dataIndex: "bound_hosts_num",
      align: "center",
    },
    {
      title: "探测周期(s)",
      key: "scrape_interval",
      dataIndex: "scrape_interval",
      width: 120,
      align: "center",
    },
    {
      title: "操作",
      width: 100,
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
                  upDateForm.setFieldsValue({
                    description: record.description,
                    scrape_interval: record.scrape_interval,
                    bound_hosts: record.bound_hosts,
                  });
                  setExecutionData(
                    record.bound_hosts.map((item, idx) => ({
                      id: idx,
                      ip: item,
                    }))
                  );
                  setUpDateVisible(true);
                }}
              >
                修改
              </a>
              <a
                style={{
                  marginLeft: 10,
                }}
                onClick={() => {
                  queryExpansionIndex(record.id);
                  setStatusVisible(true);
                }}
              >
                查询
              </a>
              <a
                style={{
                  marginLeft: 10,
                }}
                onClick={() => {
                  setDeleteRowVisible(true);
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
    fetchGet(apiRequest.ruleCenter.queryExtendRuleList, {
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

  /* 限制数字输入框只能输入整数 */
  const limitNumber = (value) => {
    if (typeof value === "string") {
      return !isNaN(Number(value)) ? value.replace(/^(0+)|[^\d]/g, "") : "";
    } else if (typeof value === "number") {
      return !isNaN(value) ? String(value).replace(/^(0+)|[^\d]/g, "") : "";
    } else {
      return "";
    }
  };

  // 添加规则
  const addExtend = (data) => {
    setLoading(true);
    let formData = new FormData();
    formData.append("file", data.collectionScript.file.originFileObj);
    formData.append("scrape_interval", data.scrape_interval);

    const config = {
      headers: {
        "Content-Type": "multipart/form-data;boundary=" + new Date().getTime(),
      },
    };

    axios
      .post(apiRequest.ruleCenter.queryExtendRuleList, formData, config)
      .then(function (response) {
        console.log(response);
        if (response && response.data && response.data.code == 1) {
          message.warning(response.data.message);
        } else {
          message.success(`添加操作下发成功`);
        }
      })
      .catch(function (error) {
        console.log(error);
      })
      .finally(() => {
        setLoading(false);
        setAddVisible(false);
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

  // 删除规则
  function deleteRule(id) {
    setLoading(true);
    fetchDelete(`${apiRequest.ruleCenter.queryExtendRuleList}${id}/`)
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.code == 0) {
            message.success(`删除操作下发成功`);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
        setDeleteRowVisible(false);
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
  }

  // 查询扩展指标
  const queryExpansionIndex = (id) => {
    setLoading(true);
    fetchGet(apiRequest.ruleCenter.queryDetail, {
      params: {
        id,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          setDetailList(res.data);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  // 请求主机列表hostPagination, setHostPagination]
  const queryHostList = (pageParams = { current: 1, pageSize: 10 }) => {
    setLoading(true);
    fetchGet(apiRequest.machineManagement.hosts, {
      params: {
        page: pageParams.current,
        size: pageParams.pageSize,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          // 设置表格的默认选中
          // setCheckedList(executionData);
          setCheckedList(
            res.data.results.filter((item) => {
              let result = executionData.filter((i) => i.ip == item.ip);
              return result.length !== 0;
            })
          );

          setHostList(res.data.results);
          setHostPagination({
            ...hostPagination,
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
  };

  // 修改接口
  const upDateRule = (data, id) => {
    setLoading(true);
    fetchPut(`${apiRequest.ruleCenter.queryExtendRuleList}${id}/`, {
      body: data,
    })
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.code == 0) {
            message.success(`修改操作下发成功`);
          }
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

  useEffect(() => {
    fetchData(pagination);
  }, []);

  return (
    <OmpContentWrapper>
      <div style={{ display: "flex" }}>
        <Button
          type="primary"
          onClick={() => {
            setAddVisible(true);
          }}
        >
          添加
        </Button>
        {/* <Button
          disabled={checkedList.map((item) => item.id).length == 0}
          onClick={() => {
            setDeleteVisible(true);
          }}
          style={{ marginLeft: 10 }}
        >
          删除
        </Button> */}
        {/* <Dropdown
          //placement="bottomLeft"
          overlay={
            <Menu>
              <Menu.Item
                key="openMaintain"
                style={{ textAlign: "center" }}
                onClick={() => {}}
                disabled={checkedList.map((item) => item.id).length == 0}
              >
                禁用
              </Menu.Item>
              <Menu.Item
                key="closeMaintain"
                style={{ textAlign: "center" }}
                disabled={checkedList.length == 0}
                onClick={() => {}}
              >
                启用
              </Menu.Item>
            </Menu>
          }
          placement="bottomCenter"
        >
          <Button style={{ marginLeft: 10, paddingRight: 10, paddingLeft: 15 }}>
            更多
            <DownOutlined />
          </Button>
        </Dropdown> */}
        <div style={{ display: "flex", marginLeft: "auto" }}>
          <span style={{ width: 50, display: "flex", alignItems: "center" }}>
            描述:
          </span>
          <Input
            placeholder="请输入描述"
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
                    description: null,
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
                  description: selectValue,
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
                  description: selectValue,
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
          //   rowKey={(record) => record.id}
          //   checkedState={[checkedList, setCheckedList]}
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

      <OmpMessageModal
        visibleHandle={[deleteRowVisible, setDeleteRowVisible]}
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
          deleteRule(row.id);
          // statusUpdate([row.id], 1)
          // deleteQuota(row);
        }}
      >
        <div style={{ padding: "20px" }}>
          确定要对 <span style={{ fontWeight: 500 }}>{row.description}</span>{" "}
          指标 <span style={{ fontWeight: 500 }}>下发删除命令</span> ？
        </div>
      </OmpMessageModal>

      {/* <OmpMessageModal
        visibleHandle={[deleteVisible, setDeleteVisible]}
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
          // statusUpdate([row.id], 1)
          // deleteQuota(row);
        }}
      >
        <div style={{ padding: "20px" }}>
          确定要对 <span style={{ fontWeight: 500 }}>{checkedList.length}</span>{" "}
          条指标 <span style={{ fontWeight: 500 }}>下发删除命令</span> ？
        </div>
      </OmpMessageModal> */}
      {/* 添加规则 */}
      <OmpModal
        loading={loading}
        width={600}
        formLabelCol={{ span: 8 }}
        formWrapperCol={{ span: 18 }}
        setLoading={setLoading}
        visibleHandle={[addVisible, setAddVisible]}
        okBtnText={"确定"}
        title={
          <span>
            <span style={{ position: "relative", left: "-10px" }}>
              <ImportOutlined />
            </span>
            <span>添加扩展指标</span>
          </span>
        }
        form={modalForm}
        onFinish={(data) => {
          console.log(data);
          addExtend(data);
        }}
        initialValues={{
          scrape_interval: 60,
        }}
      >
        <div
          style={{
            transition: "all .2s ease-in",
            position: "relative",
            left: -10,
          }}
        >
          <Form.Item label="下载模版" name="down" key="down">
            <Button
              onClick={() => {
                downloadFile("/custom_scripts/template.py");
              }}
              icon={<DownloadOutlined />}
            >
              点击下载
            </Button>
          </Form.Item>
          <Form.Item
            label="上传采集脚本"
            name="collectionScript"
            key="collectionScript"
            rules={[
              {
                required: true,
                message: "请上传采集脚本",
              },
            ]}
          >
            <Upload
              name="file"
              maxCount={1}
              accept=".py"
              beforeUpload={(file, fileList) => {
                const fileSize = file.size / 1024 / 1024; //单位是mb
                if (Math.ceil(fileSize) > 2) {
                  message.error("仅支持传入2MB以内文件");
                  return Upload.LIST_IGNORE;
                }
                // return Upload.LIST_IGNORE;
              }}
              customRequest={(e) => {
                // console.log(e)
                // 直接调用成功，在整个表单提交的时候去携带文件流
                e.onSuccess();
              }}
            >
              <Button icon={<UploadOutlined />}>点击上传</Button>
            </Upload>
          </Form.Item>

          <Form.Item
            label="探测周期(s)"
            name="scrape_interval"
            key="scrape_interval"
            rules={[
              {
                required: true,
                message: "请输入探测周期",
              },
            ]}
          >
            <Form.Item noStyle name="scrape_interval">
              <InputNumber
                min={1}
                max={120}
                formatter={limitNumber}
                parser={limitNumber}
              />
            </Form.Item>
            <span
              name="tishi"
              style={{
                paddingLeft: 20,
                position: "relative",
                top: 0,
              }}
            >
              {" "}
              <Tooltip title="指定Prometheus对指标采集间隔时间">
                <QuestionCircleOutlined />
              </Tooltip>
            </span>
          </Form.Item>
        </div>
      </OmpModal>

      {/* 查询 */}
      <OmpMessageModal
        width={900}
        visibleHandle={[statusVisible, setStatusVisible]}
        noFooter
        style={{ position: "relative", top: 180 }}
        title={<span>查看扩展指标状态</span>}
        loading={loading}
      >
        <div style={{ border: "1px solid #d6d6d6" }}>
          <Table
            scroll={{ x: 800 }}
            columns={[
              {
                title: "采集端",
                key: "scrape_url",
                dataIndex: "scrape_url",
                align: "center",
                width: 280,
                ellipsis: true,
                render: (text) => {
                  if (!text) {
                    return "-";
                  }
                  return <Tooltip title={text}>{text}</Tooltip>;
                },
              },
              {
                title: "状态",
                key: "status",
                dataIndex: "status",
                align: "center",
                width: 120,
                // fixed: "right",
                render: (text) => {
                  if (text === "down") {
                    return "停用";
                  }
                  return "正常";
                },
              },
              {
                title: "采集用时",
                key: "last_scrape_duration",
                dataIndex: "last_scrape_duration",
                align: "center",
                width: 120,
                render: (text) => {
                  if (!text) {
                    return "-";
                  }

                  return `${(text * 1000).toFixed(2)}ms`;
                },
                // fixed: "right",
              },
              {
                title: "错误信息",
                key: "last_error",
                dataIndex: "last_error",
                align: "center",
                width: 220,
                ellipsis: true,
                render: (text) => {
                  if (!text) {
                    return "-";
                  }
                  return <Tooltip title={text}>{text}</Tooltip>;
                },
                fixed: "right",
              },
            ]}
            dataSource={detailList}
          />
        </div>
      </OmpMessageModal>

      {/* 修改规则 */}
      <OmpModal
        loading={loading}
        width={900}
        formLabelCol={{ span: 4 }}
        formWrapperCol={{ span: 16 }}
        setLoading={setLoading}
        visibleHandle={[upDateVisible, setUpDateVisible]}
        okBtnText={"确定"}
        title={
          <span>
            <span style={{ position: "relative", left: "-10px" }}>
              <FormOutlined />
            </span>
            <span>修改扩展指标</span>
          </span>
        }
        form={upDateForm}
        beForeOk={() => {
          if (executionData.length == 0) {
            // performTasks();
            setIsShowErrMsg(true);
          }
        }}
        afterClose={() => {
          setExecutionData([]);
        }}
        onFinish={(data) => {
          console.log(data);
          if (executionData.length !== 0) {
            // performTasks();
            console.log("通过");
            upDateRule(
              {
                description: data.description,
                scrape_interval: data.scrape_interval,
                bound_hosts: executionData.map((i) => i.ip),
              },
              row.id
            );
          }
        }}
        initialValues={{
          scrape_interval: 60,
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
            label="描述"
            name="description"
            key="description"
            rules={[
              {
                required: true,
                message: "请输入描述",
              },
            ]}
          >
            <Input style={{ width: 520 }} placeholder={"请输入描述"} />
          </Form.Item>

          <Form.Item
            label="探测周期(s)"
            name="scrape_interval"
            key="scrape_interval"
            rules={[
              {
                required: true,
                message: "请选择规则类型",
              },
            ]}
          >
            <Form.Item noStyle name="scrape_interval">
              <InputNumber
                min={1}
                max={120}
                formatter={limitNumber}
                parser={limitNumber}
              />
            </Form.Item>
            <span
              name="tishi"
              style={{
                paddingLeft: 20,
                position: "relative",
                top: 0,
              }}
            >
              {" "}
              <Tooltip title="指定Prometheus对指标采集间隔时间">
                <QuestionCircleOutlined />
              </Tooltip>
            </span>
          </Form.Item>

          <Form.Item
            name="target_objs"
            extra={
              <div
                style={{
                  position: "relative",
                  overflow: "hidden",
                  height: 20,
                }}
              >
                <span
                  style={{
                    transition: "all .2s ease-in",
                    color: "#ff4d4f",
                    position: "absolute",
                    top: isShowErrMsg ? 0 : -20,
                  }}
                >
                  请选择绑定主机
                </span>
              </div>
            }
            label={
              <span>
                <img
                  src={star}
                  style={{ position: "relative", top: -3, left: -4 }}
                />
                绑定主机
              </span>
            }
          >
            <div
              style={{
                backgroundColor: "#f6f6f6",
                minHeight: 80,
                width: 700,
                position: "relative",
                padding: "10px",
                paddingBottom: "40px",
                display: "flex",
                flexWrap: "wrap",
                border: isShowErrMsg ? "1px solid #ff4d4f" : "none",
              }}
            >
              {executionData.map((i) => (
                <ExecutionTargetItem
                  info={i}
                  key={i.id}
                  executionData={[executionData, setExecutionData]}
                  setIsShowErrMsg={setIsShowErrMsg}
                />
              ))}
              <div
                style={{
                  position: "absolute",
                  display: "flex",
                  bottom: 10,
                  left: "50%",
                  transform: "translateX(-50%)",
                }}
              >
                <Button
                  style={{ padding: "3px 20px", height: 30 }}
                  onClick={() => {
                    setExecutionData([]);
                    setIsShowErrMsg(true);
                  }}
                >
                  清除
                </Button>
                <Button
                  style={{ padding: "3px 20px", height: 30, marginLeft: 15 }}
                  onClick={() => {
                    setIsShowErrMsg(false);
                    queryHostList();
                    setHostListVisible(true);
                  }}
                >
                  添加
                </Button>
              </div>
            </div>
          </Form.Item>
        </div>
      </OmpModal>

      <Modal
        title="选择绑定主机"
        width={800}
        afterClose={() => {
          setCheckedList([]);
        }}
        onCancel={() => {
          setHostListVisible(false);
        }}
        visible={hostListVisible}
        footer={null}
        //width={1000}
        loading={loading}
        bodyStyle={{
          paddingLeft: 30,
          paddingRight: 30,
        }}
        destroyOnClose
      >
        <div>
          <div style={{ border: "1px solid rgb(235, 238, 242)" }}>
            <OmpTable
              size="small"
              // scroll={{ x: executionColumns.length * 150 }}
              loading={loading}
              columns={[
                {
                  title: "实例名称",
                  key: "instance_name",
                  dataIndex: "instance_name",
                  align: "center",
                  ellipsis: true,
                  width: 150,
                  fixed: "left",
                  render: (text, record) => {
                    return (
                      <Tooltip title={text}>
                        <div style={{ paddingTop: 2 }}>{text}</div>
                      </Tooltip>
                    );
                  },
                },
                {
                  title: "IP地址",
                  key: "ip",
                  dataIndex: "ip",
                  align: "center",
                  ellipsis: true,
                  width: 120,
                  render: (text, record) => {
                    let v = text || "-";
                    return (
                      <Tooltip title={v}>
                        <div style={{ paddingTop: 2 }}>{v}</div>
                      </Tooltip>
                    );
                  },
                },
                {
                  title: "主机Agent",
                  key: "host_agent",
                  dataIndex: "host_agent",
                  align: "center",
                  width: 120,
                  //ellipsis: true,
                  render: (text) => {
                    return renderStatus(text);
                  },
                },
              ]}
              onChange={(e, filters, sorter) => {
                setTimeout(() => {
                  queryHostList(e);
                }, 200);
              }}
              dataSource={hostList}
              pagination={{
                showSizeChanger: true,
                pageSizeOptions: ["10", "20", "50", "100"],
                showTotal: () => (
                  <div
                    style={{
                      display: "flex",
                      width: "200px",
                      justifyContent: "space-between",
                      lineHeight: 2.8,
                      position: "relative",
                      top: -3,
                    }}
                  >
                    <p>已选中 {checkedList.length} 条</p>
                    <p style={{ color: "rgb(152, 157, 171)" }}>
                      共计{" "}
                      <span style={{ color: "rgb(63, 64, 70)" }}>
                        {hostPagination.total}
                      </span>{" "}
                      条
                    </p>
                  </div>
                ),
                ...hostPagination,
              }}
              rowKey={(record) => record.id}
              checkedState={[checkedList, setCheckedList]}
            />
          </div>
          <div
            style={{ display: "flex", justifyContent: "center", marginTop: 30 }}
          >
            <div
              style={{
                width: 170,
                display: "flex",
                justifyContent: "space-between",
              }}
            >
              <Button onClick={() => setHostListVisible(false)}>取消</Button>
              <Button
                type="primary"
                style={{ marginLeft: 16 }}
                loading={loading}
                // disabled={checkedList.length == 0}
                onClick={() => {
                  setExecutionData(checkedList);
                  setHostListVisible(false);
                }}
              >
                确认
              </Button>
            </div>
          </div>
        </div>
      </Modal>
    </OmpContentWrapper>
  );
};

const ExecutionTargetItem = ({ info, executionData, setIsShowErrMsg }) => {
  const [data, setData] = executionData;
  return (
    <div
      style={{
        backgroundColor: "#fff",
        border: "solid 1px #d9d9d9",
        height: 28,
        paddingLeft: 25,
        borderRadius: 4,
        display: "flex",
        alignItems: "center",
        marginLeft: 10,
        marginBottom: 10,
        overflow: "hidden",
        textOverflow: " ellipsis",
        whiteSpace: "nowrap",
        position: "relative",
      }}
    >
      {info.ip}
      <CloseOutlined
        style={{ paddingLeft: 15, paddingRight: 10, cursor: "pointer" }}
        onClick={() => {
          let result = data.filter((i) => !i.id == info.id);
          if (result.length == 0) {
            setIsShowErrMsg(true);
          }
          setData(() => {
            return result;
          });
        }}
      />
    </div>
  );
};

export default RuleExtend;
