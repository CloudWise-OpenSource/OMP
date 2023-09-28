import { useEffect, useState } from "react";
import { useHistory } from "react-router-dom";
import { Button, Checkbox, Popover } from "antd";
import styles from "./index.module.less";

const colorObj = {
  normal: {
    background: "#eefaf4",
    borderColor: "#54bba6",
  },
  abnormal: {
    background: "#fbe7e6",
    borderColor: "#da4e48",
  },
  noMonitored: {
    background: "#e5e5e5",
    borderColor: "#aaaaaa",
  },
  warning: {
    background: "rgba(247, 231, 24, 0.2)",
    borderColor: "rgb(245, 199, 115)",
  },
};

function OmpStateBlock(props) {
  const history = useHistory();
  const { title, data = [] } = props;
  const [allData, setAllData] = useState([]);
  //console.log(data)
  const [currentData, setCurrentData] = useState([]);

  const [isShowAll, setIsShowAll] = useState(false);

  useEffect(() => {
    if (data && data.length > 0) {
      let handleData = data.map((item) => {
        //后端的critical和warning都渲染成红色，在前端对数据进行处理 noMonitored:"未监控" abnormal:"异常" normal:"正常"
        // let status = "noMonitored";
        // if (item.severity == "warning" || item.severity == "critical") {
        //   status = "abnormal";
        // } else if (item.severity == "normal") {
        //   status = "normal";
        // }
        // return {
        //   ...item,
        //   frontendStatus: status,
        // };

        let status = "noMonitored";
        if (item.severity == "critical") {
          status = "abnormal";
        } else if (item.severity == "normal") {
          status = "normal";
        } else if (item.severity == "warning") {
          status = "warning";
        }
        return {
          ...item,
          frontendStatus: status,
        };
      });
      setCurrentData(sortData(handleData));
      setAllData(sortData(handleData));
    }
  }, [data]);

  const sortData = (data) => {
    let normalArr = data.filter((i) => i.frontendStatus == "normal");
    let noMonitoredArr = data.filter((i) => i.frontendStatus == "noMonitored");
    let abnormalArr = data.filter((i) => i.frontendStatus == "abnormal");
    let warningArr = data.filter((i) => i.frontendStatus == "warning");

    let result = abnormalArr
      .concat(normalArr)
      .concat(noMonitoredArr)
      .concat(warningArr);
    return result;
  };

  return (
    <div className={styles.blockContent}>
      <div className={styles.checkboxGroup}>
        <span className={styles.blockTitle}>{title}</span>
        <div>
          <Checkbox
            defaultChecked={true}
            onChange={(e) => {
              if (e.target.checked) {
                setCurrentData(
                  sortData(
                    currentData.concat(
                      allData.filter(
                        (i) =>
                          i.frontendStatus == "abnormal" ||
                          i.frontendStatus == "warning"
                      )
                    )
                  )
                );
              } else {
                setCurrentData(
                  sortData(
                    currentData.filter(
                      (i) =>
                        i.frontendStatus !== "abnormal" ||
                        i.frontendStatus == "warning"
                    )
                  )
                );
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
                  sortData(
                    currentData.concat(
                      allData.filter((i) => i.frontendStatus == "normal")
                    )
                  )
                );
              } else {
                setCurrentData(
                  sortData(
                    currentData.filter((i) => i.frontendStatus !== "normal")
                  )
                );
              }
            }}
          >
            正常
          </Checkbox>

          <Checkbox
            defaultChecked={true}
            onChange={(e) => {
              if (e.target.checked) {
                setCurrentData(
                  sortData(
                    currentData.concat(
                      allData.filter((i) => i.frontendStatus == "noMonitored")
                    )
                  )
                );
              } else {
                setCurrentData(
                  sortData(
                    currentData.filter(
                      (i) => i.frontendStatus !== "noMonitored"
                    )
                  )
                );
              }
            }}
          >
            未监控
          </Checkbox>

          <Button
            className={styles.dropBtn}
            size={"small"}
            onClick={() => setIsShowAll(!isShowAll)}
          >
            {isShowAll ? "收起" : "展开"}
          </Button>
        </div>
      </div>
      {currentData.length > 0 ? (
        <div
          style={isShowAll ? {} : { maxHeight: 170, overflowY: "scroll" }}
          className={styles.blockItemWrapper}
        >
          {currentData.map((item, idx) => {
            return (
              <div
                key={`${title}-${idx}`}
                onClick={() => {
                  item.frontendStatus == "abnormal"
                    ? props.criticalLink(item)
                    : props.link(item);
                }}
              >
                <Popover content={popContent(item || {})} title={"相关信息"}>
                  <Button
                    className={styles.stateButton}
                    style={colorObj[item.frontendStatus]}
                  >
                    <div>{item.instance_name || item.ip}</div>
                  </Button>
                </Popover>
              </div>
            );
          })}
        </div>
      ) : (
        <div className={styles.emptyTable}>暂无数据</div>
      )}
    </div>
  );
}

export default OmpStateBlock;

function popContent(item) {
  return (
    <div>
      {item.info.map((i) => (
        <div className={styles.popContent}>
          {i.ip && (
            <span
              className={styles.ip}
              style={{ color: colorObj[item.frontendStatus]?.borderColor }}
            >
              {i.ip}
            </span>
          )}
          <span>
            {i.date ? (
              <span>{i.date}</span>
            ) : (
              <span
                style={{ color: colorObj[item.frontendStatus]?.borderColor }}
              >
                {item.frontendStatus === "noMonitored" ? "未监控" : "正常"}
              </span>
            )}
          </span>
          {i.describe && (
            <span>
              {i.describe.length > 100
                ? i.describe.slice(0, 100) + "..."
                : i.describe.slice(0, 100)}
            </span>
          )}
        </div>
      ))}
    </div>
  );
}
