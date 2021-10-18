import { useSelector } from "react-redux";
import { Button } from "antd";
import styles from "./index.module.less";
import img from "@/config/logo/logo.svg";
import { useEffect, useRef, useState } from "react";

const Card = ({ idx }) => {
  const ref = useRef(null);
  //console.log(idx)
  const viewHeight = useSelector((state) => state.layouts.viewSize.height);
  const viewWith = useSelector((state) => state.layouts.viewSize.width);

  console.log(ref?.current?.height);
  console.log((viewHeight - 355 - 10 * 2) / 3);

  const [cardHeight, setCardHeight] = useState(120);

  //   useEffect(() => {
  //       if(viewHeight > 955){
  //         setCardHeight(200)
  //       }else if(viewHeight <= 860 && viewHeight > 760){
  //         setCardHeight(180)
  //       }else if(viewHeight <= 860 && viewHeight > 760){

  //       }
  //   }, []);

  return (
    <div
      ref={ref}
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
            }}
          >
            <img style={{ width: 40, height: 40 }} src={img} />
          </div>
        </div>
        <div
          style={{
            flex: 1,
            fontSize: 13,
            color: "#a2a2a2",
            position: "relative",
          }}
        >
          <div style={{ fontSize: 16, color: "#222222" }}>mysql</div>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span>最新版本</span>
            <span>5.7.31</span>
          </div>
          <p
            className={styles.text}
            style={{
              height: 70,
              overflow: "hidden",
              lineHeight: "18px",
              //   /backgroundColor: "aqua",
            //   display: "-webkit-box",
            //   "box-orient": "vertical",
            //   "line-clamp": 3,   
            }}
          >
            MySQL Database Service is a fully managed database service to deploy
            cloud-native applications
          </p>
          <span
            style={{
              float: "right",
              position: "absolute",
              bottom: 2,
              right: 2,
            }}
          >
            已安装3个实例
          </span>
        </div>
      </div>
      <div className={styles.cardBtn}>
        <div style={{ borderRight: "1px solid #b9b9b9" }}>查看</div>
        <div>安装</div>
      </div>
    </div>
  );
};

export default Card;
