import { Select, Form, Checkbox, InputNumber, Input } from "antd";
import { useEffect, useState } from "react";
import { randomNumber } from "@/utils/utils";
import RenderArr from "./RenderArr";
import RenderNum from "./RenderNum";

const DeployInstanceRow = ({ data, form }) => {
  const [check, setCheck] = useState(true);

  useEffect(() => {
    if (check) {
      form.setFieldsValue({
        [`${data.name}`]: JSON.stringify({
          name: data.exist_instance[0]?.name,
          id: data.exist_instance[0]?.id,
          type: data.exist_instance[0]?.type,
        }),
      });
    }
  }, [check]);

  return (
    <>
      <div style={{ flex: 1 }}>{data.name}</div>
      <div style={{ flex: 1 }}>{data.version}</div>
      {check ? (
        <>
          <div style={{ flex: 3 }}>
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
          </div>
          <div
            style={{
              flex: 5,
              display: "flex",
              justifyContent: "space-between",
            }}
          ></div>
        </>
      ) : Array.isArray(data.deploy_mode) ? (
        <RenderArr data={data} form={form} />
      ) : (
        <RenderNum data={data} form={form} />
      )}

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
