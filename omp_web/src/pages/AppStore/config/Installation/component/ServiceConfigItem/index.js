import { Collapse, Form, Input, Tooltip, Spin } from "antd";
import { CaretRightOutlined, InfoCircleOutlined } from "@ant-design/icons";
import { useEffect } from "react";

const { Panel } = Collapse;

const ServiceConfigItem = ({ data, form, loading }) => {
  let portData = data.ports || [];
  let installArgsData = data.install_args || [];
  const renderData = [...installArgsData, ...portData];

  useEffect(() => {
    // 设置默认值
    renderData.map((i) => {
      form.setFieldsValue({
        [`${data.name}=${i.key}`]: i.default,
      });
    });
  }, []);

  return (
    <div style={{ padding: 10 }}>
      <Spin spinning={loading}>
        <Collapse
          bordered={false}
          defaultActiveKey={["1"]}
          expandIcon={({ isActive }) => (
            <CaretRightOutlined rotate={isActive ? 90 : 0} />
          )}
        >
          <Panel
            header={data.name}
            key="1"
            className={"panelItem"}
            style={{ backgroundColor: "#f6f6f6" }}
          >
            {renderData.map((item) => {
              return (
                <Form.Item
                  key={item.key}
                  label={<div>{item.name}</div>}
                  name={`${data.name}=${item.key}`}
                  style={{ marginTop: 10, width: 450 }}
                  rules={[
                    {
                      required: true,
                      message: `请输入${item.name}`,
                    },
                  ]}
                >
                  <Input
                    addonBefore={
                      item.dir_key ? (
                        <span style={{ color: "#b1b1b1" }}>/ 数据分区</span>
                      ) : null
                    }
                    style={{ width: 420 }}
                    placeholder={`请输入${item.name}`}
                    suffix={
                      item.dir_key ? (
                        <Tooltip title="数据分区：主机所设置的数据分区">
                          <InfoCircleOutlined
                            style={{ color: "rgba(0,0,0,.45)" }}
                          />
                        </Tooltip>
                      ) : null
                    }
                  />
                </Form.Item>
              );
            })}
          </Panel>
        </Collapse>
      </Spin>
    </div>
  );
};

export default ServiceConfigItem;
