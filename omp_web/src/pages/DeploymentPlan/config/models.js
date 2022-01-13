import React, { useEffect } from "react";
import { useHistory } from "react-router-dom";
import {
  Button,
  Input,
  Select,
  Form,
  message,
  InputNumber,
  Row,
  Col,
  Tooltip,
  Modal,
  Steps,
  Upload,
  Switch,
  Table,
} from "antd";
import {
  PlusSquareOutlined,
  FormOutlined,
  SyncOutlined,
  ImportOutlined,
  DownloadOutlined,
  CloudUploadOutlined,
  CheckCircleFilled,
  CloseCircleFilled,
} from "@ant-design/icons";
import { handleResponse } from "@/utils/utils";
import { fetchPost } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { useState, useRef } from "react";
import XLSX from "xlsx";
import { OmpTable } from "@/components";

const getHeaderRow = (sheet) => {
  const headers = [];
  const range = XLSX.utils.decode_range(sheet["!ref"]);
  let C;
  const R = range.s.r;
  for (C = range.s.c; C <= range.e.c; ++C) {
    const cell = sheet[XLSX.utils.encode_cell({ c: C, r: R })];
    let hdr = "UNKNOWN " + C;
    if (cell && cell.t) hdr = XLSX.utils.format_cell(cell);
    headers.push(hdr);
  }
  return headers;
};

class UploadExcelComponent extends React.Component {
  state = {
    loading: false,
    excelData: {
      header: null,
      results: null,
    },
  };
  draggerProps = () => {
    let _this = this;
    return {
      name: "file",
      multiple: false,
      accept: ".xlsx",
      maxCount: 1,
      onRemove() {
        _this.props.onRemove();
        return true;
      },
      onChange(info) {
        const { status } = info.file;
        if (status === "done") {
          //console.log(info.file);
          message.success(`${info.file.name} 文件解析成功`);
        } else if (status === "error") {
          message.error(
            `${info.file.name} 文件解析失败, 请确保文件内容格式符合规范后重新上传`
          );
        }
      },
      beforeUpload(file, fileList) {
        //console.log(file);
        // bmf.md5(file,(err,md5)=>{
        //   console.log(err,md5,"=====?---")
        // })
        // 校验文件大小
        const fileSize = file.size / 1024 / 1024; //单位是M
        //console.log(fileSize);
        if (Math.ceil(fileSize) > 10) {
          message.error("仅支持传入10M以内文件");
          return Upload.LIST_IGNORE;
        }
        if (!/\.(xlsx)$/.test(file.name)) {
          message.error("仅支持传入.xlsx文件");
          return Upload.LIST_IGNORE;
        }
      },
      customRequest(e) {
        _this.readerData(e.file).then(
          (msg) => {
            //console.log(e);
            e.onSuccess();
          },
          () => {
            e.onError();
          }
        );
      },
    };
  };
  readerData = (rawFile) => {
    // bmf.md5(rawFile,(err,md5)=>{
    //   console.log(err,md5,"=====?")
    // })
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = (e) => {
        try {
          const data = e.target.result;
          const workbook = XLSX.read(data, { type: "array" });
          // 主机数据
          const firstSheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[firstSheetName];
          const header = getHeaderRow(worksheet);
          const results = XLSX.utils.sheet_to_json(worksheet);

          // 服务数据
          const sencondSheetName = workbook.SheetNames[1];
          const serviceSheet = workbook.Sheets[sencondSheetName];
          const serviceHeader = getHeaderRow(serviceSheet);
          const serviceResults = XLSX.utils.sheet_to_json(serviceSheet);

          this.generateData(
            { header, results },
            { serviceHeader, serviceResults }
          );
          resolve();
        } catch (error) {
          reject();
        }
      };
      reader.readAsArrayBuffer(rawFile);
    });
  };
  generateData = ({ header, results }, { serviceHeader, serviceResults }) => {
    this.setState({
      excelData: { header, results },
      excelServiceData: { serviceHeader, serviceResults },
    });
    this.props.uploadSuccess &&
      this.props.uploadSuccess(
        this.state.excelData,
        this.state.excelServiceData
      );
  };
  render() {
    return (
      <div>
        <Upload.Dragger {...this.draggerProps()}>
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
            支持扩展名: .xlsx
          </p>
        </Upload.Dragger>
      </div>
    );
  }
}

/* 导入执行计划 */
export const ImportPlanModal = ({ importPlan, setImportPlan }) => {
  const history = useHistory();
  const [dataSource, setDataSource] = useState([]);
  const [columns, setColumns] = useState([]);

  const [serviceDataSource, setServiceDataSource] = useState([]);
  const [serviceColumns, setServiceColumns] = useState([]);

  const [tableCorrectData, setTableCorrectData] = useState([]);
  const [tableErrorData, setTableErrorData] = useState([]);
  const [tableColumns, setTableColumns] = useState([]);

  const [serviceTableCorrectData, setServiceTableCorrectData] = useState([]);
  const [serviceTableErrorData, setServiceTableErrorData] = useState([]);
  const [serviceTableColumns, setServiceTableColumns] = useState([]);

  // 涉及数量信息
  const [numInfo, setNumInfo] = useState({});

  const [stepNum, setStepNum] = useState(0);

  const [loading, setLoading] = useState(false);

  // 导入部署步骤状态
  const [hostStep, setHostStep] = useState(null);
  const [serviceStep, setServiceStep] = useState(null);
  const [importStep, setImportStep] = useState(null);

  // 导入部署模板状态
  const [importResult, setImportResult] = useState(null);

  // 主机和服务的正确数据
  let hostCorrectData = null;
  let serviceCorrectData = null;

  // 轮训控制器
  const hostAgentTimer = useRef(null);

  // 失败的columns
  const errorColumns = [
    {
      title: "行数",
      key: "row",
      dataIndex: "row",
      align: "center",
      //render: nonEmptyProcessing,
      width: 60,
      ellipsis: true,
      fixed: "left",
    },
    {
      title: "实例名称",
      key: "instance_name",
      dataIndex: "instance_name",
      align: "center",
      //render: nonEmptyProcessing,
      width: 120,
      ellipsis: true,
      //fixed: "left",
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
    },
    {
      title: "IP地址",
      key: "ip",
      dataIndex: "ip",
      // sorter: (a, b) => a.ip - b.ip,
      // sortDirections: ["descend", "ascend"],
      align: "center",
      width: 120,
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
      ellipsis: true,
      //fixed: "left"
    },
    {
      title: "端口",
      key: "port",
      dataIndex: "port",
      // sorter: (a, b) => a.ip - b.ip,
      // sortDirections: ["descend", "ascend"],
      align: "center",
      width: 80,
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
      //ellipsis: true,
    },
    {
      title: "数据分区",
      key: "data_folder",
      dataIndex: "data_folder",
      // sorter: (a, b) => a.ip - b.ip,
      // sortDirections: ["descend", "ascend"],
      align: "center",
      width: 180,
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
      ellipsis: true,
    },
    {
      title: "用户名",
      key: "username",
      dataIndex: "username",
      align: "center",
      width: 120,
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
      ellipsis: true,
    },
    {
      title: "运行用户",
      key: "run_user",
      dataIndex: "run_user",
      align: "center",
      width: 120,
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
      ellipsis: true,
    },
    {
      title: "失败原因",
      key: "validate_error",
      dataIndex: "validate_error",
      fixed: "right",
      // sorter: (a, b) => a.ip - b.ip,
      // sortDirections: ["descend", "ascend"],
      align: "center",
      width: 240,
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
      ellipsis: true,
    },
  ];

  // 服务失败的columns
  const serviceErrorColumns = [
    {
      title: "行数",
      key: "row",
      dataIndex: "row",
      align: "center",
      width: 60,
      ellipsis: true,
      fixed: "left",
      render: (text) => {
        if (text < 1) return "-";
        return text;
      },
    },
    {
      title: "实例名称",
      key: "instance_name",
      dataIndex: "instance_name",
      align: "center",
      //render: nonEmptyProcessing,
      width: 120,
      ellipsis: true,
      //fixed: "left",
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
    },
    {
      title: "服务名称",
      key: "service_name",
      dataIndex: "service_name",
      align: "center",
      //render: nonEmptyProcessing,
      width: 140,
      ellipsis: true,
      //fixed: "left",
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
    },
    ,
    {
      title: "运行内存",
      key: "memory",
      dataIndex: "memory",
      align: "center",
      //render: nonEmptyProcessing,
      width: 80,
      ellipsis: true,
      //fixed: "left",
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
    },
    {
      title: "失败原因",
      key: "validate_error",
      dataIndex: "validate_error",
      fixed: "right",
      // sorter: (a, b) => a.ip - b.ip,
      // sortDirections: ["descend", "ascend"],
      align: "center",
      width: 260,
      render: (text) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
      ellipsis: true,
    },
  ];

  // 校验主机数据
  const fetchBatchValidate = () => {
    setLoading(true);
    if (dataSource.length == 0) {
      message.warning("节点信息中无有效数据，请补充后重新上传");
      setHostStep(false);
      setImportResult(false);
      return;
    }
    let queryBody = dataSource.map((item) => {
      let result = {};
      for (const key in item) {
        switch (key) {
          case "IP[必填]":
            result.ip = item[key];
            break;
          case "实例名[必填]":
            result.instance_name = item[key];
            break;
          case "密码[必填]":
            result.password = item[key];
            break;
          case "操作系统[必填]":
            result.operate_system = item[key];
            break;
          case "数据分区[必填]":
            result.data_folder = item[key];
            break;
          case "用户名[必填]":
            result.username = item[key];
            break;
          case "端口[必填]":
            result.port = item[key];
            break;
          case "运行用户":
            result.run_user = item[key];
            break;
          default:
            break;
        }
      }
      return {
        ...result,
        row: item.key,
      };
    });
    // 校验数据
    fetchPost(apiRequest.machineManagement.batchValidate, {
      body: {
        host_list: queryBody,
      },
    })
      .then((res) => {
        res = res.data;
        if (res.code == 0) {
          if (res.data && res.data.error?.length > 0) {
            setTableErrorData(
              res.data.error?.map((item, idx) => {
                return {
                  key: idx,
                  ...item,
                };
              })
            );
            setTableColumns(errorColumns);
            setHostStep(false);
            setImportResult(false);
          } else {
            hostCorrectData = res.data.correct?.map((item, idx) => {
              return {
                key: idx,
                ...item,
              };
            });
            setHostStep(true);
            serviceDataValidate();
          }
        } else {
          message.warning(res.message);
          setHostStep(false);
          setImportResult(false);
        }
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  // 校验服务数据
  const serviceDataValidate = () => {
    setLoading(true);
    if (serviceDataSource.length == 0) {
      message.warning("服务分布中无有效数据，请补充后重新上传");
      setServiceStep(false);
      setImportResult(false);
      return;
    }
    // 获取主机实例名数组;
    let instanceNameArr = dataSource.map((item) => {
      let instanceName = "";
      for (const key in item) {
        switch (key) {
          case "实例名[必填]":
            instanceName = item[key];
            break;
          default:
            break;
        }
      }
      return instanceName;
    });
    // 获取服务数据
    let serviceArr = serviceDataSource.map((item) => {
      let result = {};
      for (const key in item) {
        switch (key) {
          case "主机实例名[必填]":
            result.instance_name = item[key];
            break;
          case "服务名[必填]":
            result.service_name = item[key];
            break;
          case "运行内存":
            result.memory = item[key];
            break;
          case "虚拟IP":
            result.vip = item[key];
            break;
          case "角色":
            result.role = item[key];
            break;
          case "模式":
            result.mode = item[key];
            break;
          default:
            break;
        }
      }
      return {
        ...result,
        row: item.key,
      };
    });
    // 校验服务分布信息
    fetchPost(apiRequest.deloymentPlan.serviceValidate, {
      body: {
        instance_name_ls: instanceNameArr,
        service_data_ls: serviceArr,
      },
    })
      .then((res) => {
        res = res.data;
        if (res.code == 0) {
          if (res.data && res.data.error?.length > 0) {
            setServiceTableErrorData(
              res.data.error?.map((item, idx) => {
                return {
                  key: idx,
                  ...item,
                };
              })
            );
            setServiceTableColumns(serviceErrorColumns);
            setServiceStep(false);
            setImportResult(false);
          } else {
            serviceCorrectData = res.data.correct?.map((item, idx) => {
              return {
                key: idx,
                ...item,
              };
            });
            setServiceStep(true);
            startDeployment();
          }
        } else {
          message.warning(res.message);
          setServiceStep(false);
          setImportResult(false);
        }
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  // 导入服务数据
  const serviceImport = () => {
    setLoading(true);
    let instanceArr = hostCorrectData.map((item) => {
      return {
        instance_name: item.instance_name,
        run_user: item.run_user,
      };
    });
    let serviceArr = serviceCorrectData.map((item) => {
      delete item.key;
      return {
        ...item,
      };
    });
    fetchPost(apiRequest.deloymentPlan.serviceImport, {
      body: {
        instance_info_ls: instanceArr,
        service_data_ls: serviceArr,
      },
    })
      .then((res) => {
        res = res.data;
        if (res.code === 0) {
          setNumInfo(res.data);
          setImportStep(true);
          setImportResult(true);
          // 开始安装
          startInstall(res.data.operation_uuid);
        } else {
          message.warning(res.message);
          setImportStep(false);
          setImportResult(false);
        }
      })
      .catch((e) => {
        console.log(e);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  // 开始部署
  const startDeployment = () => {
    setLoading(true);
    // 批量导入主机数据
    let hostArr = hostCorrectData.map((item) => {
      delete item.key;
      return {
        ...item,
      };
    });
    // 纳管主机
    fetchPost(apiRequest.machineManagement.batchImport, {
      body: {
        host_list: hostArr,
      },
    })
      .then((res) => {
        res = res.data;
        if (res.code === 0) {
          serviceImport();
        } else {
          message.warning(res.message);
          setImportStep(false);
          setImportResult(false);
        }
      })
      .catch((e) => console.log(e))
      .finally(() => {});
  };

  // 执行安装任务
  const retryInstall = (operation_uuid) => {
    // 跳转安装页面
    fetchPost(apiRequest.appStore.retryInstall, {
      body: {
        unique_key: operation_uuid,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.code == 0) {
            // 跳转安装页面
            history.push({
              pathname: "/application_management/app_store/installation",
              state: {
                uniqueKey: operation_uuid,
                step: 3,
              },
            });
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {});
  };

  // 查询主机 agent 状态
  const queryHostAgent = (operation_uuid) => {
    let ipArr = hostCorrectData.map((item) => {
      return item.ip;
    });
    fetchPost(apiRequest.machineManagement.hostsAgentStatus, {
      body: {
        ip_list: ipArr,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.code === 0 && res.data) {
            // 调用安装
            retryInstall(operation_uuid);
            // 清除定时器
            clearInterval(hostAgentTimer.current);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {});
  };

  // 开始安装
  const startInstall = (operation_uuid) => {
    hostAgentTimer.current = setInterval(() => {
      queryHostAgent(operation_uuid);
    }, 1000);
  };

  // 点击导入按钮
  const clickImport = () => {
    setHostStep(null);
    setServiceStep(null);
    setImportStep(null);
    setImportResult(null);
    setTableCorrectData([]);
    setTableErrorData([]);
    setServiceTableCorrectData([]);
    setServiceTableErrorData([]);
    setStepNum(1);
    fetchBatchValidate();
  };

  useEffect(() => {
    return () => {
      // 页面销毁时清除延时器
      clearInterval(hostAgentTimer.current);
    };
  }, []);

  return (
    <Modal
      title={
        <span>
          <span style={{ position: "relative", left: "-10px" }}>
            <ImportOutlined />
          </span>
          <span>导入部署模板</span>
        </span>
      }
      visible={importPlan}
      footer={null}
      width={800}
      loading={loading}
      bodyStyle={{
        paddingLeft: 30,
        paddingRight: 30,
      }}
      onCancel={() => {
        setImportPlan(false);
      }}
      afterClose={() => {
        setDataSource([]);
        setTableCorrectData([]);
        setTableErrorData([]);
        setTableColumns([]);
        setStepNum(0);
        setColumns([]);

        setServiceDataSource([]);
        setServiceColumns([]);
        setServiceTableCorrectData([]);
        setServiceTableErrorData([]);
        setServiceTableColumns([]);
      }}
      destroyOnClose
    >
      <Steps size="small" current={stepNum}>
        <Steps.Step title="上传文件" />
        <Steps.Step title="导入结果" />
      </Steps>
      <div style={{ paddingLeft: 10, paddingTop: 30 }}>
        <div
          style={{
            visibility: stepNum == 0 ? "visible" : "hidden",
            height: stepNum == 0 ? null : 0,
            overflow: "hidden",
          }}
        >
          <div style={{ display: "flex", alignItems: "center" }}>
            <div style={{ flex: 1, fontWeight: 500 }}>下载模版: </div>
            <div style={{ flex: 10, paddingLeft: 20 }}>
              <Button
                icon={<DownloadOutlined />}
                size="middle"
                style={{ fontSize: 13 }}
                onClick={() => {
                  let a = document.createElement("a");
                  a.href = apiRequest.deloymentPlan.deploymentTemplate;
                  document.body.appendChild(a);
                  a.click();
                  document.body.removeChild(a);
                }}
              >
                点击下载
              </Button>
            </div>
          </div>
          <div style={{ display: "flex", marginTop: 30 }}>
            <div style={{ flex: 1, fontWeight: 500 }}>上传文件: </div>
            <div style={{ flex: 10, paddingLeft: 20 }}>
              {importPlan && (
                <UploadExcelComponent
                  onRemove={() => {
                    setDataSource([]);
                    setColumns([]);
                    setTableCorrectData([]);
                    setTableErrorData([]);
                    setTableColumns([]);

                    setServiceDataSource([]);
                    setServiceColumns([]);
                    setServiceTableCorrectData([]);
                    setServiceTableErrorData([]);
                    setServiceTableColumns([]);
                  }}
                  uploadSuccess={(
                    { results, header },
                    { serviceHeader, serviceResults }
                  ) => {
                    // 处理主机数据
                    let dataS = results
                      .filter((item) => {
                        if (item["字段名称(请勿编辑)"]?.includes("请勿编辑")) {
                          return false;
                        }
                        if (!item["实例名[必填]"]) {
                          return false;
                        }
                        return true;
                      })
                      .map((item, idx) => {
                        return { ...item, key: item.__rowNum__ + 1 };
                      });
                    let column = header.filter((item) => {
                      if (
                        item?.includes("请勿编辑") ||
                        item?.includes("UNKNOWN")
                      ) {
                        return false;
                      }
                      return true;
                    });
                    setDataSource(dataS);
                    setColumns(column);

                    // 处理服务数据
                    let dataService = serviceResults
                      .filter((item) => {
                        if (item["字段名称(请勿编辑)"]?.includes("请勿编辑")) {
                          return false;
                        }
                        if (!item["主机实例名[必填]"]) {
                          return false;
                        }
                        return true;
                      })
                      .map((item) => {
                        return { ...item, key: item.__rowNum__ + 1 };
                      });
                    setServiceDataSource(dataService);
                    setServiceColumns(serviceHeader);
                  }}
                />
              )}

              <div
                style={{
                  display: "inline-block",
                  marginLeft: "50%",
                  transform: "translateX(-50%)",
                  marginTop: 40,
                }}
              >
                <Button
                  loading={loading}
                  onClick={() => clickImport()}
                  type="primary"
                  disabled={columns.length == 0}
                >
                  开始导入
                </Button>
              </div>
            </div>
          </div>
        </div>
        {stepNum == 1 && (
          <>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                paddingBottom: 10,
                flexDirection: "column",
              }}
            >
              <p
                style={{
                  display: "flex",
                  alignItems: "center",
                  fontSize: 20,
                }}
              >
                {hostStep === null && (
                  <>
                    <SyncOutlined
                      spin
                      style={{
                        marginRight: 16,
                      }}
                    />
                    正在校验主机数据 ...
                  </>
                )}
                {hostStep === true && (
                  <>
                    <CheckCircleFilled
                      style={{
                        color: "#52c41a",
                        fontSize: 30,
                        marginRight: 10,
                      }}
                    />
                    主机数据校验通过
                  </>
                )}
                {hostStep === false && (
                  <>
                    <CloseCircleFilled
                      style={{
                        color: "#f73136",
                        fontSize: 30,
                        marginRight: 10,
                      }}
                    />
                    主机数据校验未通过
                  </>
                )}
              </p>

              {hostStep && (
                <p
                  style={{
                    display: "flex",
                    alignItems: "center",
                    fontSize: 20,
                  }}
                >
                  {serviceStep === null && (
                    <>
                      <SyncOutlined
                        spin
                        style={{
                          marginRight: 16,
                        }}
                      />
                      正在校验服务数据 ...
                    </>
                  )}
                  {serviceStep === true && (
                    <>
                      <CheckCircleFilled
                        style={{
                          color: "#52c41a",
                          fontSize: 30,
                          marginRight: 10,
                        }}
                      />
                      服务数据校验通过
                    </>
                  )}
                  {serviceStep === false && (
                    <>
                      <CloseCircleFilled
                        style={{
                          color: "#f73136",
                          fontSize: 30,
                          marginRight: 10,
                        }}
                      />
                      服务数据校验未通过
                    </>
                  )}
                </p>
              )}

              {serviceStep && (
                <p
                  style={{
                    display: "flex",
                    alignItems: "center",
                    fontSize: 20,
                  }}
                >
                  {importStep === null && (
                    <>
                      <SyncOutlined
                        spin
                        style={{
                          marginRight: 16,
                        }}
                      />
                      正在导入模板 ...
                    </>
                  )}
                  {importStep === true && (
                    <>
                      <CheckCircleFilled
                        style={{
                          color: "#52c41a",
                          fontSize: 30,
                          marginRight: 10,
                        }}
                      />
                      部署模板导入成功
                    </>
                  )}
                  {importStep === false && (
                    <>
                      <CloseCircleFilled
                        style={{
                          color: "#f73136",
                          fontSize: 30,
                          marginRight: 10,
                        }}
                      />
                      部署模板导入失败
                    </>
                  )}
                </p>
              )}

              {tableErrorData.length > 0 && (
                <Table
                  bordered
                  scroll={{ x: 700 }}
                  columns={tableColumns}
                  dataSource={
                    tableErrorData.length > 0
                      ? tableErrorData
                      : tableCorrectData
                  }
                  pagination={{
                    pageSize: 5,
                  }}
                />
              )}

              {serviceTableErrorData.length > 0 && (
                <Table
                  bordered
                  scroll={{ x: 700 }}
                  columns={serviceTableColumns}
                  dataSource={
                    serviceTableErrorData.length > 0
                      ? serviceTableErrorData
                      : serviceTableCorrectData
                  }
                  pagination={{
                    pageSize: 5,
                  }}
                />
              )}

              {importStep && (
                <>
                  <p style={{ textAlign: "center" }}>
                    成功创建 {numInfo.host_num} 台主机
                  </p>
                  <p style={{ textAlign: "center" }}>
                    本次共导入 {numInfo.product_num} 个产品，
                    {numInfo.service_num} 个服务
                  </p>
                </>
              )}
            </div>

            {importResult && (
              <div
                style={{
                  display: "inline-block",
                  marginLeft: "50%",
                  transform: "translateX(-50%)",
                  marginTop: 40,
                }}
              >
                <p
                  style={{
                    display: "flex",
                    alignItems: "center",
                    fontSize: 16,
                  }}
                >
                  <SyncOutlined
                    spin
                    style={{
                      marginRight: 16,
                    }}
                  />
                  即将进入安装，请稍后 ...
                </p>
              </div>
            )}

            {importResult === false && (
              <div
                style={{
                  display: "inline-block",
                  marginLeft: "50%",
                  transform: "translateX(-50%)",
                  marginTop: 40,
                }}
              >
                <Button
                  style={{ marginRight: 16 }}
                  onClick={() => {
                    setStepNum(0);
                  }}
                >
                  重新上传
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </Modal>
  );
};
