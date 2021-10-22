import {
  OmpContentWrapper,
  OmpTable,
  OmpMessageModal,
  OmpSelect,
  OmpDrawer,
} from "@/components";
import { Button, message, Menu, Dropdown, Input } from "antd";
import { useState, useEffect, useRef } from "react";
import { handleResponse, _idxInit } from "@/utils/utils";
import { fetchGet, fetchPost, fetchPatch } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";

// import {
//   AddMachineModal,
//   UpDateMachineModal,
//   BatchImportMachineModal,
// } from "./config/modals";
import { useDispatch } from "react-redux";
//import getColumnsConfig, { DetailHost } from "./config/columns";
import { DownOutlined, ExclamationCircleOutlined, SearchOutlined } from "@ant-design/icons";
import { useHistory, useLocation } from "react-router-dom";
const PatrolInspectionRecord = () => {
  const [loading, setLoading] = useState(false);
  const [instanceSelectValue, setInstanceSelectValue] = useState("");
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    ordering: "",
    searchParams: {},
  });
  function fetchData(
    pageParams = { current: 1, pageSize: 10 },
    searchParams = {},
    ordering
  ) {
    // setLoading(true);
    // fetchGet(apiRequest.Alert.listAlert, {
    //   params: {
    //     page: pageParams.current,
    //     size: pageParams.pageSize,
    //     ordering: ordering ? ordering : null,
    //     ...searchParams,
    //   },
    // })
    //   .then((res) => {
    //     handleResponse(res, (res) => {
    //       setDataSource(res.data.results);
    //       setPagination({
    //         ...pagination,
    //         total: res.data.count,
    //         pageSize: pageParams.pageSize,
    //         current: pageParams.current,
    //         ordering: ordering,
    //         searchParams: searchParams,
    //       });
    //     });
    //   })
    //   .catch((e) => console.log(e))
    //   .finally(() => {
    //     location.state = {};
    //     setLoading(false);
    //     fetchIPlist();
    //     //fetchNameList();
    //   });
  }
  return <div>123123</div>
  return (
    <OmpContentWrapper>
      <div style={{ display: "flex" }}>
        <Button type="primary">添加</Button>

        <Button type="primary" style={{ marginLeft: 10 }}>
          导入
        </Button>

        <div style={{ display: "flex", marginLeft: "auto" }}>
          <span style={{ width: 80, display: "flex", alignItems: "center" }}>
            报告名称:
          </span>
          <Input
            placeholder="输入实例名称"
            style={{ width: 200 }}
            allowClear
            value={instanceSelectValue}
            onChange={(e) => {
              setInstanceSelectValue(e.target.value);
              if (!e.target.value) {
                fetchData({
                  //...searchParams,
                  instance_name: null,
                });
              }
            }}
            onBlur={() => {
              fetchData({
                //...searchParams,
                instance_name: instanceSelectValue,
              });
            }}
            onPressEnter={() => {
              fetchData({
                //...searchParams,
                instance_name: instanceSelectValue,
              });
            }}
            suffix={
              !instanceSelectValue && (
                <SearchOutlined style={{ fontSize: 12, color: "#b6b6b6" }} />
              )
            }
          />
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
          //   onChange={(e, filters, sorter) => {
          //     let ordering = sorter.order
          //       ? `${sorter.order == "descend" ? "" : "-"}${sorter.columnKey}`
          //       : null;
          //     setTimeout(() => {
          //       fetchData(e, pagination.searchParams, ordering);
          //     }, 200);
          //   }}
          columns={[]}
          //   columns={getColumnsConfig(
          //     setIsShowDrawer,
          //     setRow,
          //     setUpdateMoadlVisible,
          //     fetchHistoryData,
          //     setCloseMaintainOneModal,
          //     setOpenMaintainOneModal,
          //     setShowIframe,
          //     history
          //   )}
          // dataSource={dataSource}
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
        />
      </div>
    </OmpContentWrapper>
  );
};

export default PatrolInspectionRecord;
