import { Select } from "antd";
import { useState, useRef } from "react";

const OmpSelect = ({
  searchLoading,
  selectValue,
  listSource,
  setSelectValue,
  fetchData,
  pagination,
}) => {
  const [searchValue, setSearchValue] = useState("");

  //select 的onblur函数拿不到最新的search value,使用useref存(是最新的，但是因为失去焦点时会自动触发清空search，还是得使用ref存)
  const searchValueRef = useRef(null);
  
  return (
    <Select
      allowClear
      onClear={() => {
        searchValueRef.current = "";
        setSelectValue();
        setSearchValue();
        fetchData(
          { current: pagination.current, pageSize: pagination.pageSize },
          {},
          pagination.ordering
        );
      }}
      showSearch
      placeholder="搜索"
      loading={searchLoading}
      style={{ width: 200 }}
      onInputKeyDown={(e) => {
        if (e.code == "Enter") {
          //console.log("点击了",searchValueRef.current )
          setSelectValue(searchValueRef.current);
          fetchData(
            { current: 1, pageSize: 10 },
            { ip: searchValueRef.current },
            pagination.ordering
          );
        }
      }}
      searchValue={searchValue}
      onSelect={(e) => {
        if (e == searchValue || !searchValue) {
          //console.log(1)
          setSelectValue(e);
          fetchData(
            {
              current: pagination.current,
              pageSize: pagination.pageSize,
            },
            { ip: e },
            pagination.ordering
          );
        } else {
          //console.log(2)
          setSelectValue(searchValue);
          fetchData(
            {
              current: pagination.current,
              pageSize: pagination.pageSize,
            },
            { ip: searchValueRef.current },
            pagination.ordering
          );
        }
        searchValueRef.current = "";
      }}
      value={selectValue}
      onSearch={(e) => {
        e && (searchValueRef.current = e);
        setSearchValue(e);
      }}
      onBlur={(e) => {
        //console.log(searchValueRef.current,"searchValueRef.current")
        if (searchValueRef.current) {
          setSelectValue(searchValueRef.current);
          fetchData(
            {
              current: pagination.current,
              pageSize: pagination.pageSize,
            },
            { ip: searchValueRef.current },
            pagination.ordering
          );
        }
      }}
    >
      {listSource.map((item) => {
        return (
          <Select.Option value={item} key={item}>
            {item}
          </Select.Option>
        );
      })}
    </Select>
  );
};

export default OmpSelect;
