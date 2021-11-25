import { OmpContentWrapper } from "@/components";
import { Button, Input, Form, message, Tabs, Spin, Switch } from "antd";
import { useState, useEffect, useRef } from "react";
import { handleResponse, isLowercaseChar } from "@/utils/utils";
import { fetchGet, fetchPost, fetchPatch } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { SettingOutlined, MailOutlined } from "@ant-design/icons";
//import updata from "@/store_global/globalStore";
import styles from "./index.module.less";
import { use } from "echarts";

const MonitoringSettings = () => {
  const [loading, setLoading] = useState(false);
  const [pushLoading, setPushLoading] = useState(false);

  //数据
  const [dataSource, setDataSource] = useState([]);

  const [form] = Form.useForm();
  const [pushForm] = Form.useForm();

  const [pushIsOpen, setPushIsOpen] = useState(false);

  //auth/users
  function fetchData() {
    setLoading(true);
    fetchGet(apiRequest.MonitoringSettings.monitorurl)
      .then((res) => {
        handleResponse(res, (res) => {
          // console.log(res.data);
          res.data.map((item) => {
            switch (item.name) {
              case "prometheus":
                form.setFieldsValue({
                  prometheus: item.monitor_url,
                });
                return;
              case "alertmanager":
                form.setFieldsValue({
                  alertmanager: item.monitor_url,
                });
                return;
              case "grafana":
                form.setFieldsValue({
                  grafana: item.monitor_url,
                });
                return;
              default:
                return;
            }
          });
          let dir = {};
          res.data.map((item) => {
            dir[item.name] = item.id;
          });
          setDataSource(dir);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  }

  // 查询推送数据
  const fetchPushDate = () => {
    setPushLoading(true);
    fetchGet(apiRequest.MonitoringSettings.queryPushConfig)
      .then((res) => {
        handleResponse(res, (res) => {
          if (res && res.data) {
            console.log(res);
            const { used, server_url } = res.data.email;
            pushForm.setFieldsValue({
              pushIsOpen: used,
              email: server_url,
            });
            setPushIsOpen(used);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setPushLoading(false);
      });
  };

  const multipleUpdate = (data) => {
    //  console.log(data)
    const arr = Object.keys(data).map((key) => {
      return {
        id: dataSource[key],
        monitor_url: data[key],
      };
    });
    setLoading(true);
    fetchPatch(apiRequest.MonitoringSettings.multiple_update, {
      body: {
        data: arr,
      },
    })
      .then((res) => {
        if (res && res.data) {
          if (res.data.code == 1) {
            message.warning(res.data.message);
          }
          if (res.data.code == 0) {
            message.success("更新监控平台配置成功");
            fetchData();
          }
        }
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchData();
    fetchPushDate();
  }, []);

  // 定义监控地址校验函数
  const validateMonitorAddress = (rule, value, callback, title) => {
    if (value) {
      var reg = /[^a-zA-Z0-9\-\_\.\~\!\*\'\(\)\;\:\@\&\=\+\$\,\/\?\#\[\]]/g;
      if (!reg.test(value)) {
        return Promise.resolve("success");
      } else {
        return Promise.reject(`${title}地址存在非法字符`);
      }
    } else {
      return Promise.resolve("success");
    }
  };

  // 改变告警邮件推送
  const changePush = (data) => {
    setPushLoading(true);
    fetchPost(apiRequest.MonitoringSettings.updatePushConfig, {
      body: {
        way_name: "email",
        env_id: 0,
        server_url: pushForm.getFieldValue("email"),
        used: data.pushIsOpen,
      },
    })
      .then((res) => {
        if (res && res.data) {
          if (res.data.code == 1) {
            message.warning(res.data.message);
          }
          if (res.data.code == 0) {
            message.success("更新监控推送设置成功");
          }
        }
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setPushLoading(false);
        fetchPushDate();
      });
  };

  return (
    <OmpContentWrapper>
      <div className={styles.header}>
        <SettingOutlined style={{ paddingRight: 5 }} />
        监控平台配置
      </div>
      <Spin spinning={loading}>
        <Form
          name="setting"
          labelCol={{ span: 3 }}
          wrapperCol={{ span: 6 }}
          style={{ paddingTop: 40 }}
          onFinish={multipleUpdate}
          form={form}
        >
          <Form.Item
            label="Prometheus地址"
            name="prometheus"
            rules={[
              { required: true, message: "请输入 Prometheus 地址" },
              {
                validator: (rule, value, callback) => {
                  return validateMonitorAddress(
                    rule,
                    value,
                    callback,
                    "Prometheus"
                  );
                },
              },
            ]}
          >
            <Input
              addonBefore="Http://"
              placeholder="请输入 Prometheus 地址"
              style={{
                width: 360,
              }}
            />
          </Form.Item>

          <Form.Item
            label="Grafana地址"
            name="grafana"
            rules={[
              { required: true, message: "请输入 Grafana 地址" },
              {
                validator: (rule, value, callback) => {
                  return validateMonitorAddress(
                    rule,
                    value,
                    callback,
                    "Grafana"
                  );
                },
              },
            ]}
          >
            <Input
              addonBefore="Http://"
              placeholder="请输入 Grafana 地址"
              style={{
                width: 360,
              }}
            />
          </Form.Item>

          <Form.Item
            label="Alert Manager地址"
            name="alertmanager"
            rules={[
              { required: true, message: "请输入 Alert Manager 地址" },
              {
                validator: (rule, value, callback) => {
                  return validateMonitorAddress(
                    rule,
                    value,
                    callback,
                    "Alert Manager"
                  );
                },
              },
            ]}
          >
            <Input
              addonBefore="Http://"
              placeholder="请输入 Alert Manager 地址"
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

      {/* 告警邮件 */}
      <div className={styles.header}>
        <MailOutlined style={{ paddingRight: 5 }} />
        告警邮件
      </div>
      <Spin spinning={pushLoading}>
        <Form
          name="pushSetting"
          labelCol={{ span: 3 }}
          wrapperCol={{ span: 6 }}
          style={{ paddingTop: 40 }}
          onFinish={changePush}
          form={pushForm}
          initialValues={{
            pushIsOpen: false,
          }}
        >
          <Form.Item label="邮件推送" name="pushIsOpen" valuePropName="checked">
            <Switch
              onChange={(e) => setPushIsOpen(e)}
              style={{ borderRadius: "10px" }}
            />
          </Form.Item>
          {pushIsOpen && (
            <Form.Item
              label="接收人"
              name="email"
              rules={[
                {
                  type: "email",
                  message: "请输入正确格式的邮箱",
                },
                {
                  required: true,
                  message: "请输入接收人邮箱",
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
          )}
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

export default MonitoringSettings;
