import { Cascader, Form, Tag, Button, Tooltip } from "antd";
import { useEffect, useState, useRef } from "react";
import { useSelector, useDispatch } from "react-redux";
import {
  getDataSourceChangeAction,
  getIpListChangeAction,
} from "../../store/actionsCreators";
import * as R from "ramda";
import HasInstallService from "./component/HasInstallService";

// 当前组件一次value改变，伴随着三个动作
// 1. 组件state的value 的改变
// 2. redux中dataSource 的改变
//   （1）ipList 的改变，影响页面中`已分配主机数量`
//    (2) dataSource的改变 （对应组件中的option,决定组件展开框的渲染）
// 3. form中数据的变更

// 当前组件触发value改变的情况有
// 1. 点击展开栏的check或者item容器或者文字
// 2. 点击展示框的tag

// 未完成任务
// 3. 展示框关于with的处理

const ServiceDistributionItem = ({ form, data, info, installService }) => {
  const [options, setOption] = useState([]);

  const [value, setValue] = useState([]);

  const allDataPool = useSelector((state) => state.installation.dataSource);

  const ipList = useSelector((state) => state.installation.ipList);

  const errorList = useSelector((state) => state.installation.errorList);

  const errorMsg = errorList.filter((i) => i.ip == info.ip)[0]?.error_msg;

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
          console.log(item);
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

  // 当选中这项时同时拿到所有with这项的数据
  const getWithItem = (label) => {
    // 全部with当前项的数据
    const result = [];
    for (const key in allDataPool) {
      // console.log(allDataPool[key]);
      if (allDataPool[key].with && allDataPool[key].with == label) {
        result.push(key);
      }
    }
    return result;
  };

  // 封装对选中被其他项with关联的数据的处理（选中）
  const handleWithData = (label, withItem, isCheck) => {
    if (withItem.length > 0) {
      withItem.map((w) => {
        let formData = R.clone(form.getFieldsValue());
        // 确认with这项是属于哪个product
        let optionsCopy = R.clone(options);
        let productItem = optionsCopy.filter((item) => {
          let f = item.children.filter((i) => {
            return i.label == w;
          });
          return f.length !== 0;
        });
        if (isCheck) {
          formData[info.ip].push([productItem[0].label, w]);
          form.setFieldsValue({
            [`${info.ip}`]: formData[info.ip],
          });
          setValue(formData[info.ip]);
          // 数据池子中数量变更
          let data = handleDataSourceData(w, -1);
          reduxDispatch(getDataSourceChangeAction(data));
        } else {
          let withI = [productItem[0].label, w];
          let result = formData[info.ip].filter((item) => {
            return item[0] != withI[0] || item[1] != withI[1];
          });
          form.setFieldsValue({
            [`${info.ip}`]: result,
          });
          setValue(result);
          let data = handleDataSourceData(w, 1);
          reduxDispatch(getDataSourceChangeAction(data));
        }
      });
    } else {
      handleValueAndForm(label, isCheck);
    }
  };

  const handleValueAndForm = (label, isCheck) => {
    console.log(options, label);
    // value的格式[[1,1],[1,2]]
    // setValue()
    // form的格式
    // 当前ip下和value一致
    // 判断一下当前label是一级还是二级
    if (allDataPool[label]) {
      // 二级
      if (isCheck === true) {
        let result = [...value];
        options.map((item) => {
          item.children.map((i) => {
            if (i.value == label) {
              result.push([item.label, i.label]);
            }
          });
        });
        setValue(result);
        form.setFieldsValue({
          [`${info.ip}`]: result,
        });
      } else if (isCheck === false) {
        // 取消二级选中
        let result = [...value];
        let deleteItem = [];
        options.map((item) => {
          item.children.map((i) => {
            if (i.value == label) {
              deleteItem = [item.label, i.label];
            }
          });
        });
        result = result.filter((item) => {
          return item[0] != deleteItem[0] || item[1] != deleteItem[1];
        });
        setValue(result);
        form.setFieldsValue({
          [`${info.ip}`]: result,
        });
      }
    } else {
      // 一级
      if (isCheck === true) {
        // console.log("点击到了一级的选中");
        // console.log(options, isCheck);
        // 拿到一级下的全部子项
        let checkedArr = options
          .filter((i) => {
            return i.label == label;
          })[0]
          .children.map((i) => {
            return i.label;
          });
        // 去除其中带有with的
        checkedArr = checkedArr.filter((i) => {
          if (allDataPool[i] && allDataPool[i].with) {
            return false;
          }
          return true;
        });

        let result = checkedArr.map((item) => {
          return [label, item];
        });

        // 查找是否子项中有被其他项with的
        let withArr = [];
        options.map((item) => {
          item.children.map((i) => {
            // if(!allDataPool[i.label]){
            //   console.log(i.label)
            // }
            let withI = allDataPool[i.label].with;
            let idx = checkedArr.indexOf(withI);
            if (withI && idx !== -1) {
              result.push([item.label, i.label]);
              withArr.push(i.label);
            }
          });
        });
        let data = handleDataSourceData(withArr, -1);
        reduxDispatch(getDataSourceChangeAction(data));
        // console.log(value, result, label)
        let dealValue = value.filter(i=>{
          if(i[0] !== label){
            return true
          }
          //console.log(i)
          return false
        })
        setValue(Array.from(new Set([...dealValue,...result])));
        form.setFieldsValue({
          [`${info.ip}`]: Array.from(new Set([...dealValue,...result])),
        });
      } else if (isCheck === false) {
        // console.log("点击到了一级的取消选中");
        let withArr = [];
        let v = value.filter((i) => {
          // 当这项包含with直接留在这里不动，with项的改变在与被with项
          if (allDataPool[i[1]] && allDataPool[i[1]].with) {
            // 判断这项的with是否包涵在value
            console.log(allDataPool[i[1]].with, value);
            let arr = value.filter((a) => {
              return a[1] == allDataPool[i[1]].with;
            });
            withArr.push(i[1]);
            return arr.length == 0;
          }
          return i[0] !== label;
        });
        let data = handleDataSourceData(withArr, 1);
        reduxDispatch(getDataSourceChangeAction(data));
        setValue(v);
        form.setFieldsValue({
          [`${info.ip}`]: v,
        });
      }
    }
  };

  useEffect(() => {
    let isDelete = Object.keys(allDataPool).filter((k) => {
      // console.log(value);
      // 当前组件实例已经选中了，那即使在数据池中该数据num已经为0,也不应影响组件对该数据的展示,在这里过滤掉
      return allDataPool[k].num == 0 && !dealColumnsData(value).includes(k);
    });
    // console.log(isDelete, "isDelete");
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
        // 当前项如果存在with就不可选中
        i.children = item.child.map((n) => {
          let disabled = false;
          if (allDataPool[n] && allDataPool[n].with) {
            disabled = true;
          }
          return {
            label: n,
            value: n,
            disabled: disabled,
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

    // console.log(ipList, value, idx);
    if (value.length == 0) {
      if (idx !== -1) {
        //console.log([...ipList], info.ip);
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
    <div style={{ marginBottom: 40, width: "45%" }}>
      {/* <Button
        onClick={() => {
          console.log(value);
        }}
      >
        点击
      </Button> */}
      <Form form={form} name="service">
        <div style={{ display: "flex", justifyContent: "center" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              position: "relative",
            }}
          > 
            <div
              style={{
                position: "absolute",
                top: errorMsg?40:25,
                color: "red",
                height: errorMsg ? 20 : 0,
                transition: "all .1s ease-in",
              }}
            >
              {errorMsg}
            </div>
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
                value={value}
                //value={[["基础组件", "nacos"]]}//['douc', 'doucSso']
                // onChange={(e) => {
                //   let result = [];
                //   e.map((item) => {
                //     if (item.length == 1) {
                //       let key = item[0];
                //       let arr = options
                //         .filter((i) => {
                //           return i.label == key;
                //         })[0]
                //         .children.map((i) => {
                //           return [key, i.label];
                //         });
                //       arr = arr.filter((i) => {
                //         // 过滤掉with项
                //         if (allDataPool[i[1]] && allDataPool[i[1]].with) {
                //           return false;
                //         }
                //         return true;
                //       });
                //       result = result.concat(arr);
                //     } else {
                //       result.push(item);
                //     }
                //   });
                //   form.setFieldsValue({
                //     [`${info.ip}`]: result,
                //   });
                //   console.log(result,"这个result正常吗")
                //   setValue(result);
                // }}
                allowClear={false}
                tagRender={(e) => {
                  const { value, onClose, label } = e;
                  //console.log(value)
                  // label 可能是一级或者二级
                  // let checkedItem = options.filter((i) => {
                  //   return i.label == label;
                  // });
                  return (
                    <Tag
                      //closable={allDataPool[label] && !allDataPool[label].with}
                      closable={false}
                      // onClose={(event) => {
                      //   // 判断点的是一级还是二级
                      //   let checkedItem = options.filter((i) => {
                      //     return i.label == label;
                      //   });
                      //   if (checkedItem.length == 1) {
                      //     // 是第一级
                      //     let arr = checkedItem[0].children.map(
                      //       (item) => item.label
                      //     );
                      //     let data = handleDataSourceData(arr, 1);
                      //     reduxDispatch(getDataSourceChangeAction(data));
                      //   } else {
                      //     // 是第二级
                      //     let data = handleDataSourceData(label, 1);
                      //     reduxDispatch(getDataSourceChangeAction(data));
                      //   }
                      //   onClose(event);
                      // }}
                    >
                      {allDataPool[label] ? label : `${label}-集合`}
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
                      if (allDataPool[label] && allDataPool[label].with) {
                        return;
                      }
                      // with的判断不光是选中这项，还有判断当前选中这项有没有被其他的项with
                      let withItem = getWithItem(label);
                      // 有其他通过with关联选中项的数据都要进行选中处理
                      handleWithData(label, withItem, true);

                      handleValueAndForm(label);

                      let data = handleDataSourceData(label, -1);

                      // console.log(data);
                      reduxDispatch(getDataSourceChangeAction(data));
                    } else {
                      // 点的是一级
                      // 在这个条件中还有一个情况是半选中状态
                      //console.log("点击一级");
                      let checkedArr = options
                        .filter((i) => {
                          return i.label == label;
                        })[0]
                        .children.map((i) => {
                          return i.label;
                        });
                      // 对checkedArr再做一次过滤，过滤掉含有with的项
                      checkedArr = checkedArr.filter((i) => {
                        if (allDataPool[i] && allDataPool[i].with) {
                          return false;
                        }
                        return true;
                      });
                      // 还要过滤掉已经选中状态的
                      // value适配数据只要第二级数据
                      const hasCheck = value.map((item) => {
                        return item[1];
                      });

                      checkedArr = checkedArr.filter((i) => {
                        if (hasCheck.includes(i)) {
                          return false;
                        }
                        return true;
                      });

                      handleValueAndForm(label, true);
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
                      if (allDataPool[label] && allDataPool[label].with) {
                        return;
                      }
                      // 点的是二级
                      // console.log("取消选中了一级")
                      let withItem = getWithItem(label);
                      // 有其他通过with关联选中项的数据都要进行选中处理
                      handleWithData(label, withItem, false);

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
                      // 对checkedArr再做一次过滤，过滤掉含有with的项
                      checkedArr = checkedArr.filter((i) => {
                        if (allDataPool[i] && allDataPool[i].with) {
                          return false;
                        }
                        return true;
                      });
                      handleValueAndForm(label, false);
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
                      if (
                        allDataPool[e.target.lastChild.innerHTML] &&
                        allDataPool[e.target.lastChild.innerHTML].with
                      ) {
                        return;
                      }
                      // with的判断不光是选中这项，还有判断当前选中这项有没有被其他的项with
                      let withItem = getWithItem(e.target.lastChild.innerHTML);
                      // 有其他通过with关联选中项的数据都要进行选中处理
                      handleWithData(
                        e.target.lastChild.innerHTML,
                        withItem,
                        false
                      );

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
                      if (
                        allDataPool[e.target.lastChild.innerHTML] &&
                        allDataPool[e.target.lastChild.innerHTML].with
                      ) {
                        return;
                      }
                      // with的判断不光是选中这项，还有判断当前选中这项有没有被其他的项with
                      let withItem = getWithItem(e.target.lastChild.innerHTML);
                      // 有其他通过with关联选中项的数据都要进行选中处理
                      handleWithData(
                        e.target.lastChild.innerHTML,
                        withItem,
                        true
                      );

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
                      if (
                        allDataPool[e.target.innerHTML] &&
                        allDataPool[e.target.innerHTML].with
                      ) {
                        return;
                      }

                      // 取消选中
                      if (e.target.parentNode.childNodes.length === 2) {
                        // with的判断不光是选中这项，还有判断当前选中这项有没有被其他的项with
                        let withItem = getWithItem(e.target.innerHTML);
                        // 有其他通过with关联选中项的数据都要进行选中处理
                        handleWithData(e.target.innerHTML, withItem, false);
                        let data = handleDataSourceData(e.target.innerHTML, 1);
                        reduxDispatch(getDataSourceChangeAction(data));
                        // console.log("点击的是文字，取消", e.target.innerHTML);
                      }
                    } else {
                      if (
                        allDataPool[e.target.innerHTML] &&
                        allDataPool[e.target.innerHTML].with
                      ) {
                        return;
                      }

                      // 选中
                      if (e.target.parentNode.childNodes.length === 2) {
                        let withItem = getWithItem(e.target.innerHTML);
                        // 有其他通过with关联选中项的数据都要进行选中处理
                        handleWithData(e.target.innerHTML, withItem, true);
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
              // onClick={() => {
              //   // setOption([]);
              //   console.log(form.getFieldsValue());
              // }}
            >
              已安装服务数:{" "}
              {info.num == 0 ? (
                <span>0个</span>
              ) : (
                <HasInstallService ip={info.ip} installService={installService}>
                  {info.num}个
                </HasInstallService>
              )}
            </div>
          </div>
        </div>
      </Form>
    </div>
  );
};

export default ServiceDistributionItem;
