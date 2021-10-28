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
import { DownOutlined, ExclamationCircleOutlined } from "@ant-design/icons";
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

  const [labelsData, setLabelsData] = useState([])

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

  // 定义row存数据
  const [row, setRow] = useState({});

  // 服务详情历史数据
  const [historyData, setHistoryData] = useState([]);

  // 服务详情loading
  const [historyLoading, setHistoryLoading] = useState([]);

  //const [showIframe, setShowIframe] = useState({});

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
        fetchSearchlist()
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
          console.log(res.data)
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        //setSearchLoading(false);
      });
  };

  const fetchHistoryData = (id) => {
    return
    setHistoryLoading(true);
    fetchGet(apiRequest.serviceManagement.operateLog, {
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

  useEffect(() => {
    fetchData(
      { current: pagination.current, pageSize: pagination.pageSize },
      { ip: location.state?.ip }
    );
  }, []);

  return (
    <OmpContentWrapper>
      <div style={{ display: "flex" }}>
        <Button
          type="primary"
          onClick={() => {
           // setAddMoadlVisible(true);
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
                // onClick={() => setOpenMaintainModal(true)}
                // disabled={
                //   Object.keys(checkedList)
                //     .map((k) => checkedList[k])
                //     .flat(1)
                //     .map((item) => item.id).length == 0
                // }
              >
                启动
              </Menu.Item>
              <Menu.Item
                key="closeMaintain"
                style={{ textAlign: "center" }}
                // disabled={
                //   Object.keys(checkedList)
                //     .map((k) => checkedList[k])
                //     .flat(1)
                //     .map((item) => item.id).length == 0
                // }
                // onClick={() => {
                //   setCloseMaintainModal(true);
                // }}
              >
                停止
              </Menu.Item>
              <Menu.Item
                key="reStartHost"
                style={{ textAlign: "center" }}
                // disabled={
                //   Object.keys(checkedList)
                //     .map((k) => checkedList[k])
                //     .flat(1)
                //     .map((item) => item.id).length == 0
                // }
                // onClick={() => {
                //   setRestartHostAgentModal(true);
                // }}
              >
                重启
              </Menu.Item>
              <Menu.Item
                key="reStartMonitor"
                style={{ textAlign: "center" }}
                // disabled={
                //   Object.keys(checkedList)
                //     .map((k) => checkedList[k])
                //     .flat(1)
                //     .map((item) => item.id).length == 0
                // }
                // onClick={() => {
                //   setRestartMonterAgentModal(true);
                // }}
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
                //value={labelControl}
                defaultValue="ip"
                style={{ width: 100 }}
                // onChange={(e) => {
                //   setLabelControl(e);
                //   fetchData({
                //     ...searchParams,
                //     ip: null,
                //     instance_name: null,
                //   });
                //   setInstanceSelectValue();
                //   setSelectValue();
                // }}
              >
                <Select.Option value="ip"> IP地址</Select.Option>
                <Select.Option value="instance_name">实例名称</Select.Option>
              </Select>
              <OmpSelect
            searchLoading={searchLoading}
            selectValue={selectValue}
            listSource={ipListSource}
            setSelectValue={setSelectValue}
            // onFocus={()=>{
            //   location.state = {}
            // }}
            fetchData={(value) => {
              fetchData(
                { current: 1, pageSize: pagination.pageSize, },
                { ip: value },
                pagination.ordering
              );
            }}
          />
          </Input.Group>
          {/* <span style={{ width: 60, display: "flex", alignItems: "center" }}>
            IP地址:
          </span> */}
          
          <Button
            style={{ marginLeft: 10 }}
            onClick={() => {
              //location.state = {}
              dispatch(refreshTime());
              setCheckedList({});
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
            history
          )}
          notSelectable={(record) => ({
            // 部署中的不能选中
            disabled: record?.host_agent == 3 || record?.monitor_agent == 3,
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
    </OmpContentWrapper>
  );
};

export default ServiceManagement;
