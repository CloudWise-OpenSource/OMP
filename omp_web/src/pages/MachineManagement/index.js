import {
  OmpContentWrapper,
  OmpDatePicker,
  OmpOperationWrapper,
  OmpTable,
  OmpCollapseWrapper,
  OmpButton,
  OmpMessageModal,
  OmpModal,
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
import { useState, useEffect } from "react";
import {
  handleResponse,
  _idxInit,
  TableRowButton,
  columnsConfig,
  isTableTextInvalid,
  renderInformation,
  renderFormattedTime,
  refreshTime
} from "@/utils/utils";
import { SyncOutlined, ReloadOutlined } from "@ant-design/icons";
import { fetchGet, fetchDelete, fetchPost } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { WarningFilled, DownOutlined } from "@ant-design/icons";
import { useHistory, useLocation } from "react-router-dom";
import styles from "@/pages/MachineManagement/index.module.less";
//import updata from "@/store_global/globalStore";
import D from "./data.json"
import { AddMachineModal } from "./modals"
import { useDispatch } from "react-redux";

const MachineManagement = () => {
  const dispatch = useDispatch();
  const history = useHistory();
  const location = useLocation();
  const [form] = Form.useForm();
  //console.log(location.state, "location.state");

  const [loading, setLoading] = useState(false);

  //删除弹框的控制state
  const [deleteModalVisible, setDeleteModalVisible] = useState(false);
  //添加弹框的控制state
  const [addModalVisible, setAddMoadlVisible] = useState(false);

  //选中的数据
  const [checkedList, setCheckedList] = useState({});

  //table表格数据
  const [dataSource, setDataSource] = useState([]);

  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  });

  const columns = [
    columnsConfig.machine_idx,
    //columnsConfig.ip,
    {
      title: "IP地址",
      width: 140,
      key: "ip",
      dataIndex: "ip",
      ellipsis: true,
      sorter: (a, b) => {
        if (!a.ip || !b.ip) return 0;

        const ip1 = a.ip
          .split(".")
          .map((el) => el.padStart(3, "0"))
          .join("");
        const ip2 = b.ip
          .split(".")
          .map((el) => el.padStart(3, "0"))
          .join("");
        return ip1 - ip2;
      },
      sortDirections: ["descend", "ascend"],
      align: "center",
      render: (text, record) => {
        //let rotate = expandRowsKey.includes(record.id) ? 270 : 90;
        return (
          <span style={{ display: "flex", justifyContent: "space-around" }}>
            <span>{record.is_omp_host ? `${text}(OMP)` : text}</span>
          </span>
        );
      },
    },
    columnsConfig.cpu_rate,
    columnsConfig.memory_rate,
    columnsConfig.disk_rate,
    {
      ...columnsConfig.disk_data_rate,
      width: 120,
    },
    {
      ...columnsConfig.ssh_state,
      width: 80,
    },
    {
      ...columnsConfig.agent_state,
      width: 80,
    },

    // columnsConfig.running_time,
    {
      title: "服务总数",
      width: 100,
      key: "service_number",
      dataIndex: "service_number",
      render: (text, record, index) => {
        if (isTableTextInvalid(text)) {
          return "-";
        } else if (Number(text) > 0) {
          return (
            <Badge dot={false}>
              <a
                onClick={() => {
                  history.push({
                    pathname: "/products-management/service",
                    state: {
                      host_ip: record.ip,
                    },
                  });
                }}
              >
                {`${text}`}个
              </a>
            </Badge>
          );
        } else {
          return `${text}个`;
        }
      },
      align: "center",
    },
    {
      title: "操作",
      dataIndex: "",
      render: function renderFunc(text, record, index) {
        return (
          <TableRowButton
            buttonsArr={[
              {
                btnText: "监控",
                btnHandler: () => tableButtonHandler(record),
              },
              {
                btnText: "分析",
                btnHandler: () => history.push("/operation-management/report"),
              },
            ]}
          />
        );
      },
      align: "center",
      // fixed: "right",
      width: 100,
    },
  ];

  const [isSSHChecked, setIsSSHChecked] = useState(false);

  function fetchData(pageParams = { current: 1, pageSize: 10 }) {
    // setLoading(true);
    // fetchGet(apiRequest.machineManagement.hosts, {
    //   params: {
    //     page_num: pageParams.current,
    //     page_size: pageParams.pageSize,
    //     ...form.getFieldValue(),
    //   },
    // })
      //.then((res) => {
        let res = D.data;
        //handleResponse(res, () => {
          console.log(D)
          const _used = res;

          // if (location.state && location.state.host_ip) {
          //   //console.log("进到if中");
          //   const result = R.filter(
          //     R.propEq("ip", location.state.host_ip),
          //     _used
          //   );
          //   setSearchData(result);
          // }
console.log(_used)
          const ompHost = _used.filter((item) => item.is_omp_host);
          const unOmpHost = _used.filter((item) => !item.is_omp_host);
          const sorted_used = [...ompHost, ...unOmpHost];
          setDataSource(_idxInit(sorted_used));

          //每一项如果全都是1，就说明ssh状态无需更新
          let arr = _used.filter((item) => item.ssh_state !== 0);
          setIsSSHChecked(arr.length == 0);
        //});
      // })
      // .catch((e) => console.log(e))
      // .finally(() => {
      //   //setCheckedList([]);
      //   setLoading(false);
      // });
  }

  const onSubmit = () => {
    fetchData(pagination);
  };

  //删除操作待自测
  const operationMachine = (queryMethod, data) => {
    setLoading(true);
    if (queryMethod == "delete") {
      fetchDelete(apiRequest.machineManagement.deleteOperation, {
        body: {
          ids: Object.keys(checkedList)
            .map((k) => checkedList[k])
            .flat(1)
            .map((item) => item.id),
        },
      })
        .then((res) => {
          res = res.data;
          // 再调用一次列表
          handleResponse(res, () => {
            //console.log(res);
            if (res.code === 0) {
              // setSearchData([]);
              // setSearchValue("");
              fetchData(pagination);
            }
          });
        })
        .catch((e) => console.log(e))
        .finally(() => {
          setCheckedList({});
          setLoading(false);
          setDeleteModalVisible(false);
        });
    } else if (queryMethod == "post") {
      delete data.passwordAgain;
      fetchPost(apiRequest.machineManagement.operation, {
        body: {
          ...data,
          //env_id: Number(updata()().value),
        },
      })
        .then((res) => {
          res = res.data;
          // 再调用一次列表
          handleResponse(res, () => {
            //console.log(res);
            if (res.code === 0) {
              setSearchData([]);
              setSearchValue("");
              fetchData(pagination);
            }
          });
        })
        .catch((e) => console.log(e))
        .finally(() => {
          setCheckedList({});
          setLoading(false);
          setAddMoadlVisible(false);
        });
    }
  };

  useEffect(() => {
    fetchData(pagination);
  }, []);

  const disabled =
    Object.keys(checkedList)
      .map((k) => checkedList[k])
      .flat(1).length == 0;

  return (
    <OmpContentWrapper>
      {/* <OmpCollapseWrapper
        form={form}
        onReset={() => {
          fetchData(pagination);
          setCheckedList({});
        }}
        onFinish={onSubmit}
        initialValues={{
          alert_ip: location.state?.host_ip,
        }}
        operation={
          <>
            <div>
              <Button type="primary" onClick={() => fetchData(pagination)}
                icon={<ReloadOutlined style={{fontSize:12,position:"relative",top:-1}} />}
              >
              刷新
            </Button>
              <Dropdown
                //placement="bottomLeft"
                overlay={
                  <Menu>
                    <Menu.Item
                      style={{ textAlign: "center" }}
                      onClick={() => setDeleteModalVisible(true)}
                      disabled={disabled}
                    >
                      删除
                    </Menu.Item>
                    <Menu.Item
                      style={{ textAlign: "center" }}
                      type="primary"
                      onClick={() => {
                        setAddMoadlVisible(true);
                        //setAddMachineForm({});
                      }}
                    >
                      添加
                    </Menu.Item>
                    <Menu.Item
                      style={{ textAlign: "center" }}
                      disabled={disabled}
                      onClick={() => {
                        // const ipArr = R.flatten(
                        //   R.map(
                        //     (item) => R.values(R.pick(["ip"], item)),
                        //     R.filter((item) => item.agent_state === 2, checkedList)
                        //   )
                        // );
                        // console.log(checkedList);
                        //不是0，不是1就发
                        // ssh状态不能是1
                        let newArr = Object.keys(checkedList)
                          .map((k) => checkedList[k])
                          .flat(1)
                          .map((item) => item.ip);
                        setLoading(true);
                        fetchPost(apiRequest.machineManagement.deploy, {
                          body: {
                            ip_list: newArr,
                            // env_id: Number(updata()().value),
                          },
                        })
                          .then((res) => {
                            res = res.data;
                            handleResponse(res);
                            if (res.code == 0) fetchData(pagination);
                          })
                          .catch((e) => console.log(e))
                          .finally(() => {
                            //console.log("进来了")
                            setLoading(false);
                          });
                      }}
                    >
                      Agent下发
                    </Menu.Item>

                    <Menu.Item
                      style={{ textAlign: "center" }}
                      disabled={isSSHChecked}
                      //type="primary"
                      onClick={() => {
                        message.success("开始查询更新ssh状态");
                        //setIsSSHChecked(true);
                        fetchPost(apiRequest.machineManagement.sshCheck)
                          .then((res) => {
                            res = res.data;
                            handleResponse(res, () => fetchData(pagination));
                          })
                          .catch((e) => console.log(e))
                          .finally(() => {});
                      }}
                    >
                      更新SSH状态
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
            </div>
          </>
        }
      >
        <Input name="alert_ip123" label="IP地址" placeholder="请选择IP地址" />
        <Select name="alert_level" label="SSH状态" placeholder="请选择SSH状态">
          <Select.Option value="critical">启用</Select.Option>
          <Select.Option value="warning">警告</Select.Option>
        </Select>
        <Select name="mode" label="Agent状态" placeholder="请选择Agent状态">
          <Select.Option value="zhengchang">正常</Select.Option>
          <Select.Option value="数据中心">数据中心</Select.Option>
        </Select>
      </OmpCollapseWrapper> */}
      <Button type="primary" onClick={()=>{
        setAddMoadlVisible(true)
      }}>添加</Button>
      <Button style={{marginLeft:10}} onClick={()=>{
          dispatch(refreshTime())
      }}>刷新</Button>
      <div
        style={{
          border: "1px solid #ebeef2",
          // paddingLeft: 10,
          // paddingRight: 10,
          //marginBottom:200,
          backgroundColor: "white",
          marginTop:10
        }}
      >
        <OmpTable
          loading={loading}
          //scroll={{y:'calc(100vh - 520px)'}}
          onChange={(e) => fetchData(e)}
          columns={columns}
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
          rowClassName={styles.machineTable}
          expandRowByClick={true}
          expandIconColumnIndex={-1}
          expandIconAsCell={false}
          expandedRowRender={(record) => {
            return (
              <p className={styles.antdTableExpandedRow}>
                <span>操作系统:{record["operating_system"]}</span>
                <span>配置信息:{renderInformation(null, record)}</span>
                <span>
                  运行时长:{renderFormattedTime(record["running_time"])}
                </span>
              </p>
            );
          }}
        />
      </div>
      {/* <OmpMessageModal
        visibleHandle={[deleteModalVisible, setDeleteModalVisible]}
        title="删除"
        loading={loading}
        onFinish={() => {
          operationMachine("delete");
          //console.log(checkedList);
          //serviceOperation("start");
        }}
      >
        <div>
          是否确认 <span style={{ color: "#ed5b56" }}>删除</span> 所选 主机 (共
          {
            Object.keys(checkedList)
              .map((k) => checkedList[k])
              .flat(1).length
          }
          个) ？
          <p style={{ position: "relative", top: 10, fontSize: 13 }}>
            <WarningFilled
              style={{
                fontSize: 16,
                color: "rgba(247, 207, 54)",
                marginRight: 10,
              }}
            />
            执行此操作会导致该主机下的<span style={{ color: "#ed5b56" }}></span>
            服务被删除！
          </p>
        </div>
      </OmpMessageModal> */}
      <AddMachineModal 
        loading={loading}
        visibleHandle={[addModalVisible, setAddMoadlVisible]}
        onFinish={operationMachine}
      />
    </OmpContentWrapper>
  );
};

export default MachineManagement;
