import { Layout, Menu, Dropdown, message, Form, Input } from "antd";
import {
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  DashboardOutlined,
  CaretDownOutlined,
  QuestionCircleOutlined,
  CaretUpOutlined
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
    { title: "快速部署", path: "/products-management/version/rapidDeployment" },
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
    // console.log(userInfo)
    // logout();
    // return 
    console.log(data)
    setLoading(true);
    fetchPost(apiRequest.auth.changePassword, {
      body: {
        username: localStorage.getItem("username"),
        old_password: data.old_password,
        new_password: data.new_password2
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          console.log(res)
          if(res.code == 0){
            message.success("修改密码成功, 请重新登录")
            setShowModal(false);
            setTimeout(()=>{
            logout();
            },1000)
          }
        })
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
        console.log("====")
        if (res && res.data.code == 1 && res.data.message == "未认证") {
          //message.warning("登录失效,请重新登录")
          //history.replace("/login");
        }
        //console.log(res.data);
        res.data && setUserInfo(res.data.data[0]);
      })
      .catch((e) => {
        console.log(e);
      })
      .finally(() => setLoading(false));
  }, []);

    // 这里做一个视口查询，存入store, 其他组件可以根据视口大小进行自适应
    reduxDispatch(
      getSetViewSizeAction({
        height: document.documentElement.clientHeight,
        width: document.documentElement.clientWidth,
      })
    );

    // 防止在校验进入死循环
  const flag = useRef(null)

  // 查询全局维护模式状态
  const queryMaintainState = ()=>{
    fetchGet(apiRequest.environment.queryMaintainState)
    .then((res) => {
      handleResponse(res, (res) => {
        //console.log(res)
        if (res.data) {
          reduxDispatch(getMaintenanceChangeAction(res.data.length !== 0));
        }
      })}
    )
    .catch((e) => {
      console.log(e);
    })
    .finally();
  }

  useEffect(()=>{
    queryMaintainState()
  },[])

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
            backgroundColor:"#171e2b"
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
          }}
          //theme="dark"
          onClick={onPathChange}
          onOpenChange={onOpenChange}
          openKeys={currentOpenedKeys}
          selectedKeys={selectedKeys}
          //theme="red"
          expandIcon={(e)=>{
            if(e.isOpen){
              return <CaretUpOutlined /> 
            }else{
              return <CaretDownOutlined />
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
          {/* {React.createElement(
            collapsed ? MenuUnfoldOutlined : MenuFoldOutlined,
            {
              style: {
                fontSize: "18px",
                cursor: "pointer",
                transition: "color 0.3s",
                display:"flex",
                alignItems:"center",
                position:"relative",
                top:1
              },
              onClick: toggle,
            }
          )} */}
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
        <CustomBreadcrumb />
        <Content style={{ margin: "0 16px" }}>
          <div
            //className="site-layout-background"
            style={{
              padding: 0,
              paddingBottom: 30,
              height: "calc(100% - 10px)",
              backgroundColor: "#fff",
            }}
          >
            {props.children}
          </div>
        </Content>
        <Footer
          style={{
            //color: "#acb5ba",
            backgroundColor: "rgba(0,0,0,0)",
            textAlign: "center",
            height: 30,
            padding: 0,
            paddingTop: 0,
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
        beForeOk = {()=>{
          flag.current = true
        }}
        afterClose = {()=>{
          flag.current = null
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
                  if(!isPassword(value)){
                    if(value.length < 8) {
                      return Promise.reject("密码长度为8到16位");
                    }
                    return Promise.resolve("success");
                  }else{
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
              validator: (rule, value, callback,passwordModalForm) => {
                if (value) {
                  if(!flag.current){
                    passwordModalForm.validateFields(["new_password2"])
                  }
                  if(!isPassword(value)){
                    if(value.length < 8) {
                      return Promise.reject("密码长度为8到16位");
                    }
                    return Promise.resolve("success");
                  }else{
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
                  if(!isPassword(value)){
                    if(value.length < 8) {
                      return Promise.reject("密码长度为8到16位");
                    }
                    if (
                      passwordModalForm.getFieldValue().new_password1 === value ||
                      !value
                    ) {
                      return Promise.resolve("success");
                    } else {
                      return Promise.reject("两次密码输入不一致");
                    }
                  }else{
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
