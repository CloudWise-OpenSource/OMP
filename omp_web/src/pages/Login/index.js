import { apiRequest } from "@/config/requestApi";
import { Button, Input, message } from "antd";
import React, { useState } from "react";
import { withRouter } from "react-router";
import styles from "./index.module.less";
import img from "@/config/logo/logo.svg";
import { UserOutlined, LockOutlined } from "@ant-design/icons";
import { fetchPost, fetchGet } from "@/utils/request";
import { handleResponse } from "@/utils/utils.js"

const Login = withRouter(({ history }) => {
  const inputStyle = {
    marginBottom: 20,
    height: 45,
    fontSize: 18,
    paddingLeft:10,
    //backgroundColor:"red"
  };

  const [username, setUsername] = useState(null);
  const [password, setPassword] = useState(null);

  function login() {
    const hide = message.loading("登录中", 0);
    fetchPost(apiRequest.auth.login, {
      body: { username, password },
    })
      .then((res) => {
        res = res.data
        handleResponse(res, () => {
          localStorage.setItem("username", res.data.username);
          history.replace("/homepage");
          fetchGet(apiRequest.userManagement.user, {
            params: {
              username: res.data.username,
            },
            // eslint-disable-next-line max-nested-callbacks
          }).then((res) => {
            res = res.data
            // eslint-disable-next-line max-nested-callbacks
            handleResponse(res, () => {
              const { username, role } = res.data;
              localStorage.setItem("username", username);
              localStorage.setItem("role", role);
            });
          });
        });
      })
      .catch((e) => {
        console.log(e);
        message.error(e.message);
      })
      .finally(() => hide());
  }

  function handleEnterPressed() {
    if (!username) {
      return message.warn("请输入用户名");
    }

    if (!password) {
      return message.warn("请输入密码");
    }

    login();
  }
  return (
    <div className={styles.loginWrapper}>
      <div className={styles.loginContent}>
        <div className={styles.loginTitle}>
          <img src={img} />
          <div>运维管理平台</div>
        </div>
        <Input
          prefix={
            <UserOutlined
              style={{
                color: "rgba(0,0,0,.25)",
                marginRight: 10,
                fontsize: 18,
              }}
            />
          }
          style={inputStyle}
          placeholder="请输入用户名"
          onChange={(e) => {
            setUsername(e.target.value);
          }}
          onPressEnter={handleEnterPressed}
        />
        
        <Input.Password
          prefix={
            <LockOutlined
              style={{
                color: "rgba(0,0,0,.25)",
                marginRight: 10,
                fontsize: 18,
              }}
            />
          }
          style={inputStyle}
          placeholder="请输入登录密码"
          onChange={(e) => {
            setPassword(e.target.value);
          }}
          onPressEnter={() => handleEnterPressed()}
        />
        <Button
          type={"primary"}
          style={{ marginTop: 20, ...inputStyle }}
          onClick={() => login()}
        >
          登录
        </Button>
      </div>
    </div>
  );
});
export default Login;
