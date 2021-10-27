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
      setCurrentData(data);
    }
  }, [data]);

  return (
    <div className={styles.blockContent}>
      <div className={styles.checkboxGroup}>
        <span className={styles.blockTitle}>{title}</span>
        <div>
          <Checkbox
            defaultChecked={true}
            onChange={(e) => {
              // if (e.target.checked) {
              //   setCurrentData(
              //     R.defaultTo(
              //       [],
              //       data.filter((item) => !item.is_ok)
              //     ).concat(currentData)
              //   );
              // } else {
              //   setCurrentData(currentData.filter((item) => item.is_ok));
              // }
            }}
          >
            异常
          </Checkbox>
          <Checkbox
            defaultChecked={true}
            onChange={(e) => {
              // if (e.target.checked) {
              //   setCurrentData(
              //     currentData.concat(data.filter((item) => item.is_ok))
              //   );
              // } else {
              //   setCurrentData(currentData.filter((item) => !item.is_ok));
              // }
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
              <div key={`${title}-${idx}`} onClick={() => {}}>
                <Popover
                  // content={popContent(
                  //   R.sortWith([R.ascend(R.prop("is_ok"))])(
                  //     item.service_info
                  //   )
                  // )}
                  title={"信息"}
                >
                  <Button
                    className={styles.stateButton}
                    // style={
                    //   item.is_ok
                    //     ? {
                    //         background: "#eefaf4",
                    //         borderColor: "#54bba6",
                    //       }
                    //     : {
                    //         background: "#fbe7e6",
                    //         borderColor: "#da4e48",
                    //       }
                    // }
                    //type={"danger"}
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
