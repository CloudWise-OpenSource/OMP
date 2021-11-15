import { OmpContentWrapper, OmpTable, OmpModal } from "@/components";
import { Button, Input, Form, message, Menu } from "antd";
import { useState, useEffect, useRef } from "react";
import {
  handleResponse,
  _idxInit,
  refreshTime,
  MessageTip,
  nonEmptyProcessing,
  logout,
  isPassword,
} from "@/utils/utils";
import { fetchGet, fetchPost } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
//import updata from "@/store_global/globalStore";
import { useDispatch } from "react-redux";
import moment from "moment";
import { SearchOutlined, SettingFilled } from "@ant-design/icons";

const UserManagement = () => {
  const dispatch = useDispatch();

  const [loading, setLoading] = useState(false);

  const [searchLoading, setSearchLoading] = useState(false);

  //选中的数据
  const [checkedList, setCheckedList] = useState({});

  //table表格数据
  const [dataSource, setDataSource] = useState([]);
  const [userListSource, setUserListSource] = useState([]);
  const [searchValue, setSearchValue] = useState("");
  const [selectValue, setSelectValue] = useState();

  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    ordering: "",
    searchParams: {},
  });

  //修改密码弹框
  const [showModal, setShowModal] = useState(false);

  const columns = [
    {
      title: "序列",
      width: 80,
      key: "_idx",
      dataIndex: "_idx",
      //sorter: (a, b) => a.username - b.username,
      // sortDirections: ["descend", "ascend"],
      align: "center",
      render: nonEmptyProcessing,
      fixed: "left",
    },
    {
      title: "用户名",
      key: "username",
      width: 120,
      dataIndex: "username",
      //sorter: (a, b) => a.username - b.username,
      // sortDirections: ["descend", "ascend"],
      align: "center",
      render: nonEmptyProcessing,
    },
    {
      title: "角色",
      key: "is_superuser",
      dataIndex: "is_superuser",
      width: 100,
      //sorter: (a, b) => a.is_superuser - b.is_superuser,
      //sortDirections: ["descend", "ascend"],
      align: "center",
      render: (text) => {
        if (text) {
          return "普通管理员";
        } else {
          return "超级管理员";
        }
      },
    },
    {
      title: "用户状态",
      key: "is_active",
      dataIndex: "is_active",
      align: "center",
      width: 100,
      render: (text) => {
        if (text) {
          return "正常";
        } else {
          return "停用";
        }
      },
    },
    {
      title: "创建时间",
      key: "date_joined",
      dataIndex: "date_joined",
      align: "center",
      width: 120,
      render: (text) => {
        if (text) {
          return moment(text).format("YYYY-MM-DD HH:mm:ss");
        } else {
          return "-";
        }
      },
    },
    // {
    //   title: "描述",
    //   key: "describe",
    //   dataIndex: "describe",
    //   align: "center",
    //   render: nonEmptyProcessing,
    // },
    {
      title: "用户操作",
      key: "1",
      width: 80,
      dataIndex: "1",
      align: "center",
      fixed: "right",
      render: function renderFunc(text, record, index) {
        return (
          <div
            onClick={() => {
              setRow(record);
              setShowModal(true);
            }}
            style={{ display: "flex", justifyContent: "space-around" }}
          >
            <a>修改密码</a>
          </div>
        );
      },
    },
  ];

  const msgRef = useRef(null);

  //select 的onblur函数拿不到最新的search value,使用useref存(是最新的，但是因为失去焦点时会自动触发清空search，还是得使用ref存)
  const searchValueRef = useRef(null);

  // 定义row存数据
  const [row, setRow] = useState({});

  //auth/users
  function fetchData(
    pageParams = { current: 1, pageSize: 10 },
    searchParams,
    ordering
  ) {
    setLoading(true);
    fetchGet(apiRequest.auth.users, {
      params: {
        page: pageParams.current,
        size: pageParams.pageSize,
        ordering: ordering ? ordering : null,
        ...searchParams,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          if (!searchParams) {
            setUserListSource(res.data.results.map((item) => item.username));
          }
          setDataSource(
            res.data.results.map((item, idx) => {
              return {
                ...item,
                _idx: idx + 1 + (pageParams.current - 1) * pageParams.pageSize,
              };
            })
          );
          setPagination({
            ...pagination,
            total: res.data.count,
            pageSize: pageParams.pageSize,
            current: pageParams.current,
            ordering: ordering,
            searchParams: searchParams,
          });
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  }

  const onPassWordChange = (data) => {
    setLoading(true);
    fetchPost(apiRequest.auth.changePassword, {
      body: {
        username: row.username,
        old_password: data.old_password,
        new_password: data.new_password2,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.code == 0) {
            if (localStorage.getItem("username") == row.username) {
              message.success("修改密码成功, 请重新登录");
              setTimeout(() => {
                logout();
              }, 1000);
            } else {
              message.success("修改密码成功");
            }
            setShowModal(false);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchData(pagination);
  }, []);

  //console.log(checkedList)
  // 防止在校验进入死循环
  const flag = useRef(null);

  return (
    <OmpContentWrapper>
      <div style={{ display: "flex" }}>
        <div style={{ display: "flex", marginLeft: "auto" }}>
          <span style={{ width: 60, display: "flex", alignItems: "center" }}>
            用户名:
          </span>
          {/* <Input.Search placeholder="请输入用户名"
          allowClear
          onSearch={(e)=>{
              setSelectValue(e)
              console.log(e)
              fetchData(
                { current: pagination.current, pageSize: pagination.pageSize },
                {username:e},
                pagination.ordering
              );
          }} 
          style={{ width: 200 }} /> */}
          <Input
            placeholder="请输入用户名"
            style={{ width: 200 }}
            allowClear
            value={selectValue}
            onChange={(e) => {
              setSelectValue(e.target.value);
              if (!e.target.value) {
                fetchData(
                  {
                    current: 1,
                    pageSize: pagination.pageSize,
                  },
                  {
                    ...pagination.searchParams,
                    username: null,
                  }
                );
              }
            }}
            onBlur={() => {
              fetchData(
                {
                  current: 1,
                  pageSize: pagination.pageSize,
                },
                {
                  ...pagination.searchParams,
                  username: selectValue,
                }
              );
            }}
            onPressEnter={() => {
              fetchData(
                {
                  current: 1,
                  pageSize: pagination.pageSize,
                },
                {
                  ...pagination.searchParams,
                  username: selectValue,
                },
                pagination.ordering
              );
            }}
            suffix={
              !selectValue && (
                <SearchOutlined style={{ fontSize: 12, color: "#b6b6b6" }} />
              )
            }
          />
          <Button
            style={{ marginLeft: 10 }}
            onClick={() => {
              dispatch(refreshTime());
              // console.log(pagination, "hosts/hosts/?page=1&size=10");
              fetchData(
                { current: pagination.current, pageSize: pagination.pageSize },
                { username: selectValue },
                pagination.ordering
              );
            }}
          >
            刷新
          </Button>
        </div>
      </div>
      <div
        style={{
          border: "1px solid #ebeef2",
          backgroundColor: "white",
          marginTop: 10,
        }}
      >
        <OmpTable
          loading={loading}
          onChange={(e, filters, sorter) => {
            let ordering = sorter.order
              ? `${sorter.order == "descend" ? "" : "-"}${sorter.columnKey}`
              : null;
            setTimeout(() => {
              fetchData(e, pagination.searchParams, ordering);
            }, 200);
          }}
          columns={columns}
          dataSource={dataSource}
          pagination={{
            showSizeChanger: true,
            pageSizeOptions: ["10", "20", "50", "100"],
            showTotal: () => (
              <div
                style={{
                  display: "flex",
                  width: "200px",
                  lineHeight: 2.8,
                  flexDirection: "row-reverse",
                }}
              >
                <p style={{ color: "rgb(152, 157, 171)" }}>
                  共计{" "}
                  <span style={{ color: "rgb(63, 64, 70)" }}>
                    {pagination.total}
                  </span>{" "}
                  条
                </p>
              </div>
            ),
            ...pagination,
          }}
          rowKey={(record) => record.id}
        />
      </div>
      <OmpModal
        loading={loading}
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
    </OmpContentWrapper>
  );
};

export default UserManagement;
