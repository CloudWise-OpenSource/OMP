import { Button, Form } from "antd";
import { useEffect, useState } from "react";
import ServiceDistributionItem from "../component/ServiceDistributionItem/index.js";
import { useSelector, useDispatch } from "react-redux";
import { getDataSourceChangeAction } from "../store/actionsCreators";

const Step2 = ({ setStepNum }) => {
  const reduxDispatch = useDispatch();
  useEffect(() => {
    reduxDispatch(
      // 这里做一个视口查询，存入store, 其他组件可以根据视口大小进行自适应
      getDataSourceChangeAction({
        doucApi: {
          num: 1,
          with: null,
        },
        doucSso: {
          num: 1,
          with: null,
        },
        doucDubboRpc: {
          num: 1,
          with: null,
        },
        doucAdmin: {
          num: 1,
          with: null,
        },
        doucZabbixApi: {
          num: 1,
          with: null,
        },
        doucWeb: {
          num: 1,
          with: null,
        },
        doucAdminWeb: {
          num: 1,
          with: null,
        },
        gatewayServer: {
          num: 1,
          with: null,
        },
        gatewayServerApi: {
          num: 1,
          with: null,
        },
        portalWeb: {
          num: 1,
          with: null,
        },
        portalServer: {
          num: 1,
          with: null,
        },
        kafka: {
          num: 1,
          with: null,
        },
        nacos: {
          num: 1,
          with: null,
        },
        mysql: {
          num: 1,
          with: null,
        },
        tengine: {
          num: 1,
          with: null,
        },
        tengine1233: {
          num: 0,
          with: null,
        },
      })
    );
  }, []);

  const data = {
    host: [
      {
        ip: "10.0.14.234",
        num: 5,
      },
      {
        ip: "10.0.14.235",
        num: 5,
      },
      {
        ip: "10.0.14.230",
        num: 2,
      },
      {
        ip: "10.0.14.2301",
        num: 2,
      },
    ],
    //all: ,
    product: [
      {
        name: "douc",
        child: [
          "doucApi",
          "doucSso",
          "doucDubboRpc",
          "doucAdmin",
          "doucZabbixApi",
          "doucWeb",
          "doucAdminWeb",
          "gatewayServer",
          "gatewayServerApi",
          "portalWeb",
          "portalServer",
        ],
      },
      {
        name: "基础组件",
        child: ["kafka", "nacos", "mysql", "tengine", "tengine1233"],
      },
    ],
  };

  // 基本信息的form实例
  const [form] = Form.useForm();

  return (
    <>
      <div
        style={{
          marginTop: 20,
          backgroundColor: "#fff",
          padding: 10,
        }}
      >
        <div style={{ display: "flex" }}>
          <div
            style={{
              paddingLeft: 20,
              marginTop: 10,
              paddingBottom: 30,
            }}
          >
            主机总数: 20台
          </div>
          <div
            style={{
              paddingLeft: 40,
              marginTop: 10,
              paddingBottom: 30,
            }}
          >
            未分配服务: 62个
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
              />
            );
          })}
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
        <div style={{ paddingLeft: 20 }}>已分配主机数量: 0台</div>
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
            onClick={() => {
              //   console.log(basicForm.getFieldsValue());
              //   console.log(dependentForm.getFieldsValue());
              setStepNum(2);
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
