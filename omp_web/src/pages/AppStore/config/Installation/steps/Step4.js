import { Button, Anchor } from "antd";
import { useSelector } from "react-redux";
import InstallInfoItem from "../component/InstallInfoItem";
import { useState } from "react";
import { LoadingOutlined } from "@ant-design/icons";

const { Link } = Anchor;
// 状态渲染规则
const renderStatus = {
  0: "待安装",
  1: "安装中",
  2: "安装成功",
  3: "安装失败",
};

const Step4 = () => {
  const viewHeight = useSelector((state) => state.layouts.viewSize.height);
  const [openName, setOpenName] = useState("");

  const data = {
    status: 1,
    detail: {
      mysql: [
        { ip: "10.0.1.1", status: 2 },
        { ip: "10.0.1.2", status: 3 },
        { ip: "10.0.1.9", status: 3 },
      ],
      redis: [
        { ip: "10.0.1.1", status: 2 },
        { ip: "10.0.1.2", status: 0 },
      ],
      zookeeper: [
        { ip: "10.0.1.1", status: 2 },
        { ip: "10.0.1.2", status: 2 },
      ],
      rocketmq: [
        { ip: "10.0.1.1", status: 2 },
        { ip: "10.0.1.2", status: 2 },
      ],
      arangodb: [
        { ip: "10.0.1.1", status: 2 },
        { ip: "10.0.1.2", status: 2 },
      ],
      elasticsearch: [
        { ip: "10.0.1.1", status: 2 },
        { ip: "10.0.1.2", status: 2 },
      ],
      httpd: [
        { ip: "10.0.1.1", status: 2 },
        { ip: "10.0.1.2", status: 2 },
      ],
      ignite: [
        { ip: "10.0.1.1", status: 2 },
        { ip: "10.0.1.2", status: 2 },
      ],
      tengine: [
        { ip: "10.0.1.1", status: 2 },
        { ip: "10.0.1.2", status: 2 },
      ],
    },
  };

  return (
    <div>
      <div
        style={{
          display: "flex",
          paddingTop: 20,
        }}
      >
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
            {Object.keys(data.detail).map((key) => {
              return (
                <InstallInfoItem
                  openName={openName}
                  setOpenName={setOpenName}
                  id={`a${key}`}
                  key={key}
                  title={key}
                  data={data.detail[key]}
                />
              );
            })}
          </div>
        </div>
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
            onClick={() => {}}
          >
            完成
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Step4;
