import img from "@/config/logo/logo.svg";
import styles from "./index.module.less";
import { LeftOutlined } from "@ant-design/icons";
import { Button, Select, Spin, Table } from "antd";
import { useEffect, useState } from "react";
import { fetchGet } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { useHistory, useLocation } from "react-router-dom";
import { handleResponse } from "@/utils/utils";

const AppStoreDetail = () => {
  const history = useHistory();
  const location = useLocation();
  let arr = location.pathname.split("/")
  let name = arr[arr.length-1]
  // true 是组件， false是组件
  let keyTab = location.pathname.includes("component");

//定义命名
let nameObj = {
  component:{
    logo:"app_logo",
    name:"app_name",
    version:"app_version",
    description:"app_description",
    instance_number:"instance_number",
  },
  service:{
    logo:"pro_logo",
    name:"pro_name",
    version:"pro_version",
    description:"pro_description",
    instance_number:"instance_number",
  }
}

  const [loading, setLoading] = useState(false);

  const [dataSource, setDataSource] = useState({});

  function fetchData() {
    setLoading(true);
    fetchGet(
      keyTab
        ? apiRequest.appStore.ProductDetail
        : apiRequest.appStore.ApplicationDetail,
        {
          params: {
            [keyTab?"app_name":"pro_name"]:name
          },
        }
    )
      .then((res) => {
        handleResponse(res, (res) => {});
      })
      .catch((e) => console.log(e))
      .finally(() => {
        // /location.state = {};
        setLoading(false);
      });
  }

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className={styles.detailContainer}>
      <Spin spinning={loading}>
        <div className={styles.detailHeader}>
          <div>
            <LeftOutlined
              style={{ fontSize: 16 }}
              className={styles.backIcon}
              onClick={() => {
                history?.push({
                  pathname: `/application_management/app_store`,
                });
              }}
            />{" "}
            <span style={{ paddingLeft: 20, fontSize: 16, color: "#4c4c4c" }}>
              tomcat
            </span>
          </div>
          <div style={{ marginRight: 30 }}>
            <Button style={{ marginRight: 20 }}>安装</Button>
            版本:{" "}
            <Select
              defaultValue="lucy"
              style={{ width: 160 }}
              //onChange={handleChange}
            >
              <Select.Option value="jack">Jack</Select.Option>
              <Select.Option value="lucy">Lucy</Select.Option>
              <Select.Option value="disabled" disabled>
                Disabled
              </Select.Option>
              <Select.Option value="Yiminghe">yiminghe</Select.Option>
            </Select>
          </div>
        </div>
        <div className={styles.detailTitle}>
          <div
            style={{
              width: 120,
              height: 80,
              // borderRadius: "50%",
              border: "1px solid #eaeaea",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              marginLeft: 10,
              marginRight: 10,
            }}
          >
            <img style={{ width: 40, height: 40 }} src={img} />
          </div>
          <div className={styles.detailTitleDescribe}>
            123123 2dnajdnas jkdb12312 32dnajdnasjkd bahjsfba hgvghvgh1 231232
            dnajdnasj kdbahjsfb ahgvghvg h1231232 dnajdnas jkdbahjsfbahg
            vghvgh123 1232dnaj dnasjkdbahj sfbahgvghv gh123123 2dnajdnasj
            kdbahjsfbahgv ghvgh123123 2dnajdnas jkdbahjsfbah gvghvgh1
            231232dnajdn asjkdbahjsfb ahgvghvgh123 1232dnajdn asjkdbahjs
            fbahgvghvgh ahjsfbah gvghvgh
          </div>
        </div>
        <div className={styles.detailContent}>
          <div className={styles.detailContentItem}>
            <div className={styles.detailContentItemLabel}>类别:</div>
            <div>自研组件</div>
          </div>
          <div className={styles.detailContentItem}>
            <div className={styles.detailContentItemLabel}>发布时间:</div>
            <div>2021-08-27 22:33:44</div>
          </div>
          <div className={styles.detailContentItem}>
            <div className={styles.detailContentItemLabel}>MD5:</div>
            <div>42925b30bdd19b099b777b94044c87d5</div>
          </div>
          <div className={styles.detailContentItem}>
            <div className={styles.detailContentItemLabel}>发布人:</div>
            <div>admin</div>
          </div>
        </div>
        <div  className={styles.detailDependence}>
          <div>依赖信息</div>
          <div className={styles.detailDependenceTable}>
            <Table 
              size="middle"
              columns={[
                {
                  title: "名称",
                  key: "name",
                  dataIndex: "name",
                  align: "center",
                },
                {
                  title: "版本",
                  key: "verson",
                  dataIndex: "verson",
                  align: "center",
                },
              ]}
              pagination={false}
              dataSource={[
                {
                  name:"jdk",
                  verson:"1.8",
                  key:"1.8"
                }
              ]}
            />
          </div>
        </div>
        <div  className={styles.detailDependence}>
          <div>实例信息 <span style={{paddingLeft:20,fontSize:14,color:"#1f8aee"}}>查看全部版本</span></div>
          <div className={styles.detailDependenceTable} style={{width:800}}>
            <Table 
              size="middle"
              columns={[
                {
                  title: "实例名称",
                  key: "name",
                  dataIndex: "name",
                  align: "center",
                },
                {
                  title: "主机IP",
                  key: "ip",
                  dataIndex: "ip",
                  align: "center",
                },
                {
                  title: "端口",
                  key: "port",
                  dataIndex: "port",
                  align: "center",
                },
                {
                  title: "版本",
                  key: "verson",
                  dataIndex: "verson",
                  align: "center",
                },
                {
                  title: "模式",
                  key: "mode",
                  dataIndex: "mode",
                  align: "center",
                },
                {
                  title: "安装时间",
                  key: "time",
                  dataIndex: "time",
                  align: "center",
                },
              ]}
              pagination={false}
              dataSource={[
                {
                  name:"jdk",
                  ip:"192.168.100.100",
                  port:"3306",
                  verson:"1.8",
                  mode:"单实例",
                  time:"2021-09-22 11:22:33",
                  key:"192.168.100.100",
                }
              ]}
            />
          </div>
        </div>
      </Spin>
    </div>
  );
};

export default AppStoreDetail;
