import { Button, Modal, Upload, message, Steps, Tooltip } from "antd";
import { useEffect, useRef, useState } from "react";
import {
  CloudUploadOutlined,
  ExclamationCircleOutlined,
  CloseCircleFilled,
  CheckCircleFilled,
  LoadingOutlined,
  SyncOutlined,
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
}) => {
  const [loading, setLoading] = useState(false);
  const [stepNum, setStepNum] = useState(0);

  const [timeUnix, setTimeUnix] = useState("");

  const [filesList, setFilesList] = useState([]);

  const [deleteModal, setDeleteModal] = useState(false);

  const [dataSource, setDataSource] = useState([]);

  function checkData() {
    //setLoading(true);
    fetchGet(apiRequest.appStore.pack_verification_results, {
      params: {
        operation_uuid: timeUnix,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          setDataSource(res.data);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {});
  }

  useEffect(() => {
    setTimeUnix(new Date().getTime());
  }, []);

  return (
    <>
      <Modal
        zIndex={1}
        title={
          <span>
            <span style={{ position: "relative", left: "-10px" }}></span>
            <span>批量创建主机</span>
          </span>
        }
        afterClose={()=>{
            setStepNum(0)
        }}
        onCancel={() => {
          if (filesList.length == 0) {
            setReleaseModalVisibility(false);
          } else {
            setDeleteModal(true);
          }
          //setReleaseModalVisibility(false);
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
              }}
            >
              <div>
                <Upload.Dragger
                  name="file"
                  action="/api/appStore/upload/"
                  accept=".tar,.gz"
                  multiple={true}
                  data={(file) => {
                    return {
                      uuid: timeUnix,
                      operation_user: localStorage.getItem("username"),
                      md5: "1",
                    };
                    // return new Promise((res, rej) => {
                    //   console.log("算md5了");
                    //   bmf.md5(file, (err, md5) => {
                    //     if (err) {
                    //     } else {
                    //       res({
                    //         md5: md5,
                    //         uuid: timeUnix,
                    //         operation_user: localStorage.getItem("username"),
                    //       });
                    //     }
                    //   });
                    // });
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
                        message.error("仅支持上传5个文件");
                      }

                      return Upload.LIST_IGNORE;
                    }
                  }}
                  onChange={(e) => {
                    setFilesList(e.fileList);
                  }}
                  onRemove={(e) => {
                    if (e.response.code == 0) {
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
                        .finally(() => {
                          //setSearchLoading(false);
                        });
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
                      支持扩展名: .tar .tar.gz 文件大小不超过4G
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
                    marginBottom:10,
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
                marginTop: 20,
              }}
            >
              <Button
                type="primary"
                disabled={
                  true
                }
                // onClick={() => {
                //   setStepNum(1);
                //   checkData();
                // }}
              >
                发布
              </Button>
            </div>
          </div>
        )}
      </Modal>
      <OmpMessageModal
        zIndex={2}
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
          fetchPost(apiRequest.appStore.remove, {
            body: {
              uuid: timeUnix,
              package_names: filesList.map((i) => i.name),
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
