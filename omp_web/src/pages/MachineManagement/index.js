import { OmpContentWrapper, OmpTable, OmpMessageModal } from "@/components";
import { Button, Select, message, Menu, Dropdown, Modal } from "antd";
import { useState, useEffect, useRef } from "react";
import { handleResponse, _idxInit, refreshTime } from "@/utils/utils";
import { fetchGet, fetchPost, fetchPatch } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
//import updata from "@/store_global/globalStore";
import {
  AddMachineModal,
  UpDateMachineModal,
  BatchImportMachineModal,
} from "./config/modals";
import { useDispatch } from "react-redux";
import getColumnsConfig, { DetailHost } from "./config/columns";
import {
  DownOutlined,
  ExclamationCircleOutlined,
  ImportOutlined,
} from "@ant-design/icons";

const MachineManagement = () => {
  const dispatch = useDispatch();

  //console.log(location.state, "location.state");

  const [loading, setLoading] = useState(false);

  const [searchLoading, setSearchLoading] = useState(false);

  //添加弹框的控制state
  const [addModalVisible, setAddMoadlVisible] = useState(false);
  //修改弹框的控制state
  const [updateMoadlVisible, setUpdateMoadlVisible] = useState(false);

  // 批量导入弹框
  const [batchImport, setBatchImport] = useState(false);

  //选中的数据
  const [checkedList, setCheckedList] = useState({});

  //table表格数据
  const [dataSource, setDataSource] = useState([]);
  const [ipListSource, setIpListSource] = useState([]);
  const [searchValue, setSearchValue] = useState("");
  const [selectValue, setSelectValue] = useState();

  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    ordering: "",
    searchParams: {},
  });

  const [isShowIframe, setIsShowIsframe] = useState({
    isOpen: false,
    src: "",
    record: {},
  });

  const [msgShow, setMsgShow] = useState(false);

  const msgRef = useRef(null);

  //select 的onblur函数拿不到最新的search value,使用useref存(是最新的，但是因为失去焦点时会自动触发清空search，还是得使用ref存)
  const searchValueRef = useRef(null);

  // 定义row存数据
  const [row, setRow] = useState({});

  // 主机详情历史数据
  const [historyData, setHistoryData] = useState([]);

  // 主机详情loading
  const [historyLoading, setHistoryLoading] = useState([]);

  // 重启主机agent
  const [restartHostAgentModal, setRestartHostAgentModal] = useState(false);

  // 重启监控agent
  const [restartMonterAgentModal, setRestartMonterAgentModal] = useState(false);

  // 开启维护
  const [openMaintainModal, setOpenMaintainModal] = useState(false);
  // 关闭维护
  const [closeMaintainModal, setCloseMaintainModal] = useState(false);

  // 开启维护（单次）
  const [openMaintainOneModal, setOpenMaintainOneModal] = useState(false);
  // 关闭维护（单次）
  const [closeMaintainOneModal, setCloseMaintainOneModal] = useState(false);

  function fetchData(
    pageParams = { current: 1, pageSize: 10 },
    searchParams,
    ordering
  ) {
    setLoading(true);
    fetchGet(apiRequest.machineManagement.hosts, {
      params: {
        page: pageParams.current,
        size: pageParams.pageSize,
        ordering: ordering ? ordering : null,
        ...searchParams,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          setDataSource(res.data.results);
          setPagination({
            ...pagination,
            total: res.data.count,
            pageSize: pageParams.pageSize,
            current: pageParams.current,
            ordering: ordering,
            searchParams: searchParams,
          });
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
        fetchIPlist();
      });
  }

  const fetchIPlist = () => {
    setSearchLoading(true);
    fetchGet(apiRequest.machineManagement.ipList)
      .then((res) => {
        handleResponse(res, (res) => {
          setIpListSource(res.data);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setSearchLoading(false);
      });
  };

  const createHost = (data) => {
    // console.log(data)
    //return
    setLoading(true);
    data.ip = data.IPtext;
    delete data.IPtext;
    data.port = `${data.port}`;
    fetchPost(apiRequest.machineManagement.hosts, {
      body: {
        ...data,
      },
    })
      .then((res) => {
        if (res && res.data) {
          if (res.data.code == 1) {
            // msgRef.current = res.data.message
            // setMsgShow(true)
            message.warning(res.data.message);
          }
          if (res.data.code == 0) {
            message.success("添加主机成功");
            fetchData(
              { current: pagination.current, pageSize: pagination.pageSize },
              { ip: selectValue },
              pagination.ordering
            );
            setAddMoadlVisible(false);
          }
        }
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  const upDateHost = (data) => {
    setLoading(true);
    data.ip = data.IPtext;
    delete data.IPtext;
    data.port = `${data.port}`;
    fetchPatch(`${apiRequest.machineManagement.hosts}${row.id}/`, {
      body: {
        ...data,
      },
    })
      .then((res) => {
        if (res && res.data) {
          if (res.data.code == 1) {
            // msgRef.current = res.data.message
            // setMsgShow(true)
            message.warning(res.data.message);
          }
          if (res.data.code == 0) {
            message.success("更新主机信息成功");
            fetchData(
              { current: pagination.current, pageSize: pagination.pageSize },
              { ip: selectValue },
              pagination.ordering
            );
            setUpdateMoadlVisible(false);
          }
        }
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  const fetchHistoryData = (id) => {
    setHistoryLoading(true);
    fetchGet(apiRequest.machineManagement.operateLog, {
      params: {
        host_id: id,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          setHistoryData(res.data);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setHistoryLoading(false);
      });
  };

  // 重启监控agent
  const fetchRestartMonitorAgent = ()=>{
    setLoading(true);
    fetchPost(apiRequest.machineManagement.restartMonitorAgent, {
      body: {
        host_ids: Object.keys(checkedList)
          .map((k) => checkedList[k])
          .flat(1)
          .map((item) => item.id),
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          console.log(res);
          if (res.code == 0) {
            message.success("重启监控Agent任务已下发");
          }
          if (res.code == 1) {
            message.warning(res.message);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
        setRestartMonterAgentModal(false);
        setCheckedList({});
        fetchData(
          { current: pagination.current, pageSize: pagination.pageSize },
          { ip: selectValue },
          pagination.ordering
        );
      });
  }

  // 重启主机agent
  const fetchRestartHostAgent = () => {
    setLoading(true);
    fetchPost(apiRequest.machineManagement.restartHostAgent, {
      body: {
        host_ids: Object.keys(checkedList)
          .map((k) => checkedList[k])
          .flat(1)
          .map((item) => item.id),
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          console.log(res);
          if (res.code == 0) {
            message.success("重启主机Agent任务已下发");
          }
          if (res.code == 1) {
            message.warning(res.message);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
        setRestartHostAgentModal(false);
        setCheckedList({});
        fetchData(
          { current: pagination.current, pageSize: pagination.pageSize },
          { ip: selectValue },
          pagination.ordering
        );
      });
  };

  // 主机进入｜退出维护模式
  const fetchMaintainChange = (e, checkedList) => {
    let host_arr = [];
    if (e) {
      host_arr = Object.keys(checkedList)
        .map((k) => checkedList[k])
        .flat(1)
        .filter((item) => {
          return !item.is_maintenance;
        });
    } else {
      host_arr = Object.keys(checkedList)
        .map((k) => checkedList[k])
        .flat(1)
        .filter((item) => {
          return item.is_maintenance;
        });
    }
    if (host_arr.length == 0) {
      setLoading(false);
      setOpenMaintainOneModal(false);
      setCloseMaintainOneModal(false);
      setOpenMaintainModal(false);
      setCloseMaintainModal(false);
      setCheckedList({});
      if (e) {
        message.success("主机开启维护模式成功");
      } else {
        message.success("主机关闭维护模式成功");
      }
      return;
    }
    setLoading(true);
    fetchPost(apiRequest.machineManagement.hostsMaintain, {
      body: {
        is_maintenance: e,
        host_ids: host_arr.map((item) => item.id),
      },
    })
      .then((res) => {
        //handleResponse(res, (res) => {
        console.log(res);
        if (res.data.code == 0) {
          if (e) {
            message.success("主机开启维护模式成功");
          } else {
            message.success("主机关闭维护模式成功");
          }
        }
        if (res.data.code == 1) {
          message.warning(res.data.message);
        }
        // });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
        setOpenMaintainOneModal(false);
        setCloseMaintainOneModal(false);
        setOpenMaintainModal(false);
        setCloseMaintainModal(false);
        setCheckedList({});
        fetchData(
          { current: pagination.current, pageSize: pagination.pageSize },
          { ip: selectValue },
          pagination.ordering
        );
      });
  };

  useEffect(() => {
    fetchData(pagination);
  }, []);

  //console.log(checkedList)

  return (
    <OmpContentWrapper>
      <div style={{ display: "flex" }}>
        <Button
          type="primary"
          onClick={() => {
            setAddMoadlVisible(true);
          }}
        >
          添加
        </Button>

        <Button
          type="primary"
          style={{ marginLeft: 10 }}
          onClick={() => {
            setBatchImport(true);
          }}
        >
          导入
        </Button>

        <Dropdown
          //placement="bottomLeft"
          overlay={
            <Menu>
              <Menu.Item
                key="openMaintain"
                style={{ textAlign: "center" }}
                onClick={() => setOpenMaintainModal(true)}
                disabled={Object.keys(checkedList).length == 0}
              >
                开启维护模式
              </Menu.Item>
              <Menu.Item
                key="closeMaintain"
                style={{ textAlign: "center" }}
                disabled={Object.keys(checkedList).length == 0}
                onClick={() => {
                  //setAddMoadlVisible(true);
                  //setAddMachineForm({});
                  setCloseMaintainModal(true);
                }}
              >
                关闭维护模式
              </Menu.Item>
              <Menu.Item
                key="reStartHost"
                style={{ textAlign: "center" }}
                disabled={Object.keys(checkedList).length == 0}
                onClick={() => {
                  //setAddMoadlVisible(true);
                  //setAddMachineForm({});
                  setRestartHostAgentModal(true);
                }}
              >
                重启主机Agent
              </Menu.Item>
              <Menu.Item
                key="reStartMonitor"
                style={{ textAlign: "center" }}
                disabled={Object.keys(checkedList).length == 0}
                onClick={() => {
                  //setAddMoadlVisible(true);
                  //setAddMachineForm({});
                  setRestartMonterAgentModal(true);
                }}
              >
                重启监控Agent
              </Menu.Item>
            </Menu>
          }
          placement="bottomCenter"
        >
          <Button style={{ marginLeft: 10 }}>
            更多
            <DownOutlined />
          </Button>
        </Dropdown>

        <div style={{ display: "flex", marginLeft: "auto" }}>
          <span style={{ width: 60, display: "flex", alignItems: "center" }}>
            IP地址:
          </span>
          <Select
            allowClear
            onClear={() => {
              searchValueRef.current = "";
              setSelectValue();
              setSearchValue();
              fetchData(
                { current: pagination.current, pageSize: pagination.pageSize },
                {},
                pagination.ordering
              );
            }}
            showSearch
            placeholder="搜索"
            loading={searchLoading}
            style={{ width: 200 }}
            onInputKeyDown={(e) => {
              if (e.code == "Enter") {
                //console.log("点击了",searchValueRef.current )
                setSelectValue(searchValueRef.current);
                fetchData(
                  { current: 1, pageSize: 10 },
                  { ip: searchValueRef.current },
                  pagination.ordering
                );
              }
            }}
            searchValue={searchValue}
            onSelect={(e) => {
              if (e == searchValue || !searchValue) {
                //console.log(1)
                setSelectValue(e);
                fetchData(
                  {
                    current: pagination.current,
                    pageSize: pagination.pageSize,
                  },
                  { ip: e },
                  pagination.ordering
                );
              } else {
                //console.log(2)
                setSelectValue(searchValue);
                fetchData(
                  {
                    current: pagination.current,
                    pageSize: pagination.pageSize,
                  },
                  { ip: searchValueRef.current },
                  pagination.ordering
                );
              }
              searchValueRef.current = "";
            }}
            value={selectValue}
            onSearch={(e) => {
              e && (searchValueRef.current = e);
              setSearchValue(e);
            }}
            onBlur={(e) => {
              //console.log(searchValueRef.current,"searchValueRef.current")
              if (searchValueRef.current) {
                setSelectValue(searchValueRef.current);
                fetchData(
                  {
                    current: pagination.current,
                    pageSize: pagination.pageSize,
                  },
                  { ip: searchValueRef.current },
                  pagination.ordering
                );
              }
            }}
          >
            {ipListSource.map((item) => {
              return (
                <Select.Option value={item} key={item}>
                  {item}
                </Select.Option>
              );
            })}
          </Select>
          <Button
            style={{ marginLeft: 10 }}
            onClick={() => {
              dispatch(refreshTime());
              console.log(pagination, "hosts/hosts/?page=1&size=10");
              fetchData(
                { current: pagination.current, pageSize: pagination.pageSize },
                { ip: selectValue },
                pagination.ordering
              );
            }}
          >
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
          //showSorterTooltip
          scroll={{x:1400}}
          // scroll={{ x: 1400 }}
          onChange={(e, filters, sorter) => {
            let ordering = sorter.order
              ? `${sorter.order == "descend" ? "" : "-"}${sorter.columnKey}`
              : null;
            setTimeout(() => {
              fetchData(e, pagination.searchParams, ordering);
            }, 200);
          }}
          columns={getColumnsConfig(
            setIsShowIsframe,
            setRow,
            setUpdateMoadlVisible,
            fetchHistoryData,
            setCloseMaintainOneModal,
            setOpenMaintainOneModal
          )}
          dataSource={dataSource}
          pagination={{
            showSizeChanger: true,
            pageSizeOptions: ["10", "20", "50", "100"],
            showTotal: () => (
              <div
                style={{
                  display: "flex",
                  width: "200px",
                  justifyContent: "space-between",
                  lineHeight: 2.8,
                }}
              >
                <p>
                  已选中{" "}
                  {
                    Object.keys(checkedList)
                      .map((k) => checkedList[k])
                      .flat(1).length
                  }{" "}
                  条
                </p>
                <p style={{ color: "rgb(152, 157, 171)" }}>
                  共计{" "}
                  <span style={{ color: "rgb(63, 64, 70)" }}>
                    {pagination.total}
                  </span>{" "}
                  条
                </p>
              </div>
            ),
            ...pagination,
          }}
          rowKey={(record) => record.id}
          checkedState={[checkedList, setCheckedList]}
        />
      </div>
      {addModalVisible && (
        <AddMachineModal
          setLoading={setLoading}
          loading={loading}
          visibleHandle={[addModalVisible, setAddMoadlVisible]}
          createHost={createHost}
          msgInfo={{
            msgShow: msgShow,
            setMsgShow: setMsgShow,
            msg: msgRef.current,
          }}
        />
      )}
      {updateMoadlVisible && (
        <UpDateMachineModal
          loading={loading}
          setLoading={setLoading}
          visibleHandle={[updateMoadlVisible, setUpdateMoadlVisible]}
          createHost={upDateHost}
          row={row}
          msgInfo={{
            msgShow: msgShow,
            setMsgShow: setMsgShow,
            msg: msgRef.current,
          }}
        />
      )}
      <DetailHost
        isShowIframe={isShowIframe}
        setIsShowIsframe={setIsShowIsframe}
        loading={historyLoading}
        data={historyData}
      />
      {/* 消息，重启主机agent */}
      <OmpMessageModal
        visibleHandle={[restartHostAgentModal, setRestartHostAgentModal]}
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
          fetchRestartHostAgent();
        }}
      >
        <div style={{ padding: "20px" }}>
          确定要重启{" "}
          <span style={{ fontWeight: 500 }}>
            {
              Object.keys(checkedList)
                .map((k) => checkedList[k])
                .flat(1).length
            }
            台
          </span>{" "}
          主机 <span style={{ fontWeight: 500 }}>主机Agent</span> ？
        </div>
      </OmpMessageModal>

      <OmpMessageModal
        visibleHandle={[restartMonterAgentModal, setRestartMonterAgentModal]}
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
          fetchRestartMonitorAgent();
        }}
      >
        <div style={{ padding: "20px" }}>
          确定要重启{" "}
          <span style={{ fontWeight: 500 }}>
            {
              Object.keys(checkedList)
                .map((k) => checkedList[k])
                .flat(1).length
            }
            台
          </span>{" "}
          主机 <span style={{ fontWeight: 500 }}>监控Agent</span> ？
        </div>
      </OmpMessageModal>

      <OmpMessageModal
        visibleHandle={[openMaintainModal, setOpenMaintainModal]}
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
          fetchMaintainChange(true, checkedList);
        }}
      >
        <div style={{ padding: "20px" }}>
          确定要对{" "}
          <span style={{ fontWeight: 500 }}>
            {
              Object.keys(checkedList)
                .map((k) => checkedList[k])
                .flat(1).length
            }
            台
          </span>{" "}
          主机下发 <span style={{ fontWeight: 500 }}>开启维护模式</span> 操作？
        </div>
      </OmpMessageModal>

      <OmpMessageModal
        visibleHandle={[closeMaintainModal, setCloseMaintainModal]}
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
          fetchMaintainChange(false, checkedList);
        }}
      >
        <div style={{ padding: "20px" }}>
          确定要对{" "}
          <span style={{ fontWeight: 500 }}>
            {
              Object.keys(checkedList)
                .map((k) => checkedList[k])
                .flat(1).length
            }
            台
          </span>{" "}
          主机下发 <span style={{ fontWeight: 500 }}>关闭维护模式</span> 操作？
        </div>
      </OmpMessageModal>

      <OmpMessageModal
        visibleHandle={[openMaintainOneModal, setOpenMaintainOneModal]}
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
          //console.log(1111)
          fetchMaintainChange(true, [row]);
        }}
      >
        <div style={{ padding: "20px" }}>
          确定要对 <span style={{ fontWeight: 500 }}>当前</span> 主机下发{" "}
          <span style={{ fontWeight: 500 }}>开启维护模式</span> 操作？
        </div>
      </OmpMessageModal>

      <OmpMessageModal
        visibleHandle={[closeMaintainOneModal, setCloseMaintainOneModal]}
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
          fetchMaintainChange(false, [row]);
        }}
      >
        <div style={{ padding: "20px" }}>
          确定要对 <span style={{ fontWeight: 500 }}>当前</span> 主机下发{" "}
          <span style={{ fontWeight: 500 }}>关闭维护模式</span> 操作？
        </div>
      </OmpMessageModal>
      <BatchImportMachineModal
        loading={loading}
        setLoading={setLoading}
        batchImport={batchImport}
        setBatchImport={setBatchImport}
      ></BatchImportMachineModal>
    </OmpContentWrapper>
  );
};

export default MachineManagement;
