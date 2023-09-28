import { OmpContentWrapper, OmpTable, OmpMessageModal } from "@/components";
import { Form, Button, message } from "antd";
import { useState, useEffect } from "react";
import { handleResponse } from "@/utils/utils";
import { fetchGet, fetchDelete, fetchPost, fetchPut } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import styles from "./index.module.less";
import { ExclamationCircleOutlined } from "@ant-design/icons";
import moment from "moment";
import getColumnsConfig from "./config/columns";
import { AddCustomModal, CustomModal } from "./CustomModal.js";
import { AddStrategyModal } from "./StrategyModal";
import { useHistory, useLocation } from "react-router-dom";

const BackupStrategy = () => {
  const location = useLocation();

  const history = useHistory();

  const [loading, setLoading] = useState(false);

  const [dataSource, setDataSource] = useState([]);

  // 自定义参数
  const [customModalVisibility, setCustomModalVisibility] = useState(false);
  const [customLoading, setCustomLoading] = useState(false);
  const [customData, setCustomData] = useState(false);
  const [initData, setinitData] = useState([]);

  // 增/改自定义参数共用
  const [customModalType, setCustomModalType] = useState("add");
  const [addModalVisibility, setAddModalVisibility] = useState(false);
  const [addLoading, setAddLoading] = useState(false);

  // 自定义参数表单数据
  const [row, setRow] = useState({});
  const [customModalForm] = Form.useForm();
  const [strategyRow, setStrategyRow] = useState({});
  const [updateCustomVisibility, setUpdateCustomVisibility] = useState(false);
  const [updateCustomData, setUpdateCustomData] = useState({});
  const [updateRepeatName, setUpdateRepeatName] = useState("");
  const [deleteCustomVisibility, setDeleteCustomVisibility] = useState(false);
  const [deleteRepeatName, setDeleteRepeatName] = useState("");

  // 增/改备份策略共用
  const [strategyModalType, setStrategyModalType] = useState("add");
  const [strategyModalVisibility, setStrategyModalVisibility] = useState(false);
  const [strategyLoading, setStrategyLoading] = useState(false);
  const [keyArr, setKeyArr] = useState([]);

  // 备份策略表单
  const [strategyForm] = Form.useForm();

  // 备份组件全量数据
  const [canBackupIns, setCanBackupIns] = useState([]);

  // 删除策略
  const [deleteStrategyModal, setDeleteStrategyModal] = useState(false);
  // 执行策略
  const [executeVisible, setExecuteVisible] = useState(false);
  const [frequency, setFrequency] = useState("day");

  // 星期汉字映射
  let weekData = [
    "星期一",
    "星期二",
    "星期三",
    "星期四",
    "星期五",
    "星期六",
    "星期日",
  ];

  // 策略表单初始值
  const strategyFormInit = {
    retain_path: "/data/omp/data/backup/",
    retain_day: 7,
    is_on: false,
    strategy: {
      frequency: "day",
      time: moment("00:00", "HH:mm"),
      week: "0",
      month: "1",
    },
    backup_instances: [],
    backup_custom: [],
  };

  // 数据备份策略列表查询
  const fetchData = () => {
    setLoading(true);
    fetchGet(apiRequest.dataBackup.strategySetting)
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

  // 自定义参数查询
  const queryCustom = () => {
    setCustomLoading(true);
    fetchGet(apiRequest.dataBackup.backupCustom)
      .then((res) => {
        handleResponse(res, (res) => {
          const resData = res.data.map((item, idx) => {
            return {
              ...item,
              _idx: idx + 1,
            };
          });
          setCustomData(resData);
          setinitData(resData);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setCustomLoading(false);
      });
  };

  // 添加自定义参数
  const addCustom = (data) => {
    setAddLoading(true);
    fetchPost(apiRequest.dataBackup.backupCustom, {
      body: data,
    })
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.code == 0) {
            message.success("添加自定义参数成功");
            customModalForm.setFieldsValue({
              field_k: "",
              field_v: "",
              notes: "",
            });
            queryCustom();
            setAddModalVisibility(false);
          } else {
            message.warning(res.message);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setAddLoading(false);
      });
  };

  // 修改自定义参数 - 提示存在实例使用
  const updateCustomInfo = (data) => {
    setAddLoading(true);
    fetchGet(apiRequest.dataBackup.backupRepeatCustom, {
      params: {
        id: row.id,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          const repeatName = res.data[0].name;
          if (repeatName) {
            setUpdateRepeatName(repeatName);
            setUpdateCustomData(data);
            setUpdateCustomVisibility(true);
          } else {
            updateCustom(data);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setAddLoading(false);
      });
  };

  // 修改自定义参数
  const updateCustom = (data) => {
    setAddLoading(true);
    fetchPut(`${apiRequest.dataBackup.backupCustom}${row.id}/`, {
      body: data,
    })
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.code == 0) {
            message.success("修改自定义参数成功");
            customModalForm.setFieldsValue({
              field_k: "",
              field_v: "",
              notes: "",
            });
            queryCustom();
            fetchData();
            setUpdateCustomVisibility(false);
            setAddModalVisibility(false);
          } else {
            message.warning(res.message);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setAddLoading(false);
      });
  };

  // 删除自定义参数
  const deleteCustomInfo = (id) => {
    setAddLoading(true);
    fetchGet(apiRequest.dataBackup.backupRepeatCustom, {
      params: {
        id: id,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          const repeatName = res.data[0].name;
          setDeleteRepeatName(repeatName);
          setDeleteCustomVisibility(true);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setAddLoading(false);
      });
  };

  // 删除自定义参数
  const deleteCustom = () => {
    setAddLoading(true);
    fetchDelete(`${apiRequest.dataBackup.backupCustom}${row.id}/`)
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.code == 0) {
            message.success("删除成功");
            queryCustom();
            fetchData();
            setDeleteCustomVisibility(false);
          } else {
            message.warning(res.message);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setAddLoading(false);
      });
  };

  // 查询可备份实例
  const queryCanBackup = () => {
    setStrategyLoading(true);
    fetchGet(apiRequest.dataBackup.queryCanBackup)
      .then((res) => {
        handleResponse(res, () => {
          setCanBackupIns(res.data.data);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setStrategyLoading(false);
      });
  };

  // 构建添加/修改备份策略的请求体
  const makeRequestBody = (data) => {
    const timeInfo = data.strategy.time.format("HH:mm");
    return {
      backup_instances: data.backup_instances,
      retain_path: data.retain_path,
      retain_day: data.retain_day,
      is_on: data.is_on,
      backup_custom:
        data.backup_custom?.map((e) => {
          return {
            id: e.key,
            field_k: e.label[0].props.children[1],
            field_v: e.label[1],
          };
        }) || [],
      crontab_detail: {
        month_of_year: "*",
        day_of_month: data.strategy.month || "*",
        day_of_week: data.strategy.week || "*",
        hour: timeInfo.split(":")[0] || "*",
        minute: timeInfo.split(":")[1] || "*",
      },
    };
  };

  // 添加备份策略
  const addStrategy = (data) => {
    setStrategyLoading(true);
    fetchPost(apiRequest.dataBackup.strategySetting, {
      body: makeRequestBody(data),
    })
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.code == 0) {
            message.success("添加备份策略成功");
            strategyForm.setFieldsValue(strategyFormInit);
            fetchData();
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

  // 编辑备份策略
  const updateStrategy = (data) => {
    setStrategyLoading(true);
    fetchPut(`${apiRequest.dataBackup.strategySetting}${strategyRow.id}/`, {
      body: makeRequestBody(data),
    })
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.code == 0) {
            message.success("修改备份策略成功");
            strategyForm.setFieldsValue(strategyFormInit);
            fetchData();
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

  // 删除备份策略
  const deleteStrategy = () => {
    setLoading(true);
    fetchDelete(`${apiRequest.dataBackup.strategySetting}${strategyRow.id}/`)
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

  // 执行备份策略
  const executeStrategy = () => {
    setLoading(true);
    fetchPost(apiRequest.dataBackup.strategySetting, {
      body: {
        id: strategyRow.id,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.code == 0) {
            message.success("任务下发成功");
            setExecuteVisible(false);
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
    queryCanBackup();
  }, []);

  return (
    <OmpContentWrapper>
      <div style={{ display: "flex" }}>
        <Button
          style={{ marginRight: 10 }}
          type="primary"
          onClick={() => {
            queryCustom();
            setStrategyModalType("add");
            setStrategyModalVisibility(true);
          }}
        >
          添加策略
        </Button>
        <Button
          style={{ marginRight: 10 }}
          type="primary"
          onClick={() => {
            setCustomModalVisibility(true);
            queryCustom();
          }}
        >
          自定义参数
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
            setExecuteVisible,
            strategyForm,
            queryCustom,
            setKeyArr,
            weekData,
            setFrequency
          )}
          dataSource={dataSource}
          pagination={{
            pageSize: 10,
          }}
          rowKey={(record) => record.id}
          noScroll={true}
        />
      </div>

      <CustomModal
        modalVisibility={customModalVisibility}
        setModalVisibility={setCustomModalVisibility}
        modalLoading={customLoading}
        customData={customData}
        setCustomData={setCustomData}
        initData={initData}
        setCustomModalType={setCustomModalType}
        setAddModalVisibility={setAddModalVisibility}
        deleteCustomInfo={deleteCustomInfo}
        modalForm={customModalForm}
        setRow={setRow}
      />
      <AddCustomModal
        customModalType={customModalType}
        addCustom={addCustom}
        loading={addLoading}
        modalForm={customModalForm}
        addModalVisibility={addModalVisibility}
        setAddModalVisibility={setAddModalVisibility}
        updateCustomInfo={updateCustomInfo}
        setUpdateCustomData={setUpdateCustomData}
      />
      <AddStrategyModal
        strategyModalType={strategyModalType}
        addStrategy={addStrategy}
        updateStrategy={updateStrategy}
        loading={strategyLoading}
        modalForm={strategyForm}
        addModalVisibility={strategyModalVisibility}
        setAddModalVisibility={setStrategyModalVisibility}
        canBackupIns={canBackupIns}
        initData={initData}
        strategyFormInit={strategyFormInit}
        keyArr={keyArr}
        setKeyArr={setKeyArr}
        weekData={weekData}
        frequency={frequency}
        setFrequency={setFrequency}
      />

      <OmpMessageModal
        visibleHandle={[updateCustomVisibility, setUpdateCustomVisibility]}
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
        loading={addLoading}
        onFinish={() => {
          updateCustom(updateCustomData);
        }}
        zIndex={1004}
      >
        <div style={{ padding: "20px" }}>
          该参数{" "}
          <span style={{ fontWeight: 500, color: "red" }}>
            {updateRepeatName}
          </span>{" "}
          实例正在使用
          <br />
          确认<span style={{ fontWeight: 500 }}>修改</span>该参数吗？
        </div>
      </OmpMessageModal>

      <OmpMessageModal
        visibleHandle={[deleteCustomVisibility, setDeleteCustomVisibility]}
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
        loading={addLoading}
        onFinish={() => deleteCustom()}
        zIndex={1004}
      >
        <div style={{ padding: "20px" }}>
          {deleteRepeatName && (
            <>
              该参数{" "}
              <span style={{ fontWeight: 500, color: "red" }}>
                {deleteRepeatName}
              </span>{" "}
              实例正在使用
              <br />
            </>
          )}
          确认<span style={{ fontWeight: 500 }}>删除</span>该参数吗？
        </div>
      </OmpMessageModal>

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

      <OmpMessageModal
        visibleHandle={[executeVisible, setExecuteVisible]}
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
          executeStrategy();
        }}
      >
        <div style={{ padding: "20px" }}>
          确认对实例{" "}
          <span style={{ fontWeight: 500, color: "red" }}>
            {strategyRow.backup_instances?.join(",")}
          </span>{" "}
          执行备份策略吗？
        </div>
      </OmpMessageModal>
    </OmpContentWrapper>
  );
};

export default BackupStrategy;
