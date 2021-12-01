import { Select, Form, Checkbox, InputNumber, Input } from "antd";
import { useEffect, useRef, useState } from "react";
import { randomNumber } from "@/utils/utils";

const RenderNum = ({ data, form }) => {
  const [num, setNum] = useState(data.deploy_mode.default);
  const numRef = useRef(data.deploy_mode.default);

  useEffect(() => {
    if (num == 1) {
      form.setFieldsValue({
        [`${data.name}=num`]: `${data.deploy_mode.default}`,
      });
    }

    if (num > 1) {
      form.setFieldsValue({
        [`${data.name}=num`]: `${data.deploy_mode.default}`,
      });
      form.setFieldsValue({
        [`${data.name}=name`]: `${data.name}-cluster-${randomNumber(7)}`,
      });
    }
  }, []);

  return (
    <>
      <div style={{ flex: 3 }}>
        <Form.Item
          label="部署数量"
          name={`${data.name}=num`}
          style={{ marginBottom: 0, width: 180 }}
        >
          <InputNumber
            onChange={(e) => {
              if (
                e - data.deploy_mode.step == numRef.current ||
                e + data.deploy_mode.step == numRef.current
              ) {
                numRef.current = e;
                setNum(e);
              } else {
                form.setFieldsValue({
                  [`${data.name}=num`]: numRef.current,
                });
              }

              if (e > 1) {
                form.setFieldsValue({
                  [`${data.name}=name`]: `${data.name}-cluster-${randomNumber(
                    7
                  )}`,
                });
              }
            }}
            keyboard={false}
            disabled={data.deploy_mode.step == 0}
            step={data.deploy_mode.step}
            min={1}
            max={32}
            style={{
              width: 100,
            }}
          />
        </Form.Item>
      </div>
      <div
        style={{ flex: 5, display: "flex", justifyContent: "space-between" }}
      >
        {num > 1 && (
          <Form.Item
            label="集群名称"
            name={`${data.name}=name`}
            style={{ marginBottom: 0, width: 240 }}
            rules={[
              {
                required: true,
                message: "请输入集群名称",
              },
            ]}
          >
            <Input placeholder="请输入集群名称" />
          </Form.Item>
        )}
      </div>
    </>
  );
};

export default RenderNum;
