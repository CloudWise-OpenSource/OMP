import { OmpContentWrapper, OmpTable, OmpMessageModal } from "@/components";
import { Button } from "antd";
import { useState, useEffect, useRef } from "react";
import { handleResponse, _idxInit } from "@/utils/utils";
import { fetchGet } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";
//import updata from "@/store_global/globalStore";
import { useDispatch } from "react-redux";
import { ExclamationCircleOutlined } from "@ant-design/icons";
import getColumnsConfig from "./config/columns";
import { ImportPlanModal } from "./config/models";
import { useHistory } from "react-router-dom";

const DeploymentPlan = () => {
  const dispatch = useDispatch();
  const history = useHistory();

  const [loading, setLoading] = useState(false);

  const [searchLoading, setSearchLoading] = useState(false);

  //table表格数据
  const [dataSource, setDataSource] = useState([]);
  const [userListSource, setUserListSource] = useState([]);
  const [searchValue, setSearchValue] = useState("");
  const [selectValue, setSelectValue] = useState();

  const [labelControl, setLabelControl] = useState("plan_name");
  const [instanceSelectValue, setInstanceSelectValue] = useState("");

  const [operable, setOperable] = useState(false);

  // 导入弹框
  const [importPlan, setImportPlan] = useState(false);
  // 不可用弹框
  const [disableModal, setDisableModal] = useState(false);

  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
    ordering: "",
    searchParams: {},
  });
  const [showModal, setShowModal] = useState(false);

  const msgRef = useRef(null);

  // 获取导入模板按钮是否可操作
  function getOpreable() {
    fetchGet(apiRequest.deloymentPlan.deploymentOperable)
      .then((res) => {
        handleResponse(res, (res) => {
          if (res.code === 0 && res.data === true) {
            setOperable(true);
          }
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  }

  function fetchData(
    pageParams = { current: 1, pageSize: 10 },
    searchParams,
    ordering
  ) {
    setLoading(true);
    fetchGet(apiRequest.deloymentPlan.deploymentList, {
      params: {
        page: pageParams.current,
        size: pageParams.pageSize,
        ordering: ordering ? ordering : null,
        ...searchParams,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
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
        // 获取按钮是否可操作
        getOpreable();
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  }

  useEffect(() => {
    fetchData(pagination);
  }, []);

  //console.log(checkedList)
  // 防止在校验进入死循环
  const flag = useRef(null);

  return (
    <OmpContentWrapper>
      <div style={{ display: "flex" }}>
        <Button
          type="primary"
          onClick={() => {
            if (operable) setImportPlan(true);
            else setDisableModal(true);
          }}
        >
          导入模板
        </Button>
      </div>
      <div
        style={{
          border: "1px solid #ebeef2",
          backgroundColor: "white",
          marginTop: 10,
        }}
      >
        <OmpTable
          noScroll={true}
          loading={loading}
          onChange={(e, filters, sorter) => {
            let ordering = sorter.order
              ? `${sorter.order == "descend" ? "" : "-"}${sorter.columnKey}`
              : null;
            setTimeout(() => {
              fetchData(e, pagination.searchParams, ordering);
            }, 200);
          }}
          columns={getColumnsConfig(history)}
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

      <ImportPlanModal
        importPlan={importPlan}
        setImportPlan={setImportPlan}
      ></ImportPlanModal>

      <OmpMessageModal
        visibleHandle={[disableModal, setDisableModal]}
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
        noFooter={true}
      >
        <div style={{ padding: "20px" }}>
          已安装服务，快速部署仅在未安装任何服务状态下可用
          <div
            style={{
              textAlign: "center",
              position: "relative",
              bottom: -26,
            }}
          >
            <Button
              type="primary"
              onClick={() => {
                setDisableModal(false);
              }}
            >
              确定
            </Button>
          </div>
        </div>
      </OmpMessageModal>
    </OmpContentWrapper>
  );
};

export default DeploymentPlan;
