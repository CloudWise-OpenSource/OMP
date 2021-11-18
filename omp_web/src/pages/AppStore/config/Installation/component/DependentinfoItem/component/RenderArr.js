import { Select, Form, Checkbox, InputNumber, Input } from "antd";
import { useEffect, useState } from "react";
import { randomNumber } from "@/utils/utils";

const RenderArr = ({ data, form }) => {
  const [deployValue, setDeployValue] = useState(data.deploy_mode[0].key);

  useEffect(() => {
    form.setFieldsValue({
      [`${data.name}=num`]: deployValue,
    });
    if (deployValue == "master-slave" || deployValue == "master-master") {
      form.setFieldsValue({
        [`${data.name}=name`]: `${data.name}-cluster-${randomNumber(7)}`,
      });
    }
  }, [deployValue]);
  return (
    <>
      <div style={{ flex: 3 }}>
        <Form.Item
          label="部署数量"
          name={`${data.name}=num`}
          style={{ marginBottom: 0, width: 100 }}
        >
          <Select
            onChange={(e) => {
              setDeployValue(e);
            }}
          >
            {data.deploy_mode.map((item) => {
              return (
                <Select.Option key={item.key} value={item.key}>
                  {item.name}
                </Select.Option>
              );
            })}
          </Select>
        </Form.Item>
      </div>
      <div
        style={{ flex: 3, display: "flex", justifyContent: "space-between" }}
      >
        {(deployValue == "master-slave" || deployValue == "master-master") && (
          <Form.Item
            label="集群名称"
            name={`${data.name}=name`}
            style={{ marginBottom: 0, width: 240 }}
          >
            <Input placeholder="请输入集群名称" />
          </Form.Item>
        )}
      </div>
      <div
        style={{ flex: 2, display: "flex", justifyContent: "space-between" }}
      >
        {deployValue == "master-master" && (
          <Form.Item
            label="vip"
            name={`${data.name}=vip`}
            style={{ marginBottom: 0, width: 180 }}
          >
            <Input placeholder="请输入vip" />
          </Form.Item>
        )}
      </div>
    </>
  );
};

export default RenderArr;
