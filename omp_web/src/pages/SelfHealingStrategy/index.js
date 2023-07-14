import { OmpContentWrapper, OmpTable, OmpMessageModal } from "@/components";
import { Form, Button, message } from "antd";
import { useState, useEffect, useRef } from "react";
import { handleResponse } from "@/utils/utils";
import { fetchGet, fetchDelete, fetchPost, fetchPut } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import styles from "./index.module.less";
import { ExclamationCircleOutlined } from "@ant-design/icons";
import moment from "moment";
import getColumnsConfig from "./config/columns";
import { AddStrategyModal } from "./StrategyModal";
import { useHistory, useLocation } from "react-router-dom";

const BackupStrategy = () => {
  const location = useLocation();

  const history = useHistory();

  const [loading, setLoading] = useState(false);

  const [dataSource, setDataSource] = useState([]);

  // 自定义参数

  // 增/改自愈策略共用
  const [strategyRow, setStrategyRow] = useState({});
  const [strategyModalType, setStrategyModalType] = useState("add");
  const [strategyModalVisibility, setStrategyModalVisibility] = useState(false);
  const [strategyLoading, setStrategyLoading] = useState(false);
  const [keyArr, setKeyArr] = useState([]);

  // 自愈策略表单
  const [strategyForm] = Form.useForm();

  // 自愈组件全量数据
  const [canHealingIns, setcanHealingIns] = useState([]);

  // 删除策略
  const [deleteStrategyModal, setDeleteStrategyModal] = useState(false);

  // 策略表单初始值
  const strategyFormInit = {
    repair_instance: [],
    fresh_rate: 30,
    max_healing_count: 5,
    instance_tp: 0,
    used: false
  };

  // 策略列表查询
  const fetchData = () => {
    setLoading(true);
    fetchGet(apiRequest.faultSelfHealing.selfHealingStrategy)
      .then((res) => {
        handleResponse(res, (res) => {
          setDataSource(
            res.data.map((item, idx) => {
              return {
                ...item,
                _idx: idx + 1,
              };
            })
          );
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  // 查询可自愈实例
  const queryCanHealing = () => {
    setStrategyLoading(true);
    fetchGet(apiRequest.faultSelfHealing.selfHealingStrategy, {
      params: {
        instance: true,
      },
    })
      .then((res) => {
        handleResponse(res, () => {
          setcanHealingIns(res.data.data);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setStrategyLoading(false);
      });
  };

  // 添加自愈策略
  const addStrategy = (data) => {
    setStrategyLoading(true);
    fetchPost(apiRequest.faultSelfHealing.selfHealingStrategy, {
      body: data,
    })
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.code == 0) {
            message.success("添加自愈策略成功");
            strategyForm.setFieldsValue(strategyFormInit);
            fetchData();
            setKeyArr([]);
            setStrategyModalVisibility(false);
          } else {
            message.warning(res.message);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setStrategyLoading(false);
      });
  };

  // 编辑自愈策略
  const updateStrategy = (data) => {
    setStrategyLoading(true);
    fetchPut(`${apiRequest.faultSelfHealing.selfHealingStrategy}${strategyRow.id}/`, {
      body: data,
    })
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.code == 0) {
            message.success("修改自愈策略成功");
            strategyForm.setFieldsValue(strategyFormInit);
            fetchData();
            setKeyArr([]);
            setStrategyModalVisibility(false);
          } else {
            message.warning(res.message);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setStrategyLoading(false);
      });
  };

  // 删除自愈策略
  const deleteStrategy = () => {
    setLoading(true);
    fetchDelete(`${apiRequest.faultSelfHealing.selfHealingStrategy}${strategyRow.id}/`)
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.code == 0) {
            message.success("删除成功");
            fetchData();
            setDeleteStrategyModal(false);
          } else {
            message.warning(res.message);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <OmpContentWrapper>
      <div style={{ display: "flex" }}>
        <Button
          style={{ marginRight: 10 }}
          type="primary"
          onClick={() => {
            // 暂时写死三个维度，无需查询
            // queryCanHealing();
            setStrategyModalType("add");
            setStrategyModalVisibility(true);
          }}
        >
          添加策略
        </Button>

        <div style={{ display: "flex", marginLeft: "auto" }}>
          <Button style={{ marginLeft: 10 }} onClick={() => fetchData()}>
            刷新
          </Button>
        </div>
      </div>
      <div
        style={{
          border: "1px solid #ebeef2",
          backgroundColor: "white",
          marginTop: 10,
        }}
      >
        <OmpTable
          loading={loading}
          columns={getColumnsConfig(
            setStrategyRow,
            setDeleteStrategyModal,
            setStrategyModalType,
            setStrategyModalVisibility,
            strategyForm,
            queryCanHealing
          )}
          dataSource={dataSource}
          pagination={{
            pageSize: 10,
          }}
          rowKey={(record) => record.id}
          noScroll={true}
        />
      </div>

      <AddStrategyModal
        strategyModalType={strategyModalType}
        addStrategy={addStrategy}
        updateStrategy={updateStrategy}
        loading={strategyLoading}
        modalForm={strategyForm}
        addModalVisibility={strategyModalVisibility}
        setAddModalVisibility={setStrategyModalVisibility}
        canHealingIns={canHealingIns}
        strategyFormInit={strategyFormInit}
        keyArr={keyArr}
        setKeyArr={setKeyArr}
      />

      <OmpMessageModal
        visibleHandle={[deleteStrategyModal, setDeleteStrategyModal]}
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
          deleteStrategy();
        }}
      >
        <div style={{ padding: "20px" }}>
          确定 <span style={{ fontWeight: 500 }}>删除</span> 该策略吗？
        </div>
      </OmpMessageModal>
    </OmpContentWrapper>
  );
};

export default BackupStrategy;
