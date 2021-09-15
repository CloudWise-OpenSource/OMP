import React, { useEffect, useState } from "react";
import { useHistory } from "react-router-dom";
import { Button, Checkbox, Popover } from "antd";
import styles from "./index.module.less";
import * as R from "ramda";

function OmpStateBlock(props) {
  const history = useHistory();
  const { title, data = [] } = props;
  const [currentData, setCurrentData] = useState([]);

  const [isShowAll, setIsShowAll] = useState(false);

  useEffect(() => {
    if (data && data.length > 0) {
      const normal = data.filter((item) => item.is_ok);
      const abnormal = data.filter((item) => !item.is_ok);
      setCurrentData(abnormal.concat(normal));
    }
  }, [data]);

  return (
    <div
      className={styles.blockContent}
    > 
      <div className={styles.checkboxGroup}>
        <span className={styles.blockTitle}>{title}</span>
        <div>
          <Checkbox
          defaultChecked={true}
          onChange={(e) => {
            if (e.target.checked) {
              setCurrentData(
                R.defaultTo(
                  [],
                  data.filter((item) => !item.is_ok)
                ).concat(currentData)
              );
            } else {
              setCurrentData(currentData.filter((item) => item.is_ok));
            }
          }}
        >
          异常
        </Checkbox>
        <Checkbox
          defaultChecked={true}
          onChange={(e) => {
            if (e.target.checked) {
              setCurrentData(
                currentData.concat(data.filter((item) => item.is_ok))
              );
            } else {
              setCurrentData(currentData.filter((item) => !item.is_ok));
            }
          }}
        >
          正常
        </Checkbox>

        <Button
          className={styles.dropBtn}
          size={"small"}
          onClick={() => setIsShowAll(!isShowAll)}
        >
          {isShowAll ? "收起" : "展开"}
        </Button></div>
        
      </div>
      {currentData.length > 0 ? (
        <div style={isShowAll ? {} : { maxHeight: 170, overflowY: "scroll" }}
             className={styles.blockItemWrapper}>
          {
            // currentData.length > 0 ? (
            currentData.map((item, idx) => {
              return (
                <div
                  key={`${title}-${idx}`}
                  onClick={() => {
                    if (item.service_info && item.is_ok) {
                      history.push({
                        pathname: "/products-management/service",
                        state: {
                          service_name: item.name,
                          key: props.tag,
                        },
                      });
                    } else if (item.service_info) {
                      // if(props.tag=="thirdParty"){
                      //   history.push({
                      //     pathname: "/operation-management/warnings",
                      //     state: {
                      //       host_ip: item.service_info[0].ip,
                      //       key:props.tag
                      //     },
                      //   });
                      // }else{
                      history.push({
                        pathname: "/operation-management/warnings",
                        state: {
                          service_name: item.name,
                          key: props.tag,
                        },
                      });
                      //}
                    } else {
                      if (item.is_ok) {
                        history.push({
                          pathname: "/machine-management/list",
                          state: {
                            host_ip: item.host_ip,
                            key: props.tag,
                          },
                        });
                      } else {
                        history.push({
                          pathname: "/operation-management/warnings",
                          state: {
                            host_ip: item.host_ip,
                            key: props.tag,
                          },
                        });
                      }
                    }
                  }}
                >
                  {item.service_info ? (
                    <Popover
                      content={popContent(
                        R.sortWith([R.ascend(R.prop("is_ok"))])(
                          item.service_info
                        )
                      )}
                      title={(props.tag=="basic"||props.tag=="thirdParty")?"组件信息":"服务信息"}
                    >
                      <Button
                        className={styles.stateButton}
                        style={
                          item.is_ok
                            ? {
                                background: "#eefaf4",
                                borderColor: "#54bba6",
                              }
                            : {
                                background: "#fbe7e6",
                                borderColor: "#da4e48",
                              }
                        }
                        //type={"danger"}
                      >
                        <div>{item.name}</div>
                      </Button>
                    </Popover>
                  ) : item.describe && item.describe.length > 0 ? (
                    // 主机有错误信息时才提示
                    <Popover
                      content={popContent(item.describe)}
                      title="主机信息"
                    >
                      <Button
                        className={styles.stateButton}
                        style={
                          item.is_ok
                            ? {
                                background: "#54bba6",
                                borderColor: "#54bba6",
                              }
                            : {
                                background: "#fbe7e6",
                                borderColor: "#da4e48",
                              }
                        }
                        //type={"danger"}
                      >
                        {item.host_ip}
                      </Button>
                    </Popover>
                  ) : (
                    <Button
                      className={styles.stateButton}
                      style={
                        item.is_ok
                          ? {
                              background: "#eefaf4",
                              borderColor: "#54bba6",
                            }
                          : {
                              background: "#fbe7e6",
                              borderColor: "#da4e48",
                            }
                      }
                      //type={"danger"}
                    >
                      {item.host_ip}
                    </Button>
                  )}
                </div>
              );
            })
          }
        </div>
      ) : (
        <div className={styles.emptyTable}>暂无数据</div>
      )}
    </div>
  );
}

export default OmpStateBlock;

function popContent(info) {
  return (
    <div>
      {info.map((item, idx) => (
        <div className={styles.popContent} key={idx}>
          {item.ip && (
            <span
              className={styles.ip}
              style={item.is_ok ? { color: "#54bba6" } : { color: "#df7071" }}
            >
              {item.ip}
            </span>
          )}
          <span>{item.time}</span>
          {item.describe && (
            <span>
              {item.describe.length > 100
                ? item.describe.slice(0, 100) + "..."
                : item.describe.slice(0, 100)}
            </span>
          )}
        </div>
      ))}
    </div>
  );
}
