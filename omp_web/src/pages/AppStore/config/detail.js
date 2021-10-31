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
        instances_info: "app_instances_info",
        install_url:"/application_management/app_store/component_installation",
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
        instances_info: "pro_instances_info",
        install_url:"/application_management/app_store/application_installation",
      };

  const [loading, setLoading] = useState(false);

  const [dataSource, setDataSource] = useState({});

  const [versionValue, setVersionValue] = useState("");

  // 定义全部实例信息
  const [allInstancesInfo, setAllInstancesInfo] = useState([]);

  // 是否查看全部版本
  const [isAll, setIsAll] = useState(false);

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

          setAllInstancesInfo(() => {
            return res.data.versions
              .map((item) => {
                return item[nameObj.instances_info];
              })
              .flat();
          });

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
            />{" "}
            <span style={{ paddingLeft: 20, fontSize: 16, color: "#4c4c4c" }}>
              {dataSource[nameObj.name]}
            </span>
          </div>
          <div style={{ marginRight: 30 }}>
            <Button style={{ marginRight: 20 }}
            onClick={()=>{
              history?.push({
                pathname: `${nameObj.install_url}/${
                  dataSource[nameObj.name]
                }`,
              });
            }}
            >安装</Button>
            版本:{" "}
            <Select
              style={{ width: 160 }}
              value={versionValue}
              onChange={(e) => {
                setIsAll(false);
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
              <div
                className={styles.detailDependenceTable}
                style={{ width: 800 }}
              >
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
                      render: (text) => {
                        return text || "-";
                      },
                    },
                    {
                      title: "MD5",
                      key: "md5",
                      dataIndex: "md5",
                      align: "center",
                      render: (text) => {
                        return text || "-";
                      },
                    },
                    {
                      title: "发布时间",
                      key: "created",
                      dataIndex: "created",
                      align: "center",
                      render: (text) => {
                        return text || "-";
                      },
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
        {keyTab ? (
          <div className={styles.detailDependence}>
            <div>
              实例信息
              <span style={{ paddingLeft: 20, fontSize: 14, color: "#1f8aee" }}>
                {isAll ? (
                  <span
                  style={{ cursor: "pointer" }}
                  onClick={() => {
                    setIsAll(false);
                  }}
                >
                  查看当前版本
                </span>
                ) : (
                  <span
                    style={{ cursor: "pointer" }}
                    onClick={() => {
                      setIsAll(true);
                    }}
                  >
                    查看全部版本
                  </span>
                )}
              </span>
            </div>
            <div
              className={styles.detailDependenceTable}
              style={{ width: 800 }}
            >
              <Table
                size="middle"
                columns={[
                  {
                    title: "实例名称",
                    key: "instance_name",
                    dataIndex: "instance_name",
                    align: "center",
                  },
                  {
                    title: "主机IP",
                    key: "host_ip",
                    dataIndex: "host_ip",
                    align: "center",
                  },
                  {
                    title: "端口",
                    key: "service_port",
                    dataIndex: "service_port",
                    align: "center",
                    render: (text) => {
                      if (!text) {
                        return "-";
                      }
                      return text.map((i) => i.default).join(", ");
                    },
                  },
                  {
                    title: "版本",
                    key: "app_version",
                    dataIndex: "app_version",
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
                    key: "created",
                    dataIndex: "created",
                    align: "center",
                    render: (text) => {
                      return moment(text).format("YYYY-MM-DD HH:mm:ss");
                    },
                  },
                ]}
                //pagination={false}
                dataSource={
                  isAll
                    ? allInstancesInfo
                    : currentVersionDataSource[nameObj.instances_info]
                }
              />
            </div>
          </div>
        ) : (
          <div className={styles.detailDependence}>
            <div>
              实例信息
              <span style={{ paddingLeft: 20, fontSize: 14, color: "#1f8aee" }}>
                {isAll ? (
                  <span
                  style={{ cursor: "pointer" }}
                  onClick={() => {
                    setIsAll(false);
                  }}
                >
                  查看当前版本
                </span>
                ) : (
                  <span
                    style={{ cursor: "pointer" }}
                    onClick={() => {
                      setIsAll(true);
                    }}
                  >
                    查看全部版本
                  </span>
                )}
              </span>
            </div>
            <div
              className={styles.detailDependenceTable}
              style={{ width: 800 }}
            >
              <Table
                size="middle"
                columns={[
                  {
                    title: "实例名称",
                    key: "instance_name",
                    dataIndex: "instance_name",
                    align: "center",
                  },
                  {
                    title: "版本",
                    key: "version",
                    dataIndex: "version",
                    align: "center",
                  },
                  {
                    title: "服务名称",
                    key: "app_name",
                    dataIndex: "app_name",
                    align: "center",
                  },
                  {
                    title: "服务版本",
                    key: "app_version",
                    dataIndex: "app_version",
                    align: "center",
                  },
                  {
                    title: "主机IP",
                    key: "host_ip",
                    dataIndex: "host_ip",
                    align: "center",
                  },
                  {
                    title: "端口",
                    key: "service_port",
                    dataIndex: "service_port",
                    align: "center",
                    render: (text) => {
                      if (!text) {
                        return "-";
                      }
                      return text.map((i) => i.default).join(",");
                    },
                  },
                  {
                    title: "安装时间",
                    key: "created",
                    dataIndex: "created",
                    align: "center",
                    render: (text) => {
                      return moment(text).format("YYYY-MM-DD HH:mm:ss");
                    },
                  },
                ]}
                //pagination={false}
                dataSource={
                  isAll
                    ? allInstancesInfo
                    : currentVersionDataSource[nameObj.instances_info]
                }
              />
            </div>
          </div>
        )}
      </Spin>
    </div>
  );
};

export default AppStoreDetail;
