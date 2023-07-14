import {
  Button,
  Modal,
  Divider,
  Form,
  InputNumber,
  Spin,
  Switch,
  Select,
} from "antd";
import { PlusSquareOutlined, FormOutlined } from "@ant-design/icons";

export const AddStrategyModal = ({
  strategyModalType,
  addStrategy,
  updateStrategy,
  loading,
  modalForm,
  addModalVisibility,
  setAddModalVisibility,
  canHealingIns,
  strategyFormInit,
  keyArr,
  setKeyArr,
}) => {
  return (
    <Modal
      style={{ marginTop: 10 }}
      width={600}
      onCancel={() => {
        setAddModalVisibility(false);
        setKeyArr([]);
        modalForm.setFieldsValue(strategyFormInit);
      }}
      visible={addModalVisibility}
      title={
        <span>
          <span style={{ position: "relative", left: "-10px" }}>
            {strategyModalType === "add" ? (
              <PlusSquareOutlined />
            ) : (
              <FormOutlined />
            )}
          </span>
          <span>
            {strategyModalType === "add" ? "添加自愈策略" : "编辑自愈策略"}
          </span>
        </span>
      }
      zIndex={1004}
      footer={null}
      destroyOnClose
    >
      <Spin spinning={loading}>
        <Form
          name="strategy"
          labelCol={{ span: 4 }}
          wrapperCol={{ span: 18 }}
          onFinish={(data) => {
            if (strategyModalType === "add") {
              addStrategy(data);
            } else {
              updateStrategy(data);
            }
          }}
          form={modalForm}
          initialValues={strategyFormInit}
        >
          {/* <Form.Item
            label="自愈实例"
            name="repair_instance"
            key="repair_instance"
            rules={[
              {
                required: true,
                message: "自愈实例",
              },
            ]}
          >
            <Select
              mode="multiple"
              placeholder="请选择自愈实例"
              allowClear
              maxTagCount="responsive"
              onChange={(e) => setKeyArr(e)}
              dropdownRender={(menu) => (
                <div>
                  {menu}
                  <Divider
                    style={{
                      marginTop: 2,
                      marginBottom: 5,
                    }}
                  />
                  <Button
                    size="small"
                    type="primary"
                    disabled={canHealingIns?.service_name?.length === 0}
                    style={{ marginLeft: 10 }}
                    onClick={() => {
                      modalForm.setFieldsValue({
                        repair_instance: canHealingIns.service_name,
                      });
                      setKeyArr(canHealingIns.service_name);
                    }}
                  >
                    全选
                  </Button>
                  <span style={{ float: "right", marginRight: 10 }}>
                    已选 {keyArr.length} 个
                  </span>
                </div>
              )}
            >
              <Select.Option
                key="all"
                value="all"
                disabled={
                  !canHealingIns.all ||
                  (keyArr.length !== 0 && keyArr[0] !== "all")
                }
              >
                所有服务
              </Select.Option>
              {canHealingIns.service_name?.map((e) => {
                return (
                  <Select.Option
                    key={e}
                    value={e}
                    disabled={keyArr.length === 1 && keyArr[0] === "all"}
                  >
                    {e}
                  </Select.Option>
                );
              })}
            </Select>
          </Form.Item> */}
          <Form.Item
            label="自愈维度"
            name="repair_instance"
            key="repair_instance"
            rules={[
              {
                required: true,
                message: "自愈维度",
              },
            ]}
          >
            <Select
              mode="multiple"
              placeholder="请选择自愈维度"
              allowClear
              maxTagCount="responsive"
              // onChange={(e) => setKeyArr(e)}
            >
              <Select.Option key="host" value="host">
                主机监控Agent
              </Select.Option>
              <Select.Option key="component" value="component">
                所有公共组件
              </Select.Option>
              <Select.Option key="service" value="service">
                所有自研服务
              </Select.Option>
            </Select>
          </Form.Item>
          <Form.Item
            label="探测周期"
            name="fresh_rate"
            key="fresh_rate"
            rules={[
              {
                required: true,
                message: "请填写探测周期",
              },
            ]}
          >
            <InputNumber
              min={1}
              max={60}
              style={{
                width: 140,
              }}
              addonAfter="分钟"
            />
          </Form.Item>

          <Form.Item
            label="自愈类型"
            name="instance_tp"
            key="instance_tp"
            rules={[
              {
                required: true,
                message: "请选择自愈类型",
              },
            ]}
          >
            <Select placeholder="自愈类型" style={{ width: 140 }}>
              <Select.Option key="start" value={0}>
                启动 [start]
              </Select.Option>
              <Select.Option key="restart" value={1}>
                重启 [restart]
              </Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="重试次数"
            name="max_healing_count"
            key="max_healing_count"
            rules={[
              {
                required: true,
                message: "请填写重试次数",
              },
            ]}
          >
            <InputNumber
              min={1}
              max={20}
              style={{
                width: 140,
              }}
              addonAfter="次"
            />
          </Form.Item>

          <Form.Item label="开启策略">
            <Form.Item name="used" noStyle valuePropName="checked">
              <Switch style={{ borderRadius: "10px" }} />
            </Form.Item>
          </Form.Item>

          <Form.Item
            wrapperCol={{ span: 24 }}
            style={{ textAlign: "center", position: "relative", top: 10 }}
          >
            <Button
              style={{ marginRight: 16 }}
              onClick={() => {
                setAddModalVisibility(false);
                setKeyArr([]);
                modalForm.setFieldsValue(strategyFormInit);
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
