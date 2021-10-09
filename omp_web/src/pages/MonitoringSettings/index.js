import {
  OmpContentWrapper,
} from "@/components";
import {
  Button,
  Input,
  Form,
  message,
  Tabs,
  Spin,
} from "antd";
import { useState, useEffect, useRef } from "react";
import {
  handleResponse,
} from "@/utils/utils";
import { fetchGet, fetchPatch } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
//import updata from "@/store_global/globalStore";
import styles from "./index.module.less";

const MonitoringSettings = () => {
  const [loading, setLoading] = useState(false);
  //数据
  const [dataSource, setDataSource] = useState([]);

  const [form] = Form.useForm();

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
                    prometheus: item.monitor_url
                  })
                return;
              case "alertmanager":
                form.setFieldsValue({
                    alertmanager: item.monitor_url
                  })
                return;
              case "grafana":
                form.setFieldsValue({
                    grafana: item.monitor_url
                  })
                return;
              default:
                return;
            }
          });
          let dir = {}
          res.data.map(item=>{
              dir[item.name] = item.id
          })
          setDataSource(dir);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  }

  const multipleUpdate = (data)=>{
   //  console.log(data)
    const arr = Object.keys(data).map(key=>{
        return {
            id:dataSource[key],
            monitor_url:data[key]
        }
    })
    setLoading(true);
    fetchPatch(apiRequest.MonitoringSettings.multiple_update, {
      body: {
        data:arr
      },
    })
      .then((res) => {
        if (res && res.data) {
          if (res.data.code == 1) {
            message.warning(res.data.message);
          }
          if (res.data.code == 0) {
            message.success("更新监控平台配置成功");
            fetchData()
          }
        }
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  }

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <OmpContentWrapper>
      <div className={styles.wrapper}>
        <Tabs defaultActiveKey="1">
          <Tabs.TabPane tab="监控平台配置" key="1">
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
                  ]}
                >
                  <Input
                    addonBefore="Http://"
                    placeholder="请输入 Prometheus 地址"
                  />
                </Form.Item>

                <Form.Item
                  label="Grafana地址"
                  name="grafana"
                  rules={[{ required: true, message: "请输入 Grafana 地址" }]}
                >
                  <Input
                    addonBefore="Http://"
                    placeholder="请输入 Grafana 地址"
                  />
                </Form.Item>

                <Form.Item
                  label="Alert Manager地址"
                  name="alertmanager"
                  rules={[
                    { required: true, message: "请输入 Alert Manager 地址" },
                  ]}
                >
                  <Input
                    addonBefore="Http://"
                    placeholder="请输入 Alert Manager 地址"
                  />
                </Form.Item>

                <Form.Item
                  style={{ paddingTop: 30 }}
                  wrapperCol={{ offset: 6, span: 16 }}
                >
                  <Button type="primary" htmlType="submit">
                    保存
                  </Button>
                </Form.Item>
              </Form>
            </Spin>
          </Tabs.TabPane>
        </Tabs>
      </div>
    </OmpContentWrapper>
  );
};

export default MonitoringSettings;
