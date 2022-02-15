import { OmpContentWrapper, OmpTable } from "@/components";
import {
  Switch,
  Spin,
  Form,
  Input,
  Button,
  Select,
  Tooltip,
  TimePicker,
  message,
  Checkbox,
  Row,
  InputNumber,
} from "antd";
import { useState, useEffect, useRef } from "react";
import { handleResponse } from "@/utils/utils";
import { fetchGet, fetchDelete, fetchPost, fetchPut } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import styles from "./index.module.less";
import {
  SettingOutlined,
  InfoCircleOutlined,
  SaveOutlined,
  FileSearchOutlined,
} from "@ant-design/icons";

const SelfHealingStrategy = () => {
  const [loading, setLoading] = useState(false);

  const [form] = Form.useForm();

  const [isOpen, setIsOpen] = useState(false);

  // const [maxHealingCount, setMaxHealingCount] = useState(0);

  // const onHealingCountChange = (e) => {
  //   setMaxHealingCount(e);
  // };

  // 查询策略
  const queryData = () => {
    setLoading(true);
    fetchGet(apiRequest.faultSelfHealing.querySelfHealingStrategy, {
      params: {
        env_id: "1",
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          console.log(res, "res");
          if (res && res.data) {
            setIsOpen(res.data.used);
          }
          form.setFieldsValue({
            isOpen: res.data.used,
          });
          if (res.data.used) {
            form.setFieldsValue({
              times: {
                value: res.data.max_healing_count,
              }
            });
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  // 保存策略
  const save = (data) => {
    console.log(data)
    let used = data.isOpen;
    let max_healing_count = 0;
    if (used) {
      max_healing_count = data.times.value;
    }
    setLoading(true);
    fetchPost(apiRequest.faultSelfHealing.setSelfHealingSetting, {
      body: {
        max_healing_count: max_healing_count,
        used: used,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.code == 0) {
            message.success("修改自愈策略成功");
          }
          if (res.code == 1) {
            message.warning(res.message);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
        queryData();
      });
  };

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

  useEffect(() => {
    queryData();
  }, []);

  return (
    <OmpContentWrapper>
      <div className={styles.header}>
        <SettingOutlined style={{ paddingRight: 5 }} />
        自愈设置
      </div>
      <Spin spinning={loading}>
        <Form
          name="pushSetting"
          labelCol={{ span: 3 }}
          wrapperCol={{ span: 8 }}
          style={{ paddingTop: 20, paddingBottom: 10 }}
          onFinish={save}
          form={form}
          initialValues={{
            times: {
              value: 1,
            },
          }}
        >
          <Form.Item label="启用" name="isOpen" valuePropName="checked">
            <Switch
              onChange={(e) => setIsOpen(e)}
              style={{ borderRadius: "10px" }}
            />
          </Form.Item>
          {isOpen && (
            <>
              <Form.Item label="自愈尝试次数">
                <Input.Group compact>
                  <Form.Item
                    name={["times", "value"]}
                    noStyle
                    rules={[
                      {
                        required: true,
                        message: "请输入自愈尝试次数",
                      },
                      {
                        validator: (rule, value, callback) => {
                          if (value && value > 20) {
                            return Promise.reject("自愈尝试次数不超过20次");
                          }
                          return Promise.resolve();
                        },
                      },
                    ]}
                  >
                    <InputNumber
                      min={1}
                      formatter={limitNumber}
                      parser={limitNumber}
                      // value={maxHealingCount}
                      // onChange={onHealingCountChange}
                    />
                  </Form.Item>
                  <Form.Item name={["name", "icon"]} noStyle>
                    <Tooltip
                      placement="top"
                      title={
                        "自愈操作执行第n次之后, 服务依旧异常, 停止自愈操作, 发送告警邮件"
                      }
                    >
                      <InfoCircleOutlined
                        name="icon"
                        style={{
                          color: "rgba(0,0,0,.45)",
                          position: "relative",
                          top: 8,
                          left: 15,
                          fontSize: 15,
                        }}
                      />
                    </Tooltip>
                  </Form.Item>
                </Input.Group>
              </Form.Item>
            </>
          )}
        </Form>
      </Spin>

      <div className={styles.header} style={{ marginTop: 50 }}>
        <FileSearchOutlined style={{ paddingRight: 5 }} />
        自愈策略
      </div>
      <div
        style={{
          border: "1px solid #ebeef2",
          backgroundColor: "white",
          marginTop: 30,
        }}
      >
        <OmpTable
          // size={"small"}
          noScroll
          columns={[
            {
              title: "序列",
              width: 40,
              align: "center",
              key: "idx",
              dataIndex: "idx",
            },
            {
              title: "自愈类型",
              width: 100,
              align: "center",
              key: "type",
              dataIndex: "type",
            },
            {
              title: "服务名称",
              width: 100,
              align: "center",
              key: "name",
              dataIndex: "name",
            },
            {
              title: "自愈条件",
              width: 180,
              align: "center",
              key: "condition",
              dataIndex: "condition",
            },
          ]}
          dataSource={[
            {
              idx: "1",
              type: "进程拉起",
              name: "ALL",
              condition: "当服务进程消失时,自动拉起进程",
            },
          ]}
          pagination={{
            hideOnSinglePage: true,
          }}
        />
      </div>

      <Spin spinning={loading}>
        <Form
          name="pushSetting"
          labelCol={{ span: 3 }}
          wrapperCol={{ span: 8 }}
          style={{ paddingTop: 30 }}
          onFinish={save}
          form={form}
        >
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

export default SelfHealingStrategy;
