import { Button, Modal, Upload, message, Steps, Tooltip } from "antd";
import { useEffect, useRef, useState } from "react";
import {
  CloudUploadOutlined,
  ExclamationCircleOutlined,
  CloseCircleFilled,
  CheckCircleFilled,
  LoadingOutlined,
  SyncOutlined,
  ClockCircleFilled,
  SendOutlined,
} from "@ant-design/icons";
//import BMF from "browser-md5-file";
import { fetchPost, fetchGet } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { handleResponse } from "@/utils/utils";
import { OmpMessageModal } from "@/components";

//let bmf = new BMF();

const ReleaseModal = ({
  setReleaseModalVisibility,
  releaseModalVisibility,
  timeUnix,
  refresh,
}) => {
  const [loading, setLoading] = useState(false);

  const [filesList, setFilesList] = useState([]);

  const [deleteModal, setDeleteModal] = useState(false);

  const [dataSource, setDataSource] = useState([]);

  const [stepNum, setStepNum] = useState(0);

  const isRun = useRef(null);

  const timer = useRef(null);

  // 失败时的轮训次数标识
  const trainingInRotationNum = useRef(0);

  function checkData() {
    // 防止在弹窗关闭后还继续轮训
    if (!isRun.current) {
      return;
    }
    fetchGet(apiRequest.appStore.pack_verification_results, {
      params: {
        operation_uuid: timeUnix,
      },
    })
      .then((res) => {
        if (res)
          handleResponse(res, (res) => {
            setDataSource(res.data);
            if (res.data) {
              let checkRunningArr = res.data.filter((item) => {
                return item.package_status == 2;
              });
              let publishRunningArr = res.data.filter((item) => {
                return item.package_status == 5;
              });
              if (checkRunningArr.length > 0 || publishRunningArr.length > 0) {
                timer.current = setTimeout(() => {
                  checkData();
                }, 2000);
              }
            }
          });
      })
      .catch((e) => {
        console.log(e);
        trainingInRotationNum.current++;
        if (trainingInRotationNum.current < 3) {
          setTimeout(() => {
            checkData();
          }, 5000);
        } else {
          setDataSource((data) => {
            console.log(data);
            return data.map((item) => {
              return {
                ...item,
                package_status: 9,
              };
            });
          });
        }
      })
      .finally((e) => {});
  }

  // 发布的查询
  function publishCheckData() {
    // 防止在弹窗关闭后还继续轮训
    if (!isRun.current) {
      return;
    }
    fetchGet(apiRequest.appStore.publish, {
      params: {
        operation_uuid: timeUnix,
      },
    })
      .then((res) => {
        if (res)
          handleResponse(res, (res) => {
            setDataSource(res.data);
            if (res.data) {
              let checkRunningArr = res.data.filter((item) => {
                return item.package_status == 2;
              });
              let publishRunningArr = res.data.filter((item) => {
                return item.package_status == 5;
              });
              if (checkRunningArr.length > 0 || publishRunningArr.length > 0) {
                setTimeout(() => {
                  publishCheckData();
                }, 2000);
              }
            }
          });
      })
      .catch((e) => {
        console.log(e);
        trainingInRotationNum.current++;
        if (trainingInRotationNum.current < 3) {
          setTimeout(() => {
            publishCheckData();
          }, 5000);
        } else {
          setDataSource((data) => {
            //console.log(data);
            return data.map((item) => {
              return {
                ...item,
                package_status: 9,
              };
            });
          });
        }
      })
      .finally((e) => {});
  }

  // 发布
  const publishApp = () => {
    setLoading(true);
    fetchPost(apiRequest.appStore.publish, {
      body: {
        uuid: timeUnix,
      },
    })
      .then((res) => {
        if (res && res.data) {
          if (res.data.code == 0) {
            setStepNum(2);
            publishCheckData();
          }
        }
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    isRun.current = releaseModalVisibility;
  }, [releaseModalVisibility]);

  return (
    <>
      <Modal
        zIndex={1000}
        title={
          <span>
            <span style={{ position: "relative", left: "-10px" }}>
              <SendOutlined />
            </span>
            <span>发布</span>
          </span>
        }
        afterClose={() => {
          clearTimeout(timer.current);
          setFilesList([]);
          setStepNum(0);
          setDataSource([]);
          refresh();
        }}
        onCancel={() => {
          if (
            stepNum == 2 &&
            dataSource.filter((item) => item.package_status == 5).length == 0
          ) {
            setReleaseModalVisibility(false);
            return;
          }
          if (filesList.length == 0) {
            setReleaseModalVisibility(false);
          } else {
            setDeleteModal(true);
          }
        }}
        visible={releaseModalVisibility}
        footer={null}
        width={1000}
        loading={loading}
        bodyStyle={{
          paddingLeft: 30,
          paddingRight: 30,
        }}
        destroyOnClose
      >
        <Steps size="small" current={stepNum}>
          <Steps.Step title="上传文件" />
          <Steps.Step title="数据校验" />
          <Steps.Step title="发布结果" />
        </Steps>
        {stepNum == 0 && (
          <div style={{ paddingLeft: 30, paddingTop: 30 }}>
            <div
              style={{
                visibility: stepNum == 0 ? "visible" : "hidden",
                height: stepNum == 0 ? null : 0,
                overflow: "hidden",
                paddingBottom: 20,
              }}
            >
              <div>
                <Upload.Dragger
                  name="file"
                  action="/api/appStore/upload/"
                  accept=".tar,.gz"
                  multiple={true}
                  data={(file, ...arg) => {
                    //console.log(arg,file)
                    return {
                      uuid: timeUnix,
                      operation_user: localStorage.getItem("username"),
                      md5: file.uid,
                    };
                  }}
                  maxCount={5}
                  beforeUpload={(file, fileList) => {
                    const fileSize = file.size / 1024 / 1024 / 1024; //单位是G
                    if (Math.ceil(fileSize) > 4) {
                      message.error("仅支持传入4G以内文件");
                      return Upload.LIST_IGNORE;
                    }

                    if (fileList.length > 5) {
                      if (file == fileList[0]) {
                        message.error("单次发布操作，最多支持上传5个文件");
                      }
                      return Upload.LIST_IGNORE;
                    }

                    if (filesList.length + fileList.length > 5) {
                      if (file == fileList[0]) {
                        message.error("单次发布操作，最多支持上传5个文件");
                      }
                      return Upload.LIST_IGNORE;
                    }

                    if (filesList.length >= 5) {
                      if (file == fileList[0]) {
                        message.error("单次发布操作，最多支持上传5个文件");
                      }
                      return Upload.LIST_IGNORE;
                    }

                    var reg = /[^a-zA-Z0-9\_\-\.]/g;
                    if (reg.test(file.name)) {
                      message.error(`文件名仅支持字母、数字、"_"、"-"和"."`);
                      return Upload.LIST_IGNORE;
                    }

                    let fileNameArr =
                      fileList.length == 1
                        ? [...filesList, file].map((i) => i.name)
                        : [...filesList, ...fileList].map((i) => i.name);
                    let uniqueArr = [...new Set(fileNameArr)];
                    if (fileNameArr.length !== uniqueArr.length) {
                      if (fileList[0].uid == file.uid) {
                        message.error("上传文件存在同名");
                      }
                      return Upload.LIST_IGNORE;
                    }
                  }}
                  onChange={(e) => {
                    setFilesList(e.fileList);
                  }}
                  onRemove={(e) => {
                    if (e && e.response && e.response.code == 0) {
                      fetchPost(apiRequest.appStore.remove, {
                        body: {
                          uuid: timeUnix,
                          package_names: [e.name],
                        },
                      })
                        .then((res) => {
                          handleResponse(res, (res) => {});
                        })
                        .catch((e) => console.log(e))
                        .finally(() => {});
                    }
                  }}
                >
                  <div style={{ textAlign: "center", color: "#575757" }}>
                    <p className="ant-upload-drag-icon">
                      <CloudUploadOutlined />
                    </p>
                    <p style={{ textAlign: "center", color: "#575757" }}>
                      点击或将文件拖拽到这里上传
                    </p>
                    <p
                      style={{
                        textAlign: "center",
                        color: "#8e8e8e",
                        fontSize: 13,
                        paddingTop: 10,
                      }}
                    >
                      支持扩展名: .tar 或 .tar.gz  文件大小不超过4G
                    </p>
                    <p
                      style={{
                        textAlign: "center",
                        color: "#8e8e8e",
                        fontSize: 13,
                        paddingTop: 10,
                      }}
                    >
                      最多上传5个文件
                    </p>
                  </div>
                </Upload.Dragger>
              </div>
            </div>

            <div
              style={{
                display: "flex",
                justifyContent: "center",
                marginTop: 20,
              }}
            >
              <Button
                type="primary"
                disabled={
                  filesList.filter((i) => i.status !== "done").length !== 0 ||
                  filesList.length == 0
                }
                onClick={() => {
                  setStepNum(1);
                  checkData();
                }}
              >
                校验
              </Button>
            </div>
          </div>
        )}
        {stepNum == 1 && (
          <div style={{ paddingLeft: 30, paddingTop: 30 }}>
            <p style={{ marginBottom: 30 }}>
              校验失败的安装包不会在应用商店创建，如相同名称应用已存在，发布后会替换原有安装包
            </p>
            {dataSource.map((item, idx) => {
              return (
                <div
                  key={idx}
                  style={{
                    marginBottom: 10,
                    display: "flex",
                    justifyContent: "space-around",
                    paddingRight: 80,
                  }}
                >
                  <div style={{ flex: 2 }}>{item.package_name}</div>
                  <div style={{ flex: 1, textAlign: "right" }}>
                    {item.package_status == 0 && (
                      <span style={{ color: "#3cbd35" }}>
                        校验通过
                        <CheckCircleFilled
                          style={{
                            fontSize: 18,
                            position: "relative",
                            top: 1,
                            paddingLeft: 10,
                            color: "#3cbd35",
                          }}
                        />
                      </span>
                    )}
                    {item.package_status == 1 && (
                      <span style={{ color: "#fe1937" }}>
                        校验失败
                        <CloseCircleFilled
                          style={{
                            fontSize: 18,
                            position: "relative",
                            top: 1,
                            paddingLeft: 10,
                            color: "#fe1937",
                          }}
                        />
                      </span>
                    )}

                    {item.package_status == 2 && (
                      <span>
                        校验中...
                        <SyncOutlined
                          spin
                          style={{
                            fontSize: 16,
                            position: "relative",
                            top: 1,

                            marginLeft: 10,
                            //color: "#fe1937",
                          }}
                        />
                      </span>
                    )}

                    {item.package_status == 9 && (
                      <span style={{ color: "#fe1937" }}>
                        网络错误
                        <CloseCircleFilled
                          style={{
                            fontSize: 18,
                            position: "relative",
                            top: 1,
                            paddingLeft: 10,
                            color: "#fe1937",
                          }}
                        />
                      </span>
                    )}
                  </div>
                  <Tooltip placement="right" title={item.error_msg}>
                    <div
                      style={{
                        flex: 3,
                        textAlign: "right",
                        overflow: "hidden",
                        paddingLeft: 20,
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {item.error_msg}
                    </div>
                  </Tooltip>
                </div>
              );
            })}
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
                disabled={
                  dataSource.filter((i) => i.package_status == 0).length == 0 ||
                  dataSource.filter((i) => i.package_status == 2).length !== 0
                }
                loading={loading}
                onClick={() => {
                  publishApp();
                }}
              >
                发布
              </Button>
            </div>
          </div>
        )}
        {stepNum == 2 && (
          <div style={{ paddingLeft: 30, paddingTop: 30 }}>
            {dataSource.filter((item) => item.package_status == 5).length >
            0 ? (
              <div
                style={{
                  paddingBottom: 20,
                  position: "relative",
                  left: -20,
                }}
              >
                <p style={{ textAlign: "center", fontSize: 20 }}>
                  <ClockCircleFilled
                    style={{
                      paddingRight: 10,
                      color: "#ffb436",
                      fontSize: 24,
                      position: "relative",
                      top: 1,
                    }}
                  />
                  发布中
                </p>
              </div>
            ) : (
              <div
                style={{
                  marginBottom: 20,
                  position: "relative",
                  left: -20,
                }}
              >
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
                <p style={{ textAlign: "center" }}>
                  本次成功发布{" "}
                  {dataSource.filter((item) => item.package_status == 3).length}
                  个 服务
                </p>
                <p style={{ textAlign: "center" }}>
                  发布完成的安装包存放路径:{" "}
                  <span style={{ fontWeight: 500, color: "rgba(0,0,0,0.8)" }}>
                    omp/package_hub/verified/
                  </span>{" "}
                </p>
              </div>
            )}

            {dataSource.map((item, idx) => {
              return (
                <div
                  key={idx}
                  style={{
                    marginBottom: 10,
                    display: "flex",
                    justifyContent: "space-around",
                    paddingRight: 80,
                  }}
                >
                  <div style={{ flex: 2 }}>{item.package_name}</div>
                  <div style={{ flex: 1, textAlign: "right" }}>
                    {item.package_status == 3 && (
                      <span style={{ color: "#3cbd35" }}>
                        发布成功
                        <CheckCircleFilled
                          style={{
                            fontSize: 18,
                            position: "relative",
                            top: 1,
                            paddingLeft: 10,
                            color: "#3cbd35",
                          }}
                        />
                      </span>
                    )}
                    {item.package_status == 4 && (
                      <span style={{ color: "#fe1937" }}>
                        发布失败
                        <CloseCircleFilled
                          style={{
                            fontSize: 18,
                            position: "relative",
                            top: 1,
                            paddingLeft: 10,
                            color: "#fe1937",
                          }}
                        />
                      </span>
                    )}

                    {item.package_status == 5 && (
                      <span>
                        发布中...
                        <SyncOutlined
                          spin
                          style={{
                            fontSize: 16,
                            position: "relative",
                            top: 1,

                            marginLeft: 10,
                            //color: "#fe1937",
                          }}
                        />
                      </span>
                    )}

                    {item.package_status == 9 && (
                      <span style={{ color: "#fe1937" }}>
                        网络错误
                        <CloseCircleFilled
                          style={{
                            fontSize: 18,
                            position: "relative",
                            top: 1,
                            paddingLeft: 10,
                            color: "#fe1937",
                          }}
                        />
                      </span>
                    )}
                  </div>
                  <Tooltip placement="right" title={item.error_msg}>
                    <div
                      style={{
                        flex: 3,
                        textAlign: "right",
                        overflow: "hidden",
                        paddingLeft: 20,
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {item.error_msg}
                    </div>
                  </Tooltip>
                </div>
              );
            })}
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
                disabled={
                  dataSource.filter((item) => item.package_status == 5).length >
                  0
                }
                //loading={loading}
                onClick={() => {
                  setReleaseModalVisibility(false);
                }}
              >
                完成
              </Button>
            </div>
          </div>
        )}
      </Modal>
      <OmpMessageModal
        zIndex={1100}
        style={{ top: 160 }}
        visibleHandle={[deleteModal, setDeleteModal]}
        title={
          <span>
            <ExclamationCircleOutlined
              style={{
                fontSize: 20,
                color: "#fe1937",
                paddingRight: "10px",
                position: "relative",
                top: 2,
              }}
            />
            提示
          </span>
        }
        //loading={loading}
        onFinish={() => {
          let updatedFile = filesList.filter(
            (i) => i.response && i.response.code == 0
          );
          if (updatedFile.length == 0) {
            setReleaseModalVisibility(false);
            setDeleteModal(false);
            return;
          }
          fetchPost(apiRequest.appStore.remove, {
            body: {
              uuid: timeUnix,
              package_names: updatedFile.map((i) => i.name),
            },
          })
            .then((res) => {
              handleResponse(res, (res) => {});
            })
            .catch((e) => console.log(e))
            .finally(() => {
              setReleaseModalVisibility(false);
              setDeleteModal(false);
            });
        }}
      >
        <div style={{ padding: "20px" }}>
          <p style={{ fontWeight: 500 }}>确认要中断发布操作吗 ？</p>
          <p style={{ paddingLeft: 20 }}>
            正在进行发布操作，关闭窗口将会中断，此操作不可逆。
          </p>
        </div>
      </OmpMessageModal>
    </>
  );
};

export default ReleaseModal;
