import { apiRequest } from "@/config/requestApi";
import { fetchGet, fetchPost } from "@/utils/request";
import { handleResponse } from "@/utils/utils";
import {
  Collapse,
  Select,
  Spin,
  InputNumber,
  message,
  Tabs,
  Button,
  Tooltip,
} from "antd";
import * as R from "ramda";
import { useEffect, useState } from "react";
import styles from "./index.module.less";
import {
  PlusCircleTwoTone,
  InfoCircleOutlined,
  MinusCircleTwoTone,
  CaretRightOutlined,
} from "@ant-design/icons";

const { Panel } = Collapse;
const { Option } = Select;
const { TabPane } = Tabs;

// 保存设置按钮
function SaveSettingsButtonGroup({
  saveHandler = () => ({}),
  disabled = false,
  style = {},
  wrapperStyle = {},
  title = "保存",
}) {
  return (
    <div className={styles.saveButtonWrapper} style={wrapperStyle}>
      <Button
        onClick={() => saveHandler()}
        type={"primary"}
        style={{ marginRight: 15, ...style }}
        disabled={disabled}
      >
        {title}
      </Button>
    </div>
  );
}

// InfoTip
function InfoTip({ text }) {
  return (
    <Tooltip title={text}>
      <InfoCircleOutlined
        style={{
          marginLeft: "10px",
          color: "#909090",
          height: "100%",
          display: "inline-flex",
          alignItems: "center",
        }}
      />
    </Tooltip>
  );
}

const defaultData = [
  {
    condition: ">=",
    level: "critical",
    value: 90,
  },
  {
    condition: ">=",
    level: "warning",
    value: 80,
  },
];

// 单行指标项
function TargetItem({ data: { name, info, conditionsArr, handler } }) {
  return (
    <div className={styles.targetItem}>
      <div className={styles.itemTitle}>
        <span>指标项</span>: {name}
        <InfoTip text={info} />
      </div>
      <div className={styles.conditionItemWrapper}>
        {conditionsArr.map((item, idx) => {
          return (
            <div key={idx} className={styles.conditionItem}>
              阈值：
              <Select
                value={item.condition}
                placeholder={"请选择"}
                style={{ width: 110, marginRight: 10 }}
                onChange={(item) => {
                  const foo = R.clone(conditionsArr);
                  foo[idx] = R.assoc("condition", item, foo[idx]);
                  handler(foo);
                }}
              >
                <Option value=">=">{">="}</Option>
              </Select>
              <InputNumber
                style={{ width: 110, marginRight: 20 }}
                placeholder={"例如：80%"}
                min={0}
                max={100}
                value={item.value}
                step={1}
                formatter={(value) => `${value}%`}
                parser={(value) => value.replace("%", "")}
                onChange={(val) => {
                  const foo = R.clone(conditionsArr);
                  foo[idx] = R.assoc("value", val, foo[idx]);
                  handler(foo);
                }}
              />
              级别：
              <Select
                //defaultValue={idx == 0?"critical":"warning"}
                value={item.level}
                placeholder={"请选择"}
                style={{ width: 110, marginRight: 40 }}
                onChange={(item) => {
                  const foo = R.clone(conditionsArr);
                  foo[idx] = R.assoc("level", item, foo[idx]);
                  handler(foo);
                }}
              >
                {conditionsArr.length === 1 ? (
                  <>
                    <Option value="critical">严重</Option>
                    <Option value="warning">警告</Option>
                  </>
                ) : idx === 0 ? (
                  <Option value="critical">严重</Option>
                ) : (
                  <Option value="warning">警告</Option>
                )}
              </Select>
              {conditionsArr.length === 1 && (
                <PlusCircleTwoTone
                  onClick={() => {
                    const foo = R.clone(conditionsArr);
                    const index_type = foo[0].index_type;
                    const old_value = parseInt(foo[0].value);
                    if (foo[0].level === "critical") {
                      foo.push({
                        condition: ">=",
                        level: "warning",
                        value: old_value - 10 > 0 ? old_value - 10 : 0,
                        index_type,
                      });
                    } else {
                      foo.unshift({
                        condition: ">=",
                        level: "critical",
                        value: old_value + 10 > 100 ? 100 : old_value + 10,
                        index_type,
                      });
                    }
                    handler(foo);
                  }}
                  style={{
                    fontSize: 18,
                    marginRight: 20,
                  }}
                />
              )}
              {idx === 1 && (
                <MinusCircleTwoTone
                  onClick={() => {
                    const foo = R.clone(conditionsArr);
                    foo.splice(1, 1);
                    handler(foo);
                  }}
                  style={{ fontSize: 18 }}
                  twoToneColor="#f5222d"
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function RuleCenter() {
  const [cpuUsed, setCpuUsed] = useState([0, 1]);
  const [memoryUsed, setMemoryUsed] = useState([0, 1]);
  const [diskRootUsed, setDiskRootUsed] = useState([0, 1]);
  const [diskDataUsed, setDiskDataUsed] = useState([0, 1]);
  const [serviceActive, setServiceActive] = useState([0, 1]);
  const [serviceCpuUsed, setServiceCpuUsed] = useState([0, 1]);
  const [serviceMemoryUsed, setServiceMemoryUsed] = useState([0, 1]);

  const [kafkaData, setKafkaData] = useState([
    {
      index_type: "kafka_consumergroup_lag",
      condition: ">=",
      value: 5000,
      level: "critical",
    },
    {
      index_type: "kafka_consumergroup_lag",
      condition: ">=",
      value: 3000,
      level: "warning",
    },
  ]);

  const machineTargetsMap = [
    {
      name: "cpu_used",
      info: `主机当前“CPU”使用率`,
      conditionsArr: cpuUsed,
      handler: (val) => setCpuUsed(val),
    },
    {
      name: "memory_used",
      info: `主机当前“内存”使用率`,
      conditionsArr: memoryUsed,
      handler: (val) => setMemoryUsed(val),
    },
    {
      name: "disk_root_used",
      info: `主机当前“根分区”使用率`,
      conditionsArr: diskRootUsed,
      handler: (val) => setDiskRootUsed(val),
    },
    {
      name: "disk_data_used",
      info: `主机当前“数据分区”使用率`,
      conditionsArr: diskDataUsed,
      handler: (val) => setDiskDataUsed(val),
    },
  ];

  const serviceTargetsMap = [
    {
      name: "service_active",
      info: `服务当前“是否存活”，验证标准是端口是否可以连通`,
      conditionsArr: serviceActive,
      handler: (val) => setServiceActive(val),
    },
    {
      name: "service_cup_used",
      info: `服务当前“CPU”使用率`,
      conditionsArr: serviceCpuUsed,
      handler: (val) => setServiceCpuUsed(val),
    },
    {
      name: "service_memory_used",
      info: `服务当前“内存”使用率`,
      conditionsArr: serviceMemoryUsed,
      handler: (val) => setServiceMemoryUsed(val),
    },
  ];

  const [isMachineLoading, setMachineLoading] = useState(false);
  const [isServiceLoading, setServiceLoading] = useState(false);
  const [isCustomizationLoading, setCustomizationLoading] = useState(false);

  function fetchHostDate() {
    setMachineLoading(true);
    fetchGet(apiRequest.ruleCenter.hostThreshold, {
      params: {
        env_id: 1,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          const {
            data: { cpu_used, memory_used, disk_root_used, disk_data_used },
          } = res.dat;
          setCpuUsed(cpu_used.length > 0 ? cpu_used : defaultData);
          setMemoryUsed(memory_used.length > 0 ? memory_used : defaultData);
          setDiskRootUsed(
            disk_root_used.length > 0 ? disk_root_used : defaultData
          );
          setDiskDataUsed(
            disk_data_used.length > 0 ? disk_data_used : defaultData
          );
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setMachineLoading(false);
      });
  }

  function fetchServiceDate() {
    setServiceLoading(true);
    fetchGet(apiRequest.ruleCenter.serviceThreshold, {
      params: {
        env_id: 1,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          const {
            data: { service_active, service_cpu_used, service_memory_used },
          } = res.data;
          setServiceActive(
            service_active.length > 0
              ? service_active
              : [
                  {
                    index_type: "service_active",
                    condition: "==",
                    value: "False",
                    level: "critical",
                  },
                ]
          );
          setServiceCpuUsed(
            service_cpu_used.length > 0 ? service_cpu_used : defaultData
          );
          setServiceMemoryUsed(
            service_memory_used.length > 0 ? service_memory_used : defaultData
          );
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setServiceLoading(false);
      });
  }

  function fetchCustomDate() {
    setCustomizationLoading(true);
    fetchGet(apiRequest.ruleCenter.queryCustomThreshold, {
      params: {
        env_id: 1,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.code === 0 && Object.keys(res.data).length !== 0) {
            setKafkaData(
              res.data?.kafka?.kafka_consumergroup_lag?.map((item) => {
                // 把其中的value改成number
                return { ...item, value: Number(item.value) };
              })
            );
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setServiceLoading(false);
      });
  }

  function fetchData() {
    setMachineLoading(true);
    setServiceLoading(true);
    setCustomizationLoading(true);
    Promise.all([
      fetchGet(apiRequest.ruleCenter.hostThreshold, {
        params: {
          env_id: 1,
        },
      }),
      fetchGet(apiRequest.ruleCenter.serviceThreshold, {
        params: {
          env_id: 1,
        },
      }),
      fetchGet(apiRequest.ruleCenter.queryCustomThreshold, {
        params: {
          env_id: 1,
        },
      }),
    ])
      .then(([hostResponse, serviceResponse, customThresholdRes]) => {
        hostResponse = hostResponse.data;
        serviceResponse = serviceResponse.data;
        customThresholdRes = customThresholdRes.data;
        if (hostResponse.code === 3) {
          message.warn("登录已过期，请重新登录");

          localStorage.clear();
          window.__history__.replace("/login");
          return;
        }
        const {
          data: { cpu_used, memory_used, disk_root_used, disk_data_used },
        } = hostResponse;
        const {
          data: { service_active, service_cpu_used, service_memory_used },
        } = serviceResponse;
        setCpuUsed(cpu_used.length > 0 ? cpu_used : defaultData);
        setMemoryUsed(memory_used.length > 0 ? memory_used : defaultData);
        setDiskRootUsed(
          disk_root_used.length > 0 ? disk_root_used : defaultData
        );
        setDiskDataUsed(
          disk_data_used.length > 0 ? disk_data_used : defaultData
        );
        setServiceActive(
          service_active.length > 0
            ? service_active
            : [
                {
                  index_type: "service_active",
                  condition: "==",
                  value: "False",
                  level: "critical",
                },
              ]
        );
        setServiceCpuUsed(
          service_cpu_used.length > 0 ? service_cpu_used : defaultData
        );
        setServiceMemoryUsed(
          service_memory_used.length > 0 ? service_memory_used : defaultData
        );
        if (
          customThresholdRes.code === 0 &&
          Object.keys(customThresholdRes.data).length !== 0
        ) {
          setKafkaData(
            customThresholdRes.data?.kafka?.kafka_consumergroup_lag?.map(
              (item) => {
                // 把其中的value改成number
                return { ...item, value: Number(item.value) };
              }
            )
          );
        }
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setMachineLoading(false);
        setServiceLoading(false);
        setCustomizationLoading(false);
      });
  }

  useEffect(() => {
    fetchData();
  }, []);

  function isThresholdAccurate(data) {
    console.log(data);
    const invalidData = R.filter((item) => {
      const critical = R.find(R.propEq("level", "critical"), item) || {};
      const warning = R.find(R.propEq("level", "warning"), item) || {};
      return Number(critical.value) <= Number(warning.value);
    }, data);

    //判断其中同一条指标项的程度不能重复
    for (let item of Object.values(data)) {
      if (item.length == 2 && item[0].level == item[1].level) {
        message.warn(
          `请检查${item[0].index_type}的阈值触发规则，不能设置相同级别`
        );
        return;
      }
    }

    //判断级别不能相等
    const checkDataAgain = (data) => {
      let arr = Object.values(data).filter((item) => item.length == 2);
      let result = arr.filter((item) => item[0].level == item[1].level);
      return result;
    };

    if (!R.isEmpty(invalidData)) {
      const type = R.values(invalidData)[0][0].index_type;
      message.warn(`请检查${type}的阈值触发规则，严重应该大于警告`);
      return;
    } else {
      if (checkDataAgain(data).length !== 0) {
        const type = checkDataAgain(data)[0][0].index_type;
        message.warn(`请检查${type}的阈值触发规则，严重应该大于警告`);
        return;
      }
      return true;
    }
  }

  const checkKafkaData = (data) => {
    if (data.length == 1) return;
    if (data[0].level == data[1].level)
      return "请检查kafka_consumergroup_lag的阈值触发规则，不能设置相同级别";
    let [criticalItem] = data.filter((item) => item.level === "critical");
    let [warningItem] = data.filter((item) => item.level === "warning");
    if (criticalItem.value <= warningItem.value)
      return "请检查kafka_consumergroup_lag的阈值触发规则，严重应该大于警告";
  };

  return (
    <div>
      <Collapse
        bordered={false}
        defaultActiveKey={["machine", "service", "customization"]}
        style={{ marginTop: 10 }}
        expandIcon={({ isActive }) => (
          <CaretRightOutlined rotate={isActive ? 90 : 0} />
        )}
      >
        <Panel header="主机指标" key="machine" className={styles.panelItem}>
          <Spin key={"machine"} spinning={isMachineLoading}>
            <div className={styles.targetItemWrapper}>
              {machineTargetsMap.map((item, idx) => {
                return (
                  <TargetItem
                    handler={(val) => item.handler(val)}
                    key={`machine-${idx}`}
                    data={item}
                  />
                );
              })}
            </div>
            <SaveSettingsButtonGroup
              saveHandler={() => {
                const update_data = {
                  cpu_used: cpuUsed,
                  memory_used: memoryUsed,
                  disk_root_used: diskRootUsed,
                  disk_data_used: diskDataUsed,
                };
                // 如果核验数据未通过，直接退出
                if (isThresholdAccurate(update_data)) {
                  setMachineLoading(true);
                  fetchPost(apiRequest.ruleCenter.hostThreshold, {
                    body: {
                      update_data: update_data,
                      env_id: 1,
                    },
                  })
                    .then((res) => {
                      handleResponse(res, (res) => {
                        if (res.code == 0) {
                          message.success("更新主机指标成功");
                          fetchHostDate();
                        }
                      });
                    })
                    .catch((e) => console.log(e))
                    .finally(() => {
                      setMachineLoading(false);
                    });
                }
              }}
            />
          </Spin>
        </Panel>

        <Panel header="服务指标" key="service" className={styles.panelItem}>
          <Spin key={"service"} spinning={isServiceLoading}>
            <div className={styles.targetItemWrapper}>
              {serviceTargetsMap.map((item, idx) => {
                if (item.name === "service_active") {
                  //服务状态单独展示
                  const { name, info, conditionsArr, handler } = item;
                  return (
                    <div key={"service_active"} className={styles.targetItem}>
                      <div className={styles.itemTitle}>
                        <span>指标项</span>: {name}
                        <InfoTip text={info} />
                      </div>
                      <div
                        style={{ display: "inline-flex", flexFlow: "row wrap" }}
                      >
                        <div key={idx} className={styles.conditionItem}>
                          服务：
                          <Select
                            value={conditionsArr[0].condition}
                            placeholder={"请选择"}
                            style={{ width: 110, marginRight: 10 }}
                            onChange={(item) => {
                              const _clonedArr = R.clone(conditionsArr);
                              _clonedArr[idx] = R.assoc(
                                "condition",
                                item,
                                _clonedArr[idx]
                              );
                              handler(_clonedArr);
                            }}
                          >
                            <Option value="==">{"=="}</Option>
                          </Select>
                          <Select
                            value={conditionsArr[0].value}
                            placeholder={"请选择"}
                            style={{ width: 110, marginRight: 20 }}
                            onChange={(val) => {
                              const foo = R.clone(conditionsArr);
                              foo[idx] = R.assoc("value", val, foo[idx]);
                              handler(foo);
                            }}
                          >
                            <Option value="False">未存活</Option>
                          </Select>
                          级别：
                          <Select
                            value={conditionsArr[0].level}
                            placeholder={"请选择"}
                            style={{ width: 110, marginRight: 40 }}
                            onChange={(item) => {
                              const foo = R.clone(conditionsArr);
                              foo[idx] = R.assoc("level", item, foo[idx]);
                              handler(foo);
                            }}
                          >
                            <Option value="critical">严重</Option>
                          </Select>
                        </div>
                      </div>
                    </div>
                  );
                } else {
                  return (
                    <TargetItem
                      key={item.name}
                      handler={(val) => item.handler(val)}
                      data={item}
                    />
                  );
                }
              })}
            </div>
            <SaveSettingsButtonGroup
              saveHandler={() => {
                const update_data = {
                  service_active: serviceActive,
                  service_cpu_used: serviceCpuUsed,
                  service_memory_used: serviceMemoryUsed,
                };

                // 不检查service_active，因为只有一项
                if (
                  isThresholdAccurate({
                    service_cpu_used: serviceCpuUsed,
                    service_memory_used: serviceMemoryUsed,
                  })
                ) {
                  setServiceLoading(true);
                  fetchPost(apiRequest.ruleCenter.serviceThreshold, {
                    body: {
                      update_data: update_data,
                      env_id: 1,
                    },
                  })
                    .then((res) => {
                      handleResponse(res, (res) => {
                        if (res.code == 0) {
                          message.success("更新服务指标成功");
                          fetchServiceDate();
                        }
                      });
                    })
                    .catch((e) => console.log(e))
                    .finally(() => {
                      setServiceLoading(false);
                    });
                }
              }}
            />
          </Spin>
        </Panel>
        {/* 定制化指标 */}

        <Panel
          header="定制化指标"
          key="customization"
          className={styles.panelItem}
        >
          <Spin key={"customization"} spinning={isCustomizationLoading}>
            <div className={styles.targetItemWrapper}>
              <Tabs tabPosition="left" type="card" style={{ marginTop: 10 }}>
                <TabPane tab="kafka" key="1">
                  <div
                    className={styles.targetItem}
                    style={{ padding: "20px 0px 60px 0px" }}
                  >
                    <div className={styles.itemTitle}>
                      <span>指标项</span>: kafka_consumergroup_lag
                      <InfoTip text="kafka消息队列未消费数据" />
                    </div>
                    <div
                      className={styles.conditionItemWrapper}
                      style={{ paddingLeft: 50 }}
                    >
                      {kafkaData.map((item, idx) => {
                        return (
                          <div key={idx} className={styles.conditionItem}>
                            阈值：
                            <Select
                              value={item.condition}
                              placeholder={"请选择"}
                              style={{ width: 110, marginRight: 10 }}
                              onChange={(item) => {
                                const foo = R.clone(kafkaData);
                                foo[idx].condition = item;
                                setKafkaData(foo);
                              }}
                            >
                              <Option value=">=">{">="}</Option>
                            </Select>
                            <InputNumber
                              style={{ width: 110, marginRight: 20 }}
                              placeholder={"例如：80"}
                              min={0}
                              //max={100}
                              value={item.value}
                              step={1}
                              ///formatter={(value) => `${value}%`}
                              // parser={(value) => value.replace("%", "")}
                              precision={0}
                              onChange={(val) => {
                                const copyData = [...kafkaData];
                                copyData[idx].value = val;
                                setKafkaData(copyData);
                              }}
                            />
                            级别：
                            <Select
                              //defaultValue={idx == 0?"critical":"warning"}
                              value={item.level}
                              placeholder={"请选择"}
                              style={{ width: 110, marginRight: 40 }}
                              onChange={(item) => {
                                const foo = R.clone(kafkaData);
                                foo[idx].level = item;
                                setKafkaData(foo);
                              }}
                            >
                              {kafkaData.length === 1 ? (
                                <>
                                  <Option value="critical">严重</Option>
                                  <Option value="warning">警告</Option>
                                </>
                              ) : idx === 0 ? (
                                <Option value="critical">严重</Option>
                              ) : (
                                <Option value="warning">警告</Option>
                              )}
                            </Select>
                            {kafkaData.length === 1 && (
                              <PlusCircleTwoTone
                                onClick={() => {
                                  const foo = R.clone(kafkaData);
                                  const index_type = foo[0].index_type;
                                  if (foo[0].level == "critical") {
                                    foo.push({
                                      condition: ">=",
                                      level: "warning",
                                      value:
                                        foo[0].value - 1000 > 0
                                          ? foo[0].value - 1000
                                          : 0,
                                      index_type,
                                    });
                                  } else {
                                    foo.unshift({
                                      condition: ">=",
                                      level: "critical",
                                      value: foo[0].value + 1000,
                                      index_type,
                                    });
                                  }
                                  setKafkaData(foo);
                                }}
                                style={{
                                  fontSize: 18,
                                  marginRight: 20,
                                }}
                              />
                            )}
                            {idx === 1 && (
                              <MinusCircleTwoTone
                                onClick={() => {
                                  const foo = R.clone(kafkaData);
                                  foo.splice(1, 1);
                                  setKafkaData(foo);
                                }}
                                style={{ fontSize: 18 }}
                                theme={"twoTone"}
                                twoToneColor="#f5222d"
                              />
                            )}
                          </div>
                        );
                      })}
                      {/* <Button
                        onClick={() => {
                          let checkMessage = checkKafkaData(kafkaData);
                          checkMessage
                            ? message.warn(checkMessage)
                            : console.log("校验通过");
                        }}
                      >
                        保存
                      </Button> */}
                    </div>
                  </div>
                  <SaveSettingsButtonGroup
                    wrapperStyle={{
                      position: "relative",
                      left: -45,
                    }}
                    saveHandler={() => {
                      let checkMessage = checkKafkaData(kafkaData);
                      if (checkMessage) {
                        message.warn(checkMessage);
                      } else {
                        setCustomizationLoading(true);

                        fetchPost(apiRequest.ruleCenter.queryCustomThreshold, {
                          body: {
                            //update_data: update_data,
                            env_id: 1,
                            service_name: "kafka",
                            index_type: "kafka_consumergroup_lag",
                            index_type_info: [...kafkaData],
                          },
                        })
                          .then((res) => {
                            handleResponse(res, (res) => {
                              if (res.code == 0) {
                                message.success("更新定制化指标成功");
                                fetchCustomDate();
                              }
                            });
                          })
                          .catch((e) => console.log(e))
                          .finally(() => {
                            setCustomizationLoading(false);
                          });
                      }
                    }}
                  />
                </TabPane>
              </Tabs>
            </div>
          </Spin>
        </Panel>
      </Collapse>
    </div>
  );
}

export default RuleCenter;
