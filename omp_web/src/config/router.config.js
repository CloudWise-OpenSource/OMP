//import ServiceManagement from "@/pages/ProductsManagement/ServiceManagement";
import WarningRecord from "@/pages/OperationManagement/WarningRecord";
//import VersionManagement from "@/pages/ProductsManagement/VersionManagement";
import MachineManagement from "@/pages/MachineManagement"
import { DesktopOutlined, ClusterOutlined, ProfileOutlined, SettingOutlined } from "@ant-design/icons";
import UserManagement from "@/pages/SystemSettings/UserManagement"

export default [
  {
    menuTitle: "资源管理",
    menuIcon: <DesktopOutlined />,
    menuKey: "/resource-management",
    children: [
      {
        title: "主机管理",
        path: "/resource-management/machine-management",
        component: MachineManagement,
      },
    ],
  },
  {
    menuTitle: "运维管理",
    menuIcon: <ProfileOutlined />,
    menuKey: "/operation-management",
    children: [
      {
        title: "告警记录",
        path: "/operation-management/waring-records",
        component: WarningRecord ,
      },
    ],
  },
  {
    menuTitle: "系统设置",
    menuIcon: <SettingOutlined />,
    menuKey: "/system-settings",
    children: [
      {
        title: "用户管理",
        path: "/system-settings/user-management",
        component: UserManagement,
      },
    ],
  },
];
