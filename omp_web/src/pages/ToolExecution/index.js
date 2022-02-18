import { useEffect, useState } from "react";
import {
  Button,
  Form,
  Spin,
  Input,
  InputNumber,
  Tooltip,
  Checkbox,
  Modal,
  Select,
  Upload,
  message,
} from "antd";
import { useHistory, useLocation } from "react-router-dom";
import { fetchGet, fetchPost } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import {
  OmpContentWrapper,
  OmpTable,
  OmpMessageModal,
  OmpSelect,
  OmpDatePicker,
  OmpDrawer,
} from "@/components";
import styles from "./index.module.less";
import {
  handleResponse,
  _idxInit,
  refreshTime,
  downloadFile,
} from "@/utils/utils";
import {
  QuestionCircleOutlined,
  CloseOutlined,
  UploadOutlined,
} from "@ant-design/icons";
import star from "./asterisk.svg";

const ToolExecution = () => {
  const history = useHistory();
  const locationArr = useLocation().pathname.split("/");

  const [loading, setLoading] = useState(false);

  const [executionLoading, setExecutionLoading] = useState(false);

  const [form] = Form.useForm();

  const [conf, setConf] = useState();

  // 是否采用纳管用户
  const [isUseManagement, setIsUseManagement] = useState(true);

  // 执行对象弹框控制器
  const [executionTarget, setExecutionTarget] = useState(false);

  // 选中的数据
  const [checkedList, setCheckedList] = useState([]);

  // 执行对象数据
  const [executionData, setExecutionData] = useState([]);

  // 是否展示执行对象校验信息
  const [isShowErrMsg, setIsShowErrMsg] = useState(false);

  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    ordering: "",
    searchParams: {},
  });

  // 执行对象列表
  const [executionList, setExecutionList] = useState([]);

  const initColumns = [
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
      title: "Agent状态",
      key: "host_agent_state",
      dataIndex: "host_agent_state",
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
  ];

  // 执行对象columns
  const [executionColumns, setExecutionColumn] = useState(initColumns);

  // 扩展
  const [extendForm, setExtendForm] = useState([]);

  const queryConf = () => {
    setLoading(true);
    fetchGet(
      `${apiRequest.utilitie.queryFormConf}${
        locationArr[locationArr.length - 1]
      }/`
    )
      .then((res) => {
        handleResponse(res, (res) => {
          setConf(res.data);
          if (!res.data.default_form.runuser) {
            setIsUseManagement(true);
          } else {
            setIsUseManagement(false);
          }
          // 设置扩展表单组件默认值
          if (res.data?.script_args) {
            let script_args = res.data?.script_args;
            setExtendForm(script_args);
            script_args.forEach((item) => {
              console.log(item);
              form.setFieldsValue({
                [item.key]: item.default,
              });
            });
          }

          // 设置固定表单默认值
          form.setFieldsValue({
            task_name: res?.data?.default_form?.task_name,
            timeout: res?.data?.default_form?.timeout,
            runuser: res?.data?.default_form?.runuser,
          });
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  const queryExecutionList = (pageParams = { current: 1, pageSize: 10 }) => {
    setExecutionLoading(true);
    fetchGet(
      `${apiRequest.utilitie.queryFormConf}${
        locationArr[locationArr.length - 1]
      }/target-object`,
      {
        params: {
          page: pageParams.current,
          size: pageParams.pageSize,
        },
      }
    )
      .then((res) => {
        handleResponse(res, (res) => {
          // 当有需要扩展的column时 // setExecutionColumn
          if (
            res.data.results &&
            res.data.results[0] &&
            res.data.results[0].modifiable_kwargs
          ) {
            let extendItems = [];
            let modifiableKwargs = res.data.results[0].modifiable_kwargs;
            for (const key in modifiableKwargs) {
              extendItems.push({
                title: key,
                key: key,
                dataIndex: key,
                align: "center",
                ellipsis: true,
                width: 150,
                render: (text, record) => {
                  return (
                    <Tooltip title={text}>
                      <div style={{ paddingTop: 2 }}>{text}</div>
                    </Tooltip>
                  );
                },
              });
            }
            setExecutionColumn([...initColumns, ...extendItems]);
          }
          setExecutionList(
            res.data.results.map((m, idx) => {
              return {
                ...m,
                ...m?.modifiable_kwargs,
              };
            })
          );
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
        setExecutionTarget(true);
        setExecutionLoading(false);
      });
  };

  const getExtendFormComponent = (item) => {
    switch (item.type) {
      case "input":
        return (
          <Form.Item
            label={item.name}
            name={item.key}
            key={item.key}
            rules={[{ required: item.required, message: `请输入${item.name}` }]}
          >
            <Input
              placeholder={`请输入${item.name}`}
              style={{
                width: 460,
              }}
            />
          </Form.Item>
        );
        break;
      case "select":
        return (
          <Form.Item
            label={item.name}
            name={item.key}
            key={item.key}
            rules={[{ required: item.required, message: `请输入${item.name}` }]}
          >
            <Select placeholder={`请选择${item.name}`} style={{ width: 150 }}>
              {item.options.map((i) => (
                <Select.Option value={i} key={i}>
                  {i}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
        );
        break;
      case "file":
        return (
          <Form.Item
            label={item.name}
            name={item.key}
            key={item.key}
            rules={[
              { required: item.required, message: `请将文件传入${item.name}` },
            ]}
          >
            <Upload
              name="file"
              action={apiRequest.utilitie.uploadFile}
              maxCount={1}
              data={{
                module: "ToolInfo",
                module_id: locationArr[locationArr.length - 1],
              }}
              beforeUpload={(file, fileList) => {
                const fileSize = file.size / 1024 / 1024; //单位是mb
                if (Math.ceil(fileSize) > 20) {
                  message.error("仅支持传入20MB以内文件");
                  return Upload.LIST_IGNORE;
                }
                // return Upload.LIST_IGNORE;
              }}
            >
              <Button icon={<UploadOutlined />}>点击上传</Button>
            </Upload>
          </Form.Item>
        );
        break;
      default:
        return "暂无类型";
        break;
    }
  };

  // 执行任务下发
  const performTasks = () => {
    setLoading(true);
    let formData = form.getFieldsValue();

    let defaultForm = { ...conf.default_form };
    let scriptArgs = [...conf.script_args];
    // defaultForm填充数据
    for (const key in defaultForm) {
      defaultForm[key] = formData[key];
    }
    defaultForm.target_objs = executionData;

    // scriptArgs数据填充
    scriptArgs = scriptArgs.map((item) => {
      if (item.type == "file") {
        let defaultData = {};
        // 为了可读性，分两层写
        console.log(formData);
        if (
          formData[item.key] &&
          formData[item.key].file &&
          formData[item.key].file.status == "done"
        ) {
          if (formData[item.key].file.response.code == 0) {
            defaultData.file_name =
              formData[item.key].file.response.data.file_name;
            defaultData.file_url =
              formData[item.key].file.response.data.file_url;
            defaultData.union_id =
              formData[item.key].file.response.data.union_id;
          }
        }

        return {
          ...item,
          default: defaultData,
        };
      }
      return {
        ...item,
        default: formData[item.key],
      };
    });

    fetchPost(
      `${apiRequest.utilitie.queryFormConf}${
        locationArr[locationArr.length - 1]
      }/answer`,
      {
        body: {
          default_form: defaultForm,
          script_args: scriptArgs,
        },
      }
    )
      .then((res) => {
        if (res && res.data) {
          if (res.data.code == 1) {
            message.warning(res.data.message);
          }
          if (res.data.code == 0) {
            message.success("执行命令下发成功");
            setTimeout(() => {
              history.push(
                `/utilitie/tool-management/tool-execution-results/${
                  locationArr[locationArr.length - 1]
                }`
              );
            }, 300);
          }
        }
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    queryConf();
  }, []);

  return (
    <OmpContentWrapper
      wrapperStyle={{ padding: 0, paddingBottom: 30, backgroundColor: "#fff" }}
    >
      <div className={styles.header}>
        <div>创建任务: {conf?.name}</div>
        <Button
          style={{ padding: "3px 20px", height: 30 }}
          onClick={() => {
            history?.goBack();
          }}
        >
          返回
        </Button>
      </div>
      <div style={{ paddingTop: 20 }}>
        <Spin spinning={loading}>
          <Form
            name="implement"
            labelCol={{ span: 3 }}
            wrapperCol={{ span: 6 }}
            style={{ paddingTop: 10 }}
            onFinish={() => {
              if (executionData.length !== 0) {
                console.log("通过校验了");
                performTasks();
              }
            }}
            form={form}
          >
            <Form.Item
              label="任务标题"
              name="task_name"
              rules={[{ required: true, message: "请输入任务标题" }]}
            >
              <Input
                placeholder="请输入任务标题"
                style={{
                  width: 460,
                }}
              />
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
                    请选择执行对象
                  </span>
                </div>
              }
              label={
                <span>
                  <img
                    src={star}
                    style={{ position: "relative", top: -3, left: -4 }}
                  />
                  执行对象
                </span>
              }
            >
              <div
                style={{
                  backgroundColor: "#f6f6f6",
                  minHeight: 80,
                  width: 800,
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
                      queryExecutionList();
                      setCheckedList(executionData);
                    }}
                  >
                    添加
                  </Button>
                </div>
              </div>
            </Form.Item>
            <Form.Item
              label="超时时间"
              name="timeout"
              rules={[{ required: true, message: "请输入超时时间" }]}
            >
              <Form.Item
                name="timeout"
                noStyle
                rules={[
                  {
                    validator: (rule, value, callback) => {
                      console.log("执行了");
                      let reg = new RegExp(/^[1-9]\d*$/, "g");
                      if (value == 0) {
                        return Promise.reject("请输入正整数");
                      }
                      if (value) {
                        if (!reg.test(value)) {
                          return Promise.reject("请输入正整数");
                        }
                        return Promise.resolve("success");
                      } else {
                        return Promise.resolve("success");
                      }
                    },
                  },
                ]}
              >
                <InputNumber />
              </Form.Item>
              <span name="miao" style={{ paddingLeft: 5 }}>
                秒
              </span>
              <span
                name="tishi"
                style={{
                  paddingLeft: 20,
                  position: "relative",
                  top: 1,
                }}
              >
                {" "}
                <Tooltip title="工具在目标主机执行的超时时间，超过该时间后，任务将退出">
                  <QuestionCircleOutlined />
                </Tooltip>
              </span>
            </Form.Item>
            <Form.Item
              name="runuser"
              label="执行用户"
              rules={[
                { required: !isUseManagement, message: "请输入执行用户" },
              ]}
            >
              <Form.Item name="runuser" noStyle>
                <Input
                  disabled={isUseManagement}
                  style={{ width: 140 }}
                  placeholder="请输入执行用户"
                />
              </Form.Item>
              <span style={{ paddingLeft: 15 }}>
                <Checkbox
                  onChange={(e) => {
                    form.setFieldsValue({
                      runuser: null,
                    });
                    setIsUseManagement(e.target.checked);
                  }}
                  checked={isUseManagement}
                >
                  使用纳管用户
                </Checkbox>
                <Tooltip title="工具在目标主机执行的用户名，请确保具有相应用户权限">
                  <QuestionCircleOutlined
                    style={{ position: "relative", left: 15 }}
                  />
                </Tooltip>
              </span>
            </Form.Item>
            {extendForm.map((item) => {
              return getExtendFormComponent(item);
            })}
            <div
              style={{
                paddingTop: 30,
                width: "80%",
                display: "flex",
                justifyContent: "center",
              }}
            >
              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={loading}
                  onClick={() => {
                    if (executionData.length == 0) {
                      setIsShowErrMsg(true);
                    }
                  }}
                >
                  执行
                </Button>
              </Form.Item>
            </div>
          </Form>
        </Spin>
      </div>
      <Modal
        title="选择执行对象"
        width={800}
        afterClose={() => {
          setCheckedList([]);
        }}
        onCancel={() => {
          setExecutionTarget(false);
        }}
        visible={executionTarget}
        footer={null}
        //width={1000}
        loading={executionLoading}
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
              scroll={{ x: executionColumns.length * 150 }}
              loading={executionLoading}
              columns={executionColumns}
              onChange={(e, filters, sorter) => {
                setTimeout(() => {
                  queryExecutionList(e);
                }, 200);
              }}
              dataSource={executionList}
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
                        {pagination.total}
                      </span>{" "}
                      条
                    </p>
                  </div>
                ),
                ...pagination,
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
              <Button onClick={() => setExecutionTarget(false)}>取消</Button>
              <Button
                type="primary"
                style={{ marginLeft: 16 }}
                loading={executionLoading}
                // disabled={checkedList.length == 0}
                onClick={() => {
                  setExecutionData(checkedList);
                  setExecutionTarget(false);
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
      {info.instance_name}
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

export default ToolExecution;
