import { Tag, Modal, Cascader, message } from "antd";
import { useEffect, useRef, useState } from "react";
import {
  SendOutlined,
  LoadingOutlined,
  CheckCircleFilled,
  ScanOutlined,
} from "@ant-design/icons";
//import BMF from "browser-md5-file";
import { fetchPost, fetchGet } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { handleResponse } from "@/utils/utils";

const DeleteServerModal = ({
  deleteServerVisibility,
  setDeleteServerVisibility,
  tabKey,
  refresh,
}) => {
  const [loading, setLoading] = useState(false);

  const [options, setOptions] = useState([]);

  const [resApp, setResApp] = useState([]);

  const [initData, setInitData] = useState([]);

  // 获取可删除选项
  const queryData = () => {
    setLoading(true);
    fetchGet(apiRequest.appStore.deleteServer, {
      params: {
        type: tabKey === "component" ? "component" : "product",
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          setInitData(res.data.data);
          setOptions(
            res.data.data.map((e) => {
              return {
                label: (
                  <>
                    {e.name.includes("|") ? (
                      <>
                        {e.name.split("|")[0]}
                        <span style={{ float: "right", marginLeft: 20 }}>
                          {e.name.split("|")[1]}
                        </span>
                      </>
                    ) : (
                      e.name
                    )}
                  </>
                ),
                value: e.name,
                children: e.versions.map((i) => {
                  return {
                    label: (
                      <>
                        {i.includes("|") ? (
                          <>
                            {i.split("|")[0]}
                            <span style={{ float: "right", marginLeft: 20 }}>
                              {i.split("|")[1]}
                            </span>
                          </>
                        ) : (
                          i
                        )}
                      </>
                    ),
                    value: i,
                  };
                }),
              };
            })
          );
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  // 删除操作
  const doDelete = () => {
    if (resApp.length === 0) {
      message.info("请先选择要删除的服务");
      return;
    }
    const allList = [];
    const someList = {};
    const resData = [];
    for (let i = 0; i < resApp.length; i++) {
      const e = resApp[i];
      if (e.length === 1) {
        allList.push(e[0]);
      } else {
        if (someList.hasOwnProperty(e[0])) {
          someList[e[0]].push(e[1]);
        } else {
          someList[e[0]] = [e[1]];
        }
      }
    }
    for (let i = 0; i < initData.length; i++) {
      const e = initData[i];
      if (allList.includes(e.name)) {
        resData.push(e);
      } else if (someList.hasOwnProperty(e.name)) {
        resData.push({
          name: e.name,
          versions: someList[e.name],
        });
      }
    }
    setLoading(true);
    fetchPost(apiRequest.appStore.deleteServer, {
      body: {
        type: tabKey === "component" ? "component" : "product",
        data: resData,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.code === 0) {
            message.success("删除成功");
            setDeleteServerVisibility(false);
            queryData();
          } else {
            message.warning(res.message);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    queryData();
  }, [tabKey]);

  return (
    <Modal
      zIndex={1000}
      title={
        <span>删除{tabKey === "component" ? "基础组件" : "自研服务"}</span>
      }
      afterClose={() => {
        setResApp([]);
        refresh();
      }}
      onCancel={() => {
        setDeleteServerVisibility(false);
      }}
      visible={deleteServerVisibility}
      width={480}
      confirmLoading={loading}
      okText={loading ? "稍候" : "删除"}
      bodyStyle={{
        paddingLeft: 30,
        paddingRight: 30,
      }}
      destroyOnClose
      onOk={() => doDelete()}
    >
      <div
        style={{
          marginLeft: 10,
          marginBottom: 20,
        }}
      >
        选择服务：
        <Cascader
          style={{
            width: 300,
            marginLeft: 6,
          }}
          options={options}
          onChange={(value) => setResApp(value)}
          multiple
          maxTagCount="responsive"
          placeholder={tabKey === "component" ? "选择基础组件" : "选择自研服务"}
        />
      </div>
    </Modal>
  );
};

export default DeleteServerModal;
