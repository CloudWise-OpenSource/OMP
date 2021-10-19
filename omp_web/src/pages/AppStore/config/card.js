import { useSelector } from "react-redux";
import { Button, Tooltip } from "antd";
import styles from "./index.module.less";
import imgObj from "./img";
import { useEffect, useState } from "react";

const Card = ({ idx, history, info, tabKey }) => {

  //定义命名
  let nameObj = {
    component:{
      logo:"app_logo",
      name:"app_name",
      version:"app_version",
      description:"app_description",
      instance_number:"instance_number",
    },
    service:{
      logo:"pro_logo",
      name:"pro_name",
      version:"pro_version",
      description:"pro_description",
      instance_number:"instance_number",
    }
  }

  return (
    <div
      className={styles.cardContainer}
      style={{
        transition: "all .2s ease-in-out",
        width: "calc(94% / 4)",
        marginLeft: (idx - 1) % 4 !== 0 && "2%",
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
    >
      <div className={styles.cardContent}>
        <div style={{ width: 80, paddingTop: 10 }}>
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
              overflow:"hidden"
            }}
            dangerouslySetInnerHTML={{__html: info[nameObj[tabKey].logo] || imgObj[tabKey]}}
          >
          </div>
        </div>
        <div
          style={{
            //flex: 1,
            fontSize: 13,
            color: "#a2a2a2",
            position: "relative",
            width:"calc(100% - 80px)"
          }}
          onClick={()=>{
            history?.push({
              pathname: `/application_management/app_store/app-${tabKey}-detail/${info[nameObj[tabKey].name]}`,
            });
          }}
        >
          <div style={{ fontSize: 16, color: "#222222" }}>{info[nameObj[tabKey].name]}</div>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span>最新版本</span>
            <span>{info[nameObj[tabKey].version]}</span>
          </div>
          <p
            className={styles.text}
          >
            <Tooltip placement="top" title={info[nameObj[tabKey].description]}>
            {info[nameObj[tabKey].description]}
      </Tooltip>
            
          </p>
          <span
            style={{
              float: "right",
              position: "absolute",
              bottom: 2,
              right: 2,
            }}
          >
            已安装{info[nameObj[tabKey].instance_number]}个实例
          </span>
        </div>
      </div>
      <div className={styles.cardBtn}>
        <div style={{ borderRight: "1px solid #e7e7e7" }}
           onClick={()=>{
            history?.push({
              pathname: `/application_management/app_store/app-${tabKey}-detail/${info[nameObj[tabKey].name]}`,
            });
          }}
        >查看</div>
        <div>安装</div>
      </div>
    </div>
  );
};
export default Card;
