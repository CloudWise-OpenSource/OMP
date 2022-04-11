import {
    Input,
    Button,
    Pagination,
    Empty,
    Spin,
    Modal,
    Upload,
    message,
    Dropdown,
    Menu,
  } from "antd";
  import { useEffect, useRef, useState } from "react";
  import styles from "./index.module.less";
  import {
    SearchOutlined,
    DownloadOutlined,
    DownOutlined,
    SendOutlined,
    ScanOutlined,
    ArrowUpOutlined,
    SyncOutlined,
  } from "@ant-design/icons";
  import Card from "./config/card.js";
  import { useSelector, useDispatch } from "react-redux";
  import { useHistory } from "react-router-dom";
  import { fetchGet } from "@/utils/request";
  import { apiRequest } from "@/config/requestApi";
  import { handleResponse, downloadFile } from "@/utils/utils";

  const ToolManagement = () => {
    // 视口高度
    const viewHeight = useSelector((state) => state.layouts.viewSize.height);
    const history = useHistory();
    const [tabKey, setTabKey] = useState();

    const [searchName, setSearchName] = useState("");
  
    const [total, setTotal] = useState(0);
  
    const [loading, setLoading] = useState(false);
    const [dataSource, setDataSource] = useState([]);
    const [pagination, setPagination] = useState({
      current: 1,
      pageSize: viewHeight > 955 ? 16 : 12,
      total: 0,
      searchParams: {},
    });
  
    function fetchData(pageParams = { current: 1, pageSize: 8 }, searchParams) {
      setLoading(true);
      fetchGet(apiRequest.utilitie.queryList,
        {
          params: {
            page: pageParams.current,
            size: pageParams.pageSize,
            ...searchParams,
          },
        }
      )
        .then((res) => {
          handleResponse(res, (res) => {
            // 获得真正的总数，要查询条件都为空时
            let obj = { ...searchParams };
            delete obj.tabKey;
            let arr = Object.values(obj).filter((i) => i);
            if (arr.length == 0) {
              setTotal(res.data.count);
            }
            setDataSource(res.data.results);
            setPagination({
              ...pagination,
              total: res.data.count,
              pageSize: pageParams.pageSize,
              current: pageParams.current,
              searchParams: searchParams,
            });
          });
        })
        .catch((e) => console.log(e))
        .finally(() => {
          location.state = {};
          setLoading(false);
          // fetchSearchlist();
          //fetchIPlist();
        });
    }
  
    useEffect(() => {
      fetchData(
        { current: 1, pageSize: pagination.pageSize },
        {
          ...pagination.searchParams,
          kind: tabKey,
        }
      );
    }, [tabKey]);
  
    return (
      <div>
        <div className={styles.header}>
          <div className={styles.headerTabRow}>
            <div
              className={styles.headerTab}
              onClick={(e) => {
                setPagination({
                  current: 1,
                  pageSize: viewHeight > 955 ? 16 : 12,
                  total: 0,
                  searchParams: {},
                });
                if (e.target.innerHTML == "全部") {
                  setTabKey();
                } else if (e.target.innerHTML == "管理工具") {
                  setTabKey(0);
                }else if(e.target.innerHTML == "安全工具"){
                  setTabKey(2);
                }
              }}
            >
              <div
                style={
                  tabKey == undefined ? { color: "rgb(46, 124, 238)" } : {}
                }
              >
                全部
              </div>
              <div>|</div>
              <div
                style={tabKey == "0" ? { color: "rgb(46, 124, 238)" } : {}}
              >
                管理工具
              </div>
              <div>|</div>
              <div
                style={tabKey == "2" ? { color: "rgb(46, 124, 238)" } : {}}
              >
                安全工具
              </div>
            </div>
            <div className={styles.headerBtn}>
              <Input
                placeholder="请输入工具名称"
                suffix={
                  !searchName && <SearchOutlined style={{ color: "#b6b6b6" }} />
                }
                style={{ marginRight: 10, width: 280 }}
                value={searchName}
                allowClear
                onChange={(e) => {
                  setSearchName(e.target.value);
                  if (!e.target.value) {
                    fetchData(
                      {
                        current: 1,
                        pageSize: pagination.pageSize,
                      },
                      {
                        ...pagination.searchParams,
                        kind:tabKey,
                        name: null
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
                      name: searchName,
                      kind:tabKey
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
                      name: searchName,
                      kind:tabKey
                    }
                  );
                }}
              />
            </div>
          </div>
  
          <hr className={styles.headerHr} />
          <div className={styles.headerSearch}>
            <div
              className={styles.headerSearchCondition}
            >
              {/* <p
                style={searchKey == "全部" ? { color: "rgb(46, 124, 238)" } : {}}
              >
                全部
              </p> */}
            
            </div>
            <div className={styles.headerSearchInfo} style={{paddingTop:8}}>
              {/* <Button
                style={{ marginRight: 15, fontSize: 13 }}
                icon={<DownloadOutlined />}
                onClick={() => {
                  downloadFile(apiRequest.appStore.applicationTemplate);
                }}
              >
                <span style={{ color: "#818181" }}>下载发布说明</span>
              </Button> */}
              共收录 {total} 个实用工具
            </div>
          </div>
        </div>
        <Spin spinning={loading}>
          <div style={{ display: "flex", flexWrap: "wrap" }}>
            {dataSource.length == 0 ? (
              <Empty
                style={{
                  width: "100%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  height: viewHeight > 955 ? 500 : 300,
                  flexDirection: "column",
                }}
                description={"暂无使用工具"}
              />
            ) : (
              <>
                {dataSource.map((item, idx) => {
                  return (
                    <Card
                      history={history}
                      key={idx}
                      idx={idx + 1}
                      info={item}
                      tabKey={tabKey}
                    />
                  );
                })}
              </>
            )}
          </div>
        </Spin>
        {dataSource.length !== 0 && (
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              position: "relative",
              top: 25,
            }}
          >
            <Pagination
              onChange={(e) => {
                fetchData(
                  { ...pagination, current: e },
                  {
                    ...pagination.searchParams,
                    kind: tabKey,
                  }
                );
              }}
              current={pagination.current}
              pageSize={pagination.pageSize}
              total={pagination.total}
            />
          </div>
        )}
      </div>
    );
  };
  
  export default ToolManagement;
  