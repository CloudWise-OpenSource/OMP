import styles from "../index.module.less";
import { Form, Input, InputNumber } from "antd";
import { useEffect, useState, useRef } from "react";
import { randomNumber } from "@/utils/utils";
import { DownOutlined } from "@ant-design/icons";

const BasicInfoItem = ({ data, form }) => {
  // step3的安装详情是否是展开状态 因为多个所以为对象
  const [isOpen, setIsOpen] = useState(false);

  const numRef = useRef({});

  const step2Open = (num) => ({
    marginTop: 10,
    minHeight: 30,
    height: num * 55,
    transition: "all .2s ease-in",
    overflow: "hidden",
    backgroundColor: "#f9f9f9",
    display: "flex",
    padding: 10,
    flexWrap: "wrap",
  });

  const step2NotOpen = () => ({
    height: 0,
    minHeight: 0,
    transition: "all .2s ease-in",
    overflow: "hidden",
    backgroundColor: "#f9f9f9",
    display: "flex",
  });

  useEffect(() => {
    form.setFieldsValue({
      [`${data.name}`]: `${data.name}-${randomNumber()}`,
    });
    data.services_list.map((item) => {
      numRef.current[
        `${data.name}=${item.name}`
      ] = `${item.deploy_mode.default}`;
      form.setFieldsValue({
        [`${data.name}=${item.name}`]: `${item.deploy_mode.default}`,
      });
    });
  }, []);

  return (
    <>
      <div className={styles.basicInfoItem}>
        <div style={{ flex: 2 }}>{data.name}</div>
        <div style={{ flex: 2 }}>{data.version}</div>
        <div style={{ flex: 3 }}>
          <Form.Item
            label="实例名称"
            name={`${data.name}`}
            style={{ marginBottom: 0 }}
            rules={[
              {
                required: true,
                message: "请输入密码",
              },
            ]}
          >
            <Input />
          </Form.Item>
        </div>
        <div
          style={{ flex: 7, display: "flex", justifyContent: "space-between" }}
        >
          <div />
          <div style={{ paddingRight: 20 }}>
            <a
              style={{
                fontSize: 13,
                display: "flex",
                alignItems: "center",
                flexDirection: "row-reverse",
                paddingRight: 50,
              }}
              onClick={() => {
                setIsOpen(!isOpen);
              }}
            >
              <DownOutlined
                style={{
                  transform: `rotate(${isOpen ? 180 : 0}deg)`,
                  position: "relative",
                  top: isOpen ? -1 : 1,
                  left: 3,
                }}
              />
              更改服务信息
            </a>
          </div>
        </div>
      </div>
      <div
        //className={styles.backIcon}
        style={
          isOpen
            ? step2Open(Math.ceil(data.services_list.length / 3))
            : step2NotOpen()
        }
      >
        {data.services_list.map((item) => {
          return (
            <div style={{ width: 360 }} key={item.name}>
              <Form.Item
                label={<span style={{ width: 180 }}>{item.name}</span>}
                name={`${data.name}=${item.name}`}
                style={{ marginBottom: 0 }}
              >
                <InputNumber
                  min={1}
                  max={32}
                  onChange={(e) => {
                    if (
                      e &&
                      (e - item.deploy_mode.step ==
                        numRef.current[`${data.name}=${item.name}`] ||
                        e + item.deploy_mode.step ==
                          numRef.current[`${data.name}=${item.name}`])
                    ) {
                      numRef.current[`${data.name}=${item.name}`] = e;
                    } else {
                      form.setFieldsValue({
                        [`${data.name}=${item.name}`]:
                          numRef.current[`${data.name}=${item.name}`],
                      });
                    }
                  }}
                  keyboard={false}
                  disabled={item.deploy_mode.step == 0}
                  step={item.deploy_mode.step}
                />
              </Form.Item>
            </div>
          );
        })}
      </div>
      <div style={{ marginTop: 5, color: "red", whiteSpace: "pre-line" }}>
        {data.error_msg}
      </div>
    </>
  );
};

export default BasicInfoItem;
