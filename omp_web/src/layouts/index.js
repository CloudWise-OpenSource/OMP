import { Layout, Menu, Dropdown, message, Form, Input } from "antd";
import {
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  DashboardOutlined,
  CaretDownOutlined,
  QuestionCircleOutlined,
  CaretUpOutlined,
} from "@ant-design/icons";
import React, { useState, useEffect, useRef } from "react";
import img from "@/config/logo/logo.svg";
import styles from "./index.module.less";
import routerConfig from "@/config/router.config";
import { useHistory, useLocation } from "react-router-dom";
import { CustomBreadcrumb, OmpModal } from "@/components";
import { fetchGet, fetchPost } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import { handleResponse, _idxInit, logout, isPassword } from "@/utils/utils";
import { useDispatch } from "react-redux";
import { getSetViewSizeAction } from "./store/actionsCreators";
import { getMaintenanceChangeAction } from "@/pages/SystemManagement/store/actionsCreators";

const { Header, Content, Footer, Sider } = Layout;
const { SubMenu } = Menu;

const OmpLayout = (props) => {
  const reduxDispatch = useDispatch();
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

  const headerLink = [
    // { title: "仪表盘", path: "/homepage" },
    // { title: "应用商店", path: "/application_management/app_store" },
    { title: "快速部署", path: "/application_management/deployment-plan" },
    // { title: "数据上传", path: "/products-management/version/upload" },
    // { title: "深度分析", path: "/operation-management/report" },
    {
      title: "监控平台",
      path: "/proxy/v1/grafana/d/XrwAXz_Mz/mian-ban-lie-biao",
    },
  ];

  const [currentOpenedKeys, setCurrentOpenedKeys] = useState([]);
  const [selectedKeys, setSelectedKeys] = useState([]);
  //修改密码弹框
  const [showModal, setShowModal] = useState(false);
  //用户相关信息
  const [userInfo, setUserInfo] = useState({});

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

  const toggle = () => {
    setCollapsed(!collapsed);
  };

  const onPathChange = (e) => {
    //console.log(e);
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
    fetchPost(apiRequest.auth.changePassword, {
      body: {
        username: localStorage.getItem("username"),
        old_password: data.old_password,
        new_password: data.new_password2,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          console.log(res);
          if (res.code == 0) {
            message.success("修改密码成功, 请重新登录");
            setShowModal(false);
            setTimeout(() => {
              logout();
            }, 1000);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  // 相应路由跳转，submenu打开
  useEffect(() => {
    try {
      let pathArr = location.pathname.split("/");
      console.log(pathArr);
      if (pathArr[1] == "homepage") {
        setSelectedKeys(["/homepage"]);
      } else {
        setSelectedKeys([`/${pathArr[1]}/${pathArr[2]}`]);
      }
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
        }
        res.data && res.data.data && setUserInfo(res.data.data[0]);
      })
      .catch((e) => {
        console.log(e);
      })
      .finally(() => setLoading(false));
  }, []);

  const antiShakeRef = useRef(null);

  const getViewSize = () => {
    reduxDispatch(
      // 这里做一个视口查询，存入store, 其他组件可以根据视口大小进行自适应
      getSetViewSizeAction({
        height: document.documentElement.clientHeight,
        width: document.documentElement.clientWidth,
      })
    );
  };

  getViewSize();

  useEffect(() => {
    window.onresize = () => {
      if (!antiShakeRef.current) {
        antiShakeRef.current = true;
        setTimeout(() => {
          getViewSize();
          antiShakeRef.current = false;
        }, 300);
      }
    };
  }, []);

  // 防止在校验进入死循环
  const flag = useRef(null);

  // 查询全局维护模式状态
  const queryMaintainState = () => {
    fetchGet(apiRequest.environment.queryMaintainState)
      .then((res) => {
        handleResponse(res, (res) => {
          //console.log(res)
          if (res.data) {
            reduxDispatch(getMaintenanceChangeAction(res.data.length !== 0));
          }
        });
      })
      .catch((e) => {
        console.log(e);
      })
      .finally();
  };

  useEffect(() => {
    queryMaintainState();
  }, []);

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider
        trigger={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
        collapsible
        collapsed={collapsed}
        onCollapse={toggle}
        collapsedWidth={50}
      >
        <div
          style={{
            position: "relative",
            left: collapsed ? 0 : -15,
            display: "flex",
            height: 60,
            color: "white",
            justifyContent: "center",
            // /marginBottom:10,
            backgroundColor: "#171e2b",
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
            borderRight: "1px solid #d7d9e1",
            color: "rgba(0,0,0,0.65)",
            // position:"fixed",
            // zIndex:1000,
          }}
          //theme="dark"
          onClick={onPathChange}
          onOpenChange={onOpenChange}
          openKeys={currentOpenedKeys}
          selectedKeys={selectedKeys}
          //theme="red"
          expandIcon={(e) => {
            if (e.isOpen) {
              return <CaretUpOutlined />;
            } else {
              return (
                <CaretDownOutlined style={{ color: "rgba(0,0,0,0.65)" }} />
              );
            }
          }}
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
                  if (!i.notInMenu) {
                    return <Menu.Item key={i.path}>{i.title}</Menu.Item>;
                  }
                })}
              </SubMenu>
            );
          })}
        </Menu>
      </Sider>
      <Layout className="site-layout" style={{ width: "100%" }}>
        <Header
          className="site-layout-background"
          style={{
            padding: 0,
            display: "flex",
            justifyContent: "space-between",
            position: "fixed",
            zIndex: 1000,
            transition: collapsed ?"all 0.1s ease-out" : "all 0.4s ease-out",
            width: collapsed ? "calc(100% - 50px)" : "calc(100% - 200px)",
            marginLeft: collapsed ? 50 : 200,
          }}
        >
          <div style={{ display: "flex" }}>
            {headerLink.map((item, idx) => {
              return (
                <div
                  style={
                    window.location.hash.includes(item.path)
                      ? { background: "#0C1423", color: "#fff" }
                      : { cursor: disabled ? "not-allowed" : null }
                  }
                  className={
                    !disabled || item.title === "快速部署"
                      ? styles.headerLink
                      : styles.headerLinkNohover
                  }
                  key={idx}
                  onClick={() => {
                    if (!disabled || item.title === "快速部署") {
                      if (item.title === "监控平台") {
                        window.open(
                          "/proxy/v1/grafana/d/XrwAXz_Mz/mian-ban-lie-biao"
                        );
                      } else {
                        history.push(item.path);
                      }
                    }
                  }}
                >
                  {item.title}
                </div>
              );
            })}
          </div>
          <div
            className={styles.userAvatar}
            style={{ display: "flex", position: "relative", top: 2 }}
          >
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
                {localStorage.getItem("username")}{" "}
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
        <CustomBreadcrumb collapsed={collapsed} />
        <Content style={{ margin: "0 16px", color: "rgba(0,0,0,0.65)" }}>
          <div
            style={{
              transition: "all 0.2s ease-in-out",
              marginTop: 120,
              marginLeft: collapsed ? 50 : 200,
              padding: 0,
              paddingBottom: 30,
              height: "calc(100% - 130px)",
              // 应用商店content大背景不是白色，特殊处理
              backgroundColor:
                location.pathname == "/application_management/app_store" ||
                location.pathname.includes("installation") || location.pathname.includes("service_upgrade") ||
                location.pathname.includes("/homepage")
                  ? undefined
                  : "#fff",
            }}
          >
            {props.children}
          </div>
        </Content>
        <Footer
          style={{
            backgroundColor: "rgba(0,0,0,0)",
            textAlign: "center",
            height: 30,
            padding: 0,
            paddingTop: 0,
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
        beForeOk={() => {
          flag.current = true;
        }}
        afterClose={() => {
          flag.current = null;
        }}
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
            {
              validator: (rule, value, callback) => {
                if (value) {
                  if (!isPassword(value)) {
                    if (value.length < 8) {
                      return Promise.reject("密码长度为8到16位");
                    }
                    return Promise.resolve("success");
                  } else {
                    return Promise.reject(
                      `密码只支持数字、字母以及常用英文符号`
                    );
                  }
                } else {
                  return Promise.resolve("success");
                }
              },
            },
          ]}
        >
          <Input.Password maxLength={16} placeholder="请输入当前密码" />
        </Form.Item>
        <Form.Item
          label="新密码"
          name="new_password1"
          key="new_password1"
          useforminstanceinvalidator="true"
          rules={[
            {
              required: true,
              message: "请输入新密码",
            },
            {
              validator: (rule, value, callback, passwordModalForm) => {
                if (value) {
                  if (!flag.current) {
                    passwordModalForm.validateFields(["new_password2"]);
                  }
                  if (!isPassword(value)) {
                    if (value.length < 8) {
                      return Promise.reject("密码长度为8到16位");
                    }
                    return Promise.resolve("success");
                  } else {
                    return Promise.reject(
                      `密码只支持数字、字母以及常用英文符号`
                    );
                  }
                } else {
                  return Promise.resolve("success");
                }
              },
            },
          ]}
        >
          <Input.Password maxLength={16} placeholder="请设置新密码" />
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
                if (value) {
                  if (!isPassword(value)) {
                    if (value.length < 8) {
                      return Promise.reject("密码长度为8到16位");
                    }
                    if (
                      passwordModalForm.getFieldValue().new_password1 ===
                        value ||
                      !value
                    ) {
                      return Promise.resolve("success");
                    } else {
                      return Promise.reject("两次密码输入不一致");
                    }
                  } else {
                    return Promise.reject(
                      `密码只支持数字、字母以及常用英文符号`
                    );
                  }
                } else {
                  return Promise.resolve("success");
                }
              },
            },
          ]}
        >
          <Input.Password maxLength={16} placeholder="请再次输入新密码" />
        </Form.Item>
      </OmpModal>
    </Layout>
  );
};

export default OmpLayout;
