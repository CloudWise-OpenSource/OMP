import {
  OmpContentWrapper,
  OmpTable,
  OmpMessageModal,
  OmpSelect,
  OmpDrawer,
} from "@/components";
import { Button, message, Menu, Dropdown, Input, Select } from "antd";
import { useState, useEffect, useRef } from "react";
import { handleResponse, _idxInit, refreshTime } from "@/utils/utils";
import { fetchGet, fetchPost, fetchPatch } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { useDispatch } from "react-redux";
import getColumnsConfig, { DetailHost } from "./config/columns";
import {
  DownOutlined,
  ExclamationCircleOutlined,
  SearchOutlined,
} from "@ant-design/icons";
import { useHistory, useLocation } from "react-router-dom";

const ServiceManagement = () => {
  const location = useLocation();

  const history = useHistory();

  const dispatch = useDispatch();

  const [loading, setLoading] = useState(false);

  const [searchLoading, setSearchLoading] = useState(false);

  //选中的数据
  const [checkedList, setCheckedList] = useState({});

  //table表格数据
  const [dataSource, setDataSource] = useState([]);
  const [ipListSource, setIpListSource] = useState([]);
  const [selectValue, setSelectValue] = useState(location.state?.ip);

  const [labelsData, setLabelsData] = useState([]);

  const [instanceSelectValue, setInstanceSelectValue] = useState("");

  const [labelControl, setLabelControl] = useState("ip");

  const [installationRecordModal, setInstallationRecordModal] = useState(false);

  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    ordering: "",
    searchParams: {},
  });

  const [isShowDrawer, setIsShowDrawer] = useState({
    isOpen: false,
    src: "",
    record: {},
  });

  const [showIframe, setShowIframe] = useState({});

  // 定义row存数据
  const [row, setRow] = useState({});

  // 服务详情历史数据
  const [historyData, setHistoryData] = useState([]);

  // 服务详情loading
  const [historyLoading, setHistoryLoading] = useState([]);

  //const [showIframe, setShowIframe] = useState({});

  const [serviceAcitonModal, setServiceAcitonModal] = useState(false);
  const [currentSerAcitonModal, setCurrentSerAcitonModal] = useState(false);

  // 1启动，2停止，3重启，4删除
  let operateObj = {
    1: "启动",
    2: "停止",
    3: "重启",
    4: "删除",
  };
  const [operateAciton, setOperateAciton] = useState(1);

  // 列表查询
  function fetchData(
    pageParams = { current: 1, pageSize: 10 },
    searchParams,
    ordering
  ) {
    setLoading(true);
    fetchGet(apiRequest.appStore.services, {
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
        location.state = {};
        setLoading(false);
        fetchIPlist();
        fetchSearchlist();
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

  // 功能模块筛选
  const fetchSearchlist = () => {
    //setSearchLoading(true);
    fetchGet(apiRequest.appStore.queryLabels)
      .then((res) => {
        handleResponse(res, (res) => {
          setLabelsData(res.data);
          //console.log(res.data);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        //setSearchLoading(false);
      });
  };

  const fetchHistoryData = (id) => {
    setHistoryLoading(true);
    fetchGet(`${apiRequest.appStore.servicesDetail}/${id}/`, {
      // params: {
      //   id: id,
      // },
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

  const t = useRef(null)

  // 服务的启动｜停止｜重启
  const operateService = (data, operate) => {
    setLoading(true);
    fetchPost(apiRequest.appStore.servicesAction, {
      body: {
        data: data.map((i) => ({
          action: operate,
          id: i.id,
          operation_user: localStorage.getItem("username"),
        })),
      },
    })
      .then((res) => {
        //console.log(operateObj[operateAciton])
        handleResponse(res, (res) => {
          message.success(`${operateObj[operateAciton]}操作下发成功`);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
        setServiceAcitonModal(false);
        setCurrentSerAcitonModal(false);
        // setRestartHostAgentModal(false);
        setCheckedList({});
        setRow({});
        setLoading(true)
        t.current = setTimeout(()=>{
          fetchData(
            { current: pagination.current, pageSize: pagination.pageSize },
            {
              ...pagination.searchParams,
              ip: selectValue,
              service_instance_name: instanceSelectValue,
            },
            pagination.ordering
          );
        },1500)
      });
  };

  const containerRef = useRef(null);

  const timer = useRef(null);

  const [log, setLog] = useState("")

  const queryServiceInstallHistoryDetail = (id) => {
    fetchGet(apiRequest.appStore.serviceInstallHistoryDetail, {
      params: {
        id: id,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          setLog(res.data[0].log)
          if (
            res.data[0].install_step_status == 1 ||
            res.data[0].install_step_status == 0
          ) {
            timer.current = setTimeout(() => {
              queryServiceInstallHistoryDetail(id);
            }, 2000);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        containerRef.current.scrollTop = containerRef.current.scrollHeight;
      });
  };

  useEffect(() => {
    fetchData(
      { current: pagination.current, pageSize: pagination.pageSize },
      {
        ip: location.state?.ip,
        app_type: location.state?.app_type,
        label_name: location.state?.label_name,
      }
    );
    return ()=>{
      if(t.current){
        clearTimeout(t.current)
      }
    }
  }, []);

  return (
    <OmpContentWrapper>
      <div style={{ display: "flex" }}>
        <Button
          type="primary"
          onClick={() => {
            history.push("/application_management/app_store");
          }}
        >
          安装
        </Button>

        <Dropdown
          //placement="bottomLeft"
          overlay={
            <Menu>
              <Menu.Item
                key="openMaintain"
                style={{ textAlign: "center" }}
                onClick={() => {
                  setOperateAciton(1);
                  setServiceAcitonModal(true);
                }}
                disabled={
                  Object.keys(checkedList)
                    .map((k) => checkedList[k])
                    .flat(1)
                    .map((item) => item.id).length == 0
                }
              >
                启动
              </Menu.Item>
              <Menu.Item
                key="closeMaintain"
                style={{ textAlign: "center" }}
                disabled={
                  Object.keys(checkedList)
                    .map((k) => checkedList[k])
                    .flat(1)
                    .map((item) => item.id).length == 0
                }
                onClick={() => {
                  setOperateAciton(2);
                  setServiceAcitonModal(true);
                }}
              >
                停止
              </Menu.Item>
              <Menu.Item
                key="reStartHost"
                style={{ textAlign: "center" }}
                disabled={
                  Object.keys(checkedList)
                    .map((k) => checkedList[k])
                    .flat(1)
                    .map((item) => item.id).length == 0
                }
                onClick={() => {
                  setOperateAciton(3);
                  setServiceAcitonModal(true);
                }}
              >
                重启
              </Menu.Item>
              <Menu.Item
                key="reStartMonitor"
                style={{ textAlign: "center" }}
                disabled={
                  Object.keys(checkedList)
                    .map((k) => checkedList[k])
                    .flat(1)
                    .map((item) => item.id).length == 0
                }
                onClick={() => {
                  setOperateAciton(4);
                  setServiceAcitonModal(true);
                }}
              >
                删除
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
          <Input.Group compact style={{ display: "flex" }}>
            <Select
              value={labelControl}
              defaultValue="ip"
              style={{ width: 100 }}
              onChange={(e) => {
                setLabelControl(e);
                fetchData(
                  {
                    current: 1,
                    pageSize: pagination.pageSize,
                  },
                  {
                    ...pagination.searchParams,
                    ip: null,
                    service_instance_name: null,
                  },
                  pagination.ordering
                );
                setInstanceSelectValue();
                setSelectValue();
              }}
            >
              <Select.Option value="ip"> IP地址</Select.Option>
              <Select.Option value="instance_name">实例名称</Select.Option>
            </Select>
            {labelControl === "ip" && (
              <OmpSelect
                searchLoading={searchLoading}
                selectValue={selectValue}
                listSource={ipListSource}
                setSelectValue={setSelectValue}
                fetchData={(value) => {
                  fetchData(
                    { current: 1, pageSize: pagination.pageSize },
                    { ip: value },
                    pagination.ordering
                  );
                }}
              />
            )}
            {labelControl === "instance_name" && (
              <Input
                placeholder="输入实例名称"
                style={{ width: 200 }}
                allowClear
                value={instanceSelectValue}
                onChange={(e) => {
                  setInstanceSelectValue(e.target.value);
                  if (!e.target.value) {
                    fetchData(
                      {
                        current: 1,
                        pageSize: pagination.pageSize,
                      },
                      {
                        ...pagination.searchParams,
                        service_instance_name: null,
                      },
                      pagination.ordering
                    );
                  }
                }}
                onBlur={() => {
                  if (instanceSelectValue) {
                    fetchData(
                      {
                        current: 1,
                        pageSize: pagination.pageSize,
                      },
                      {
                        ...pagination.searchParams,
                        service_instance_name: instanceSelectValue,
                      },
                      pagination.ordering
                    );
                  }
                }}
                onPressEnter={() => {
                  fetchData(
                    {
                      current: 1,
                      pageSize: pagination.pageSize,
                    },
                    {
                      ...pagination.searchParams,
                      service_instance_name: instanceSelectValue,
                    },
                    pagination.ordering
                  );
                }}
                suffix={
                  !instanceSelectValue && (
                    <SearchOutlined style={{ color: "#b6b6b6" }} />
                  )
                }
              />
            )}
          </Input.Group>

          <Button
            style={{ marginLeft: 10 }}
            onClick={() => {
              //location.state = {}
              dispatch(refreshTime());
              setCheckedList({});
              fetchData(
                { current: pagination.current, pageSize: pagination.pageSize },
                {
                  ...pagination.searchParams,
                  ip: selectValue,
                  service_instance_name: instanceSelectValue,
                },
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
          //scroll={{ x: 1900 }}
          onChange={(e, filters, sorter) => {
            let ordering = sorter.order
              ? `${sorter.order == "descend" ? "" : "-"}${sorter.columnKey}`
              : null;
            setTimeout(() => {
              fetchData(e, pagination.searchParams, ordering);
            }, 200);
          }}
          columns={getColumnsConfig(
            setIsShowDrawer,
            setRow,
            fetchHistoryData,
            history,
            labelsData,
            (params) => {
              fetchData(
                { current: 1, pageSize: pagination.pageSize },
                { ...pagination.searchParams, ...params },
                pagination.ordering
              );
            },
            location.state?.app_type,
            location.state?.label_name,
            setShowIframe,
            setOperateAciton,
            setCurrentSerAcitonModal,
          )}
          notSelectable={(record) => ({
            // 部署中的不能选中
            disabled: !record?.operable,
          })}
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
      <OmpDrawer showIframe={showIframe} setShowIframe={setShowIframe}  />
      <DetailHost
        isShowDrawer={isShowDrawer}
        setIsShowDrawer={setIsShowDrawer}
        loading={historyLoading}
        data={historyData}
        setInstallationRecordModal={setInstallationRecordModal}
        queryServiceInstallHistoryDetail={
          (id)=>queryServiceInstallHistoryDetail(id)
          }
      />
      <OmpMessageModal
        visibleHandle={[serviceAcitonModal, setServiceAcitonModal]}
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
          operateService(
            Object.keys(checkedList)
              .map((k) => checkedList[k])
              .flat(1),
            operateAciton
          );
          //fetchMaintainChange(false, [row]);
        }}
      >
        <div style={{ padding: "20px" }}>
          确定要对{" "}
          <span style={{ fontWeight: 500 }}>
            {" "}
            {
              Object.keys(checkedList)
                .map((k) => checkedList[k])
                .flat(1).length
            }
          </span>{" "}
          个 服务下发{" "}
          <span style={{ fontWeight: 500 }}>{operateObj[operateAciton]}</span>{" "}
          操作？
        </div>
      </OmpMessageModal>
      <OmpMessageModal
        visibleHandle={[currentSerAcitonModal, setCurrentSerAcitonModal]}
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
          operateService([row], operateAciton);
        }}
      >
        <div style={{ padding: "20px" }}>
          确定要对 <span style={{ fontWeight: 500 }}>当前</span> 服务下发{" "}
          <span style={{ fontWeight: 500 }}>{operateObj[operateAciton]}</span>{" "}
          操作？
        </div>
      </OmpMessageModal>
      <OmpMessageModal
        title="安装记录"
        bodyStyle={{
          backgroundColor: "#000",
          color: "#fff",
          padding:0
        }}
        style={{
          top: 200,
        }}
        afterClose={()=>{
          console.log("关闭")
          if(timer.current){
            clearTimeout(timer.current)
          }
        }}
        noFooter={true}
        visibleHandle={[installationRecordModal, setInstallationRecordModal]}
      >
        <div
          ref={containerRef}
          style={{
            padding:10,
            // marginTop: 10,
            // padding: 10,
            minHeight: 30,
            height: 300,
            // transition: "all .2s ease-in",
            // overflow: "hidden",
            color: "#fff",
            backgroundColor: "#000",
            wordWrap: "break-word",
            wordBreak: "break-all",
            whiteSpace: "pre-line",
            overflowY: "auto",
            overflowX: "hidden",
          }}
        >
          {log ? log : "正在安装..."}
        </div>
      </OmpMessageModal>
    </OmpContentWrapper>
  );
};

export default ServiceManagement;
