import { Button, Anchor, Spin, Progress } from "antd";
import { useSelector } from "react-redux";
import UpgradeInfoItem from "./component/UpgradeInfoItem";
import { useEffect, useRef, useState } from "react";
import { LoadingOutlined } from "@ant-design/icons";
import { apiRequest } from "@/config/requestApi";
import { fetchGet } from "@/utils/request";
import { handleResponse } from "@/utils/utils";
import { useHistory, useLocation } from "react-router-dom";
import { fetchPut } from "src/utils/request";
import ServiceRollbackModal from "../../ServiceRollbackModal";

const { Link } = Anchor;
// 状态渲染规则
const renderStatus = {
  0: "等待升级",
  1: "正在升级",
  2: "升级成功",
  3: "升级失败",
  4: "正在注册",
};

const Content = () => {
  const history = useHistory();
  const viewHeight = useSelector((state) => state.layouts.viewSize.height);
  // 在轮训时使用ref存值
  const openNameRef = useRef(null);
  const location = useLocation();
  console.log(location?.state?.history);

  const [loading, setLoading] = useState(true);

  const [retryLoading, setRetryLoading] = useState(false);

  const [data, setData] = useState({
    detail: {},
    upgrade_state: 0,
  });

  // 轮训的timer控制器
  const timer = useRef(null);

  const [vfModalVisibility, setVfModalVisibility] = useState(false);
  const [rowId, setRowId] = useState("");

  const queryUpgradeProcess = () => {
    !timer.current && setLoading(true);
    fetchGet(
      `${apiRequest.appStore.queryUpgradeProcess}/${location?.state?.history}`
    )
      .then((res) => {
        handleResponse(res, (res) => {
          setData(res.data);
          if (
            res.data.upgrade_state == 0 ||
            res.data.upgrade_state == 1 ||
            res.data.upgrade_state == 4
          ) {
            // 状态为未安装或者安装中
            timer.current = setTimeout(() => {
              queryUpgradeProcess();
            }, 5000);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  const retryUpgrade = () => {
    setRetryLoading(true);
    fetchPut(
      `${apiRequest.appStore.queryUpgradeProcess}/${location?.state?.history}`
    )
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.code == 0) {
            queryUpgradeProcess();
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setRetryLoading(false);
      });
  };

  useEffect(() => {
    queryUpgradeProcess();
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
            <div>
              {data?.upgrade_detail?.map((item, idx) => {
                return (
                  <UpgradeInfoItem
                    id={`a${idx}`}
                    key={idx}
                    title={item.service_name}
                    data={item.upgrade_details}
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
              {data?.upgrade_detail?.map((item, idx) => {
                let hasError =
                  item.upgrade_details.filter((a) => a.upgrade_state == 3)
                    .length !== 0;
                return (
                  <div style={{ padding: 5 }} key={idx}>
                    <Link
                      href={`#a${idx}`}
                      title={
                        <span style={{ color: hasError && "rgb(218, 78, 72)" }}>
                          {item.service_name}
                        </span>
                      }
                    />
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
            {renderStatus[data.upgrade_state]}
            {(data.upgrade_state == 0 ||
              data.upgrade_state == 1 ||
              data.upgrade_state == 4) && (
              <LoadingOutlined style={{ marginLeft: 10, fontWeight: 600 }} />
            )}
          </div>
        </div>
        <div style={{ width: "70%" }}>
          <Progress
            percent={((data.success_count / data.all_count) * 100).toFixed()}
            status={data.upgrade_state == 3 && "exception"}
          />
        </div>
        <div style={{ paddingLeft: 60 }}>
          {data.upgrade_state == 3 && (
            <>
              <Button
                loading={retryLoading}
                style={{ marginLeft: 10 }}
                type="primary"
                //disabled={unassignedServices !== 0}
                onClick={() => {
                  setRowId(location?.state?.history);
                  // retryUpgrade();
                  setVfModalVisibility(true)
                }}
              >
                回滚
              </Button>
              <Button
                loading={retryLoading}
                style={{ marginLeft: 10 }}
                type="primary"
                //disabled={unassignedServices !== 0}
                onClick={() => {
                  retryUpgrade();
                }}
              >
                重试
              </Button>
            </>
          )}

          <Button
            style={{ marginLeft: 10 }}
            type="primary"
            //disabled={unassignedServices !== 0}
            onClick={() => {
              history.push({
                pathname: "/application_management/install-record",
                state: {
                  tabKey: "upgrade",
                },
              });
            }}
          >
            完成
          </Button>
        </div>
      </div>
      <ServiceRollbackModal
        sRModalVisibility={vfModalVisibility}
        setSRModalVisibility={setVfModalVisibility}
        initLoading={retryLoading}
        fixedParams={`?history_id=${rowId}`}
      />
    </div>
  );
};

export default Content;
