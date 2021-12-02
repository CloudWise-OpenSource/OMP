import { Button, Anchor, Spin, Progress } from "antd";
import { useSelector } from "react-redux";
import InstallInfoItem from "../component/InstallInfoItem";
import { useEffect, useRef, useState } from "react";
import { LoadingOutlined } from "@ant-design/icons";
import { apiRequest } from "@/config/requestApi";
import { fetchGet } from "@/utils/request";
import { handleResponse } from "@/utils/utils";
import { useHistory, useLocation } from "react-router-dom";
import { fetchPost } from "src/utils/request";

const { Link } = Anchor;
// 状态渲染规则
const renderStatus = {
  0: "等待安装",
  1: "正在安装",
  2: "安装成功",
  3: "安装失败",
};

const Step4 = () => {
  const history = useHistory();
  const viewHeight = useSelector((state) => state.layouts.viewSize.height);
  const [openName, setOpenName] = useState("");
  // 在轮训时使用ref存值
  const openNameRef = useRef(null);
  const location = useLocation();
  const defaultUniqueKey = location.state?.uniqueKey;
  const uniqueKey = useSelector((state) => state.appStore.uniqueKey);

  const [loading, setLoading] = useState(true);

  const [retryLoading, setRetryLoading] = useState(false);

  const [data, setData] = useState({
    detail: {},
    status: 0,
  });

  const [log, setLog] = useState("");

  // 轮训的timer控制器
  const timer = useRef(null);

  const queryInstallProcess = () => {
    !timer.current && setLoading(true);
    fetchGet(apiRequest.appStore.queryInstallProcess, {
      params: {
        unique_key: defaultUniqueKey || uniqueKey,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          setData(res.data);
          if (res.data.status == 0 || res.data.status == 1) {
            // 状态为未安装或者安装中
            if (openNameRef.current) {
              let arr = openNameRef.current.split("=");
              queryDetailInfo(defaultUniqueKey || uniqueKey, arr[1], arr[0]);
            }

            timer.current = setTimeout(() => {
              queryInstallProcess();
            }, 5000);
          } else {
            if (openNameRef.current) {
              let arr = openNameRef.current.split("=");
              queryDetailInfo(defaultUniqueKey || uniqueKey, arr[1], arr[0]);
            }
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  // 请求详细信息
  const queryDetailInfo = (uniqueKey, ip, app_name) => {
    fetchGet(apiRequest.appStore.showSingleServiceInstallLog, {
      params: {
        unique_key: uniqueKey,
        app_name: app_name,
        ip: ip,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          setLog(res.data.log);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        //setLoading(false);
      });
  };

  const retryInstall = () => {
    setRetryLoading(true);
    setOpenName("");
    openNameRef.current = "";
    fetchPost(apiRequest.appStore.retryInstall, {
      body: {
        unique_key: defaultUniqueKey || uniqueKey,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.code == 0) {
            queryInstallProcess();
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setRetryLoading(false);
      });
  };

  useEffect(() => {
    queryInstallProcess();
    return () => {
      // 页面销毁时清除延时器
      clearTimeout(timer.current);
    };
  }, []);

  return (
    <div>
      <div
        style={{
          display: "flex",
          paddingTop: 20,
        }}
      >
        <Spin spinning={loading}>
          <div
            id="Step4Wrapper"
            style={{
              flex: 1,
              //backgroundColor: "#fff",
              height: viewHeight - 270,
              overflowY: "auto",
            }}
          >
            <div style={{}}>
              {Object.keys(data.detail).map((key, idx) => {
                return (
                  <InstallInfoItem
                    openName={openName}
                    setOpenName={(n) => {
                      setLog("");
                      if (n) {
                        let arr = n.split("=");
                        queryDetailInfo(
                          defaultUniqueKey || uniqueKey,
                          arr[1],
                          arr[0]
                        );
                      }
                      // console.log(n);
                      // queryDetailInfo(uniqueKey, arr[1], arr[0]);
                      setOpenName(n);
                      openNameRef.current = n;
                    }}
                    id={`a${key}`}
                    key={key}
                    title={key}
                    data={data.detail[key]}
                    log={log}
                    idx={idx}
                  />
                );
              })}
            </div>
          </div>
        </Spin>

        <div
          style={{
            //height: 300,
            width: 200,
            backgroundColor: "#fff",
            marginLeft: 20,
            height: viewHeight - 270,
            overflowY: "auto",
            paddingTop: 10,
          }}
        >
          <div style={{ paddingLeft: 5 }}>
            <Anchor
              style={{}}
              affix={false}
              getContainer={() => {
                let con = document.getElementById("Step4Wrapper");
                return con;
              }}
              onClick={(e) => {
                e.preventDefault();
              }}
            >
              {Object.keys(data.detail).map((key) => {
                return (
                  <div style={{ padding: 5 }}>
                    <Link href={`#a${key}`} title={key} />
                  </div>
                );
              })}
            </Anchor>
          </div>
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
        <div style={{ paddingLeft: 20, display: "flex" }}>
          <div style={{ width: 100 }}>
            {renderStatus[data.status]}
            {(data.status == 0 || data.status == 1) && (
              <LoadingOutlined style={{ marginLeft: 10, fontWeight: 600 }} />
            )}
          </div>
        </div>
        <div style={{ width: "70%" }}>
          <Progress percent={data.percentage} status={data.status == 3 && "exception"}/>
        </div>
        <div style={{paddingLeft:60}}>
          {data.status == 3 && (
            <Button
              loading={retryLoading}
              style={{ marginLeft: 10 }}
              type="primary"
              //disabled={unassignedServices !== 0}
              onClick={() => {
                retryInstall();
              }}
            >
              重试
            </Button>
          )}

          <Button
            style={{ marginLeft: 10 }}
            type="primary"
            //disabled={unassignedServices !== 0}
            onClick={() => {
              history?.push("/application_management/install-record");
            }}
          >
            完成
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Step4;
