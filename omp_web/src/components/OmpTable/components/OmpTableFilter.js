import { Dropdown, Menu } from "antd";
import { FilterFilled } from "@ant-design/icons";
import { useState } from "react";

const OmpTableFilter = () => {
  // 表格的筛选控制器
  const [filterControl, setFilterControl] = useState("");

  // 展开菜单是否
  const [dropDownIsOpen, setDropDownIsOpen] = useState(false);

  return (
    <Dropdown
      visible={dropDownIsOpen}
      onVisibleChange={(e) => {
        if (filterControl) {
          setFilterControl("");
        } else {
          setDropDownIsOpen(e);
        }
      }}
      overlay={
        <Menu
          selectedKeys={[filterControl]}
          onClick={(e) => {
            setFilterControl(e.key);
            console.log(e);
            setDropDownIsOpen(false);
          }}
        >
          <Menu.Item key={133}>
            <a
              target="_blank"
              rel="noopener noreferrer"
              key={1}
              href="https://www.antgroup.com"
            >
              1st menu item
            </a>
          </Menu.Item>
          <Menu.Item key={311232}>
            <a
              target="_blank"
              rel="noopener noreferrer"
              key={2}
              href="https://www.aliyun.com"
            >
              2nd menu item
            </a>
          </Menu.Item>
          <Menu.Item key={1233}>
            <a
              target="_blank"
              rel="noopener noreferrer"
              key={3}
              href="https://www.luohanacademy.com"
            >
              3rd menu item
            </a>
          </Menu.Item>
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
