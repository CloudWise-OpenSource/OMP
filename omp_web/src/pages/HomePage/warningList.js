//import { TableRowButton } from "@/components";
import { apiRequest } from "@/config/requestApi";
//import ContentNav from "@/layouts/ContentNav";
//import ContentWrapper from "@/layouts/ContentWrapper";
import { fetchGet } from "@/utils/request";
import {
  columnsConfig,
  handleResponse,
  paginationConfig,
  tableButtonHandler,
  _idxInit,
  newTableButtonHandler,
} from "@/utils/utils";
import {
  AutoComplete,
  Icon,
  Input,
  Spin,
  Table,
  Button,
  Select,
  Tooltip,
  Drawer,
} from "antd";
import * as R from "ramda";
import React, { useEffect, useState } from "react";
import { useHistory, useLocation } from "react-router-dom";
//import OmpIframe from "@/components/OmpIframe";
/*eslint-disable*/
function WarningList() {
  const location = useLocation();
  const history = useHistory();

  const locationIpState = R.call(() => {
    if (!location.state) return "";

    // 路由携带IP、服务名称作为查询条件，不会存在两种查询同时存在
    const { host_ip, service_name } = location.state;

    if (host_ip) {
      return host_ip;
    }
    // else if (service_name) {
    //   return service_name;
    // }
    else {
      return "";
    }
  });

  const locationState = R.call(() => {
    if (!location.state) return "";

    // 路由携带IP、服务名称作为查询条件，不会存在两种查询同时存在
    const { host_ip, service_name } = location.state;

    // if (host_ip) {
    //   return host_ip;
    // } else
    if (service_name) {
      return service_name;
    } else {
      return "";
    }
  });

  const [isLoading, setLoading] = useState(false);

  // 表格数据
  const [dataSource, setDataSource] = useState([]);

  const [searchData, setSearchData] = useState([]);
  const [searchIpValue, setSearchIpValue] = useState(locationIpState);
  const [searchNameValue, setSearchNameValue] = useState(locationState);
  const [searchTypeValue, setSearchTypeValue] = useState("");
  const [searchLevelValue, setSearchLevelValue] = useState("");
  //功能模块筛选
  const [searchModalValue, setSearchModalValue] = useState("");

  // const [searchValue, setSearchValue] = useState(locationState);

  //筛选框label
  const [searchBarController, setSearchBarController] = useState("ip");

  const columns = [
    columnsConfig.service_idx,
    columnsConfig.alert_host_ip,
    {
      title: "告警类型",
      width: 120,
      key: "alert_service_type_frontend",
      dataIndex: "alert_service_type_frontend",
      //ellipsis: true,
      sorter: (a, b) => {
        const str1 = R.defaultTo(" ", a.alert_service_type_frontend);
        const str2 = R.defaultTo(" ", b.alert_service_type);
        return (
          str1.toLowerCase().charCodeAt(0) - str2.toLowerCase().charCodeAt(0)
        );
      },
      sortDirections: ["descend", "ascend"],
      align: "center",
      // render: (text,record)=>{
      //   if(text){
      //     if(text == "host")return "主机异常"
      //     if(text == "service"){
      //       if(record.alert_service_en_type == "external"){
      //         return "三方组件"
      //       }
      //       return record.alert_service_type
      //     }
      //     return text
      //   }else{
      //     return "-"
      //   }
      // },
    },
    columnsConfig.alert_service_name,
    columnsConfig.alert_level,
    columnsConfig.alert_time,
    columnsConfig.alert_describe,
    // {
    //   title: "操作",
    //   key: "操作",
    //   dataIndex: "",
    //   render: function renderFunc(text, record, index) {
    //     if (record.alert_service_type_frontend == "三方组件") {
    //       return "-";
    //     }
    //     return (
    //       <TableRowButton
    //         buttonsArr={[
    //           {
    //             btnText: "监控",
    //             btnHandler: () => {
    //               if (typeof newTableButtonHandler(record) !== "function") {
    //                 setIsShowIsframe({
    //                   isOpen: true,
    //                   src: newTableButtonHandler(record),
    //                   record: record,
    //                 });
    //               }
    //             },
    //           },
    //           {
    //             btnText:
    //               record.alert_service_type_frontend == "主机异常" ? "分析" : "日志",
    //             btnHandler: () => {
    //               if (record.alert_service_type_frontend == "主机异常") {
    //                 history.push("/operation-management/report");
    //               } else {
    //                 if (
    //                   typeof newTableButtonHandler(record, "log") !== "function"
    //                 ) {
    //                   setIsShowIsframe({
    //                     isOpen: true,
    //                     src: newTableButtonHandler(record, "log"),
    //                     record: record,
    //                     isLog:true
    //                   });
    //                 }
    //               }
    //             },
    //           },
    //         ]}
    //       />
    //     );
    //   },
    //   width: 100,
    //   align: "center",
    //   fixed: "right",
    // },
  ];

  const queryData = () => {
    setLoading(true);
    fetchGet(apiRequest.operationManagement.alertList)
      .then((res) => {
        if(res.code == 0){
          if (res.data) {
            let arr = res.data.map((item) => {
              // console.log(item)
              if (item.alert_service_en_type) {
                if (item.alert_service_en_type == "self_dev") {
                  item.alert_service_type_frontend = "自有服务";
                } else if (item.alert_service_en_type == "component") {
                  item.alert_service_type_frontend = "自有组件";
                } else if (item.alert_service_en_type == "database") {
                  item.alert_service_type_frontend = "数据库";
                } else if (item.alert_service_en_type == "external") {
                  item.alert_service_type_frontend = "三方组件";
                  item.alert_host_ip = item.ip;
                  item.alert_service_name = item.service_name;
                  item.alert_describe = item.state_info[0]?.describe;
                  /// ===============================
                  let arr = item.ip?.split(",");
                  let ipStr = "";
                  arr.map((i,idx)=>{
                    if(idx == 0){
                      let a = i.split(":");
                      ipStr+=`${a[0]}`;
                    }else{
                      let b = i.split(":");
                      ipStr+=`, ${b[0]}`;
                    }
                  });
                  item.alert_host_ip = ipStr
                }
              } else {
                item.alert_service_type_frontend = "主机异常";
              }
              return item;
            });
            // console.log(arr)
            // eslint-disable-next-line max-nested-callbacks
            setDataSource(_idxInit(arr));
            //console.log(location)
            if (location.state && location.state.key) {
              //setSearchBarController("type");
              if (location.state.key == "all") {
                setSearchTypeValue("自有服务");
                const result = R.filter(
                  R.propEq("alert_service_type_frontend", "自有服务"),
                  _idxInit(arr)
                );
                if(location.state.service_name){
                  setSearchBarController("name")
                  setSearchNameValue(location.state.service_name)
                  const resultFinally = R.filter(
                    R.propEq("alert_service_name", location.state.service_name),
                    result
                  );
                  setSearchData(resultFinally);
                  return
                }
                setSearchData(result);
              }

              if (location.state.key == "basic") {
                setSearchTypeValue("自有组件");
                const result = R.filter(
                  R.propEq("alert_service_type_frontend", "自有组件"),
                  _idxInit(arr)
                );
                if(location.state.service_name){
                  setSearchBarController("name")
                  setSearchNameValue(location.state.service_name)
                  const resultFinally = R.filter(
                    R.propEq("alert_service_name", location.state.service_name),
                    result
                  );
                  setSearchData(resultFinally);
                  return
                }
                setSearchData(result);
              }

              if (location.state.key == "thirdParty") {
                setSearchTypeValue("三方组件");
                const result = R.filter(
                  R.propEq("alert_service_type_frontend", "三方组件"),
                  _idxInit(arr)
                );
                if(location.state.service_name){
                  setSearchBarController("name")
                  setSearchNameValue(location.state.service_name)
                  const resultFinally = R.filter(
                    R.propEq("alert_service_name", location.state.service_name),
                    result
                  );
                  setSearchData(resultFinally);
                  return
                }
                setSearchData(result);
              }

              if (location.state.key == "database") {
                setSearchTypeValue("数据库");
                const result = R.filter(
                  R.propEq("alert_service_type_frontend", "数据库"),
                  _idxInit(arr)
                );
                if(location.state.service_name){
                  setSearchBarController("name")
                  setSearchNameValue(location.state.service_name)
                  const resultFinally = R.filter(
                    R.propEq("alert_service_name", location.state.service_name),
                    result
                  );
                  setSearchData(resultFinally);
                  return
                }
                setSearchData(result);
              }

              if (location.state.key == "host") {
                //console.log("主机")
                setSearchTypeValue("主机异常");
                const result = R.filter(
                  R.propEq("alert_service_type_frontend", "主机异常"),
                  _idxInit(arr)
                );
                setSearchData(result);
              }

              if (location.state.key == "hostData") {
                setSearchTypeValue("主机异常");
                setSearchIpValue(location.state.host_ip)
                const result = R.filter(
                  R.propEq("alert_service_type_frontend", "主机异常"),
                  _idxInit(arr)
                );
                const resultFinally =  R.filter(
                  R.propEq( "alert_host_ip",location.state.host_ip),
                  result
                );
                setSearchData(resultFinally);
              }
            }
          }
        };
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    queryData();
  }, []);

  const [isShowIframe, setIsShowIsframe] = useState({
    isOpen: false,
    src: "",
    record: {},
    isLog:false
  });

  console.log(location);

  return (
    <div style={{margin:10,border:"1px solid #e8e8e8"}}>
      <Spin spinning={isLoading}>
        {/* <ContentNav data={contentNavData} currentFocus={currentList} /> */}
        <Table
          size={"small"}
          rowKey={(record, index) => index}
          // scroll={{ x: 1200 }}
          columns={columns}
          pagination={{
            showSizeChanger: true,
            pageSizeOptions: ["5", "10", "20", "50"],
            defaultPageSize:5,
            showTotal: () => <span style={{color:"rgb(152, 157, 171)"}}>共计 <span style={{color:"rgb(63, 64, 70)"}}>{dataSource.length}</span> 条</span>,
            total: dataSource.length,
          }}
          dataSource={searchTypeValue ? searchData : dataSource}
        />
      </Spin>
      {/* <Drawer
        title={
          <div style={{ display: "flex" }}>
            <Icon
              type="desktop"
              style={{ position: "relative", top: 3, left: -5 }}
            />
            信息面板
            <span style={{ paddingLeft: 30, fontWeight: 400, fontSize: 15 }}>
              IP: {isShowIframe.record.alert_host_ip}
            </span>
          </div>
        }
        placement="right"
        closable={true}
        width={`calc(100%)`}
        onClose={() => {
          setIsShowIsframe({
            ...isShowIframe,
            isOpen: false,
          });
        }}
        visible={isShowIframe.isOpen}
        bodyStyle={{
          padding: 0,
          //paddingLeft: 50,
          backgroundColor: "#f4f6f8",
        }}
        destroyOnClose={true}
      >
        <OmpIframe
          isShowIframe={isShowIframe}
          setIsShowIsframe={setIsShowIsframe}
        />
      </Drawer> */}
    </div>
  );
}

export default WarningList;
/*eslint-disable*/
