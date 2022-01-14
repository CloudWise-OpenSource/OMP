import { OmpContentWrapper, OmpTable, OmpMessageModal } from "@/components";
import { Button, message, Checkbox, Row, Col, Form, Input } from "antd";
import { useState, useEffect, useRef } from "react";
import { handleResponse, _idxInit } from "@/utils/utils";
import { fetchGet, fetchPost, fetchPatch } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import star from "./config/asterisk.svg";
import getColumnsConfig from "./config/columns";
import { SaveOutlined, ExclamationCircleOutlined } from "@ant-design/icons";
import { useHistory, useLocation } from "react-router-dom";

const BackupRecords = () => {
  const location = useLocation();

  const history = useHistory();

  const [loading, setLoading] = useState(false);
  const [deleteLoading, setDeleteLoadin] = useState(false);

  const [backupLoading, setBackupLoading] = useState(false);
  const [pushLoading, setPushLoading] = useState(false);

  //选中的数据
  const [checkedList, setCheckedList] = useState([]);

  //table表格数据
  const [dataSource, setDataSource] = useState([]);

  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    ordering: "",
    searchParams: {},
  });

  // 定义row存数据
  const [row, setRow] = useState({});

  // 备份
  const [backupModal, setBackupModal] = useState(false);
  // 删除文件
  const [deleteModal, setDeleteModal] = useState(false);
  const [deleteOneModal, setDeleteOneModal] = useState(false);

  // 备份组件全量数据
  const [canBackupIns, setCanBackupIns] = useState([]);
  // 选中数据
  const [backupIns, setBackupIns] = useState([]);
  // 邮件推送modal弹框
  const [pushAnalysisModal, setPushAnalysisModal] = useState(false);

  // 推送表单数据
  const [pushForm] = Form.useForm();
  // 点击推送按钮数据
  const [pushInfo, setPushInfo] = useState();

  // 列表查询
  function fetchData(
    pageParams = { current: 1, pageSize: 10 },
    searchParams,
    ordering
  ) {
    setLoading(true);
    fetchGet(apiRequest.dataBackup.queryBackupHistory, {
      params: {
        page: pageParams.current,
        size: pageParams.pageSize,
        ordering: ordering ? ordering : null,
        ...searchParams,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          setDataSource(res.data.results);
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
        location.state = {};
        setLoading(false);
      });
  }

  // 查询可选备份项目
  const queryCanBackup = () => {
    setLoading(true);
    fetchGet(apiRequest.dataBackup.queryCanBackup, {
      params: {
        env_id: 1,
      },
    })
      .then((res) => {
        handleResponse(res, () => {
          setCanBackupIns(res.data.data);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  };

  // 数据备份
  const backupData = () => {
    if (canBackupIns.length === 0) {
      message.warning("当前暂无可用的备份实例");
      return;
    }
    if (backupIns.length === 0) {
      message.warning("请选择您定时备份的实例后，再进行保存");
      return;
    }
    setBackupLoading(true);
    fetchPost(apiRequest.dataBackup.backupOnce, {
      body: {
        env_id: 1,
        backup_instances: backupIns,
      },
    })
      .then((res) => {
        if (res.data.code === 0) {
          message.success("数据备份任务已下发");
          setBackupModal(false);
          fetchData({
            current: pagination.current,
            pageSize: pagination.pageSize,
          });
        } else {
          message.warning(res.data.message);
        }
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setBackupLoading(false);
      });
  };

  const pushEmail = () => {
    setPushLoading(true);
    fetchPost(apiRequest.dataBackup.pushEmail, {
      body: {
        ...pushInfo,
        env_id: 1,
        to_users: pushForm.getFieldValue("email"),
      },
    })
      .then((res) => {
        if (res && res.data) {
          if (res.data.code == 1) {
            message.warning(res.data.message);
          }
          if (res.data.code == 0) {
            message.success("推送成功");
            setPushAnalysisModal(false);
            fetchData();
          }
        }
      })
      .catch((e) => console.log(e))
      .finally(() => setPushLoading(false));
  };

  // 删除
  const deleteBackup = (deleteType = null) => {
    setDeleteLoadin(true);
    fetchPost(apiRequest.dataBackup.deleteBackupFile, {
      body: {
        env_id: 1,
        ids: deleteType === "only" ? [row.id] : checkedList.map((e) => e.id),
      },
    })
      .then((res) => {
        if (res && res.data) {
          if (res.data.code == 1) {
            message.warning(res.data.message);
          }
          if (res.data.code == 0) {
            message.success("删除文件成功");
            setCheckedList([]);
            setDeleteModal(false);
            setDeleteOneModal(false);
            fetchData({
              current: pagination.current,
              pageSize: pagination.pageSize,
            });
          }
        }
      })
      .catch((e) => console.log(e))
      .finally(() => setDeleteLoadin(false));
  };

  useEffect(() => {
    fetchData({ current: pagination.current, pageSize: pagination.pageSize });
    queryCanBackup();
  }, []);

  return (
    <OmpContentWrapper>
      <div style={{ display: "flex" }}>
        <Button
          style={{ marginRight: 15 }}
          type="primary"
          onClick={() => {
            setBackupModal(true);
          }}
        >
          备份
        </Button>
        <Button
          style={{ marginRight: 15 }}
          type="primary"
          disabled={checkedList.length == 0}
          onClick={() => {
            checkedList.map((item, idx) => {
              setTimeout(() => {
                if (record.file_name || record.result === 1) {
                  // if (item.file_size == 0) {
                  //   message.warning("要下载的文件不存在");
                  //   setDownLoadModal(false);
                  //   queryListData(pagination);
                  //   return;
                  // }
                  let a = document.createElement("a");
                  a.setAttribute("id", `${idx}-downA`);
                  document.body.appendChild(a);
                  let dom = document.getElementById(`${idx}-downA`);
                  dom.href = `/download-backup/${item.file_name}`;
                  dom.click();
                  setTimeout(() => {
                    document.body.removeChild(dom);
                  }, 1000);
                } else {
                  message.warning("该任务文件不支持下载");
                }
              }, idx * 500);
              //}
            });
            queryListData(pagination);
          }}
        >
          下载
        </Button>
        <Button
          style={{ marginRight: 15 }}
          disabled={checkedList.length == 0}
          //type={"primary"}
          onClick={() => {
            setDeleteModal(true);
          }}
        >
          删除
        </Button>

        <div style={{ display: "flex", marginLeft: "auto" }}>
          <Button
            style={{ marginLeft: 10 }}
            onClick={() => {
              setCheckedList([]);
              fetchData({
                current: pagination.current,
                pageSize: pagination.pageSize,
              });
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
          //scroll={{ x: 1900 }}
          onChange={(e, filters, sorter) => {
            let ordering = sorter.order
              ? `${sorter.order == "descend" ? "" : "-"}${sorter.columnKey}`
              : null;
            setTimeout(() => {
              fetchData(e, pagination.searchParams, ordering);
            }, 200);
          }}
          columns={getColumnsConfig(setRow, setDeleteOneModal, {
            pushForm,
            setPushLoading,
            setPushAnalysisModal,
            setPushInfo,
          })}
          notSelectable={(record) => ({
            // 执行中、失败、文件删除不能选中
            disabled:
              record?.file_deleted === true ||
              record.result === 0 ||
              record.result === 2,
          })}
          dataSource={dataSource}
          pagination={{
            showSizeChanger: true,
            pageSizeOptions: ["10", "20", "50", "100"],
            showTotal: () => (
              <div
                style={{
                  display: "flex",
                  width: "200px",
                  justifyContent: "space-between",
                  lineHeight: 2.8,
                }}
              >
                <p>已选中 {checkedList.length} 条</p>
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
          checkedState={[checkedList, setCheckedList]}
        />
      </div>

      <OmpMessageModal
        visibleHandle={[backupModal, setBackupModal]}
        title={
          <span>
            <SaveOutlined
              style={{
                fontSize: 20,
                paddingRight: "10px",
                position: "relative",
                top: 2,
              }}
            />
            数据备份
          </span>
        }
        loading={backupLoading}
        onFinish={() => {
          backupData();
        }}
      >
        <div style={{ padding: "10px 20px 20px 20px" }}>
          <p>
            <span>
              <img
                src={star}
                style={{ position: "relative", top: -2, left: -3 }}
              />
              请选择要备份的实例 :
            </span>
          </p>
          {canBackupIns.length === 0 ? (
            <span style={{ marginLeft: 20, color: "#a7abb7" }}>
              暂无可选实例
            </span>
          ) : (
            <Checkbox.Group
              value={backupIns}
              onChange={(checkedValues) => {
                setBackupIns(checkedValues);
              }}
              style={{
                marginLeft: 20,
              }}
            >
              {canBackupIns.map((e) => {
                return (
                  <Row>
                    <Checkbox key={e} value={e} style={{ lineHeight: "32px" }}>
                      {e}
                    </Checkbox>
                  </Row>
                );
              })}
            </Checkbox.Group>
          )}
          <p
            style={{
              marginTop: 10,
              marginLeft: 6,
              fontSize: 14,
              color: "#595959",
            }}
          >
            是否确认对已选实例进行单次备份操作 ?
          </p>
        </div>
      </OmpMessageModal>

      <OmpMessageModal
        visibleHandle={[deleteModal, setDeleteModal]}
        title={
          <span>
            <ExclamationCircleOutlined
              style={{
                fontSize: 20,
                color: "#f0a441",
                paddingRight: "10px",
                position: "relative",
                top: 2,
              }}
            />
            提示
          </span>
        }
        loading={deleteLoading}
        onFinish={() => {
          deleteBackup();
        }}
      >
        <div style={{ padding: "20px" }}>
          确定要删除{" "}
          <span style={{ fontWeight: 500 }}>{checkedList.length}条</span> 记录的{" "}
          <span style={{ fontWeight: 500 }}>备份文件</span> ？
        </div>
      </OmpMessageModal>

      <OmpMessageModal
        visibleHandle={[deleteOneModal, setDeleteOneModal]}
        title={
          <span>
            <ExclamationCircleOutlined
              style={{
                fontSize: 20,
                color: "#f0a441",
                paddingRight: "10px",
                position: "relative",
                top: 2,
              }}
            />
            提示
          </span>
        }
        loading={deleteLoading}
        onFinish={() => {
          deleteBackup("only");
        }}
      >
        <div style={{ padding: "20px" }}>
          确定要删除 <span style={{ fontWeight: 500 }}>当前</span> 记录的{" "}
          <span style={{ fontWeight: 500 }}>备份文件</span> ？
        </div>
      </OmpMessageModal>

      <OmpMessageModal
        visibleHandle={[pushAnalysisModal, setPushAnalysisModal]}
        title={<span>邮件推送</span>}
        loading={pushLoading}
        onFinish={() => pushEmail()}
      >
        <Form style={{ marginLeft: 40 }} form={pushForm}>
          <Form.Item
            name="email"
            label="接收人"
            rules={[
              {
                type: "email",
                message: "请输入正确格式的邮箱",
              },
            ]}
          >
            <Input
              placeholder="例如: emailname@163.com"
              style={{
                width: 320,
              }}
            />
          </Form.Item>
          <p
            style={{
              marginTop: 30,
              paddingLeft: 40,
              fontSize: 13,
            }}
          >
            <ExclamationCircleOutlined style={{ paddingRight: 10 }} />
            如果需要配置默认的备份记录接收人，请点击
            <a
              onClick={() =>
                history.push({
                  pathname: "/data-backup/backup-strategy",
                })
              }
              style={{ marginLeft: 4 }}
            >
              这里
            </a>
          </p>
        </Form>
      </OmpMessageModal>
    </OmpContentWrapper>
  );
};

export default BackupRecords;
