import { useCallback, useEffect, useState } from "react";
import { useHistory, useLocation } from "react-router-dom";
import { handleResponse } from "@/utils/utils";
import { fetchGet } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { Steps, Form, Input, Button, Select, Checkbox, Tooltip } from "antd";
import { LeftOutlined, DownOutlined, InfoCircleOutlined } from "@ant-design/icons";
import styles from "./index.module.less";
import RenderComDependence from "./component/RenderComDependence";

const step2Open = (num) => ({
  minHeight: 30,
  height: num * 60,
  transition: "all .2s ease-in",
  overflow: "hidden",
  backgroundColor:"red"
});

const step2NotOpen = () => ({
  height: 0,
  minHeight: 0,
  transition: "all .2s ease-in",
  overflow: "hidden",
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
  const [isOpen, setIsOpen] = useState(false);

  const [versionCurrent, setVersionCurrent] = useState("");

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
          setIpListSource([res.data[0], "19.202.304.0", "19.202.34.10"]);
          const firstIP = res.data[0].split(".");
          form.setFieldsValue({
            ip: res.data[0],
            instanceName: `${name}-${firstIP[firstIP.length - 2]}-${
              firstIP[firstIP.length - 1]
            }`,
          });
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setSearchLoading(false);
      });
  };

  useEffect(() => {
    fetchData();
    fetchIPlist();
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
              <Form
                form={form}
                layout="inline"
                name="basic"
                initialValues={{
                  clusterMode: "singleInstance",
                }}
              >
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
                    <Select.Option value="singleInstance">单实例</Select.Option>
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
                console.log(form.getFieldsValue());
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
                    setIsOpen(!isOpen);
                  }}
                >
                  <DownOutlined
                    style={{
                      transform: `rotate(${isOpen ? 180 : 0}deg)`,
                      position: "relative",
                      top: isOpen ? -1 : 1,
                      left: 3,
                    }}
                  />
                  查看更多配置
                </a>
              </Form>
              <div
                //className={styles.backIcon}
                style={
                  isOpen
                    ? step2Open(
                        currentAppDependenceData.app_install_args.length
                      )
                    : step2NotOpen()
                }
              >
                <Form
                  form={form}
                  layout="inline"
                  name="basic"
                  style={{
                    marginTop:20
                  }}
                  rules={[
                    {
                      required: true,
                      message: "请填写安装目录",
                    },
                  ]}
                >
                  <Form.Item label="安装目录" name="ip">
                    <Input addonBefore={123} style={{ width: 400 }} 
                    suffix={
                      <Tooltip title="请使用root或具有sudo免密码权限的用户">
                        <InfoCircleOutlined style={{ color: "rgba(0,0,0,.45)" }} />
                      </Tooltip>
                    }
                    />
                  </Form.Item>
                </Form>
              </div>
            </div>
          </div>

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
                  marginRight: 10,
                }}
                type="primary"
                onClick={() => {
                  //console.log(form.getFieldsValue())
                  setStepNum(0);
                }}
              >
                上一步
              </Button>
              <Button
                type="primary"
                onClick={() => {
                  //console.log(form.getFieldsValue())
                  setStepNum(2);
                }}
              >
                开始安装
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default ComponentInstallation;
