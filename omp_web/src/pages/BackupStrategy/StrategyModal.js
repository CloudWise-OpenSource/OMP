import {
  Button,
  Modal,
  Input,
  Tooltip,
  Form,
  TimePicker,
  Spin,
  Switch,
  Select,
} from "antd";
import {
  PlusSquareOutlined,
  FormOutlined,
  InfoCircleOutlined,
} from "@ant-design/icons";

export const AddStrategyModal = ({
  strategyModalType,
  addStrategy,
  updateStrategy,
  loading,
  modalForm,
  addModalVisibility,
  setAddModalVisibility,
  canBackupIns,
  initData,
  strategyFormInit,
  keyArr,
  setKeyArr,
  weekData,
  frequency,
  setFrequency,
}) => {
  return (
    <Modal
      style={{ marginTop: 10 }}
      width={660}
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
            {strategyModalType === "add" ? "添加备份策略" : "编辑备份策略"}
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
          <Form.Item
            label="备份实例"
            name="backup_instances"
            key="backup_instances"
            rules={[
              {
                required: true,
                message: "请选择备份实例",
              },
            ]}
          >
            <Select
              mode="multiple"
              placeholder="选择实例"
              allowClear
              maxTagCount="responsive"
            >
              {canBackupIns?.map((e) => {
                return (
                  <Select.Option key={e} value={e}>
                    {e}
                  </Select.Option>
                );
              })}
            </Select>
          </Form.Item>

          <Form.Item
            label="备份路径"
            key="retain_path"
            name="retain_path"
            rules={[
              { required: true, message: "请输入备份路径" },
              {
                validator: (rule, value, callback) => {
                  if (value) {
                    if (value.match(/^[ ]*$/)) {
                      return Promise.reject("请输入备份路径");
                    }
                    return Promise.resolve("success");
                  } else {
                    return Promise.resolve("success");
                  }
                },
              },
            ]}
          >
            <Input placeholder="请输入备份路径" />
          </Form.Item>

          <Form.Item
            label="备份保留"
            name="retain_day"
            rules={[
              {
                required: true,
                message: "请选择保留策略",
              },
            ]}
          >
            <Select
              style={{
                width: 100,
              }}
            >
              <Select.Option key={-1} value={-1}>
                永久保留
              </Select.Option>
              <Select.Option key={1} value={1}>
                1天
              </Select.Option>
              <Select.Option key={7} value={7}>
                7天
              </Select.Option>
              <Select.Option key={30} value={30}>
                30天
              </Select.Option>
            </Select>
          </Form.Item>

          <Form.Item label="定时备份">
            <Input.Group compact>
              <Form.Item name="is_on" noStyle valuePropName="checked">
                <Switch style={{ borderRadius: "10px" }} />
              </Form.Item>
              <Form.Item noStyle>
                <Tooltip
                  placement="top"
                  title={"开启定时后，将自动执行定时任务"}
                >
                  <InfoCircleOutlined
                    name="icon"
                    style={{
                      color: "rgba(0,0,0,.45)",
                      position: "relative",
                      top: 4,
                      left: 15,
                      fontSize: 15,
                    }}
                  />
                </Tooltip>
              </Form.Item>
            </Input.Group>
          </Form.Item>

          <Form.Item
            label="定时策略"
            style={{
              height: 32,
            }}
          >
            <Input.Group compact>
              <Form.Item name={["strategy", "frequency"]} noStyle>
                <Select
                  style={{
                    width: 100,
                  }}
                  onChange={(e) => {
                    setFrequency(e);
                  }}
                >
                  <Select.Option value="day" key="day">
                    每天
                  </Select.Option>
                  <Select.Option value="week" key="week">
                    每周
                  </Select.Option>
                  <Select.Option value="month" key="month">
                    每月
                  </Select.Option>
                </Select>
              </Form.Item>

              {frequency == "week" && (
                <Form.Item
                  name={["strategy", "week"]}
                  style={{ display: "inline-block", marginLeft: "10px" }}
                >
                  <Select
                    style={{
                      width: 120,
                    }}
                  >
                    {weekData.map((item, idx) => {
                      return (
                        <Select.Option value={`${idx}`} key={item}>
                          {item}
                        </Select.Option>
                      );
                    })}
                  </Select>
                </Form.Item>
              )}

              {frequency == "month" && (
                <Form.Item
                  name={["strategy", "month"]}
                  style={{ display: "inline-block", marginLeft: "10px" }}
                >
                  <Select
                    style={{
                      width: 120,
                    }}
                  >
                    {new Array(28).fill(0).map((item, idx) => {
                      return (
                        <Select.Option key={`${idx + 1}`} value={`${idx + 1}`}>
                          {idx + 1}日
                        </Select.Option>
                      );
                    })}
                  </Select>
                </Form.Item>
              )}

              <Form.Item
                name={["strategy", "time"]}
                style={{ display: "inline-block", marginLeft: "10px" }}
              >
                <TimePicker
                  //defaultValue={moment("00:00", "HH:mm")}
                  format={"HH:mm"}
                  allowClear={false}
                />
              </Form.Item>
            </Input.Group>
          </Form.Item>

          <Form.Item
            label="自定义参数"
            name="backup_custom"
            key="backup_custom"
          >
            <Select
              mode="multiple"
              placeholder="选择自定义参数"
              allowClear
              maxTagCount="responsive"
              onChange={(e) => {
                setKeyArr(
                  e.map((i) => {
                    return i.label[0].props.children[1];
                  })
                );
              }}
              labelInValue
            >
              {initData?.map((e) => {
                return (
                  <Select.Option
                    key={e.id}
                    value={e.id}
                    disabled={
                      keyArr.includes(e.field_k) &&
                      !modalForm
                        .getFieldValue("backup_custom")
                        ?.map((i) => i.key)
                        .includes(e.id)
                    }
                  >
                    <span
                      style={{
                        color: "#096dd9",
                        fontWeight: 600,
                        marginRight: 10,
                      }}
                    >
                      [{e.field_k}]
                    </span>
                    {e.field_v}
                  </Select.Option>
                );
              })}
            </Select>
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
