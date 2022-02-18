import {
  OmpContentWrapper,
  OmpTable,
  OmpMessageModal,
  OmpSelect,
  OmpDatePicker,
  OmpDrawer,
} from "@/components";
import { Button, Collapse, Tooltip, Table, Spin } from "antd";
import { fetchGet, fetchPost } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import styles from "./index.module.less";
import {
  CaretRightOutlined,
  QuestionCircleOutlined,
  DownloadOutlined,
} from "@ant-design/icons";
import { useEffect, useRef, useState } from "react";
import { useHistory, useLocation } from "react-router-dom";
import {
  handleResponse,
  _idxInit,
  refreshTime,
  downloadFile,
} from "@/utils/utils";
import moment from "moment";

const { Panel } = Collapse;

const statusTextMap = [
  "等待执行",
  "执行中",
  "执行成功",
  "执行失败",
  "任务超时",
];

const statusColorMap = ["#ffbf00", "#ffbf00", "#76ca68", "#f04134", "#f04134"];

const ToolExecutionResults = () => {
  const history = useHistory();
  const locationArr = useLocation().pathname.split("/");
  const [loading, setLoading] = useState(false);
  const [info, setInfo] = useState({});

  // 当前选中的ip
  const [currentIp, setCurrentIp] = useState(null);
  // 当前选中的状态
  const [currentStatus, setCurrentStatus] = useState(null);

  const tiemr = useRef(null);

  const queryData = (init) => {
    init && setLoading(true);
    fetchGet(
      `${apiRequest.utilitie.queryResult}${
        locationArr[locationArr.length - 1]
      }/`
    )
      .then((res) => {
        handleResponse(res, (res) => {
          setInfo(res.data);
          if (res.data.tool_detail && init) {
            currentIp == null && setCurrentIp(res.data.tool_detail[0].ip);
            currentStatus == null &&
              setCurrentStatus(res.data.tool_detail[0].status);
          }

          // 等待执行 和 执行中 要继续请求
          if (res.data.status == 0 || res.data.status == 1) {
            tiemr.current = setTimeout(() => {
              queryData();
            }, 5000);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        init && setLoading(false);
      });
  };

  // 执行结果当前选中的项
  const currentItem = info.tool_detail?.filter((i) => i.ip == currentIp)[0];

  // 确定执行结果的tab状态
  const tabRenderStatus = (status) => {
    return info.tool_detail?.filter((i) => i.status == status).length;
  };

  useEffect(() => {
    queryData("init");
  }, []);
  return (
    <OmpContentWrapper
      wrapperStyle={{ padding: "10px 30px 30px 30px", backgroundColor: "#fff" }}
    >
      <Spin spinning={loading}>
        <div className={styles.resultTitle}>
          <div style={{ display: "flex" }}>
            {info.task_name || "-"}{" "}
            <span
              className={styles.resultTitleStatus}
              style={{ color: statusColorMap[info.status] }}
            >
              {statusTextMap[info.status]}
            </span>
          </div>
          <a style={{ fontSize: 14 }} onClick={() => history?.goBack()}>
            返回
          </a>
        </div>
        <Collapse
          bordered={false}
          defaultActiveKey={["baseInfo", "executionInfo", "executionResult"]}
          onChange={() => {}}
          style={{ marginTop: 0, border: "none", backgroundColor: "#fff" }}
          expandIcon={({ isActive }) => (
            <CaretRightOutlined rotate={isActive ? 90 : 0} />
          )}
        >
          <Panel
            header="基本信息"
            key="baseInfo"
            className={styles.panelItem}
            style={{ paddingBottom: 1 }}
          >
            <div className={styles.baseTable}>
              <div className={styles.baseTableFirstRow}>
                <div className={styles.baseTableItem}>
                  <div className={styles.baseTableItemLabel}>
                    操作用户{" "}
                    <Tooltip title="执行本次任务的平台用户">
                      <QuestionCircleOutlined
                        style={{
                          cursor: "pointer",
                          fontWeight: 400,
                          marginLeft: 5,
                        }}
                      />
                    </Tooltip>
                  </div>
                  <div className={styles.baseTableItemContent}>
                    {info.operator || "-"}
                  </div>
                </div>
                <div className={styles.baseTableItem}>
                  <div className={styles.baseTableItemLabel}>
                    执行对象{" "}
                    <Tooltip title="实用工具操作的目标对象类型，可以是主机或者具体服务">
                      <QuestionCircleOutlined
                        style={{
                          cursor: "pointer",
                          fontWeight: 400,
                          marginLeft: 5,
                        }}
                      />
                    </Tooltip>
                  </div>
                  <div className={styles.baseTableItemContent}>
                    {info.tool?.target_name || "-"}
                  </div>
                </div>
                <div className={styles.baseTableItem}>
                  <div className={styles.baseTableItemLabel}>
                    目标数量{" "}
                    <Tooltip title="本次执行对象的数量">
                      <QuestionCircleOutlined
                        style={{
                          cursor: "pointer",
                          fontWeight: 400,
                          marginLeft: 5,
                        }}
                      />
                    </Tooltip>
                  </div>
                  <div className={styles.baseTableItemContent}>
                    {info.count || "-"}
                  </div>
                </div>
                <div
                  className={styles.baseTableItem}
                  style={{ borderRight: "none" }}
                >
                  <div className={styles.baseTableItemLabel}>
                    执行用户
                    <Tooltip title="工具在目标主机执行的用户名">
                      <QuestionCircleOutlined
                        style={{
                          cursor: "pointer",
                          fontWeight: 400,
                          marginLeft: 5,
                        }}
                      />
                    </Tooltip>
                  </div>
                  <div className={styles.baseTableItemContent}>
                    {" "}
                    {info.run_user || "-"}
                  </div>
                </div>
              </div>
              <div className={styles.baseTableSecondRow}>
                <div className={styles.baseTableItem}>
                  <div className={styles.baseTableItemLabel}>
                    超时时间 (s)
                    <Tooltip title="工具在目标主机的执行的超时时间">
                      <QuestionCircleOutlined
                        style={{
                          cursor: "pointer",
                          fontWeight: 400,
                          marginLeft: 5,
                        }}
                      />
                    </Tooltip>
                  </div>
                  <div className={styles.baseTableItemContent}>
                    {info.time_out || "-"}
                  </div>
                </div>
                <div className={styles.baseTableItem}>
                  <div className={styles.baseTableItemLabel}>开始时间</div>
                  <div className={styles.baseTableItemContent}>
                    {info.start_time
                      ? moment(info.start_time).format("YYYY-MM-DD HH:mm:ss")
                      : "-"}
                  </div>
                </div>
                <div className={styles.baseTableItem}>
                  <div className={styles.baseTableItemLabel}>结束时间</div>
                  <div className={styles.baseTableItemContent}>
                    {" "}
                    {info.end_time
                      ? moment(info.end_time).format("YYYY-MM-DD HH:mm:ss")
                      : "-"}
                  </div>
                </div>
                <div
                  className={styles.baseTableItem}
                  style={{ borderRight: "none" }}
                >
                  <div className={styles.baseTableItemLabel}>总耗时</div>
                  <div className={styles.baseTableItemContent}>
                    {info.duration || "-"}
                  </div>
                </div>
              </div>
            </div>
          </Panel>
          <Panel
            header="执行参数信息"
            key="executionInfo"
            className={styles.panelItem}
            style={{ marginTop: 25 }}
          >
            <div style={{ border: "1px solid #d6d6d6", marginTop: 10 }}>
              <Table
                size="middle"
                columns={[
                  {
                    title: "参数名称",
                    key: "name",
                    dataIndex: "name",
                    align: "center",
                    width: 120,
                    render: (text) => text || "-",
                  },
                  {
                    title: "参数值",
                    key: "value",
                    dataIndex: "value",
                    width: 120,
                    align: "center",
                    // render: (text) => (text ? argType[text] : "-"),
                  },
                ]}
                pagination={false}
                dataSource={info.tool_args}
              />
            </div>
          </Panel>
          <Panel
            header="执行结果"
            key="executionResult"
            className={styles.panelItem}
            style={{ marginTop: 25 }}
          >
            <div style={{ marginTop: 10 }}>
              <div
                style={{
                  height: 36,
                  width: 450,
                  display: "flex",
                  borderTop: "1px solid #d6d6d6",
                  borderLeft: "1px solid #d6d6d6",
                  borderRight: "1px solid #d6d6d6",
                  backgroundColor: "#fff",
                  position: "relative",
                  top: 1,
                }}
              >
                <div
                  style={{
                    flex: 1,
                    height: 35,
                    lineHeight: "35px",
                    textAlign: "center",
                    color:
                      currentStatus == 0
                        ? "#007bf3"
                        : tabRenderStatus(0) == 0 && "rgba(0, 0, 0, 0.25)",
                    cursor:
                      currentStatus == 0
                        ? "pointer"
                        : tabRenderStatus(0) == 0
                        ? "not-allowed"
                        : "pointer",
                  }}
                  onClick={() => {
                    if (tabRenderStatus(0) !== 0) {
                      setCurrentStatus(0);
                      setCurrentIp(
                        info.tool_detail?.filter((i) => i.status == 0)[0].ip
                      );
                    }
                  }}
                >
                  待执行({tabRenderStatus(0)})
                </div>
                <div
                  style={{
                    flex: 1,
                    height: 35,
                    lineHeight: "35px",
                    textAlign: "center",
                    color:
                      currentStatus == 1
                        ? "#007bf3"
                        : tabRenderStatus(1) == 0 && "rgba(0, 0, 0, 0.25)",
                    cursor:
                      currentStatus == 1
                        ? "pointer"
                        : tabRenderStatus(1) == 0
                        ? "not-allowed"
                        : "pointer",
                  }}
                  onClick={() => {
                    if (tabRenderStatus(1) !== 0) {
                      setCurrentStatus(1);
                      setCurrentIp(
                        info.tool_detail?.filter((i) => i.status == 1)[0].ip
                      );
                    }
                  }}
                >
                  执行中({tabRenderStatus(1)})
                </div>
                <div
                  style={{
                    flex: 1,
                    height: 35,
                    lineHeight: "35px",
                    textAlign: "center",
                    color:
                      currentStatus == 2
                        ? "#007bf3"
                        : tabRenderStatus(2) == 0 && "rgba(0, 0, 0, 0.25)",
                    cursor:
                      currentStatus == 2
                        ? "pointer"
                        : tabRenderStatus(2) == 0
                        ? "not-allowed"
                        : "pointer",
                  }}
                  onClick={() => {
                    if (tabRenderStatus(2) !== 0) {
                      setCurrentStatus(2);
                      setCurrentIp(
                        info.tool_detail?.filter((i) => i.status == 2)[0].ip
                      );
                    }
                  }}
                >
                  执行成功({tabRenderStatus(2)})
                </div>
                <div
                  style={{
                    flex: 1,
                    height: 35,
                    lineHeight: "35px",
                    textAlign: "center",
                    color:
                      currentStatus == 3
                        ? "#007bf3"
                        : tabRenderStatus(3) == 0 && "rgba(0, 0, 0, 0.25)",
                    cursor:
                      currentStatus == 3
                        ? "pointer"
                        : tabRenderStatus(3) == 0
                        ? "not-allowed"
                        : "pointer",
                  }}
                  onClick={() => {
                    if (tabRenderStatus(3) !== 0) {
                      setCurrentStatus(3);
                      setCurrentIp(
                        info.tool_detail?.filter((i) => i.status == 3)[0].ip
                      );
                    }
                  }}
                >
                  执行失败({tabRenderStatus(3)})
                </div>
                <div
                  style={{
                    flex: 1,
                    height: 35,
                    lineHeight: "35px",
                    textAlign: "center",
                    color:
                      currentStatus == 4
                        ? "#007bf3"
                        : tabRenderStatus(4) == 0 && "rgba(0, 0, 0, 0.25)",
                    cursor:
                      currentStatus == 4
                        ? "pointer"
                        : tabRenderStatus(4) == 0
                        ? "not-allowed"
                        : "pointer",
                  }}
                  onClick={() => {
                    if (tabRenderStatus(4) !== 0) {
                      setCurrentStatus(4);
                      setCurrentIp(
                        info.tool_detail?.filter((i) => i.status == 4)[0].ip
                      );
                    }
                  }}
                >
                  任务超时({tabRenderStatus(4)})
                </div>
              </div>
              <div
                style={{
                  height: 400,
                  border: "1px solid #d6d6d6",
                  display: "flex",
                }}
              >
                <div
                  style={{
                    width: 160,
                    height: "100%",
                    overflowY: "auto",
                    // paddingTop: 5,
                  }}
                >
                  {info.tool_detail
                    ?.filter((i) => i.status == currentStatus)
                    .map((item) => {
                      return (
                        <div
                          onClick={() => {
                            setCurrentIp(item.ip);
                          }}
                          style={{
                            cursor: "pointer",
                            padding: "10px 0px",
                            backgroundColor:
                              currentIp == item.ip ? "#2f7bed" : "#fff",
                            color: currentIp == item.ip ? "#fff" : "#37474d",
                            textAlign: "center",
                          }}
                        >
                          {item.ip}
                        </div>
                      );
                    })}
                </div>
                <div
                  style={{
                    flex: 1,
                    height: "100%",
                    backgroundColor: "#f6f6f6",
                    padding: 10,
                  }}
                >
                  {currentItem && currentItem.url && (
                    <Button
                      style={{ marginBottom: 10 }}
                      icon={<DownloadOutlined />}
                      onClick={() => {
                        downloadFile(`/${currentItem.url}`);
                      }}
                    >
                      <span style={{ color: "#818181" }}>下载文件</span>
                    </Button>
                  )}
                  <div
                    style={{
                      height:
                        currentItem && currentItem.url
                          ? "calc(100% - 40px)"
                          : "100%",
                      backgroundColor: "#000000",
                      padding: 20,
                      paddingTop: 25,
                      color: "#fff",
                      wordWrap: "break-word",
                      wordBreak: "break-all",
                      whiteSpace: "pre-line",
                      overflowY: "auto",
                      overflowX: "hidden",
                    }}
                  >
                    {currentItem?.log}
                  </div>
                </div>
              </div>
            </div>
          </Panel>
        </Collapse>
      </Spin>
    </OmpContentWrapper>
  );
};

export default ToolExecutionResults;
