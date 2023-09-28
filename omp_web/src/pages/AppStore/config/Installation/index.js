import { useHistory, useLocation } from "react-router-dom";
import { useDispatch } from "react-redux";
import { Steps } from "antd";
import { useState } from "react";
import styles from "./index.module.less";
import Step1 from "./steps/Step1";
import Step2 from "./steps/Step2";
import Step3 from "./steps/Step3";
import Step4 from "./steps/Step4";

import { LeftOutlined } from "@ant-design/icons";
// 安装页面
const Installation = () => {

  const dispatch = useDispatch();
  const history = useHistory();
  const location = useLocation()

  const defaultStep = location.state?.step
  //console.log(location, defaultStep)

  const [stepNum, setStepNum] = useState(defaultStep || 0);

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
              // dispatch(getTabKeyChangeAction("service"));
              history?.goBack();
              // history?.push({
              //   pathname: `/application_management/app_store`,
              // });
            }}
          />
          安装
        </div>
        <div style={{ width: 600, position: "relative", left: -60 }}>
          <Steps size="small" current={stepNum}>
            <Steps.Step title="基本信息" />
            <Steps.Step title="服务分布" />
            <Steps.Step title="修改配置" />
            <Steps.Step title="开始安装" />
          </Steps>
        </div>
        <div />
      </div>
      {stepNum == 0 && <Step1 setStepNum={setStepNum} />}
      {stepNum == 1 && <Step2 setStepNum={setStepNum} />}
      {stepNum == 2 && <Step3 setStepNum={setStepNum} />}
      {stepNum == 3 && <Step4 />}
    </div>
  );
};

export default Installation;
