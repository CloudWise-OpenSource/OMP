import { OmpContentWrapper } from "@/components";
import { Spin, Form, Input, Button, InputNumber, message } from "antd";
import { useState, useEffect } from "react";
import { handleResponse, _idxInit } from "@/utils/utils";
import { fetchGet, fetchPost } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import styles from "./index.module.less";
import { MailOutlined } from "@ant-design/icons";

const EmailSettings = () => {
  const [loading, setLoading] = useState(false);
  const [dataSource, setDataSource] = useState([]);
  const [form] = Form.useForm();

  function fetchData() {
    setLoading(true);
    fetchGet(apiRequest.emailSetting.querySetting)
      .then((res) => {
        handleResponse(res, (res) => {
          form.setFieldsValue({
            address: res.data.host,
            port: res.data.port,
            email: res.data.username,
            token: res.data.password,
          });
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  }

  const multipleUpdate = (data) => {
    setLoading(true);
    fetchPost(apiRequest.emailSetting.updateSetting, {
      body: {
        host: data.address,
        port: data.port,
        username: data.email,
        password: data.token,
      },
    })
      .then((res) => {
        console.log(res);
        if (res && res.data) {
          if (res.data.code == 1) {
            message.warning(res.data.message);
          }
          if (res.data.code == 0) {
            message.success("更新邮件全局设置成功");
          }
        }
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
        fetchData();
      });
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <OmpContentWrapper>
      <div className={styles.header}>
        <MailOutlined style={{ paddingRight: 5 }} />
        全局设置
      </div>
      <Spin spinning={loading}>
        <Form
          name="email-setting"
          labelCol={{ span: 3 }}
          wrapperCol={{ span: 6 }}
          style={{ paddingTop: 40 }}
          onFinish={multipleUpdate}
          form={form}
        >
          <Form.Item
            label="邮件服务器"
            name="address"
            rules={[{ required: true, message: "请输入邮件服务器地址" }]}
          >
            <Input
              placeholder="例如: 192.168.10.10"
              style={{
                width: 360,
              }}
            />
          </Form.Item>

          <Form.Item
            label="端口号"
            name="port"
            rules={[{ required: true, message: "请输入端口号" }]}
          >
            <InputNumber
              placeholder="例如: 465"
              min={1}
              max={65535}
              style={{
                width: 360,
              }}
            />
          </Form.Item>

          <Form.Item
            label="发件人邮箱"
            name="email"
            rules={[
              {
                type: "email",
                message: "请输入正确格式的邮箱",
              },
              {
                required: true,
                message: "请输入发件人邮箱",
              },
            ]}
          >
            <Input
              placeholder="例如: emailname@163.com"
              style={{
                width: 360,
              }}
            />
          </Form.Item>

          <Form.Item
            label="发件人令牌"
            name="token"
            rules={[{ required: true, message: "请输入发件人令牌" }]}
          >
            <Input.Password
              placeholder="请输入Token"
              style={{
                width: 360,
              }}
            />
          </Form.Item>

          <Form.Item className={styles.saveButtonWrapper}>
            <Button
              type="primary"
              htmlType="submit"
              className={styles.saveButton}
            >
              保存
            </Button>
          </Form.Item>
        </Form>
      </Spin>
    </OmpContentWrapper>
  );
};

export default EmailSettings;
