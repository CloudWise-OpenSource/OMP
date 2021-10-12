import {
  OmpContentWrapper,
  OmpTable,
  OmpMessageModal,
  OmpSelect,
  OmpDatePicker
} from "@/components";
import { Button, Select, message, Menu, Dropdown, Modal, Input } from "antd";
import { useState, useEffect, useRef } from "react";
import { handleResponse, _idxInit, refreshTime } from "@/utils/utils";
import { fetchGet, fetchPost, fetchPatch } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
//import updata from "@/store_global/globalStore";
import { useDispatch } from "react-redux";
import getColumnsConfig from "./config/columns";

const ExceptionList = () => {
  //console.log(location.state, "location.state");

  const [loading, setLoading] = useState(false);

  const [searchLoading, setSearchLoading] = useState(false);

  //选中的数据
  const [checkedList, setCheckedList] = useState({});

  //table表格数据
  const [dataSource, setDataSource] = useState([]);
  const [ipListSource, setIpListSource] = useState([]);

  const [selectValue, setSelectValue] = useState();

  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    ordering: "",
    searchParams: {},
  });

  // 筛选label
  const [labelControl, setLabelControl] = useState("ip");

  function fetchData(
    pageParams = { current: 1, pageSize: 10 },
    searchParams,
    ordering
  ) {
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
    setLoading(true);
    fetchGet("/api/promemonitor/listAlert/", {
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

  useEffect(() => {
    fetchData(pagination);
  }, []);

  return (
    <OmpContentWrapper>
      <div style={{ display: "flex", justifyContent:"space-between" }}>
        <Button
          type="primary"
          onClick={() => {
            setAddMoadlVisible(true);
          }}
        >
          批量已读
        </Button>
        <div style={{display:"flex"}}>
        <OmpDatePicker/>
        <div style={{ display: "flex", marginLeft: "10px" }}>
          <Input.Group compact style={{ display: "flex"}}> 
            <Select
              value={labelControl}
              style={{ width: 100 }}
              onChange={(e) => setLabelControl(e)}
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
                fetchData={fetchData}
                pagination={pagination}
              />
            )}
             {labelControl === "instance_name" && (
              <Input placeholder="输入实例名称" style={{ width: 200 }}/>
            )}
          </Input.Group>

          <Button
            style={{ marginLeft: 10 }}
            onClick={() => {
              //   dispatch(refreshTime());
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
          scroll={{ x: 1400 }}
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
          rowKey={(record) => record.ip}
          checkedState={[checkedList, setCheckedList]}
        />
      </div>
    </OmpContentWrapper>
  );
};

export default ExceptionList;