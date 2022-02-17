import {
  OmpContentWrapper,
  OmpTable,
  OmpMessageModal,
  OmpSelect,
  OmpDatePicker,
  OmpDrawer,
} from "@/components";
import { Button, Collapse } from "antd";
import styles from "./index.module.less";
const { Panel } = Collapse;
const ToolExecutionResults = () => {
  return (
    <OmpContentWrapper  wrapperStyle={{ padding: 0, paddingBottom: 30, backgroundColor: "#fff" }}>
     <div className={styles.resultTitle}>
        kafka生产者&消费者 <span className={styles.resultTitleStatus}>执行中</span>
     </div>
     <Panel header="概述信息" key="overview" className={"panelItem"}>
            <div className={"overviewItemWrapper"}>
             
            </div>
          </Panel>
     {/* </div> */}
    </OmpContentWrapper>
  );
};

export default ToolExecutionResults;
