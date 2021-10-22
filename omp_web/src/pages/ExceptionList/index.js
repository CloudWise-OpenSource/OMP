import {
  OmpContentWrapper,
  OmpTable,
  OmpMessageModal,
  OmpSelect,
  OmpDatePicker,
  OmpDrawer,
} from "@/components";
import { Button, Select, message, Menu, Dropdown, Modal, Input } from "antd";
import { useState, useEffect, useRef } from "react";
import { handleResponse, _idxInit, refreshTime } from "@/utils/utils";
import { fetchGet, fetchPost, fetchPatch } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import getColumnsConfig from "./config/columns";
import { SearchOutlined } from "@ant-design/icons";
import moment from "moment";
import { useHistory } from "react-router-dom";

const ExceptionList = () => {
  const history = useHistory();
  const [loading, setLoading] = useState(false);

  const [searchLoading, setSearchLoading] = useState(false);

  //table表格数据
  const [dataSource, setDataSource] = useState([]);
  const [ipListSource, setIpListSource] = useState([]);

  const [selectValue, setSelectValue] = useState();

  const [instanceSelectValue, setInstanceSelectValue] = useState();

  const [searchParams, setSearchParams] = useState({});

  // 筛选label
  const [labelControl, setLabelControl] = useState("ip");

  const [showIframe, setShowIframe] = useState({});

  function fetchData(searchParams = {}) {
    setLoading(true);
    fetchGet(apiRequest.ExceptionList.exceptionList, {
      params: {
        ...searchParams,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          setSearchParams(searchParams)
          setDataSource(
            res.data.map((item, idx) => ({
              ...item,
              key: idx + item.ip,
            }))
          );
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
    fetchData();
  }, []);

  return (
    <OmpContentWrapper>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <div />
        <div style={{ display: "flex" }}>
          <div style={{ display: "flex", marginLeft: "10px" }}>
            <Input.Group compact style={{ display: "flex" }}>
              <Select
                value={labelControl}
                style={{ width: 100 }}
                onChange={(e) => {
                  setLabelControl(e);
                  fetchData({
                    ...searchParams,
                    ip: null,
                    instance_name: null,
                  });
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
                    fetchData({ ...searchParams, ip: value });
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
                      fetchData({
                        ...searchParams,
                        instance_name: null,
                      });
                    }
                  }}
                  onBlur={() => {
                    if(instanceSelectValue){
                      fetchData({
                        ...searchParams,
                        instance_name: instanceSelectValue,
                      });
                    }
                  }}
                  onPressEnter={() => {
                    fetchData({
                      ...searchParams,
                      instance_name: instanceSelectValue,
                    });
                  }}
                  suffix={
                    !instanceSelectValue && (
                      <SearchOutlined
                        style={{ fontSize: 12, color: "#b6b6b6" }}
                      />
                    )
                  }
                />
              )}
            </Input.Group>

            <Button
              style={{ marginLeft: 10 }}
              onClick={() => {
                fetchData({ ...searchParams });
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
          //scroll={{ x: 1400 }}
          onChange={(e, filters, sorter) => {
            if (sorter.columnKey) {
              let sort = sorter.order == "descend" ? 0 : 1;
              setTimeout(() => {
                fetchData({
                  ...searchParams,
                  ordering: sorter.column ? sorter.columnKey : null,
                  asc: sorter.column ? sort : null,
                });
              }, 200);
            }
          }}
          columns={getColumnsConfig(
            (params) => {
              fetchData({ ...searchParams, ...params });
            },
            setShowIframe,
            history
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
                  //justifyContent: "space-between",
                  flexDirection: "row-reverse",
                  lineHeight: 2.8,
                }}
              >
                <p style={{ color: "rgb(152, 157, 171)" }}>
                  共计{" "}
                  <span style={{ color: "rgb(63, 64, 70)" }}>
                    {dataSource?.length}
                  </span>{" "}
                  条
                </p>
              </div>
            ),
          }}
          //rowKey={(record) => record.ip}
          //checkedState={[checkedList, setCheckedList]}
        />
      </div>
      <OmpDrawer showIframe={showIframe} setShowIframe={setShowIframe} />
    </OmpContentWrapper>
  );
};

export default ExceptionList;
