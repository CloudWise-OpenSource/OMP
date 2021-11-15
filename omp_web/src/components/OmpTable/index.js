/*
 * @Author: your name
 * @Date: 2021-06-28 16:04:55
 * @LastEditTime: 2021-06-28 16:41:31
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: /omp-fontend123/src/components/OmpTable/index.js
 */
import { Table, Pagination, Tree } from "antd";
import styles from "./index.module.less";
import { useEffect, useLayoutEffect, useState } from "react";
import { useSelector } from "react-redux";
import OmpTableFilter from "./components/OmpTableFilter";
import { SettingOutlined } from "@ant-design/icons";
import { columnsConfig } from "src/utils/utils";
import { createTrue } from "typescript";
// import * as R from "ramda"

const OmpTable = ({
  checkedState,
  columns,
  notSelectable,
  ...residualParam
}) => {
  const [checkedList, setCheckedList] = checkedState ? checkedState : [];
  // 视口高度
  const viewHeight = useSelector((state) => state.layouts.viewSize.height);
  // 视口宽度
  const viewWidth = useSelector((state) => state.layouts.viewSize.width);
  const [maxWidth, setMaxWidth] = useState(1900);

  // 表格项的筛选selectKey
  const [selectKeys, setSelectKeys] = useState(
    columns.map((item) => item.dataIndex)
  );

  // 当columns传入usefilter时，对该项做处理
  const extensionsColumns = columns.map((item, idx) => {
    // // 复制一下item
    // let item = R.clone(i);

    // // 当columns的width未设置时，直接添加width200,然后计算最大宽度
    // if (!item.width) {
    //   item = {
    //     width: 120,
    //     ellipsis: true,
    //     ...item,
    //   };
    // }

    //item.isShow = true;

    let lastIndex = columns.length - 1;
    if (idx == lastIndex) {
      return {
        ...item,
        filterIcon: (filtered) => <SettingOutlined />,
        filterDropdown: ({ confirm, clearFilters }) => (
          <div style={{ padding: 8, overflow: "hidden" }}>
            <Tree
              style={{
                left: -20,
                fontSize:13
              }}
              checkable
              switcherIcon={<SettingOutlined />}
              selectable={false}
              onCheck={(checkedKeys, info) => {
                setSelectKeys(checkedKeys);
              }}
              treeData={columns.map((item, idx)=>{
                return {
                  ...item,
                  disabled : idx == columns.length - 1 ? true:false
                }
              })}
              checkedKeys={selectKeys}
            />
          </div>
        ),
      };
    }

    // 筛选功能
    if (item.usefilter) {
      return {
        ...item,
        filterIcon: () => {
          return (
            <OmpTableFilter
              initfilter={item?.initfilter}
              dataIndex={item.dataIndex}
              filterMenuList={item.filterMenuList}
              queryRequest={item.queryRequest}
            />
          );
        },
        filters: [{ text: "mock", value: "mock" }],
        filterDropdown: () => {
          return <span key="mock_"></span>;
        },
      };
    }
    return {
      ...item,
    };
  });

  // 计算表格实际横向宽度（最大）
  // useLayoutEffect(() => {
  //   let maxW = 0
  //   extensionsColumns.map((item) => {
  //     maxW += item.width
  //   });
  //   console.log(maxW)
  //   setMaxWidth(maxW)
  //   //console.log(extensionsColumns)
  // }, []);

  // useEffect(()=>{

  // },[selectKeys])

  useLayoutEffect(() => {
    //console.log(viewHeight);
    // 为了能够让omptable能够根据视口高度进行自适应
    // 订出如下标准 视口高度大于955 设置 表格cell的padding为1rem
    // 视口高度大于 760 设置cell的padding为0.72rem
    let cellPadding = ".5";
    if (viewHeight > 955) {
      cellPadding = ".9";
    } else if (viewHeight <= 955 && viewHeight > 860) {
      cellPadding = ".75";
    } else if (viewHeight <= 860 && viewHeight > 760) {
      cellPadding = ".6";
    }
    try {
      //window.style = "body{background-color:blue;}";
      var stylee = document.createElement("style");
      stylee.type = "text/css";
      var sHtml = `
      .ant-table-thead > tr > th, .ant-table-tbody 
      > tr > td, .ant-table tfoot > 
      tr > th, .ant-table tfoot > tr > td {
            padding: ${cellPadding}rem;
        }`;
      stylee.innerHTML = sHtml;
      document.getElementsByTagName("head").item(0).appendChild(stylee);
    } catch (error) {
      console.log(error);
    }
  }, []);

  return (
    <Table
      //scroll={(viewWidth - 300) > maxWidth ? null : { x: (maxWidth + 30) }}
      scroll={viewWidth > 1900 ? null : { x: 1400 }}
      {...residualParam}
      columns={extensionsColumns.filter((i) => {
        return selectKeys.includes(i.dataIndex)
      })}
      //size="small"
      rowSelection={
        checkedState && {
          onSelect: (record, selected, selectedRows) => {
            setCheckedList({
              ...checkedList,
              [residualParam.pagination.current]: selectedRows,
            });
          },
          onSelectAll: (selected, selectedRows, changeRows) => {
            setCheckedList({
              ...checkedList,
              [residualParam.pagination.current]: selectedRows.filter(
                (item) => item
              ),
            });
          },
          getCheckboxProps:
            notSelectable ||
            ((record) => ({
              disabled: record.is_read === 1,
            })),
          selectedRowKeys: Object.keys(checkedList)
            .map((k) => checkedList[k])
            .flat(1)
            .map((item) => item?.id),
          // 传入rowselect优先使用传入的
          ...residualParam.rowSelection,
        }
      }
    />
  );
};

export default OmpTable;
