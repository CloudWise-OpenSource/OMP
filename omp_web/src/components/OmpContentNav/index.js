/*
 * @Author: your name
 * @Date: 2021-06-25 15:27:32
 * @LastEditTime: 2021-06-28 11:37:20
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: /omp-fontend123/src/component/ContentNav/index.js
 */
import styles from "./index.module.less";

// 用于面包屑导航组件下部的 切换页面content的导航
const OmpContentNav = ({ data, currentFocus }) => {
  const focusedStyle = {
    color: "#4986f7",
    borderBottom: "2px solid #4986f7",
    //paddingBottom:10
    height: "30px",
    marginRight: 15,
    zIndex: 2,
  };

  return (
    <>
      <div className={styles.warningListHeader}>
        {data.map((item, index) => {
          return (
            <div
              key={index}
              style={
                currentFocus === item.name
                  ? focusedStyle
                  : { height: "30px", marginRight: 15 }
              }
              onClick={() => item.handler()}
            >
              {item.text}
            </div>
          );
        })}
      </div>
      <div style={{ backgroundColor: "#bfbfbf", height: 1, zIndex: 1 }} />
    </>
  );
};
export default OmpContentNav;
