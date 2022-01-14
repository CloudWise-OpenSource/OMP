// 服务的升级和回滚
import { useHistory, useLocation } from "react-router-dom";
// import { getTabKeyChangeAction } from "../../store/actionsCreators";
import { useDispatch } from "react-redux";
import { Steps } from "antd";
import { useState } from "react";
import styles from "./index.module.less";

import { LeftOutlined } from "@ant-design/icons";
import Content from "./content/index.js"
// 安装页面
const Rollback = () => {
  // const dispatch = useDispatch();
  const history = useHistory();

  return (
    <div>
      <div
        style={{
          height: 50,
          backgroundColor: "#fff",
          display: "flex",
          paddingLeft: 20,
          paddingRight: 50,
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div style={{ fontSize: 16 }}>
          <LeftOutlined
            style={{ fontSize: 16, marginRight: 20 }}
            className={styles.backIcon}
            onClick={() => {
              history?.goBack();
            }}
          />
          服务回滚
        </div>
        <div />
      </div>
      <Content />
    </div>
  );
};

export default Rollback;
