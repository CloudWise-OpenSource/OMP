import { Button, Anchor, Spin } from "antd";
import { useSelector } from "react-redux";
import InstallInfoItem from "../component/InstallInfoItem";
import { useEffect, useRef, useState } from "react";
import { LoadingOutlined } from "@ant-design/icons";
import { apiRequest } from "@/config/requestApi";
import { fetchGet } from "@/utils/request";
import { handleResponse } from "@/utils/utils";
import { useHistory } from "react-router-dom";

const { Link } = Anchor;
// 状态渲染规则
const renderStatus = {
  0: "等待安装",
  1: "安装中",
  2: "安装成功",
  3: "安装失败",
};

const Step4 = () => {
  const viewHeight = useSelector((state) => state.layouts.viewSize.height);
  const [openName, setOpenName] = useState("");
  // 在轮训时使用ref存值
  const openNameRef = useRef(null);

  const uniqueKey = useSelector((state) => state.appStore.uniqueKey);

  const [loading, setLoading] = useState(true);

  const [data, setData] = useState({
    detail: {},
    status: 0,
  });

  const [log, setLog] = useState("");

  const history = useHistory();

  // const data = {
  //   status: 1,
  //   detail: {
  //     mysql: [
  //       { ip: "10.0.1.1", status: 2 },
  //       { ip: "10.0.1.2", status: 3 },
  //       { ip: "10.0.1.9", status: 3 },
  //     ],
  //     redis: [
  //       { ip: "10.0.1.1", status: 2 },
  //       { ip: "10.0.1.2", status: 0 },
  //     ],
  //     zookeeper: [
  //       { ip: "10.0.1.1", status: 2 },
  //       { ip: "10.0.1.2", status: 2 },
  //     ],
  //     rocketmq: [
  //       { ip: "10.0.1.1", status: 2 },
  //       { ip: "10.0.1.2", status: 2 },
  //     ],
  //     arangodb: [
  //       { ip: "10.0.1.1", status: 2 },
  //       { ip: "10.0.1.2", status: 2 },
  //     ],
  //     elasticsearch: [
  //       { ip: "10.0.1.1", status: 2 },
  //       { ip: "10.0.1.2", status: 2 },
  //     ],
  //     httpd: [
  //       { ip: "10.0.1.1", status: 2 },
  //       { ip: "10.0.1.2", status: 2 },
  //     ],
  //     ignite: [
  //       { ip: "10.0.1.1", status: 2 },
  //       { ip: "10.0.1.2", status: 2 },
  //     ],
  //     tengine: [
  //       { ip: "10.0.1.1", status: 2 },
  //       { ip: "10.0.1.2", status: 2 },
  //     ],
  //   },
  // };

  // 轮训的timer控制器
  const timer = useRef(null);

  const queryInstallProcess = () => {
    !timer.current && setLoading(true);
    fetchGet(apiRequest.appStore.queryInstallProcess, {
      params: {
        unique_key: uniqueKey || "21e041a9-c9a5-4734-9673-7ed932625d21",
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          // console.log(res);
          console.log(res.data);
          setData(res.data);
          if (res.data.status == 0 || res.data.status == 1) {
            // 状态为未安装或者安装中
            console.log("开始轮训");
            console.log(openName, res.data, openNameRef.current);
            if (openNameRef.current) {
              let arr = openNameRef.current.split("=");
              queryDetailInfo(uniqueKey, arr[1], arr[0]);
            }

            timer.current = setTimeout(() => {
              queryInstallProcess();
            }, 5000);
          }
          //setDataSource(res.data);
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
        unique_key: uniqueKey || "21e041a9-c9a5-4734-9673-7ed932625d21",
        app_name: app_name,
        ip: ip,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          // console.log(res);
          console.log(res, "打印了log");
          //setDataSource(res.data);
          setLog(res.data.log);
          // setLog(`2021-11-02 22:12:05 redis-7-194 开始发送服务包\n2021-11-02 22:12:06 redis-7-194 成功发送服务包\n2021-11-02 22:12:07 redis-7-194 开始解压服务包\n2021-11-02 22:12:07 redis-7-194 成功解压服务包\n2021-11-02 22:12:08 redis-7-194 开始安装服务\n2021-11-02 22:12:09 安装脚本执行成功，脚本输出如下:\n开始检查目录\n开始创建用户,修改目录权限\n开始更新文件占位符\n开始声明环境变量\n2021-11-02 22:12:09 redis-7-194 成功安装服务\n2021-11-02 22:12:12 启动脚本执行成功，脚本输出如下:\nredis  [running]\n2021-11-02 22:12:10 redis-7-194 开始初始化服务\n2021-11-02 22:12:10 redis-7-194 无需执行初始化\n2021-11-02 22:12:10 redis-7-194 开始启动服务\n2021-11-02 22:12:13 redis-7-194 成功启动服务\n
          // 2021-11-02 22:12:05 redis-7-194 开始发送服务包\n2021-11-02 22:12:06 redis-7-194 成功发送服务包\n2021-11-02 22:12:07 redis-7-194 开始解压服务包\n2021-11-02 22:12:07 redis-7-194 成功解压服务包\n2021-11-02 22:12:08 redis-7-194 开始安装服务\n2021-11-02 22:12:09 安装脚本执行成功，脚本输出如下:\n开始检查目录\n开始创建用户,修改目录权限\n开始更新文件占位符\n开始声明环境变量\n2021-11-02 22:12:09 redis-7-194 成功安装服务\n2021-11-02 22:12:12 启动脚本执行成功，脚本输出如下:\nredis  [running]\n2021-11-02 22:12:10 redis-7-194 开始初始化服务\n2021-11-02 22:12:10 redis-7-194 无需执行初始化\n2021-11-02 22:12:10 redis-7-194 开始启动服务\n2021-11-02 22:12:13 redis-7-194 成功启动服务\n
          // 2021-11-02 22:12:05 redis-7-194 开始发送服务包\n2021-11-02 22:12:06 redis-7-194 成功发送服务包\n2021-11-02 22:12:07 redis-7-194 开始解压服务包\n2021-11-02 22:12:07 redis-7-194 成功解压服务包\n2021-11-02 22:12:08 redis-7-194 开始安装服务\n2021-11-02 22:12:09 安装脚本执行成功，脚本输出如下:\n开始检查目录\n开始创建用户,修改目录权限\n开始更新文件占位符\n开始声明环境变量\n2021-11-02 22:12:09 redis-7-194 成功安装服务\n2021-11-02 22:12:12 启动脚本执行成功，脚本输出如下:\nredis  [running]\n2021-11-02 22:12:10 redis-7-194 开始初始化服务\n2021-11-02 22:12:10 redis-7-194 无需执行初始化\n2021-11-02 22:12:10 redis-7-194 开始启动服务\n2021-11-02 22:12:13 redis-7-194 成功启动服务\n
          // 2021-11-02 22:12:05 redis-7-194 开始发送服务包\n2021-11-02 22:12:06 redis-7-194 成功发送服务包\n2021-11-02 22:12:07 redis-7-194 开始解压服务包\n2021-11-02 22:12:07 redis-7-194 成功解压服务包\n2021-11-02 22:12:08 redis-7-194 开始安装服务\n2021-11-02 22:12:09 安装脚本执行成功，脚本输出如下:\n开始检查目录\n开始创建用户,修改目录权限\n开始更新文件占位符\n开始声明环境变量\n2021-11-02 22:12:09 redis-7-194 成功安装服务\n2021-11-02 22:12:12 启动脚本执行成功，脚本输出如下:\nredis  [running]\n2021-11-02 22:12:10 redis-7-194 开始初始化服务\n2021-11-02 22:12:10 redis-7-194 无需执行初始化\n2021-11-02 22:12:10 redis-7-194 开始启动服务\n2021-11-02 22:12:13 redis-7-194 成功启动服务\n
          // 2021-11-02 22:12:05 redis-7-194 开始发送服务包\n2021-11-02 22:12:06 redis-7-194 成功发送服务包\n2021-11-02 22:12:07 redis-7-194 开始解压服务包\n2021-11-02 22:12:07 redis-7-194 成功解压服务包\n2021-11-02 22:12:08 redis-7-194 开始安装服务\n2021-11-02 22:12:09 安装脚本执行成功，脚本输出如下:\n开始检查目录\n开始创建用户,修改目录权限\n开始更新文件占位符\n开始声明环境变量\n2021-11-02 22:12:09 redis-7-194 成功安装服务\n2021-11-02 22:12:12 启动脚本执行成功，脚本输出如下:\nredis  [running]\n2021-11-02 22:12:10 redis-7-194 开始初始化服务\n2021-11-02 22:12:10 redis-7-194 无需执行初始化\n2021-11-02 22:12:10 redis-7-194 开始启动服务\n2021-11-02 22:12:13 redis-7-194 成功启动服务\n2021-11-02 22:12:05 redis-7-194 开始发送服务包\n2021-11-02 22:12:06 redis-7-194 成功发送服务包\n2021-11-02 22:12:07 redis-7-194 开始解压服务包\n2021-11-02 22:12:07 redis-7-194 成功解压服务包\n2021-11-02 22:12:08 redis-7-194 开始安装服务\n2021-11-02 22:12:09 安装脚本执行成功，脚本输出如下:\n开始检查目录\n开始创建用户,修改目录权限\n开始更新文件占位符\n开始声明环境变量\n2021-11-02 22:12:09 redis-7-194 成功安装服务\n2021-11-02 22:12:12 启动脚本执行成功，脚本输出如下:\nredis  [running]\n2021-11-02 22:12:10 redis-7-194 开始初始化服务\n2021-11-02 22:12:10 redis-7-194 无需执行初始化\n2021-11-02 22:12:10 redis-7-194 开始启动服务\n2021-11-02 22:12:13 redis-7-194 成功启动服务\n
          // 2021-11-02 22:12:05 redis-7-194 开始发送服务包\n2021-11-02 22:12:06 redis-7-194 成功发送服务包\n2021-11-02 22:12:07 redis-7-194 开始解压服务包\n2021-11-02 22:12:07 redis-7-194 成功解压服务包\n2021-11-02 22:12:08 redis-7-194 开始安装服务\n2021-11-02 22:12:09 安装脚本执行成功，脚本输出如下:\n开始检查目录\n开始创建用户,修改目录权限\n开始更新文件占位符\n开始声明环境变量\n2021-11-02 22:12:09 redis-7-194 成功安装服务\n2021-11-02 22:12:12 启动脚本执行成功，脚本输出如下:\nredis  [running]\n2021-11-02 22:12:10 redis-7-194 开始初始化服务\n2021-11-02 22:12:10 redis-7-194 无需执行初始化\n2021-11-02 22:12:10 redis-7-194 开始启动服务\n2021-11-02 22:12:13 redis-7-194 成功启动服务\n`);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        //setLoading(false);
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
              {Object.keys(data.detail).map((key,idx) => {
                return (
                  <InstallInfoItem
                    openName={openName}
                    setOpenName={(n) => {
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
        <div style={{ paddingLeft: 20 }}>
          {renderStatus[data.status]}
          <LoadingOutlined style={{ marginLeft: 10, fontWeight: 600 }} />
        </div>
        <div>
          <Button
            style={{ marginLeft: 10 }}
            type="primary"
            //disabled={unassignedServices !== 0}
            onClick={() => {
              history?.push("/application-management/installation-record");
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
