import { Cascader, Form, Tag } from "antd";
import { useEffect, useState, useRef } from "react";
import { useSelector, useDispatch } from "react-redux";
import { getDataSourceChangeAction } from "../../store/actionsCreators";

const ServiceDistributionItem = ({ form, data, info }) => {
  const [options, setOption] = useState([]);

  const [value, setValue] = useState([]);

  const allDataPool = useSelector((state) => state.installation.dataSource);

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
          allDataPool[item].num = allDataPool[item].num + num;
        }
      });
      return allDataPool;
    } else {
      if (allDataPool[key].num >= 0) {
        allDataPool[key].num = allDataPool[key].num + num;
      }
      return allDataPool;
    }
  };

  useEffect(() => {
    console.log(
      "======================================",
      allDataPool,
      info.ip,
      value
    );
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

  return (
    <div style={{ marginBottom: 30, width: "45%" }}>
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
                changeOnSelect={true}
                value={value}
                onChange={(e) => {
                  console.log(e);
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
                  setValue(result);
                }}
                allowClear={false}
                tagRender={(e) => {
                  // console.log(e.onClose);
                  // console.log(e);
                  const { value, onClose, label } = e;
                  return (
                    <Tag
                      closable
                      onClose={(event) => {
                        onClose(event);
                      }}
                    >
                      {label}
                    </Tag>
                  );
                }}
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
            <div style={{ fontSize: 13 }}>选择服务数: 0个</div>
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
