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

const BatchInstallationModal = ({
  bIModalVisibility,
  setBIModalVisibility,
}) => {
  const [loading, setLoading] = useState(false);

  const history = useHistory();

  const [dataSource, setDataSource] = useState([
    {
      name: "douc",
      id: "douc",
      version: ["5.3.0", "5.3.1"],
    },
    {
      name: "cmdb",
      id: "cmdb",
      version: ["5.3.0", "5.3.1"],
    },
    {
      name: "cmdb1",
      id: "cmdb1",
      version: ["5.3.0", "5.3.1"],
    },
    {
      name: "cmdb2",
      id: "cmdb2",
      version: ["5.3.0", "5.3.1"],
    },
    {
      name: "cmdb3",
      id: "cmdb3",
      version: ["5.3.0", "5.3.1"],
    },
    {
      name: "cmdb4",
      id: "cmdb4",
      version: ["5.3.0", "5.3.1"],
    },
    {
      name: "cmdb5",
      id: "cmdb5",
      version: ["5.3.0", "5.3.1"],
    },
    {
      name: "cmdb6",
      id: "cmdb6",
      version: ["5.3.0", "5.3.1"],
    },
    {
      name: "cmdb11",
      id: "cmdb11",
      version: ["5.3.0", "5.3.1"],
    },
    {
      name: "cmdb22",
      id: "cmdb22",
      version: ["5.3.0", "5.3.1"],
    },
    {
      name: "cmd2b",
      id: "cmd2b",
      version: ["5.3.0", "5.3.1"],
    },
    {
      name: "cmd1b",
      id: "cmd1b",
      version: ["5.3.0", "5.3.1"],
    },

    {
      name: "cmd123b",
      id: "cmd123b",
      version: ["5.3.0", "5.3.1"],
    },
    {
      name: "cm123123db",
      id: "cm123123db",
      version: ["5.3.0", "5.3.1"],
    },
    {
      name: "cm123121233db",
      id: "cm123121233db",
      version: ["5.3.0", "5.3.1"],
    },
    {
      name: "c1admdb",
      id: "c1admdb",
      version: ["5.3.0", "5.3.1"],
    },
  ]);

  //选中的数据
  const [checkedList, setCheckedList] = useState({});

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

  return (
    <Modal
      title={
        <span>
          <span style={{ position: "relative", left: "-10px" }}>
            <CopyOutlined />
          </span>
          <span>批量安装-选择应用服务</span>
        </span>
      }
      afterClose={() => {}}
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
            rowKey={(record) => record.id}
            checkedState={[checkedList, setCheckedList]}
            pagination={false}
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
            <Switch style={{ marginLeft: 10 }} defaultChecked />
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
              //style={{ marginRight: 16 }}
              onClick={() => {
                  history.push("/application_management/app_store/installation")
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
