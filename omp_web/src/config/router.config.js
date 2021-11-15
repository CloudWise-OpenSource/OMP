import AppStore from "@/pages/AppStore";
import AppStoreDetail from "@/pages/AppStore/config/detail";
//import VersionManagement from "@/pages/ProductsManagement/VersionManagement";
import MachineManagement from "@/pages/MachineManagement";
import UserManagement from "@/pages/UserManagement";
import MonitoringSettings from "@/pages/MonitoringSettings";
import SystemManagement from "@/pages/SystemManagement";
import AlarmLog from "@/pages/AlarmLog";
import ExceptionList from "@/pages/ExceptionList";
import PatrolInspectionRecord from "@/pages/PatrolInspectionRecord";
import PatrolStrategy from "@/pages/PatrolStrategy";
import PatrolInspectionDetail from "@/pages/PatrolInspectionRecord/config/detail";
import ServiceManagement from "@/pages/ServiceManagement";
import ComponentInstallation from "@/pages/AppStore/config/ComponentInstallation";
import ApplicationInstallation from "@/pages/AppStore/config/ApplicationInstallation";
import Installation from "@/pages/AppStore/config/Installation";
import {
  DesktopOutlined,
  ClusterOutlined,
  ProfileOutlined,
  SettingOutlined,
  LineChartOutlined,
  AppstoreOutlined,
  EyeOutlined,
} from "@ant-design/icons";

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
    menuTitle: "应用管理",
    menuIcon: <AppstoreOutlined />,
    menuKey: "/application_management",
    children: [
      {
        title: "服务管理",
        path: "/application_management/service_management",
        component: ServiceManagement,
      },
      {
        title: "应用商店",
        path: "/application_management/app_store",
        component: AppStore,
      },
      {
        title: "组件安装",
        path: "/application_management/app_store/component_installation/:name",
        notInMenu: true,
        component: ComponentInstallation,
      },
      {
        title: "应用安装",
        path: "/application_management/app_store/application_installation/:name",
        notInMenu: true,
        component: ApplicationInstallation,
      },
      {
        title: "应用商店服务详情",
        path: "/application_management/app_store/app-service-detail/:name/:verson",
        notInMenu: true,
        component: AppStoreDetail,
      },
      {
        title: "应用商店组件详情",
        path: "/application_management/app_store/app-component-detail/:name/:verson",
        notInMenu: true,
        component: AppStoreDetail,
      },
      {
        title: "批量安装",
        path: "/application_management/app_store/installation",
        notInMenu: true,
        component: Installation,
      },
    ],
  },
  {
    menuTitle: "应用监控",
    menuIcon: <LineChartOutlined />,
    menuKey: "/application-monitoring",
    children: [
      {
        title: "异常清单",
        path: "/application-monitoring/exception-list",
        component: ExceptionList,
      },
      {
        title: "告警记录",
        path: "/application-monitoring/alarm-log",
        component: AlarmLog,
      },
      {
        title: "监控设置",
        path: "/application-monitoring/monitoring-settings",
        component: MonitoringSettings,
      },
    ],
  },
  {
    menuTitle: "状态巡检",
    menuIcon: <EyeOutlined />,
    menuKey: "/status-patrol",
    children: [
      {
        title: "巡检记录",
        path: "/status-patrol/patrol-inspection-record",
        component: PatrolInspectionRecord,
      },
      {
        title: "巡检记录详情",
        path: "/status-patrol/patrol-inspection-record/status-patrol-detail/:id",
        notInMenu: true,
        component: PatrolInspectionDetail,
      },
      {
        title: "巡检策略",
        path: "/status-patrol/patrol-strategy",
        component: PatrolStrategy,
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
