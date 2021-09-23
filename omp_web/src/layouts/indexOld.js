import { useState, useEffect, createContext, useReducer } from "react";
import { Layout, Menu, Dropdown, message, Form, Input, Button } from "antd";
import { fetchGet, fetchDelete, fetchPost } from "@/utils/request";
import { handleResponse } from "@/utils/utils";
import { apiRequest } from "@/config/requestApi";
import {
  DashboardOutlined,
  QuestionCircleFilled,
  CaretDownOutlined,
  QuestionCircleOutlined
} from "@ant-design/icons";
import { useHistory, useLocation } from "react-router-dom";
import img from "@/config/logo/logo.svg";
import routerConfig from "@/config/router.config";
import { CustomBreadcrumb, OmpModal } from "@/components";
import styles from "./index.module.less";
//import defaultState, { reducer } from "@/store_global";
import { getSetViewSizeAction } from "./store/actionsCreators";
import { useSelector, useDispatch } from "react-redux";

const { SubMenu } = Menu;
const { Header, Content, Sider } = Layout;

export const context = createContext(null);

const OmpLayout = (props) => {
  const reduxDispatch = useDispatch();

  const viewWidth = useSelector((state) => state.layouts.viewSize.width);

  // const [state, dispatch] = useReducer(reducer, defaultState);

  const history = useHistory();
  const location = useLocation();
  //是否禁用
  //console.log(props);
  //不可用状态是一个全局状态，放在layout
  const [disabled, setDisabled] = useState(false);
  const [isLoading, setLoading] = useState(false);
  
  const [currentOpenedKeys, setCurrentOpenedKeys] = useState([]);
  const [selectedKeys, setSelectedKeys] = useState([]);

  function delCookie(name){
    var exp = new Date();
    exp.setTime(exp.getTime() - 1);
    var cval = getCookie(name);
    //console.log(cval)
    if (cval != null) document.cookie = name + "=" + cval + ';domin="localhost"'+";expires=" + exp.toGMTString();
  }
  function getCookie(name){
    //console.log(document.cookie)
    let arr = document.cookie.match(new RegExp("(^| )" + name + "=([^;]*)(;|$)"));
    if (arr != null) return unescape(arr[2]); 
    return null;
  }

  const logout = () => {
    delCookie("jwtToken")
    history.replace("/login");
    return 
    fetchDelete(apiRequest.auth.logout).then((data) => {
      data = data.data;
      if ([0, 3].includes(data.code)) {
        data.code == 0 && message.success(data.message);
        localStorage.clear();
        history.replace("/login");
      }
      if (data.code === 1) {
        message.error(data.message);
      }
    });
  };

  const rootSubmenuKeys = [
    "/machine-management",
    "/products-management",
    "/operation-management",
    "/actions-record",
    "/product-settings",
    "/system-settings",
  ];

  const headerLink = [
    { title: "仪表盘", path: "/homepage" },
    { title: "快速部署", path: "/products-management/version/rapidDeployment" },
    { title: "深度分析", path: "/operation-management/report" },
    {
      title: "监控平台",
      path: "/proxy/v1/grafana/d/XrwAXz_Mz/mian-ban-lie-biao",
    },
  ];

  //修改密码弹框
  const [showModal, setShowModal] = useState(false);

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

  const onPathChange = (e) => {
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
        res = res.data;
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

  //校验是否已登录
  useEffect(() => {
    window.__history__ = history;
    if (!localStorage.getItem("username")) {
      return 
      history.replace("/login");
    }
  }, []);

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

  // 这里做一个视口查询，存入store, 其他组件可以根据视口大小进行自适应
  reduxDispatch(
    getSetViewSizeAction({
      height: document.documentElement.clientHeight,
      width: document.documentElement.clientWidth,
    })
  );

  useEffect(()=>{
    fetchGet(apiRequest.auth.users)
      .then((res) => {
        if(res && res.data.code == 1 && res.data.message == "未认证"){
          //message.warning("登录失效,请重新登录")
          history.replace("/login");
        }
        console.log(res)
      })
      .catch((e) => {
        console.log(e);
      })
      .finally(() => setLoading(false));
  },[])

  return (
    // <context.Provider value={{ state, dispatch }}>
      <Layout className={styles.OmpLayoutContainer}>
        <Header className={styles.OmpHeader}>
          <div className={styles.headerLogo}>
            <img src={img} />
          </div>
          <div
            style={{ cursor: "pointer", position:"relative",top:1 }}
            onClick={() => history.push("/homepage")}
          >
            运维管理平台
          </div>
          {headerLink.map((item, idx) => {
            return (
              <div
                style={
                  window.location.hash.includes(item.path)
                    ? { fontSize: 14, background: "#31405e", color: "#fff" }
                    : { fontSize: 14, cursor: disabled ? "not-allowed" : null }
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
                <span style={{position:"relative",top:1}}>{item.title}</span>
              </div>
            );
          })}
          <Button onClick={()=>{
            reduxDispatch({
              type: "c",
            })
          }}>点击</Button>
          <div className={styles.userAvatar}>
            <Dropdown overlay={menu} trigger={["click"]}>
              <div style={{ fontWeight: 500, fontSize: 14, cursor: "pointer" }}>
                {localStorage.getItem("username")}{" "}
                <CaretDownOutlined className={styles.userAvatarIcon} />
              </div>
            </Dropdown>
            <Dropdown
              trigger={["click"]}
              placement="bottomCenter"
              overlay={
                <Menu className="menu">
                  <Menu.Item>版本信息：V1.5.0</Menu.Item>
                </Menu>
              }
            >
              <div
                style={{
                  margin: "0 5px 0 22px",
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
        <Layout>
          <Sider width={240} className={styles.siteLayoutBackground}>
            {/* <div className={styles.MenuTop}>
              <OmpEnvSelect />
            </div> */}
            <Menu
              mode="inline"
              style={{ height:"100%",//"calc(100% - 52px)", 
              //paddingTop:3,
              borderRight: 0 }}
              theme="dark"
              onClick={onPathChange}
              onOpenChange={onOpenChange}
              openKeys={currentOpenedKeys}
              selectedKeys={selectedKeys}
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
          <Layout style={{ padding: "0 24px 24px" }}>
            <CustomBreadcrumb />
            <div
              style={{
                //padding: 20,
                paddingTop: 0,
                margin: 10,
                marginRight:0,
                paddingRight:10,
                height: "100%",
                overflowY: "auto",
                //backgroundColor:"#fff"
              }}
            >
              {props.children}
            </div>
          </Layout>
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
    // </context.Provider>
  );
};

export default OmpLayout;
