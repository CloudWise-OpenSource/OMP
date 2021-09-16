import { useState, useEffect } from "react";
import {
  Button,
  Input,
  Select,
  Badge,
  Form,
  DatePicker,
  Menu,
  Dropdown,
} from "antd";
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
  OmpButton,
} from "@/components";
import { fetchGet, fetchPut } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { getAbnormalServiceNumberChangeAsyncAction } from "../store/actionsCreators";
import { useDispatch } from "react-redux";
import { SyncOutlined, ReloadOutlined, DownOutlined } from "@ant-design/icons";

const HostTab = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  });

  const dispatch = useDispatch();

  //表格dataSource
  const [hostData, sethostData] = useState([]);

  //选中的数据
  const [checkedList, setCheckedList] = useState({});

  const columnsHost = [
    {
      title: "序列",
      key: "index",
      // eslint-disable-next-line react/display-name
      render: (text, record, index) => {
        //console.log(record);
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
    {
      ...columnsConfig.alert_host_ip,
      width: 80,
    },
    // columnsConfig.alert_host_system,
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
              {
                btnText: "分析",
                btnHandler: () => history.push("/operation-management/report"),
              },
            ]}
          />
        );
      },
      width: 120,
      align: "center",
      fixed: "right",
    },
  ];

  //数据请求
  const getHostData = (pageParams = { current: 1, pageSize: 10 }) => {
    const searchParams = form.getFieldValue();
    setLoading(true);
    fetchGet(apiRequest.operationManagement.alertRecord, {
      params: {
        query_type: "normal",
        alert_type: "host",
        //alert_service_type: serviceTypeEffect,
        page_num: pageParams.current,
        page_size: pageParams.pageSize,
        ...searchParams,
      },
    })
      .then((hostDataRes) => {
        hostDataRes = hostDataRes.data;
        //console.log(hostDataRes.code);
        setPagination((pagination) => ({
          ...pagination,
          current: Number(hostDataRes.data.page_num),
          pageSize: Number(hostDataRes.data.per_page),
          total: hostDataRes.data.total,
        }));
        if (hostDataRes && hostDataRes.code == 0) {
          // console.log("进来了", hostDataRes);
          handleResponse(hostDataRes, () => {
            sethostData(_idxInit(hostDataRes.data.data));
          });
          //if(searchParams == {})
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
        res = res.data;
        handleResponse(res, () => {
          if (res.code == 0) {
            getHostData(pagination);
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
    getHostData(pagination);
  };

  useEffect(async () => {
    getHostData(pagination);
    dispatch(await getAbnormalServiceNumberChangeAsyncAction());
  }, []);

  return (
    <>
      {/* <OmpCollapseWrapper
        form={form}
        onReset={() => {
          getHostData(pagination);
          setCheckedList({});
        }}
        onFinish={onSubmit}
        operation={
          <>
            <Button type="primary" onClick={() => getHostData(pagination)}
                icon={<ReloadOutlined style={{fontSize:12,position:"relative"}} />}
              >
              刷新
            </Button>
            <OmpButton
              type="primary"
              style={{ marginLeft: 10 }}
              disabled={
                Object.keys(checkedList)
                  .map((k) => checkedList[k])
                  .flat(1).length == 0
              }
              onClick={() => {
                let cl = Object.keys(checkedList)
                  .map((k) => checkedList[k])
                  .flat(1);
                updateRead(cl.map((item) => item.id));
              }}
            >
              批量已读
            </OmpButton>
          </>
        }
      >
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
          label="服务名称"
          placeholder="请选择服务名称"
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
          onChange={(e) => getHostData(e)}
          columns={columnsHost}
          dataSource={hostData}
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

export default HostTab;
