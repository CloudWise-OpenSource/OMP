import {
  OmpContentWrapper,
  OmpMessageModal,
} from "@/components";
import {
  message,
  Switch,
} from "antd";
import { useState } from "react";
import {
  handleResponse,
  _idxInit,
} from "@/utils/utils";
import { fetchPost } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import styles from "./index.module.less";
import {
  ToolFilled,
  ExclamationCircleOutlined,
} from "@ant-design/icons";
import { getMaintenanceChangeAction } from "./store/actionsCreators";
import { useSelector, useDispatch } from "react-redux";

const SystemManagement = () => {
  const [loading, setLoading] = useState(false);
  const dispatch = useDispatch();

  //是否展示维护模式提示词
  const isMaintenance = useSelector(
    (state) => state.systemManagement.isMaintenance
  );

  const [closeMaintenanceModal, setCloseMaintenanceModal] = useState(false);

  const [openMaintenanceModal, setOpenMaintenanceModal] = useState(false);

    // 更改维护模式
    const changeMaintain = (e)=>{
        setLoading(true);
        fetchPost(apiRequest.environment.queryMaintainState, {
          body: {
            matcher_name:"env",
            matcher_value:"default"
          },
        })
          .then((res) => {
            handleResponse(res, (res) => {
              if(res.code == 0){
                if (e) {   
                    message.success("已进入全局维护模式")
                    dispatch(getMaintenanceChangeAction(true));
                  } else {
                    message.success("已退出全局维护模式")
                    dispatch(getMaintenanceChangeAction(false));
                  }
              }
              if(res.code == 1){
                message.warning(res.message)
              }
            });
          })
          .catch((e) => console.log(e))
          .finally(() => {
            setLoading(false);
            setOpenMaintenanceModal(false);
            setCloseMaintenanceModal(false);
          });
    }

  return (
    <OmpContentWrapper>
      <div className={styles.header}>
        <ToolFilled style={{ paddingRight: 5 }} />
        维护模式
      </div>
      <div className={styles.content}>
        <span className={styles.label}>启用: </span>
        <Switch
          checked={isMaintenance}
          onChange={(e) => {
            if (e) {
              setOpenMaintenanceModal(true);
            } else {
              setCloseMaintenanceModal(true);
            }
          }}
        />
      </div>
      <p className={styles.tips}>
        <ExclamationCircleOutlined
          style={{
            position: "relative",
            top: 1,
            paddingRight: 10,
            fontSize: 18,
          }}
        />
        开启维护模式后，将暂停平台异常告警功能；此功能适用于计划性升级、变更操作期间，避免造成误报带来的影响。
      </p>

      <OmpMessageModal
        visibleHandle={[openMaintenanceModal, setOpenMaintenanceModal]}
        title={
          <span>
            <ExclamationCircleOutlined
              style={{
                fontSize: 20,
                color: "#f0a441",
                paddingRight: "10px",
                position: "relative",
                top: 2,
              }}
            />
            提示
          </span>
        }
        loading={loading}
        onFinish={() => {
            changeMaintain(true)
        }}
      >
        <div style={{ padding: "20px" }}>确定进入全局维护模式 ？</div>
      </OmpMessageModal>

      <OmpMessageModal
        visibleHandle={[closeMaintenanceModal, setCloseMaintenanceModal]}
        title={
          <span>
            <ExclamationCircleOutlined
              style={{
                fontSize: 20,
                color: "#f0a441",
                paddingRight: "10px",
                position: "relative",
                top: 2,
              }}
            />
            提示
          </span>
        }
        loading={loading}
        onFinish={() => {
            changeMaintain(false)
        }}
      >
        <div style={{ padding: "20px" }}>确定退出全局维护模式 ？</div>
      </OmpMessageModal>
    </OmpContentWrapper>
  );
};

export default SystemManagement;
