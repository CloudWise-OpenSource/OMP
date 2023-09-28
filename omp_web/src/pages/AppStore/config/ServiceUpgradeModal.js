import {
  Button,
  Modal,
  Upload,
  message,
  Steps,
  Tooltip,
  Select,
  Switch,
  Input,
  Table,
} from "antd";
import { useEffect, useRef, useState } from "react";
import { CopyOutlined, SearchOutlined, ArrowUpOutlined } from "@ant-design/icons";
//import BMF from "browser-md5-file";
import { fetchPost, fetchGet } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { handleResponse } from "@/utils/utils";
import { useHistory } from "react-router-dom";

const ServiceUpgradeModal = ({
  sUModalVisibility,
  setSUModalVisibility,
  // dataSource,
  installTitle,
  initLoading,
}) => {
  const [loading, setLoading] = useState(false);

  const [selectValue, setSelectValue] = useState();

  const [rows, setRows] = useState([]);

  const history = useHistory();

  //选中的数据
  const [checkedList, setCheckedList] = useState([]);
  // console.log(checkedList)
  //应用服务选择的版本号
  const versionInfo = useRef({});

  const lock = useRef(false);

  const columns = [
    {
      title: "名称",
      key: "instance_name",
      dataIndex: "instance_name",
      // align: "center",
      ellipsis: true,
      width: 150,
      render: (text, record) => {
        return (
          <Tooltip title={text}>
            <div style={{ paddingTop: 2 }}>{text}</div>
          </Tooltip>
        );
      },
    },
    {
      title: "当前版本",
      key: "version",
      dataIndex: "version",
      align: "center",
      ellipsis: true,
      width: 120,
      render: (text, record) => {
        let v =  text || "-";
        return (
          <Tooltip title={v}>
            <div style={{ paddingTop: 2 }}>{v}</div>
          </Tooltip>
        );
      },
    },
    {
      title: "升级版本",
      key: "can_upgrade",
      dataIndex: "can_upgrade",
      align: "center",
      ellipsis: true,
      width: 120,
      render: (text, record) => {
        let v =  text[0].app_version || "-";
        return (
          <Tooltip title={v}>
            <div style={{ paddingTop: 2 }}>{v}</div>
          </Tooltip>
        );
      },
    },
  ];

  const [dataSource, setDataSource] = useState([]);
  const [allLength, setAllLength] = useState(0)

  const queryDataList = (search) => {
    // setRows([]);
    // setCheckedList([]);
    setLoading(true);
    fetchGet(apiRequest.appStore.canUpgrade, {
      params: {
        search: search,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          let result = formatResData(res.data.results)
          if(!search || search == undefined){
            setAllLength(result.map((i) => i.children).flat().length)
          }
          setDataSource(result);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  const formatResData = (data = []) => {
    console.log(data);
    // 遍历数据添加key以及判断父级数据的当前版本
    // （当其子项的当前版本全部一致时设置父级数据版本为此值）
    let result = data.map((item) => {
      let currentVersion = "-";
      let can_upgrade = [item.can_upgrade];
      let c = Array.from(
        new Set(
          item.children.map((i, idx) => {
            item.children[idx].key = item.children[idx].instance_name;
            item.children[idx].id = item.children[idx].instance_name;
            item.children[idx].isChildren = item.app_name;
            return i.version;
          })
        )
      );
      c.length == 1 && (currentVersion = c[0]);
      return {
        ...item,
        version: currentVersion,
        can_upgrade: can_upgrade,
        instance_name: item.app_name,
        id: item.app_name || item.instance_name,
        key: item.app_name || item.instance_name,
      };
    });
    return result;
  };

  // 组件的checkedList并不能很好的对应业务数据需求，封装函数进行转换
  const formatCheckedListData = (data) => {
    return data.filter((item) => {
      return item.isChildren;
    });
  };

  // 升级命令下发
  const doUpgrade = (checkedList) => {
    setLoading(true);
    fetchPost(apiRequest.appStore.doUpgrade, {
      body: {
        choices: checkedList.map((item) => ({
          app_id: item.can_upgrade[0].app_id,
          service_id: item.service_id,
        })),
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.code == 0) {
            history.push({
              pathname: "/application_management/app_store/service_upgrade",
              state: {
                history: res.data.history
              },
            });
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    sUModalVisibility && queryDataList();
  }, [sUModalVisibility]);

  return (
    <Modal
      title={
        <span>
          <span style={{ position: "relative", left: "-10px" }}>
            <ArrowUpOutlined />
          </span>
          <span>服务升级-选择应用服务</span>
        </span>
      }
      width={600}
      afterClose={() => {
        setRows([]);
        setCheckedList([]);
      }}
      onCancel={() => {
        setSUModalVisibility(false);
      }}
      visible={sUModalVisibility}
      footer={null}
      //width={1000}
      loading={loading}
      bodyStyle={{
        paddingLeft: 30,
        paddingRight: 30,
      }}
      destroyOnClose
    >
      <div>
        <div style={{ display: "flex", marginLeft: "290px", marginBottom: 15 }}>
          <span
            style={{
              width: 70,
              display: "flex",
              alignItems: "center",
              fontSize: 14,
            }}
          >
            服务名称:
          </span>
          <Input
            placeholder="请输入服务名称"
            style={{ width: 180 }}
            allowClear
            // size="small"
            value={selectValue}
            onChange={(e) => {
              setSelectValue(e.target.value);
              if (!e.target.value) {
                queryDataList();
              }
            }}
            onBlur={() => {
              queryDataList(selectValue);
            }}
            onPressEnter={() => {
              queryDataList(selectValue);
            }}
            suffix={
              !selectValue && (
                <SearchOutlined style={{ fontSize: 12, color: "#b6b6b6" }} />
              )
            }
          />
        </div>
        <div style={{ border: "1px solid rgb(235, 238, 242)" }}>
          <Table
            size="small"
            scroll={{ y: 295 }}
            loading={loading || initLoading}
            //scroll={{ x: 1900 }}
            columns={columns}
            dataSource={dataSource}
            pagination={false}
            // notSelectable={(record) => ({
            //   // is_continue的不能选中
            //   disabled: !record.is_continue,
            // })}
            rowSelection={{
              onChange: (selectedRowKeys, selectedRows, select, lll) => {
                // 全选动作交给onchange事件
                if (lock.current) {
                  setRows(selectedRowKeys);
                  setCheckedList(formatCheckedListData(selectedRows));
                  // 关闭锁，下次事件触发时优先使用onselect处理rowkey变更
                  lock.current = false;
                }
              },
              selectedRowKeys: rows,
              onSelect: (record, selected, selectedRows) => {
                if (record.isChildren) {
                  if (selected) {
                    for (const item of dataSource) {
                      if (item.instance_name == record.isChildren) {
                        let results = item.children.filter(
                          (i) => i.ip == record.ip
                        );
                        // results是当前点击要变动的
                        // row中原本的数据不应该改变
                        // row原本数据不改变,考虑到每次都是直接选中全部ip的项，也不会出现选中已经选中项的情况
                        setRows((r) => {
                          return [...r, ...results.map((k) => k.instance_name)];
                        });
                        setCheckedList((checks) => {
                          return formatCheckedListData([...checks, ...results]);
                        });
                        break;
                      }
                    }
                  } else {
                    // 删除掉和record 父级和ip一样的项
                    let checkedListCopy = JSON.parse(
                      JSON.stringify(checkedList)
                    );
                    let results = formatCheckedListData(
                      checkedListCopy.filter(
                        (i) =>
                          i.ip !== record.ip ||
                          i.isChildren !== record.isChildren
                      )
                    );

                    setRows(results.map((i) => i.instance_name));
                    setCheckedList(results);
                  }
                } else {
                  // 打开锁，使用onchange事件处理rowkey变更
                  lock.current = true;
                }
              },
              onSelectAll: (selected, selectedRows, changeRows) => {
                // 打开锁，使用onchange事件处理rowkey变更
                lock.current = true;
              },
              checkStrictly: false,
            }}
          />
        </div>
        <div
          style={{
            display: "flex",
            marginTop: 20,
            justifyContent: "space-between",
            padding: "0px 20px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center" }}></div>
          <div style={{ display: "flex" }}>
            <div style={{ marginRight: 15 }}>
              已选择 {checkedList.length} 个
            </div>
            <div>共 {allLength} 个</div>
          </div>
        </div>
        <div
          style={{ display: "flex", justifyContent: "center", marginTop: 30 }}
        >
          <div
            style={{
              width: 170,
              display: "flex",
              justifyContent: "space-between",
            }}
          >
            <Button onClick={() => setSUModalVisibility(false)}>取消</Button>
            <Button
              type="primary"
              style={{ marginLeft: 16 }}
              loading={loading || initLoading}
              disabled={checkedList.length == 0}
              onClick={() => {
                doUpgrade(checkedList);
              }}
            >
              确认选择
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  );
};

export default ServiceUpgradeModal;
