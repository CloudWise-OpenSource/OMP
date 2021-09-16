import styles from "./index.module.less";
import { Layout } from "antd";

function OmpContentWrapper({ children, wrapperStyle }) {
  return (
    <div style={wrapperStyle} className={styles.contentWrapper}>
      {children}
      <Layout.Footer
        style={{
          color: "#acb5ba",
          backgroundColor: "rgba(0,0,0,0)",
          textAlign: "center",
          height: 40,
          padding: 0,
          paddingTop: 15,
        }}
      >
        Copyright © 2020-2021 Cloudwise.All Rights Reserved{" "}
      </Layout.Footer>
    </div>
  );
}

export default OmpContentWrapper;
