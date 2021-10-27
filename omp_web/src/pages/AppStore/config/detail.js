import img from "@/config/logo/logo.svg";
import styles from "./index.module.less";
import { LeftOutlined } from "@ant-design/icons";
import { Button, Select, Spin, Table } from "antd";
import { useEffect, useState } from "react";
import { fetchGet } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { useHistory, useLocation } from "react-router-dom";
import { handleResponse } from "@/utils/utils";
import imgObj from "./img";
import moment from "moment";
import { getTabKeyChangeAction } from "../store/actionsCreators";
import { useDispatch } from "react-redux";

const AppStoreDetail = () => {
  const dispatch = useDispatch();
  const history = useHistory();
  const location = useLocation();
  let arr = location.pathname.split("/");
  let name = arr[arr.length - 2];
  let verson = arr[arr.length - 1];
  // true 是组件， false是服务
  let keyTab = location.pathname.includes("component");

  //定义命名
  let nameObj = keyTab
    ? {
        logo: "app_logo",
        name: "app_name",
        version: "app_version",
        description: "app_description",
        instance_number: "instance_number",
        package_md5: "app_package_md5",
        type: "app_labels",
        user: "app_operation_user",
        dependence: "app_dependence",
      }
    : {
        logo: "pro_logo",
        name: "pro_name",
        version: "pro_version",
        description: "pro_description",
        instance_number: "instance_number",
        package_md5: "pro_package_md5",
        type: "pro_labels",
        user: "pro_operation_user",
        dependence: "pro_dependence",
        pro_services: "pro_services",
      };

  const [loading, setLoading] = useState(false);

  const [dataSource, setDataSource] = useState({});

  const [versionValue, setVersionValue] = useState("");

  function fetchData() {
    setLoading(true);
    fetchGet(
      keyTab
        ? apiRequest.appStore.ProductDetail
        : apiRequest.appStore.ApplicationDetail,
      {
        params: {
          [keyTab ? "app_name" : "pro_name"]: name,
        },
      }
    )
      .then((res) => {
        handleResponse(res, (res) => {
          setVersionValue(verson);
          setDataSource(() => {
            let obj = {};
            res.data.versions.map((item) => {
              obj[item[nameObj.version]] = item;
            });
            return {
              ...res.data,
              versionObj: obj,
            };
          });
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  }

  let currentVersionDataSource = dataSource.versionObj
    ? dataSource.versionObj[versionValue]
    : {};

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
                keyTab
                  ? dispatch(getTabKeyChangeAction("component"))
                  : dispatch(getTabKeyChangeAction("service"));
                history?.push({
                  pathname: `/application_management/app_store`,
                });
              }}
            />
            {" "}
            <span style={{ paddingLeft: 20, fontSize: 16, color: "#4c4c4c" }}>
              {dataSource[nameObj.name]}
            </span>
          </div>
          <div style={{ marginRight: 30 }}>
            <Button style={{ marginRight: 20 }}>安装</Button>
            版本:{" "}
            <Select
              style={{ width: 160 }}
              value={versionValue}
              onChange={(e) => {
                setVersionValue(e);
              }}
            >
              {dataSource.versionObj &&
                Object.keys(dataSource?.versionObj).map((item) => {
                  return (
                    <Select.Option key={item} value={item}>
                      {item}
                    </Select.Option>
                  );
                })}
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
              overflow: "hidden",
              padding: 10,
            }}
          >
            <div
              style={{
                width: 80,
                height: 80,
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
              }}
              dangerouslySetInnerHTML={{
                __html:
                  currentVersionDataSource[nameObj.logo] ||
                  imgObj[keyTab ? "component" : "service"],
              }}
            ></div>
          </div>
          <div className={styles.detailTitleDescribe}>
            {currentVersionDataSource[nameObj.description]}
          </div>
        </div>
        <div className={styles.detailContent}>
          <div className={styles.detailContentItem}>
            <div className={styles.detailContentItemLabel}>类别:</div>
            <div>{currentVersionDataSource[nameObj.type]?.join(",")}</div>
          </div>
          <div className={styles.detailContentItem}>
            <div className={styles.detailContentItemLabel}>发布时间:</div>
            <div>
              {moment(currentVersionDataSource?.created).format(
                "YYYY-MM-DD HH:mm:ss"
              )}
            </div>
          </div>
          <div className={styles.detailContentItem}>
            <div className={styles.detailContentItemLabel}>MD5:</div>
            <div>{currentVersionDataSource[nameObj.package_md5]}</div>
          </div>
          <div className={styles.detailContentItem}>
            <div className={styles.detailContentItemLabel}>发布人:</div>
            <div>{currentVersionDataSource[nameObj.user]}</div>
          </div>
        </div>
        <div className={styles.detailDependence}>
          <div>依赖信息</div>
          {currentVersionDataSource[nameObj.dependence] ? (
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
                    key: "version",
                    dataIndex: "version",
                    align: "center",
                  },
                ]}
                pagination={false}
                dataSource={JSON.parse(
                  currentVersionDataSource[nameObj.dependence]
                )}
              />
            </div>
          ) : (
            <p style={{ paddingTop: 10 }}>无</p>
          )}
        </div>
        {!keyTab && (
          <div className={styles.detailDependence}>
            <div>包含服务</div>
            {currentVersionDataSource.pro_services ? (
              <div className={styles.detailDependenceTable} style={{width:800}}>
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
                      key: "version",
                      dataIndex: "version",
                      align: "center",
                    },
                    {
                      title: "MD5",
                      key: "md5",
                      dataIndex: "md5",
                      align: "center",
                    },
                    {
                      title: "发布时间",
                      key: "created",
                      dataIndex: "created",
                      align: "center",
                    },
                  ]}
                  pagination={false}
                  dataSource={currentVersionDataSource.pro_services}
                />
              </div>
            ) : (
              <p style={{ paddingTop: 10 }}>无</p>
            )}
          </div>
        )}

        {/* <div className={styles.detailDependence}>
          <div>
            实例信息{" "}
            <span style={{ paddingLeft: 20, fontSize: 14, color: "#1f8aee" }}>
              查看全部版本
            </span>
          </div>
          <div className={styles.detailDependenceTable} style={{ width: 800 }}>
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
                  name: "jdk",
                  ip: "192.168.100.100",
                  port: "3306",
                  verson: "1.8",
                  mode: "单实例",
                  time: "2021-09-22 11:22:33",
                  key: "192.168.100.100",
                },
              ]}
            />
          </div>
        </div> */}
      </Spin>
    </div>
  );
};

export default AppStoreDetail;
