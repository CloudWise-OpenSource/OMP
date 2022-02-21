//import { ColorfulNotice } from "@/components";
import { Badge, message, Tooltip } from "antd";
import moment from "moment";
import * as R from "ramda";
import styles from "./index.module.less";
import { getRefreshTimeChangeAction } from "@/components/CustomBreadcrumb/store/actionsCreators";
import { CloseCircleFilled } from "@ant-design/icons";

/**
 * 正常/绿色  bg"rgb(238, 250, 244)"  bo:"rgb(84, 187, 166)"
 * 异常/红色     "#da4e48", "#fbe7e6"
 * 警告/黄色      rgba(247, 231, 24,.2)" borderColor="#f5c773"
 */

/**
 * 统一的分页配置项
 * @param data
 * @returns {{total, pageSizeOptions: [string, string, string, string], showTotal: (function(): string), showSizeChanger: boolean}}
 */
/*eslint-disable*/
export const paginationConfig = (data) => ({
  showSizeChanger: true,
  pageSizeOptions: ["10", "20", "50", "100"],
  showTotal: () => (
    <span style={{ color: "rgb(152, 157, 171)" }}>
      共计 <span style={{ color: "rgb(63, 64, 70)" }}>{data.length}</span> 条
    </span>
  ),
  total: data.length,
  // onShowSizeChange: (current, pageSize) => this.changePageSize(pageSize, current),
  // onChange: (current) => this.changePage(current),
});
/*eslint-disable*/
export const isTableTextInvalid = (text) =>
  String(text) === "null" || text === "" || text === undefined;

/**
 * 格式化 table 渲染项
 * @param text
 * @param record
 * @param index
 * @returns {JSX.Element|string|*}
 */
export function formatTableRenderData(text, record, index) {
  if (isTableTextInvalid(text)) {
    return "-";
  } else if (text === 0 || text === "active" || text === true) {
    return (
      <div>{renderCircular("rgb(84, 187, 166)", "rgb(238, 250, 244)")}正常</div>
    );
  } else if (text === 1 || text === "unactive" || text === false) {
    return <div>{renderCircular("#da4e48", "#fbe7e6")}异常</div>;
  } else if (text === "CREATE") {
    return "增加";
  } else if (text === "UPDATE") {
    return "更新";
  } else if (text === "DELETE") {
    return "删除";
  } else {
    // /console.log("text",text);
    return text;
  }
}

function report_service_RenderData(text, record, index) {
  if (text) {
    return text;
  } else {
    return "-";
  }
}

export function renderFormattedTime(text, record, index) {
  {
    if (isTableTextInvalid(text)) {
      return "-";
    } else {
      let duration = "";
      const second = Math.round(Number(text)),
        days = Math.floor(second / 86400),
        hours = Math.floor((second % 86400) / 3600),
        minutes = Math.floor(((second % 86400) % 3600) / 60),
        seconds = Math.floor(((second % 86400) % 3600) % 60);

      if (days > 0) {
        duration = days + "天" + hours + "小时";
      } else if (hours > 0) {
        duration = hours + "小时" + minutes + "分";
      } else if (minutes > 0) {
        duration = minutes + "分";
      } else if (seconds > 0) {
        duration = seconds + "秒";
      }

      return duration;
    }
  }
}

export function renderInformation(text, record, index) {
  const { cpu, memory, disk } = record;
  const unit = 1024 * 1024 * 1024;

  const cpuText = isTableTextInvalid(cpu) ? "-" : `${cpu}C`;
  const memoryText = isTableTextInvalid(memory)
    ? "-"
    : `${(memory / unit).toFixed(1)}G`;
  const diskText = isTableTextInvalid(disk)
    ? "-"
    : `${(disk / unit).toFixed(1)}G`;

  if (cpuText === "-" && memoryText === "-" && diskText === "-") {
    return "-";
  }

  return `${cpuText}|${memoryText}|${diskText}`;
}

//小圆点
export const renderCircular = (borderColor, backgroundColor) => {
  return (
    <span
      style={{
        width: 10,
        height: 10,
        borderStyle: "solid",
        borderWidth: 2,
        borderColor,
        backgroundColor,
        display: "inline-block",
        marginRight: 5,
        borderRadius: "50%",
      }}
    ></span>
  );
};

export function ColorfulNotice({
  backgroundColor,
  borderColor,
  text,
  top,
  width = 55,
}) {
  //if(top)console.log("top",top);
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        width,
        height: 20,
        margin: "0 auto",
        //color: "white",
        color: "rgba(0, 0, 0, 0.6)",
        fontSize: "12px",
        borderRadius: "4px",
        border: "1px solid #fff",
        backgroundColor,
        borderColor,
        position: "relative",
        top,
      }}
      // className={styles.warningNotice}
    >
      {text}
    </div>
  );
}

/**
 * table组件中ip排序
 * @param a
 * @param b
 * @returns {number}
 */
export const tableSorter = {
  sortIP: (a, b) => {
    if (!a.ip || !b.ip) return 0;

    const ip1 = a.ip
      .split(".")
      .map((el) => el.padStart(3, "0"))
      .join("");
    const ip2 = b.ip
      .split(".")
      .map((el) => el.padStart(3, "0"))
      .join("");
    return ip1 - ip2;
  },
  sortAlertIP: (a, b) => {
    if (!a.alert_host_ip || !b.alert_host_ip) return 0;

    const ip1 = a.alert_host_ip
      .split(".")
      .map((el) => el.padStart(3, "0"))
      .join("");
    const ip2 = b.alert_host_ip
      .split(".")
      .map((el) => el.padStart(3, "0"))
      .join("");
    return ip1 - ip2;
  },
  sortUsageRate: (a, b) => {
    return (
      Number(isTableTextInvalid(a) ? 0 : a) -
      Number(isTableTextInvalid(b) ? 0 : b)
    );
  },
};

export function renderToolTip(text) {
  return (
    <Tooltip title={text}>
      <div
        style={{
          overflow: "hidden",
          whiteSpace: "nowrap",
          textOverflow: "ellipsis",
        }}
      >
        {text}
      </div>
    </Tooltip>
  );
}

// 汇总了所有无需额外逻辑的 table配置项
export const columnsConfig = {
  idx: {
    title: "序列",
    key: "index",
    render: (text, record, index) => `${index + 1}`,
    align: "center",
    width: 60,
    //ixed: "left",
  },
  product_name: {
    title: "服务类型",
    //width: 150,
    key: "product_name",
    dataIndex: "product_name",
    //ellipsis: true,
    sorter: (a, b) => {
      const str1 = R.defaultTo(" ", a.product_name);
      const str2 = R.defaultTo(" ", b.product_name);
      return (
        str1.toLowerCase().charCodeAt(0) - str2.toLowerCase().charCodeAt(0)
      );
    },
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: formatTableRenderData,
  },
  functional_module: {
    title: "功能模块",
    width: 120,
    key: "product_cn_name",
    dataIndex: "product_cn_name",
    //ellipsis: true,
    sorter: (a, b) => {
      const str1 = R.defaultTo(" ", a.product_cn_name);
      const str2 = R.defaultTo(" ", b.product_cn_name);
      return (
        str1.toLowerCase().charCodeAt(0) - str2.toLowerCase().charCodeAt(0)
      );
    },
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: formatTableRenderData,
  },
  alert_service_type: {
    title: "功能模块",
    width: 120,
    key: "alert_service_type",
    dataIndex: "alert_service_type",
    //ellipsis: true,
    sorter: (a, b) => {
      const str1 = R.defaultTo(" ", a.alert_service_type);
      const str2 = R.defaultTo(" ", b.alert_service_type);
      return (
        str1.toLowerCase().charCodeAt(0) - str2.toLowerCase().charCodeAt(0)
      );
    },
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: formatTableRenderData,
  },
  service_name: {
    title: "服务名称",
    width: 180,
    key: "service_name",
    dataIndex: "service_name",
    //ellipsis: true,
    sorter: (a, b) => {
      const str1 = R.defaultTo(" ", a.service_name);
      const str2 = R.defaultTo(" ", b.service_name);
      return (
        str1.toLowerCase().charCodeAt(0) - str2.toLowerCase().charCodeAt(0)
      );
    },
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: formatTableRenderData,
  },
  alert_service_name: {
    title: "服务名称",
    width: 160,
    key: "alert_service_name",
    dataIndex: "alert_service_name",
    ellipsis: true,
    sorter: (a, b) => {
      const str1 = R.defaultTo(" ", a.alert_service_name);
      const str2 = R.defaultTo(" ", b.alert_service_name);
      return (
        str1.toLowerCase().charCodeAt(0) - str2.toLowerCase().charCodeAt(0)
      );
    },
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: formatTableRenderData,
  },
  ip: {
    title: "IP地址",
    width: 160,
    key: "ip",
    dataIndex: "ip",
    //ellipsis: true,
    sorter: tableSorter.sortIP,
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: formatTableRenderData,
  },
  thirdParty_ip: {
    title: "连接地址",
    //width: 120,
    key: "ip",
    dataIndex: "ip",
    //ellipsis: true,
    sorter: tableSorter.sortIP,
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: formatTableRenderData,
  },
  alert_host_ip: {
    title: "IP地址",
    width: 80,
    key: "alert_host_ip",
    dataIndex: "alert_host_ip",
    //ellipsis: true,
    sorter: tableSorter.sortAlertIP,
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: formatTableRenderData,
  },
  alert_level: {
    title: "告警级别",
    width: 100,
    key: "alert_level",
    dataIndex: "alert_level",
    //ellipsis: true,
    sorter: (a, b) => {
      const str1 = R.defaultTo(" ", a.alert_level);
      const str2 = R.defaultTo(" ", b.alert_level);
      return (
        str1.toLowerCase().charCodeAt(0) - str2.toLowerCase().charCodeAt(0)
      );
    },
    render: function renderFunc(text, record, index) {
      switch (record.alert_level) {
        case "critical":
          return (
            <ColorfulNotice
              borderColor={"#da4e48"}
              backgroundColor="#fbe7e6"
              text={"严重"}
            />
          );
        case "warning":
          return (
            <ColorfulNotice
              borderColor={"#f5c773"}
              backgroundColor="rgba(247, 231, 24,.2)"
              text={"警告"}
            />
          );
        default:
          return "-";
      }
    },
    sortDirections: ["descend", "ascend"],
    align: "center",
  },
  alert_describe: {
    title: "告警描述",
    key: "alert_describe",
    dataIndex: "alert_describe",
    width: 280,
    align: "center",
    ellipsis: true,
    render: renderToolTip,
  },
  alert_time: {
    title: "告警时间",
    width: 140,
    key: "alert_time",
    dataIndex: "alert_time",
    //ellipsis: true,
    sorter: (a, b) =>
      moment(a.alert_time).valueOf() - moment(b.alert_time).valueOf(),
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: formatTableRenderData,
  },
  // 告警记录中的告警时间，使用创建时间字段
  warning_record_alert_time: {
    title: "告警时间",
    width: 180,
    key: "alert_time",
    dataIndex: "create_time",
    //ellipsis: true,
    sorter: (a, b) =>
      moment(a.create_time).valueOf() - moment(b.create_time).valueOf(),
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: formatTableRenderData,
  },
  alert_receiver: {
    title: "告警推送",
    //width: 150,
    key: "alert_receiver",
    dataIndex: "alert_receiver",
    //ellipsis: true,
    align: "center",
    render: renderToolTip,
  },
  alert_resolve: {
    title: "解决方案",
    key: "alert_resolve",
    dataIndex: "alert_resolve",
    //width: 100,
    //ellipsis: true,
    align: "center",
    render: formatTableRenderData,
  },
  operating_system: {
    title: "操作系统",
    //width: 130,
    key: "operating_system",
    dataIndex: "operating_system",
    //ellipsis: true,
    align: "center",
    render: formatTableRenderData,
  },
  alert_host_system: {
    title: "操作系统",
    //width: 130,
    key: "alert_host_system",
    dataIndex: "alert_host_system",
    //ellipsis: true,
    align: "center",
    render: formatTableRenderData,
  },
  port: {
    title: "端口",
    //width: 100,
    key: "port",
    dataIndex: "port",
    //ellipsis: true,
    sorter: (a, b) => a.port - b.port,
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: formatTableRenderData,
  },
  service_port: {
    title: "端口",
    //width: 100,
    key: "service_port",
    dataIndex: "service_port",
    //ellipsis: true,
    sorter: (a, b) => a.service_port - b.service_port,
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: formatTableRenderData,
  },
  service_version: {
    title: "服务版本",
    //width: 120,
    key: "service_version",
    dataIndex: "service_version",
    //ellipsis: true,
    align: "center",
    render: formatTableRenderData,
  },
  configuration_information: {
    title: "配置信息",
    //width: 120,
    key: "configuration_information",
    dataIndex: "configuration_information",
    //ellipsis: true,
    align: "center",
    render: renderInformation,
  },
  cpu_rate: {
    title: "CPU使用率",
    width: 110,
    key: "cpu_rate",
    dataIndex: "cpu_rate",
    //ellipsis: true,
    sorter: (a, b) => tableSorter.sortUsageRate(a.cpu_rate, b.cpu_rate),
    render: (text, record, index) => {
      if (isTableTextInvalid(text)) return <div>-</div>;
      const _num = Number(Number(text).toFixed(2));
      if (record.cpu_rate_check === "normal") {
        return (
          <ColorfulNotice
            backgroundColor="rgb(238, 250, 244)"
            borderColor="rgb(84, 187, 166)"
            text={`${_num}%`}
            top={1}
          />
        );
      } else if (record.cpu_rate_check === "critical") {
        return (
          <ColorfulNotice
            backgroundColor={"#fbe7e6"}
            borderColor="#da4e48"
            text={`${_num}%`}
            top={1}
          />
        );
      } else if (record.cpu_rate_check === "warning") {
        return (
          <ColorfulNotice
            backgroundColor="rgba(247, 231, 24,.2)"
            borderColor="#f5c773"
            text={`${_num}%`}
            top={1}
          />
        );
      } else {
        return (
          <ColorfulNotice
            backgroundColor="rgb(238, 250, 244)"
            borderColor="rgb(84, 187, 166)"
            text={`${_num}%`}
            top={1}
          />
        );
      }
    },
    sortDirections: ["descend", "ascend"],
    align: "center",
  },
  disk_rate: {
    title: "(根分区)使用率",
    width: 150,
    key: "disk_rate",
    dataIndex: "disk_rate",
    //ellipsis: true,
    sorter: (a, b) => tableSorter.sortUsageRate(a.disk_rate, b.disk_rate),
    render: (text, record, index) => {
      if (isTableTextInvalid(text)) return <div>-</div>;
      const _num = Number(Number(text).toFixed(2));
      if (record.disk_rate_check === "normal") {
        return (
          <ColorfulNotice
            backgroundColor="rgb(238, 250, 244)"
            borderColor="rgb(84, 187, 166)"
            top={1}
            text={`${_num}%`}
          />
        );
      } else if (record.disk_rate_check === "critical") {
        return (
          <ColorfulNotice
            backgroundColor={"#fbe7e6"}
            borderColor="#da4e48"
            text={`${_num}%`}
            top={1}
          />
        );
      } else if (record.disk_rate_check === "warning") {
        return (
          <ColorfulNotice
            backgroundColor="rgba(247, 231, 24,.2)"
            borderColor="#f5c773"
            text={`${_num}%`}
            top={1}
          />
        );
      } else {
        return (
          <ColorfulNotice
            backgroundColor={"rgb(238, 250, 244)"}
            borderColor="rgb(84, 187, 166)"
            text={`${_num}%`}
            top={1}
          />
        );
      }
    },
    sortDirections: ["descend", "ascend"],
    align: "center",
  },
  disk_data_rate: {
    title: "(数据分区)使用率",
    width: 160,
    key: "disk_data_rate",
    dataIndex: "disk_data_rate",
    //ellipsis: true,
    sorter: (a, b) =>
      tableSorter.sortUsageRate(a.disk_data_rate, b.disk_data_rate),
    render: (text, record, index) => {
      if (isTableTextInvalid(text)) return <div>-</div>;
      const _num = Number(Number(text).toFixed(2));
      if (record.disk_data_check === "normal") {
        return (
          <ColorfulNotice
            backgroundColor={"rgb(238, 250, 244)"}
            borderColor="rgb(84, 187, 166)"
            text={`${_num}%`}
            top={1}
          />
        );
      } else if (record.disk_data_check === "critical") {
        return (
          <ColorfulNotice
            backgroundColor={"#fbe7e6"}
            borderColor="#da4e48"
            text={`${_num}%`}
            top={1}
          />
        );
      } else if (record.disk_data_check === "warning") {
        return (
          <ColorfulNotice
            backgroundColor="rgba(247, 231, 24,.2)"
            borderColor="#f5c773"
            text={`${_num}%`}
            top={1}
          />
        );
      } else {
        return (
          <ColorfulNotice
            backgroundColor={"rgb(238, 250, 244)"}
            borderColor="rgb(84, 187, 166)"
            text={`${_num}%`}
            top={1}
          />
        );
      }
    },
    sortDirections: ["descend", "ascend"],
    align: "center",
  },

  memory_rate: {
    title: "内存使用率",
    width: 100,
    key: "memory_rate",
    dataIndex: "memory_rate",
    //ellipsis: true,
    sorter: (a, b) => tableSorter.sortUsageRate(a.memory_rate, b.memory_rate),
    render: (text, record, index) => {
      if (isTableTextInvalid(text)) return <div>-</div>;
      const _num = Number(Number(text).toFixed(2));
      if (record.memory_rate_check === "normal") {
        return (
          <ColorfulNotice
            backgroundColor={"rgb(238, 250, 244)"}
            borderColor="rgb(84, 187, 166)"
            text={`${_num}%`}
            top={1}
          />
        );
      } else if (record.memory_rate_check === "critical") {
        return (
          <ColorfulNotice
            backgroundColor={"#fbe7e6"}
            borderColor="#da4e48"
            text={`${_num}%`}
            top={1}
          />
        );
      } else if (record.memory_rate_check === "warning") {
        return (
          <ColorfulNotice
            backgroundColor="rgba(247, 231, 24,.2)"
            borderColor="#f5c773"
            text={`${_num}%`}
            top={1}
          />
        );
      } else {
        return (
          <ColorfulNotice
            backgroundColor={"rgb(238, 250, 244)"}
            borderColor="rgb(84, 187, 166)"
            text={`${_num}%`}
            top={1}
          />
        );
      }
    },
    sortDirections: ["descend", "ascend"],
    align: "center",
  },
  running_time: {
    title: "运行时间",
    key: "running_time",
    width: 120,
    dataIndex: "running_time",
    //ellipsis: true,
    sorter: (a, b) =>
      Number(isTableTextInvalid(a.running_time) ? 0 : a.running_time) -
      Number(isTableTextInvalid(b.running_time) ? 0 : b.running_time),
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: renderFormattedTime,
  },
  ssh_state: {
    title: "SSH状态",
    width: 140,
    key: "ssh_state",
    dataIndex: "ssh_state",
    //ellipsis: true,
    align: "center",
    render: (text, record, index) => {
      if (isTableTextInvalid(text)) {
        return "-";
      } else if (text === 0) {
        return (
          <div>
            {renderCircular("rgb(84, 187, 166)", "rgb(238, 250, 244)")}启用
          </div>
        );
      } else if (text === 1) {
        return <div>{renderCircular("#da4e48", "#fbe7e6")}禁用</div>;
      } else {
        return text;
      }
    },
  },
  agent_state: {
    title: "Agent状态",
    width: 140,
    key: "agent_state",
    dataIndex: "agent_state",
    //ellipsis: true,
    align: "center",
    render: (text, record, index) => {
      if (isTableTextInvalid(text)) {
        return "-";
      } else if (text === 0) {
        return (
          <div>
            {renderCircular("rgb(84, 187, 166)", "rgb(238, 250, 244)")}正常
          </div>
        );
      } else if (text === 1) {
        return "安装中";
      } else if (text === 2) {
        return "未安装";
      } else if (text === 3) {
        return <div>{renderCircular("#da4e48", "#fbe7e6")}异常</div>;
      } else {
        return text;
      }
    },
  },
  cluster_name: {
    title: "集群名称",
    //width: 120,
    key: "cluster_name",
    dataIndex: "cluster_name",
    //ellipsis: true,
    sorter: (a, b) => {
      const str1 = R.defaultTo(" ", a.cluster_name);
      const str2 = R.defaultTo(" ", b.cluster_name);
      return (
        str1.toLowerCase().charCodeAt(0) - str2.toLowerCase().charCodeAt(0)
      );
    },
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: formatTableRenderData,
  },
  linkAddress: {
    title: "连接地址",
    //width: 150,
    key: "linkAddress",
    dataIndex: "linkAddress",
    //ellipsis: true,
    align: "center",
    render: formatTableRenderData,
  },
  cluster_mode: {
    title: "集群模式",
    //width: 120,
    key: "cluster_mode",
    dataIndex: "cluster_mode",
    //ellipsis: true,
    align: "center",
    render: formatTableRenderData,
  },
  quote: {
    title: "已引用",
    //width: 120,
    key: "quote",
    dataIndex: "quote",
    //ellipsis: true,
    align: "center",
    render: (text) => (text === 0 ? "否" : "是"),
  },
  created_at: {
    title: "添加时间",
    //width: 120,
    key: "created_at",
    dataIndex: "created_at",
    //ellipsis: true,
    sorter: (a, b) => a - b,
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: formatTableRenderData,
  },
  username: {
    title: "用户名",
    width: 120,
    key: "username",
    dataIndex: "username",
    //ellipsis: true,
    sorter: (a, b) => {
      const str1 = R.defaultTo(" ", a.username);
      const str2 = R.defaultTo(" ", b.username);
      return str1.charCodeAt(0) - str2.charCodeAt(0);
    },
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: formatTableRenderData,
  },
  role: {
    title: "角色",
    width: 120,
    key: "role",
    dataIndex: "role",
    //ellipsis: true,
    sorter: (a, b) => {
      const str1 = R.defaultTo(" ", a.role);
      const str2 = R.defaultTo(" ", b.role);
      return str1.charCodeAt(0) - str2.charCodeAt(0);
    },
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: formatTableRenderData,
  },
  login_time: {
    title: "登入时间",
    width: 180,
    key: "login_time",
    dataIndex: "login_time",
    //ellipsis: true,
    sorter: (a, b) =>
      moment(a.login_time).valueOf() - moment(b.login_time).valueOf(),
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: formatTableRenderData,
  },
  datetime: {
    title: "操作时间",
    width: 150,
    key: "datetime",
    dataIndex: "datetime",
    //ellipsis: true,
    sorter: (a, b) =>
      moment(a.datetime).valueOf() - moment(b.datetime).valueOf(),
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: formatTableRenderData,
  },
  status: {
    title: "用户状态",
    width: 160,
    key: "status",
    dataIndex: "status",
    //ellipsis: true,
    align: "center",
    render: formatTableRenderData,
  },
  date_joined: {
    title: "创建时间",
    width: 120,
    key: "date_joined",
    dataIndex: "date_joined",
    //ellipsis: true,
    align: "center",
    render: formatTableRenderData,
  },
  desc: {
    title: "描述",
    width: 220,
    key: "desc",
    dataIndex: "desc",
    //ellipsis: true,
    align: "center",
    render: formatTableRenderData,
  },
  action: {
    title: "操作类型",
    width: 120,
    key: "action",
    dataIndex: "action",
    //ellipsis: true,
    align: "center",
    render: formatTableRenderData,
  },
  permission_count: {
    title: "权限个数",
    width: 120,
    key: "permission_count",
    dataIndex: "permission_count",
    //ellipsis: true,
    align: "center",
    render: formatTableRenderData,
  },

  // 巡检报告
  inspection_operator: {
    title: "操作员",
    width: 80,
    key: "inspection_operator",
    dataIndex: "inspection_operator",
    //ellipsis: true,
    sorter: (a, b) =>
      a.inspection_operator.charCodeAt(0) - b.inspection_operator.charCodeAt(0),
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: formatTableRenderData,
  },
  inspection_status: {
    title: "巡检结果",
    width: 150,
    key: "inspection_status",
    dataIndex: "inspection_status",
    //ellipsis: true,
    sorter: (a, b) => a.inspection_status - b.inspection_status,
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: (text, record, index) => {
      if (isTableTextInvalid(text)) {
        return "-";
      } else if (text === 2) {
        return <div>{renderCircular("#6cbe7b", "#e8f5eb")}成功</div>;
      } else if (text === 1) {
        return "进行中";
      } else if (text === 0) {
        return "未开始";
      } else if (text === 3) {
        return <div>{renderCircular("#da4e48", "#fbe7e6")}失败</div>;
      } else {
        return text;
      }
    },
  },
  run_status: {
    title: "执行结果",
    width: 120,
    key: "inspection_status",
    dataIndex: "inspection_status",
    //ellipsis: true,
    sorter: (a, b) => a.inspection_status - b.inspection_status,
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: (text, record, index) => {
      if (isTableTextInvalid(text)) {
        return "-";
      } else if (text === 2) {
        return <div>{renderCircular("#6cbe7b", "#e8f5eb")}成功</div>;
      } else if (text === 1) {
        return "进行中";
      } else if (text === 0) {
        return "未开始";
      } else if (text === 3) {
        return <div>{renderCircular("#da4e48", "#fbe7e6")}失败</div>;
      } else {
        return text;
      }
    },
  },

  service_status: {
    title: "业务状态",
    //width: 120,
    key: "service_status",
    dataIndex: "service_status",
    //ellipsis: true,
    sorter: (a, b) => a.service_status - b.service_status,
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: formatTableRenderData,
  },
  // 产品管理-服务管理中新增的字段
  product_service_status: {
    title: "运行状态",
    width: 120,
    key: "product_service_status",
    dataIndex: "service_status",
    //ellipsis: true,
    align: "center",
    render: (text, record, index) => {
      if (isTableTextInvalid(text)) {
        return "-";
      } else if (text === 0) {
        return (
          <div>{renderCircular("#f5c773", "rgba(247, 231, 24,.2)")}未安装</div>
        );
        //return <div style={{ color: "#389e0d" }}>运行</div>;
      } else if (text === 1) {
        return (
          <div>{renderCircular("#f5c773", "rgba(247, 231, 24,.2)")}安装中</div>
        );
      } else if (text === 2) {
        return (
          <div>
            {renderCircular("rgb(84, 187, 166)", "rgb(238, 250, 244)")}正常
          </div>
        );
      } else if (text === 3) {
        return <div>{renderCircular("#da4e48", "#fbe7e6")}异常</div>;
      } else if (text === 4) {
        return <div>{renderCircular("#da4e48", "#fbe7e6")}停止</div>;
      } else if (text == 5) {
        return (
          <div>{renderCircular("#f5c773", "rgba(247, 231, 24,.2)")}启动中</div>
        );
      } else if (text == 6) {
        return (
          <div>{renderCircular("#f5c773", "rgba(247, 231, 24,.2)")}停止中</div>
        );
      } else if (text == 7) {
        return (
          <div>{renderCircular("#f5c773", "rgba(247, 231, 24,.2)")}重启中</div>
        );
      } else if (text == -1) {
        if (record.is_web_service) {
          return (
            <div>
              {renderCircular("rgb(84, 187, 166)", "rgb(238, 250, 244)")}正常
            </div>
          );
        } else {
          return (
            <div>
              {renderCircular("#f5c773", "rgba(247, 231, 24,.2)")}未监控
            </div>
          );
        }
      } else {
        return text;
      }
    },
  },
  product_thrityPart_status: {
    title: "运行状态",
    //width: 100,
    key: "product_service_status",
    dataIndex: "state",
    //ellipsis: true,
    align: "center",
    render: (text, record, index) => {
      if (isTableTextInvalid(text)) {
        return "-";
      } else if (text === 1) {
        return (
          <div>
            {renderCircular("rgb(84, 187, 166)", "rgb(238, 250, 244)")}正常
          </div>
        );
      } else if (text === 2) {
        return (
          <div>{renderCircular("#f5c773", "rgba(247, 231, 24,.2)")}异常</div>
        );
      } else if (text === 0) {
        return <div>{renderCircular("#da4e48", "#fbe7e6")}停止</div>;
      } else {
        return text;
      }
    },
  },
  host_risk: {
    title: "主机风险",
    //width: 120,
    key: "host_risk",
    dataIndex: "host_risk",
    //ellipsis: true,
    sorter: (a, b) => a.host_risk - b.host_risk,
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: (text, record, index) => {
      if (isTableTextInvalid(text)) {
        return "-";
      } else {
        return `${text}个`;
      }
    },
  },
  service_risk: {
    title: "服务风险",
    //width: 120,
    key: "service_risk",
    dataIndex: "service_risk",
    //ellipsis: true,
    sorter: (a, b) => a.service_risk - b.service_risk,
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: (text, record, index) => {
      if (isTableTextInvalid(text)) {
        return "-";
      } else {
        return `${text}个`;
      }
    },
  },
  start_time: {
    title: "开始时间",
    width: 160,
    key: "start_time",
    dataIndex: "start_time",
    //ellipsis: true,
    sorter: (a, b) =>
      moment(a.start_time).valueOf() - moment(b.start_time).valueOf(),
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: formatTableRenderData,
  },
  patrol_start_time: {
    title: "开始时间",
    width: 200,
    key: "patrol_start_time",
    dataIndex: "start_time",
    //ellipsis: true,
    sorter: (a, b) =>
      moment(a.start_time).valueOf() - moment(b.start_time).valueOf(),
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: formatTableRenderData,
  },
  patrol_end_time: {
    title: "结束时间",
    width: 160,
    key: "patrol_end_time",
    dataIndex: "end_time",
    //ellipsis: true,
    sorter: (a, b) =>
      moment(a.end_time).valueOf() - moment(b.end_time).valueOf(),
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: formatTableRenderData,
  },
  duration: {
    title: "用时",
    width: 100,
    key: "duration",
    dataIndex: "duration",
    //ellipsis: true,
    sorter: (a, b) => a.duration - b.duration,
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: renderFormattedTime,
  },

  // 巡检报告内容
  // 主机风险
  report_system: {
    title: "操作系统",
    //width: 150,
    key: "report_system",
    dataIndex: "system",
    //ellipsis: true,
    render: formatTableRenderData,
    align: "center",
  },
  report_risk_level: {
    title: "风险级别",
    key: "report_risk_level",
    dataIndex: "risk_level",
    //ellipsis: true,
    //width: 100,
    render: function renderFunc(text, record, index) {
      switch (record.risk_level) {
        case "critical":
          return (
            <ColorfulNotice
              backgroundColor={"#fbe7e6"}
              borderColor="#da4e48"
              text={"严重"}
            />
          );
        case "warning":
          return (
            <ColorfulNotice
              backgroundColor="rgba(247, 231, 24,.2)"
              borderColor="#f5c773"
              text={`警告`}
            />
          );
        default:
          return "-";
      }
    },
    align: "center",
  },
  report_risk_describe: {
    width: 400,
    title: "风险描述",
    key: "report_risk_describe",
    dataIndex: "risk_describe",
    ellipsis: true,
    render: formatTableRenderData,
    align: "center",
  },
  report_resolve_info: {
    title: "解决方案",
    key: "report_resolve_info",
    dataIndex: "resolve_info",
    //ellipsis: true,
    render: formatTableRenderData,
    align: "center",
  },
  // 主机列表
  report_release_version: {
    title: "操作系统",
    key: "report_release_version",
    dataIndex: "release_version",
    //ellipsis: true,
    //width: 180,
    render: formatTableRenderData,
    align: "center",
  },
  report_host_massage: {
    title: "配置信息",
    key: "report_host_massage",
    dataIndex: "host_massage",
    //ellipsis: true,
    //ellipsis: true,
    //width: 180,
    render: formatTableRenderData,
    align: "center",
  },
  report_disk_usage_root: {
    title: "根分区使用率",
    width: 150,
    key: "report_disk_usage_root",
    dataIndex: "disk_usage_root",
    //ellipsis: true,
    render: formatTableRenderData,
    align: "center",
  },
  report_disk_usage_data: {
    title: "数据分区使用率",
    width: 130,
    key: "report_disk_usage_data",
    dataIndex: "disk_usage_data",
    //ellipsis: true,
    render: formatTableRenderData,
    align: "center",
  },
  report_sys_load: {
    title: "平均负载",
    key: "report_sys_load",
    dataIndex: "sys_load",
    //width:180,
    //ellipsis: true,
    render: formatTableRenderData,
    align: "center",
  },
  // 服务列表、数据库列表、组件列表
  report_idx: {
    title: "序列",
    key: "index",
    width: 50,
    render: (text, record, index) => `${index + 1}`,
    align: "center",
    //fixed: "left",
    ////ellipsis:true
  },
  report_host_ip: {
    title: "IP地址",
    key: "report_host_ip",
    dataIndex: "host_ip",
    //ellipsis: true,
    width: 150,
    render: formatTableRenderData,
    align: "center",
  },
  report_log_level: {
    title: "日志等级",
    key: "report_log_level",
    dataIndex: "log_level",
    //ellipsis: true,
    render: formatTableRenderData,
    align: "center",
  },
  report_mem_usage: {
    title: "内存使用率",
    key: "report_mem_usage",
    dataIndex: "mem_usage",
    //ellipsis: true,
    width: 100,
    render: formatTableRenderData,
    align: "center",
  },
  report_cpu_usage: {
    title: "CPU使用率",
    key: "report_cpu_usage",
    dataIndex: "cpu_usage",
    //ellipsis: true,
    width: 110,
    render: formatTableRenderData,
    align: "center",
  },
  report_service_name: {
    title: "服务名称",
    //width: 200,
    key: "report_service_name",
    dataIndex: "service_name",
    //ellipsis: true,
    render: formatTableRenderData,
    align: "center",
  },
  report_service_port: {
    title: "端口号",
    key: "report_service_port",
    dataIndex: "service_port",
    //ellipsis: true,
    //width: 100,
    render: report_service_RenderData,
    align: "center",
  },
  report_service_status: {
    title: "运行状态",
    key: "report_service_status",
    dataIndex: "service_status",
    //ellipsis: true,
    //width: 100,
    render: formatTableRenderData,
    align: "center",
  },
  report_run_time: {
    title: "运行时间",
    width: 120,
    key: "report_run_time",
    dataIndex: "run_time",
    //ellipsis: true,
    render: formatTableRenderData,
    align: "center",
  },
  report_cluster_name: {
    title: "集群名称",
    key: "report_cluster_name",
    dataIndex: "cluster_name",
    //ellipsis: true,
    render: formatTableRenderData,
    align: "center",
  },
  operator: {
    title: "操作人员",
    key: "operator",
    dataIndex: "operator",
    align: "center",
    width: 80,
  },
  install_process: {
    title: "安装进度",
    key: "install_process",
    dataIndex: "install_process",
    align: "center",
    width: 80,
    render: (text) => {
      if (text == "0%") {
        return <span>{renderCircular("#da4e48", "#fbe7e6")}失败</span>;
      } else if (text == "100%") {
        return (
          <span>
            {renderCircular("rgb(84, 187, 166)", "rgb(238, 250, 244)")}成功
          </span>
        );
      } else {
        return text;
      }
    },
  },
  verson_start_time: {
    title: "开始时间",
    key: "start_time",
    dataIndex: "start_time",
    align: "center",
    width: 160,
  },
  verson_end_time: {
    title: "结束时间",
    key: "end_time",
    dataIndex: "end_time",
    align: "center",
    width: 150,
  },
  use_time: {
    title: "用时",
    key: "duration",
    dataIndex: "duration",
    render: (text) => {
      if (text && text !== "-") {
        let timer = moment.duration(text, "seconds");

        let hours = timer.hours();
        let hoursResult = hours ? `${hours}小时` : "";

        let minutes = timer.minutes();
        let minutesResult = minutes % 60 ? `${minutes % 60}分钟` : "";

        let seconds = timer.seconds();
        let secondsResult = seconds % 60 ? `${seconds % 60}秒` : "";

        return `${hoursResult} ${minutesResult} ${secondsResult}`;

        // if(minutes >= 1){
        //   return `${minutes.toFixed()}分钟`;
        // }else{
        //   return `${text}秒`;
        // }
      } else {
        return "-";
      }
    },
    align: "center",
    width: 100,
  },
  execution_mdoal: {
    title: "执行方式",
    align: "center",
    dataIndex: "execute_type",
    key: "execute_type",
    render: (text) => {
      if (text == "man") {
        return "手动执行";
      } else if (text == "auto") {
        return "定时执行";
      } else {
        return "-";
      }
    },
    width: 80,
  },
  machine_idx: {
    title: "序列",
    key: "index",
    render: (text, record, index) => `${record._idx}`,
    align: "center",
    width: 60,
    //fixed: "left",
  },
  /*eslint-disable*/
  service_idx: {
    title: "序列",
    key: "index",
    dataIndex: "_idx",
    //render: (text, record, index) => `${index + 1}`,
    //ellipsis: true,
    align: "center",
    width: 60,
    //fixed: "left",
    // render:(text,record)=>{
    //   return (
    //     <div className="record-name">
    //       <span>{record._idx}</span>
    //     </div>
    //   );
    // }
  },
  /*eslint-disable*/
  service_port_new: {
    title: "端口",
    width: 100,
    key: "service_port",
    dataIndex: "service_port",
    //ellipsis: true,
    sorter: (a, b) => a.service_port - b.service_port,
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: (text) => {
      return text ? text : "-";
    },
  },
  _port_new: {
    title: "端口",
    //width: 100,
    key: "port",
    dataIndex: "port",
    //ellipsis: true,
    sorter: (a, b) => a.port - b.port,
    sortDirections: ["descend", "ascend"],
    align: "center",
    render: (text) => {
      return text ? text : "-";
    },
  },
};
// 巡检报告-主机列表-连通性报告配置
export const host_port_connectivity_columns = [
  {
    title: "服务",
    dataIndex: "name",
    //ellipsis: true,
    className: styles._bigfontSize,
  },
  {
    title: "IP地址",
    dataIndex: "ip",
    //ellipsis: true,
    align: "center",
    className: styles._bigfontSize,
  },
  {
    title: "端口",
    dataIndex: "port",
    //ellipsis: true,
    align: "center",
    className: styles._bigfontSize,
  },
  /*eslint-disable*/
  {
    title: "连通性",
    dataIndex: "status",
    //ellipsis: true,
    align: "center",
    className: styles._bigfontSize,
    render: (text) => {
      return (
        <div style={{ color: text == "False" ? "rgb(207, 19, 34)" : null }}>
          {text}
        </div>
      );
    },
  },
  /*eslint-disable*/
];
// 巡检报告-主机列表-内存使用率配置
export const host_memory_top_columns = [
  {
    title: "TOP",
    dataIndex: "TOP",
    //ellipsis: true,
    width: 50,
    className: styles._bigfontSize,
  },
  {
    title: "PID",
    dataIndex: "PID",
    //ellipsis: true,
    align: "center",
    width: 100,
    className: styles._bigfontSize,
  },
  {
    title: "使用率",
    dataIndex: "P_RATE",
    //ellipsis: true,
    align: "center",
    width: 100,
    className: styles._bigfontSize,
  },
  {
    title: "进程",
    dataIndex: "P_CMD",
    //ellipsis: true,
    className: styles._bigfontSize,
  },
];

// 巡检报告-组件列表-kafka-分区信息
export const kafka_partition_columns = [
  {
    title: "Topic",
    dataIndex: "topic",
    //ellipsis: true,
    className: styles._bigfontSize,
  },
  {
    title: "分区数",
    dataIndex: "partition",
    //ellipsis: true,
    align: "center",
    className: styles._bigfontSize,
  },
  {
    title: "副本数",
    dataIndex: "replication",
    //ellipsis: true,
    align: "center",
    className: styles._bigfontSize,
  },
];

// 巡检报告-组件列表-kafka-消费位移信息
export const kafka_offsets_columns = [
  {
    title: "Group",
    dataIndex: "group",
    //ellipsis: true,
    className: styles._bigfontSize,
  },
  {
    title: "Topic",
    dataIndex: "topic",
    //ellipsis: true,
    className: styles._bigfontSize,
  },
  {
    title: "Log Offset",
    dataIndex: "log_offset",
    //ellipsis: true,
    align: "center",
    className: styles._bigfontSize,
  },
  {
    title: "Lag Offset",
    dataIndex: "lag_offset",
    //ellipsis: true,
    align: "center",
    className: styles._bigfontSize,
  },
];

// 巡检报告-组件列表-kafka-topic消息大小
export const kafka_topic_size_columns = [
  {
    title: "Topic",
    dataIndex: "topic",
    //ellipsis: true,
    className: styles._bigfontSize,
  },
  {
    title: "Size",
    dataIndex: "size",
    //ellipsis: true,
    align: "center",
    className: styles._bigfontSize,
  },
];

/**
 * table组件最后一列操作按钮的跳转逻辑
 * 以=结尾的需要拼接ip地址
 * @param record
 * @param type 默认是监控跳转
 */
export const tableButtonHandler = (record, type = "monitor") => {
  if (type === "log") {
    if (isTableTextInvalid(record.monitor_log)) {
      return message.warn("请确认数据采集地址是否正确");
    }
    //console.log(record.monitor_log,"===",record.service_name,record);
    if (record.service_name) {
      //window.open(`${record.monitor_log}${record.service_name}&var-env=${updata()().text}`);
      window.open(`${record.monitor_log}${record.service_name}`);
    } else if (record.alert_service_name) {
      //window.open(`${record.monitor_log}${record.alert_service_name}&var-env=${updata()().text}`);
      window.open(`${record.monitor_log}${record.alert_service_name}`);
    }
  } else {
    const url = record.monitor;
    if (isTableTextInvalid(url)) {
      return message.warn("请确认数据采集地址是否正确");
    } else if (url.endsWith("=")) {
      // 主机管理、服务管理中用的ip，告警记录里用的alert_host_ip，但二者不会共存
      // window.open(`${url}${record.ip ? record.ip : record.alert_host_ip}&var-env=${record.is_omp_host?record.master_env_name:updata()().text}`);
      window.open(`${url}${record.ip ? record.ip : record.alert_host_ip}`);
    } else if (url.endsWith("1")) {
      // 服务管理-自研服务，跳转监控时拼接服务名称
      // window.open(
      //   `${url}&var-app=${
      //     record.service_name ? record.service_name : record.alert_service_name
      //   }&var-ip=${record.ip?record.ip:(record.alert_host_ip?record.alert_host_ip:undefined)}&var-env=${updata()().text}`
      // );
      window.open(
        `${url}&var-app=${
          record.service_name ? record.service_name : record.alert_service_name
        }&var-ip=${
          record.ip
            ? record.ip
            : record.alert_host_ip
            ? record.alert_host_ip
            : undefined
        }`
      );
    } else {
      //window.open(`${url}&var-env=${updata()().text}`);
      window.open(`${url}`);
    }
  }
};

/**
 * 测试ip地址准确性
 * @param ip
 * @returns {boolean}
 */
export function isValidIP(ip) {
  const reg =
    /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\:([0-9]|[1-9]\d{1,3}|[1-5]\d{4}|6[0-5]{2}[0-3][0-5])$/;
  return reg.test(ip);
}

/**
 * @name:
 * @test: test font
 * @msg:
 * @param {*} data
 * @return {*}
 */
//给列表item添加idx做id用
export const _idxInit = (data) => {
  let result = [...data];
  result.map((item, i) => {
    result[i]._idx = i + 1;
    result[i].key = result[i].id ? result[i].id : result[i]._idx;
  });
  return result;
};

export function TableRowButton({ buttonsArr }) {
  return (
    <div className={styles.listButton}>
      {buttonsArr.map((item, idx) => {
        return (
          <div key={idx} onClick={() => item.btnHandler()}>
            {item.btnText}
          </div>
        );
      })}
    </div>
  );
}

export const refreshTime = () => {
  return getRefreshTimeChangeAction(moment().format("YYYY-MM-DD HH:mm:ss"));
};

export function delCookie(name) {
  var exp = new Date();
  exp.setTime(exp.getTime() - 1);
  var cval = getCookie(name);
  //console.log(cval)
  if (cval != null)
    document.cookie =
      name +
      "=" +
      cval +
      ';domin="localhost"' +
      ";expires=" +
      exp.toGMTString();
}

export function getCookie(name) {
  //console.log(document.cookie)
  let arr = document.cookie.match(new RegExp("(^| )" + name + "=([^;]*)(;|$)"));
  if (arr != null) return unescape(arr[2]);
  return null;
}

export const logout = (login) => {
  delCookie("jwtToken");
  localStorage.clear();
  !login && window.__history__.replace("/login");
  return;
};

//文本非空处理
export const nonEmptyProcessing = (text) => {
  if (text === "" || text === null || text === undefined) {
    return "-";
  } else {
    return `${text}`;
  }
};

export const handleResponse = (res, succCallback, failedCallback) => {
  if (res.data.code === 0) {
    if (typeof succCallback === "function") {
      succCallback(res.data);
    }
  }

  if (res.data.code === 1) {
    if (res.data.message) {
      if (res.data.message == "未认证") {
        logout();
        return;
      }
      message.warn(res.data.message);
    }

    if (typeof failedCallback === "function") {
      failedCallback();
    }
  }
};

export const colorConfig = {
  normal: "#76ca68",
  warning: "#ffbf00",
  critical: "#f04134",
  notMonitored: "rgb(170, 170, 170)"
};

export const renderDisc = (level = "normal", size = 5, top = 0, left = 0) => {
  return (
    <div
      style={{
        color: colorConfig[level],
        width: size,
        height: size,
        borderStyle: "solid",
        //borderWidth: 2,
        borderColor: colorConfig[level],
        backgroundColor: colorConfig[level],
        display: "inline-block",
        marginRight: 8,
        borderRadius: "50%",
        position: "relative",
        top: top,
        left: left,
      }}
    ></div>
  );
};

export const MessageTip = ({ setMsgShow, msgShow, msg }) => {
  return (
    <div
      style={{
        position: "relative",
        top: -10,
        left: 10,
        backgroundColor: "#fbe3e2",
        padding: "10px",
        height: "40px",
        color: "#86292e",
        display: "flex",
        justifyContent: "space-between",
        cursor: "pointer",
        width: 240,
        margin: "0 auto",
        paddingLeft: 15,
      }}
      className={msgShow ? styles.loginMessageShow : styles.loginMessageHide}
      onClick={() => setMsgShow(false)}
    >
      {msg}
      <CloseCircleFilled
        style={{ color: "#fff", fontSize: 20, marginLeft: "10px" }}
      />
    </div>
  );
};

//校验中文
export const isChineseChar = (str) => {
  var reg = /[\u4E00-\u9FA5\uF900-\uFA2D]/;
  return reg.test(str);
};

//校验数字
export const isNumberChar = (str) => {
  const reg = /^\d+$/;
  return reg.test(str);
};

// 校验小写
export const isLowercaseChar = (str) => {
  const reg = /^[a-z]+$/;
  return reg.test(str);
};

// 校验大写
export const isUppercaseChar = (str) => {
  const reg = /^[A-Z]+$/;
  return reg.test(str);
};

// 校验字母
export const isLetterChar = (str) => {
  const reg = /^[a-zA-Z]+$/;
  return reg.test(str);
};

// 校验ip
export const isValidIpChar = (ip) => {
  var reg =
    /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/;
  return reg.test(ip);
};

// 校验表情
export const isExpression = (str) => {
  var reg =
    /[^\u0020-\u007E\u00A0-\u00BE\u2E80-\uA4CF\uF900-\uFAFF\uFE30-\uFE4F\uFF00-\uFFEF\u0080-\u009F\u2000-\u201f\u2026\u2022\u20ac\r\n]/g;
  return reg.test(str);
};

// 校验空格
export const isSpace = (str) => {
  return str.includes(" ");
};

export function debounce(fn, wait) {
  return function () {
    clearTimeout(window.timer);
    window.timer = setTimeout(fn, wait);
  };
}

// 校验密码
export function isPassword(str) {
  var reg = /[^a-zA-Z0-9\`\~\!\?\@\#\$\%\^\&\,\(\)\[\]\{\}\_\+\_\*\/\.\;\:]/g;
  return reg.test(str);
}

// 下载文件
export const downloadFile = (url) => {
  let a = document.createElement("a");
  a.href = url;
  a.download =  url.split("/").pop()
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
};

// 检测对象类型
function checkType(any) {
  return Object.prototype.toString.call(any).slice(8, -1);
}

// 深拷贝函数
export const clone = (any) => {
  if (checkType(any) === "Object") {
    // 拷贝对象
    let o = {};
    for (let key in any) {
      o[key] = clone(any[key]);
    }
    return o;
  } else if (checkType(any) === "Array") {
    // 拷贝数组
    var arr = [];
    for (let i = 0, leng = any.length; i < leng; i++) {
      arr[i] = clone(any[i]);
    }
    return arr;
  } else if (checkType(any) === "Function") {
    // 拷贝函数
    return new Function("return " + any.toString()).call(this);
  } else if (checkType(any) === "Date") {
    // 拷贝日期
    return new Date(any.valueOf());
  } else if (checkType(any) === "RegExp") {
    // 拷贝正则
    return new RegExp(any);
  } else if (checkType(any) === "Map") {
    // 拷贝Map 集合
    let m = new Map();
    any.forEach((v, k) => {
      m.set(k, clone(v));
    });
    return m;
  } else if (checkType(any) === "Set") {
    // 拷贝Set 集合
    let s = new Set();
    for (let val of any.values()) {
      s.add(clone(val));
    }
    return s;
  }
  return any;
};

export const randomNumber = (length = 6) => {
  let r = "";
  let str = "QWERTYUIOPLKJHGFDSAZXCVBNM123456790";
  new Array(length).fill(0).map((item) => {
    let num = parseInt(Math.random() * 26);
    r += str[num];
  });
  return r;
};