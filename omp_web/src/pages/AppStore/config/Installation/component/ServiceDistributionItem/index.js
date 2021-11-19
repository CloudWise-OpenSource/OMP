import { Cascader, Form, Tag, Button, Tooltip } from "antd";
import { useEffect, useState, useRef } from "react";
import { useSelector, useDispatch } from "react-redux";
import {
  getDataSourceChangeAction,
  getIpListChangeAction,
} from "../../store/actionsCreators";

const ServiceDistributionItem = ({ form, data, info }) => {
  const [options, setOption] = useState([]);

  const [value, setValue] = useState([]);

  const allDataPool = useSelector((state) => state.installation.dataSource);

  const ipList = useSelector((state) => state.installation.ipList);

  const reduxDispatch = useDispatch();

  // 对value进行处理(因为当把某一级菜单下对应的全部二级菜单选中后，value会合并成一个，只会存展示一级菜单)
  const dealColumnsData = (value) => {
    let result = [];
    value.map((item) => {
      //console.log(item);
      switch (item.length) {
        case 1:
          // value长度为1时，代表选中全部的一级菜单
          let checkedItem = options
            .filter((i) => {
              return i.label == item[0];
            })[0]
            .children.map((i) => {
              return i.label;
            });
          result = result.concat([...checkedItem]);
          break;
        case 2:
          result.push(item[1]);
          break;
        default:
          return [];
          break;
      }
    });
    return result;
  };

  const handleDataSourceData = (key, num) => {
    if (Array.isArray(key)) {
      key.forEach((item) => {
        if (allDataPool[item].num >= 0) {
          let n =
            allDataPool[item].num + num <= 0 ? 0 : allDataPool[item].num + num;
          allDataPool[item].num = n;
        }
      });
      return allDataPool;
    } else {
      if (allDataPool[key].num >= 0) {
        let n =
          allDataPool[key].num + num <= 0 ? 0 : allDataPool[key].num + num;
        allDataPool[key].num = n;
      }
      return allDataPool;
    }
  };

  useEffect(() => {
    console.log(allDataPool, info.ip, value);
    let isDelete = Object.keys(allDataPool).filter((k) => {
      // 当前组件实例已经选中了，那即使在数据池中该数据num已经为0,也不应影响组件对该数据的展示,在这里过滤掉
      return allDataPool[k].num == 0 && !dealColumnsData(value).includes(k);
    });
    let c = [...data];
    c = c.map((i) => {
      // 去除在child对应数据池num为0的项
      let child = i.child.filter((e) => {
        return isDelete.indexOf(e) == -1;
      });

      return {
        ...i,
        child: child,
      };
    });

    setOption(() => {
      let result = [];
      c.map((item) => {
        let i = {
          label: item.name,
          value: item.name,
        };
        i.children = item.child.map((n) => {
          return {
            label: n,
            value: n,
          };
        });
        //console.log("child", item.child, dealColumnsData(value));
        if (item.child.length > 0 && dealColumnsData(value)) {
          result.push(i);
        }
      });
      // console.log(result);
      return result;
    });
  }, [allDataPool]);

  // 当value值发生改变时触发事件，用来判断当前组件所对应主机是否已经选择服务
  useEffect(() => {
    let idx = ipList.indexOf(info.ip);

    console.log(ipList, value, idx);
    if (value.length == 0) {
      if (idx !== -1) {
        console.log([...ipList], info.ip);
        let newIpList = [...ipList];
        newIpList.splice(idx, 1);
        reduxDispatch(getIpListChangeAction(newIpList));
      }
    } else {
      if (idx == -1) {
        let newIpList = [...ipList];
        newIpList.push(info.ip);
        reduxDispatch(getIpListChangeAction(newIpList));
      }
    }
  }, [value]);

  return (
    <div style={{ marginBottom: 30, width: "45%" }}>
      {/* <Button onClick={()=>{
        console.log(allDataPool)
      }}>点击</Button> */}
      <Form form={form} name="service">
        <div style={{ display: "flex", justifyContent: "center" }}>
          <div style={{ display: "flex", alignItems: "center" }}>
            <Form.Item
              label={info.ip}
              name={info.ip}
              style={{ marginBottom: 0 }}
            >
              <Cascader
                placeholder="请选择"
                style={{ width: 240, marginTop: 0, paddingLeft: 10 }}
                options={options}
                expandTrigger={"hover"}
                //value={[["基础组件", "nacos"]]}//['douc', 'doucSso']
                onChange={(e) => {
                  let result = [];
                  e.map((item) => {
                    if (item.length == 1) {
                      let key = item[0];
                      let arr = options
                        .filter((i) => {
                          return i.label == key;
                        })[0]
                        .children.map((i) => {
                          return [key, i.label];
                        });
                      console.log(arr);
                      result = result.concat(arr);
                    } else {
                      result.push(item);
                    }
                  });
                  form.setFieldsValue({
                    [`${info.ip}`]: result,
                  });
                  setValue(result);
                }}
                allowClear={false}
                tagRender={(e) => {
                  const { value, onClose, label } = e;
                  // label 可能是一级或者二级
                  return (
                    <Tag
                      closable
                      onClose={(event) => {
                        // 判断点的是一级还是二级
                        let checkedItem = options.filter((i) => {
                          return i.label == label;
                        });
                        if (checkedItem.length == 1) {
                          // 是第一级
                          let arr = checkedItem[0].children.map(
                            (item) => item.label
                          );
                          let data = handleDataSourceData(arr, 1);
                          reduxDispatch(getDataSourceChangeAction(data));
                        } else {
                          // 是第二级
                          let data = handleDataSourceData(label, 1);
                          reduxDispatch(getDataSourceChangeAction(data));
                        }
                        onClose(event);
                      }}
                    >
                      {label}
                    </Tag>
                  );
                }}
                // tagRender={(e) => {
                //   // console.log(e.onClose);
                //   // console.log(e);
                //   const { value, onClose, label } = e;
                //   console.log(value);
                //   if (value.includes("__RC_CASCADER_SPLIT__")) {
                //     return (
                //       <Tag
                //         // closable
                //         // onClose={(event) => {
                //         //   onClose(event);
                //         // }}
                //       >
                //         {label}
                //       </Tag>
                //     );
                //   } else {
                //     // 选中了一级菜单
                //     console.log(value);
                //     let checkedItem = options
                //       .filter((i) => {
                //         return i.label == value;
                //       })[0]
                //       .children.map((i) => {
                //         return i.label;
                //       });
                //     console.log(checkedItem);
                //     return (
                //       <>
                //         {checkedItem.map((item) => {
                //           return (
                //             <Tag
                //               key={item}
                //               // closable
                //               // onClose={(event) => {
                //               //   onClose(event);
                //               // }}
                //             >
                //               {item}
                //             </Tag>
                //           );
                //         })}
                //       </>
                //     );
                //   }
                // }}
                onClick={(e) => {
                  // 使用onclick的原因是因为onchange在每次点击后会触发两次，
                  // 每次onchange执行都是一次单独逻辑,不能在每次onchange时，故不能准确对应整个数据池的num增减情况
                  // 点击总共会出现三种情况
                  // 1. 点击了checkbox
                  // 2. 点击了背后的容器
                  // 3. 点击了文字
                  // console.log(e.target);

                  // 1. 点击了checkbox(这个比较特殊，也可能是点击了一级菜单触发)
                  if (e.target.className == "ant-cascader-checkbox-inner") {
                    // 选中（可能是一级也可能是二级,点击了checkbox）
                    // 判断是点击的一级还是二级
                    let label =
                      e.target.parentNode.parentNode.childNodes[1].innerHTML;
                    if (allDataPool[label]) {
                      // 点的是二级
                      let data = handleDataSourceData(label, -1);
                      reduxDispatch(getDataSourceChangeAction(data));
                    } else {
                      // 点的是一级
                      //console.log("点击一级");
                      let checkedArr = options
                        .filter((i) => {
                          return i.label == label;
                        })[0]
                        .children.map((i) => {
                          return i.label;
                        });
                      let data = handleDataSourceData(checkedArr, -1);
                      reduxDispatch(getDataSourceChangeAction(data));
                    }
                    // console.log(
                    //   "选中",
                    //   e.target.parentNode.parentNode.childNodes[1].innerHTML
                    // );
                  } else if (
                    e.target.className ==
                    "ant-cascader-checkbox ant-cascader-checkbox-checked"
                  ) {
                    // reduxDispatch(getDataSourceChangeAction(data));
                    // 取消选中（可能是一级也可能是二级,点击了checkbox
                    // 判断是点击的一级还是二级
                    let label = e.target.parentNode.childNodes[1].innerHTML;
                    if (allDataPool[label]) {
                      // 点的是二级
                      let data = handleDataSourceData(label, 1);
                      reduxDispatch(getDataSourceChangeAction(data));
                    } else {
                      // 点的是一级
                      let checkedArr = options
                        .filter((i) => {
                          return i.label == label;
                        })[0]
                        .children.map((i) => {
                          return i.label;
                        });
                      let data = handleDataSourceData(checkedArr, 1);
                      reduxDispatch(getDataSourceChangeAction(data));
                    }
                    // console.log(
                    //   "取消选中",
                    //   e.target.parentNode.childNodes[1].innerHTML
                    // );
                  }

                  // 2. 点击了背后的容器
                  if (
                    e.target.className == "ant-cascader-menu-item" ||
                    e.target.className ==
                      "ant-cascader-menu-item ant-cascader-menu-item-active"
                  ) {
                    if (e.target.getAttribute("aria-checked") === "true") {
                      let data = handleDataSourceData(
                        e.target.lastChild.innerHTML,
                        1
                      );
                      reduxDispatch(getDataSourceChangeAction(data));
                      // console.log(
                      //   "点击了背后容器，取消",
                      //   e.target.lastChild.innerHTML
                      // );
                    } else {
                      let data = handleDataSourceData(
                        e.target.lastChild.innerHTML,
                        -1
                      );
                      reduxDispatch(getDataSourceChangeAction(data));
                      // console.log(
                      //   "点击了背后容器，选中",
                      //   e.target.lastChild.innerHTML
                      // );
                    }
                  }

                  // 3. 点击了文字
                  if (e.target.className == "ant-cascader-menu-item-content") {
                    // 这个文字要判断是一级还是二级
                    // 判断是选中还是取消选中
                    if (
                      e.target.parentNode.getAttribute("aria-checked") ===
                      "true"
                    ) {
                      // 取消选中
                      if (e.target.parentNode.childNodes.length === 2) {
                        let data = handleDataSourceData(e.target.innerHTML, 1);
                        reduxDispatch(getDataSourceChangeAction(data));
                        // console.log("点击的是文字，取消", e.target.innerHTML);
                      }
                    } else {
                      // 选中
                      if (e.target.parentNode.childNodes.length === 2) {
                        let data = handleDataSourceData(e.target.innerHTML, -1);
                        reduxDispatch(getDataSourceChangeAction(data));
                        //console.log("点击的是文字，选中", e.target.innerHTML);
                      }
                    }
                  }
                }}
                multiple="multiple"
                maxTagCount="responsive"
              />
            </Form.Item>
          </div>
          <div style={{ paddingLeft: 15 }}>
            <div style={{ fontSize: 13 }}>
              选择服务数:{" "}
              {value.length == 0 ? (
                <span>0个</span>
              ) : (
                <Tooltip
                  mouseEnterDelay={0.3}
                  placement="right"
                  color="#fff"
                  title={
                    <div
                      style={{
                        color: "rgba(0, 0, 0, 0.85)",
                        padding: 5,
                      }}
                    >
                      <div
                        style={{
                          borderBottom: "1px solid #d9d9d9",
                          fontSize: 13,
                          paddingBottom: 5,
                        }}
                      >
                        已选服务
                      </div>
                      <div
                        style={{
                          overflowY: "auto",
                          height: 100,
                        }}
                      >
                        {value.map((item) => {
                          return (
                            <div
                              style={{ paddingTop: 5, fontSize: 13 }}
                              key={`${item[0]}/${item[1]}`}
                            >
                              {`${item[0]} / ${item[1]}`}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  }
                >
                  <a>{value.length}个</a>
                </Tooltip>
              )}
            </div>
            <div
              style={{ fontSize: 12 }}
              onClick={() => {
                // setOption([]);
                console.log(form.getFieldsValue());
              }}
            >
              已安装服务数: <a>{info.num}个</a>
            </div>
          </div>
        </div>
      </Form>
    </div>
  );
};

export default ServiceDistributionItem;
