import { Input, Button, Pagination } from "antd";
import { useEffect, useState } from "react";
import styles from "./index.module.less";
import { SearchOutlined, DownloadOutlined } from "@ant-design/icons";
import Card from "./config/card.js";
import { useSelector } from "react-redux";

const AppStore = () => {
  const [tabKey, setTabKey] = useState("component");
  const [searchKey, setSearchKey] = useState("all");
  // 视口高度
  const viewHeight = useSelector((state) => state.layouts.viewSize.height);
  console.log(viewHeight);

  return (
    <div>
      <div className={styles.header}>
        <div className={styles.headerTabRow}>
          <div
            className={styles.headerTab}
            onClick={(e) => {
              if (e.target.innerHTML == "应用服务") {
                setTabKey("service");
              } else if (e.target.innerHTML == "基础组件") {
                setTabKey("component");
              }
            }}
          >
            <div
              style={
                tabKey == "component" ? { color: "rgb(46, 124, 238)" } : {}
              }
            >
              基础组件
            </div>
            <div>|</div>
            <div
              style={tabKey == "service" ? { color: "rgb(46, 124, 238)" } : {}}
            >
              应用服务
            </div>
          </div>
          <div className={styles.headerBtn}>
            <Input
              style={{ marginRight: 10 }}
              placeholder="请输入应用名称"
              suffix={<SearchOutlined style={{ color: "#b6b6b6" }} />}
            />
            <Button style={{ marginRight: 10 }} type="primary">
              发布
            </Button>
            <Button type="primary">扫描服务端</Button>
          </div>
        </div>

        <hr className={styles.headerHr} />
        <div className={styles.headerSearch}>
          <div className={styles.headerSearchCondition}>
            <p style={searchKey == "all" ? { color: "rgb(46, 124, 238)" } : {}}>
              全部
            </p>
            <p
              style={searchKey == "data" ? { color: "rgb(46, 124, 238)" } : {}}
            >
              数据库
            </p>
            <p style={searchKey == "msg" ? { color: "rgb(46, 124, 238)" } : {}}>
              消息队列
            </p>
            <p style={searchKey == "web" ? { color: "rgb(46, 124, 238)" } : {}}>
              WEB服务
            </p>
            <p
              style={
                searchKey == "config" ? { color: "rgb(46, 124, 238)" } : {}
              }
            >
              配置中心
            </p>
          </div>
          <div className={styles.headerSearchInfo}>
            <Button
              style={{ marginRight: 15, fontSize: 13 }}
              icon={<DownloadOutlined />}
            >
              <span style={{ color: "#818181" }}>下载组件模版</span>
            </Button>
            共收录21个基础组件
          </div>
        </div>
      </div>
      <div style={{ display: "flex", flexWrap: "wrap" }}>
        <Card key={1} idx={1} />
        <Card key={2} idx={2} />
        <Card key={3} idx={3} />
        <Card key={4} idx={4} />
        <Card key={5} idx={5} />
        <Card key={6} idx={6} />
        {viewHeight > 955 && (
          <>
            <Card key={7} idx={7} />
            <Card key={8} idx={8} />
            <Card key={9} idx={9} />
            <Card key={10} idx={10} />
          </>
        )}
      </div>
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          position: "relative",
          top: 25,
        }}
      >
        <Pagination defaultCurrent={1} total={50} />
      </div>
    </div>
  );
};

export default AppStore;
