import { OmpContentWrapper, OmpTable, OmpMessageModal } from "@/components";
import { Button, message } from "antd";
import { useState, useEffect } from "react";
import { handleResponse, _idxInit } from "@/utils/utils";
import { fetchGet, fetchPost } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
import getColumnsConfig from "./config/columns";
import {
  ExclamationCircleOutlined,
} from "@ant-design/icons";
import { useHistory, useLocation } from "react-router-dom";

const BackupRecords = () => {
  const location = useLocation();

  const history = useHistory();

  const [loading, setLoading] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);

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

  // 删除文件
  const [deleteModal, setDeleteModal] = useState(false);
  const [deleteOneModal, setDeleteOneModal] = useState(false);

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

  // 删除
  const deleteBackup = (deleteType = null) => {
    setDeleteLoading(true);
    fetchPost(apiRequest.dataBackup.queryBackupHistory, {
      body: {
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
      .finally(() => setDeleteLoading(false));
  };

  useEffect(() => {
    fetchData({ current: pagination.current, pageSize: pagination.pageSize });
  }, []);

  return (
    <OmpContentWrapper>
      <div style={{ display: "flex" }}>
        {/* <Button
          style={{ marginRight: 15 }}
          type="primary"
          disabled={checkedList.length == 0}
          onClick={() => {
            checkedList.map((item, idx) => {
              setTimeout(() => {
                if (item.file_name || item.result === 1) {
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
          }}
        >
          下载
        </Button> */}
        <Button
          style={{ marginRight: 15 }}
          disabled={checkedList.length == 0}
          type="primary"
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
          onChange={(e, filters, sorter) => {
            let ordering = sorter.order
              ? `${sorter.order == "descend" ? "" : "-"}${sorter.columnKey}`
              : null;
            setTimeout(() => {
              fetchData(e, pagination.searchParams, ordering);
            }, 200);
          }}
          columns={getColumnsConfig(setRow, setDeleteOneModal)}
          notSelectable={(record) => ({
            // 执行中不能选中
            disabled: record.result === 2,
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
          确定{" "}
          <span style={{ fontWeight: 500 }}>删除 {checkedList.length} </span> 条{" "}
          <span style={{ fontWeight: 500 }}>备份记录</span> 吗？
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
          确定 <span style={{ fontWeight: 500 }}>删除</span> 当前{" "}
          <span style={{ fontWeight: 500 }}>备份记录</span> 吗？
        </div>
      </OmpMessageModal>
    </OmpContentWrapper>
  );
};

export default BackupRecords;
