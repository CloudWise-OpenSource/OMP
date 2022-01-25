import { OmpContentWrapper } from "@/components";
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
} from "@ant-design/icons";
import moment from "moment";
import star from "@/pages/BackupRecords/config/asterisk.svg";

const SelfHealingStrategy = () => {
  const [loading, setLoading] = useState(false);

  const [form] = Form.useForm();

  const [isOpen, setIsOpen] = useState(false);
  const [pushIsOpen, setPushIsOpen] = useState(false);
  const [frequency, setFrequency] = useState("day");

  // 备份组件全量数据
  const [canBackupIns, setCanBackupIns] = useState([]);
  // 选中数据
  const [backupIns, setBackupIns] = useState([]);

  let weekData = [
    "星期一",
    "星期二",
    "星期三",
    "星期四",
    "星期五",
    "星期六",
    "星期日",
  ];

  const queryBackupSettingData = () => {
    setLoading(true);
    fetchGet(apiRequest.dataBackup.queryBackupSettingData, {
      params: {
        env_id: 1,
      },
    })
      .then((res) => {
        handleResponse(res, () => {
          let backup_setting = res.data.data.backup_setting;
          let crontab_detail = backup_setting.crontab_detail;

          form.setFieldsValue({
            retain_path: backup_setting.retain_path,
            pushIsOpen: backup_setting.send_email,
            isOpen: backup_setting.is_on,
            email: backup_setting.to_users,
          });

          if (backup_setting?.retain_day) {
            form.setFieldsValue({
              retain_day: backup_setting.retain_day,
            });
          }
          if (crontab_detail && crontab_detail?.day_of_week) {
            if (crontab_detail?.day_of_week !== "*") {
              setFrequency("week");
              form.setFieldsValue({
                strategy: {
                  frequency: "week",
                  time: moment(
                    `${crontab_detail.hour}:${crontab_detail.minute}`,
                    "HH:mm"
                  ),
                  week: crontab_detail.day_of_week,
                },
              });
            }

            if (crontab_detail?.day !== "*") {
              setFrequency("month");
              form.setFieldsValue({
                strategy: {
                  frequency: "month",
                  time: moment(
                    `${crontab_detail.hour}:${crontab_detail.minute}`,
                    "HH:mm"
                  ),
                  month: crontab_detail.day,
                },
              });
            }

            if (
              crontab_detail?.day == "*" &&
              crontab_detail?.day_of_week == "*"
            ) {
              setFrequency("day");
              form.setFieldsValue({
                strategy: {
                  frequency: "day",
                  time: moment(
                    `${crontab_detail.hour}:${crontab_detail.minute}`,
                    "HH:mm"
                  ),
                },
              });
            }
          }

          setBackupIns(backup_setting.backup_instances);
          setIsOpen(backup_setting.is_on);
          setPushIsOpen(backup_setting.send_email);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  // 查询可选备份项目
  const queryCanBackup = () => {
    setLoading(true);
    fetchGet(apiRequest.dataBackup.queryCanBackup, {
      params: {
        env_id: 1,
      },
    })
      .then((res) => {
        handleResponse(res, () => {
          setCanBackupIns(res.data.data);
          // setCanBackupIns(["mysql1", "arangodb1", "a1", "a2"]);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  // 保存备份
  const saveBackup = () => {
    if (canBackupIns.length === 0) {
      message.warning("当前暂无可用的备份实例");
      return;
    }
    if (form.getFieldValue("isOpen") && backupIns.length === 0) {
      message.warning("请选择您定时备份的实例后，再进行保存");
      return;
    }
    setLoading(true);
    let queryData = form.getFieldsValue();
    let timeInfo = form.getFieldValue("strategy");
    if (queryData.strategy) timeInfo = queryData.strategy;
    fetchPost(apiRequest.dataBackup.updateBackupSetting, {
      body: {
        backup_instances: backupIns,
        env_id: 1,
        is_on: queryData.isOpen,
        crontab_detail: {
          hour: timeInfo.time.format("HH:mm").split(":")[0] || "*",
          minute: timeInfo.time.format("HH:mm").split(":")[1] || "*",
          month: "*",
          day_of_week: timeInfo.week || "*",
          day: timeInfo.month || "*",
        },
        retain_path: queryData.retain_path,
        send_email: queryData.pushIsOpen,
        to_users: form.getFieldValue("email"),
        retain_day: form.getFieldValue("retain_day"),
      },
    })
      .then((res) => {
        if (res && res.data) {
          if (res.data.code == 1) {
            message.warning(res.data.message);
          }
          if (res.data.code == 0) {
            message.success("修改备份策略成功");
          }
        }
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    queryCanBackup();
    queryBackupSettingData();
  }, []);

  return (
    <OmpContentWrapper>
      <div className={styles.header}>
        <SaveOutlined style={{ paddingRight: 5 }} />
        备份实例
      </div>
      <Spin spinning={loading}>
        <div
          style={{
            marginLeft: 50,
            marginTop: 30,
            marginBottom: 30,
          }}
        >
          <p>请选择要备份的实例(存储基础元数据信息):</p>

          {canBackupIns.length === 0 ? (
            <span style={{ marginLeft: 30, color: "#a7abb7" }}>
              暂无可选实例
            </span>
          ) : (
            <Checkbox.Group
              value={backupIns}
              onChange={(checkedValues) => {
                setBackupIns(checkedValues);
                if (checkedValues.length === 0) {
                  form.setFieldsValue({
                    isOpen: false,
                  });
                  setIsOpen(false);
                } else {
                  form.setFieldsValue({
                    isOpen: true,
                  });
                  setIsOpen(true);
                }
              }}
              style={{
                marginLeft: 30,
              }}
            >
              {canBackupIns.map((e) => {
                return (
                  <Row>
                    <Checkbox key={e} value={e} style={{ lineHeight: "32px" }}>
                      {e}
                    </Checkbox>
                  </Row>
                );
              })}
            </Checkbox.Group>
          )}
        </div>
      </Spin>

      <div className={styles.header}>
        <SettingOutlined style={{ paddingRight: 5 }} />
        备份策略
      </div>
      <Spin spinning={loading}>
        <Form
          name="pushSetting"
          labelCol={{ span: 3 }}
          wrapperCol={{ span: 8 }}
          style={{ paddingTop: 30 }}
          onFinish={saveBackup}
          form={form}
          initialValues={{
            retain_path: "/data/omp/data/backup/",
            retain_day: -1,
            pushIsOpen: false,
            isOpen: false,
            strategy: {
              frequency: "day",
              time: moment("00:00", "HH:mm"),
              week: "0",
              month: "1",
            },
            email: "",
          }}
        >
          <Form.Item
            label={
              <span>
                <img
                  src={star}
                  style={{ position: "relative", top: -2, left: -3 }}
                />
                备份路径
              </span>
            }
          >
            <Input.Group compact>
              <Form.Item
                name="retain_path"
                noStyle
                rules={[
                  { required: true, message: "请输入备份路径" },
                  {
                    validator: (rule, value, callback) => {
                      if (value) {
                        if (value.match(/^[ ]*$/)) {
                          return Promise.reject("请输入备份路径");
                        }
                        return Promise.resolve("success");
                      } else {
                        return Promise.resolve("success");
                      }
                    },
                  },
                ]}
              >
                <Input
                  placeholder="请输入备份路径"
                  style={{
                    width: 360,
                  }}
                />
              </Form.Item>
              <Form.Item noStyle>
                <Tooltip
                  placement="top"
                  title={"开启定时备份后，会自动备份已勾选的实例"}
                >
                  <InfoCircleOutlined
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

          <Form.Item label="定时备份">
            <Input.Group compact>
              <Form.Item name="isOpen" noStyle valuePropName="checked">
                <Switch
                  onChange={(e) => setIsOpen(e)}
                  style={{ borderRadius: "10px" }}
                />
              </Form.Item>
              <Form.Item noStyle>
                <Tooltip
                  placement="top"
                  title={"开启定时巡检后，将在设定的时间，自动执行巡检任务"}
                >
                  <InfoCircleOutlined
                    name="icon"
                    style={{
                      color: "rgba(0,0,0,.45)",
                      position: "relative",
                      top: 4,
                      left: 15,
                      fontSize: 15,
                    }}
                  />
                </Tooltip>
              </Form.Item>
            </Input.Group>
          </Form.Item>
          {isOpen && (
            <>
              <Form.Item
                label="定时策略"
                style={{
                  height: 32,
                }}
              >
                <Input.Group compact>
                  <Form.Item name={["strategy", "frequency"]} noStyle>
                    <Select
                      style={{
                        width: 100,
                      }}
                      onChange={(e) => {
                        setFrequency(e);
                      }}
                    >
                      <Select.Option value="day" key="day">
                        每天
                      </Select.Option>
                      <Select.Option value="week" key="week">
                        每周
                      </Select.Option>
                      <Select.Option value="month" key="month">
                        每月
                      </Select.Option>
                    </Select>
                  </Form.Item>

                  {frequency == "week" && (
                    <Form.Item
                      name={["strategy", "week"]}
                      style={{ display: "inline-block", marginLeft: "10px" }}
                    >
                      <Select
                        style={{
                          width: 120,
                        }}
                      >
                        {weekData.map((item, idx) => {
                          return (
                            <Select.Option value={`${idx}`} key={item}>
                              {item}
                            </Select.Option>
                          );
                        })}
                      </Select>
                    </Form.Item>
                  )}

                  {frequency == "month" && (
                    <Form.Item
                      name={["strategy", "month"]}
                      style={{ display: "inline-block", marginLeft: "10px" }}
                    >
                      <Select
                        style={{
                          width: 120,
                        }}
                      >
                        {new Array(28).fill(0).map((item, idx) => {
                          return (
                            <Select.Option
                              key={`${idx + 1}`}
                              value={`${idx + 1}`}
                            >
                              {idx + 1}日
                            </Select.Option>
                          );
                        })}
                      </Select>
                    </Form.Item>
                  )}

                  <Form.Item
                    name={["strategy", "time"]}
                    style={{ display: "inline-block", marginLeft: "10px" }}
                  >
                    <TimePicker
                      //defaultValue={moment("00:00", "HH:mm")}
                      format={"HH:mm"}
                      allowClear={false}
                    />
                  </Form.Item>
                </Input.Group>
              </Form.Item>

              <Form.Item label="备份保留" name="retain_day">
                <Select
                  style={{
                    width: 100,
                  }}
                >
                  <Select.Option key={-1} value={-1}>
                    永久保留
                  </Select.Option>
                  <Select.Option key={1} value={1}>
                    1天
                  </Select.Option>
                  <Select.Option key={7} value={7}>
                    7天
                  </Select.Option>
                  <Select.Option key={30} value={30}>
                    30天
                  </Select.Option>
                </Select>
              </Form.Item>
            </>
          )}

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

export default SelfHealingStrategy;
