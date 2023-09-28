import { useHistory, useLocation } from "react-router-dom";
import styles from "./index.module.less";
import { useSelector } from "react-redux";
import { fetchPost } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { handleResponse } from "@/utils/utils";
import {
  Radio,
  Steps,
  Table,
  Button,
  Form,
  Checkbox,
  Row,
  Input,
  Tooltip,
  Collapse,
  Tag,
  Modal,
  Spin,
  Result,
  message,
  Select,
  Switch,
} from "antd";
import { useState, useEffect } from "react";
import {
  LeftOutlined,
  CheckCircleFilled,
  CloseCircleFilled,
  CaretRightOutlined,
  InfoCircleOutlined,
  SyncOutlined,
  ExclamationCircleFilled,
  ZoomInOutlined,
} from "@ant-design/icons";

const { Panel } = Collapse;

const ServiceItem = ({ form, itemData, errInfo, productName }) => {
  const version =
    typeof itemData?.version === "string"
      ? itemData.version
      : itemData.version[0];

  useEffect(() => {
    form.setFieldsValue({
      [`${itemData.name}-base_dir`]: itemData.base_dir?.replace(
        "{data_path}",
        ""
      ),
      [`${itemData.name}-data_dir`]: itemData.data_dir?.replace(
        "{data_path}",
        ""
      ),
      [`${itemData.name}-log_dir`]: itemData.log_dir?.replace(
        "{data_path}",
        ""
      ),
      [`${itemData.name}-run_user`]: itemData.run_user,
      [`${itemData.name}-service_port`]: itemData.service_port,
    });
  }, []);

  return (
    <div style={{ padding: 10, paddingTop: 0 }}>
      <Collapse
        bordered={false}
        defaultActiveKey={["1"]}
        expandIcon={({ isActive }) => (
          <CaretRightOutlined rotate={isActive ? 90 : 0} />
        )}
      >
        <Panel
          header={
            <>
              {productName ? (
                <span
                  style={{ color: "rgb(73,134,247)", marginRight: 12 }}
                >{`[ ${productName} ]`}</span>
              ) : (
                ""
              )}
              {itemData.name}
              {errInfo && (
                <span style={{ color: "red", marginLeft: 20 }}>{errInfo}</span>
              )}
            </>
          }
          extra={version}
          key="1"
          className={"panelItem"}
          style={{ backgroundColor: "#f6f6f6" }}
        >
          <Form.Item
            label="安装目录"
            key="base_dir"
            name={`${itemData.name}-base_dir`}
            style={{ marginTop: 10, width: 600 }}
          >
            <Input
              addonBefore={<span style={{ color: "#b1b1b1" }}>/ 数据分区</span>}
              placeholder="请输入安装目录"
              suffix={
                <Tooltip title="数据分区：主机所设置的数据分区">
                  <InfoCircleOutlined style={{ color: "rgba(0,0,0,.45)" }} />
                </Tooltip>
              }
            />
          </Form.Item>
          <Form.Item
            label="数据目录"
            key="data_dir"
            name={`${itemData.name}-data_dir`}
            style={{ marginTop: 10, width: 600 }}
          >
            <Input
              addonBefore={<span style={{ color: "#b1b1b1" }}>/ 数据分区</span>}
              placeholder="请输入数据目录"
              suffix={
                <Tooltip title="数据分区：主机所设置的数据分区">
                  <InfoCircleOutlined style={{ color: "rgba(0,0,0,.45)" }} />
                </Tooltip>
              }
            />
          </Form.Item>
          <Form.Item
            label="日志目录"
            key="log_dir"
            name={`${itemData.name}-log_dir`}
            style={{ marginTop: 10, width: 600 }}
          >
            <Input
              addonBefore={<span style={{ color: "#b1b1b1" }}>/ 数据分区</span>}
              placeholder="请输入数据目录"
              suffix={
                <Tooltip title="数据分区：主机所设置的数据分区">
                  <InfoCircleOutlined style={{ color: "rgba(0,0,0,.45)" }} />
                </Tooltip>
              }
            />
          </Form.Item>
          <Form.Item
            label="运行用户"
            key="run_user"
            name={`${itemData.name}-run_user`}
            style={{ marginTop: 10, width: 600 }}
          >
            <Input placeholder="请输入运行用户" />
          </Form.Item>
          <Form.Item
            label="服务端口"
            key="service_port"
            name={`${itemData.name}-service_port`}
            style={{ marginTop: 10, width: 600 }}
          >
            <Input placeholder="请输入服务端口" />
          </Form.Item>
        </Panel>
      </Collapse>
    </div>
  );
};

// 第一步
const Step1 = ({
  setStepNum,
  getServiceData,
  setCheckServiceData,
  setServiceConnectionData,
}) => {
  const ipArr = Object.keys(getServiceData?.ips || []);

  const viewHeight = useSelector((state) => state.layouts.viewSize.height);

  // 选中ip数据
  const [getServiceIpArr, setGetServiceIpArr] = useState([]);

  // 选中所有ip
  const [selectAllIp, setSelectAllIp] = useState(false);

  // 服务数据表单
  const [serviceForm] = Form.useForm();

  // 扫描中对话框
  const [ingVisible, setIngVisible] = useState(false);

  // 加载
  const [loading, setLoading] = useState(false);

  const getPathValue = (name, dirType) => {
    const value = serviceForm.getFieldValue(name + "-" + dirType);
    return value !== "" ? "{data_path}" + value : "";
  };

  // 服务纳管
  const startGetService = () => {
    setLoading(true);
    setIngVisible(true);
    const serviceData = [...getServiceData.service];
    const resArr = [];
    // 处理服务信息
    for (let i = 0; i < serviceData.length; i++) {
      const element = serviceData[i];
      if (element.hasOwnProperty("child")) {
        const childInfo = {};
        childInfo[element.version[0]] = element.child[element.version[0]].map(
          (i) => {
            return {
              name: i.name,
              version: i.version,
              base_dir: getPathValue(i.name, "base_dir"),
              data_dir: getPathValue(i.name, "data_dir"),
              log_dir: getPathValue(i.name, "log_dir"),
              run_user: serviceForm.getFieldValue(`${i.name}-run_user`),
              service_port: serviceForm.getFieldValue(`${i.name}-service_port`),
            };
          }
        );
        resArr.push({
          name: element.name,
          version: element.version,
          child: childInfo,
        });
      } else {
        resArr.push({
          name: element.name,
          version: element.version,
          base_dir: getPathValue(element.name, "base_dir"),
          data_dir: getPathValue(element.name, "data_dir"),
          log_dir: getPathValue(element.name, "log_dir"),
          run_user: serviceForm.getFieldValue(`${element.name}-run_user`),
          service_port: serviceForm.getFieldValue(
            `${element.name}-service_port`
          ),
        });
      }
    }
    // 处理ip信息
    const ipsRes = {};
    for (const key in getServiceData.ips) {
      if (Object.hasOwnProperty.call(getServiceData.ips, key)) {
        const element = getServiceData.ips[key];
        if (getServiceIpArr.indexOf(key) !== -1) {
          ipsRes[key] = element;
        }
      }
    }
    fetchPost(apiRequest.appStore.appConfCheck, {
      body: {
        data: {
          service: resArr,
          ips: ipsRes,
          is_continue: getServiceData.is_continue,
        },
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          setCheckServiceData(res.data);
          let connectData = {};
          const targetData = res.data.ser_info;
          for (let index = 0; index < targetData.length; index++) {
            const element = targetData[index];
            connectData[element.name] = {
              is_use_exist: element.is_use_exist,
              exist_instance:
                element.exist_instance.length === 0
                  ? []
                  : [element.exist_instance[0]],
            };
          }
          setServiceConnectionData(connectData);
          setStepNum(1);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
        setIngVisible(false);
      });
  };

  return (
    <div>
      <div
        style={{
          marginTop: 20,
          padding: 10,
          paddingLeft: 30,
          display: "flex",
          alignItems: "center",
          backgroundColor: "#fff",
        }}
      >
        <ExclamationCircleFilled
          style={{ fontSize: 16, marginRight: 10, color: "rgb(72,134,247)" }}
        />
        请选择本次纳管的主机范围，填写服务相关信息
      </div>
      <Spin spinning={loading}>
        <div
          style={{
            marginTop: 15,
            display: "flex",
            backgroundColor: "#fff",
          }}
        >
          <div
            style={{
              width: 240,
            }}
          >
            <div
              style={{
                padding: "15px 5px 10px 5px",
              }}
            >
              <p style={{ marginLeft: 20 }}>
                选择主机 :
                <Radio
                  style={{ float: "right" }}
                  disabled={ipArr.length === 0}
                  checked={selectAllIp}
                  onClick={() => {
                    const target = !selectAllIp;
                    setSelectAllIp(target);
                    setGetServiceIpArr(target ? ipArr : []);
                  }}
                >
                  全选
                </Radio>
              </p>

              {ipArr?.length === 0 ? (
                <span style={{ marginLeft: 30, color: "#a7abb7" }}>
                  暂无可选的主机
                </span>
              ) : (
                <Checkbox.Group
                  value={getServiceIpArr}
                  onChange={(checkedValues) => {
                    setGetServiceIpArr(checkedValues);
                    setSelectAllIp(
                      checkedValues.length === ipArr.length ? true : false
                    );
                  }}
                  style={{
                    marginLeft: 30,
                  }}
                >
                  {ipArr.map((e) => {
                    return (
                      <Row>
                        <Checkbox
                          key={e}
                          value={e}
                          style={{ lineHeight: "32px" }}
                        >
                          {e}
                        </Checkbox>
                      </Row>
                    );
                  })}
                </Checkbox.Group>
              )}
            </div>

            <div
              style={{
                overflowY: "auto",
              }}
            >
              <div
                style={{
                  cursor: "pointer",
                  borderRight: "0px",
                  height: viewHeight - 390,
                }}
              >
                <div style={{ height: 100 }}></div>
              </div>
            </div>
          </div>
          <div
            style={{
              flex: 1,
              borderLeft: "1px solid #d9d9d9",
              overflowY: "auto",
              paddingTop: 10,
            }}
          >
            <Form
              form={serviceForm}
              name="serviceForm"
              labelCol={{ span: 8 }}
              wrapperCol={{ span: 40 }}
            >
              {getServiceData?.service?.map((item) => {
                if (item.hasOwnProperty("child")) {
                  const childArr = item.child[item.version[0]];
                  return childArr.map((i) => {
                    return (
                      <ServiceItem
                        itemData={i}
                        form={serviceForm}
                        errInfo={item.error}
                        productName={item.name}
                      />
                    );
                  });
                }
                return (
                  <ServiceItem
                    itemData={item}
                    form={serviceForm}
                    errInfo={item.error}
                  />
                );
              })}
            </Form>
          </div>
        </div>
      </Spin>
      <div
        style={{
          position: "fixed",
          backgroundColor: "#fff",
          width: "calc(100% - 230px)",
          bottom: 4,
          padding: "10px 0px",
          display: "flex",
          justifyContent: "space-between",
          paddingRight: 30,
          boxShadow: "0px 0px 10px #999999",
          alignItems: "center",
          borderRadius: 2,
        }}
      >
        <div style={{ paddingLeft: 20 }}>
          分布主机: {getServiceIpArr.length} 台
        </div>
        <div>
          <Button
            style={{ marginLeft: 10 }}
            type="primary"
            disabled={
              !getServiceData?.is_continue || getServiceIpArr.length === 0
            }
            loading={loading}
            onClick={() => {
              startGetService();
            }}
          >
            扫描服务
          </Button>
        </div>
      </div>

      <Modal
        title={
          <span>
            <span style={{ position: "relative", left: "-10px" }}>
              <ZoomInOutlined />
            </span>
            <span>服务纳管</span>
          </span>
        }
        visible={ingVisible}
        width={600}
        bodyStyle={{
          fontSize: 14,
        }}
        onCancel={() => {
          setIngVisible(false);
        }}
        footer={null}
      >
        <div style={{ margin: 20 }}>
          <SyncOutlined
            spin
            style={{
              marginRight: 16,
              fontSize: 16,
            }}
          />
          正在按照服务相关信息，对指定服务器进行扫描，请稍后...
        </div>
      </Modal>
    </div>
  );
};

// 第二步
const Step2 = ({
  setStepNum,
  getServiceData,
  checkServiceData,
  serviceConnectionData,
  setServiceConnectionData,
}) => {
  const tableData = checkServiceData?.ser_info;

  // 加载
  const [loading, setLoading] = useState(false);

  const addService = () => {
    const resSerInfo = [];
    const sourceData = checkServiceData.ser_info;
    for (let index = 0; index < sourceData.length; index++) {
      const element = sourceData[index];
      resSerInfo.push({
        name: element.name,
        error: element.error,
        ip: element.ip,
        is_use_exist: serviceConnectionData[element.name].is_use_exist,
        exist_instance: serviceConnectionData[element.name].exist_instance,
      });
    }
    setLoading(true);
    fetchPost(apiRequest.appStore.appConfCheck, {
      body: {
        data: {
          ser_info: resSerInfo,
          uuid: checkServiceData.uuid,
        },
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.data.is_error) {
            message.warning(res.data.message);
          } else {
            setStepNum(2);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => setLoading(false));
  };

  const tableColumn = [
    {
      title: "服务名称",
      dataIndex: "name",
      key: "name",
      align: "center",
      width: 200,
    },
    {
      title: "扫描到该服务的IP",
      dataIndex: "ip",
      key: "ip",
      align: "center",
      width: 300,
      filters: Object.keys(getServiceData?.ips || []).map((i) => {
        return {
          value: i,
          text: i,
        };
      }),
      onFilter: (value, record) => record.ip.indexOf(value) !== -1,
      render: (text) => {
        if (typeof text === "string") {
          return text;
        } else if (text.length === 0) {
          return "-";
        } else {
          return (
            <>
              {text.map((i) => (
                <Tag>{i}</Tag>
              ))}
            </>
          );
        }
      },
    },
    {
      title: "关联集群",
      dataIndex: "is_use_exist",
      key: "is_use_exist",
      align: "center",
      width: 80,
      render: (text, record) => {
        return (
          <Switch
            defaultChecked={record.is_use_exist}
            disabled={!record.is_use_exist}
            onChange={(value) => {
              const resData = {};
              for (const key in serviceConnectionData) {
                if (Object.hasOwnProperty.call(serviceConnectionData, key)) {
                  const element = serviceConnectionData[key];
                  if (key === record.name) {
                    resData[key] = {
                      is_use_exist: value,
                      exist_instance: element.exist_instance,
                    };
                  } else {
                    resData[key] = element;
                  }
                }
              }
              setServiceConnectionData(resData);
            }}
          />
        );
      },
    },
    {
      title: "可选集群实例",
      dataIndex: "exist_instance",
      key: "exist_instance",
      align: "center",
      width: 260,
      render: (text, record) => {
        if (record.exist_instance.length === 0) {
          return "无可用实例";
        } else {
          return (
            <Select
              defaultValue={record.exist_instance[0]}
              disabled={!serviceConnectionData[record.name].is_use_exist}
              onChange={(value) => {
                const resData = {};
                for (const key in serviceConnectionData) {
                  if (Object.hasOwnProperty.call(serviceConnectionData, key)) {
                    const element = serviceConnectionData[key];
                    if (key === record.name) {
                      resData[key] = {
                        is_use_exist: element.is_use_exist,
                        exist_instance: value,
                      };
                    } else {
                      resData[key] = element;
                    }
                  }
                }
                setServiceConnectionData(resData);
              }}
              options={record.exist_instance.map((e) => {
                return {
                  value: e,
                  label: e,
                };
              })}
            />
          );
        }
      },
    },
    {
      title: "校验结果",
      dataIndex: "check",
      key: "check",
      align: "center",
      width: 100,
      render: (text, record) => {
        return record.error ? (
          <CloseCircleFilled
            style={{ color: "rgb(247,77,80)", fontSize: 16 }}
          />
        ) : (
          <CheckCircleFilled
            style={{ color: "rgb(82,196,27)", fontSize: 16 }}
          />
        );
      },
    },
    {
      title: "错误信息",
      dataIndex: "error",
      key: "error",
      align: "center",
      render: (text) => {
        return text || "-";
      },
    },
  ];

  return (
    <div>
      <div
        style={{
          marginTop: 20,
          padding: 10,
          paddingLeft: 30,
          display: "flex",
          alignItems: "center",
          backgroundColor: "#fff",
        }}
      >
        <ExclamationCircleFilled
          style={{ fontSize: 16, marginRight: 10, color: "rgb(72,134,247)" }}
        />
        扫描结果如下
      </div>

      <div
        style={{
          width: "100%",
          marginTop: 15,
          display: "flex",
          backgroundColor: "#fff",
          padding: 20,
        }}
      >
        <Table
          columns={tableColumn}
          dataSource={tableData}
          bordered
          style={{ width: "100%" }}
          pagination={{
            pageSize: 10,
          }}
        />
      </div>

      <div
        style={{
          position: "fixed",
          backgroundColor: "#fff",
          width: "calc(100% - 230px)",
          bottom: 4,
          padding: "10px 0px",
          display: "flex",
          justifyContent: "space-between",
          paddingRight: 30,
          boxShadow: "0px 0px 10px #999999",
          alignItems: "center",
          borderRadius: 2,
        }}
      >
        <div />
        <div>
          <Button
            type="primary"
            onClick={() => {
              setStepNum(0);
            }}
          >
            上一步
          </Button>
          <Button
            style={{ marginLeft: 10 }}
            type="primary"
            disabled={!checkServiceData?.is_continue}
            loading={loading}
            onClick={() => {
              addService();
            }}
          >
            纳管
          </Button>
        </div>
      </div>
    </div>
  );
};

const GetService = () => {
  const history = useHistory();
  const location = useLocation();

  // 服务纳管初始数据
  const getServiceData = location.state?.getServiceData;
  // 服务扫描信息
  const [checkServiceData, setCheckServiceData] = useState(null);
  // 服务关联信息
  const [serviceConnectionData, setServiceConnectionData] = useState({});
  // 步骤
  const [stepNum, setStepNum] = useState(0);

  return (
    <div
      style={{
        backgroundColor: "rgb(240, 242, 245)",
      }}
    >
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
            onClick={() => {
              history?.goBack();
            }}
          />
          服务纳管
        </div>
        <div style={{ width: 600, position: "relative", left: -60 }}>
          <Steps size="small" current={stepNum}>
            <Steps.Step title="基本信息" />
            <Steps.Step title="扫描结果" />
            <Steps.Step title="服务纳管" />
          </Steps>
        </div>
        <div />
      </div>
      {stepNum == 0 && (
        <Step1
          setStepNum={setStepNum}
          getServiceData={getServiceData}
          setCheckServiceData={setCheckServiceData}
          setServiceConnectionData={setServiceConnectionData}
        />
      )}
      {stepNum == 1 && (
        <Step2
          setStepNum={setStepNum}
          getServiceData={getServiceData}
          checkServiceData={checkServiceData}
          serviceConnectionData={serviceConnectionData}
          setServiceConnectionData={setServiceConnectionData}
        />
      )}
      {stepNum == 2 && (
        <Result
          style={{
            paddingTop: "10%",
            backgroundColor: "#fff",
          }}
          status="success"
          title="服务纳管执行成功"
          extra={[
            <Button
              onClick={() => {
                history?.goBack();
              }}
            >
              返回
            </Button>,
            <Button
              type="primary"
              onClick={() => {
                history?.push("/application_management/service_management");
              }}
            >
              查看服务
            </Button>,
          ]}
        />
      )}
    </div>
  );
};

export default GetService;
