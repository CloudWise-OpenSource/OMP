import { Collapse, Form, Input, Tooltip, Spin } from "antd";
import { CaretRightOutlined, InfoCircleOutlined } from "@ant-design/icons";
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

const { Panel } = Collapse;

const ServiceConfigItem = ({ form, loading, ip, idx }) => {
  let data = useSelector((state) => state.installation.step3Data)[ip][idx];

  // console.log(data)

  let portData = data.ports || [];
  let installArgsData = data.install_args || [];
  const renderData = [...installArgsData, ...portData];
  // let instanceName = data.instance_name;

  const errInfo = useSelector((state) => state.installation.step3ErrorData);

  useEffect(() => {
    // 设置默认值
    // form.setFieldsValue({
    //   [`${data.name}=instance_name`]: data.instance_name,
    // });
    renderData.map((i) => {
      form.setFieldsValue({
        [`${data.name}=${i.key}`]: i.default,
      });
    });
  }, [data]);

  useEffect(() => {
    if (errInfo[ip] && errInfo[ip][data.name]) {
      // form.setFields([
      //   {
      //     name: `${data.name}=instance_name`,
      //     errors: [errInfo[ip][data.name][key]],
      //   },
      // ]);
      for (const key in errInfo[ip][data.name]) {
        if(errInfo[ip][data.name][key]){
          form.setFields([
            {
              name: `${data.name}=${key}`,
              errors: [errInfo[ip][data.name][key]],
            },
          ]);
        }
      }
    }
  }, [errInfo[ip]]);

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
                  label={item?.name}
                  name={`${data.name}=${item?.key}`}
                  style={{ marginTop: 10, width: 600 }}
                  rules={[
                    {
                      required: item.key !== "vip",
                      message: `请输入${item.name}`,
                    },
                  ]}
                >
                  <Input
                    // onChange={(e) => {
                    //   //console.log(e.target.value);
                    //   dispatch(
                    //     getStep3ServiceChangeAction(
                    //       ip,
                    //       data.name,
                    //       item.key,
                    //       e.target.value
                    //     )
                    //   );
                    // }}
                    addonBefore={
                      item.dir_key ? (
                        <span style={{ color: "#b1b1b1" }}>/ 数据分区</span>
                      ) : null
                    }
                    //style={{ width: 420 }}
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
