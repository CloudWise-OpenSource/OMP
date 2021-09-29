import { Input, Checkbox, Button, Form, message } from "antd";
import { useState } from "react";
import styles from "./index.module.less";
import img from "@/config/logo/logo.svg";
import {
  LockOutlined,
  UserOutlined,
  CloseCircleFilled,
} from "@ant-design/icons";
import { OmpContentWrapper } from "@/components";
import { fetchGet, fetchPost } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { handleResponse } from "@/utils/utils";
import { withRouter } from "react-router";

const Login = withRouter(({ history }) => {
  const [msgShow, setMsgShow] = useState(false);
  const [isAutoLogin, setIsAutoLogin] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();
  const onCheckboxChange = (e) => {
    setIsAutoLogin(e.target.checked);
  };

  function login(data) {
    setLoading(true);
    fetchPost(apiRequest.auth.login, {
      body: {
        ...data,
        remember: isAutoLogin,
      },
    })
      .then((res) => {
        if (res.data && res.data.code == 1) {
          setMsgShow(true);
        } else if (res.data.code == 0) {
          //history.replace({pathname:"/homepage"})
          history.replace({
            pathname: "/homepage",
            state: {
              data: {},
            },
          });
          //console.log(data)
          localStorage.setItem("username",data.username)
        }
      })
      .catch((e) => {
        console.log(e);
      })
      .finally(() => setLoading(false));
  }

  return (
    <OmpContentWrapper
      wrapperStyle={{ width: "100%", height: "calc(100% - 40px)" }}
    >
      <div className={styles.loginWrapper}>
        <div className={styles.loginContent}>
          <header className={styles.loginTitle}>
            <img className={styles.loginLogo} src={img} />
            <span className={styles.loginOMP}>
              OMP<span className={styles.loginOpenText}>运维管理平台</span>
            </span>
          </header>
          <p className={styles.loginInputTitle}>用户名密码登录</p>
          <div
            style={{
              position: "relative",
              top: -20,
              backgroundColor: "#fbe3e2",
              padding: "10px",
              height: "40px",
              color: "#86292e",
              display: "flex",
              justifyContent: "space-between",
              cursor: "pointer",
            }}
            className={
              msgShow ? styles.loginMessageShow : styles.loginMessageHide
            }
            onClick={() => setMsgShow(false)}
          >
            用户名或密码错误
            <CloseCircleFilled
              style={{ color: "#fff", fontSize: 20, marginLeft: "auto" }}
            />
          </div>
          <main
            className={styles.loginInputWrapper}
            style={{ position: "relative", top: msgShow ? 0 : -24 }}
          >
            <Form
              form={form}
              onFinish={(e) => {
                login(e);
              }}
            >
              <Form.Item
                label=""
                name="username"
                key="username"
                rules={[
                  {
                    required: true,
                    message: "请输入用户名",
                  },
                ]}
              >
                <Input
                  prefix={
                    <UserOutlined
                      style={{ color: "#b8b8b8", paddingRight: 10 }}
                    />
                  }
                  style={{ paddingLeft: 10, width: 360, height: 40 }}
                  placeholder="用户名"
                />
              </Form.Item>
              <Form.Item
                label=""
                name="password"
                key="password"
                rules={[
                  {
                    required: true,
                    message: "请输入密码",
                  },
                ]}
              >
                <Input.Password
                  prefix={
                    <LockOutlined
                      style={{ color: "#b8b8b8", paddingRight: 10 }}
                    />
                  }
                  style={{
                    paddingLeft: 10,
                    width: 360,
                    height: 40,
                    marginTop: 10,
                  }}
                  placeholder="密码"
                />
              </Form.Item>
              <div className={styles.loginAuto}>
                <Checkbox checked={isAutoLogin} onChange={onCheckboxChange}>
                  <span style={{ color: "#3a3542" }}>7天自动登录</span>
                </Checkbox>
              </div>
              <Form.Item>
                <Button
                  style={{
                    width: 360,
                    height: 40,
                    fontSize: 16,
                    marginTop: 24,
                  }}
                  type="primary"
                  htmlType="submit"
                  loading={loading}
                >
                  {loading ? "登录中" : "登录"}
                </Button>{" "}
              </Form.Item>
            </Form>
          </main>
          {/* <p className={styles.loginFooter}>一站式运维管理平台</p> */}
        </div>
      </div>
    </OmpContentWrapper>
  );
});

export default Login;
