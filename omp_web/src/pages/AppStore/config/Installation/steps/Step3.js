import { Button, Form, Checkbox, Input, Menu } from "antd";
import { useEffect, useRef, useState } from "react";
import { SearchOutlined } from "@ant-design/icons";

const Step3 = ({ setStepNum }) => {
  const [checked, setChecked] = useState(false);
  return (
    <div>
      <div
        style={{
          marginTop: 20,
          backgroundColor: "#fff",
          padding: 20,
          paddingLeft: 30,
          display: "flex",
          alignItems: "center",
        }}
      >
        <div style={{ width: 220 }}>
          <Checkbox
            checked={checked}
            onChange={(e) => {
              console.log(e);
              setChecked(e.target.checked);
            }}
          >
            指定本次安装服务运行用户
          </Checkbox>
        </div>

        <Input
          disabled={!checked}
          placeholder="请输入本次安装服务运行用户"
          style={{ width: 300 }}
        />
      </div>

      <div
        style={{
          marginTop: 20,
          backgroundColor: "#fff",
          //padding: 10,
          display: "flex",

          height: "calc(100% - 300px)",
        }}
      >
        <div style={{ width: 240,height:"calc(100%)" }}>
          <div
            style={{
              padding: "15px 5px 15px 5px",
              //,borderBottom:"1px solid #d9d9d9"
            }}
          >
            <Input placeholder="搜索IP地址" suffix={<SearchOutlined />} />
          </div>
          <div
            style={{
              overflowY: "auto",
              height: "calc(100% - 200px)",
            }}
          >
            <Menu
              mode="inline"
              //theme="dark"
              style={{ borderRight: "0px",height: "calc(100% - 600px)" }}
            >
              <Menu.Item key="1">10.0.14.2301</Menu.Item>
              <Menu.Item key="2">10.0.14.9</Menu.Item>
              <Menu.Item key="3">10.0.14.81</Menu.Item>
              <Menu.Item key="4">10.0.14.21</Menu.Item>
              <Menu.Item key="5">10.0.14.1</Menu.Item>
              <Menu.Item key="6">10.0.14.01</Menu.Item>
              <Menu.Item key="7">10.0.14.2z1</Menu.Item>
              <Menu.Item key="8">10.0.14.291</Menu.Item>
              <Menu.Item key="9">10.0.14.a01</Menu.Item>
              {/* <Menu.Item key="10">10.0.14.237</Menu.Item>
              <Menu.Item key="11">10.0.14.78</Menu.Item>
              <Menu.Item key="12">10.0.14.89</Menu.Item>
              <Menu.Item key="13">10.0.14.2301</Menu.Item>
              <Menu.Item key="14">10.0.14.23</Menu.Item>
              <Menu.Item key="15">10.0.14.341</Menu.Item> */}
            </Menu>
          </div>
        </div>
        <div style={{ flex: 1, borderLeft: "1px solid #d9d9d9" }}>3333</div>
      </div>

      <div
        style={{
          position: "fixed",
          backgroundColor: "#fff",
          width: "calc(100% - 230px)",
          bottom: 10,
          padding: "10px 0px",
          display: "flex",
          justifyContent: "space-between",
          paddingRight: 30,
          boxShadow: "0px 0px 10px #999999",
          alignItems: "center",
          borderRadius: 2,
        }}
      >
        <div style={{ paddingLeft: 20 }}>分布主机数量: 台</div>
        <div>
          <Button
            type="primary"
            onClick={() => {
              //   console.log(basicForm.getFieldsValue());
              //   console.log(dependentForm.getFieldsValue());
              setStepNum(1);
            }}
          >
            上一步
          </Button>
          <Button
            style={{ marginLeft: 10 }}
            type="primary"
            //disabled={unassignedServices !== 0}
            onClick={() => {
              //   console.log(basicForm.getFieldsValue());
              //   console.log(dependentForm.getFieldsValue());
              setStepNum(3);
            }}
          >
            开始安装
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Step3;
