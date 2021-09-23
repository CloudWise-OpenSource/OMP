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
} from "antd";

export const AddMachineModal = ({ loading, visibleHandle, onFinish }) => {
  return (
    <OmpModal
      loading={loading}
      visibleHandle={visibleHandle}
      title="创建主机信息"
      onFinish={(data) => {
        onFinish("post", data);
      }}
    >
      <Form.Item
        label="实例名称"
        name="name"
        key="name"
        //useforminstanceinonchange="true"
        // onChange={(e,formInstance)=>{
        //   console.log("onchange",e,"p",f)
        // }}
        rules={[
          {
            required: true,
            message: "请输入实例名称",
          },
        //   {
        //     validator: (rule, value, callback, passwordModalForm) => {
        //       const reg =
        //         /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/;
        //       if (reg.test(value) || !value) {
        //         return Promise.resolve("success");
        //       } else {
        //         return Promise.reject("请输入正确的ip地址");
        //       }
        //     },
        //   },
        ]}
      >
        <Input placeholder={"请输入实例名称"} />
      </Form.Item>

      <Form.Item
        label="系统平台"
        name="systemPlatform"
        key="systemPlatform"
        //useforminstanceinonchange="true"
        // onChange={(e,formInstance)=>{
        //   console.log("onchange",e,"p",f)
        // }}
        rules={[
          {
            required: true,
            message: "请选择系统平台",
          },
        //   {
        //     validator: (rule, value, callback, passwordModalForm) => {
        //       const reg =
        //         /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/;
        //       if (reg.test(value) || !value) {
        //         return Promise.resolve("success");
        //       } else {
        //         return Promise.reject("请输入正确的ip地址");
        //       }
        //     },
        //   },
        ]}
      >
        <Select placeholder={"请选择系统平台"}>
            <Select.Option value="CentOS">CentOS</Select.Option>
        </Select>
      </Form.Item>
      {/* <Form.Item
        label="主机IP"
        name="ip"
        key="ip"
        //useforminstanceinonchange="true"
        // onChange={(e,formInstance)=>{
        //   console.log("onchange",e,"p",f)
        // }}
        rules={[
          {
            required: true,
            message: "请输入主机IP",
          },
          {
            validator: (rule, value, callback, passwordModalForm) => {
              const reg =
                /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/;
              if (reg.test(value) || !value) {
                return Promise.resolve("success");
              } else {
                return Promise.reject("请输入正确的ip地址");
              }
            },
          },
        ]}
      >
        <Input placeholder={"请输入主机IP"} />
      </Form.Item>

      <Form.Item
        label="SSH端口"
        name="ssh_port"
        key="ssh_port"
        //useforminstanceinonchange="true"
        // onChange={(e,f)=>{
        //   console.log("onchange",e,f)
        // }}
        rules={[
          {
            required: true,
            message: "请输入SSH端口",
          },
          {
            validator: (rule, value, callback, passwordModalForm) => {
              const reg = /^-?[0-9]*([0-9]*)?$/;
              if (value && reg.test(value)) {
                if (value <= 65535 && value > 0) {
                  return Promise.resolve("success");
                } else {
                  return Promise.reject("端口号大于0且小于等于65535");
                }
              } else {
                if (value) {
                  return Promise.reject("请输入正确的SSH端口号");
                } else {
                  //没有值的话交给第一条校验规则就行，避免同时出现两个message提示
                  return Promise.resolve("success");
                }
              }
            },
          },
        ]}
      >
        <Input placeholder="请输入SSH端口号" />
      </Form.Item>

      <Form.Item
        label="登录用户"
        name="username"
        key="username"
        rules={[
          {
            required: true,
            message: "请输入用户名",
          },
        ]}
      >
        <Input placeholder={"请输入用户名"} />
      </Form.Item>

      <Form.Item
        label="输入密码"
        name="password"
        key="password"
        rules={[
          {
            required: true,
            message: "请输入密码",
          },
          {
            validator: (rule, value) => {
              const reg = /[\u4E00-\u9FA5]/g;
              if (reg.test(value)) {
                return Promise.reject("密码不支持中文");
              } else {
                return Promise.resolve("success");
              }
            },
          },
        ]}
      >
        <Input.Password placeholder={"请输入密码"} />
      </Form.Item>

      <Form.Item
        label="确认密码"
        name="passwordAgain"
        key="passwordAgain"
        useforminstanceinvalidator="true"
        rules={[
          {
            required: true,
            message: "请再次输入密码",
          },
          {
            validator: (rule, value, callback, passwordModalForm) => {
              if (
                passwordModalForm.getFieldValue().password === value ||
                !value
              ) {
                return Promise.resolve("success");
              } else {
                return Promise.reject("两次密码输入不一致");
              }
            },
          },
        ]}
      >
        <Input.Password placeholder={"请再次确认密码"} />
      </Form.Item> */}
    </OmpModal>
  );
};
