import {
  Button,
  Modal,
  Upload,
  message,
  Steps,
  Tooltip,
  Select,
  Switch,
} from "antd";
import { useEffect, useRef, useState } from "react";
import { CopyOutlined } from "@ant-design/icons";
//import BMF from "browser-md5-file";
import { fetchPost, fetchGet } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { handleResponse } from "@/utils/utils";
import { OmpMessageModal, OmpTable } from "@/components";
import { useHistory, useLocation } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { getStep1ChangeAction } from "./Installation/store/actionsCreators";
import { getUniqueKeyChangeAction } from "../store/actionsCreators";

const BatchInstallationModal = ({
  bIModalVisibility,
  setBIModalVisibility,
  dataSource,
  installTitle,
}) => {
  const uniqueKey = useSelector((state) => state.appStore.uniqueKey);

  const reduxDispatch = useDispatch();

  const [loading, setLoading] = useState(false);

  const history = useHistory();

  //选中的数据
  const [checkedList, setCheckedList] = useState({});
  // console.log(checkedList)
  //应用服务选择的版本号
  const versionInfo = useRef({});

  const columns = [
    {
      title: "名称",
      key: "name",
      dataIndex: "name",
      align: "center",
      ellipsis: true,
      width: 80,
      render: (text, record) => {
        return text;
      },
    },
    {
      title: "版本",
      key: "version",
      dataIndex: "version",
      align: "center",
      ellipsis: true,
      width: 120,
      render: (text, record) => {
        return (
          <Select
            bordered={false}
            defaultValue={text[0]}
            style={{ width: 120 }}
            onSelect={(v) => {
              versionInfo.current[record.name] = v;
            }}
          >
            {text.map((item) => {
              return (
                <Select.Option value={item} key={`${item}-${record.name}`}>
                  {item}
                </Select.Option>
              );
            })}
          </Select>
        );
      },
    },
  ];

  // 高可用是否开启
  const [highAvailabilityCheck, setHighAvailabilityCheck] = useState(false);

  // 批量安装/服务安装选择确认请求
  const createInstallInfo = (install_product) => {
    setLoading(true);
    fetchPost(apiRequest.appStore.createInstallInfo, {
      body: {
        high_availability: highAvailabilityCheck,
        install_product: install_product,
        unique_key: uniqueKey,
      },
    })
      .then((res) => {
        //console.log(operateObj[operateAciton])
        handleResponse(res, (res) => {
          if (res.data && res.data.data) {
            reduxDispatch(getStep1ChangeAction(res.data.data));
          }
          history.push("/application_management/app_store/installation");
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  // 组件安装
  const createComponentInstallInfo = (install_product) => {
    setLoading(true);
    fetchPost(apiRequest.appStore.createComponentInstallInfo, {
      body: {
        high_availability: highAvailabilityCheck,
        install_component: install_product,
      },
    })
      .then((res) => {
        //console.log(operateObj[operateAciton])
        handleResponse(res, (res) => {
          if (res.data && res.data.data) {
            reduxDispatch(getStep1ChangeAction(res.data.data));
            reduxDispatch(getUniqueKeyChangeAction(res.data.unique_key));
          }
          history.push("/application_management/app_store/installation");
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    setCheckedList({
      data: dataSource.filter(item=>item.is_continue),
    });
  }, [dataSource]);
  // console.log(checkedList)
  return (
    <Modal
      title={
        <span>
          <span style={{ position: "relative", left: "-10px" }}>
            <CopyOutlined />
          </span>
          <span>
            {installTitle == "服务"
              ? "服务安装-选择版本"
              : installTitle == "组件"
              ? "组件安装-选择版本"
              : "批量安装-选择应用服务"}
          </span>
        </span>
      }
      afterClose={() => {
        setCheckedList({});
      }}
      onCancel={() => {
        setBIModalVisibility(false);
      }}
      visible={bIModalVisibility}
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
        <div style={{ border: "1px solid rgb(235, 238, 242)" }}>
          <OmpTable
            size="small"
            scroll={{ y: 270 }}
            loading={loading}
            //scroll={{ x: 1900 }}
            columns={columns}
            dataSource={dataSource}
            rowKey={(record) => {
              return record.name;
            }}
            checkedState={[checkedList, setCheckedList]}
            pagination={false}
            notSelectable={(record) => ({
              // is_continue的不能选中
              disabled: !record.is_continue,
            })}
            rowSelection={{
              selectedRowKeys: Object.keys(checkedList)
                .map((k) => checkedList[k])
                .flat(1)
                .map((item) => item?.name),
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
          <div style={{ display: "flex", alignItems: "center" }}>
            高可用
            <Switch
              style={{ marginLeft: 10 }}
              checked={highAvailabilityCheck}
              onChange={(e) => {
                setHighAvailabilityCheck(e);
              }}
            />
          </div>
          <div style={{ display: "flex" }}>
            <div style={{ marginRight: 15 }}>
              已选择{" "}
              {
                Object.keys(checkedList)
                  .map((k) => checkedList[k])
                  .flat(1).length
              }{" "}
              个
            </div>
            <div>共 {dataSource.length} 个</div>
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
            <Button onClick={() => setBIModalVisibility(false)}>取消</Button>
            <Button
              type="primary"
              style={{ marginLeft: 16 }}
              loading={loading}
              disabled={
                Object.keys(checkedList)
                  .map((k) => checkedList[k])
                  .flat(1).length == 0
              }
              onClick={() => {
                if (installTitle == "组件") {
                  let install_product = checkedList.data.map((item) => {
                    return {
                      name: item.name,
                      version:
                        versionInfo.current[item.name] || item.version[0],
                    };
                  });
                  createComponentInstallInfo(install_product);
                } else {
                  let install_product = checkedList.data.map((item) => {
                    return {
                      name: item.name,
                      version:
                        versionInfo.current[item.name] || item.version[0],
                    };
                  });
                  createInstallInfo(install_product);
                  // history.push("/application_management/app_store/installation")
                }
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

export default BatchInstallationModal;
