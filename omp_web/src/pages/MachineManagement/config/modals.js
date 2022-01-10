import React from "react";
import { OmpModal } from "@/components";
import {
  Button,
  Input,
  Select,
  Form,
  message,
  InputNumber,
  Row,
  Col,
  Tooltip,
  Modal,
  Steps,
  Upload,
  Switch,
} from "antd";
import {
  PlusSquareOutlined,
  FormOutlined,
  InfoCircleOutlined,
  ImportOutlined,
  DownloadOutlined,
  CloudUploadOutlined,
  CheckCircleFilled,
  CloseCircleFilled,
} from "@ant-design/icons";
import {
  MessageTip,
  isChineseChar,
  isNumberChar,
  isValidIpChar,
  isExpression,
  isLetterChar,
  isSpace,
  handleResponse,
} from "@/utils/utils";
import { fetchPost } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { useState, useRef } from "react";
import star from "./asterisk.svg";
import XLSX from "xlsx";
import { OmpTable } from "@/components";
// import BMF from 'browser-md5-file';

// let bmf = new BMF()
// const [modalForm] = Form.useForm();

export const AddMachineModal = ({
  loading,
  visibleHandle,
  onFinish,
  createHost,
  msgInfo,
  setLoading,
}) => {
  const [modalForm] = Form.useForm();
  const [modalLoading, setmodalLoading] = useState(false);
  const timer = useRef(null);
  const timer2 = useRef(null);
  return (
    <OmpModal
      loading={modalLoading ? modalLoading : loading}
      setLoading={setLoading}
      visibleHandle={visibleHandle}
      okBtnText={modalLoading ? "校验中" : loading ? "创建中" : null}
      title={
        <span>
          <span style={{ position: "relative", left: "-10px" }}>
            <PlusSquareOutlined />
          </span>
          <span>创建主机信息</span>
        </span>
      }
      form={modalForm}
      onFinish={(data) => {
        createHost(data);
        //onFinish("post", data);
      }}
      initialValues={{
        data_folder: "/data",
        port: 22,
        operate_system: "CentOS",
        username: "root",
      }}
    >
      <MessageTip
        msg={msgInfo.msg}
        setMsgShow={msgInfo.setMsgShow}
        msgShow={msgInfo.msgShow}
      />
      <div
        style={{
          transition: "all .2s ease-in",
          position: "relative",
          top: msgInfo.msgShow ? 0 : -24,
        }}
      >
        <Form.Item
          label="实例名称"
          name="instance_name"
          key="instance_name"
          rules={[
            {
              required: true,
              message: "请输入实例名称",
            },
            {
              validator: (rule, value, callback) => {
                if (!value) {
                  return Promise.resolve("success");
                }
                // 校验开头
                let startChar = value.slice(0, 1);
                if (
                  isNumberChar(startChar) ||
                  isLetterChar(startChar) ||
                  startChar == "-"
                ) {
                  if (!isExpression(value)) {
                    if (isChineseChar(value)) {
                      return Promise.reject(`实例名称不支持中文`);
                    } else {
                      if (value.length > 16) {
                        return Promise.resolve("success");
                      } else {
                        if (isSpace(value)) {
                          return Promise.reject("实例名称不支持空格");
                        }
                        return new Promise((resolve, rej) => {
                          if (timer.current) {
                            clearTimeout(timer.current);
                          }
                          timer.current = setTimeout(() => {
                            setmodalLoading(true);
                            fetchPost(apiRequest.machineManagement.checkHost, {
                              body: {
                                instance_name: value,
                              },
                            })
                              .then((res) => {
                                if (res && res.data) {
                                  if (res.data.data) {
                                    resolve("success");
                                  } else {
                                    rej(`实例名称已存在`);
                                  }
                                }
                              })
                              .catch((e) => console.log(e))
                              .finally(() => {
                                setmodalLoading(false);
                              });
                          }, 400);
                        });
                      }
                    }
                  } else {
                    return Promise.reject("实例名称不支持表情");
                  }
                } else {
                  return Promise.reject(`实例名称开头只支持字母、数字或"-"`);
                }
              },
            },
          ]}
        >
          <Input maxLength={16} placeholder={"请输入实例名称"} />
        </Form.Item>

        <Form.Item
          label="系统平台"
          name="operate_system"
          key="operate_system"
          rules={[
            {
              required: true,
              message: "请选择系统平台",
            },
          ]}
        >
          <Select placeholder={"请选择系统平台"}>
            <Select.Option value="CentOS">CentOS</Select.Option>
            <Select.Option value="RedHat">RedHat</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item
          label="数据分区"
          name="data_folder"
          key="data_folder"
          extra={
            <span style={{ fontSize: 10 }}>
              应用组件默认安装到数据分区,请确保具有足够空间
            </span>
          }
          rules={[
            {
              required: true,
              message: "请输入数据分区",
            },
            {
              validator: (rule, value, callback) => {
                var reg = /[^a-zA-Z0-9\_\-\/]/g;
                if (!value) {
                  return Promise.resolve("success");
                } else {
                  if (value.startsWith("/")) {
                    if (!isChineseChar(value)) {
                      if (!reg.test(value)) {
                        return Promise.resolve("success");
                      } else {
                        return Promise.reject(
                          `数据分区只支持字母、数字、"/"、"-"和"_"`
                        );
                      }
                    } else {
                      return Promise.reject(
                        `数据分区只支持字母、数字、"/"、"-"和"_"`
                      );
                    }
                  } else {
                    return Promise.reject(`数据分区开头必须为"/"`);
                  }
                }
              },
            },
          ]}
        >
          <Input maxLength={255} placeholder={"请输入数据分区"} />
        </Form.Item>

        <Form.Item
          name="ip"
          key="ip"
          label={
            <span>
              <img
                src={star}
                style={{ position: "relative", top: -2, left: -3 }}
              />
              IP地址
            </span>
          }
          useforminstanceinvalidator="true"
          rules={[
            // {
            //   required: true,
            //   message: "请输入IP地址或端口号",
            // },
            {
              validator: (rule, v, callback) => {
                let value = modalForm.getFieldValue("IPtext");
                let portValue = modalForm.getFieldValue("port");
                if (!value) {
                  return Promise.reject("请输入IP地址或端口号");
                }
                if (!portValue) {
                  return Promise.reject("请输入IP地址或端口号");
                }
                if (isValidIpChar(value)) {
                  return new Promise((resolve, rej) => {
                    if (timer2.current) {
                      clearTimeout(timer2.current);
                    }
                    timer2.current = setTimeout(() => {
                      setmodalLoading(true);
                      fetchPost(apiRequest.machineManagement.checkHost, {
                        body: {
                          ip: value,
                        },
                      })
                        .then((res) => {
                          if (res && res.data) {
                            if (res.data.data) {
                              resolve("success");
                            } else {
                              rej(`ip地址已存在`);
                            }
                          }
                        })
                        .catch((e) => console.log(e))
                        .finally(() => {
                          setmodalLoading(false);
                        });
                    }, 600);
                  });
                } else {
                  return Promise.reject("请输入正确格式的IP地址");
                }
              },
            },
          ]}
        >
          <Row gutter={8}>
            <Col span={16}>
              <Form.Item
                name="IPtext"
                key="IPtext"
                noStyle
                seforminstanceinvalidator="true"
              >
                <Input placeholder={"例如: 192.168.10.10"} />
              </Form.Item>
            </Col>
            <span style={{ display: "flex", alignItems: "center" }}>:</span>
            <Col span={4}>
              <Form.Item name="port" key="port" noStyle>
                <InputNumber
                  onChange={() => {
                    modalForm.validateFields(["ip"]);
                  }}
                  style={{ width: 82 }}
                  min={1}
                  max={65535}
                />
              </Form.Item>
            </Col>
          </Row>
        </Form.Item>

        <Form.Item
          label="用户名"
          name="username"
          key="username"
          rules={[
            {
              required: true,
              message: "请输入用户名",
            },
            {
              validator: (rule, value, callback) => {
                var reg = /[^a-zA-Z0-9\_\-]/g;
                var startReg = /[^a-zA-Z0-9\_]/g;
                if (value) {
                  let startChar = value.slice(0, 1);
                  if (!startReg.test(startChar)) {
                    if (isChineseChar(value)) {
                      return Promise.reject(`用户名只支持数字、字母、"-"或"_"`);
                    } else {
                      if (!reg.test(value)) {
                        return Promise.resolve("success");
                      } else {
                        return Promise.reject(
                          `用户名只支持数字、字母、"-"或"_"`
                        );
                      }
                    }
                  } else {
                    return Promise.reject(`用户名开头只支持数字、字母、或"_"`);
                  }
                } else {
                  return Promise.resolve("success");
                }
              },
            },
          ]}
        >
          <Input
            // suffix={
            //   <Tooltip title="请使用root或具有sudo免密码权限的用户">
            //     <InfoCircleOutlined style={{ color: "rgba(0,0,0,.45)" }} />
            //   </Tooltip>
            // }
            maxLength={16}
            placeholder={"请输入用户名"}
          />
        </Form.Item>

        <Form.Item
          label="密码"
          name="password"
          key="password"
          rules={[
            {
              required: true,
              message: "请输入密码",
            },
            {
              validator: (rule, value, callback) => {
                if (value) {
                  if (!isExpression(value)) {
                    if (isChineseChar(value)) {
                      return Promise.reject("密码不支持中文");
                    } else {
                      if (value.length < 8) {
                        return Promise.reject("密码长度为8到64位");
                      } else {
                        if (isSpace(value)) {
                          return Promise.reject("密码不支持空格");
                        }
                        return Promise.resolve("success");
                      }
                    }
                  } else {
                    return Promise.reject(`密码不支持输入表情`);
                  }
                } else {
                  return Promise.resolve("success");
                }
              },
            },
          ]}
        >
          <Input.Password maxLength={64} placeholder={"请输入密码"} />
        </Form.Item>
      </div>
    </OmpModal>
  );
};

export const UpDateMachineModal = ({
  loading,
  visibleHandle,
  onFinish,
  createHost,
  msgInfo,
  row,
  setLoading,
}) => {
  const [modalForm] = Form.useForm();
  // console.log(row)
  const [modalLoading, setmodalLoading] = useState(false);
  const timer = useRef(null);
  const timer2 = useRef(null);
  return (
    <OmpModal
      loading={modalLoading ? modalLoading : loading}
      setLoading={setLoading}
      okBtnText={modalLoading ? "校验中" : loading ? "修改中" : null}
      visibleHandle={visibleHandle}
      title={
        <span>
          <span style={{ position: "relative", left: "-10px" }}>
            <FormOutlined />
          </span>
          <span>修改主机信息</span>
        </span>
      }
      form={modalForm}
      onFinish={(data) => {
        createHost(data);
        //onFinish("post", data);
      }}
      initialValues={{
        instance_name: row.instance_name,
        IPtext: row.ip,
        data_folder: row.data_folder,
        port: row.port,
        operate_system: row.operate_system,
        username: row.username,
        ip: row.ip,
        password: row.password && window.atob(row.password),
      }}
    >
      <MessageTip
        msg={msgInfo.msg}
        setMsgShow={msgInfo.setMsgShow}
        msgShow={msgInfo.msgShow}
      />
      <div
        style={{
          transition: "all .2s ease-in",
          position: "relative",
          top: msgInfo.msgShow ? 0 : -24,
        }}
      >
        <Form.Item
          label="实例名称"
          name="instance_name"
          key="instance_name"
          rules={[
            {
              required: true,
              message: "请输入实例名称",
            },
            {
              validator: (rule, value, callback) => {
                if (!value) {
                  return Promise.resolve("success");
                }
                // 校验开头
                let startChar = value.slice(0, 1);
                if (
                  isNumberChar(startChar) ||
                  isLetterChar(startChar) ||
                  startChar == "-"
                ) {
                  if (!isExpression(value)) {
                    if (isChineseChar(value)) {
                      return Promise.reject(`实例名称不支持中文`);
                    } else {
                      if (value.length > 16) {
                        return Promise.resolve("success");
                      } else {
                        if (isSpace(value)) {
                          return Promise.reject("实例名称不支持空格");
                        }
                        return new Promise((resolve, rej) => {
                          if (timer.current) {
                            clearTimeout(timer.current);
                          }
                          timer.current = setTimeout(() => {
                            setmodalLoading(true);
                            fetchPost(apiRequest.machineManagement.checkHost, {
                              body: {
                                instance_name: value,
                                id: row.id,
                              },
                            })
                              .then((res) => {
                                if (res && res.data) {
                                  if (res.data.data) {
                                    resolve("success");
                                  } else {
                                    rej(`实例名称已存在`);
                                  }
                                }
                              })
                              .catch((e) => console.log(e))
                              .finally(() => {
                                setmodalLoading(false);
                              });
                          }, 400);
                        });
                      }
                    }
                  } else {
                    return Promise.reject("实例名称不支持表情");
                  }
                } else {
                  return Promise.reject(`实例名称开头只支持字母、数字或"-"`);
                }
              },
            },
          ]}
        >
          <Input maxLength={16} placeholder={"请输入实例名称"} />
        </Form.Item>

        <Form.Item
          label="系统平台"
          name="operate_system"
          key="operate_system"
          rules={[
            {
              required: true,
              message: "请选择系统平台",
            },
          ]}
        >
          <Select placeholder={"请选择系统平台"}>
            <Select.Option value="CentOS">CentOS</Select.Option>
            <Select.Option value="RedHat">RedHat</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item
          label="数据分区"
          name="data_folder"
          key="data_folder"
          extra={
            <span style={{ fontSize: 10 }}>
              应用组件默认安装到数据分区,请确保具有足够空间
            </span>
          }
          rules={[
            {
              required: true,
              message: "请输入数据分区",
            },
            {
              validator: (rule, value, callback) => {
                var reg = /[^a-zA-Z0-9\_\-\/]/g;
                if (!value) {
                  return Promise.resolve("success");
                } else {
                  if (value.startsWith("/")) {
                    if (!isChineseChar(value)) {
                      if (!reg.test(value)) {
                        return Promise.resolve("success");
                      } else {
                        return Promise.reject(
                          `数据分区只支持字母、数字、"/"、"-"和"_"`
                        );
                      }
                    } else {
                      return Promise.reject(
                        `数据分区只支持字母、数字、"/"、"-"和"_"`
                      );
                    }
                  } else {
                    return Promise.reject(`数据分区开头必须为"/"`);
                  }
                }
              },
            },
          ]}
        >
          <Input maxLength={255} placeholder={"请输入数据分区"} />
        </Form.Item>

        <Form.Item
          name="ip"
          key="ip"
          label={
            <span>
              <img
                src={star}
                style={{ position: "relative", top: -2, left: -3 }}
              />
              IP地址
            </span>
          }
          rules={[
            {
              validator: (rule, v, callback) => {
                let value = modalForm.getFieldValue("IPtext");
                let portValue = modalForm.getFieldValue("port");
                if (!value) {
                  return Promise.reject("请输入IP地址或端口号");
                }
                if (!portValue) {
                  return Promise.reject("请输入IP地址或端口号");
                }
                if (isValidIpChar(value)) {
                  return new Promise((resolve, rej) => {
                    setmodalLoading(true);
                    fetchPost(apiRequest.machineManagement.checkHost, {
                      body: {
                        ip: value,
                        id: row.id,
                      },
                    })
                      .then((res) => {
                        if (res && res.data) {
                          if (res.data.data) {
                            resolve("success");
                          } else {
                            rej(`ip地址已存在`);
                          }
                        }
                      })
                      .catch((e) => console.log(e))
                      .finally(() => {
                        setmodalLoading(false);
                      });
                  });
                } else {
                  return Promise.reject("请输入正确格式的IP地址");
                }
              },
            },
          ]}
        >
          <Row gutter={8}>
            <Col span={16}>
              <Form.Item name="IPtext" key="IPtext" noStyle>
                <Input disabled placeholder={"例如: 192.168.10.10"} />
              </Form.Item>
            </Col>
            <span style={{ display: "flex", alignItems: "center" }}>:</span>
            <Col span={4}>
              <Form.Item name="port" key="port" noStyle>
                <InputNumber
                  style={{ width: 82 }}
                  min={1}
                  max={65535}
                  onChange={() => {
                    modalForm.validateFields(["ip"]);
                  }}
                />
              </Form.Item>
            </Col>
          </Row>
        </Form.Item>

        <Form.Item
          label="用户名"
          name="username"
          key="username"
          rules={[
            {
              required: true,
              message: "请输入用户名",
            },
            {
              validator: (rule, value, callback) => {
                var reg = /[^a-zA-Z0-9\_\-]/g;
                var startReg = /[^a-zA-Z0-9\_]/g;
                if (value) {
                  let startChar = value.slice(0, 1);
                  if (!startReg.test(startChar)) {
                    if (isChineseChar(value)) {
                      return Promise.reject(`用户名只支持数字、字母、"-"或"_"`);
                    } else {
                      if (!reg.test(value)) {
                        return Promise.resolve("success");
                      } else {
                        return Promise.reject(
                          `用户名只支持数字、字母、"-"或"_"`
                        );
                      }
                    }
                  } else {
                    return Promise.reject(`用户名开头只支持数字、字母、或"_"`);
                  }
                } else {
                  return Promise.resolve("success");
                }
              },
            },
          ]}
        >
          <Input
            maxLength={16}
            placeholder={"请输入用户名"}
            suffix={
              <Tooltip title="请使用root或具有sudo免密码权限的用户">
                <InfoCircleOutlined style={{ color: "rgba(0,0,0,.45)" }} />
              </Tooltip>
            }
          />
        </Form.Item>

        <Form.Item
          label="密码"
          name="password"
          key="password"
          rules={[
            {
              required: true,
              message: "请输入密码",
            },
            {
              validator: (rule, value, callback) => {
                if (value) {
                  if (!isExpression(value)) {
                    if (isChineseChar(value)) {
                      return Promise.reject("密码不支持中文");
                    } else {
                      if (value.length < 8) {
                        return Promise.reject("密码长度为8到64位");
                      } else {
                        if (isSpace(value)) {
                          return Promise.reject("密码不支持空格");
                        }
                        return Promise.resolve("success");
                      }
                    }
                  } else {
                    return Promise.reject(`密码不支持输入表情`);
                  }
                } else {
                  return Promise.resolve("success");
                }
              },
            },
          ]}
        >
          <Input.Password maxLength={64} placeholder={"请输入密码"} />
        </Form.Item>
      </div>
    </OmpModal>
  );
};

const getHeaderRow = (sheet) => {
  const headers = [];
  const range = XLSX.utils.decode_range(sheet["!ref"]);
  let C;
  const R = range.s.r;
  for (C = range.s.c; C <= range.e.c; ++C) {
    const cell = sheet[XLSX.utils.encode_cell({ c: C, r: R })];
    let hdr = "UNKNOWN " + C;
    if (cell && cell.t) hdr = XLSX.utils.format_cell(cell);
    headers.push(hdr);
  }
  return headers;
};

class UploadExcelComponent extends React.Component {
  state = {
    loading: false,
    excelData: {
      header: null,
      results: null,
    },
  };
  draggerProps = () => {
    let _this = this;
    return {
      name: "file",
      multiple: false,
      accept: ".xlsx",
      maxCount: 1,
      onRemove() {
        _this.props.onRemove();
        return true;
      },
      onChange(info) {
        const { status } = info.file;
        if (status === "done") {
          //console.log(info.file);
          message.success(`${info.file.name} 文件解析成功`);
        } else if (status === "error") {
          message.error(
            `${info.file.name} 文件解析失败, 请确保文件内容格式符合规范后重新上传`
          );
        }
      },
      beforeUpload(file, fileList) {
        //console.log(file);
        // bmf.md5(file,(err,md5)=>{
        //   console.log(err,md5,"=====?---")
        // })
        // 校验文件大小
        const fileSize = file.size / 1024 / 1024; //单位是M
        //console.log(fileSize);
        if (Math.ceil(fileSize) > 10) {
          message.error("仅支持传入10M以内文件");
          return Upload.LIST_IGNORE;
        }
        if (!/\.(xlsx)$/.test(file.name)) {
          message.error("仅支持传入.xlsx文件");
          return Upload.LIST_IGNORE;
        }
      },
      customRequest(e) {
        _this.readerData(e.file).then(
          (msg) => {
            //console.log(e);
            e.onSuccess();
          },
          () => {
            e.onError();
          }
        );
      },
    };
  };
  readerData = (rawFile) => {
    // bmf.md5(rawFile,(err,md5)=>{
    //   console.log(err,md5,"=====?")
    // })
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = (e) => {
        try {
          const data = e.target.result;
          const workbook = XLSX.read(data, { type: "array" });
          const firstSheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[firstSheetName];
          const header = getHeaderRow(worksheet);
          const results = XLSX.utils.sheet_to_json(worksheet);
          //console.log(header, results, "====");
          this.generateData({ header, results });
          resolve();
        } catch (error) {
          reject();
        }
      };
      reader.readAsArrayBuffer(rawFile);
    });
  };
  generateData = ({ header, results }) => {
    this.setState({
      excelData: { header, results },
    });
    this.props.uploadSuccess && this.props.uploadSuccess(this.state.excelData);
  };
  render() {
    return (
      <div>
        <Upload.Dragger {...this.draggerProps()}>
          <p className="ant-upload-drag-icon">
            <CloudUploadOutlined />
          </p>
          <p style={{ textAlign: "center", color: "#575757" }}>
            点击或将文件拖拽到这里上传
          </p>
          <p
            style={{
              textAlign: "center",
              color: "#8e8e8e",
              fontSize: 13,
              paddingTop: 10,
            }}
          >
            支持扩展名: .xlsx
          </p>
        </Upload.Dragger>
      </div>
    );
  }
}

/* 批量导入主机 */
export const BatchImportMachineModal = ({
  batchImport,
  setBatchImport,
  refreshData,
}) => {
  const [dataSource, setDataSource] = useState([]);
  const [columns, setColumns] = useState([]);

  // 校验后的表格的colums和dataSource也是不确定的
  // 因为不单是在表格展示中需要区分校验成功与否，在这里定义多个数据源用以区分是否成功
  const [tableCorrectData, setTableCorrectData] = useState([]);
  const [tableErrorData, setTableErrorData] = useState([]);
  const [tableColumns, setTableColumns] = useState([]);

  const [stepNum, setStepNum] = useState(0);

  const [loading, setLoading] = useState(false);

  // 失败的columns
  const errorColumns = [
    {
      title: "行数",
      key: "row",
      dataIndex: "row",
      align: "center",
      //render: nonEmptyProcessing,
      width: 60,
      ellipsis: true,
      fixed: "left",
    },
    {
      title: "实例名称",
      key: "instance_name",
      dataIndex: "instance_name",
      align: "center",
      //render: nonEmptyProcessing,
      width: 140,
      ellipsis: true,
      //fixed: "left",
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
    },
    {
      title: "IP地址",
      key: "ip",
      dataIndex: "ip",
      // sorter: (a, b) => a.ip - b.ip,
      // sortDirections: ["descend", "ascend"],
      align: "center",
      width: 140,
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
      ellipsis: true,
      //fixed: "left"
    },
    {
      title: "端口",
      key: "port",
      dataIndex: "port",
      // sorter: (a, b) => a.ip - b.ip,
      // sortDirections: ["descend", "ascend"],
      align: "center",
      width: 80,
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
      //ellipsis: true,
    },
    {
      title: "数据分区",
      key: "data_folder",
      dataIndex: "data_folder",
      // sorter: (a, b) => a.ip - b.ip,
      // sortDirections: ["descend", "ascend"],
      align: "center",
      width: 180,
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
      ellipsis: true,
    },
    {
      title: "失败原因",
      key: "validate_error",
      dataIndex: "validate_error",
      fixed: "right",
      // sorter: (a, b) => a.ip - b.ip,
      // sortDirections: ["descend", "ascend"],
      align: "center",
      width: 240,
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
      ellipsis: true,
    },
  ];

  // 成功的columns
  const correctColumns = [
    {
      title: "实例名称",
      key: "instance_name",
      dataIndex: "instance_name",
      align: "center",
      //render: nonEmptyProcessing,
      width: 140,
      ellipsis: true,
      fixed: "left",
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
    },
    {
      title: "IP地址",
      key: "ip",
      dataIndex: "ip",
      align: "center",
      width: 140,
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
      ellipsis: true,
    },
    {
      title: "端口",
      key: "port",
      dataIndex: "port",
      align: "center",
      width: 80,
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
    },
    {
      title: "数据分区",
      key: "data_folder",
      dataIndex: "data_folder",
      align: "center",
      width: 180,
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
      ellipsis: true,
    },
    {
      title: "用户名",
      key: "username",
      dataIndex: "username",
      align: "center",
      width: 120,
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
      ellipsis: true,
    },
    {
      title: "密码",
      key: "password",
      dataIndex: "password",
      align: "center",
      width: 130,
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
      ellipsis: true,
    },
    {
      title: "是否执行初始化",
      key: "init_host",
      dataIndex: "init_host",
      align: "center",
      width: 120,
      render: (text) => {
        return (
          <span>{text === false ? "否" : text === true ? "是" : "-"}</span>
        );
      },
      ellipsis: true,
    },
    {
      title: "系统",
      key: "operate_system",
      dataIndex: "operate_system",
      align: "center",
      width: 120,
      fixed: "right",
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
      ellipsis: true,
    },
  ];

  // 校验数据接口
  const fetchBatchValidate = () => {
    if (dataSource.length == 0) {
      message.warning(
        "解析结果中无有效数据，请确保文件内容格式符合规范后重新上传"
      );
      return;
    }
    setLoading(true);
    setTableCorrectData([]);
    setTableErrorData([]);
    let queryBody = dataSource.map((item) => {
      let result = {};
      for (const key in item) {
        switch (key) {
          case "IP[必填]":
            result.ip = item[key];
            break;
          case "实例名[必填]":
            result.instance_name = item[key];
            break;
          case "密码[必填]":
            result.password = item[key];
            break;
          case "操作系统[必填]":
            result.operate_system = item[key];
            break;
          case "数据分区[必填]":
            result.data_folder = item[key];
            break;
          case "用户名[必填]":
            result.username = item[key];
            break;
          case "端口[必填]":
            result.port = item[key];
            break;
          default:
            break;
        }
      }
      return {
        ...result,
        row: item.key,
      };
    });
    // console.log(queryBody)
    // 校验数据
    fetchPost(apiRequest.machineManagement.batchValidate, {
      body: {
        host_list: queryBody,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.code == 0) {
            if (res.data && res.data.error?.length > 0) {
              setTableErrorData(
                res.data.error?.map((item, idx) => {
                  return {
                    key: idx,
                    ...item,
                  };
                })
              );
              setTableColumns(errorColumns);
            } else {
              setTableCorrectData(
                res.data.correct?.map((item, idx) => {
                  return {
                    key: idx,
                    ...item,
                  };
                })
              );
              setTableColumns(correctColumns);
            }
            setStepNum(1);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  // 主机创建操作
  const fetchBatchImport = () => {
    let queryBody = tableCorrectData.map((item) => {
      delete item.key;
      return {
        ...item,
      };
    });
    setLoading(true);
    fetchPost(apiRequest.machineManagement.batchImport, {
      body: {
        host_list: queryBody,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.code == 0) {
            setStepNum(2);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <Modal
      title={
        <span>
          <span style={{ position: "relative", left: "-10px" }}>
            <ImportOutlined />
          </span>
          <span>批量创建主机</span>
        </span>
      }
      visible={batchImport}
      footer={null}
      width={800}
      loading={loading}
      // onFinish={(data) => {
      //   createHost(data);
      //   //onFinish("post", data);
      // }}
      bodyStyle={{
        paddingLeft: 30,
        paddingRight: 30,
      }}
      onCancel={() => {
        setBatchImport(false);
      }}
      afterClose={() => {
        setDataSource([]);
        setTableCorrectData([]);
        setTableErrorData([]);
        setTableColumns([]);
        setStepNum(0);
        setColumns([]);
        refreshData();
      }}
      destroyOnClose
    >
      <Steps size="small" current={stepNum}>
        <Steps.Step title="上传文件" />
        <Steps.Step title="数据校验" />
        <Steps.Step title="创建结果" />
      </Steps>
      <div style={{ paddingLeft: 30, paddingTop: 30 }}>
        <div
          style={{
            visibility: stepNum == 0 ? "visible" : "hidden",
            height: stepNum == 0 ? null : 0,
            overflow: "hidden",
          }}
        >
          <div style={{ display: "flex", alignItems: "center" }}>
            <div style={{ flex: 1, fontWeight: 500 }}>下载模版: </div>
            <div style={{ flex: 10, paddingLeft: 20 }}>
              <Button
                icon={<DownloadOutlined />}
                size="middle"
                style={{ fontSize: 13 }}
                onClick={() => {
                  let a = document.createElement("a");
                  a.href = apiRequest.machineManagement.downTemplate;
                  document.body.appendChild(a);
                  a.click();
                  document.body.removeChild(a);
                }}
              >
                点击下载
              </Button>
            </div>
          </div>
          <div style={{ display: "flex", marginTop: 30 }}>
            <div style={{ flex: 1, fontWeight: 500 }}>上传文件: </div>
            <div style={{ flex: 10, paddingLeft: 20 }}>
              {batchImport && (
                <UploadExcelComponent
                  onRemove={() => {
                    setDataSource([]);
                    setColumns([]);
                    setTableCorrectData([]);
                    setTableErrorData([]);
                    setTableColumns([]);
                  }}
                  uploadSuccess={({ results, header }) => {
                    //console.log(results, header);
                    let dataS = results
                      .filter((item) => {
                        if (item["字段名称(请勿编辑)"]?.includes("请勿编辑")) {
                          return false;
                        }
                        if (!item["实例名[必填]"]) {
                          return false;
                        }
                        return true;
                      })
                      .map((item, idx) => {
                        return { ...item, key: item.__rowNum__ + 1 };
                      });
                    let column = header.filter((item) => {
                      if (
                        item?.includes("请勿编辑") ||
                        item?.includes("UNKNOWN")
                      ) {
                        return false;
                      }
                      return true;
                    });

                    setDataSource(dataS);
                    setColumns(column);
                  }}
                />
              )}

              <div
                style={{
                  display: "inline-block",
                  marginLeft: "50%",
                  transform: "translateX(-50%)",
                  marginTop: 40,
                }}
              >
                <Button
                  loading={loading}
                  onClick={() => fetchBatchValidate()}
                  type="primary"
                  disabled={columns.length == 0}
                >
                  校验
                </Button>
              </div>
            </div>
          </div>
        </div>
        {stepNum == 1 && (
          <>
            {tableErrorData.length > 0 ? (
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  paddingBottom: 10,
                  flexDirection: "column",
                }}
              >
                <p
                  style={{
                    display: "flex",
                    alignItems: "center",
                    fontSize: 20,
                    color: "#f73136",
                  }}
                >
                  <CloseCircleFilled
                    style={{ color: "#f73136", fontSize: 30, marginRight: 10 }}
                  />
                  数据校验失败 !
                </p>
                <p style={{ fontSize: 13 }}>请核对并修改信息后，再重新提交</p>
              </div>
            ) : (
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  paddingBottom: 10,
                }}
              >
                <p
                  style={{
                    display: "flex",
                    alignItems: "center",
                    fontSize: 20,
                  }}
                >
                  <CheckCircleFilled
                    style={{ color: "#52c41a", fontSize: 30, marginRight: 10 }}
                  />
                  数据校验成功 !
                </p>
              </div>
            )}

            <OmpTable
              bordered
              scroll={{ x: 700 }}
              columns={tableColumns}
              dataSource={
                tableErrorData.length > 0 ? tableErrorData : tableCorrectData
              }
              pagination={{
                pageSize: 5,
              }}
            />
            <div
              style={{
                display: "inline-block",
                marginLeft: "50%",
                transform: "translateX(-50%)",
                marginTop: 40,
              }}
            >
              <Button
                style={{ marginRight: 16 }}
                onClick={() => {
                  setStepNum(0);
                }}
              >
                上一步
              </Button>
              <Button
                loading={loading}
                type="primary"
                htmlType="submit"
                onClick={() => {
                  fetchBatchImport();
                }}
                disabled={tableErrorData.length > 0}
              >
                创建
              </Button>
            </div>
          </>
        )}
        {stepNum == 2 && (
          <>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                paddingBottom: 20,
                paddingTop: 30,
              }}
            >
              <p
                style={{ display: "flex", alignItems: "center", fontSize: 20 }}
              >
                <CheckCircleFilled
                  style={{ color: "#52c41a", fontSize: 30, marginRight: 10 }}
                />
                主机创建完成 !
              </p>
            </div>
            <p style={{ textAlign: "center" }}>
              本次共创建 {tableCorrectData.length} 台主机
            </p>
            <div
              style={{
                display: "inline-block",
                marginLeft: "50%",
                transform: "translateX(-50%)",
                marginTop: 40,
              }}
            >
              <Button
                loading={loading}
                type="primary"
                htmlType="submit"
                onClick={() => {
                  setBatchImport(false);
                }}
              >
                完成
              </Button>
            </div>
          </>
        )}
      </div>
    </Modal>
  );
};
