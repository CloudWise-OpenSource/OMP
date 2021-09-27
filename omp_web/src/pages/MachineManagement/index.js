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
} from "antd";
import { useState, useEffect, useRef } from "react";
import {
  handleResponse,
  _idxInit,
  refreshTime,
  MessageTip,
} from "@/utils/utils";
import { fetchGet, fetchDelete, fetchPost, fetchPut } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
//import updata from "@/store_global/globalStore";
import { AddMachineModal, UpDateMachineModal } from "./config/modals";
import { useDispatch } from "react-redux";
import getColumnsConfig, { DetailHost } from "./config/columns";
import { DesktopOutlined } from "@ant-design/icons";

const MachineManagement = () => {
  const dispatch = useDispatch();

  //console.log(location.state, "location.state");

  const [loading, setLoading] = useState(false);

  const [searchLoading, setSearchLoading] = useState(false);

  //添加弹框的控制state
  const [addModalVisible, setAddMoadlVisible] = useState(false);
  //修改弹框的控制state
  const [updateMoadlVisible, setUpdateMoadlVisible] = useState(false);

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
        fetchIPlist()
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
            message.warning(res.data.message.split(":")[1].replace(/;/g,""));
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
    fetchPut(`${apiRequest.machineManagement.hosts}${row.id}/`, {
      body: {
        ...data,
      },
    })
      .then((res) => {
        if (res && res.data) {
          if (res.data.code == 1) {
            // msgRef.current = res.data.message
            // setMsgShow(true)
            message.warning(res.data.message.split(":")[1].replace(/;/g,""));
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

  useEffect(() => {
    fetchData(pagination);
  }, []);

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
        <div style={{ display: "flex", marginLeft: "auto" }}>
          <span style={{ width: 60, display: "flex", alignItems: "center" }}>
            IP地址:
          </span>
          <Select
            allowClear
            onClear={() => {
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
          //scroll={{y:'calc(100vh - 520px)'}}
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
            setUpdateMoadlVisible
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
                  lineHeight: 3,
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
      />
    </OmpContentWrapper>
  );
};

export default MachineManagement;
