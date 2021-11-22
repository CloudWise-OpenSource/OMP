import { Button, Form, Checkbox, Input, Menu } from "antd";
import { useEffect, useRef, useState, useCallback } from "react";
import { SearchOutlined } from "@ant-design/icons";
import { useSelector } from "react-redux";
import ServiceConfigItem from "../component/ServiceConfigItem";

const Step3 = ({ setStepNum }) => {
  // 服务的loading
  const [loading, setLoading] = useState(false)

  const [checked, setChecked] = useState(false);

  const [serviceConfigform] = Form.useForm();

  const viewHeight = useSelector((state) => state.layouts.viewSize.height);

  // 指定本次安装服务运行用户
  const [runUser, setRunUser] = useState("");

  // 筛选后的ip列表
  const [currentIpList, setCurrentIpList] = useState([]);

  // ip列表中的选中项
  const [checkIp, setCheckIp] = useState("");

  // ip 筛选value
  const [searchIp, setSearchIp] = useState("");

  // ip列表的数据源
  const [ipList, setIpList] = useState([]);

  const dataSource = [
    {
      name: "doucApi",
      install_args: [
        {
          name: "安装目录",
          key: "base_dir",
          default: "/app/doucApi",
          dir_key: "{data_path}",
        },
        {
          name: "日志目录",
          key: "log_dir",
          default: "/logs/doucApi",
          dir_key: "{data_path}",
        },
        {
          name: "数据目录",
          key: "data_dir",
          default: "/appData/doucApi",
          dir_key: "{data_path}",
        },
        {
          name: "启动内存",
          key: "memory",
          default: "1g",
        },
        {
          name: "数据库",
          key: "dbname",
          default: "cw_douc",
        },
        {
          name: "安装用户",
          key: "run_user",
          default: "commonuser",
        },
        {
          name: "kafka_topic名字",
          key: "kafka_topic",
          default: "cw-logs",
        },
      ],
      ports: [
        {
          name: "服务端口",
          protocol: "TCP",
          key: "service_port",
          default: "18241",
        },
        {
          name: "metric端口",
          protocol: "TCP",
          key: "metrics_port",
          default: "18241",
        },
      ],
    },
    {
      name: "doucSso",
      install_args: [
        {
          name: "安装目录",
          key: "base_dir",
          default: "/app/doucSso",
          dir_key: "{data_path}",
        },
        {
          name: "日志目录",
          key: "log_dir",
          default: "/logs/doucSso",
          dir_key: "{data_path}",
        },
        {
          name: "数据目录",
          key: "data_dir",
          default: "/appData/doucSso",
          dir_key: "{data_path}",
        },
        {
          name: "启动内存",
          key: "memory",
          default: "1g",
        },
        {
          name: "数据库",
          key: "dbname",
          default: "cw_douc",
        },
        {
          name: "安装用户",
          key: "run_user",
          default: "commonuser",
        },
        {
          name: "kafka_topic名字",
          key: "kafka_topic",
          default: "cw-logs",
        },
      ],
      ports: [
        {
          name: "服务端口",
          protocol: "TCP",
          key: "service_port",
          default: "18256",
        },
        {
          name: "metric端口",
          protocol: "TCP",
          key: "metrics_port",
          default: "18256",
        },
      ],
    },
  ];

  useEffect(() => {
    // 请求ip数据
    // currentIpList
    let res = [
      "192.168.100.100",
      "10.0.14.81",
      "10.0.14.91",
      "10.0.14.90",
      "10.0.14.21",
      "10.0.14.12",
      "10.0.14.98",
      "10.0.14.34",
      "10.0.14.09",
      "10.0.14.451",
      "10.0.14.67",
      "10.0.14.56",
      "10.0.14.78",
      "10.0.14.59",
    ];
    setIpList(res);
    setCurrentIpList(res);
    setCheckIp(res[0]);
  }, []);

  useEffect(() => {
    if (checkIp) {
      console.log("checkIp改变了", checkIp);
      setLoading(true)
      setTimeout(() => {
        setLoading(false)
      }, 1000);
    }
  }, [checkIp]);

  return (
    <div>
      <div
        style={{
          marginTop: 20,
          backgroundColor: "#fff",
          padding: 10,
          paddingLeft: 30,
          display: "flex",
          alignItems: "center",
        }}
      >
        <div style={{ width: 220 }}>
          <Checkbox
            checked={checked}
            onChange={(e) => {
              if (!e.target.checked) {
                setRunUser("");
              }
              setChecked(e.target.checked);
            }}
          >
            指定本次安装服务运行用户
          </Checkbox>
        </div>

        <Input
          disabled={!checked}
          placeholder="请输入本次安装服务运行用户"
          style={{ width: 300 }}
          value={runUser}
          onChange={(e) => {
            setRunUser(e.target.value);
          }}
        />
      </div>

      <div
        style={{
          marginTop: 15,
          backgroundColor: "#fff",
          display: "flex",
        }}
      >
        <div style={{ width: 240 }}>
          <div
            style={{
              padding: "15px 5px 10px 5px",
            }}
          >
            <Input
              allowClear
              onBlur={() => {
                if (searchIp) {
                  let result = ipList.filter((i) => {
                    return i.includes(searchIp);
                  });
                  setCurrentIpList(result);
                  result.length > 0 && setCheckIp(result[0]);
                } else {
                  setCurrentIpList(ipList);
                  setCheckIp(ipList[0]);
                }
              }}
              value={searchIp}
              onChange={(e) => {
                setSearchIp(e.target.value);
                if (!e.target.value) {
                  setCurrentIpList(ipList);
                  setCheckIp(ipList[0]);
                }
              }}
              onPressEnter={() => {
                if (searchIp) {
                  let result = ipList.filter((i) => {
                    return i.includes(searchIp);
                  });
                  setCurrentIpList(result);
                  result.length > 0 && setCheckIp(result[0]);
                } else {
                  setCurrentIpList(ipList);
                  setCheckIp(ipList[0]);
                }
              }}
              placeholder="搜索IP地址"
              suffix={
                !searchIp && <SearchOutlined style={{ color: "#b6b6b6" }} />
              }
            />
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
              {currentIpList.map((item) => {
                return (
                  <div
                    style={{
                      padding: 5,
                      paddingLeft: 30,
                      color: checkIp == item ? "#4986f7" : "",
                      backgroundColor: checkIp == item ? "#edf8fe" : "",
                    }}
                    key={item}
                    onClick={() => {
                      setCheckIp(item);
                    }}
                  >
                    {item}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
        <div
          style={{
            flex: 1,
            borderLeft: "1px solid #d9d9d9",
            height: viewHeight - 335,
            overflowY: "auto",
          }}
        >
          <Form form={serviceConfigform} name="config" labelCol={{ span: 8 }}>
            {dataSource.map((item) => {
              return (
                <ServiceConfigItem
                  key={item.name}
                  data={item}
                  form={serviceConfigform}
                  loading={loading}
                />
              );
            })}
          </Form>
        </div>
      </div>

      <div
        style={{
          position: "fixed",
          backgroundColor: "#fff",
          width: "calc(100% - 230px)",
          bottom: 10,
          padding: "10px 0px",
          display: "flex",
          justifyContent: "space-between",
          paddingRight: 30,
          boxShadow: "0px 0px 10px #999999",
          alignItems: "center",
          borderRadius: 2,
        }}
      >
        <div style={{ paddingLeft: 20 }}>分布主机数量: {ipList.length}台</div>
        <div>
          <Button
            type="primary"
            onClick={() => {
              setStepNum(1);
            }}
          >
            上一步
          </Button>
          <Button
            style={{ marginLeft: 10 }}
            type="primary"
            //disabled={unassignedServices !== 0}
            onClick={() => {
              setStepNum(3);
              serviceConfigform.validateFields().then(
                (e) => {
                  console.log("成功了", e);
                },
                (e) => {
                  console.log("失败了", e);
                }
              );
            }}
          >
            开始安装
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Step3;
