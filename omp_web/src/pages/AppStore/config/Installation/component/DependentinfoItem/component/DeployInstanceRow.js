import { Select, Form, Checkbox, InputNumber, Input } from "antd";
import { useEffect, useState } from "react";
import { randomNumber } from "@/utils/utils";

const DeployInstanceRow = ({ data, form }) => {
  const [check, setCheck] = useState(true);

  const [num, setNum] = useState(data.deploy_mode.default);

  useEffect(() => {
    if (check) {
      form.setFieldsValue({
        [`${data.name}`]: JSON.stringify({
          name: data.exist_instance[0].name,
          id: data.exist_instance[0].id,
          type: data.exist_instance[0].type,
        }),
      });
    } else {
      form.setFieldsValue({
        [`${data.name}=num`]: `${data.deploy_mode.default}`,
      });
      form.setFieldsValue({
        [`${data.name}=name`]: `${data.name}-${randomNumber()}`,
      });
    }
  }, [check]);

  return (
    <>
      <div style={{ flex: 2 }}>{data.name}</div>
      <div style={{ flex: 2 }}>{data.version}</div>
      <div style={{ flex: 3 }}>
        {check ? (
          <Form.Item
            label="选择实例"
            name={`${data.name}`}
            style={{ marginBottom: 0, width: 180 }}
          >
            <Select>
              {data.exist_instance.map((item) => (
                <Select.Option
                  key={item.name}
                  value={JSON.stringify({
                    name: item.name,
                    id: item.id,
                    type: item.type,
                  })}
                >
                  {item.name}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
        ) : (
          <Form.Item
            label="部署数量"
            name={`${data.name}=num`}
            style={{ marginBottom: 0, width: 180 }}
          >
            <InputNumber
              onChange={(e) => {
                setNum(e);
              }}
              disabled={data.deploy_mode.step == 0}
              step={data.deploy_mode.step}
              min={1}
              max={32}
            />
          </Form.Item>
        )}
      </div>
      <div
        style={{ flex: 5, display: "flex", justifyContent: "space-between" }}
      >
        {check ? (
          ""
        ) : (
          <>
            {num > 1 && (
              <Form.Item
                label="集群名称"
                name={`${data.name}=name`}
                style={{ marginBottom: 0, width: 240 }}
              >
                <Input placeholder="请输入集群名称" />
              </Form.Item>
            )}
          </>
        )}
      </div>
      <div
        style={{ flex: 2, display: "flex", justifyContent: "space-between" }}
      >
        <div />
        <div
          style={{
            fontSize: 13,
            display: "flex",
            alignItems: "center",
            flexDirection: "row-reverse",
            paddingRight: 70,
          }}
        >
          <Checkbox
            checked={check}
            onChange={(e) => {
              setCheck(e.target.checked);
            }}
          >
            复用依赖
          </Checkbox>
        </div>
      </div>
    </>
  );
};

export default DeployInstanceRow;
