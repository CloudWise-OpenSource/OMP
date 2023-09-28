import { Button, Modal, Input, Select } from "antd";
import { useEffect, useRef, useState } from "react";
import { CopyOutlined, SearchOutlined } from "@ant-design/icons";
//import BMF from "browser-md5-file";
import { fetchPost } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { handleResponse } from "@/utils/utils";
import { OmpTable } from "@/components";
import { useHistory } from "react-router-dom";

const GetServiceModal = ({
  modalVisibility,
  setModalVisibility,
  initData,
  dataSource,
  setDataSource,
  initLoading,
}) => {
  const [loading, setLoading] = useState(false);

  const history = useHistory();

  //选中的数据
  const [checkedList, setCheckedList] = useState([]);

  //应用服务选择的版本号
  const versionInfo = useRef({});

  const [searchName, setSearchName] = useState("");

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
        if (typeof text === "string") {
          return text;
        } else if (text.length === 1) {
          return text[0];
        } else {
          return (
            <Select
              defaultValue={text[0]}
              style={{ width: 120, textAlign: "left" }}
              onSelect={(newVersion) => {
                const oldVersion =
                  versionInfo.current[record.name] || record.version[0];
                versionInfo.current[record.name] = newVersion;
                // 如果版本发生变化，改变数据，清空选中，关闭展开
                if (oldVersion != newVersion) {
                  for (let i = 0; i < dataSource.length; i++) {
                    const element = dataSource[i];
                    if (
                      element.name === record.name &&
                      element.hasOwnProperty("child")
                    ) {
                      element.children = element.child[newVersion];

                      let arr = element.child[oldVersion].map((i) => i.name);
                      arr = [...arr, record.name];
                      setCheckedList(
                        checkedList.filter((i) => arr.indexOf(i.name) === -1)
                      );
                    }
                  }
                }
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
        }
      },
    },
  ];

  const checkServiceData = () => {
    // setLoading(true);
    const copyCheckData = [...checkedList];
    // 处理选中数据

    const childArr = copyCheckData.filter((i) => typeof i.version === "string");

    const resData = copyCheckData
      .filter((i) => typeof i.version !== "string")
      .map((i) => {
        const version = versionInfo.current[i.name] || i.version[0];
        const itemData = {
          name: i.name,
          version: [version],
        };
        if (i.hasOwnProperty("child")) {
          const childOjb = {};
          childOjb[version] = i.child[version]?.filter(
            (i) => childArr.indexOf(i) !== -1
          );
          itemData.child = childOjb;
        }
        return itemData;
      });
    fetchPost(apiRequest.appStore.queryAppList, {
      body: {
        data: resData,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          setLoading(false);
          if (res.data) {
            history.push({
              pathname: "/application_management/get-service",
              state: {
                getServiceData: res.data,
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

  useEffect(() => {}, []);

  return (
    <Modal
      title={
        <span>
          <span style={{ position: "relative", left: "-10px" }}>
            <CopyOutlined />
          </span>
          <span>选择纳管服务</span>
        </span>
      }
      afterClose={() => {
        setCheckedList([]);
        versionInfo.current = {};
      }}
      onCancel={() => {
        setModalVisibility(false);
      }}
      visible={modalVisibility}
      footer={null}
      //width={1000}
      loading={loading}
      bodyStyle={{
        paddingLeft: 30,
        paddingRight: 30,
        marginTop: -10,
      }}
      destroyOnClose
    >
      <div
        style={{
          display: "flex",
          marginBottom: 10,
        }}
      >
        <div style={{ flex: 1 }}>
          <Input
            placeholder="请输入名称"
            suffix={<SearchOutlined style={{ color: "#b6b6b6" }} />}
            style={{
              width: 220,
            }}
            value={searchName}
            onChange={(e) => {
              setSearchName(e.target.value);
              if (e.target.value === "") {
                setDataSource(initData);
              }
            }}
            onPressEnter={() => {
              setDataSource(
                initData.filter((i) => i.name.includes(searchName))
              );
            }}
          />
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            flex: 1,
            textAlign: "right",
          }}
        >
          <div
            style={{
              display: "flex",
              width: "100%",
              justifyContent: "flex-end",
              paddingTop: 6,
            }}
          >
            <div style={{ marginRight: 10 }}>
              已选择{" "}
              {checkedList.filter((i) => typeof i.version !== "string").length}{" "}
              个
            </div>
          </div>
        </div>
      </div>
      <div>
        <div style={{ border: "1px solid rgb(235, 238, 242)" }}>
          <OmpTable
            size="small"
            scroll={{ y: 270 }}
            loading={loading || initLoading}
            //scroll={{ x: 1900 }}
            columns={columns}
            dataSource={dataSource}
            rowKey={(record) => {
              return record.name;
            }}
            checkedState={[checkedList, setCheckedList]}
            pagination={false}
            rowSelection={{
              selectedRowKeys: checkedList?.map((item) => item?.name),
              onSelect: (record, selected, selectedRows, nativeEvent) => {
                if (selected) {
                  // 如果有子项则全部选中
                  let childArr = [];
                  if (record.hasOwnProperty("child")) {
                    const version =
                      versionInfo.current[record.name] || record.version[0];
                    childArr = record.child[version];
                  }
                  // 如果有父则选中
                  let fatherArr = [];
                  if (typeof record.version === "string") {
                    for (let i = 0; i < dataSource.length; i++) {
                      const element = dataSource[i];
                      if (element.hasOwnProperty("child")) {
                        const version =
                          versionInfo.current[element.name] ||
                          element.version[0];
                        if (element.child[version].indexOf(record) !== -1) {
                          fatherArr.push(element);
                          break;
                        }
                      }
                    }
                  }
                  setCheckedList(
                    Array.from(
                      new Set([
                        ...checkedList,
                        ...childArr,
                        ...fatherArr,
                        record,
                      ])
                    )
                  );
                } else {
                  let arr = [record.name];
                  if (record.hasOwnProperty("child")) {
                    const version =
                      versionInfo.current[record.name] || record.version[0];
                    arr = [...arr, ...record.child[version].map((i) => i.name)];
                  }
                  setCheckedList(
                    checkedList.filter((i) => arr.indexOf(i.name) === -1)
                  );
                }
              },
              onSelectAll: (selected, selectedRows, changeRows) => {
                if (selected) {
                  let resArr = [];
                  if (
                    !(changeRows.length === 1 && changeRows[0] === undefined)
                  ) {
                    for (let i = 0; i < dataSource.length; i++) {
                      const element = dataSource[i];
                      resArr.push(element);
                      const version =
                        versionInfo.current[element.name] || element.version[0];

                      if (element.hasOwnProperty("child")) {
                        resArr = [...resArr, ...element.child[version]];
                      }
                    }
                  }
                  setCheckedList(Array.from(new Set(resArr)));
                } else {
                  setCheckedList([]);
                }
              },
            }}
          />
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
            <Button onClick={() => setModalVisibility(false)}>取消</Button>
            <Button
              type="primary"
              style={{ marginLeft: 16 }}
              loading={loading || initLoading}
              disabled={checkedList.length == 0}
              onClick={() => {
                checkServiceData();
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

export default GetServiceModal;
