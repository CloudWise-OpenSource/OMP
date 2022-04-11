import { useSelector } from "react-redux";
import { Button, Tooltip } from "antd";
import styles from "./index.module.less";
import imgObj from "./img";
import { useEffect, useState } from "react";

const Card = ({ idx, history, info, tabKey, installOperation }) => {
  //定义命名
  let nameObj = {
    component: {
      logo: "app_logo",
      name: "app_name",
      version: "app_version",
      description: "app_description",
      instance_number: "instance_number",
      install_url: "/application_management/app_store/component_installation",
    },
    service: {
      logo: "pro_logo",
      name: "pro_name",
      version: "pro_version",
      description: "pro_description",
      instance_number: "instance_number",
      install_url: "/application_management/app_store/application_installation",
    },
  };

  const [isHover, setIsHover] = useState(false);

  return (
    <div
      className={styles.cardContainer}
      style={{
        transition: "all .2s ease-in-out",
        width: "calc(97.7% / 4)",
        marginLeft: (idx - 1) % 4 !== 0 && "0.75%",
        height: 200,
        boxSizing: "border-box",
        //border: "1px solid #000",
        marginTop: 10,
        position: "relative",
        top: 0,
        backgroundColor: "#fff",
        paddingLeft: 10,
        paddingRight: 10,
      }}
      onMouseEnter={() => {
        setIsHover(true);
      }}
      onMouseLeave={() => {
        setIsHover(false);
      }}
    >
      <div className={styles.cardContent}>
        <div style={{ width: 80, paddingTop: 10 }}>
          {info[nameObj[tabKey].logo] ? (
            <div
              style={{
                width: 50,
                height: 50,
                borderRadius: "50%",
                border: "1px solid #a8d0f8",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                marginLeft: 10,
                marginRight: 10,
                overflow: "hidden",
              }}
              dangerouslySetInnerHTML={{
                __html: info[nameObj[tabKey].logo],
              }}
            ></div>
          ) : (
            <div
              style={{
                width: 50,
                height: 50,
                borderRadius: "50%",
                border: "1px solid #a8d0f8",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                marginLeft: 10,
                marginRight: 10,
                overflow: "hidden",
                fontSize: 22,
                backgroundImage: "linear-gradient(to right, #4f85f6, #669aee)",
                // backgroundColor:"#5c8df6",
                color:"#fff",
              }}
            >
              <div
                style={{ textAlign: "center", position: "relative" }}
              >
                {info[nameObj[tabKey].name] && info[nameObj[tabKey].name][0].toLocaleUpperCase()}
              </div>
            </div>
          )}
        </div>
        <div
          style={{
            //flex: 1,
            fontSize: 13,
            color: "#a2a2a2",
            position: "relative",
            width: "calc(100% - 80px)",
          }}
          onClick={() => {
            history?.push({
              pathname: `/application_management/app_store/app-${tabKey}-detail/${
                info[nameObj[tabKey].name]
              }/${info[nameObj[tabKey].version]}`,
            });
          }}
        >
          <div style={{ fontSize: 14, color: isHover ? "#247fe6" : "#222222" }}>
            {info[nameObj[tabKey].name]}
          </div>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              fontSize: 12,
              padding: "8px 10px 10px 0px",
              //fontSize:12
            }}
          >
            <span>最新版本</span>
            <span>{info[nameObj[tabKey].version]}</span>
          </div>
          <p className={styles.text}>
            {/* <Tooltip placement="top" title={info[nameObj[tabKey].description]}> */}
            {info[nameObj[tabKey].description]}
            {/* </Tooltip> */}
          </p>
          <span
            style={{
              float: "right",
              position: "absolute",
              bottom: 8,
              right: 10,
              fontSize: 12,
            }}
          >
            已安装{info[nameObj[tabKey].instance_number]}个实例
          </span>
        </div>
      </div>
      <div
        className={styles.cardBtn}
        style={{ color: isHover ? "#247fe6" : "rgba(0,0,0,0.65)" }}
      >
        <div
          style={{ borderRight: "1px solid #e7e7e7" }}
          onClick={() => {
            history?.push({
              pathname: `/application_management/app_store/app-${tabKey}-detail/${
                info[nameObj[tabKey].name]
              }/${info[nameObj[tabKey].version]}`,
            });
          }}
        >
          查看
        </div>
        <div
          onClick={() => {
            if (tabKey == "service") {
              installOperation({ product_name: info.pro_name }, "服务");
            } else {
              installOperation({ app_name: info.app_name }, "组件");
              // history?.push({
              //   pathname: `${nameObj[tabKey].install_url}/${
              //     info[nameObj[tabKey].name]
              //   }`,
              // });
            }
          }}
        >
          安装
        </div>
      </div>
    </div>
  );
};
export default Card;
