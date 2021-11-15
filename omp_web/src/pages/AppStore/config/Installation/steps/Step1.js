import BasicInfoItem from "../component/BasicInfoItem/index";
import DependentInfoItem from "../component/DependentinfoItem/index";
import { Form, Button } from "antd";

const Step1 = () => {
  const basic = [
    {
      name: "douc",
      version: "1.1",
      error_msg:
        "jenkinsService安装包不存在，请查看 /Users/jon/Desktop/github/omp_open/package_hub/verified/jenkins-2.303.2/jenkinsService-2.303.2-f342bb1437ee05cd39870323dc26c9fe.tar.gz",
      services_list: [
        {
          name: "doucApi",
          deploy_mode: {
            default: 1,
            step: 1,
          },
        },
        {
          name: "doucWeb",
          deploy_mode: {
            default: 1,
            step: 0,
          },
        },
        {
          name: "douc5Web",
          deploy_mode: {
            default: 1,
            step: 2,
          },
        },
        {
          name: "do4ucWeb",
          deploy_mode: {
            default: 2,
            step: 0,
          },
        },
        {
          name: "douc3Web",
          deploy_mode: {
            default: 4,
            step: 0,
          },
        },
        {
          name: "doucW2eb",
          deploy_mode: {
            default: 1,
            step: 0,
          },
        },
        {
          name: "doucWe1b",
          deploy_mode: {
            default: 1,
            step: 0,
          },
        },
        {
          name: "d123oucWe1b",
          deploy_mode: {
            default: 1,
            step: 0,
          },
        },
      ],
    },
    {
      name: "cmdb",
      version: "5.3",
      services_list: [
        {
          name: "doucApi333",
          deploy_mode: {
            default: 1,
            step: 1,
          },
        },
        {
          name: "doucWeb12",
          deploy_mode: {
            default: 1,
            step: 0,
          },
        },
      ],
    },
  ];

  const dependence = [
    {
      name: "jdk",
      version: "8u211",
      exist_instance: [],
      error_msg:
        "/Users/jon/Desktop/github/omp_open/package_hub/verified/jdk-8u211-3eb087bb67353b4beb5230502f3ac9eb.tar.gz",
      is_base_env: true,
    },
    {
      name: "kafka",
      version: "2.2.2",
      exist_instance: [{ id: 1, name: "kafka-cluster-1", type: "cluster" }],
      deploy_mode: {
        default: 1,
        step: 2,
      },
      is_use_exist: true,
      is_base_env: false,
    },
    {
      name: "mysql",
      version: "5.7.34",
      deploy_mode: [
        {
          key: "single",
          name: "单实例(无集群名称，无vip)",
        },
        {
          key: "master-slave",
          name: "主从",
        },
        {
          key: "master-master",
          name: "主主(选中此项要在集群名称后增加vip列(必填,ip地址校验)，请输入vip地址)",
        },
      ],
      exist_instance: [
        {
          id: 1,
          type: "instance",
          name: "mysql-instance-1",
        },
        {
          id: 2,
          type: "cluster",
          name: "mysql-cluster-1",
        },
      ],
      // 判断是否复用依赖，渲染时决定 选择实例 还是 部署数量
      is_use_exist: true,
    },
    {
      name: "nacos",
      version: "2.1.2",
      exist_instance: [{ id: 1, name: "kafka-cluster-1", type: "cluster" }],
      deploy_mode: {
        default: 3,
        step: 2,
      },
      is_use_exist: false,
      is_base_env: false,
    },
  ];

  // 基本信息的form实例
  const [basicForm] = Form.useForm();

  // 依赖信息的form实例
  const [dependentForm] = Form.useForm();

  return (
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
        <div
          style={{
            paddingLeft: 20,
            marginTop: 10,
            paddingBottom: 40,
            // paddingTop: 20,
          }}
        >
          <Form form={basicForm} name="basic">
            {basic.map((item) => {
              return (
                <BasicInfoItem key={item.name} form={basicForm} data={item} />
              );
            })}
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
            // paddingTop: 20,
          }}
        >
          <Form form={dependentForm} name="dependent" layout="vertical">
            {dependence.map((item) => {
              return (
                <DependentInfoItem
                  key={item.name}
                  form={dependentForm}
                  data={item}
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
          boxShadow: "0px 0px 10px #999999"
        }}
      >
        <div />
        <div>
          <Button
            type="primary"
            onClick={() => {
              console.log(basicForm.getFieldsValue());
              console.log(dependentForm.getFieldsValue());
            }}
          >
            下一步
          </Button>
        </div>
      </div>
    </>
  );
};

export default Step1;
