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
  message
} from "antd";
import { useState, useEffect, useRef } from "react";
import { handleResponse } from "@/utils/utils";
import { fetchGet, fetchDelete, fetchPost, fetchPut } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import styles from "./index.module.less";
import { SettingOutlined, InfoCircleOutlined } from "@ant-design/icons";
import moment from "moment";

const PatrolStrategy = () => {
  const [loading, setLoading] = useState(false);

  const [form] = Form.useForm();

  const [dataSource, setDataSource] = useState({});

  const [isOpen, setIsOpen] = useState(false);
  const [frequency, setFrequency] = useState("day");

  let weekData = [
    "星期一",
    "星期二",
    "星期三",
    "星期四",
    "星期五",
    "星期六",
    "星期日",
  ];

  const queryPatrolStrategyData = () => {
    fetchGet(apiRequest.inspection.queryPatrolStrategy, {
      params: {
        job_type: 0,
      },
    })
      .then((res) => {
        if (res && res.data && res.data.data) {
          setDataSource(res.data.data);
          let data = res.data.data;
          let crontab_detail = data.crontab_detail;
          form.setFieldsValue({
            name: {
              value: data.job_name,
            },
            type: {
              value: data.job_type + "",
            },
            isOpen: {
              value: !Boolean(data.is_start_crontab),
            },
          });

          if (crontab_detail.day_of_week !== "*") {
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

          if (crontab_detail.day !== "*") {
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

          if (crontab_detail.day == "*" && crontab_detail.day_of_week == "*") {
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

          setIsOpen(!Boolean(res.data.data.is_start_crontab));
        }
      })
      .catch((e) => {
        console.log(e);
      })
      .finally();
  };

  // 修改策略的方法，当前无策略时使用post请求，当前有策略时使用put
  const changeStrategy = (data) => {
    //console.log(data, form.getFieldsValue("isOpen"));
    let queryData = form.getFieldsValue();
    //console.log(queryData);
    if (dataSource.job_name) {
      // 本来有任务，使用更新put
      fetchPut(apiRequest.inspection.updatePatrolStrategy, {
        body: {
          job_type: 0,
          job_name: queryData.name.value,
          is_start_crontab: queryData.isOpen.value ? 0 : 1,
          crontab_detail: {
            hour: queryData.strategy.time.format("HH:mm").split(":")[0] || "*",
            minute:
              queryData.strategy.time.format("HH:mm").split(":")[1] || "*",
            month: "*",
            day_of_week: queryData.strategy.week || "*",
            day: queryData.strategy.month || "*",
          },
          env: 1,
        },
      })
        .then((res) => {
          if (res && res.data) {
            if (res.data.code == 1) {
              message.warning(res.data.message);
            }
            if (res.data.code == 0) {
              message.success("更新巡检策略成功");
            }
          }
        })
        .catch((e) => console.log(e))
        .finally(() => {
          setLoading(false);
          queryPatrolStrategyData();
        });
    } else {
      // 无任务使用post
      fetchPost(apiRequest.inspection.createPatrolStrategy, {
        body: {
          job_type: "0",
          job_name: queryData.name.value,
          is_start_crontab: queryData.isOpen.value ? 0 : 1,
          crontab_detail: {
            hour: queryData.strategy.time.format("HH:mm").split(":")[0] || "*",
            minute:
              queryData.strategy.time.format("HH:mm").split(":")[1] || "*",
            month: "*",
            day_of_week: queryData.strategy.week || "*",
            day:  queryData.strategy.month || "*",
          },
          env: 1,
        },
      })
        .then((res) => {
          if (res && res.data) {
            if (res.data.code == 1) {
              message.warning(res.data.message);
            }
            if (res.data.code == 0) {
              message.success("新增巡检策略成功");
            }
          }
        })
        .catch((e) => console.log(e))
        .finally(() => {
          setLoading(false);
          queryPatrolStrategyData();
        });
    }
  };

  useEffect(() => {
    queryPatrolStrategyData();
  }, []);

  return (
    <OmpContentWrapper>
      <div className={styles.header}>
        <SettingOutlined style={{ paddingRight: 5 }} />
        巡检设置
      </div>
      <Spin spinning={loading}>
        <Form
          name="setting"
          labelCol={{ span: 3 }}
          wrapperCol={{ span: 6 }}
          style={{ paddingTop: 40 }}
          onFinish={changeStrategy}
          form={form}
          initialValues={{
            type: {
              value: "0",
            },
            name: {
              value: "深度分析",
            },
            isOpen: {
              value: false,
            },
            strategy: {
              frequency: "day",
              time: moment("00:00", "HH:mm"),
              week: "0",
              month: "1",
            },
          }}
        >
          <Form.Item label="任务类型">
            <Input.Group compact>
              <Form.Item
                name={["type", "value"]}
                noStyle
                rules={[{ required: true, message: "请选择任务类型" }]}
              >
                <Select
                  style={{
                    width: 200,
                  }}
                  placeholder="请选择巡检任务类型"
                >
                  <Select.Option value="0" key="0">
                    深度分析
                  </Select.Option>
                  <Select.Option value="1" key="1">
                    主机巡检
                  </Select.Option>
                  <Select.Option value="2" key="2">
                    组件巡检
                  </Select.Option>
                </Select>
              </Form.Item>
              <Form.Item name={["type", "icon"]} noStyle>
                <Tooltip
                  placement="top"
                  title={"当前版本只支持“深度分析”类型的巡检任务设置"}
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

          <Form.Item label="任务名称">
            <Input.Group compact>
              <Form.Item
                name={["name", "value"]}
                noStyle
                rules={[{ required: true, message: "请输入巡检任务名称" }]}
              >
                <Input
                  placeholder="例如：深度分析"
                  style={{
                    width: 200,
                  }}
                  maxLength={16}
                />
              </Form.Item>
              <Form.Item name={["name", "icon"]} noStyle>
                <Tooltip
                  placement="top"
                  title={
                    "任务名称显示在“报告列表”及“报告内容”中，系统自动补充日期信息"
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

          <Form.Item label="定时巡检">
            <Input.Group compact>
              <Form.Item
                name={["isOpen", "value"]}
                noStyle
                valuePropName="checked"
              >
                <Switch
                  onChange={(e) => setIsOpen(e)}
                  style={{ borderRadius: "10px" }}
                />
              </Form.Item>
              <Form.Item name={["name", "icon"]} noStyle>
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
            <Form.Item label="定时策略">
              <Input.Group compact>
                <Form.Item name={["strategy", "frequency"]} noStyle>
                  <Select
                    style={{
                      width: 80,
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
          )}
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
    </OmpContentWrapper>
  );
};

export default PatrolStrategy;
