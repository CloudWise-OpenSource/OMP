import "./index.css";
import {
  columnsConfig,
  formatTableRenderData,
  host_port_connectivity_columns,
  kafka_offsets_columns,
  kafka_partition_columns,
  kafka_topic_size_columns,
  handleResponse,
  downloadFile,
} from "@/utils/utils";
import { Card, Collapse, message, Table, Drawer } from "antd";
import * as R from "ramda";
import { useEffect, useState } from "react";
//import data from "./data.json";
import { useHistory, useLocation } from "react-router-dom";
import { fetchGet } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
const { Panel } = Collapse;

const reportColumnConfig = [
  { ...columnsConfig.report_service_name, className: "_bigfontSize" },
  { ...columnsConfig.report_host_ip, className: "_bigfontSize" },
  { ...columnsConfig.report_service_port, className: "_bigfontSize" },
  { ...columnsConfig.report_service_status, className: "_bigfontSize" },
  { ...columnsConfig.report_cpu_usage, className: "_bigfontSize" },
  { ...columnsConfig.report_mem_usage, className: "_bigfontSize" },
  { ...columnsConfig.report_run_time, className: "_bigfontSize" },
  { ...columnsConfig.report_log_level, className: "_bigfontSize" },
  // { ...columnsConfig.report_cluster_name, className: styles._bigfontSize },
];

export default function PatrolInspectionDetail() {
  const title = "巡检报告";

  const location = useLocation();
  const history = useHistory();

  // /const data = localStorage.getItem("recordDetailData");

  let arr = location.pathname.split("/");
  const id = arr[arr.length - 1];
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [drawerText, setDrawerText] = useState("");

  const [expandKey, setExpandKey] = useState([]);

  const [data, setData] = useState({});

  const [loading, setLoading] = useState(false);

  // 是否为主机巡检
  const [isHost, setIsHost] = useState(false);

  const fetchDetailData = (id) => {
    setLoading(true);
    fetchGet(`${apiRequest.inspection.reportDetail}/${id}/`)
      .then((res) => {
        handleResponse(res, (res) => {
          setData(res.data);

          // 通过文件名判断是否为主机巡检
          if (res.data.file_name.indexOf("host") === 0) {
            setIsHost(true);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchDetailData(id);
  }, []);

  if (!data) {
    return <div>数据暂无</div>;
  }

  return (
    <div id="reportContent" className={"reportContent"}>
      <div className={"reportTitle"}>
        <div
          style={{
            width: "100%",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          {title}
        </div>
        <div>
          <div
            className={"goBackElement"}
            id={"invisible"}
            style={{ paddingRight: 10 }}
            onClick={() =>
              history.push("/status-patrol/patrol-inspection-record")
            }
          >
            返回
          </div>
          <div
            id={"invisible"}
            onClick={() => {
              message.success(
                `正在下载巡检报告，双击文件夹中index.html查看报告`
              );
              // download();
              downloadFile(`/download-inspection/${data.file_name}`);
            }}
          >
            导出
          </div>
        </div>
      </div>
      <div>
        <Collapse
          bordered={false}
          defaultActiveKey={[
            "overview",
            "risk",
            "map",
            "host",
            "database",
            "component",
            "service",
          ]}
          style={{ marginTop: 10 }}
          //   expandIcon={({ isActive }) => (
          //     <Icon type="caret-right" rotate={isActive ? 90 : 0} />
          //   )}
        >
          <Panel header="概述信息" key="overview" className={"panelItem"}>
            <div className={"overviewItemWrapper"}>
              <OverviewItem data={data.summary?.task_info} type={"task_info"} />
              <OverviewItem data={data.summary?.time_info} type={"time_info"} />
              <OverviewItem
                data={data.summary?.scan_info}
                type={"scan_info"}
                isHost={isHost}
              />
              <OverviewItem
                data={data.summary?.scan_result}
                type={"scan_result"}
              />
            </div>
          </Panel>

          {/* risks存在，且内部数据任一不为空才显示风险指标一栏 */}
          {data.risks &&
            (!R.isEmpty(data.risks.host_list) ||
              !R.isEmpty(data.risks.service_list)) && (
              <Panel header="风险指标" key="risk" className={"panelItem"}>
                {data.risks.host_list.length > 0 && (
                  <Table
                    style={{ marginTop: 20 }}
                    bordered={true}
                    size={"small"}
                    pagination={false}
                    rowKey={(record, index) => record.id}
                    columns={[
                      {
                        ...columnsConfig.report_idx,
                        className: "_bigfontSize",
                      },
                      {
                        ...columnsConfig.report_host_ip,
                        className: "_bigfontSize",
                      },
                      {
                        ...columnsConfig.report_system,
                        className: "_bigfontSize",
                      },
                      {
                        ...columnsConfig.report_risk_level,
                        className: "_bigfontSize",
                      },
                      {
                        ...columnsConfig.report_risk_describe,
                        className: "_bigfontSize",
                        render: (text) => {
                          return (
                            <span
                              style={{ cursor: "pointer" }}
                              onClick={() => {
                                console.log(text);
                                setDrawerText(text);
                                setDrawerVisible(true);
                              }}
                            >
                              {text}
                            </span>
                          );
                        },
                      },
                      {
                        ...columnsConfig.report_resolve_info,
                        className: "_bigfontSize",
                      },
                    ]}
                    title={() => "主机指标"}
                    dataSource={data.risks.host_list}
                  />
                )}
                {data.risks.service_list.length > 0 && (
                  <Table
                    bordered={true}
                    style={{ marginTop: 20 }}
                    size={"small"}
                    pagination={false}
                    rowKey={(record, index) => record.id}
                    columns={[
                      {
                        ...columnsConfig.report_idx,
                        className: "_bigfontSize",
                      },
                      {
                        ...columnsConfig.report_service_name,
                        className: "_bigfontSize",
                      },
                      {
                        ...columnsConfig.report_host_ip,
                        className: "_bigfontSize",
                      },
                      {
                        ...columnsConfig.report_service_port,
                        className: "_bigfontSize",
                      },
                      {
                        ...columnsConfig.report_risk_level,
                        className: "_bigfontSize",
                      },
                      {
                        ...columnsConfig.report_risk_describe,
                        className: "_bigfontSize",
                        render: (text) => {
                          return (
                            <span
                              style={{ cursor: "pointer" }}
                              onClick={() => {
                                console.log(text);
                                setDrawerText(text);
                                setDrawerVisible(true);
                              }}
                            >
                              {text}
                            </span>
                          );
                        },
                      },
                      {
                        ...columnsConfig.report_resolve_info,
                        className: "_bigfontSize",
                      },
                    ]}
                    title={() => "服务指标"}
                    dataSource={data.risks.service_list}
                  />
                )}
              </Panel>
            )}

          {!R.either(R.isNil, R.isEmpty)(data?.service_topology) && (
            <Panel header="服务平面图" key="map" className={"panelItem"}>
              <div
                style={{ display: "flex", flexFlow: "row wrap", margin: 10 }}
              >
                {R.addIndex(R.map)((item, index) => {
                  return (
                    <PlanChart
                      key={index}
                      title={item?.host_ip}
                      list={item?.service_list}
                      data={data}
                    />
                  );
                }, data?.service_topology)}
              </div>
            </Panel>
          )}

          {!R.either(R.isNil, R.isEmpty)(data.detail_dict?.host) && (
            <Panel header="主机列表" key="host" className={"panelItem"}>
              <Table
                //rowClassName={()=>{return styles.didingyi;}}
                bordered={true}
                size={"small"}
                style={{ marginTop: 20 }}
                scroll={{ x: 1100 }}
                pagination={false}
                rowKey={(record, index) => record.id}
                // defaultExpandAllRows
                columns={[
                  {
                    ...columnsConfig.report_idx,
                    className: "_bigfontSize",
                  },
                  {
                    ...columnsConfig.report_host_ip,
                    className: "_bigfontSize",
                  },
                  {
                    ...columnsConfig.report_release_version,
                    className: "_bigfontSize",
                  },
                  {
                    ...columnsConfig.report_host_massage,
                    className: "_bigfontSize",
                  },
                  {
                    ...columnsConfig.report_cpu_usage,
                    className: "_bigfontSize",
                  },
                  {
                    ...columnsConfig.report_mem_usage,
                    className: "_bigfontSize",
                  },
                  {
                    ...columnsConfig.report_disk_usage_root,
                    className: "_bigfontSize",
                  },
                  {
                    ...columnsConfig.report_disk_usage_data,
                    className: "_bigfontSize",
                  },
                  {
                    ...columnsConfig.report_run_time,
                    className: "_bigfontSize",
                  },
                  {
                    ...columnsConfig.report_sys_load,
                    className: "_bigfontSize",
                  },
                ]}
                //expandedRowKeys={expandKey}
                expandedRowRender={(...arg) => {
                  arg[0].basic = arg[0].basic.filter(
                    (item) => item.name !== "cluster_ip"
                  );
                  return RenderExpandedContent(
                    ...arg,
                    drawerVisible,
                    setDrawerVisible,
                    drawerText,
                    setDrawerText
                  );
                }}
                // onExpand={(expanded, record) => {
                //   //console.log([...expandKey, record.id]);
                //   setExpandKey([...expandKey, record.id]);
                //   //console.log(`selectedRowKeys: ${selectedRowKeys}`, 'selectedRows: ', selectedRows);
                // }}
                dataSource={data.detail_dict.host}
              />
            </Panel>
          )}

          {!R.either(R.isNil, R.isEmpty)(data.detail_dict?.database) && (
            <Panel header="数据库列表" key="database" className={"panelItem"}>
              <Table
                size={"small"}
                bordered={true}
                style={{ marginTop: 20 }}
                pagination={false}
                rowKey={(record, index) => record.id}
                // defaultExpandAllRows
                columns={reportColumnConfig}
                expandedRowRender={(...arg) => {
                  arg[0].basic = arg[0].basic.filter(
                    (item) => item.name !== "cluster_ip"
                  );
                  RenderExpandedContent(
                    ...arg,
                    drawerVisible,
                    setDrawerVisible,
                    drawerText,
                    setDrawerText
                  );
                }}
                dataSource={data.detail_dict.database}
              />
            </Panel>
          )}

          {!R.either(R.isNil, R.isEmpty)(data.detail_dict?.component) && (
            <Panel header="组件列表" key="component" className={"panelItem"}>
              <Table
                size={"small"}
                bordered={true}
                style={{ marginTop: 20 }}
                pagination={false}
                rowKey={(record, index) => record.id}
                // defaultExpandAllRows
                columns={reportColumnConfig}
                expandedRowRender={(...arg) => {
                  arg[0].basic = arg[0].basic.filter(
                    (item) => item.name !== "cluster_ip"
                  );
                  return RenderExpandedContent(
                    ...arg,
                    drawerVisible,
                    setDrawerVisible,
                    drawerText,
                    setDrawerText
                  );
                }}
                dataSource={data.detail_dict.component}
              />
            </Panel>
          )}

          {!R.either(R.isNil, R.isEmpty)(data.detail_dict?.service) && (
            <Panel header="服务列表" key="service" className={"panelItem"}>
              <Table
                size={"small"}
                bordered={true}
                style={{ marginTop: 20 }}
                pagination={false}
                rowKey={(record, index) => record.id}
                // defaultExpandAllRows
                columns={reportColumnConfig}
                expandedRowRender={(...arg) => {
                  arg[0].basic = arg[0].basic.filter(
                    (item) => item.name !== "cluster_ip"
                  );
                  return RenderExpandedContent(
                    ...arg,
                    drawerVisible,
                    setDrawerVisible,
                    drawerText,
                    setDrawerText
                  );
                }}
                dataSource={data.detail_dict.service}
              />
            </Panel>
          )}
        </Collapse>
      </div>
      <Drawer
        title="进程日志"
        placement="right"
        closable={false}
        onClose={() => setDrawerVisible(false)}
        visible={drawerVisible}
        width={720}
        destroyOnClose
      >
        {drawerText}
      </Drawer>
    </div>
  );
}

function formatTime(text = 0) {
  let duration = text;
  const second = Math.round(Number(text)),
    days = Math.floor(second / 86400),
    hours = Math.floor((second % 86400) / 3600),
    minutes = Math.floor(((second % 86400) % 3600) / 60),
    seconds = Math.floor(((second % 86400) % 3600) % 60);

  if (days > 0) {
    duration = days + "天" + hours + "小时" + minutes + "分" + seconds + "秒";
  } else if (hours > 0) {
    duration = hours + "小时" + minutes + "分" + seconds + "秒";
  } else if (minutes > 0) {
    duration = minutes + "分" + seconds + "秒";
  } else if (seconds > 0) {
    duration = seconds + "秒";
  }

  return duration;
}

// 概览信息
function OverviewItem({ data, type, isHost = false }) {
  switch (type) {
    case "task_info":
      return (
        <div className={"overviewItem"}>
          <div>任务信息</div>
          <div>
            <div>任务名称：{data?.task_name}</div>
            <div>操作人员：{data?.operator}</div>
            <div>任务状态：{data?.task_status === 2 ? "已完成" : "失败"}</div>
          </div>
        </div>
      );
    case "time_info":
      return (
        <div className={"overviewItem"}>
          <div>时间统计</div>
          <div>
            <div>开始时间：{data?.start_time}</div>
            <div>结束时间：{data?.end_time}</div>
            <div>任务耗时：{formatTime(data?.cost)}</div>
          </div>
        </div>
      );
    case "scan_info":
      return (
        <div className={"overviewItem"}>
          <div>扫描统计</div>
          <div style={{ display: "flex", alignItems: "center" }}>
            <div>
              {data?.host >= 0 && <div>主机个数：{data.host}台</div>}
              {/* {data?.component >= 0 && <div>组件个数：{data.component}个</div>} */}
              {data?.service >= 0 && <div>服务个数：{data.service}个</div>}
            </div>
          </div>
        </div>
      );
    case "scan_result":
      return (
        <div className={"overviewItem"}>
          <div>分析结果</div>
          <div style={{ display: "flex", alignItems: "center" }}>
            <div>
              <div>总指标数：{data?.all_target_num}</div>
              <div>异常指标：{data?.abnormal_target}</div>
              {/* <div>健康度：{data.healthy}</div> */}
            </div>
          </div>
        </div>
      );
  }
}

//平面图
function PlanChart({ title, list, data }) {
  return (
    <div className={"planChartWrapper"}>
      <div className={"planChartTitle"}>
        <span className={"planChartTitleCircular"} />
        {title}
      </div>
      <div className={"planChartBlockWrapper"}>
        {list?.map((item) => {
          return (
            <div className={"stateButton"} key={item}>
              <div>{item}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// Table渲染的子项
// 注：此处需要针对特殊属性渲染额外效果，故将已在table渲染过的属性单独拿出来
function RenderExpandedContent(
  {
    basic,
    host_ip,
    service_status,
    run_time,
    log_level,
    mem_usage,
    cpu_usage,
    service_name,
    service_port,
    cluster_name,
    release_version,
    host_massage,
    disk_usage_root,
    disk_usage_data,
    sys_load,
    ...specialProps
  },
  ...arg
) {
  const { topic_partition, kafka_offsets, topic_size } = specialProps;

  let [drawerVisible, setDrawerVisible, drawerText, setDrawerText] =
    arg.slice(-4);

  const formattedData = Object.entries(specialProps).filter((item) =>
    Array.isArray(item[1])
  );

  /* eslint-disable */
  let deal_host_memory_top_columns = [
    {
      title: "TOP",
      dataIndex: "TOP",
      //ellipsis: true,
      width: 50,
      className: "_bigfontSize",
    },
    {
      title: "PID",
      dataIndex: "PID",
      //ellipsis: true,
      align: "center",
      width: 100,
      className: "_bigfontSize",
    },
    {
      title: "使用率",
      dataIndex: "P_RATE",
      //ellipsis: true,
      align: "center",
      width: 100,
      className: "_bigfontSize",
    },
    {
      title: "进程",
      dataIndex: "P_CMD",
      ellipsis: true,
      className: "_bigfontSize",
      render: (text) => {
        return (
          <span
            style={{ cursor: "pointer" }}
            onClick={() => {
              setDrawerText(text);
              setDrawerVisible(true);
            }}
          >
            {text}
          </span>
        );
      },
    },
  ];
  /* eslint-disable */
  const contentMap = {
    // 主机列表
    port_connectivity: {
      columns: host_port_connectivity_columns,
      dataSource: specialProps.port_connectivity,
      title: "端口连通性",
    },
    memory_top: {
      columns: deal_host_memory_top_columns,
      dataSource: specialProps.memory_top,
      title: "内存使用率Top10进程",
    },
    cpu_top: {
      columns: deal_host_memory_top_columns,
      dataSource: specialProps.cpu_top,
      title: "cpu使用率Top10进程",
    },
    kernel_parameters: {
      columns: [],
      dataSource: specialProps.kernel_parameters,
      title: "内核参数",
    },
    //  服务列表
    topic_partition: {
      columns: kafka_partition_columns,
      dataSource: specialProps.topic_partition,
      title: "分区信息",
    },
    kafka_offsets: {
      columns: kafka_offsets_columns,
      dataSource: specialProps.kafka_offsets,
      title: "消费位移信息",
    },
    topic_size: {
      columns: kafka_topic_size_columns,
      dataSource: specialProps.topic_size,
      title: "Topic消息大小",
    },
  };

  return (
    <div className={"expandedRowWrapper"}>
      {Array.isArray(basic) && <BasicCard basic={basic} />}
      {formattedData.length > 0 && (
        <Collapse
          defaultActiveKey={R.keys(specialProps)}
          style={{ marginTop: 10 }}
          //   expandIcon={({ isActive }) => (
          //     <Icon type="caret-right" rotate={isActive ? 90 : 0} />
          //   )}
        >
          {formattedData.map((item, idx) => {
            // 根据当前渲染项，找到对应的content配置数据
            const currentContent = contentMap[item[0]];

            // 只取目前已经配置了的数据
            if (!R.isNil(currentContent)) {
              return (
                <Panel header={currentContent.title} key={item[0]}>
                  {currentContent.columns.length > 0 ? (
                    <Table
                      bordered={true}
                      rowKey={(record, index) => record.id}
                      size={"small"}
                      columns={currentContent.columns}
                      dataSource={currentContent.dataSource}
                      pagination={false}
                    />
                  ) : (
                    <div className={"basicCardWrapper"}>
                      {currentContent.dataSource.map((item, idx) => {
                        return (
                          <div key={idx} className={"basicCardItem"}>
                            {item}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </Panel>
              );
            } else {
              //   todo 其他数据项
              console.log("未配置的数据项", item);
            }
          })}
        </Collapse>
      )}
      <Drawer
        title="进程日志"
        placement="right"
        closable={false}
        onClose={() => setDrawerVisible(false)}
        visible={drawerVisible}
        width={720}
        destroyOnClose
      >
        {drawerText}
      </Drawer>
    </div>
  );
}

// 卡片面板
function BasicCard({ basic }) {
  return (
    <Card>
      <div className={"basicCardWrapper"}>
        {basic.map((item, idx) => (
          <div key={idx} className={"basicCardItem"}>
            <span style={{ color: "#333" }}>{item.name_cn}: </span>
            <span>{formatTableRenderData(JSON.stringify(item.value))}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}
