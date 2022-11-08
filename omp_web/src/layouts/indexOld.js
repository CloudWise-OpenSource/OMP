import { Layout, Menu, Dropdown, message, Form, Input, Button } from "antd";
import {
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  DashboardOutlined,
  CaretDownOutlined,
  QuestionCircleOutlined,
} from "@ant-design/icons";
import React, { useState, useEffect } from "react";
import img from "@/config/logo/logo.svg";
import styles from "./index.module.less";
import routerConfig from "@/config/router.config";
import { useHistory, useLocation } from "react-router-dom";
import { CustomBreadcrumb, OmpModal } from "@/components";
import { fetchGet, fetchPost } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import {
  handleResponse,
  _idxInit,
  logout
} from "@/utils/utils";

const { Header, Content, Footer, Sider } = Layout;
const { SubMenu } = Menu;

const OmpLayout = (props) => {
  const history = useHistory();
  const location = useLocation();
  //不可用状态是一个全局状态，放在layout
  const [disabled, setDisabled] = useState(false);
  const [isLoading, setLoading] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const rootSubmenuKeys = [
    "/machine-management",
    "/products-management",
    "/operation-management",
    "/actions-record",
    "/product-settings",
    "/system-settings",
  ];
  const menu = (
    <Menu className="menu">
      <Menu.Item key="changePass" onClick={() => setShowModal(true)}>
        修改密码
      </Menu.Item>
      <Menu.Item key="logout" onClick={() => logout()}>
        <span>退出登录</span>
      </Menu.Item>
    </Menu>
  );
  const [currentOpenedKeys, setCurrentOpenedKeys] = useState([]);
  const [selectedKeys, setSelectedKeys] = useState([]);
  //修改密码弹框
  const [showModal, setShowModal] = useState(false);
  //用户相关信息
  const [userInfo, setUserInfo] = useState({})

  const toggle = () => {
    setCollapsed(!collapsed);
  };

  const onPathChange = (e) => {
    console.log(e);
    if (e.key === history.location.pathname) {
      return;
    }
    // homepage没有submenu
    if (e.key === "/homepage") {
      setCurrentOpenedKeys([]);
    }
    history.push(e.key);
  };

  const onOpenChange = (openKeys) => {
    const latestOpenKey = openKeys.find(
      (key) => currentOpenedKeys.indexOf(key) === -1
    );
    //console.log(latestOpenKey)
    if (rootSubmenuKeys.indexOf(latestOpenKey) === -1) {
      setCurrentOpenedKeys(openKeys);
    } else {
      setCurrentOpenedKeys(latestOpenKey ? [latestOpenKey] : []);
    }
  };

  const onPassWordChange = (data) => {
    setLoading(true);
    fetchPost(apiRequest.auth.password, {
      body: {
        ...data,
      },
    })
      .then((res) => {
        handleResponse(res);
        if (res.code == 0) {
          setShowModal(false);
          logout();
        }
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  // 相应路由跳转，submenu打开
  useEffect(() => {
    try {
      if (
        location.pathname == "/products-management/version/rapidDeployment" ||
        location.pathname == "/products-management/version/upload" ||
        location.pathname == "/products-management/version/installationDetails"
      ) {
        setSelectedKeys(["/products-management/version"]);
      } else {
        setSelectedKeys([location.pathname]);
      }
      let pathArr = location.pathname.split("/");
      let newPath = `/${pathArr[1]}`;
      setCurrentOpenedKeys([newPath]);
    } catch (e) {
      console.log(e);
    }
  }, [location]);

  useEffect(() => {
    window.__history__ = history;
    fetchGet(apiRequest.auth.users)
      .then((res) => {
        if (res && res.data.code == 1 && res.data.message == "未认证") {
          //message.warning("登录失效,请重新登录")
          //history.replace("/login");
        }
        console.log(res.data)
        res.data && setUserInfo(res.data.data[0])
      })
      .catch((e) => {
        console.log(e);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider trigger={null} collapsible collapsed={collapsed}>
        <div
          style={{
            position: "relative",
            left: collapsed ? 0 : -15,
            display: "flex",
            height: 46,
            color: "white",
            justifyContent: "center",
            marginBottom:10
          }}
        >
          <div className={styles.headerLogo}>
            <img src={img} />
          </div>
          {!collapsed && (
            <div
              style={{
                cursor: "pointer",
                position: "relative",
                top: 1,
                fontSize: 16,
                fontWeight: 600,
                display: "flex",
                alignItems: "center",
              }}
              onClick={() => history.push("/homepage")}
            >
              运维管理平台
            </div>
          )}
        </div>
        <Menu
          mode="inline"
          style={{
            height: "calc(100% - 60px)",
            //paddingTop:3,
            borderRight: 0,
          }}
          theme="dark"
          onClick={onPathChange}
          onOpenChange={onOpenChange}
          openKeys={currentOpenedKeys}
          selectedKeys={selectedKeys}
          //theme="red"
        >
          <Menu.Item key="/homepage" icon={<DashboardOutlined />}>
            仪表盘
          </Menu.Item>
          {routerConfig.map((item) => {
            return (
              <SubMenu
                key={item.menuKey}
                icon={item.menuIcon}
                title={item.menuTitle}
              >
                {item.children.map((i) => {
                  return <Menu.Item key={i.path}>{i.title}</Menu.Item>;
                })}
              </SubMenu>
            );
          })}
        </Menu>
      </Sider>
      <Layout className="site-layout">
        <Header
          className="site-layout-background"
          style={{
            padding: 0,
            display: "flex",
            justifyContent: "space-between",
          }}
        >
          {React.createElement(
            collapsed ? MenuUnfoldOutlined : MenuFoldOutlined,
            {
              style: {
                padding: "0 24px",
                fontSize: "18px",
                lineHeight: "60px",
                cursor: "pointer",
                transition: "color 0.3s",
              },
              onClick: toggle,
            }
          )}
          <div className={styles.userAvatar} style={{ display: "flex" }}>
            <Dropdown overlay={menu} trigger={["click"]}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  fontWeight: 500,
                  fontSize: 14,
                  cursor: "pointer",
                }}
              >
                {userInfo?.username}{" "}
                <CaretDownOutlined
                  style={{ position: "relative", top: 1, left: 3 }}
                />
              </div>
            </Dropdown>
            <Dropdown
              trigger={["click"]}
              placement="bottomCenter"
              overlay={
                <Menu className="menu">
                  <Menu.Item>版本信息：V0.1.0</Menu.Item>
                </Menu>
              }
            >
              <div
                style={{
                  margin: "0 25px 0 22px",
                  display: "flex",
                  alignItems: "center",
                  fontSize: 14,
                }}
              >
                <QuestionCircleOutlined />
              </div>
            </Dropdown>
          </div>
        </Header>
        <Content style={{ margin: "0 16px" }}>
          <CustomBreadcrumb />
          <div
            //className="site-layout-background"
            style={{ padding: 0, paddingBottom: 30, height:"calc(100% - 30px)",backgroundColor:"#fff" }}
          >
            {props.children}
          </div>
        </Content>
        <Footer
          style={{
            //color: "#acb5ba",
            backgroundColor: "rgba(0,0,0,0)",
            textAlign: "center",
            height: 40,
            padding: 0,
            paddingTop: 10,
            // position:"absolute",
            // bottom:0
          }}
        >
          Copyright © 2020-2021 Cloudwise.All Rights Reserved{" "}
        </Footer>
      </Layout>
      <OmpModal
        loading={isLoading}
        onFinish={onPassWordChange}
        visibleHandle={[showModal, setShowModal]}
        title="修改密码"
      >
        <Form.Item
          label="当前密码"
          name="old_password"
          key="old_password"
          rules={[
            {
              required: true,
              message: "请输入当前用户密码",
            },
          ]}
        >
          <Input.Password placeholder="请输入当前密码" />
        </Form.Item>
        <Form.Item
          label="新密码"
          name="new_password1"
          key="new_password1"
          rules={[
            {
              required: true,
              message: "请输入新密码",
            },
          ]}
        >
          <Input.Password placeholder="请设置新密码" />
        </Form.Item>
        <Form.Item
          label="确认密码"
          name="new_password2"
          key="new_password2"
          useforminstanceinvalidator="true"
          rules={[
            {
              required: true,
              message: "请再次输入新密码",
            },
            {
              validator: (rule, value, callback, passwordModalForm) => {
                if (
                  passwordModalForm.getFieldValue().new_password1 === value ||
                  !value
                ) {
                  return Promise.resolve("success");
                } else {
                  return Promise.reject("两次密码输入不一致");
                }
              },
            },
          ]}
        >
          <Input.Password placeholder="请再次输入新密码" />
        </Form.Item>
      </OmpModal>
    </Layout>
  );
};

export default OmpLayout;
