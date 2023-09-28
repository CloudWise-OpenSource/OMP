import { useEffect, useState, useRef } from "react";
import { useHistory } from "react-router-dom";
import { handleResponse } from "@/utils/utils";
import { fetchGet, fetchPost } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { Steps, Form, Input, Button, Select, Tooltip, message } from "antd";
import {
  LeftOutlined,
  DownOutlined,
  InfoCircleOutlined,
  LoadingOutlined,
} from "@ant-design/icons";
import styles from "./index.module.less";
import RenderComDependence from "./component/RenderComDependence";
import { useDispatch } from "react-redux";
import { getTabKeyChangeAction } from "../store/actionsCreators";

const step2Open = (num) => ({
  marginTop: 10,
  minHeight: 30,
  height: num * 75,
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

const ApplicationInstallation = () => {
  const [form] = Form.useForm();

  const dispatch = useDispatch();

  const [processContinue, setProcessContinue] = useState(true);
  //定义校验弹出msessage函数
  const verificationError = (arr) => {
    // console.log(arr);
    for (const item of arr) {
      if (item.process_continue == false) {
        setProcessContinue(false);
        message.warning(item.process_message);
        return false;
        break;
      }
    }
    setProcessContinue(true);
    return true;
  };

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
    fetchGet(apiRequest.appStore.productEntrance, {
      params: {
        pro_name: name,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          console.log(res.data);
          setDataSource(res.data);

          // 设置版本默认选中第一个
          //console.log(form);
          verificationError(res.data[0]?.pro_services);
          setVersionCurrent(res.data[0]?.pro_version);
          form.setFieldsValue({ version: res.data[0]?.pro_version });
          form.setFieldsValue({
            clusterMode: "single",
          });
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  }

  let currentproDependenceData = dataSource.filter(
    (item) => item.pro_version == versionCurrent
  )[0];

  const [ipListSource, setIpListSource] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);

  const use_exist_servicesRef = useRef([]);
  const install_servicesRef = useRef([]);

  // 定义选中的ip是否包含在instance_info
  const hasSameIp = (item, ip) => {
    return (
      item.is_base_env &&
      item.instance_info &&
      item.instance_info.filter((b) => b.ip == ip)
    );
  };

  const [showJdk, setShowJdk] = useState(false);

  const jdkHandleInitData = (data = [], ip) => {
    console.log("jdk 尝试设置默认值", data);
    //data.map((item) => {
    if (hasSameIp(data, ip).length == 0) {
      console.log("不存在相同");
      setShowJdk(true);
      install_servicesRef.current = [
        {
          ...data,
        },
      ];
      use_exist_servicesRef.current = [];

      data?.app_install_args?.map((i) => {
        setIsOpen({
          ...isOpen,
          [i.name]: false,
        });
        form.setFieldsValue({
          [`install|${data.name}|${JSON.stringify({
            name: i.name,
            key: i.key,
            dir_key: i.dir_key,
          })}`]: i.default,
        });
      });

      data?.app_port?.map((i) => {
        setIsOpen({
          ...isOpen,
          [i.name]: false,
        });
        form.setFieldsValue({
          [`port|${data.name}|${JSON.stringify({
            name: i.name,
            key: i.key,
            //dir_key: i.dir_key,
          })}`]: i.default,
        });
      });

      form.setFieldsValue({
        [`${data.name}|ip`]: ip,
        [`${data.name}|instanceName`]: `${data.name}-${ip[ip.length - 2]}-${
          ip[ip.length - 1]
        }`,
      });
    } else {
      setShowJdk(false);
      //console.log("存在相同");
      let isSame = hasSameIp(data, ip)[0];
      use_exist_servicesRef.current = [isSame];
      install_servicesRef.current = [];
    }
    //});
  };

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
          let firstIp = res.data[0];
          // jdk 数据默认设置
          jdkHandleInitData(
            currentproDependenceData?.dependence_services_info[0],
            firstIp
          );
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
                [item.service_name]: false,
              });
            });
          }

          if (
            res.data[0]?.install_status == 1 ||
            res.data[0]?.install_status == 0
          ) {
            timer.current = setTimeout(() => {
              queryInstallationInfo(operateId);
            }, 2000);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        containerRef.current.scrollTop = containerRef.current.scrollHeight;
      });
  };

  useEffect(() => {
    fetchData();
    return () => {
      clearTimeout(timer.current);
    };
  }, []);

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
              dispatch(getTabKeyChangeAction("service"));
              history?.goBack();
              // history?.push({
              //   pathname: `/application_management/app_store`,
              // });
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
                      verificationError(
                        dataSource.filter((item) => item.pro_version == e)[0]
                          ?.pro_services
                      );
                    }}
                  >
                    {dataSource?.map((item) => (
                      <Select.Option
                        key={item.pro_version}
                        value={item.pro_version}
                      >
                        {item.pro_version}
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
                    <Select.Option key={"single"} value={"single"}>
                      单实例
                    </Select.Option>
                    {/* {currentproDependenceData?.deploy_mode?.map((item) => {
                      return (
                        <Select.Option
                          key={JSON.stringify(item)}
                          value={JSON.stringify(item)}
                        >
                          {item.name}
                        </Select.Option>
                      );
                    })} */}
                  </Select>
                </Form.Item>
              </Form>
            </div>
          </div>

          {/* 服务信息 */}
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
                服务信息
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
              {currentproDependenceData &&
              currentproDependenceData.pro_services &&
              currentproDependenceData.pro_services.length == 0 ? (
                <div>无</div>
              ) : (
                currentproDependenceData?.pro_services?.map((item) => {
                  return (
                    <div
                      key={item.name}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        paddingBottom: 20,
                      }}
                    >
                      <span
                        style={{
                          //width: 100,
                          paddingRight: 15,
                          textAlign: "right",
                        }}
                      >
                        {item.name}:
                      </span>
                      <Select
                        style={{ width: 240 }}
                        defaultValue={item.version}
                        // onSelect={(e) => {
                        // setDeploy_mode(e);
                        // }}
                      >
                        <Select.Option value={item.version} key={item.version}>
                          {item.version}
                        </Select.Option>
                      </Select>
                    </div>
                  );
                })
              )}
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
              {currentproDependenceData &&
              currentproDependenceData.dependence_services_info &&
              currentproDependenceData.dependence_services_info.length == 0 ? (
                <div>无</div>
              ) : (
                currentproDependenceData?.dependence_services_info?.map(
                  (item) => (
                    <RenderComDependence
                      key={item.name}
                      data={item}
                      form={form}
                    />
                  )
                )
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
              disabled={!processContinue}
              type="primary"
              onClick={() => {
                currentproDependenceData?.pro_services[0].app_install_args?.map(
                  (item) => {
                    form.setFieldsValue({
                      [`install|${
                        currentproDependenceData?.pro_services[0]?.name
                      }|${JSON.stringify({
                        name: item.name,
                        key: item.key,
                        dir_key: item.dir_key,
                      })}`]: item.default,
                    });
                  }
                );
                currentproDependenceData?.pro_services[0].app_port?.map(
                  (item) => {
                    //console.log(item.default, item);
                    form.setFieldsValue({
                      [`port|${
                        currentproDependenceData?.pro_services[0]?.name
                      }|${JSON.stringify({
                        name: item.name,
                        key: item.key,
                        //dir_key: item.dir_key,
                      })}`]: item.default,
                    });
                  }
                );

                setStep1Data(form.getFieldsValue());

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
          {/* 不遍历了，直接用第一项 */}
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
                {currentproDependenceData?.pro_services[0]?.name}
              </div>
              <div
                style={{ height: 1, backgroundColor: "#b3b2b3", width: "100%" }}
              />
            </div>
            <div style={{ paddingLeft: 20, marginTop: 10, paddingBottom: 40 }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
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
                        jdkHandleInitData(
                          currentproDependenceData?.dependence_services_info[0],
                          e
                        );
                        form.setFieldsValue({
                          instanceName: `${
                            currentproDependenceData?.pro_services[0]?.name
                          }-${IpArr[IpArr.length - 2]}-${
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
                </Form>
                <a
                  style={{
                    fontSize: 13,
                    display: "flex",
                    alignItems: "center",
                    flexDirection: "row-reverse",
                    paddingRight: 100,
                  }}
                  onClick={() => {
                    setIsOpen({
                      ...isOpen,
                      [currentproDependenceData?.pro_services[0]?.name]:
                        !isOpen[
                          currentproDependenceData?.pro_services[0]?.name
                        ],
                    });
                    // setIsDetailOpen({
                    //   ...isDetailOpen,
                    //   [item.ip]: !isDetailOpen[item.ip],
                    // });
                  }}
                >
                  <DownOutlined
                    style={{
                      transform: `rotate(${
                        isOpen[currentproDependenceData?.pro_services[0]?.name]
                          ? 180
                          : 0
                      }deg)`,
                      position: "relative",
                      top: isOpen[name] ? -1 : 1,
                      left: 3,
                    }}
                  />
                  查看更多配置
                </a>
              </div>
              <div
                //className={styles.backIcon}
                style={
                  isOpen[currentproDependenceData?.pro_services[0]?.name]
                    ? step2Open(
                        currentproDependenceData?.pro_services[0]
                          ?.app_install_args?.length +
                          currentproDependenceData?.pro_services[0]?.app_port
                            ?.length
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
                  {currentproDependenceData?.pro_services[0]?.app_install_args?.map(
                    (item) => {
                      return (
                        <Form.Item
                          key={item.key}
                          style={{ paddingLeft: 15, paddingBottom: 15 }}
                          label={<span style={{ width: 60 }}>{item.name}</span>}
                          name={`install|${
                            currentproDependenceData?.pro_services[0]?.name
                          }|${JSON.stringify({
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
                    }
                  )}
                  {currentproDependenceData?.pro_services[0]?.app_port?.map(
                    (item) => {
                      return (
                        <Form.Item
                          key={item.key}
                          style={{ paddingLeft: 15 }}
                          label={<span style={{ width: 60 }}>{item.name}</span>}
                          name={`port|${
                            currentproDependenceData?.pro_services[0]?.name
                          }|${JSON.stringify({
                            name: item.name,
                            key: item.key,
                            //dir_key: item.dir_key,
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
                    }
                  )}
                </Form>
              </div>
            </div>
          </div>

          {/* 展示jdk */}
          {showJdk ? (
            <>
              <div
                key={
                  currentproDependenceData?.dependence_services_info[0]?.name
                }
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
                    {
                      currentproDependenceData?.dependence_services_info[0]
                        ?.name
                    }
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
                  {/* {currentproDependenceData?.dependence_services_info[0]
                    ?.is_pack_exist ? ( "" ) : (
                      <p style={{color:"red"}}>{currentproDependenceData?.dependence_services_info[0]?.name} 服务的安装包不存在 ！</p>
                    )} */}
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
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
                      <Form.Item
                        label="选择主机"
                        name={`${currentproDependenceData?.dependence_services_info[0]?.name}|ip`}
                      >
                        <Select
                          disabled={true}
                          style={{ width: 200 }}
                          // onChange={(e) => {
                          //   const IpArr = e.split(".");
                          //   form.setFieldsValue({
                          //     [`${currentproDependenceData?.dependence_services_info[0]?.name}|instanceName`]: `${
                          //       currentproDependenceData
                          //         ?.dependence_services_info[0]?.name
                          //     }-${IpArr[IpArr.length - 2]}-${
                          //       IpArr[IpArr.length - 1]
                          //     }`,
                          //   });
                          // }}
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
                        name={`${currentproDependenceData?.dependence_services_info[0]?.name}|instanceName`}
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
                    </Form>
                    <a
                      style={{
                        fontSize: 13,
                        display: "flex",
                        alignItems: "center",
                        flexDirection: "row-reverse",
                        paddingRight: 100,
                      }}
                      onClick={() => {
                        setIsOpen({
                          ...isOpen,
                          [currentproDependenceData?.dependence_services_info[0]
                            ?.name]:
                            !isOpen[
                              currentproDependenceData
                                ?.dependence_services_info[0]?.name
                            ],
                        });
                      }}
                    >
                      <DownOutlined
                        style={{
                          transform: `rotate(${
                            isOpen[
                              currentproDependenceData
                                ?.dependence_services_info[0]?.name
                            ]
                              ? 180
                              : 0
                          }deg)`,
                          position: "relative",
                          top: isOpen[
                            currentproDependenceData
                              ?.dependence_services_info[0]?.name
                          ]
                            ? -1
                            : 1,
                          left: 3,
                        }}
                      />
                      查看更多配置
                    </a>
                  </div>

                  <div
                    //className={styles.backIcon}
                    style={
                      isOpen[
                        currentproDependenceData?.dependence_services_info[0]
                          ?.name
                      ]
                        ? step2Open(
                            currentproDependenceData
                              ?.dependence_services_info[0]?.app_install_args
                              ?.length +
                              currentproDependenceData
                                ?.dependence_services_info[0]?.app_port.length
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
                      {currentproDependenceData?.dependence_services_info[0]?.app_install_args?.map(
                        (i) => {
                          return (
                            <Form.Item
                              key={i.key}
                              style={{ paddingLeft: 15, paddingBottom: 15 }}
                              label={
                                <span style={{ width: 60 }}>{i.name}</span>
                              }
                              name={`install|${
                                currentproDependenceData
                                  ?.dependence_services_info[0]?.name
                              }|${JSON.stringify({
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
                        }
                      )}
                      {currentproDependenceData?.dependence_services_info[0]?.app_port?.map(
                        (i) => {
                          return (
                            <Form.Item
                              key={i.key}
                              style={{ paddingLeft: 15, paddingBottom: 15 }}
                              label={
                                <span style={{ width: 60 }}>{i.name}</span>
                              }
                              name={`port|${
                                currentproDependenceData
                                  ?.dependence_services_info[0]?.name
                              }|${JSON.stringify({
                                name: i.name,
                                key: i.key,
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
                        }
                      )}
                    </Form>
                  </div>
                </div>
              </div>
            </>
          ) : (
            ""
          )}

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
                  setStepNum(0);
                }}
              >
                上一步
              </Button>
              <Button
                type="primary"
                loading={loading}
                onClick={() => {
                  // 先出发表单校验
                  form
                    .validateFields()
                    .then((values) => {
                      setLoading(true);
                      setStep2Data(form.getFieldsValue());
                      let st2 = form.getFieldsValue();
                      //setStepNum(2);

                      let parameterCreate = (
                        step2Data,
                        type,
                        length = 3,
                        type2
                      ) => {
                        console.log(step2Data, type, (length = 3), type2);
                        let arr = [];
                        Object.keys(step2Data).map((key) => {
                          if (
                            key.split("|")[0] == type &&
                            key.split("|").length == length &&
                            key.split("|")[1] == type2
                          ) {
                            let data = JSON.parse(key.split("|")[length - 1]);
                            arr.push({
                              ...data,
                              default: step2Data[key],
                            });
                          }
                        });
                        return arr;
                      };

                      const analysisJdk = (st2, type, length = 3, type2) => {
                        let result = {};
                        for (const key in st2) {
                          let keyArr = key.split("|");
                          if (keyArr.length == length) {
                            if (keyArr[0] == type && keyArr[1] == type2) {
                              result[keyArr[2]] = st2[key];
                            }
                          }
                        }
                        return result;
                      };

                      let installArr = install_servicesRef.current;
                      let app_install_args = install_servicesRef.current[0]
                        ? analysisJdk(
                            st2,
                            "install",
                            3,
                            install_servicesRef.current[0]?.name
                          )
                        : {};

                      let ipAndInstanceName = {};
                      Object.keys(st2).map((o) => {
                        let arr = o.split("|");
                        if (arr.length == 2 && arr[0] == installArr[0]?.name) {
                          ipAndInstanceName[arr[1]] = st2[o];
                        }
                      });

                      if (installArr.length > 0) {
                        install_servicesRef.current[0].ip =
                          ipAndInstanceName.ip;
                        install_servicesRef.current[0].service_instance_name =
                          ipAndInstanceName.instanceName;
                        install_servicesRef.current[0].app_install_args =
                          install_servicesRef.current[0]?.app_install_args?.map(
                            (item) => {
                              let key = JSON.stringify({
                                name: item.name,
                                key: item.key,
                                dir_key: item.dir_key,
                              });
                              return {
                                ...item,
                                default: app_install_args[key],
                              };
                            }
                          );
                        install_servicesRef.current[0].app_port = [];
                      }

                      use_exist_servicesRef.current =
                        use_exist_servicesRef.current.map((item) => {
                          return {
                            ...item,
                            type: "single",
                          };
                        });

                      let data = {
                        install_type: 0,
                        use_exist_services: use_exist_servicesRef.current,
                        install_services: [
                          {
                            name: currentproDependenceData?.pro_services[0]
                              ?.name,
                            version: versionCurrent,
                            ip: st2.ip,
                            app_install_args: parameterCreate(
                              st2,
                              "install",
                              3,
                              currentproDependenceData?.pro_services[0]?.name
                            ),
                            app_port: parameterCreate(
                              st2,
                              "port",
                              3,
                              currentproDependenceData?.pro_services[0]?.name
                            ),
                            service_instance_name: st2.instanceName,
                            //deploy_mode: JSON.parse(step1Data.clusterMode),
                          },
                          ...install_servicesRef.current,
                        ],
                      };
                      console.log(data);
                      //return;
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
                                let isOpenCopy = JSON.parse(
                                  JSON.stringify(isOpen)
                                );
                                for (const key in isOpenCopy) {
                                  isOpenCopy[key] = true;
                                }
                                setIsOpen({
                                  ...isOpenCopy,
                                  [currentproDependenceData
                                    ?.dependence_services_info[0]?.name]: true,
                                });

                                res.data.install_services?.map((item, idx) => {
                                  if (
                                    item.check_flag == false &&
                                    item.check_msg
                                  ) {
                                    if (idx == 0) {
                                      form.setFields([
                                        {
                                          name: "instanceName",
                                          errors: [
                                            res.data.install_services[0]
                                              .check_msg,
                                          ],
                                        },
                                      ]);
                                    } else {
                                      form.setFields([
                                        {
                                          name: `${item.name}|instanceName`,
                                          errors: [item.check_msg],
                                        },
                                      ]);
                                    }
                                  }
                                  item.app_port?.map((i) => {
                                    if (i.check_flag == false) {
                                      form.setFields([
                                        {
                                          name: `port|${
                                            item.name
                                          }|${JSON.stringify({
                                            name: i.name,
                                            key: i.key,
                                          })}`,
                                          errors: [i.check_msg],
                                        },
                                      ]);
                                    }
                                  });
                                  item.app_install_args?.map((i) => {
                                    if (i.check_flag == false) {
                                      form.setFields([
                                        {
                                          name: `install|${
                                            item.name
                                          }|${JSON.stringify({
                                            name: i.name,
                                            key: i.key,
                                            dir_key: i.dir_key,
                                          })}`,
                                          errors: [i.check_msg],
                                        },
                                      ]);
                                    }
                                  });
                                });
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
                    })
                    .catch((errorInfo) => {
                      console.log(errorInfo);
                      let isOpenCopy = JSON.parse(JSON.stringify(isOpen));
                      for (const key in isOpenCopy) {
                        isOpenCopy[key] = true;
                      }
                      setIsOpen({
                        ...isOpenCopy,
                      });
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
          {step3Data?.detail_lst?.map((item) => {
            return (
              <div
                key={item?.service_instance_name}
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
                    {item.service_name}
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
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                    }}
                  >
                    <div
                      style={{
                        width: 320,
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
                        paddingRight: 100,
                      }}
                      onClick={() => {
                        setIsDetailOpen({
                          ...isDetailOpen,
                          [item.service_name]: !isDetailOpen[item.service_name],
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
                      isDetailOpen[item.service_name]
                        ? step3Open(2)
                        : step3NotOpen()
                    }
                  >
                    {item.log ? item.log : "正在安装..."}
                  </div>
                </div>
              </div>
            );
          })}
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

export default ApplicationInstallation;
