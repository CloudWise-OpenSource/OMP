import styles from "./index.module.less";
// import { Layout } from "antd";
// import { useLocation } from "react-router-dom";

function OmpContentWrapper({ children, wrapperStyle }) {
  //const location = useLocation();
  //console.log(location.pathname == "/homepage");
  return (
    <div style={wrapperStyle} className={styles.contentWrapper}>
      {children}
    </div>
  );
}

export default OmpContentWrapper;
