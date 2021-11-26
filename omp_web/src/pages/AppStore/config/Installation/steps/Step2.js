import { Button, Form, Spin, message } from "antd";
import { useEffect, useState } from "react";
import ServiceDistributionItem from "../component/ServiceDistributionItem/index.js";
import { useSelector, useDispatch } from "react-redux";
import {
  getDataSourceChangeAction,
  getStep2ErrorLstChangeAction,
} from "../store/actionsCreators";
import { fetchPost, fetchGet } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { handleResponse } from "@/utils/utils";

const Step2 = ({ setStepNum }) => {
  const reduxDispatch = useDispatch();

  const uniqueKey = useSelector((state) => state.appStore.uniqueKey);

  // 基本信息的form实例
  const [form] = Form.useForm();

  const [loading, setLoading] = useState(false);

  const [installService, setInstallService] = useState({});

  const allDataPool = useSelector((state) => state.installation.dataSource);
  const ipList = useSelector((state) => state.installation.ipList);
  // useEffect(() => {
  //   reduxDispatch(
  //     getDataSourceChangeAction({
  //       doucApi: {
  //         num: 1,
  //         with: "doucSso",
  //       },
  //       doucSso: {
  //         num: 1,
  //         with: null,
  //       },
  //       doucDubboRpc: {
  //         num: 1,
  //         with: null,
  //       },
  //       doucAdmin: {
  //         num: 1,
  //         with: "doucSso",
  //       },
  //       doucZabbixApi: {
  //         num: 1,
  //         with: null,
  //       },
  //       doucWeb: {
  //         num: 1,
  //         with: null,
  //       },
  //       doucAdminWeb: {
  //         num: 1,
  //         with: null,
  //       },
  //       gatewayServer: {
  //         num: 1,
  //         with: null,
  //       },
  //       gatewayServerApi: {
  //         num: 1,
  //         with: null,
  //       },
  //       portalWeb: {
  //         num: 1,
  //         with: null,
  //       },
  //       portalServer: {
  //         num: 1,
  //         with: null,
  //       },
  //       kafka: {
  //         num: 1,
  //         with: null,
  //       },
  //       nacos: {
  //         num: 1,
  //         with: null,
  //       },
  //       mysql: {
  //         num: 1,
  //         with: null,
  //       },
  //       tengine: {
  //         num: 2,
  //         with: null,
  //       },
  //       tengine1233: {
  //         num: 1,
  //         with: "doucSso",
  //       },
  //     })
  //   );
  // }, []);

  const [data, setData] = useState({
    host: [],
    product: [],
  });

  // const data = {
  //   host: [
  //     {
  //       ip: "10.0.14.234",
  //       num: 5,
  //     },
  //     {
  //       ip: "10.0.14.235",
  //       num: 5,
  //     },
  //     {
  //       ip: "10.0.14.230",
  //       num: 2,
  //     },
  //     {
  //       ip: "10.0.14.2301",
  //       num: 2,
  //     },
  //   ],
  //   //all: ,
  //   product: [
  //     {
  //       name: "douc",
  //       child: [
  //         "doucApi",
  //         "doucSso",
  //         "doucDubboRpc",
  //         "doucAdmin",
  //         "doucZabbixApi",
  //         "doucWeb",
  //         "doucAdminWeb",
  //         "gatewayServer",
  //         "gatewayServerApi",
  //         "portalWeb",
  //         "portalServer",
  //       ],
  //     },
  //     {
  //       name: "基础组件",
  //       child: ["kafka", "nacos", "mysql", "tengine", "tengine1233"],
  //     },
  //   ],
  // };

  // 未分配服务个数
  const unassignedServices = Object.keys(allDataPool).reduce((prev, cur) => {
    return prev + allDataPool[cur].num;
  }, 0);

  const queryCreateServiceDistribution = () => {
    // checkInstallInfo 基本信息提交操作，决定是否跳转服务分布以及数据校验回显
    setLoading(true);
    fetchPost(apiRequest.appStore.createServiceDistribution, {
      body: {
        unique_key: uniqueKey,
      },
    })
      .then((res) => {
        //console.log(operateObj[operateAciton])
        handleResponse(res, (res) => {
          if (res.data && res.data.data) {
            reduxDispatch(getDataSourceChangeAction(res.data.data.all));
            setData((data) => {
              return {
                ...data,
                host: res.data.data.host,
                product: res.data.data.product,
              };
            });
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  // 已安装服务列表查询
  const queryInstallServiceData = () => {
    // setLoading(true);
    fetchGet(apiRequest.appStore.queryListServiceByIp)
      .then((res) => {
        handleResponse(res, (res) => {
          setInstallService(res.data);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        //setLoading(false);
      });
  };

  // 提交前对数据进行处理
  const dataProcessing = () => {
    let data = form.getFieldValue();
    console.log(data);
    let result = {}
    for (const key in data) {
      result[key] = data[key].map(item=>{
        return item[1]
      })
    }
    return result
  };

  // 最后的提交操作
  // checkServiceDistribution 服务分布提交操作，决定是否跳转修改配置以及数据校验回显
  const checkServiceDistribution = (queryData) => {
    // reduxDispatch(
    //   getStep2ErrorLstChangeAction([
    //     {
    //       ip: "10.0.12.243",
    //       error_msg: "主机10.0.14.234上存在重复服务: redis",
    //     },
    //   ])
    // );
    // return;
    setLoading(true);
    fetchPost(apiRequest.appStore.checkServiceDistribution, {
      body: {
        unique_key: uniqueKey,
        data: queryData,
      },
    })
      .then((res) => {
        //console.log(operateObj[operateAciton])
        handleResponse(res, (res) => {
          if (res.data && res.data.data) {
            if (res.data.is_continue) {
              // 校验通过，跳转，请求服务分布数据并跳转
              setStepNum(2);
            } else {
              message.warn("校验未通过");
              reduxDispatch(
                getStep2ErrorLstChangeAction(res.data.error_lst))
            }
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    queryCreateServiceDistribution();
    queryInstallServiceData();
  }, []);

  return (
    <>
      <div
        style={{
          marginTop: 20,
          backgroundColor: "#fff",
          padding: 10,
          paddingBottom:30
        }}
      >
        <Spin spinning={loading}>
          <div style={{ display: "flex" }}>
            <div
              style={{
                paddingLeft: 20,
                marginTop: 10,
                paddingBottom: 30,
              }}
            >
              主机总数: {data.host.length}台
            </div>
            <div
              style={{
                paddingLeft: 40,
                marginTop: 10,
                paddingBottom: 30,
              }}
            >
              未分配服务: {unassignedServices}个
            </div>
          </div>
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              paddingLeft: 30,
              paddingRight: 30,
            }}
          >
            {data.host.map((item) => {
              return (
                <ServiceDistributionItem
                  key={item.ip}
                  form={form}
                  info={item}
                  data={data.product}
                  installService={installService}
                />
              );
            })}
          </div>
        </Spin>
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
        <div style={{ paddingLeft: 20 }}>
          已分配主机数量: {ipList?.length}台
        </div>
        <div>
          <Button
            type="primary"
            onClick={() => {
              //   console.log(basicForm.getFieldsValue());
              //   console.log(dependentForm.getFieldsValue());
              setStepNum(0);
            }}
          >
            上一步
          </Button>
          <Button
            style={{ marginLeft: 10 }}
            type="primary"
            disabled={unassignedServices !== 0}
            loading={loading}
            onClick={() => {
              //setStepNum(2);
              checkServiceDistribution(dataProcessing());
            }}
          >
            下一步
          </Button>
        </div>
      </div>
    </>
  );
};

export default Step2;
