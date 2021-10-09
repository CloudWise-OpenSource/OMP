import { OmpContentWrapper, OmpTable, OmpMessageModal } from "@/components";
import { Button, Select, message, Menu, Dropdown, Modal } from "antd";
import { useState, useEffect, useRef } from "react";
import { handleResponse, _idxInit, refreshTime } from "@/utils/utils";
import { fetchGet, fetchPost, fetchPatch } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
//import updata from "@/store_global/globalStore";
import { useDispatch } from "react-redux";
import getColumnsConfig from "./config/columns";
import {
  DownOutlined,
  ExclamationCircleOutlined,
  ImportOutlined,
} from "@ant-design/icons";

const AlarmLog = () => {
  //console.log(location.state, "location.state");

  const [loading, setLoading] = useState(false);

  const [searchLoading, setSearchLoading] = useState(false);

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

  //select 的onblur函数拿不到最新的search value,使用useref存(是最新的，但是因为失去焦点时会自动触发清空search，还是得使用ref存)
  const searchValueRef = useRef(null);

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
          setDataSource([
            {
              type: "host",
              ip: "10.0.3.72",
              instance_name: "hosts1",
              severity: "critical",
              description: "实例 10.0.3.72 已宕机超过1分钟",
              date: "2021-09-27 07:08:05",
              monitor_url:
                "http://127.0.0.1:19013/proxy/v1/grafana/d/9CWBz0bik/zhu-ji-xin-xi-mian-ban?var-node=10.0.3.72",
              log_url: null,
            },
            {
              type: "host",
              ip: "10.0.3.73",
              instance_name: null,
              severity: "critical",
              description: "实例 10.0.3.71 已宕机超过1分钟",
              date: "2021-09-27 07:07:24",
              monitor_url:
                "http://127.0.0.1:19013/proxy/v1/grafana/d/9CWBz0bik/zhu-ji-xin-xi-mian-ban?var-node=10.0.3.73",
              log_url: null,
            },
            {
              type: "service",
              ip: "10.0.7.164",
              instance_name: "dolaLogMonitorServer",
              severity: "critical",
              description:
                "主机 10.0.7.164 中的 服务 dolaLogMonitorServer 已经down掉超过一分钟.",
              date: "2021-06-26 07:23:42",
              monitor_url:
                "http://127.0.0.1:19013/proxy/v1/grafana/d/9CSxoPAGz/fu-wu-zhuang-tai-xin-xi-mian-ban?var-ip=10.0.7.164&var-app=dolaLogMonitorServer",
              log_url:
                "http://127.0.0.1:19013/proxy/v1/grafana/d/liz0yRCZz/applogs?var-app=dolaLogMonitorServer",
            },
          ]);
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
          批量已读
        </Button>

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
              //   dispatch(refreshTime());
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
          scroll={{x:1400}}
          onChange={(e, filters, sorter) => {
            let ordering = sorter.order
              ? `${sorter.order == "descend" ? "" : "-"}${sorter.columnKey}`
              : null;
            setTimeout(() => {
              fetchData(e, pagination.searchParams, ordering);
            }, 200);
          }}
          columns={getColumnsConfig()}
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

export default AlarmLog;
