import BasicInfoItem from "../component/BasicInfoItem/index";
import DependentInfoItem from "../component/DependentinfoItem/index";
import { Form, Button } from "antd";
import { useEffect, useState } from "react";
import { fetchPost } from "@/utils/request";
import { useSelector, useDispatch } from "react-redux";

const Step1 = ({ setStepNum }) => {
  // const [basic, setBasic] = useState([])
  // const [dependence, setDependence] = useState([])
  const data = useSelector((state) => state.installation.step1Data);
  const reduxDispatch = useDispatch();

  const [loading, setLoading] = useState(false)

  const uniqueKey = useSelector((state) => state.appStore.uniqueKey);

  console.log(uniqueKey,"uniqueKey")

  // let data = { is_continue: true };
  // data.basic = [
  //   {
  //     name: "douc",
  //     version: "1.1",
  //     error_msg:
  //       "jenkinsService安装包不存在，请查看 /Users/jon/Desktop/github/omp_open/package_hub/verified/jenkins-2.303.2/jenkinsService-2.303.2-f342bb1437ee05cd39870323dc26c9fe.tar.gz",
  //     services_list: [
  //       {
  //         name: "doucApi",
  //         deploy_mode: {
  //           default: 1,
  //           step: 1,
  //         },
  //       },
  //       {
  //         name: "doucWeb",
  //         deploy_mode: {
  //           default: 1,
  //           step: 0,
  //         },
  //       },
  //       {
  //         name: "douc5Web",
  //         deploy_mode: {
  //           default: 1,
  //           step: 2,
  //         },
  //       },
  //       {
  //         name: "do4ucWeb",
  //         deploy_mode: {
  //           default: 2,
  //           step: 0,
  //         },
  //       },
  //       {
  //         name: "douc3Web",
  //         deploy_mode: {
  //           default: 4,
  //           step: 0,
  //         },
  //       },
  //       {
  //         name: "doucW2eb",
  //         deploy_mode: {
  //           default: 1,
  //           step: 0,
  //         },
  //       },
  //       {
  //         name: "doucWe1b",
  //         deploy_mode: {
  //           default: 1,
  //           step: 0,
  //         },
  //       },
  //       {
  //         name: "d123oucWe1b",
  //         deploy_mode: {
  //           default: 1,
  //           step: 0,
  //         },
  //       },
  //     ],
  //   },
  //   {
  //     name: "cmdb",
  //     version: "5.3",
  //     services_list: [
  //       {
  //         name: "doucApi333",
  //         deploy_mode: {
  //           default: 1,
  //           step: 1,
  //         },
  //       },
  //       {
  //         name: "doucWeb12",
  //         deploy_mode: {
  //           default: 1,
  //           step: 0,
  //         },
  //       },
  //     ],
  //   },
  // ];

  // data.dependence = [
  //   {
  //     name: "jdk",
  //     version: "8u211",
  //     exist_instance: [],
  //     error_msg:
  //       "/Users/jon/Desktop/github/omp_open/package_hub/verified/jdk-8u211-3eb087bb67353b4beb5230502f3ac9eb.tar.gz",
  //     is_base_env: true,
  //   },
  //   {
  //     name: "kafka",
  //     version: "2.2.2",
  //     exist_instance: [{ id: 1, name: "kafka-cluster-1", type: "cluster" }],
  //     deploy_mode: {
  //       default: 1,
  //       step: 2,
  //     },
  //     is_use_exist: true,
  //     is_base_env: false,
  //   },
  //   {
  //     name: "mysql",
  //     version: "5.7.34",
  //     deploy_mode: [
  //       //(无集群名称，无vip
  //       {
  //         key: "single",
  //         name: "单实例",
  //       },
  //       {
  //         key: "master-slave",
  //         name: "主从",
  //       },
  //       {
  //         //(选中此项要在集群名称后增加vip列(必填,ip地址校验)，请输入vip地址)
  //         key: "master-master",
  //         name: "主主",
  //       },
  //     ],
  //     exist_instance: [
  //       {
  //         id: 1,
  //         type: "instance",
  //         name: "mysql-instance-1",
  //       },
  //       {
  //         id: 2,
  //         type: "cluster",
  //         name: "mysql-cluster-1",
  //       },
  //     ],
  //     // 判断是否复用依赖，渲染时决定 选择实例 还是 部署数量
  //     is_use_exist: true,
  //     error_msg:
  //       "/Users/jon/Desktop/github/omp_open/package_hub/verified/jdk-8u211-3eb087bb67353b4beb5230502f3ac9eb.tar.gz",
  //   },
  //   {
  //     name: "nacos",
  //     version: "2.1.2",
  //     exist_instance: [{ id: 1, name: "kafka-cluster-1", type: "cluster" }],
  //     deploy_mode: {
  //       default: 3,
  //       step: 2,
  //     },
  //     is_use_exist: false,
  //     is_base_env: false,
  //   },
  //   {
  //     name: "nacosMock",
  //     version: "2.1.2",
  //     exist_instance: [{ id: 1, name: "kafka-cluster-1", type: "cluster" }],
  //     deploy_mode: [
  //       //(无集群名称，无vip
  //       {
  //         key: "single",
  //         name: "单实例",
  //       },
  //       {
  //         key: "master-slave",
  //         name: "主从",
  //       },
  //       {
  //         //(选中此项要在集群名称后增加vip列(必填,ip地址校验)，请输入vip地址)
  //         key: "master-master",
  //         name: "主主",
  //       },
  //     ],
  //     is_use_exist: false,
  //     is_base_env: false,
  //   },
  // ];

  // 基本信息的form实例
  const [basicForm] = Form.useForm();

  // 依赖信息的form实例
  const [dependentForm] = Form.useForm();

  const dataProcessing = () => {
    let formBasicData = basicForm.getFieldsValue();
    let formDependentData = dependentForm.getFieldsValue();;
    //setStepNum(1);
    let basic = JSON.parse(JSON.stringify(data.basic));
    let dependent = JSON.parse(JSON.stringify(data.dependence));

    basic = basic.map((item) => {
      let services_list = item.services_list;
      let cluster_name = "";

      Object.keys(formBasicData).map((k) => {
        let kArr = k.split("=");
        if (kArr.length == 1) {
          // 长度为1 说明当前key就是实例名称
          console.log(k, formBasicData[k]);
          if (k == item.name) {
            cluster_name = formBasicData[k];
          }
        } else if (kArr.length == 2) {
          services_list = services_list.map((i) => {
            console.log(i);
            if (i.name == kArr[1]) {
              return {
                name: i.name,
                version: i.version,
                deploy_mode: formBasicData[k],
              };
            } else {
              return {
                ...i,
              };
            }
          });
        }
      });
      return {
        name: item.name,
        version: item.version,
        cluster_name: cluster_name,
        services_list: services_list,
      };
    });

    dependent = dependent.map((item) => {
      if (item.is_base_env) {
        // jdk
        return {
          ...item,
        };
      } else {
        //if(item.is_use_exist){
        // deployInstanceRow
        let exist_instance = item.exist_instance;
        let deploy_mode = item.deploy_mode;
        let cluster_name = "";
        let vip = "";
        let is_use_exist = false;

        Object.keys(formDependentData).map((k) => {
          let kArr = k.split("=");
          if (kArr[0] == item.name) {
            if (kArr.length == 1) {
              // 选中了勾选了说明当前为选择实例信息
              exist_instance = JSON.parse(formDependentData[k]);
              is_use_exist = true;
            } else {
              // 取消了选中，当前为部署数量信息
              // 判断部署数量是否是数字
              if (kArr[1] == "num") {
                deploy_mode = formDependentData[k];
                cluster_name = formDependentData[`${item.name}=name`];
                vip = formDependentData[`${item.name}=vip`];
                // if(isNaN(Number(formDependentData[k]))){
                //   // 非数字代表单实例，主从，主主
                //   console.log("主从主主",item.name,k)

                // }else{
                //   // 数字代表部署数量
                //   console.log("数字",item.name)
                //   // 数量
                //   //cluster_name
                // }
              }
            }
          }
        });

        return {
          ...item,
          exist_instance: exist_instance,
          deploy_mode: deploy_mode,
          cluster_name: cluster_name,
          vip: vip,
          is_use_exist: is_use_exist,
        };
      }

      return {
        ...item,
      };
    });

    return {
      basic: basic,
      dependence: dependent
    }
  };

  // checkInstallInfo 基本信息提交操作，决定是否跳转服务分布以及数据校验回显
  const checkInstallInfo = (data) => {
    console.log(uniqueKey,data)
    return 
    setLoading(true);
    fetchPost(apiRequest.appStore.checkInstallInfo, {
      body: {

        ...data
      },
    })
      .then((res) => {
        //console.log(operateObj[operateAciton])
        handleResponse(res, (res) => {
          
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

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
            {data.basic.map((item) => {
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
            {data.dependence.map((item) => {
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
          boxShadow: "0px 0px 10px #999999",
        }}
      >
        <div />
        <div>
          <Button
            type="primary"
            loading={loading}
            disabled={!data.is_continue}
            onClick={() => {
              console.log(dataProcessing())
              checkInstallInfo(dataProcessing())
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
