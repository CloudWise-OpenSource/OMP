/*
 * @Author: your name
 * @Date: 2021-06-28 16:04:55
 * @LastEditTime: 2021-06-28 16:41:31
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: /omp-fontend123/src/components/OmpTable/index.js
 */
import { Table, Pagination } from "antd";
import styles from "./index.module.less";
import { useLayoutEffect } from "react";
import { useSelector } from "react-redux";
import OmpTableFilter from "./components/OmpTableFilter";

const OmpTable = ({
  checkedState,
  columns,
  notSelectable,
  ...residualParam
}) => {
  // console.log(residualParam)
  // 当columns传入usefilter时，对该项做处理
  const extensionsColumns = columns.map((item) => {
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

  const [checkedList, setCheckedList] = checkedState ? checkedState : [];
  // 视口高度
  const viewHeight = useSelector((state) => state.layouts.viewSize.height);
  // 视口宽度
  const viewWith = useSelector((state) => state.layouts.viewSize.width);

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
      scroll={viewWith > 1500 ? null : { x: 1400 }}
      {...residualParam}
      columns={extensionsColumns}
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