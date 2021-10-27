import React, { useEffect, useState } from "react";
import { useHistory } from "react-router-dom";
import { Button, Checkbox, Popover } from "antd";
import styles from "./index.module.less";
import * as R from "ramda";

const colorObj = {
  normal: {
    background: "#eefaf4",
    borderColor: "#54bba6",
  },
  critical: {
    background: "#fbe7e6",
    borderColor: "#da4e48",
  },
  warning: {
    background: "rgba(247, 231, 24, 0.2)",
    borderColor: "rgb(245, 199, 115)",
  },
};

function OmpStateBlock(props) {
  const history = useHistory();
  const { title, data = [] } = props;
  //console.log(data)
  const [currentData, setCurrentData] = useState([]);

  const [isShowAll, setIsShowAll] = useState(false);

  useEffect(() => {
    if (data && data.length > 0) {
      setCurrentData(sortData(data));
    }
  }, [data]);

  const sortData = (data) => {
    let normalArr = data.filter((i) => i.severity == "normal");
    let warningArr = data.filter((i) => i.severity == "warning");
    let criticalArr = data.filter((i) => i.severity == "critical");

    let result = criticalArr.concat(normalArr).concat(warningArr);
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
                      data.filter((i) => i.severity == "critical")
                    )
                  )
                );
              } else {
                setCurrentData(
                  sortData(currentData.filter((i) => i.severity !== "critical"))
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
                      data.filter((i) => i.severity == "normal")
                    )
                  )
                );
              } else {
                setCurrentData(
                  sortData(currentData.filter((i) => i.severity !== "normal"))
                );
              }
            }}
          >
            正常
          </Checkbox>

          {props.hasNotMonitored && (
            <Checkbox
              defaultChecked={true}
              onChange={(e) => {
                if (e.target.checked) {
                  setCurrentData(
                    sortData(
                      currentData.concat(
                        data.filter((i) => i.severity == "warning")
                      )
                    )
                  );
                } else {
                  setCurrentData(
                    sortData(
                      currentData.filter((i) => i.severity !== "warning")
                    )
                  );
                }
              }}
            >
              未监控
            </Checkbox>
          )}

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
                  item.severity == "critical"
                    ? props.criticalLink(item)
                    : props.link(item);
                }}
              >
                <Popover content={popContent(item || {})} title={"相关信息"}>
                  <Button
                    className={styles.stateButton}
                    style={colorObj[item.severity]}
                  >
                    <div>{item.instance_name}</div>
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
      <div className={styles.popContent}>
        {item.ip && (
          <span
            className={styles.ip}
            style={{ color: colorObj[item.severity]?.borderColor }}
          >
            {item.ip}
          </span>
        )}
        <span>
          {item.date ? (
            item.date
          ) : (
            <span style={{ color: colorObj[item.severity]?.borderColor }}>
              正常
            </span>
          )}
        </span>
        {item.describe && (
          <span>
            {item.describe.length > 100
              ? item.describe.slice(0, 100) + "..."
              : item.describe.slice(0, 100)}
          </span>
        )}
      </div>
    </div>
  );
}
