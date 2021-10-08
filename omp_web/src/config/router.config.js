//import ServiceManagement from "@/pages/ProductsManagement/ServiceManagement";
import WarningRecord from "@/pages/OperationManagement/WarningRecord";
//import VersionManagement from "@/pages/ProductsManagement/VersionManagement";
import MachineManagement from "@/pages/MachineManagement"
import UserManagement from "@/pages/UserManagement";
import MonitoringSettings from "@/pages/MonitoringSettings"
import SystemManagement from "@/pages/SystemManagement"
import { DesktopOutlined, ClusterOutlined, ProfileOutlined, SettingOutlined, LineChartOutlined } from "@ant-design/icons";

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
    menuTitle: "应用监控",
    menuIcon: <LineChartOutlined />,
    menuKey: "/application-monitoring",
    children: [
      {
        title: "监控设置",
        path: "/application-monitoring/monitoring-settings",
        component: MonitoringSettings ,
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
      {
        title: "系统管理",
        path: "/system-settings/system-management",
        component: SystemManagement,
      },
    ],
  },
];
