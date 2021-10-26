(this["webpackJsonpomp-fontend"] = this["webpackJsonpomp-fontend"] || []).push([
  [0],
  {
    172: function (a, r, t) {},
    22: function (a) {
      a.exports = {"summary": {"task_info": {"task_name": "\u4e3b\u673a\u5de1\u68c02021102616", "operator": "admin", "task_status": 2}, "time_info": {"start_time": "2021-10-26 13:00:40", "end_time": "2021-10-26 13:00:40", "cost": 0}, "scan_info": {"host": 1, "service": 0, "component": 0}, "scan_result": {"healthy": "4.35%", "all_target_num": 23, "abnormal_target": 1}}, "risks": {"host_list": [], "service_list": []}, "detail_dict": {"host": [{"basic": [{"name": "IP", "value": "10.0.7.146", "name_cn": "\u4e3b\u673aIP"}, {"name": "hostname", "value": null, "name_cn": "\u4e3b\u673a\u540d"}, {"name": "kernel_version", "value": "", "name_cn": "\u5185\u6838\u7248\u672c"}, {"name": "selinux", "value": "", "name_cn": "SElinux \u72b6\u6001"}, {"name": "max_openfile", "value": "790692", "name_cn": "\u6700\u5927\u6253\u5f00\u6587\u4ef6\u6570"}, {"name": "iowait", "value": "0", "name_cn": "IOWait"}, {"name": "inode_usage", "value": {"/": "fail%"}, "name_cn": "inode \u4f7f\u7528\u7387"}, {"name": "now_time", "value": "2021-10-26 13:00:40", "name_cn": "\u5f53\u524d\u65f6\u95f4"}, {"name": "run_process", "value": "", "name_cn": "\u8fdb\u7a0b\u6570"}, {"name": "umask", "value": {"user": "commonuser", "umask": ""}, "name_cn": "umask"}, {"name": "bandwidth", "value": {"receive": "5.470442708333334", "transmit": "0.55703125"}, "name_cn": "\u5e26\u5bbd"}, {"name": "throughput", "value": {"read": "4642", "write": "19661"}, "name_cn": "IO"}, {"name": "zombies_process", "value": [], "name_cn": "\u50f5\u5c38\u8fdb\u7a0b"}], "cpu_top": [], "host_ip": "10.0.7.146", "run_time": "3554131.4049999714", "sys_load": {"load1": "0.27", "load5": "0.21", "load15": "0.19"}, "cpu_usage": "6", "mem_usage": "29", "memory_top": [], "host_massage": "", "disk_usage_root": "6", "release_version": "CentOS", "kernel_parameters": []}]}, "file_name": "hostinspection2021102616.tar.gz"};
    },
    331: function (a, r, t) {
      "use strict";
      t.r(r);
      var e = t(9),
        o = t.n(e),
        p = (t(332), t(17)),
        i = t(161),
        d = (t(171), t(330), t(160)),
        l = t(163),
        n = (t(333), t(122)),
        c = (t(329), t(41)),
        s = (t(334), t(13)),
        b = t(70),
        j = t(4),
        m = (t(335), t(100)),
        u = (t(172), t(162), t(336), t(61), t(337), t(98)),
        g = t(24),
        v = t.n(g),
        S = t(338),
        E = t.p + "static/media/index.module.b57695f6.less",
        _ = t(2),
        f = function (a) {
          return "null" === String(a) || "" === a || void 0 === a;
        };
      function k(a, r, t) {
        return f(a)
          ? "-"
          : 0 === a || "active" === a || !0 === a
          ? Object(_.jsxs)("div", {
              style: { fontSize: 14 },
              children: [
                R("rgb(84, 187, 166)", "rgb(238, 250, 244)"),
                "\u6b63\u5e38",
              ],
            })
          : 1 === a || "unactive" === a || !1 === a
          ? Object(_.jsxs)("div", {
              style: { fontSize: 14 },
              children: [R("#da4e48", "#fbe7e6"), "\u5f02\u5e38"],
            })
          : "CREATE" === a
          ? Object(_.jsx)("div", {
              style: { fontSize: 14 },
              children: "\u589e\u52a0",
            })
          : "UPDATE" === a
          ? Object(_.jsx)("div", {
              style: { fontSize: 14 },
              children: "\u66f4\u65b0",
            })
          : "DELETE" === a
          ? Object(_.jsx)("div", {
              style: { fontSize: 14 },
              children: "\u5220\u9664",
            })
          : a;
      }
      function A(a, r, t) {
        if (f(a)) return "-";
        var e = "",
          o = Math.round(Number(a)),
          p = Math.floor(o / 86400),
          i = Math.floor((o % 86400) / 3600),
          d = Math.floor(((o % 86400) % 3600) / 60),
          l = Math.floor(((o % 86400) % 3600) % 60);
        return (
          p > 0
            ? (e = p + "\u5929" + i + "\u5c0f\u65f6")
            : i > 0
            ? (e = i + "\u5c0f\u65f6" + d + "\u5206")
            : d > 0
            ? (e = d + "\u5206")
            : l > 0 && (e = l + "\u79d2"),
          e
        );
      }
      var R = function (a, r) {
        return Object(_.jsx)("span", {
          style: {
            width: 10,
            height: 10,
            borderStyle: "solid",
            borderWidth: 2,
            borderColor: a,
            backgroundColor: r,
            display: "inline-block",
            marginRight: 5,
            borderRadius: "50%",
          },
        });
      };
      function D(a) {
        var r = a.backgroundColor,
          t = a.borderColor,
          e = a.text,
          o = a.top,
          p = a.width,
          i = void 0 === p ? 55 : p;
        return Object(_.jsx)("div", {
          style: {
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: i,
            height: 20,
            margin: "0 auto",
            color: "rgba(0, 0, 0, 0.6)",
            fontSize: "12px",
            borderRadius: "4px",
            border: "1px solid #fff",
            backgroundColor: r,
            borderColor: t,
            position: "relative",
            top: o,
          },
          children: e,
        });
      }
      var L = {
        sortIP: function (a, r) {
          return a.ip && r.ip
            ? a.ip
                .split(".")
                .map(function (a) {
                  return a.padStart(3, "0");
                })
                .join("") -
                r.ip
                  .split(".")
                  .map(function (a) {
                    return a.padStart(3, "0");
                  })
                  .join("")
            : 0;
        },
        sortAlertIP: function (a, r) {
          return a.alert_host_ip && r.alert_host_ip
            ? a.alert_host_ip
                .split(".")
                .map(function (a) {
                  return a.padStart(3, "0");
                })
                .join("") -
                r.alert_host_ip
                  .split(".")
                  .map(function (a) {
                    return a.padStart(3, "0");
                  })
                  .join("")
            : 0;
        },
        sortUsageRate: function (a, r) {
          return Number(f(a) ? 0 : a) - Number(f(r) ? 0 : r);
        },
      };
      function y(a) {
        return Object(_.jsx)(u.a, {
          title: a,
          children: Object(_.jsx)("div", {
            style: {
              overflow: "hidden",
              whiteSpace: "nowrap",
              textOverflow: "ellipsis",
            },
            children: a,
          }),
        });
      }
      var x = {
          idx: {
            title: "\u5e8f\u5217",
            key: "index",
            render: function (a, r, t) {
              return "".concat(t + 1);
            },
            align: "center",
            width: 60,
          },
          product_name: {
            title: "\u670d\u52a1\u7c7b\u578b",
            key: "product_name",
            dataIndex: "product_name",
            sorter: function (a, r) {
              var t = S.a(" ", a.product_name),
                e = S.a(" ", r.product_name);
              return (
                t.toLowerCase().charCodeAt(0) - e.toLowerCase().charCodeAt(0)
              );
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: k,
          },
          functional_module: {
            title: "\u529f\u80fd\u6a21\u5757",
            width: 120,
            key: "product_cn_name",
            dataIndex: "product_cn_name",
            sorter: function (a, r) {
              var t = S.a(" ", a.product_cn_name),
                e = S.a(" ", r.product_cn_name);
              return (
                t.toLowerCase().charCodeAt(0) - e.toLowerCase().charCodeAt(0)
              );
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: k,
          },
          alert_service_type: {
            title: "\u529f\u80fd\u6a21\u5757",
            width: 120,
            key: "alert_service_type",
            dataIndex: "alert_service_type",
            sorter: function (a, r) {
              var t = S.a(" ", a.alert_service_type),
                e = S.a(" ", r.alert_service_type);
              return (
                t.toLowerCase().charCodeAt(0) - e.toLowerCase().charCodeAt(0)
              );
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: k,
          },
          service_name: {
            title: "\u670d\u52a1\u540d\u79f0",
            width: 180,
            key: "service_name",
            dataIndex: "service_name",
            sorter: function (a, r) {
              var t = S.a(" ", a.service_name),
                e = S.a(" ", r.service_name);
              return (
                t.toLowerCase().charCodeAt(0) - e.toLowerCase().charCodeAt(0)
              );
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: k,
          },
          alert_service_name: {
            title: "\u670d\u52a1\u540d\u79f0",
            width: 160,
            key: "alert_service_name",
            dataIndex: "alert_service_name",
            ellipsis: !0,
            sorter: function (a, r) {
              var t = S.a(" ", a.alert_service_name),
                e = S.a(" ", r.alert_service_name);
              return (
                t.toLowerCase().charCodeAt(0) - e.toLowerCase().charCodeAt(0)
              );
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: k,
          },
          ip: {
            title: "IP\u5730\u5740",
            width: 160,
            key: "ip",
            dataIndex: "ip",
            sorter: L.sortIP,
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: k,
          },
          thirdParty_ip: {
            title: "\u8fde\u63a5\u5730\u5740",
            key: "ip",
            dataIndex: "ip",
            sorter: L.sortIP,
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: k,
          },
          alert_host_ip: {
            title: "IP\u5730\u5740",
            width: 80,
            key: "alert_host_ip",
            dataIndex: "alert_host_ip",
            sorter: L.sortAlertIP,
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: k,
          },
          alert_level: {
            title: "\u544a\u8b66\u7ea7\u522b",
            width: 100,
            key: "alert_level",
            dataIndex: "alert_level",
            sorter: function (a, r) {
              var t = S.a(" ", a.alert_level),
                e = S.a(" ", r.alert_level);
              return (
                t.toLowerCase().charCodeAt(0) - e.toLowerCase().charCodeAt(0)
              );
            },
            render: function (a, r, t) {
              switch (r.alert_level) {
                case "critical":
                  return Object(_.jsx)(D, {
                    borderColor: "#da4e48",
                    backgroundColor: "#fbe7e6",
                    text: "\u4e25\u91cd",
                  });
                case "warning":
                  return Object(_.jsx)(D, {
                    borderColor: "#f5c773",
                    backgroundColor: "rgba(247, 231, 24,.2)",
                    text: "\u8b66\u544a",
                  });
                default:
                  return "-";
              }
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
          },
          alert_describe: {
            title: "\u544a\u8b66\u63cf\u8ff0",
            key: "alert_describe",
            dataIndex: "alert_describe",
            width: 280,
            align: "center",
            ellipsis: !0,
            render: y,
          },
          alert_time: {
            title: "\u544a\u8b66\u65f6\u95f4",
            width: 140,
            key: "alert_time",
            dataIndex: "alert_time",
            sorter: function (a, r) {
              return v()(a.alert_time).valueOf() - v()(r.alert_time).valueOf();
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: k,
          },
          warning_record_alert_time: {
            title: "\u544a\u8b66\u65f6\u95f4",
            width: 180,
            key: "alert_time",
            dataIndex: "create_time",
            sorter: function (a, r) {
              return (
                v()(a.create_time).valueOf() - v()(r.create_time).valueOf()
              );
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: k,
          },
          alert_receiver: {
            title: "\u544a\u8b66\u63a8\u9001",
            key: "alert_receiver",
            dataIndex: "alert_receiver",
            align: "center",
            render: y,
          },
          alert_resolve: {
            title: "\u89e3\u51b3\u65b9\u6848",
            key: "alert_resolve",
            dataIndex: "alert_resolve",
            align: "center",
            render: k,
          },
          operating_system: {
            title: "\u64cd\u4f5c\u7cfb\u7edf",
            key: "operating_system",
            dataIndex: "operating_system",
            align: "center",
            render: k,
          },
          alert_host_system: {
            title: "\u64cd\u4f5c\u7cfb\u7edf",
            key: "alert_host_system",
            dataIndex: "alert_host_system",
            align: "center",
            render: k,
          },
          port: {
            title: "\u7aef\u53e3",
            key: "port",
            dataIndex: "port",
            sorter: function (a, r) {
              return a.port - r.port;
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: k,
          },
          service_port: {
            title: "\u7aef\u53e3",
            key: "service_port",
            dataIndex: "service_port",
            sorter: function (a, r) {
              return a.service_port - r.service_port;
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: k,
          },
          service_version: {
            title: "\u670d\u52a1\u7248\u672c",
            key: "service_version",
            dataIndex: "service_version",
            align: "center",
            render: k,
          },
          configuration_information: {
            title: "\u914d\u7f6e\u4fe1\u606f",
            key: "configuration_information",
            dataIndex: "configuration_information",
            align: "center",
            render: function (a, r, t) {
              var e = r.cpu,
                o = r.memory,
                p = r.disk,
                i = 1073741824,
                d = f(e) ? "-" : "".concat(e, "C"),
                l = f(o) ? "-" : "".concat((o / i).toFixed(1), "G"),
                n = f(p) ? "-" : "".concat((p / i).toFixed(1), "G");
              return "-" === d && "-" === l && "-" === n
                ? "-"
                : "".concat(d, "|").concat(l, "|").concat(n);
            },
          },
          cpu_rate: {
            title: "CPU\u4f7f\u7528\u7387",
            width: 110,
            key: "cpu_rate",
            dataIndex: "cpu_rate",
            sorter: function (a, r) {
              return L.sortUsageRate(a.cpu_rate, r.cpu_rate);
            },
            render: function (a, r, t) {
              if (f(a)) return Object(_.jsx)("div", { children: "-" });
              var e = Number(Number(a).toFixed(2));
              return "normal" === r.cpu_rate_check
                ? Object(_.jsx)(D, {
                    backgroundColor: "rgb(238, 250, 244)",
                    borderColor: "rgb(84, 187, 166)",
                    text: "".concat(e, "%"),
                    top: 1,
                  })
                : "critical" === r.cpu_rate_check
                ? Object(_.jsx)(D, {
                    backgroundColor: "#fbe7e6",
                    borderColor: "#da4e48",
                    text: "".concat(e, "%"),
                    top: 1,
                  })
                : "warning" === r.cpu_rate_check
                ? Object(_.jsx)(D, {
                    backgroundColor: "rgba(247, 231, 24,.2)",
                    borderColor: "#f5c773",
                    text: "".concat(e, "%"),
                    top: 1,
                  })
                : Object(_.jsx)(D, {
                    backgroundColor: "rgb(238, 250, 244)",
                    borderColor: "rgb(84, 187, 166)",
                    text: "".concat(e, "%"),
                    top: 1,
                  });
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
          },
          disk_rate: {
            title: "(\u6839\u5206\u533a)\u4f7f\u7528\u7387",
            width: 150,
            key: "disk_rate",
            dataIndex: "disk_rate",
            sorter: function (a, r) {
              return L.sortUsageRate(a.disk_rate, r.disk_rate);
            },
            render: function (a, r, t) {
              if (f(a)) return Object(_.jsx)("div", { children: "-" });
              var e = Number(Number(a).toFixed(2));
              return "normal" === r.disk_rate_check
                ? Object(_.jsx)(D, {
                    backgroundColor: "rgb(238, 250, 244)",
                    borderColor: "rgb(84, 187, 166)",
                    top: 1,
                    text: "".concat(e, "%"),
                  })
                : "critical" === r.disk_rate_check
                ? Object(_.jsx)(D, {
                    backgroundColor: "#fbe7e6",
                    borderColor: "#da4e48",
                    text: "".concat(e, "%"),
                    top: 1,
                  })
                : "warning" === r.disk_rate_check
                ? Object(_.jsx)(D, {
                    backgroundColor: "rgba(247, 231, 24,.2)",
                    borderColor: "#f5c773",
                    text: "".concat(e, "%"),
                    top: 1,
                  })
                : Object(_.jsx)(D, {
                    backgroundColor: "rgb(238, 250, 244)",
                    borderColor: "rgb(84, 187, 166)",
                    text: "".concat(e, "%"),
                    top: 1,
                  });
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
          },
          disk_data_rate: {
            title: "(\u6570\u636e\u5206\u533a)\u4f7f\u7528\u7387",
            width: 160,
            key: "disk_data_rate",
            dataIndex: "disk_data_rate",
            sorter: function (a, r) {
              return L.sortUsageRate(a.disk_data_rate, r.disk_data_rate);
            },
            render: function (a, r, t) {
              if (f(a)) return Object(_.jsx)("div", { children: "-" });
              var e = Number(Number(a).toFixed(2));
              return "normal" === r.disk_data_check
                ? Object(_.jsx)(D, {
                    backgroundColor: "rgb(238, 250, 244)",
                    borderColor: "rgb(84, 187, 166)",
                    text: "".concat(e, "%"),
                    top: 1,
                  })
                : "critical" === r.disk_data_check
                ? Object(_.jsx)(D, {
                    backgroundColor: "#fbe7e6",
                    borderColor: "#da4e48",
                    text: "".concat(e, "%"),
                    top: 1,
                  })
                : "warning" === r.disk_data_check
                ? Object(_.jsx)(D, {
                    backgroundColor: "rgba(247, 231, 24,.2)",
                    borderColor: "#f5c773",
                    text: "".concat(e, "%"),
                    top: 1,
                  })
                : Object(_.jsx)(D, {
                    backgroundColor: "rgb(238, 250, 244)",
                    borderColor: "rgb(84, 187, 166)",
                    text: "".concat(e, "%"),
                    top: 1,
                  });
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
          },
          memory_rate: {
            title: "\u5185\u5b58\u4f7f\u7528\u7387",
            width: 100,
            key: "memory_rate",
            dataIndex: "memory_rate",
            sorter: function (a, r) {
              return L.sortUsageRate(a.memory_rate, r.memory_rate);
            },
            render: function (a, r, t) {
              if (f(a)) return Object(_.jsx)("div", { children: "-" });
              var e = Number(Number(a).toFixed(2));
              return "normal" === r.memory_rate_check
                ? Object(_.jsx)(D, {
                    backgroundColor: "rgb(238, 250, 244)",
                    borderColor: "rgb(84, 187, 166)",
                    text: "".concat(e, "%"),
                    top: 1,
                  })
                : "critical" === r.memory_rate_check
                ? Object(_.jsx)(D, {
                    backgroundColor: "#fbe7e6",
                    borderColor: "#da4e48",
                    text: "".concat(e, "%"),
                    top: 1,
                  })
                : "warning" === r.memory_rate_check
                ? Object(_.jsx)(D, {
                    backgroundColor: "rgba(247, 231, 24,.2)",
                    borderColor: "#f5c773",
                    text: "".concat(e, "%"),
                    top: 1,
                  })
                : Object(_.jsx)(D, {
                    backgroundColor: "rgb(238, 250, 244)",
                    borderColor: "rgb(84, 187, 166)",
                    text: "".concat(e, "%"),
                    top: 1,
                  });
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
          },
          running_time: {
            title: "\u8fd0\u884c\u65f6\u95f4",
            key: "running_time",
            width: 120,
            dataIndex: "running_time",
            sorter: function (a, r) {
              return (
                Number(f(a.running_time) ? 0 : a.running_time) -
                Number(f(r.running_time) ? 0 : r.running_time)
              );
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: A,
          },
          ssh_state: {
            title: "SSH\u72b6\u6001",
            width: 140,
            key: "ssh_state",
            dataIndex: "ssh_state",
            align: "center",
            render: function (a, r, t) {
              return f(a)
                ? "-"
                : 0 === a
                ? Object(_.jsxs)("div", {
                    children: [
                      R("rgb(84, 187, 166)", "rgb(238, 250, 244)"),
                      "\u542f\u7528",
                    ],
                  })
                : 1 === a
                ? Object(_.jsxs)("div", {
                    children: [R("#da4e48", "#fbe7e6"), "\u7981\u7528"],
                  })
                : a;
            },
          },
          agent_state: {
            title: "Agent\u72b6\u6001",
            width: 140,
            key: "agent_state",
            dataIndex: "agent_state",
            align: "center",
            render: function (a, r, t) {
              return f(a)
                ? "-"
                : 0 === a
                ? Object(_.jsxs)("div", {
                    children: [
                      R("rgb(84, 187, 166)", "rgb(238, 250, 244)"),
                      "\u6b63\u5e38",
                    ],
                  })
                : 1 === a
                ? "\u5b89\u88c5\u4e2d"
                : 2 === a
                ? "\u672a\u5b89\u88c5"
                : 3 === a
                ? Object(_.jsxs)("div", {
                    children: [R("#da4e48", "#fbe7e6"), "\u5f02\u5e38"],
                  })
                : a;
            },
          },
          cluster_name: {
            title: "\u96c6\u7fa4\u540d\u79f0",
            key: "cluster_name",
            dataIndex: "cluster_name",
            sorter: function (a, r) {
              var t = S.a(" ", a.cluster_name),
                e = S.a(" ", r.cluster_name);
              return (
                t.toLowerCase().charCodeAt(0) - e.toLowerCase().charCodeAt(0)
              );
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: k,
          },
          linkAddress: {
            title: "\u8fde\u63a5\u5730\u5740",
            key: "linkAddress",
            dataIndex: "linkAddress",
            align: "center",
            render: k,
          },
          cluster_mode: {
            title: "\u96c6\u7fa4\u6a21\u5f0f",
            key: "cluster_mode",
            dataIndex: "cluster_mode",
            align: "center",
            render: k,
          },
          quote: {
            title: "\u5df2\u5f15\u7528",
            key: "quote",
            dataIndex: "quote",
            align: "center",
            render: function (a) {
              return 0 === a ? "\u5426" : "\u662f";
            },
          },
          created_at: {
            title: "\u6dfb\u52a0\u65f6\u95f4",
            key: "created_at",
            dataIndex: "created_at",
            sorter: function (a, r) {
              return a - r;
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: k,
          },
          username: {
            title: "\u7528\u6237\u540d",
            width: 120,
            key: "username",
            dataIndex: "username",
            sorter: function (a, r) {
              var t = S.a(" ", a.username),
                e = S.a(" ", r.username);
              return t.charCodeAt(0) - e.charCodeAt(0);
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: k,
          },
          role: {
            title: "\u89d2\u8272",
            width: 120,
            key: "role",
            dataIndex: "role",
            sorter: function (a, r) {
              var t = S.a(" ", a.role),
                e = S.a(" ", r.role);
              return t.charCodeAt(0) - e.charCodeAt(0);
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: k,
          },
          login_time: {
            title: "\u767b\u5165\u65f6\u95f4",
            width: 180,
            key: "login_time",
            dataIndex: "login_time",
            sorter: function (a, r) {
              return v()(a.login_time).valueOf() - v()(r.login_time).valueOf();
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: k,
          },
          datetime: {
            title: "\u64cd\u4f5c\u65f6\u95f4",
            width: 150,
            key: "datetime",
            dataIndex: "datetime",
            sorter: function (a, r) {
              return v()(a.datetime).valueOf() - v()(r.datetime).valueOf();
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: k,
          },
          status: {
            title: "\u7528\u6237\u72b6\u6001",
            width: 160,
            key: "status",
            dataIndex: "status",
            align: "center",
            render: k,
          },
          date_joined: {
            title: "\u521b\u5efa\u65f6\u95f4",
            width: 120,
            key: "date_joined",
            dataIndex: "date_joined",
            align: "center",
            render: k,
          },
          desc: {
            title: "\u63cf\u8ff0",
            width: 220,
            key: "desc",
            dataIndex: "desc",
            align: "center",
            render: k,
          },
          action: {
            title: "\u64cd\u4f5c\u7c7b\u578b",
            width: 120,
            key: "action",
            dataIndex: "action",
            align: "center",
            render: k,
          },
          permission_count: {
            title: "\u6743\u9650\u4e2a\u6570",
            width: 120,
            key: "permission_count",
            dataIndex: "permission_count",
            align: "center",
            render: k,
          },
          inspection_operator: {
            title: "\u64cd\u4f5c\u5458",
            width: 80,
            key: "inspection_operator",
            dataIndex: "inspection_operator",
            sorter: function (a, r) {
              return (
                a.inspection_operator.charCodeAt(0) -
                r.inspection_operator.charCodeAt(0)
              );
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: k,
          },
          inspection_status: {
            title: "\u5de1\u68c0\u7ed3\u679c",
            width: 150,
            key: "inspection_status",
            dataIndex: "inspection_status",
            sorter: function (a, r) {
              return a.inspection_status - r.inspection_status;
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: function (a, r, t) {
              return f(a)
                ? "-"
                : 2 === a
                ? Object(_.jsxs)("div", {
                    children: [R("#6cbe7b", "#e8f5eb"), "\u6210\u529f"],
                  })
                : 1 === a
                ? "\u8fdb\u884c\u4e2d"
                : 0 === a
                ? "\u672a\u5f00\u59cb"
                : 3 === a
                ? Object(_.jsxs)("div", {
                    children: [R("#da4e48", "#fbe7e6"), "\u5931\u8d25"],
                  })
                : a;
            },
          },
          run_status: {
            title: "\u6267\u884c\u7ed3\u679c",
            width: 120,
            key: "inspection_status",
            dataIndex: "inspection_status",
            sorter: function (a, r) {
              return a.inspection_status - r.inspection_status;
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: function (a, r, t) {
              return f(a)
                ? "-"
                : 2 === a
                ? Object(_.jsxs)("div", {
                    children: [R("#6cbe7b", "#e8f5eb"), "\u6210\u529f"],
                  })
                : 1 === a
                ? "\u8fdb\u884c\u4e2d"
                : 0 === a
                ? "\u672a\u5f00\u59cb"
                : 3 === a
                ? Object(_.jsxs)("div", {
                    children: [R("#da4e48", "#fbe7e6"), "\u5931\u8d25"],
                  })
                : a;
            },
          },
          service_status: {
            title: "\u4e1a\u52a1\u72b6\u6001",
            key: "service_status",
            dataIndex: "service_status",
            sorter: function (a, r) {
              return a.service_status - r.service_status;
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: k,
          },
          product_service_status: {
            title: "\u8fd0\u884c\u72b6\u6001",
            width: 120,
            key: "product_service_status",
            dataIndex: "service_status",
            align: "center",
            render: function (a, r, t) {
              return f(a)
                ? "-"
                : 0 === a
                ? Object(_.jsxs)("div", {
                    children: [
                      R("#f5c773", "rgba(247, 231, 24,.2)"),
                      "\u672a\u5b89\u88c5",
                    ],
                  })
                : 1 === a
                ? Object(_.jsxs)("div", {
                    children: [
                      R("#f5c773", "rgba(247, 231, 24,.2)"),
                      "\u5b89\u88c5\u4e2d",
                    ],
                  })
                : 2 === a
                ? Object(_.jsxs)("div", {
                    children: [
                      R("rgb(84, 187, 166)", "rgb(238, 250, 244)"),
                      "\u6b63\u5e38",
                    ],
                  })
                : 3 === a
                ? Object(_.jsxs)("div", {
                    children: [R("#da4e48", "#fbe7e6"), "\u5f02\u5e38"],
                  })
                : 4 === a
                ? Object(_.jsxs)("div", {
                    children: [R("#da4e48", "#fbe7e6"), "\u505c\u6b62"],
                  })
                : 5 == a
                ? Object(_.jsxs)("div", {
                    children: [
                      R("#f5c773", "rgba(247, 231, 24,.2)"),
                      "\u542f\u52a8\u4e2d",
                    ],
                  })
                : 6 == a
                ? Object(_.jsxs)("div", {
                    children: [
                      R("#f5c773", "rgba(247, 231, 24,.2)"),
                      "\u505c\u6b62\u4e2d",
                    ],
                  })
                : 7 == a
                ? Object(_.jsxs)("div", {
                    children: [
                      R("#f5c773", "rgba(247, 231, 24,.2)"),
                      "\u91cd\u542f\u4e2d",
                    ],
                  })
                : -1 == a
                ? r.is_web_service
                  ? Object(_.jsxs)("div", {
                      children: [
                        R("rgb(84, 187, 166)", "rgb(238, 250, 244)"),
                        "\u6b63\u5e38",
                      ],
                    })
                  : Object(_.jsxs)("div", {
                      children: [
                        R("#f5c773", "rgba(247, 231, 24,.2)"),
                        "\u672a\u76d1\u63a7",
                      ],
                    })
                : a;
            },
          },
          product_thrityPart_status: {
            title: "\u8fd0\u884c\u72b6\u6001",
            key: "product_service_status",
            dataIndex: "state",
            align: "center",
            render: function (a, r, t) {
              return f(a)
                ? "-"
                : 1 === a
                ? Object(_.jsxs)("div", {
                    children: [
                      R("rgb(84, 187, 166)", "rgb(238, 250, 244)"),
                      "\u6b63\u5e38",
                    ],
                  })
                : 2 === a
                ? Object(_.jsxs)("div", {
                    children: [
                      R("#f5c773", "rgba(247, 231, 24,.2)"),
                      "\u5f02\u5e38",
                    ],
                  })
                : 0 === a
                ? Object(_.jsxs)("div", {
                    children: [R("#da4e48", "#fbe7e6"), "\u505c\u6b62"],
                  })
                : a;
            },
          },
          host_risk: {
            title: "\u4e3b\u673a\u98ce\u9669",
            key: "host_risk",
            dataIndex: "host_risk",
            sorter: function (a, r) {
              return a.host_risk - r.host_risk;
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: function (a, r, t) {
              return f(a) ? "-" : "".concat(a, "\u4e2a");
            },
          },
          service_risk: {
            title: "\u670d\u52a1\u98ce\u9669",
            key: "service_risk",
            dataIndex: "service_risk",
            sorter: function (a, r) {
              return a.service_risk - r.service_risk;
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: function (a, r, t) {
              return f(a) ? "-" : "".concat(a, "\u4e2a");
            },
          },
          start_time: {
            title: "\u5f00\u59cb\u65f6\u95f4",
            width: 160,
            key: "start_time",
            dataIndex: "start_time",
            sorter: function (a, r) {
              return v()(a.start_time).valueOf() - v()(r.start_time).valueOf();
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: k,
          },
          patrol_start_time: {
            title: "\u5f00\u59cb\u65f6\u95f4",
            width: 200,
            key: "patrol_start_time",
            dataIndex: "start_time",
            sorter: function (a, r) {
              return v()(a.start_time).valueOf() - v()(r.start_time).valueOf();
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: k,
          },
          patrol_end_time: {
            title: "\u7ed3\u675f\u65f6\u95f4",
            width: 160,
            key: "patrol_end_time",
            dataIndex: "end_time",
            sorter: function (a, r) {
              return v()(a.end_time).valueOf() - v()(r.end_time).valueOf();
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: k,
          },
          duration: {
            title: "\u7528\u65f6",
            width: 100,
            key: "duration",
            dataIndex: "duration",
            sorter: function (a, r) {
              return a.duration - r.duration;
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: A,
          },
          report_system: {
            title: "\u64cd\u4f5c\u7cfb\u7edf",
            key: "report_system",
            dataIndex: "system",
            render: k,
            align: "center",
          },
          report_risk_level: {
            title: "\u98ce\u9669\u7ea7\u522b",
            key: "report_risk_level",
            dataIndex: "risk_level",
            render: function (a, r, t) {
              switch (r.risk_level) {
                case "critical":
                  return Object(_.jsx)(D, {
                    backgroundColor: "#fbe7e6",
                    borderColor: "#da4e48",
                    text: "\u4e25\u91cd",
                  });
                case "warning":
                  return Object(_.jsx)(D, {
                    backgroundColor: "rgba(247, 231, 24,.2)",
                    borderColor: "#f5c773",
                    text: "\u8b66\u544a",
                  });
                default:
                  return "-";
              }
            },
            align: "center",
          },
          report_risk_describe: {
            title: "\u98ce\u9669\u63cf\u8ff0",
            key: "report_risk_describe",
            dataIndex: "risk_describe",
            ellipsis: !0,
            render: k,
            align: "center",
            width: 400,
          },
          report_resolve_info: {
            title: "\u89e3\u51b3\u65b9\u6848",
            key: "report_resolve_info",
            dataIndex: "resolve_info",
            render: k,
            align: "center",
          },
          report_release_version: {
            title: "\u64cd\u4f5c\u7cfb\u7edf",
            key: "report_release_version",
            dataIndex: "release_version",
            render: k,
            align: "center",
          },
          report_host_massage: {
            title: "\u914d\u7f6e\u4fe1\u606f",
            key: "report_host_massage",
            dataIndex: "host_massage",
            render: k,
            align: "center",
          },
          report_disk_usage_root: {
            title: "\u6839\u5206\u533a\u4f7f\u7528\u7387",
            width: 150,
            key: "report_disk_usage_root",
            dataIndex: "disk_usage_root",
            render: k,
            align: "center",
          },
          report_disk_usage_data: {
            title: "\u6570\u636e\u5206\u533a\u4f7f\u7528\u7387",
            width: 130,
            key: "report_disk_usage_data",
            dataIndex: "disk_usage_data",
            render: k,
            align: "center",
          },
          report_sys_load: {
            title: "\u5e73\u5747\u8d1f\u8f7d",
            key: "report_sys_load",
            dataIndex: "sys_load",
            render: k,
            align: "center",
          },
          report_idx: {
            title: "\u5e8f\u5217",
            key: "index",
            width: 50,
            render: function (a, r, t) {
              return "".concat(t + 1);
            },
            align: "center",
          },
          report_host_ip: {
            title: "IP\u5730\u5740",
            key: "report_host_ip",
            dataIndex: "host_ip",
            width: 150,
            render: k,
            align: "center",
          },
          report_log_level: {
            title: "\u65e5\u5fd7\u7b49\u7ea7",
            key: "report_log_level",
            dataIndex: "log_level",
            render: k,
            align: "center",
          },
          report_mem_usage: {
            title: "\u5185\u5b58\u4f7f\u7528\u7387",
            key: "report_mem_usage",
            dataIndex: "mem_usage",
            width: 100,
            render: k,
            align: "center",
          },
          report_cpu_usage: {
            title: "CPU\u4f7f\u7528\u7387",
            key: "report_cpu_usage",
            dataIndex: "cpu_usage",
            width: 110,
            render: k,
            align: "center",
          },
          report_service_name: {
            title: "\u670d\u52a1\u540d\u79f0",
            key: "report_service_name",
            dataIndex: "service_name",
            render: k,
            align: "center",
          },
          report_service_port: {
            title: "\u7aef\u53e3\u53f7",
            key: "report_service_port",
            dataIndex: "service_port",
            render: function (a, r, t) {
              return a || "-";
            },
            align: "center",
          },
          report_service_status: {
            title: "\u8fd0\u884c\u72b6\u6001",
            key: "report_service_status",
            dataIndex: "service_status",
            render: k,
            align: "center",
          },
          report_run_time: {
            title: "\u8fd0\u884c\u65f6\u95f4",
            width: 120,
            key: "report_run_time",
            dataIndex: "run_time",
            render: k,
            align: "center",
          },
          report_cluster_name: {
            title: "\u96c6\u7fa4\u540d\u79f0",
            key: "report_cluster_name",
            dataIndex: "cluster_name",
            render: k,
            align: "center",
          },
          operator: {
            title: "\u64cd\u4f5c\u4eba\u5458",
            key: "operator",
            dataIndex: "operator",
            align: "center",
            width: 80,
          },
          install_process: {
            title: "\u5b89\u88c5\u8fdb\u5ea6",
            key: "install_process",
            dataIndex: "install_process",
            align: "center",
            width: 80,
            render: function (a) {
              return "0%" == a
                ? Object(_.jsxs)("span", {
                    children: [R("#da4e48", "#fbe7e6"), "\u5931\u8d25"],
                  })
                : "100%" == a
                ? Object(_.jsxs)("span", {
                    children: [
                      R("rgb(84, 187, 166)", "rgb(238, 250, 244)"),
                      "\u6210\u529f",
                    ],
                  })
                : a;
            },
          },
          verson_start_time: {
            title: "\u5f00\u59cb\u65f6\u95f4",
            key: "start_time",
            dataIndex: "start_time",
            align: "center",
            width: 160,
          },
          verson_end_time: {
            title: "\u7ed3\u675f\u65f6\u95f4",
            key: "end_time",
            dataIndex: "end_time",
            align: "center",
            width: 150,
          },
          use_time: {
            title: "\u7528\u65f6",
            key: "duration",
            dataIndex: "duration",
            render: function (a) {
              if (a && "-" !== a) {
                var r = v.a.duration(a, "seconds"),
                  t = r.hours(),
                  e = t ? "".concat(t, "\u5c0f\u65f6") : "",
                  o = r.minutes(),
                  p = o % 60 ? "".concat(o % 60, "\u5206\u949f") : "",
                  i = r.seconds(),
                  d = i % 60 ? "".concat(i % 60, "\u79d2") : "";
                return "".concat(e, " ").concat(p, " ").concat(d);
              }
              return "-";
            },
            align: "center",
            width: 100,
          },
          execution_mdoal: {
            title: "\u6267\u884c\u65b9\u5f0f",
            align: "center",
            dataIndex: "execute_type",
            key: "execute_type",
            render: function (a) {
              return "man" == a
                ? "\u624b\u52a8\u6267\u884c"
                : "auto" == a
                ? "\u5b9a\u65f6\u6267\u884c"
                : "-";
            },
            width: 80,
          },
          machine_idx: {
            title: "\u5e8f\u5217",
            key: "index",
            render: function (a, r, t) {
              return "".concat(r._idx);
            },
            align: "center",
            width: 60,
          },
          service_idx: {
            title: "\u5e8f\u5217",
            key: "index",
            dataIndex: "_idx",
            align: "center",
            width: 60,
          },
          service_port_new: {
            title: "\u7aef\u53e3",
            width: 100,
            key: "service_port",
            dataIndex: "service_port",
            sorter: function (a, r) {
              return a.service_port - r.service_port;
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: function (a) {
              return a || "-";
            },
          },
          _port_new: {
            title: "\u7aef\u53e3",
            key: "port",
            dataIndex: "port",
            sorter: function (a, r) {
              return a.port - r.port;
            },
            sortDirections: ["descend", "ascend"],
            align: "center",
            render: function (a) {
              return a || "-";
            },
          },
        },
        w = [
          {
            title: "\u670d\u52a1",
            dataIndex: "name",
            className: E._bigfontSize,
          },
          {
            title: "IP\u5730\u5740",
            dataIndex: "ip",
            align: "center",
            className: E._bigfontSize,
          },
          {
            title: "\u7aef\u53e3",
            dataIndex: "port",
            align: "center",
            className: E._bigfontSize,
          },
          {
            title: "\u8fde\u901a\u6027",
            dataIndex: "status",
            align: "center",
            className: E._bigfontSize,
            render: function (a) {
              return Object(_.jsx)("div", {
                style: { color: "False" == a ? "rgb(207, 19, 34)" : null },
                children: a,
              });
            },
          },
        ],
        h = [
          { title: "Topic", dataIndex: "topic", className: E._bigfontSize },
          {
            title: "\u5206\u533a\u6570",
            dataIndex: "partition",
            align: "center",
            className: E._bigfontSize,
          },
          {
            title: "\u526f\u672c\u6570",
            dataIndex: "replication",
            align: "center",
            className: E._bigfontSize,
          },
        ],
        P = [
          { title: "Group", dataIndex: "group", className: E._bigfontSize },
          { title: "Topic", dataIndex: "topic", className: E._bigfontSize },
          {
            title: "Log Offset",
            dataIndex: "log_offset",
            align: "center",
            className: E._bigfontSize,
          },
          {
            title: "Lag Offset",
            dataIndex: "lag_offset",
            align: "center",
            className: E._bigfontSize,
          },
        ],
        C = [
          { title: "Topic", dataIndex: "topic", className: E._bigfontSize },
          {
            title: "Size",
            dataIndex: "size",
            align: "center",
            className: E._bigfontSize,
          },
        ];
      var M = t(341),
        X = t(342),
        G = t(339),
        O = t(340),
        B = t(99),
        U = t(69),
        N = t(0),
        T = (t(221), t(22)),
        F = m.a.Panel,
        z = [
          Object(j.a)(
            Object(j.a)({}, x.report_service_name),
            {},
            { className: "_bigfontSize" }
          ),
          Object(j.a)(
            Object(j.a)({}, x.report_host_ip),
            {},
            { className: "_bigfontSize" }
          ),
          Object(j.a)(
            Object(j.a)({}, x.report_service_port),
            {},
            { className: "_bigfontSize" }
          ),
          Object(j.a)(
            Object(j.a)({}, x.report_service_status),
            {},
            { className: "_bigfontSize" }
          ),
          Object(j.a)(
            Object(j.a)({}, x.report_cpu_usage),
            {},
            { className: "_bigfontSize" }
          ),
          Object(j.a)(
            Object(j.a)({}, x.report_mem_usage),
            {},
            { className: "_bigfontSize" }
          ),
          Object(j.a)(
            Object(j.a)({}, x.report_run_time),
            {},
            { className: "_bigfontSize" }
          ),
          Object(j.a)(
            Object(j.a)({}, x.report_log_level),
            {},
            { className: "_bigfontSize" }
          ),
        ];
      function I() {
        var a = Object(N.useState)(!1),
          r = Object(b.a)(a, 2),
          t = r[0],
          e = r[1],
          o = Object(N.useState)(""),
          p = Object(b.a)(o, 2),
          i = p[0],
          d = p[1],
          l = Object(N.useState)([]),
          u = Object(b.a)(l, 2);
        u[0], u[1];
        return Object(_.jsxs)("div", {
          id: "reportContent",
          className: "reportContent",
          children: [
            Object(_.jsx)("div", {
              className: "reportTitle",
              children: Object(_.jsxs)("div", {
                children: [" ", "\u5de1\u68c0\u62a5\u544a"],
              }),
            }),
            Object(_.jsx)("div", {
              children: Object(_.jsxs)(m.a, {
                bordered: !1,
                defaultActiveKey: [
                  "overview",
                  "risk",
                  "map",
                  "host",
                  "database",
                  "component",
                  "service",
                ],
                style: { marginTop: 10 },
                expandIcon: function (a) {
                  var r = a.isActive;
                  return Object(_.jsx)(s.a, {
                    type: "caret-right",
                    rotate: r ? 90 : 0,
                  });
                },
                children: [
                  Object(_.jsx)(
                    F,
                    {
                      header: "\u6982\u8ff0\u4fe1\u606f",
                      className: "panelItem",
                      children: Object(_.jsxs)("div", {
                        className: "overviewItemWrapper",
                        children: [
                          Object(_.jsx)(Z, {
                            data: T.summary.task_info,
                            type: "task_info",
                          }),
                          Object(_.jsx)(Z, {
                            data: T.summary.time_info,
                            type: "time_info",
                          }),
                          Object(_.jsx)(Z, {
                            data: T.summary.scan_info,
                            type: "scan_info",
                          }),
                          Object(_.jsx)(Z, {
                            data: T.summary.scan_result,
                            type: "scan_result",
                          }),
                        ],
                      }),
                    },
                    "overview"
                  ),
                  T.risks &&
                    (!M.a(T.risks.host_list) || !M.a(T.risks.service_list)) &&
                    Object(_.jsxs)(
                      F,
                      {
                        header: "\u98ce\u9669\u6307\u6807",
                        className: "panelItem",
                        children: [
                          T.risks.host_list.length > 0 &&
                            Object(_.jsx)(c.a, {
                              style: { marginTop: 20 },
                              size: "small",
                              pagination: !1,
                              rowKey: function (a, r) {
                                return r;
                              },
                              columns: [
                                Object(j.a)(
                                  Object(j.a)({}, x.report_idx),
                                  {},
                                  { className: "_bigfontSize" }
                                ),
                                Object(j.a)(
                                  Object(j.a)({}, x.report_host_ip),
                                  {},
                                  { className: "_bigfontSize" }
                                ),
                                Object(j.a)(
                                  Object(j.a)({}, x.report_system),
                                  {},
                                  { className: "_bigfontSize" }
                                ),
                                Object(j.a)(
                                  Object(j.a)({}, x.report_risk_level),
                                  {},
                                  { className: "_bigfontSize" }
                                ),
                                Object(j.a)(
                                  Object(j.a)({}, x.report_risk_describe),
                                  {},
                                  {
                                    className: "_bigfontSize",
                                    render: function (a) {
                                      return Object(_.jsx)("span", {
                                        style: { cursor: "pointer" },
                                        onClick: function () {
                                          console.log(a), d(a), e(!0);
                                        },
                                        children: a,
                                      });
                                    },
                                  }
                                ),
                                Object(j.a)(
                                  Object(j.a)({}, x.report_resolve_info),
                                  {},
                                  { className: "_bigfontSize" }
                                ),
                              ],
                              title: function () {
                                return "\u4e3b\u673a\u6307\u6807";
                              },
                              dataSource: T.risks.host_list,
                            }),
                          T.risks.service_list.length > 0 &&
                            Object(_.jsx)(c.a, {
                              style: { marginTop: 20 },
                              size: "small",
                              pagination: !1,
                              rowKey: function (a, r) {
                                return r;
                              },
                              columns: [
                                Object(j.a)(
                                  Object(j.a)({}, x.report_idx),
                                  {},
                                  { className: "_bigfontSize" }
                                ),
                                Object(j.a)(
                                  Object(j.a)({}, x.report_service_name),
                                  {},
                                  { className: "_bigfontSize" }
                                ),
                                Object(j.a)(
                                  Object(j.a)({}, x.report_host_ip),
                                  {},
                                  { className: "_bigfontSize" }
                                ),
                                Object(j.a)(
                                  Object(j.a)({}, x.report_service_port),
                                  {},
                                  { className: "_bigfontSize" }
                                ),
                                Object(j.a)(
                                  Object(j.a)({}, x.report_risk_level),
                                  {},
                                  { className: "_bigfontSize" }
                                ),
                                Object(j.a)(
                                  Object(j.a)({}, x.report_risk_describe),
                                  {},
                                  {
                                    className: "_bigfontSize",
                                    render: function (a) {
                                      return Object(_.jsx)("span", {
                                        style: { cursor: "pointer" },
                                        onClick: function () {
                                          console.log(a), d(a), e(!0);
                                        },
                                        children: a,
                                      });
                                    },
                                  }
                                ),
                                Object(j.a)(
                                  Object(j.a)({}, x.report_resolve_info),
                                  {},
                                  { className: "_bigfontSize" }
                                ),
                              ],
                              title: function () {
                                return "\u670d\u52a1\u6307\u6807";
                              },
                              dataSource: T.risks.service_list,
                            }),
                        ],
                      },
                      "risk"
                    ),
                  !X.a(G.a, M.a)(T.service_topology) &&
                    Object(_.jsx)(
                      F,
                      {
                        header: "\u670d\u52a1\u5e73\u9762\u56fe",
                        className: "panelItem",
                        children: Object(_.jsx)("div", {
                          style: {
                            display: "flex",
                            flexFlow: "row wrap",
                            margin: 10,
                          },
                          children: O.a(B.a)(function (a, r) {
                            return Object(_.jsx)(
                              J,
                              {
                                title: a.host_ip,
                                list: a.service_list,
                                data: T,
                              },
                              r
                            );
                          }, T.service_topology),
                        }),
                      },
                      "map"
                    ),
                  !X.a(G.a, M.a)(T.detail_dict.host) &&
                    Object(_.jsx)(
                      F,
                      {
                        header: "\u4e3b\u673a\u5217\u8868",
                        className: "panelItem",
                        children: Object(_.jsx)(c.a, {
                          size: "small",
                          style: { marginTop: 20 },
                          scroll: { x: 1100 },
                          pagination: !1,
                          rowKey: function (a) {
                            return a.id;
                          },
                          columns: [
                            Object(j.a)(
                              Object(j.a)({}, x.report_idx),
                              {},
                              { className: "_bigfontSize" }
                            ),
                            Object(j.a)(
                              Object(j.a)({}, x.report_host_ip),
                              {},
                              { className: "_bigfontSize" }
                            ),
                            Object(j.a)(
                              Object(j.a)({}, x.report_release_version),
                              {},
                              { className: "_bigfontSize" }
                            ),
                            Object(j.a)(
                              Object(j.a)({}, x.report_host_massage),
                              {},
                              { className: "_bigfontSize" }
                            ),
                            Object(j.a)(
                              Object(j.a)({}, x.report_cpu_usage),
                              {},
                              { className: "_bigfontSize" }
                            ),
                            Object(j.a)(
                              Object(j.a)({}, x.report_mem_usage),
                              {},
                              { className: "_bigfontSize" }
                            ),
                            Object(j.a)(
                              Object(j.a)({}, x.report_disk_usage_root),
                              {},
                              { className: "_bigfontSize" }
                            ),
                            Object(j.a)(
                              Object(j.a)({}, x.report_disk_usage_data),
                              {},
                              { className: "_bigfontSize" }
                            ),
                            Object(j.a)(
                              Object(j.a)({}, x.report_run_time),
                              {},
                              { className: "_bigfontSize" }
                            ),
                            Object(j.a)(
                              Object(j.a)({}, x.report_sys_load),
                              {},
                              { className: "_bigfontSize" }
                            ),
                          ],
                          expandedRowRender: function () {
                            for (
                              var a = arguments.length, r = new Array(a), o = 0;
                              o < a;
                              o++
                            )
                              r[o] = arguments[o];
                            return (
                              (r[0].basic = r[0].basic.filter(function (a) {
                                return "cluster_ip" !== a.name;
                              })),
                              K.apply(void 0, r.concat([t, e, i, d]))
                            );
                          },
                          dataSource: T.detail_dict.host,
                        }),
                      },
                      "host"
                    ),
                  !X.a(G.a, M.a)(T.detail_dict.database) &&
                    Object(_.jsx)(
                      F,
                      {
                        header: "\u6570\u636e\u5e93\u5217\u8868",
                        className: "panelItem",
                        children: Object(_.jsx)(c.a, {
                          size: "small",
                          style: { marginTop: 20 },
                          pagination: !1,
                          rowKey: function (a, r) {
                            return a.id;
                          },
                          columns: z,
                          expandedRowRender: function () {
                            for (
                              var a = arguments.length, r = new Array(a), o = 0;
                              o < a;
                              o++
                            )
                              r[o] = arguments[o];
                            (r[0].basic = r[0].basic.filter(function (a) {
                              return "cluster_ip" !== a.name;
                            })),
                              K.apply(void 0, r.concat([t, e, i, d]));
                          },
                          dataSource: T.detail_dict.database,
                        }),
                      },
                      "database"
                    ),
                  !X.a(G.a, M.a)(T.detail_dict.component) &&
                    Object(_.jsx)(
                      F,
                      {
                        header: "\u7ec4\u4ef6\u5217\u8868",
                        className: "panelItem",
                        children: Object(_.jsx)(c.a, {
                          size: "small",
                          style: { marginTop: 20 },
                          pagination: !1,
                          rowKey: function (a, r) {
                            return a.id;
                          },
                          columns: z,
                          expandedRowRender: function () {
                            for (
                              var a = arguments.length, r = new Array(a), o = 0;
                              o < a;
                              o++
                            )
                              r[o] = arguments[o];
                            return (
                              (r[0].basic = r[0].basic.filter(function (a) {
                                return "cluster_ip" !== a.name;
                              })),
                              K.apply(void 0, r.concat([t, e, i, d]))
                            );
                          },
                          dataSource: T.detail_dict.component,
                        }),
                      },
                      "component"
                    ),
                  !X.a(G.a, M.a)(T.detail_dict.service) &&
                    Object(_.jsx)(
                      F,
                      {
                        header: "\u670d\u52a1\u5217\u8868",
                        className: "panelItem",
                        children: Object(_.jsx)(c.a, {
                          size: "small",
                          style: { marginTop: 20 },
                          pagination: !1,
                          rowKey: function (a, r) {
                            return a.id;
                          },
                          columns: z,
                          expandedRowRender: function () {
                            for (
                              var a = arguments.length, r = new Array(a), o = 0;
                              o < a;
                              o++
                            )
                              r[o] = arguments[o];
                            return (
                              (r[0].basic = r[0].basic.filter(function (a) {
                                return "cluster_ip" !== a.name;
                              })),
                              K.apply(void 0, r.concat([t, e, i, d]))
                            );
                          },
                          dataSource: T.detail_dict.service,
                        }),
                      },
                      "service"
                    ),
                ],
              }),
            }),
            Object(_.jsx)(n.a, {
              title: "\u8fdb\u7a0b\u65e5\u5fd7",
              placement: "right",
              closable: !1,
              onClose: function () {
                return e(!1);
              },
              visible: t,
              width: 720,
              destroyOnClose: !0,
              children: i,
            }),
          ],
        });
      }
      function H() {
        var a =
            arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : 0,
          r = a,
          t = Math.round(Number(a)),
          e = Math.floor(t / 86400),
          o = Math.floor((t % 86400) / 3600),
          p = Math.floor(((t % 86400) % 3600) / 60),
          i = Math.floor(((t % 86400) % 3600) % 60);
        return (
          e > 0
            ? (r =
                e + "\u5929" + o + "\u5c0f\u65f6" + p + "\u5206" + i + "\u79d2")
            : o > 0
            ? (r = o + "\u5c0f\u65f6" + p + "\u5206" + i + "\u79d2")
            : p > 0
            ? (r = p + "\u5206" + i + "\u79d2")
            : i > 0 && (r = i + "\u79d2"),
          r
        );
      }
      function Z(a) {
        var r = a.data;
        switch (a.type) {
          case "task_info":
            return Object(_.jsxs)("div", {
              className: "overviewItem",
              children: [
                Object(_.jsx)("div", { children: "\u4efb\u52a1\u4fe1\u606f" }),
                Object(_.jsxs)("div", {
                  children: [
                    Object(_.jsxs)("div", {
                      children: ["\u4efb\u52a1\u540d\u79f0\uff1a", r.task_name],
                    }),
                    Object(_.jsxs)("div", {
                      children: ["\u64cd\u4f5c\u4eba\u5458\uff1a", r.operator],
                    }),
                    Object(_.jsxs)("div", {
                      children: [
                        "\u4efb\u52a1\u72b6\u6001\uff1a",
                        2 === r.task_status
                          ? "\u5df2\u5b8c\u6210"
                          : "\u5931\u8d25",
                      ],
                    }),
                  ],
                }),
              ],
            });
          case "time_info":
            return Object(_.jsxs)("div", {
              className: "overviewItem",
              children: [
                Object(_.jsx)("div", { children: "\u65f6\u95f4\u7edf\u8ba1" }),
                Object(_.jsxs)("div", {
                  children: [
                    Object(_.jsxs)("div", {
                      children: [
                        "\u5f00\u59cb\u65f6\u95f4\uff1a",
                        r.start_time,
                      ],
                    }),
                    Object(_.jsxs)("div", {
                      children: ["\u7ed3\u675f\u65f6\u95f4\uff1a", r.end_time],
                    }),
                    Object(_.jsxs)("div", {
                      children: ["\u4efb\u52a1\u8017\u65f6\uff1a", H(r.cost)],
                    }),
                  ],
                }),
              ],
            });
          case "scan_info":
            return Object(_.jsxs)("div", {
              className: "overviewItem",
              children: [
                Object(_.jsx)("div", { children: "\u626b\u63cf\u7edf\u8ba1" }),
                Object(_.jsx)("div", {
                  style: { display: "flex", alignItems: "center" },
                  children: Object(_.jsxs)("div", {
                    children: [
                      r.host > 0 &&
                        Object(_.jsxs)("div", {
                          children: [
                            "\u4e3b\u673a\u4e2a\u6570\uff1a",
                            r.host,
                            "\u53f0",
                          ],
                        }),
                      r.component > 0 &&
                        Object(_.jsxs)("div", {
                          children: [
                            "\u7ec4\u4ef6\u4e2a\u6570\uff1a",
                            r.component,
                            "\u4e2a",
                          ],
                        }),
                      r.service > 0 &&
                        Object(_.jsxs)("div", {
                          children: [
                            "\u670d\u52a1\u4e2a\u6570\uff1a",
                            r.service,
                            "\u4e2a",
                          ],
                        }),
                    ],
                  }),
                }),
              ],
            });
          case "scan_result":
            return Object(_.jsxs)("div", {
              className: "overviewItem",
              children: [
                Object(_.jsx)("div", { children: "\u5206\u6790\u7ed3\u679c" }),
                Object(_.jsx)("div", {
                  style: { display: "flex", alignItems: "center" },
                  children: Object(_.jsxs)("div", {
                    children: [
                      Object(_.jsxs)("div", {
                        children: [
                          "\u603b\u6307\u6807\u6570\uff1a",
                          r.all_target_num,
                        ],
                      }),
                      Object(_.jsxs)("div", {
                        children: [
                          "\u5f02\u5e38\u6307\u6807\uff1a",
                          r.abnormal_target,
                        ],
                      }),
                    ],
                  }),
                }),
              ],
            });
        }
      }
      function J(a) {
        var r = a.title,
          t = a.list;
        a.data;
        return Object(_.jsxs)("div", {
          className: "planChartWrapper",
          children: [
            Object(_.jsxs)("div", {
              className: "planChartTitle",
              children: [
                Object(_.jsx)("span", { className: "planChartTitleCircular" }),
                r,
              ],
            }),
            Object(_.jsx)("div", {
              className: "planChartBlockWrapper",
              children: t.map(function (a) {
                return Object(_.jsx)(
                  "div",
                  {
                    className: "stateButton",
                    children: Object(_.jsx)("div", { children: a }),
                  },
                  a
                );
              }),
            }),
          ],
        });
      }
      function K(a) {
        for (
          var r = a.basic,
            t =
              (a.host_ip,
              a.service_status,
              a.run_time,
              a.log_level,
              a.mem_usage,
              a.cpu_usage,
              a.service_name,
              a.service_port,
              a.cluster_name,
              a.release_version,
              a.host_massage,
              a.disk_usage_root,
              a.disk_usage_data,
              a.sys_load,
              Object(l.a)(a, [
                "basic",
                "host_ip",
                "service_status",
                "run_time",
                "log_level",
                "mem_usage",
                "cpu_usage",
                "service_name",
                "service_port",
                "cluster_name",
                "release_version",
                "host_massage",
                "disk_usage_root",
                "disk_usage_data",
                "sys_load",
              ])),
            e =
              (t.topic_partition,
              t.kafka_offsets,
              t.topic_size,
              arguments.length),
            o = new Array(e > 1 ? e - 1 : 0),
            p = 1;
          p < e;
          p++
        )
          o[p - 1] = arguments[p];
        var i = o.slice(-4),
          d = Object(b.a)(i, 4),
          j = d[0],
          u = d[1],
          g = d[2],
          v = d[3],
          S = Object.entries(t).filter(function (a) {
            return Array.isArray(a[1]);
          }),
          E = [
            {
              title: "TOP",
              dataIndex: "TOP",
              width: 50,
              className: "_bigfontSize",
            },
            {
              title: "PID",
              dataIndex: "PID",
              align: "center",
              width: 100,
              className: "_bigfontSize",
            },
            {
              title: "\u4f7f\u7528\u7387",
              dataIndex: "P_RATE",
              align: "center",
              width: 100,
              className: "_bigfontSize",
            },
            {
              title: "\u8fdb\u7a0b",
              dataIndex: "P_CMD",
              ellipsis: !0,
              className: "_bigfontSize",
              render: function (a) {
                return Object(_.jsx)("span", {
                  style: { cursor: "pointer" },
                  onClick: function () {
                    v(a), u(!0);
                  },
                  children: a,
                });
              },
            },
          ],
          f = {
            port_connectivity: {
              columns: w,
              dataSource: t.port_connectivity,
              title: "\u7aef\u53e3\u8fde\u901a\u6027",
            },
            memory_top: {
              columns: E,
              dataSource: t.memory_top,
              title: "\u5185\u5b58\u4f7f\u7528\u7387Top10\u8fdb\u7a0b",
            },
            cpu_top: {
              columns: E,
              dataSource: t.cpu_top,
              title: "cpu\u4f7f\u7528\u7387Top10\u8fdb\u7a0b",
            },
            kernel_parameters: {
              columns: [],
              dataSource: t.kernel_parameters,
              title: "\u5185\u6838\u53c2\u6570",
            },
            topic_partition: {
              columns: h,
              dataSource: t.topic_partition,
              title: "\u5206\u533a\u4fe1\u606f",
            },
            kafka_offsets: {
              columns: P,
              dataSource: t.kafka_offsets,
              title: "\u6d88\u8d39\u4f4d\u79fb\u4fe1\u606f",
            },
            topic_size: {
              columns: C,
              dataSource: t.topic_size,
              title: "Topic\u6d88\u606f\u5927\u5c0f",
            },
          };
        return Object(_.jsxs)("div", {
          className: "expandedRowWrapper",
          children: [
            Array.isArray(r) && Object(_.jsx)(q, { basic: r }),
            S.length > 0 &&
              Object(_.jsx)(m.a, {
                defaultActiveKey: U.a(t),
                style: { marginTop: 10 },
                expandIcon: function (a) {
                  var r = a.isActive;
                  return Object(_.jsx)(s.a, {
                    type: "caret-right",
                    rotate: r ? 90 : 0,
                  });
                },
                children: S.map(function (a, r) {
                  var t = f[a[0]];
                  if (!G.a(t))
                    return Object(_.jsx)(
                      F,
                      {
                        header: t.title,
                        children:
                          t.columns.length > 0
                            ? Object(_.jsx)(c.a, {
                                rowKey: function (a, r) {
                                  return r;
                                },
                                size: "small",
                                columns: t.columns,
                                dataSource: t.dataSource,
                                pagination: !1,
                              })
                            : Object(_.jsx)("div", {
                                className: "basicCardWrapper",
                                children: t.dataSource.map(function (a, r) {
                                  return Object(_.jsx)(
                                    "div",
                                    { className: "basicCardItem", children: a },
                                    r
                                  );
                                }),
                              }),
                      },
                      a[0]
                    );
                  console.log("\u672a\u914d\u7f6e\u7684\u6570\u636e\u9879", a);
                }),
              }),
            Object(_.jsx)(n.a, {
              title: "\u8fdb\u7a0b\u65e5\u5fd7",
              placement: "right",
              closable: !1,
              onClose: function () {
                return u(!1);
              },
              visible: j,
              width: 720,
              destroyOnClose: !0,
              children: g,
            }),
          ],
        });
      }
      function q(a) {
        var r = a.basic;
        return Object(_.jsx)(d.a, {
          children: Object(_.jsx)("div", {
            className: "basicCardWrapper",
            children: r.map(function (a, r) {
              return Object(_.jsxs)(
                "div",
                {
                  className: "basicCardItem",
                  children: [
                    Object(_.jsxs)("span", {
                      style: { color: "#333" },
                      children: [a.name_cn, ": "],
                    }),
                    Object(_.jsx)("span", {
                      children: k(JSON.stringify(a.value)),
                    }),
                  ],
                },
                r
              );
            }),
          }),
        });
      }
      var W = function () {
        return Object(_.jsx)(p.a, {
          locale: i.a,
          children: Object(_.jsx)(I, {}),
        });
      };
      o.a.render(Object(_.jsx)(W, {}), document.getElementById("root"));
    },
  },
  [[331, 1, 2]],
]);
//# sourceMappingURL=main.e4ade54a.chunk.js.map
