import {
  OmpContentWrapper,
  OmpDatePicker,
  OmpOperationWrapper,
  OmpTable,
  OmpCollapseWrapper,
  OmpButton,
  OmpMessageModal,
  OmpModal,
  OmpIframe,
} from "@/components";
import {
  Button,
  Input,
  Select,
  Badge,
  Form,
  message,
  Menu,
  Dropdown,
  Table,
  Switch,
} from "antd";
import { useState, useEffect, useRef } from "react";
import {
  handleResponse,
  _idxInit,
  refreshTime,
  MessageTip,
  nonEmptyProcessing,
  logout,
  isPassword,
} from "@/utils/utils";
import { fetchGet, fetchDelete, fetchPost, fetchPut } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import styles from "./index.module.less";
import {
  ToolFilled,
  InfoCircleOutlined,
  ExclamationCircleOutlined,
} from "@ant-design/icons";
import { getMaintenanceChangeAction } from "./store/actionsCreators";
import { useSelector, useDispatch } from "react-redux";

const SystemManagement = () => {
  const [loading, setLoading] = useState(false);
  const dispatch = useDispatch();

  function fetchData(
    pageParams = { current: 1, pageSize: 10 },
    searchParams,
    ordering
  ) {
    setLoading(true);
    fetchGet(apiRequest.auth.users, {
      params: {
        page: pageParams.current,
        size: pageParams.pageSize,
        ordering: ordering ? ordering : null,
        ...searchParams,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
        //   /setDataSource(res.data.results);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  }

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <OmpContentWrapper>
      <div className={styles.header}>
        <ToolFilled style={{ paddingRight: 5 }} />
        维护模式
      </div>
      <div className={styles.content}>
        <span className={styles.label}>启用: </span>
        <Switch onChange={(e)=>{
            dispatch(getMaintenanceChangeAction(e))
        }} />
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
    </OmpContentWrapper>
  );
};

export default SystemManagement;
