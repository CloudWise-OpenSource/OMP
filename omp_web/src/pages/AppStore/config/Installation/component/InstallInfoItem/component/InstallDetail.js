import { DownOutlined } from "@ant-design/icons";
import { useEffect, useRef } from "react";

const stepOpen = {
  marginTop: 10,
  minHeight: 30,
  height: 300,
  transition: "all .2s ease-in",
  //overflow: "hidden",
  backgroundColor: "#000",
  color: "#fff",
  padding: 10,
  overflowY: "auto",
  whiteSpace: "pre-line"
};
const stepNotOpen = {
  height: 0,
  minHeight: 0,
  transition: "all .2s ease-in",
  overflow: "hidden",
  backgroundColor: "#f9f9f9",
};

// 状态渲染规则
  const renderStatus = {
    0: <span style={{ color: "#f0c242" }}>等待安装</span>,
    1: <span style={{ color: "rgba(0, 0, 0, 0.85)" }}>正在安装</span>,
    2: <span style={{ color: "rgb(118,204,104)" }}>安装成功</span>,
    3: <span style={{ color: "#da4e48" }}>安装失败</span>,
  };

const InstallDetail = ({ title, ip, status, openName, setOpenName,log }) => {

  const containerRef = useRef(null)

  useEffect(()=>{
    containerRef.current.scrollTop =
    containerRef.current.scrollHeight;
  },[log])

  return (
    <div
      style={{
        padding: 10,
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
        }}
      >
        <div style={{ flex: 2 }}>{ip}</div>
        <div style={{ flex: 1 }}>{renderStatus[status]}</div>
        <div style={{ flex: 6, textAlign: "right", paddingRight: 50 }}>
          <a
            onClick={() => {
              if (openName == `${title}=${ip}`) {
                setOpenName("");
              } else {
                setOpenName(`${title}=${ip}`);
              }
            }}
          >
            查看详细安装信息
            <DownOutlined
              style={{
                transform: `rotate(${
                  openName == `${title}=${ip}` ? 180 : 0
                }deg)`,
                position: "relative",
                top: openName == `${title}=${ip}` ? -1 : 1,
                left: 3,
              }}
            />
          </a>
        </div>
      </div>
      <div ref={containerRef} style={openName == `${title}=${ip}` ? stepOpen : stepNotOpen}>
        {log || "暂无数据"}
      </div>
    </div>
  );
};

export default InstallDetail;
