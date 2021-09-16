import { useState, useEffect } from "react";
import { Button, Input, Select, Badge, Form } from "antd";
import {
  columnsConfig,
  tableButtonHandler,
  _idxInit,
  TableRowButton,
  handleResponse,
} from "@/utils/utils";
import {
  OmpOperationWrapper,
  OmpTable,
  OmpCollapseWrapper,
  OmpDatePicker,
  OmpButton
} from "@/components";
import { fetchGet, fetchPut } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { getAbnormalHostNumberChangeAction } from "../store/actionsCreators";
import { useDispatch } from "react-redux";
import { SyncOutlined } from "@ant-design/icons";

const ServiceTab = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });

  const dispatch = useDispatch();

  //只是对servicetype value的记录，并不是servicetype的value
  const [serviceTypeEffect, setServiceTypeEffect] = useState();

  //表格dataSource
  const [serviceData, setServiceData] = useState([]);

  //选中的数据
  const [checkedList, setCheckedList] = useState({});

  const columnsService = [
    {
      title: "序列",
      key: "index",
      render: (text, record, index) => {
        let idx = record._idx + (pagination.current - 1) * pagination.pageSize;
        return (
          <Badge style={{ marginRight: "-8px" }} dot={record.is_read === 0}>
            {idx}
          </Badge>
        );
      },
      align: "center",
      width: 70,
      fixed: "left",
    },
    columnsConfig.alert_service_type,
    {
      ...columnsConfig.alert_service_name,
      title:serviceTypeEffect=="component"?"组件名称":"服务名称"
    },
    //columnsConfig.alert_service_name,
    columnsConfig.alert_host_ip,
    columnsConfig.alert_level,
    columnsConfig.warning_record_alert_time,
    columnsConfig.alert_describe,
    // columnsConfig.alert_receiver,
    // columnsConfig.alert_resolve,
    {
      title: "操作",
      dataIndex: "",
      render: function renderFunc(text, record, index) {
        return (
          <TableRowButton
            buttonsArr={[
              {
                btnText: "监控",
                btnHandler: () => {
                  tableButtonHandler(record);
                  updateRead([record.id]);
                },
              },
              // {
              //   btnText: "分析",
              //   btnHandler: () => history.push("/operation-management/report"),
              // },
              {
                btnText: "日志",
                btnHandler: () => tableButtonHandler(record, "log"),
              },
            ]}
          />
        );
      },
      width: 150,
      align: "center",
      fixed: "right",
    },
  ];

  const columnsThridService = [
    {
      title: "序列",
      key: "index",
      render: (text, record, index) => {
        let idx = record._idx + (pagination.current - 1) * pagination.pageSize;
        return (
          <Badge style={{ marginRight: "-8px" }} dot={record.is_read === 0}>
            {idx}
          </Badge>
        );
      },
      align: "center",
      width: 70,
      fixed: "left",
    },
    columnsConfig.alert_service_type,
    {
      ...columnsConfig.alert_service_name,
      title: "组件名称"
    },
    columnsConfig.alert_host_ip,
    columnsConfig.alert_level,
    columnsConfig.warning_record_alert_time,
    columnsConfig.alert_describe,
    // columnsConfig.alert_receiver,
    // columnsConfig.alert_resolve,
  ];

  const onServiceTypeChange = (e) => {
    setServiceTypeEffect(e);
  };

  //数据请求
  const getServiceData = (pageParams = { current: 1, pageSize: 10 }) => {
    setLoading(true);
    fetchGet(apiRequest.operationManagement.alertRecord, {
      params: {
        query_type: "normal",
        alert_type: "service",
        alert_service_type: serviceTypeEffect,
        page_num: pageParams.current,
        page_size: pageParams.pageSize,
        ...form.getFieldValue(),
      },
    })
      .then((serviceDataRes) => {
        serviceDataRes = serviceDataRes.data
        //console.log(serviceDataRes.code);
        setPagination((pagination) => ({
          ...pagination,
          current: Number(serviceDataRes.data.page_num),
          pageSize: Number(serviceDataRes.data.per_page),
          total: serviceDataRes.data.total,
        }));
        if (serviceDataRes && serviceDataRes.code == 0) {
          // console.log("进来了", serviceDataRes);
          handleResponse(serviceDataRes, () => {
            setServiceData(_idxInit(serviceDataRes.data.data));
          });
        }
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  // 点击监控按钮时更新已读信息
  function updateRead(idArr) {
    setLoading(true);
    fetchPut(apiRequest.operationManagement.alertRecord, {
      body: {
        update_data: idArr,
      },
    })
      .then((res) => {
        res = res.data
        handleResponse(res, () => {
          if (res.code == 0) {
            getServiceData(pagination);
            setCheckedList({});
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  }

  const onSubmit = (e) => {
    getServiceData(pagination);
  };

  useEffect(async() => {
    getServiceData(pagination);
    dispatch(await getAbnormalHostNumberChangeAction());
  }, [serviceTypeEffect]);

  return (
    <>
      {/* <OmpCollapseWrapper
        form={form}
        onReset={() => {
          !serviceTypeEffect && getServiceData(pagination);
          setCheckedList({})
          setServiceTypeEffect();
        }}
        onFinish={onSubmit}
      >
        <Select
          label="服务类型"
          name="serverType"
          placeholder="请选择服务类型"
          onChange={onServiceTypeChange}
        >
          <Select.Option value="self_dev">自有服务</Select.Option>
          <Select.Option value="component">自有组件</Select.Option>
          <Select.Option value="external">三方组件</Select.Option>
          <Select.Option value="database">数据库</Select.Option>
        </Select>

        <Select
          name="alert_level"
          label="告警级别"
          placeholder="请选择告警级别"
        >
          <Select.Option value="critical">严重</Select.Option>
          <Select.Option value="warning">警告</Select.Option>
        </Select>
        <Select
          name="alert_service_name"
          label={serviceTypeEffect=="component"||serviceTypeEffect=="external"?"组件名称":"服务名称"}
          placeholder={`请选择${serviceTypeEffect=="component"||serviceTypeEffect=="external"?"组件":"服务"}名称`}
        >
          <Select.Option value="clickhouse">clickhouse</Select.Option>
          <Select.Option value="arangodb">arangodb</Select.Option>
          <Select.Option value="ignite">ignite</Select.Option>
          <Select.Option value="elasticsearch">elasticsearch</Select.Option>
        </Select>
        <Select name="alert_ip" label="IP地址" placeholder="请选择IP地址">
          <Select.Option value="10.0.9.61">10.0.9.61</Select.Option>
          <Select.Option value="10.0.9.62">10.0.9.62</Select.Option>
          <Select.Option value="10.0.9.63">10.0.9.63</Select.Option>
        </Select>
        <Select name="mode" label="功能模块" placeholder="请选择功能模块">
          <Select.Option value="基础组件">基础组件</Select.Option>
          <Select.Option value="数据中心">数据中心</Select.Option>
        </Select>
        <OmpDatePicker name="time" label="告警时间" width={460} />
      </OmpCollapseWrapper> */}
      <div
        style={{
          border: "1px solid #dcdee5",
          // paddingLeft: 10,
          // paddingRight: 10,
          //marginBottom:200,
          backgroundColor: "white",
        }}
      >
        <OmpTable
          loading={loading}
          //scroll={{y:'calc(100vh - 520px)'}}
          onChange={(e) => getServiceData(e)}
          columns={
            serviceTypeEffect === "external"
              ? columnsThridService
              : columnsService
          }
          dataSource={serviceData}
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
    </>
  );
};

export default ServiceTab;
