import { Steps, Form, Input, Button, Select, Checkbox } from "antd";
import { useEffect, useState } from "react";
// 组件安装的依赖信息

const randomNumber = () => {
  let r = "";
  let str = "QWERTYUIOPLKJHGFDSAZXCVBNM123456790";
  new Array(6).fill(0).map((item) => {
    let num = parseInt(Math.random() * 26);
    r += str[num];
  });
  return r;
};

const RenderComDependence = ({ data, form }) => {
  if (data.is_base_env) {
    return (
      <div
        key={data.name}
        style={{
          marginBottom: 20,
          display: "flex",
          //justifyContent: "space-between",
          paddingRight: 80,
        }}
      >
        <div
          style={{
            flex: 2,
            paddingLeft: 20,
          }}
        >
          {data.name}
        </div>

        <div
          style={{
            flex: 3,
          }}
        >
          {data.version}
        </div>
        <div
          style={{
            flex: 14,
          }}
        />
        <div style={{ color: "#c2c2c2", flex: 2 }}>
          <Checkbox defaultChecked disabled style={{ marginRight: 10 }} />
          安装依赖
        </div>
      </div>
    );
  } else {
    // 当is_base_env为false的渲染逻辑
    return <RenderHasData data={data} form={form} />;
  }
};

// 分类渲染
const RenderHasData = ({ data, form }) => {
  if (data.cluster_info.length == 0 && data.instance_info.length == 0) {
    return <RenderClusterDom data={data} form={form} />;
  } else {
    let dataSource = data.cluster_info.concat(data.instance_info);
    console.log(dataSource);
    // 因为是两个数据源拼接并且字段不一致在这里合并并统一字段
    let result = dataSource.map((item) => {
      if (item.ip) {
        return {
          id: `single|${item.id}`,
          name: item.service_instance_name,
        };
      } else {
        return {
          id: `cluster|${item.id}`,
          name: item.cluster_name,
        };
      }
    });
    return <RenderInstanceDom instanceData={result} data={data} form={form} />;
  }
};

// 当判断为集群时的渲染
const RenderClusterDom = ({ data, form }) => {
  // 将当前数据在deployModeObj初始化
  // let obj = R.clone(deployModeObj);

  // console.log(form.getFieldValue(`${data.name}|deploy_mode`));

  return (
    <Form form={form} name="basic" layout="vertical">
      <div
        key={data.name}
        style={{
          display: "flex",
          //justifyContent: "space-between",
          paddingRight: 80,
          alignItems: "center",
        }}
      >
        <div
          style={{
            flex: 2,
            paddingLeft: 20,
          }}
        >
          {data.name}
        </div>

        <div
          style={{
            flex: 3,
          }}
        >
          {data.version}
        </div>

        <ClusterComponent form={form} data={data} />
        <div
          style={{
            flex: 3,
          }}
        />
        <div style={{ fontSize: 14, color: "#c2c2c2", flex: 2 }}>
          {/* <Checkbox defaultChecked disabled style={{ marginRight: 10 }} />
            安装依赖 */}
        </div>
      </div>
    </Form>
  );
};

// 单实例没有实例名称。其他有(单独封装为了复用)
const ClusterComponent = ({ data, form }) => {
  const [deploy_mode, setDeploy_mode] = useState(data.ser_deploy_mode[0].key);
  useEffect(() => {
    form.setFieldsValue({
      [`${data.name}|deploy_mode`]: data.ser_deploy_mode[0].key,
      [`${data.name}|modeName`]: `${data.name}-${randomNumber()}`,
    });
  }, []);

  return (
    <>
      <div
        style={{
          flex: 6,
        }}
      >
        <Form.Item
          label={<div style={{ fontSize: 12 }}>集群模式</div>}
          name={`${data.name}|deploy_mode`}
        >
          <Select
            style={{ width: 240 }}
            onSelect={(e) => {
              setDeploy_mode(e);
            }}
          >
            {data.ser_deploy_mode.map((item) => (
              <Select.Option value={item.key} key={item.key}>
                {item.name}
              </Select.Option>
            ))}
          </Select>
        </Form.Item>
      </div>
      {deploy_mode !== "single" ? (
        <div
          style={{
            flex: 6,
          }}
        >
          <Form.Item
            label={<div style={{ fontSize: 12 }}>集群名称</div>}
            name={`${data.name}|modeName`}
            rules={[{ required: true, message: "请输入集群名称" }]}
          >
            <Input style={{ width: 240 }} />
          </Form.Item>
        </div>
      ) : (
        <div
          style={{
            flex: 6,
          }}
        />
      )}
    </>
  );
};

// 判断为实例的渲染
const RenderInstanceDom = ({ instanceData, data, form }) => {
  const [isMultiplexing, setIsMultiplexing] = useState("checked");

  useEffect(() => {
    form.setFieldsValue({
      [`${data.name}|isMultiplexing`]: "checked",
      [`${data.name}|instance`]: instanceData[0].id,
    });
  }, []);

  return (
    <Form form={form} name="basic" layout="vertical">
      <div
        key={data.name}
        style={{
          display: "flex",
          //justifyContent: "space-between",
          paddingRight: 80,
          alignItems: "center",
        }}
      >
        <div
          style={{
            flex: 2,
            paddingLeft: 20,
          }}
        >
          {data.name}
        </div>

        <div
          style={{
            flex: 3,
          }}
        >
          {data.version}
        </div>
        {isMultiplexing == "checked" ? (
          <>
            <div
              style={{
                flex: 6,
              }}
            >
              <Form.Item
                label={<div style={{ fontSize: 12 }}>选择实例</div>}
                name={`${data.name}|instance`}
              >
                <Select style={{ width: 240 }}>
                  {instanceData.map((item) => (
                    <Select.Option value={item.id} key={item.id}>
                      {item.name}
                    </Select.Option>
                  ))}
                  {/* <Select.Option value={123} key={123}>
                  {123}
                </Select.Option> */}
                </Select>
              </Form.Item>
            </div>
            <div
              style={{
                flex: 6,
              }}
            />
          </>
        ) : (
          <ClusterComponent form={form} data={data} />
        )}

        <div
          style={{
            flex: 3,
          }}
        >
          存在实例,是否复用？
        </div>
        <div style={{ fontSize: 14, flex: 2 }}>
          <Form.Item
            valuePropName="checked"
            name={`${data.name}|isMultiplexing`}
            style={{ marginBottom: 0 }}
          >
            <Checkbox
              onChange={(e) => {
                e.target.checked
                  ? setIsMultiplexing("checked")
                  : setIsMultiplexing("unChecked");
              }}
              style={{ marginRight: 10 }}
            >
              复用
            </Checkbox>
          </Form.Item>
        </div>
      </div>
    </Form>
  );
};

export default RenderComDependence;
