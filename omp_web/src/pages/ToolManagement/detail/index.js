import {
  OmpContentWrapper,
  OmpTable,
  OmpMessageModal,
  OmpSelect,
  OmpDatePicker,
  OmpDrawer,
} from "@/components";
import {
  Button,
  Select,
  message,
  Menu,
  Dropdown,
  Modal,
  Input,
  Table,
  Tooltip,
  Spin,
} from "antd";
import { useState, useEffect, useRef } from "react";
import {
  handleResponse,
  _idxInit,
  refreshTime,
  downloadFile,
} from "@/utils/utils";
import { fetchGet, fetchPost, fetchPatch } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { QuestionCircleOutlined, FileProtectOutlined } from "@ant-design/icons";
import moment from "moment";
import { useHistory, useLocation } from "react-router-dom";
import styles from "./index.module.less";
import Readme from "./Readme.js";

const kindMap = ["管理工具", "检查工具", "安全工具", "其他工具"];

const argType = {
  select: "单选",
  file: "文件",
  input: "单行文本",
};

const Details = () => {
  const history = useHistory();
  const [loading, setLoading] = useState(false);
  // console.log([...location].pop())
  // let href = window.location.href.split("#")[0];
  const locationArr = useLocation().pathname.split("/");

  const [info, setInfo] = useState({});

  const queryInfo = () => {
    setLoading(true);
    fetchGet(
      `${apiRequest.utilitie.queryList}${locationArr[locationArr.length - 1]}/`
    )
      .then((res) => {
        handleResponse(res, (res) => {
          setInfo(res.data);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    queryInfo();
  }, []);

  return (
    <OmpContentWrapper wrapperStyle={{ padding: "20px 30px" }}>
      <Spin spinning={loading}>
        <div className={styles.header}>
          {info.logo == "logo.svg" ? (
            <div className={styles.icon}>
              {" "}
              <InitLogo name={info.name} />
            </div>
          ) : (
            <div className={styles.icon}>
              <div
                style={{
                  width: 80,
                  height: 80,
                  // borderRadius: "50%",
                  // border: "1px solid #a8d0f8",
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  // marginLeft: 10,
                  // marginRight: 10,
                  overflow: "hidden",
                  fontSize: 22,
                  // backgroundImage: "linear-gradient(to right, #4f85f6, #669aee)",
                  backgroundColor: "#f5f5f5",
                  color: "#fff",
                }}
              >
                <div
                  style={{
                    textAlign: "center",
                    position: "relative",
                    display: "flex",
                    alignItems: "center",
                  }}
                >
                  {/* {info.name && info.name[0].toLocaleUpperCase()} */}
                  <img
                    style={{
                      width: "65px",
                      height: "65px",
                      position: "relative",
                      top: 1,
                    }}
                    src={`${info.logo}`}
                  />
                </div>
              </div>
            </div>
          )}
          <div className={styles.headerContent}>
            <div className={styles.headerContentTitle}>{info.name}</div>
            <div className={styles.headerContentDescribe}>
              {info.description}
            </div>
            <div className={styles.headerContentBtn}>
              <Button
                style={{ padding: "3px 20px", height: 30 }}
                type="primary"
                onClick={() => {
                  history?.push({
                    pathname: `/utilitie/tool-management/tool-execution/${
                      locationArr[locationArr.length - 1]
                    }`,
                  });
                }}
              >
                执行
              </Button>
              <Button
                style={{ padding: "3px 20px", height: 30, marginLeft: 20 }}
                onClick={() => {
                  downloadFile(`/${info.tar_url}`);
                }}
              >
                下载
              </Button>
            </div>
          </div>
          <div className={styles.headerBtn}>
            <Button
              style={{ padding: "3px 20px", height: 30 }}
              onClick={() => {
                history?.goBack();
              }}
            >
              返回
            </Button>
          </div>
        </div>
        <div className={styles.detailInfo}>
          <div className={styles.detailItem}>
            <div className={styles.detailItemLabel}>工具类别</div>
            <div>{kindMap[info.kind]}</div>
          </div>
          {/* <div className={styles.detailItem}>
          <div className={styles.detailItemLabel}>
            执行位置
            <Tooltip placement="right" title={"提示信息"}>
              <QuestionCircleOutlined
                style={{
                  marginLeft: 10,
                  fontSize: 16,
                  position: "relative",
                  top: 1,
                }}
              />
            </Tooltip>
          </div>
          <div>目标主机</div>
        </div> */}
          <div className={styles.detailItem} style={{ paddingBottom: 10 }}>
            <div className={styles.detailItemLabel}>
              执行对象
              <Tooltip
                placement="right"
                title={"实用工具操作的目标对象类型，可以是主机或者具体服务"}
              >
                <QuestionCircleOutlined
                  style={{
                    marginLeft: 10,
                    fontSize: 16,
                    position: "relative",
                    top: 1,
                  }}
                />
              </Tooltip>
            </div>
            <div>{info.target_name == "host" ? "主机" : info.target_name}</div>
          </div>
        </div>
        <div className={styles.detailContent}>
          <div className={styles.detailContentTitle}>执行参数</div>
          <div className={styles.tableContainer}>
            <Table
              size="middle"
              columns={[
                {
                  title: "名称",
                  key: "name",
                  dataIndex: "name",
                  align: "center",
                  render: (text) => text || "-",
                },
                {
                  title: "类型",
                  key: "type",
                  dataIndex: "type",
                  align: "center",
                  render: (text) => (text ? argType[text] : "-"),
                },
                {
                  title: "默认值",
                  key: "default",
                  dataIndex: "default",
                  align: "center",
                  render: (text) => text || "-",
                },
                {
                  title: "必填字段",
                  key: "required",
                  dataIndex: "required",
                  align: "center",
                  render: (text) => `${text}`,
                },
              ]}
              pagination={false}
              dataSource={info.script_args}
            />
          </div>
        </div>
        {info && info.templates && info.templates.length > 0 && (
          <div className={styles.detailContent}>
            <div className={styles.detailContentTitle}>下载示例文件</div>
            <div className={styles.tableContainer}>
              <Table
                size="middle"
                columns={[
                  {
                    title: "名称",
                    key: "name",
                    dataIndex: "name",
                    align: "center",
                    width: 300,
                  },
                  {
                    title: "操作",
                    key: "sub_url",
                    dataIndex: "sub_url",
                    align: "center",
                    width: 100,
                    render: (text) => {
                      return (
                        <a
                          onClick={() => {
                            downloadFile(`/${text}`);
                          }}
                        >
                          下载
                        </a>
                      );
                    },
                  },
                ]}
                pagination={false}
                dataSource={info.templates}
              />
            </div>
          </div>
        )}

        <div className={styles.readme}>
          <div className={styles.readmeTitle}>
            <FileProtectOutlined style={{ fontSize: 16, marginRight: 10 }} />
            <span style={{ color: "rgb(34, 34, 34)" }}>README.md</span>
          </div>
          <div className={styles.readmeContent}>
            <Readme text={info.readme_info} />
          </div>
        </div>
      </Spin>
    </OmpContentWrapper>
  );
};

const InitLogo = ({ name }) => {
  return (
    <div
      style={{
        width: 80,
        height: 80,
        borderRadius: "50%",
        border: "1px solid #a8d0f8",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        // marginLeft: 10,
        // marginRight: 10,
        overflow: "hidden",
        fontSize: 32,
        backgroundImage: "linear-gradient(to right, #4f85f6, #669aee)",
        backgroundColor: "#f5f5f5",
        color: "#fff",
      }}
    >
      <div
        style={{
          textAlign: "center",
          position: "relative",
          display: "flex",
          alignItems: "center",
        }}
      >
        {name && name[0].toLocaleUpperCase()}
      </div>
    </div>
  );
};

export default Details;
