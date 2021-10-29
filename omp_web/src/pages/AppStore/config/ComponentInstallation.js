import { useCallback, useEffect, useState, useRef } from "react";
import { useHistory, useLocation } from "react-router-dom";
import { handleResponse } from "@/utils/utils";
import { fetchGet, fetchPost } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { Steps, Form, Input, Button, Select, Checkbox, Tooltip } from "antd";
import {
  LeftOutlined,
  DownOutlined,
  InfoCircleOutlined,
  LoadingOutlined,
} from "@ant-design/icons";
import styles from "./index.module.less";
import RenderComDependence from "./component/RenderComDependence";

const step2Open = (num) => ({
  marginTop: 10,
  minHeight: 30,
  height: num * 60,
  transition: "all .2s ease-in",
  overflow: "hidden",
  backgroundColor: "#f9f9f9",
});

const step2NotOpen = () => ({
  height: 0,
  minHeight: 0,
  transition: "all .2s ease-in",
  overflow: "hidden",
  backgroundColor: "#f9f9f9",
});

const step3Open = () => ({
  marginTop: 10,
  padding: 10,
  minHeight: 30,
  height: 240,
  transition: "all .2s ease-in",
  overflow: "hidden",
  color: "#fff",
  backgroundColor: "#222222",
  wordWrap: "break-word",
  wordBreak: "break-all",
  whiteSpace: "pre-line",
  overflowY: "auto",
  overflowX: "hidden",
});

const step3NotOpen = () => ({
  height: 0,
  minHeight: 0,
  padding: 0,
  transition: "all .2s ease-in",
  overflow: "hidden",
  color: "#fff",
  backgroundColor: "#222222",
  wordWrap: "break-word",
  wordBreak: "break-all",
  whiteSpace: "pre-line",
  overflowY: "auto",
  overflowX: "hidden",
});

const ComponentInstallation = () => {
  const [form] = Form.useForm();

  const history = useHistory();
  let pathArr = history.location.pathname.split("/");
  let name = pathArr[pathArr.length - 1];

  const [loading, setLoading] = useState(false);

  const [dataSource, setDataSource] = useState([]);

  const [stepNum, setStepNum] = useState(0);

  // setp2的查看更多配置是否是展开状态
  const [isOpen, setIsOpen] = useState({
    [name]: false,
  });

  // step3的安装详情是否是展开状态 因为多个所以为对象
  const [isDetailOpen, setIsDetailOpen] = useState({});

  const [versionCurrent, setVersionCurrent] = useState("");

  const [step1Data, setStep1Data] = useState({});

  const [step2Data, setStep2Data] = useState({});

  const [step3Data, setStep3Data] = useState({});

  // 第二步校验通过后，存储数据
  const [vPassedresData, setVPassedresData] = useState({});

  //
  const containerRef = useRef(null);

  const timer = useRef(null);

  function fetchData() {
    setLoading(true);
    fetchGet(apiRequest.appStore.componentEntrance, {
      params: {
        app_name: name,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          //console.log(res.data);
          setDataSource(res.data);
          // 设置版本默认选中第一个
          //console.log(form);
          setVersionCurrent(res.data[0].app_version);
          form.setFieldsValue({ version: res.data[0].app_version });
          form.setFieldsValue({
            clusterMode: JSON.stringify(res.data[0].deploy_mode[0]),
          });
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  }

  let currentAppDependenceData = dataSource.filter(
    (item) => item.app_version == versionCurrent
  )[0];

  const [ipListSource, setIpListSource] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);

  const fetchIPlist = () => {
    setSearchLoading(true);
    fetchGet(apiRequest.machineManagement.ipList)
      .then((res) => {
        handleResponse(res, (res) => {
          setIpListSource(res.data);
          const firstIP = res.data[0].split(".");
          form.setFieldsValue({
            ip: res.data[0],
            instanceName: `${name}-${firstIP[firstIP.length - 2]}-${
              firstIP[firstIP.length - 1]
            }`,
          });

          // jdk 数据默认设置
          currentAppDependenceData?.app_dependence.map((item) => {
            if (item.is_base_env && item.instance_info.length == 0) {
              form.setFieldsValue({
                [`${item.name}|ip`]: res.data[0],
                [`${item.name}|instanceName`]: `${item.name}-${
                  firstIP[firstIP.length - 2]
                }-${firstIP[firstIP.length - 1]}`,
              });
            }
          });
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setSearchLoading(false);
      });
  };

  // 开始安装get
  const queryInstallationInfo = (operateId) => {
    fetchGet(apiRequest.appStore.installHistory, {
      params: {
        operation_uuid: operateId,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          setStep3Data(res.data[0]);
          if (!timer.current) {
            res.data[0].detail_lst.map((item) => {
              setIsDetailOpen({
                ...isDetailOpen,
                [item.ip]: false,
              });
            });
          }
          containerRef.current.scrollTop = containerRef.current.scrollHeight;
          if (
            res.data[0].install_status == 1 ||
            res.data[0].install_status == 0
          ) {
            timer.current = setTimeout(() => {
              queryInstallationInfo(operateId);
            }, 2000);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {});
  };

  useEffect(() => {
    fetchData();
    return () => {
      clearTimeout(timer.current);
    };
  }, []);

  //  0 待安装 1安装中 2 安装成功 3安装失败

  return (
    <div>
      <div
        style={{
          height: 50,
          backgroundColor: "#fff",
          display: "flex",
          paddingLeft: 20,
          paddingRight: 50,
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div style={{ fontSize: 16 }}>
          <LeftOutlined
            style={{ fontSize: 16, marginRight: 20 }}
            className={styles.backIcon}
            onClick={() => {
              history?.push({
                pathname: `/application_management/app_store`,
              });
            }}
          />
          {name}
        </div>
        <div style={{ width: 600, position: "relative", left: -60 }}>
          <Steps size="small" current={stepNum}>
            <Steps.Step title="基本信息" />
            <Steps.Step title="部署信息" />
            <Steps.Step title="开始安装" />
          </Steps>
        </div>
        <div />
      </div>

      {/* 第一步 */}
      {stepNum == 0 && (
        <>
          <div
            style={{
              marginTop: 20,
              backgroundColor: "#fff",
              padding: 10,
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                width: "100%",
                position: "relative",
                height: 30,
              }}
            >
              <div
                style={{
                  fontWeight: 500,
                  position: "absolute",
                  left: 30,
                  backgroundColor: "#fff",
                  paddingLeft: 20,
                  paddingRight: 20,
                }}
              >
                基本信息
              </div>
              <div
                style={{ height: 1, backgroundColor: "#b3b2b3", width: "100%" }}
              />
            </div>
            <div style={{ paddingLeft: 20, marginTop: 10, paddingBottom: 40 }}>
              <Form form={form} layout="inline" name="basic">
                <Form.Item label="选择版本" name="version">
                  <Select
                    style={{ width: 200 }}
                    onChange={(e) => {
                      setVersionCurrent(e);
                    }}
                  >
                    {dataSource?.map((item) => (
                      <Select.Option
                        key={item.app_version}
                        value={item.app_version}
                      >
                        {item.app_version}
                      </Select.Option>
                    ))}
                  </Select>
                </Form.Item>
                <Form.Item
                  label="集群模式"
                  name="clusterMode"
                  style={{ marginLeft: 30 }}
                >
                  <Select style={{ width: 200 }}>
                    {currentAppDependenceData?.deploy_mode?.map((item) => {
                      return (
                        <Select.Option
                          key={JSON.stringify(item)}
                          value={JSON.stringify(item)}
                        >
                          {item.name}
                        </Select.Option>
                      );
                    })}
                  </Select>
                </Form.Item>
              </Form>
            </div>
          </div>

          <div
            style={{
              marginTop: 20,
              backgroundColor: "#fff",
              padding: 10,
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                width: "100%",
                position: "relative",
                height: 30,
              }}
            >
              <div
                style={{
                  fontWeight: 500,
                  position: "absolute",
                  left: 30,
                  backgroundColor: "#fff",
                  paddingLeft: 20,
                  paddingRight: 20,
                }}
              >
                依赖信息
              </div>
              <div
                style={{ height: 1, backgroundColor: "#b3b2b3", width: "100%" }}
              />
            </div>
            <div
              style={{
                paddingLeft: 20,
                marginTop: 10,
                paddingBottom: 40,
                paddingTop: 10,
              }}
            >
              {currentAppDependenceData &&
              currentAppDependenceData.app_dependence &&
              currentAppDependenceData.app_dependence.length == 0 ? (
                <div>无</div>
              ) : (
                currentAppDependenceData?.app_dependence?.map((item) => (
                  <RenderComDependence
                    key={item.name}
                    data={item}
                    form={form}
                  />
                ))
              )}
            </div>
          </div>

          <div
            style={{
              marginTop: 20,
              backgroundColor: "#fff",
              padding: 25,
              display: "flex",
              justifyContent: "space-between",
              paddingRight: 80,
            }}
          >
            <div />
            <Button
              type="primary"
              onClick={() => {
                currentAppDependenceData?.app_install_args?.map((item) => {
                  form.setFieldsValue({
                    [`install|${JSON.stringify({
                      name: item.name,
                      key: item.key,
                      dir_key: item.dir_key,
                    })}`]: item.default,
                  });
                });
                currentAppDependenceData?.app_port?.map((item) => {
                  console.log(item.default,item)
                  form.setFieldsValue({
                    [`port|${JSON.stringify({
                      name: item.name,
                      key: item.key,
                      dir_key: item.dir_key,
                    })}`]: item.default,
                  });
                });

                // jdk 初始值添加
                currentAppDependenceData?.app_dependence.map((item) => {
                  if (item.is_base_env && item.instance_info.length == 0) {
                    item?.app_install_args.map((i) => {
                      setIsOpen({
                        ...isOpen,
                        [i.name]: false,
                      });
                      form.setFieldsValue({
                        [`install|${JSON.stringify({
                          name: i.name,
                          key: i.key,
                          dir_key: i.dir_key,
                        })}`]: i.default,
                      });
                    });
                  }
                });
                currentAppDependenceData?.app_port.map((item) => {
                  if (item.is_base_env && item.instance_info.length == 0) {
                    item?.app_port.map((i) => {
                      setIsOpen({
                        ...isOpen,
                        [i.name]: false,
                      });
                      form.setFieldsValue({
                        [`port|${JSON.stringify({
                          name: i.name,
                          key: i.key,
                          dir_key: i.dir_key,
                        })}`]: i.default,
                      });
                    });
                  }
                });

                setStep1Data(form.getFieldsValue());
                console.log(form.getFieldsValue());

                fetchIPlist();
                setStepNum(1);
              }}
            >
              下一步
            </Button>
          </div>
        </>
      )}
      {/* 第二步 */}
      {stepNum == 1 && (
        <>
          <div
            style={{
              marginTop: 20,
              backgroundColor: "#fff",
              padding: 10,
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                width: "100%",
                position: "relative",
                height: 30,
              }}
            >
              <div
                style={{
                  fontWeight: 500,
                  position: "absolute",
                  left: 30,
                  backgroundColor: "#fff",
                  paddingLeft: 20,
                  paddingRight: 20,
                }}
              >
                {name}
              </div>
              <div
                style={{ height: 1, backgroundColor: "#b3b2b3", width: "100%" }}
              />
            </div>
            <div style={{ paddingLeft: 20, marginTop: 10, paddingBottom: 40 }}>
              <Form
                form={form}
                layout="inline"
                name="basic"
                // initialValues={{
                //   clusterMode: "singleInstance",
                // }}
              >
                <Form.Item label="选择主机" name="ip">
                  <Select
                    style={{ width: 200 }}
                    onChange={(e) => {
                      const IpArr = e.split(".");
                      form.setFieldsValue({
                        instanceName: `${name}-${IpArr[IpArr.length - 2]}-${
                          IpArr[IpArr.length - 1]
                        }`,
                      });
                    }}
                  >
                    {ipListSource?.map((item) => (
                      <Select.Option key={item} value={item}>
                        {item}
                      </Select.Option>
                    ))}
                  </Select>
                </Form.Item>
                <Form.Item
                  label="实例名称"
                  name="instanceName"
                  style={{ marginLeft: 30 }}
                  rules={[
                    {
                      required: true,
                      message: "请填写实例名称",
                    },
                  ]}
                >
                  <Input />
                </Form.Item>

                <a
                  style={{
                    fontSize: 13,
                    display: "flex",
                    alignItems: "center",
                    flexDirection: "row-reverse",
                    paddingLeft: 200,
                  }}
                  onClick={() => {
                    setIsOpen({
                      ...isOpen,
                      [name]: !isOpen[name],
                    });
                    // setIsDetailOpen({
                    //   ...isDetailOpen,
                    //   [item.ip]: !isDetailOpen[item.ip],
                    // });
                  }}
                >
                  <DownOutlined
                    style={{
                      transform: `rotate(${isOpen[name] ? 180 : 0}deg)`,
                      position: "relative",
                      top: isOpen[name] ? -1 : 1,
                      left: 3,
                    }}
                  />
                  查看更多配置
                </a>
              </Form>
              <div
                //className={styles.backIcon}
                style={
                  isOpen[name]
                    ? step2Open(
                        currentAppDependenceData.app_install_args.length +
                          currentAppDependenceData.app_port.length
                      )
                    : step2NotOpen()
                }
              >
                <Form
                  form={form}
                  //layout="inline"
                  name="basic"
                  style={{
                    marginTop: 20,
                  }}
                >
                  {currentAppDependenceData?.app_install_args?.map((item) => {
                    return (
                      <Form.Item
                        key={item.key}
                        style={{ paddingLeft: 15 }}
                        label={<span style={{ width: 60 }}>{item.name}</span>}
                        name={`install|${JSON.stringify({
                          name: item.name,
                          key: item.key,
                          dir_key: item.dir_key,
                        })}`}
                        rules={[
                          {
                            required: true,
                            message: `请填写${item.name}`,
                          },
                        ]}
                      >
                        <Input
                          addonBefore={item.dir_key ? "/ 数据分区" : null}
                          style={{ width: 420 }}
                          suffix={
                            item.dir_key ? (
                              <Tooltip title="数据分区：主机所设置的数据分区">
                                <InfoCircleOutlined
                                  style={{ color: "rgba(0,0,0,.45)" }}
                                />
                              </Tooltip>
                            ) : null
                          }
                        />
                      </Form.Item>
                    );
                  })}
                  {currentAppDependenceData?.app_port?.map((item) => {
                    return (
                      <Form.Item
                        key={item.key}
                        style={{ paddingLeft: 15 }}
                        label={<span style={{ width: 60 }}>{item.name}</span>}
                        name={`port|${JSON.stringify({
                          name: item.name,
                          key: item.key,
                          dir_key: item.dir_key,
                        })}`}
                        rules={[
                          {
                            required: true,
                            message: `请填写${item.name}`,
                          },
                        ]}
                      >
                        <Input
                          addonBefore={item.dir_key ? "/ 数据分区" : null}
                          style={{ width: 420 }}
                          suffix={
                            item.dir_key ? (
                              <Tooltip title="数据分区：主机所设置的数据分区">
                                <InfoCircleOutlined
                                  style={{ color: "rgba(0,0,0,.45)" }}
                                />
                              </Tooltip>
                            ) : null
                          }
                        />
                      </Form.Item>
                    );
                  })}
                </Form>
              </div>
            </div>
          </div>
          {/* 渲染jdk */}
          {currentAppDependenceData?.app_dependence.map((item) => {
            if (item.is_base_env && item.instance_info.length == 0) {
              return (
                <div
                  key={item.name}
                  style={{
                    marginTop: 20,
                    backgroundColor: "#fff",
                    padding: 10,
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      width: "100%",
                      position: "relative",
                      height: 30,
                    }}
                  >
                    <div
                      style={{
                        fontWeight: 500,
                        position: "absolute",
                        left: 30,
                        backgroundColor: "#fff",
                        paddingLeft: 20,
                        paddingRight: 20,
                      }}
                    >
                      {item.name}
                    </div>
                    <div
                      style={{
                        height: 1,
                        backgroundColor: "#b3b2b3",
                        width: "100%",
                      }}
                    />
                  </div>
                  <div
                    style={{
                      paddingLeft: 20,
                      marginTop: 10,
                      paddingBottom: 40,
                    }}
                  >
                    <Form
                      form={form}
                      layout="inline"
                      name="basic"
                      // initialValues={{
                      //   clusterMode: "singleInstance",
                      // }}
                    >
                      <Form.Item label="选择主机" name={`${item.name}|ip`}>
                        <Select
                          style={{ width: 200 }}
                          onChange={(e) => {
                            const IpArr = e.split(".");
                            form.setFieldsValue({
                              [`${item.name}|instanceName`]: `${item.name}-${
                                IpArr[IpArr.length - 2]
                              }-${IpArr[IpArr.length - 1]}`,
                            });
                          }}
                        >
                          {ipListSource?.map((item) => (
                            <Select.Option key={item} value={item}>
                              {item}
                            </Select.Option>
                          ))}
                        </Select>
                      </Form.Item>
                      <Form.Item
                        label="实例名称"
                        name={`${item.name}|instanceName`}
                        style={{ marginLeft: 30 }}
                        rules={[
                          {
                            required: true,
                            message: "请填写实例名称",
                          },
                        ]}
                      >
                        <Input />
                      </Form.Item>

                      <a
                        style={{
                          fontSize: 13,
                          display: "flex",
                          alignItems: "center",
                          flexDirection: "row-reverse",
                          paddingLeft: 200,
                        }}
                        onClick={() => {
                          setIsOpen({
                            ...isOpen,
                            [item.name]: !isOpen[item.name],
                          });
                        }}
                      >
                        <DownOutlined
                          style={{
                            transform: `rotate(${
                              isOpen[item.name] ? 180 : 0
                            }deg)`,
                            position: "relative",
                            top: isOpen[item.name] ? -1 : 1,
                            left: 3,
                          }}
                        />
                        查看更多配置
                      </a>
                    </Form>
                    <div
                      //className={styles.backIcon}
                      style={
                        isOpen[item.name]
                          ? step2Open(
                              item.app_install_args.length +
                                item.app_port.length
                            )
                          : step2NotOpen()
                      }
                    >
                      <Form
                        form={form}
                        //layout="inline"
                        name="basic"
                        style={{
                          marginTop: 20,
                        }}
                      >
                        {item?.app_install_args?.map((i) => {
                          return (
                            <Form.Item
                              key={i.key}
                              style={{ paddingLeft: 15 }}
                              label={
                                <span style={{ width: 60 }}>{i.name}</span>
                              }
                              name={`install|${JSON.stringify({
                                name: i.name,
                                key: i.key,
                                dir_key: i.dir_key,
                              })}`}
                              rules={[
                                {
                                  required: true,
                                  message: `请填写${i.name}`,
                                },
                              ]}
                            >
                              <Input
                                addonBefore={i.dir_key ? "/ 数据分区" : null}
                                style={{ width: 420 }}
                                suffix={
                                  i.dir_key ? (
                                    <Tooltip title="数据分区：主机所设置的数据分区">
                                      <InfoCircleOutlined
                                        style={{ color: "rgba(0,0,0,.45)" }}
                                      />
                                    </Tooltip>
                                  ) : null
                                }
                              />
                            </Form.Item>
                          );
                        })}
                        {item?.app_port?.map((i) => {
                          return (
                            <Form.Item
                              key={i.key}
                              style={{ paddingLeft: 15 }}
                              label={
                                <span style={{ width: 60 }}>{i.name}</span>
                              }
                              name={`port|${JSON.stringify({
                                name: i.name,
                                key: i.key,
                                dir_key: i.dir_key,
                              })}`}
                              rules={[
                                {
                                  required: true,
                                  message: `请填写${i.name}`,
                                },
                              ]}
                            >
                              <Input
                                addonBefore={i.dir_key ? "/ 数据分区" : null}
                                style={{ width: 420 }}
                                suffix={
                                  i.dir_key ? (
                                    <Tooltip title="数据分区：主机所设置的数据分区">
                                      <InfoCircleOutlined
                                        style={{ color: "rgba(0,0,0,.45)" }}
                                      />
                                    </Tooltip>
                                  ) : null
                                }
                              />
                            </Form.Item>
                          );
                        })}
                      </Form>
                    </div>
                  </div>
                </div>
              );
            }
          })}

          <div
            style={{
              marginTop: 20,
              backgroundColor: "#fff",
              padding: 25,
              display: "flex",
              justifyContent: "space-between",
              paddingRight: 40,
            }}
          >
            <div style={{ display: "flex", alignItems: "center" }}>
              分布主机数量: 1台
            </div>
            <div>
              <Button
                style={{
                  marginRight: 15,
                }}
                type="primary"
                onClick={() => {
                  //console.log(requestData);
                  //console.log(form.getFieldsValue())
                  setStepNum(0);
                }}
              >
                上一步
              </Button>
              <Button
                type="primary"
                loading={loading}
                onClick={() => {
                  setLoading(true);
                  setStep2Data(form.getFieldsValue());
                  let st2 = form.getFieldsValue();
                  console.log(step1Data, form.getFieldsValue());
                  //setStepNum(2);
                  console.log(dataSource);
                  //if(currentAppDependenceData.)
                  // if( {currentAppDependenceData?.app_dependence.map((item) => {
                  //   if (item.is_base_env && item.instance_info.length == 0) {

                  //   }})
                  let use_exist_services =
                    currentAppDependenceData.app_dependence.length == 0
                      ? []
                      : [{ zxc: 123 }];

                  // key == install port
                  let parameterCreate = (step2Data, type) => {
                    let Obj = {};
                    Object.keys(step2Data).map((key) => {
                      console.log(key);
                      if (key.split("|")[0] == type) {
                        let data = JSON.parse(key.split("|")[1]);
                        Obj = {
                          ...data,
                          default: step2Data[key],
                        };
                      }
                    });
                    if (Object.keys(Obj).length !== 0) {
                      console.log(Obj);
                      return Obj;
                    }
                  };

                  // let use_exist_services_Arr = [];
                  // let install_services_Arr = [];
                  // currentAppDependenceData?.app_dependence.map((item) => {
                  //   if (item.is_base_env && item.instance_info.length == 0) {
                  //       // 这里是填写的数据
                  //   }else{
                  //     use_exist_services_Arr.push(item)
                  //   }
                  // });

                  let data = {
                    install_type: 0,
                    use_exist_services: [],
                    install_services: [
                      {
                        name: name,
                        version: versionCurrent,
                        ip: st2.ip,
                        app_install_args:
                          [parameterCreate(st2, "install")] || [],
                        app_port: [parameterCreate(st2, "port")] || [],
                        service_instance_name: st2.instanceName,
                        deploy_mode: JSON.parse(step1Data.clusterMode),
                      },
                    ],
                  };

                  fetchPost(apiRequest.appStore.executeInstall, {
                    body: {
                      ...data,
                    },
                  })
                    .then((res) => {
                      handleResponse(res, (res) => {
                        if (res.data && res.data.install_services) {
                          if (!res.data.is_valid_flag) {
                            // 打开全部的展开栏
                            let isOpenCopy = JSON.parse(JSON.stringify(isOpen));
                            for (const key in isOpenCopy) {
                              isOpenCopy[key] = true;
                            }
                            setIsOpen({
                              ...isOpenCopy,
                            });
                            if (
                              res.data.install_services[0].check_msg &&
                              res.data.install_services[0].check_msg.includes(
                                "实例名称"
                              )
                            ) {
                              form.setFields([
                                // { name: '表单字段name', value: '需要设置的值', errors: ['错误信息'] }, 当 errors 为非空数组时，表单项呈现红色，
                                {
                                  name: "instanceName",
                                  errors: [
                                    res.data.install_services[0].check_msg,
                                  ],
                                },
                              ]);
                            }

                            res.data.install_services[0].app_port.map((i) => {
                              if (i.check_flag == false) {
                                form.setFields([
                                  {
                                    name: `port|${JSON.stringify({
                                      name: i.name,
                                      key: i.key,
                                      dir_key: i.dir_key,
                                    })}`,
                                    errors: [i.check_msg],
                                  },
                                ]);
                              }
                            });
                            res.data.install_services[0].app_install_args.map(
                              (i) => {
                                if (i.check_flag == false) {
                                  form.setFields([
                                    {
                                      name: `install|${JSON.stringify({
                                        name: i.name,
                                        key: i.key,
                                        dir_key: i.dir_key,
                                      })}`,
                                      errors: [i.check_msg],
                                    },
                                  ]);
                                }
                              }
                            );
                          } else {
                            // 后端校验通过
                            setVPassedresData(res.data);
                            queryInstallationInfo(res.data.operation_uuid);
                            setStepNum(2);
                          }
                        }
                      });
                    })
                    .catch((e) => console.log(e))
                    .finally(() => {
                      setLoading(false);
                    });
                }}
              >
                开始安装
              </Button>
            </div>
          </div>
        </>
      )}
      {stepNum == 2 && (
        <>
          <div
            style={{
              marginTop: 20,
              backgroundColor: "#fff",
              padding: 10,
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                width: "100%",
                position: "relative",
                height: 30,
              }}
            >
              <div
                style={{
                  fontWeight: 500,
                  position: "absolute",
                  left: 30,
                  backgroundColor: "#fff",
                  paddingLeft: 20,
                  paddingRight: 20,
                }}
              >
                {name}
              </div>
              <div
                style={{ height: 1, backgroundColor: "#b3b2b3", width: "100%" }}
              />
            </div>
            {step3Data?.detail_lst?.map((item) => {
              return (
                <div
                  key={item.ip}
                  style={{
                    paddingLeft: 20,
                    marginTop: 10,
                    paddingBottom: 40,
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center" }}>
                    <div
                      style={{
                        width: 592,
                        display: "flex",
                        alignItems: "center",
                      }}
                    >
                      {item.ip}
                    </div>
                    <a
                      style={{
                        fontSize: 13,
                        display: "flex",
                        alignItems: "center",
                        flexDirection: "row-reverse",
                        paddingLeft: 200,
                      }}
                      onClick={() => {
                        setIsDetailOpen({
                          ...isDetailOpen,
                          [item.ip]: !isDetailOpen[item.ip],
                        });
                        //setIsDetailOpen(!isDetailOpen);
                      }}
                    >
                      <DownOutlined
                        style={{
                          transform: `rotate(${
                            isDetailOpen[item.ip] ? 180 : 0
                          }deg)`,
                          position: "relative",
                          top: isDetailOpen[item.ip] ? -1 : 1,
                          left: 3,
                        }}
                      />
                      查看详细安装信息
                    </a>
                  </div>

                  <div
                    //className={styles.backIcon}
                    ref={containerRef}
                    style={
                      isDetailOpen[item.ip] ? step3Open(2) : step3NotOpen()
                    }
                  >
                    {item.log}
                  </div>
                </div>
              );
            })}
          </div>
          <div
            style={{
              marginTop: 20,
              backgroundColor: "#fff",
              padding: 25,
              display: "flex",
              justifyContent: "space-between",
              paddingRight: 80,
            }}
          >
            <div style={{ display: "flex", alignItems: "center" }}>
              {step3Data.install_status_msg}{" "}
              {(step3Data.install_status == 0 ||
                step3Data.install_status == 1) && (
                <LoadingOutlined
                  style={{ fontSize: 20, fontWeight: 600, marginLeft: 10 }}
                />
              )}
            </div>
            <div>
              <Button
                type="primary"
                onClick={() => {
                  history.push("/application_management/service_management");
                }}
              >
                完成
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default ComponentInstallation;
