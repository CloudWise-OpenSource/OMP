import { Dropdown, Menu } from "antd";
import { FilterFilled } from "@ant-design/icons";
import { useState } from "react";

const OmpTableFilter = ({ dataIndex, filterMenuList, queryRequest, initfilter }) => {
  // 表格的筛选控制器
  const [filterControl, setFilterControl] = useState(initfilter);

  // 展开菜单是否
  const [dropDownIsOpen, setDropDownIsOpen] = useState(false);

  return (
    <Dropdown
      visible={dropDownIsOpen}
      onVisibleChange={(e) => {
        if (filterControl) {
          queryRequest({ [dataIndex]: null });
          setFilterControl("");
        } else {
          setDropDownIsOpen(e);
        }
      }}
      overlay={
        <Menu
          style={{
            maxHeight:200,
            overflow:"hidden",
            overflowY: "auto",
          }}
          selectedKeys={[filterControl]}
          onClick={(e) => {
            setFilterControl(e.key);
            queryRequest({ [dataIndex]: e.key });
            setDropDownIsOpen(false);
          }}
        >
          {filterMenuList?.map((item) => {
            return <Menu.Item key={item.value}>{item.text}</Menu.Item>;
          })}
        </Menu>
      }
      placement="bottomCenter"
      trigger="click"
    >
      <FilterFilled style={{ color: filterControl ? "#4986f7" : null }} />
    </Dropdown>
  );
};

export default OmpTableFilter;
