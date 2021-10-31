import { Button, Modal, Upload, message, Steps, Tooltip, Table } from "antd";
import { useEffect, useRef, useState } from "react";
import {
  SendOutlined,
  LoadingOutlined,
  CheckCircleFilled,
} from "@ant-design/icons";
//import BMF from "browser-md5-file";
import { fetchPost, fetchGet } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { handleResponse } from "@/utils/utils";

const ScanServerModal = ({
  scanServerModalVisibility,
  setScanServerModalVisibility,
  refresh,
}) => {
  const [stepNum, setStepNum] = useState(0);
  const [loading, setLoading] = useState(false);

  const [dataSource, setDataSource] = useState();

  const isOpen = useRef(null);

  const timer = useRef(null);

  // 失败时的轮训次数标识
  const trainingInRotationNum = useRef(0);

  function fetchData(data) {
    // 防止在弹窗关闭后还继续轮训
    if (!isOpen.current) {
      return;
    }
    fetchGet(apiRequest.appStore.localPackageScanResult, {
      params: {
        uuid: data.uuid,
        package_names: data.package_names.join(","),
      },
    })
      .then((res) => {
        // timer.current = setTimeout(() => {
        //   fetchData(data);
        // }, 2000);
        if (res)
          handleResponse(res, (res) => {
            if (res.data.stage_status.includes("check")) {
              setStepNum(1);
            }
            if (res.data.stage_status.includes("publish")) {
              setStepNum(2);
            }
            setDataSource(res.data);
            if (res.data && res.data.stage_status.includes("ing")) {
              timer.current = setTimeout(() => {
                fetchData(data);
              }, 2000);
            }
          });
      })
      .catch((e) => {
        trainingInRotationNum.current++;
        if (trainingInRotationNum.current < 3) {
          setTimeout(() => {
            fetchData(data);
          }, 5000);
        } else {
          setDataSource((dataS) => {
            // /console.log(dataS);
            let arr = dataS?.package_detail?.map((item) => {
              return {
                ...item,
                status: 9,
              };
            });
            //console.log(arr);
            return {
              ...dataS,
              package_detail: arr,
            };
          });
        }
      })
      .finally((e) => {});
  }

  // 扫描服务端executeLocalPackageScan
  const executeLocalPackageScan = () => {
    setStepNum(0);
    setLoading(true);
    fetchPost(apiRequest.appStore.executeLocalPackageScan)
      .then((res) => {
        handleResponse(res, (res) => {
          if (
            res.data &&
            res.data?.package_names?.filter((item) => item).length > 0
          ) {
            fetchData(res.data);
          }
        });
      })
      .catch((e) => {
        console.log(e);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    isOpen.current = scanServerModalVisibility;
    if (scanServerModalVisibility) {
      executeLocalPackageScan();
    }
  }, [scanServerModalVisibility]);

  return (
    <Modal
      zIndex={1}
      title={
        <span>
          <span style={{ position: "relative", left: "-10px" }}>
            <SendOutlined />
          </span>
          <span>
            {stepNum == 0 && "扫描服务端安装包"}
            {stepNum == 1 && "校验服务端安装包"}
            {stepNum == 2 && "发布服务端安装包"}
          </span>
        </span>
      }
      afterClose={() => {
        setDataSource([]);
        setStepNum(0);
        clearTimeout(timer.current);
        refresh();
      }}
      onCancel={() => {
        setScanServerModalVisibility(false);
      }}
      visible={scanServerModalVisibility}
      footer={null}
      width={1000}
      loading={loading}
      bodyStyle={{
        paddingLeft: 30,
        paddingRight: 30,
      }}
      destroyOnClose
    >
      <Steps
        type="navigation"
        size="small"
        current={stepNum}
        //onChange={this.onChange}
      >
        <Steps.Step
          title="扫描服务端安装包"
          icon={loading && <LoadingOutlined />}
        />
        <Steps.Step
          title="安装包数据校验"
          icon={dataSource?.stage_status == "checking" && <LoadingOutlined />}
        />
        <Steps.Step
          title="发布"
          icon={dataSource?.stage_status == "publishing" && <LoadingOutlined />}
        />
      </Steps>
      {stepNum == 0 && (
        <div style={{ paddingLeft: 30, paddingTop: 30 }}>
          <div
            style={{
              overflow: "hidden",
              paddingBottom: 20,
            }}
          >
            {loading ? (
              <p style={{ textAlign: "center" }}>正在扫描服务端...</p>
            ) : (
              <p style={{ textAlign: "center" }}>
                扫描结束，服务端暂无安装包！
              </p>
            )}
          </div>
        </div>
      )}
      {stepNum == 1 && (
        <div style={{ paddingLeft: 30, paddingTop: 30 }}>
          <div
            style={{
              overflow: "hidden",
              paddingBottom: 20,
            }}
          >
            <p style={{ textAlign: "center" }}>{dataSource?.message}</p>
          </div>
          <Table
            style={{ border: "1px solid #e3e3e3" }}
            size="middle"
            //hideOnSinglePage
            pagination={{
              defaultPageSize: 5,
            }}
            columns={[
              {
                title: "安装包名称",
                key: "name",
                dataIndex: "name",
                align: "center",
              },
              {
                title: "状态",
                key: "status",
                dataIndex: "status",
                align: "center",
                render: (text) => {
                  switch (text) {
                    case 2:
                      return "校验中";
                      break;
                    case 1:
                      return "校验失败";
                      break;
                    case 0:
                      return "校验成功";
                      break;
                    case 9:
                      return "网络错误";
                      break;
                    default:
                      break;
                  }
                },
              },
              {
                title: "说明",
                key: "message",
                dataIndex: "message",
                align: "center",
                //width:120,
                ellipsis: true,
                render: (text) => {
                  return (
                    <Tooltip title={text} placement="top">
                      <div
                        style={{
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                          whiteSpace: "nowrap",
                        }}
                      >
                        {text ? text : "-"}
                      </div>
                    </Tooltip>
                  );
                },
              },
            ]}
            pagination={false}
            dataSource={dataSource?.package_detail?.map((item, idx) => {
              return {
                ...item,
                name:
                  dataSource &&
                  dataSource.package_names_lst &&
                  dataSource.package_names_lst[idx],
              };
            })}
          />
          {dataSource?.stage_status == "check_all_failed" && (
            <div
              style={{
                display: "flex",
                justifyContent: "center",
                marginTop: 60,
                position: "relative",
                left: -20,
              }}
            >
              <Button
                type="primary"
                //disabled={dataSource?.stage_status !== "published"}
                //loading={loading}
                onClick={() => {
                  setScanServerModalVisibility(false);
                }}
              >
                完成
              </Button>
            </div>
          )}
        </div>
      )}
      {stepNum == 2 && (
        <div style={{ paddingLeft: 30, paddingTop: 30 }}>
          <div
            style={{
              overflow: "hidden",
              paddingBottom: 20,
            }}
          >
            {dataSource?.stage_status == "published" && (
              <p style={{ textAlign: "center", fontSize: 20 }}>
                <CheckCircleFilled
                  style={{
                    paddingRight: 10,
                    color: "#3cbd35",
                    fontSize: 24,
                    position: "relative",
                    top: 1,
                  }}
                />
                发布完成
              </p>
            )}
            <p style={{ textAlign: "center" }}>{dataSource?.message}</p>
          </div>
          <Table
            style={{ border: "1px solid #e3e3e3" }}
            size="middle"
            //hideOnSinglePage
            pagination={{
              defaultPageSize: 5,
            }}
            columns={[
              {
                title: "安装包名称",
                key: "name",
                dataIndex: "name",
                align: "center",
              },
              {
                title: "状态",
                key: "status",
                dataIndex: "status",
                align: "center",
                render: (text) => {
                  switch (text) {
                    case 3:
                      return "发布成功";
                      break;
                    case 4:
                      return "发布失败";
                      break;
                    case 5:
                      return "发布中";
                      break;
                    case 9:
                      return "网络错误";
                      break;
                    default:
                      break;
                  }
                },
              },
              {
                title: "说明",
                key: "message",
                dataIndex: "message",
                align: "center",
                ellipsis: true,
                render: (text) => {
                  return (
                    <Tooltip title={text} placement="top">
                      <div
                        style={{
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                          whiteSpace: "nowrap",
                        }}
                      >
                        {text ? text : "-"}
                      </div>
                    </Tooltip>
                  );
                },
              },
            ]}
            pagination={false}
            dataSource={dataSource?.package_detail?.map((item, idx) => {
              return {
                ...item,
                name:
                  dataSource &&
                  dataSource.package_names_lst &&
                  dataSource.package_names_lst[idx],
              };
            })}
          />
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              marginTop: 60,
              position: "relative",
              left: -20,
            }}
          >
            <Button
              type="primary"
              disabled={dataSource?.stage_status !== "published"}
              //loading={loading}
              onClick={() => {
                setScanServerModalVisibility(false);
              }}
            >
              完成
            </Button>
          </div>
        </div>
      )}
    </Modal>
  );
};

export default ScanServerModal;
