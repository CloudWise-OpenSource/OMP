import { OmpModal } from "@/components";

import {
  Button,
  Input,
  Select,
  Badge,
  Form,
  message,
  Menu,
  Dropdown,
  InputNumber,
  Row,
  Col,
  Tooltip,
} from "antd";
import {
  PlusSquareOutlined,
  FormOutlined,
  InfoCircleOutlined,
} from "@ant-design/icons";
import {
  MessageTip,
  isChineseChar,
  isNumberChar,
  isLowercaseChar,
  isValidIpChar,
  isExpression,
  isLetterChar,
  isSpace
} from "@/utils/utils";
import { fetchPost } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { useState, useRef } from "react";
import star from "./asterisk.svg";

//const [modalForm] = Form.useForm();

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
  const timer2 = useRef(null)
  return (
    <OmpModal
    loading={modalLoading ? modalLoading : loading}
      setLoading={setLoading}
      visibleHandle={visibleHandle}
      okBtnText={modalLoading ? "校验中" : (loading?"创建中":null)}
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
                        if(isSpace(value)){
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
                // rules={[
                //   {

                //   },
                // ]}
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
            suffix={
              <Tooltip title="请使用root或具有sudo免密码权限的用户">
                <InfoCircleOutlined style={{ color: "rgba(0,0,0,.45)" }} />
              </Tooltip>
            }
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
                        return Promise.reject("密码长度为8到16位");
                      } else {
                        if(isSpace(value)){
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
          <Input.Password maxLength={16} placeholder={"请输入密码"} />
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
      okBtnText={modalLoading ? "校验中" : (loading?"修改中":null)}
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
        password: window.atob(row.password),
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
                        if(isSpace(value)){
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
              <Form.Item
                name="IPtext"
                key="IPtext"
                noStyle
                // rules={[
                //   {
                //     validator: (rule, value, callback) => {
                //       if (isValidIpChar(value) || !value) {
                //         return Promise.resolve("success");
                //       } else {
                //         return Promise.reject("请输入正确格式的IP地址");
                //       }
                //     },
                //   },
                // ]}
              >
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
                        return Promise.reject("密码长度为8到16位");
                      } else {
                        if(isSpace(value)){
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
          <Input.Password maxLength={16} placeholder={"请输入密码"} />
        </Form.Item>
      </div>
    </OmpModal>
  );
};
