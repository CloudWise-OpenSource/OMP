import { Button, Modal, Input, Table, Tooltip, Form, Spin } from "antd";
import { useEffect, useState } from "react";
import {
  CopyOutlined,
  SearchOutlined,
  PlusSquareOutlined,
  FormOutlined,
} from "@ant-design/icons";

export const AddCustomModal = ({
  customModalType,
  addCustom,
  loading,
  modalForm,
  addModalVisibility,
  setAddModalVisibility,
  updateCustomInfo,
  setUpdateCustomData,
}) => {
  return (
    <Modal
      width={580}
      onCancel={() => {
        setAddModalVisibility(false);
        setUpdateCustomData({});
        modalForm.setFieldsValue({ field_k: "", field_v: "", notes: "" });
      }}
      visible={addModalVisibility}
      title={
        <span>
          <span style={{ position: "relative", left: "-10px" }}>
            {customModalType === "add" ? (
              <PlusSquareOutlined />
            ) : (
              <FormOutlined />
            )}
          </span>
          <span>
            {customModalType === "add" ? "添加自定义参数" : "编辑自定义参数"}
          </span>
        </span>
      }
      zIndex={1004}
      footer={null}
      destroyOnClose
    >
      <Spin spinning={loading}>
        <Form
          name="custom"
          labelCol={{ span: 4 }}
          wrapperCol={{ span: 18 }}
          onFinish={(data) => {
            if (customModalType === "add") {
              addCustom(data);
            } else {
              updateCustomInfo(data);
            }
          }}
          form={modalForm}
          initialValues={{
            field_k: "",
            field_v: "",
            notes: "",
          }}
        >
          <Form.Item
            label="参数名称"
            name="field_k"
            key="field_k"
            rules={[
              {
                required: true,
                message: "请输入参数名称",
              },
            ]}
          >
            <Input
              placeholder={"请输入参数名称"}
              disabled={customModalType === "update"}
              maxLength={64}
            />
          </Form.Item>

          <Form.Item
            label="参数值"
            name="field_v"
            key="field_v"
            rules={[
              {
                required: true,
                message: "请输入参数值",
              },
            ]}
          >
            <Input.TextArea
              rows={4}
              style={{ width: 480 }}
              placeholder={"请输入参数值"}
              maxLength={256}
            />
          </Form.Item>

          <Form.Item label="备注" name="notes" key="notes">
            <Input placeholder={"请输入备注"} maxLength={32} />
          </Form.Item>

          <Form.Item
            wrapperCol={{ span: 24 }}
            style={{ textAlign: "center", position: "relative", top: 10 }}
          >
            <Button
              style={{ marginRight: 16 }}
              onClick={() => {
                setAddModalVisibility(false);
                setUpdateCustomData({});
                modalForm.setFieldsValue({
                  field_k: "",
                  field_v: "",
                  notes: "",
                });
              }}
            >
              取消
            </Button>
            <Button type="primary" htmlType="submit">
              确定
            </Button>
          </Form.Item>
        </Form>
      </Spin>
    </Modal>
  );
};

export const CustomModal = ({
  modalVisibility,
  setModalVisibility,
  modalLoading,
  customData,
  setCustomData,
  initData,
  setCustomModalType,
  setAddModalVisibility,
  deleteCustomInfo,
  modalForm,
  setRow,
}) => {
  const [searchName, setSearchName] = useState("");

  const columns = [
    {
      title: "序号",
      key: "_idx",
      dataIndex: "_idx",
      align: "center",
      ellipsis: true,
      width: 40,
      render: (text, record) => {
        return text;
      },
    },
    {
      title: "名称",
      key: "field_k",
      dataIndex: "field_k",
      align: "center",
      ellipsis: true,
      width: 80,
      render: (text, record) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
    },
    {
      title: "值",
      key: "field_v",
      dataIndex: "field_v",
      align: "center",
      ellipsis: true,
      width: 150,
    },
    {
      title: "备注",
      key: "notes",
      dataIndex: "notes",
      align: "center",
      ellipsis: true,
      width: 100,
      render: (text, record) => {
        return (
          <Tooltip title={text}>
            <span>{text ? text : "-"}</span>
          </Tooltip>
        );
      },
    },
    {
      title: "操作",
      width: 60,
      key: "",
      dataIndex: "",
      align: "center",
      render: (text, record) => {
        return (
          <div
            onClick={() => setRow(record)}
            style={{ display: "flex", justifyContent: "space-around" }}
          >
            <div style={{ margin: "auto" }}>
              <a
                onClick={() => {
                  setCustomModalType("update");
                  setAddModalVisibility(true);
                  modalForm.setFieldsValue({
                    field_k: record.field_k,
                    field_v: record.field_v,
                    notes: record.notes,
                  });
                }}
              >
                编辑
              </a>

              <a
                style={{ marginLeft: 10 }}
                onClick={() => deleteCustomInfo(record.id)}
              >
                删除
              </a>
            </div>
          </div>
        );
      },
    },
  ];

  useEffect(() => {}, []);

  return (
    <Modal
      title={
        <span>
          <span style={{ position: "relative", left: "-10px" }}>
            <CopyOutlined />
          </span>
          <span>自定义参数</span>
        </span>
      }
      width={860}
      onCancel={() => {
        setModalVisibility(false);
      }}
      visible={modalVisibility}
      footer={null}
      //width={1000}
      bodyStyle={{
        paddingLeft: 30,
        paddingRight: 30,
        marginTop: -10,
      }}
      destroyOnClose
      zIndex={1002}
    >
      <Spin spinning={modalLoading}>
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
                  setCustomData(initData);
                }
              }}
              onPressEnter={() => {
                setCustomData(
                  initData.filter((i) => i.field_k.includes(searchName))
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
              }}
            >
              <Button
                type="primary"
                onClick={() => {
                  setCustomModalType("add");
                  setAddModalVisibility(true);
                }}
              >
                添加参数
              </Button>
            </div>
          </div>
        </div>
        <div>
          <div style={{ border: "1px solid rgb(235, 238, 242)" }}>
            <Table
              size="small"
              scroll={{ y: 270 }}
              columns={columns}
              dataSource={customData}
              rowKey={(record) => {
                return record.id;
              }}
              pagination={false}
            />
          </div>
          <div
            style={{ display: "flex", justifyContent: "center", marginTop: 20 }}
          >
            <Button onClick={() => setModalVisibility(false)}>返回</Button>
          </div>
        </div>
      </Spin>
    </Modal>
  );
};
