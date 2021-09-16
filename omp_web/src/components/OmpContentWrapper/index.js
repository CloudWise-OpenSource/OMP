import styles from "./index.module.less";

function OmpContentWrapper({ children,wrapperStyle}) {
  return <div style={wrapperStyle} className={styles.contentWrapper}>{children}</div>;
}

export default OmpContentWrapper;
