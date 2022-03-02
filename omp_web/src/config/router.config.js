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
import EmailSettings from "src/pages/EmailSettings";
import RuleCenter from "src/pages/RuleCenter";
import InstallationRecord from "@/pages/InstallationRecord";
import Upgrade from "@/pages/AppStore/config/Upgrade";
import Rollback from "@/pages/AppStore/config/Rollback";
import DeploymentPlan from "@/pages/DeploymentPlan";
import BackupRecords from "@/pages/BackupRecords";
import BackupStrategy from "@/pages/BackupStrategy";
import LoginLog from "@/pages/LoginLog";
import SystemLog from "@/pages/SystemLog";
import SelfHealingRecord from "@/pages/SelfHealingRecord";
import SelfHealingStrategy from "@/pages/SelfHealingStrategy";
import ToolManagement from "@/pages/ToolManagement";
import TaskRecord from "@/pages/TaskRecord";
import ToolDetails from "@/pages/ToolManagement/detail";
import ToolExecution from "@/pages/ToolExecution";
import ToolExecutionResults from "@/pages/ToolExecutionResults";
import RuleIndicator from "@/pages/RuleIndicator";
import RuleExtend from "@/pages/RuleExtend"

import {
  DesktopOutlined,
  ClusterOutlined,
  ProfileOutlined,
  SettingOutlined,
  LineChartOutlined,
  AppstoreOutlined,
  EyeOutlined,
  UnorderedListOutlined,
  SaveOutlined,
  SolutionOutlined,
  InteractionOutlined,
  ToolOutlined
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
      // {
      //   title: "服务安装",
      //   path: "/application_management/app_store/installation-service",
      //   notInMenu: true,
      //   component: Installation,
      // },
      {
        title: "执行记录",
        path: "/application_management/install-record",
        component: InstallationRecord,
      },
      {
        title: "服务升级",
        path: "/application_management/app_store/service_upgrade",
        notInMenu: true,
        component: Upgrade,
      },
      {
        title: "服务回滚",
        path: "/application_management/app_store/service_rollback",
        notInMenu: true,
        component: Rollback,
      },
      {
        title: "部署模板",
        path: "/application_management/deployment-plan",
        component: DeploymentPlan,
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
    menuTitle: "故障自愈",
    menuIcon: <InteractionOutlined />,
    menuKey: "/fault-selfHealing",
    children: [
      {
        title: "自愈记录",
        path: "/fault-selfHealing/selfHealing-record",
        component: SelfHealingRecord,
      },
      {
        title: "自愈策略",
        path: "/fault-selfHealing/selfHealing-strategy",
        component: SelfHealingStrategy,
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
    menuTitle: "指标中心",
    menuIcon: <UnorderedListOutlined />,
    menuKey: "/rule-center",
    children: [
      // {
      //   title: "默认指标",
      //   path: "/rule-center/default-rule",
      //   component: RuleCenter,
      // },
      {
        title: "指标规则",
        path: "/rule-center/indicator-rule",
        component: RuleIndicator,
      },
      {
        title: "扩展指标",
        path: "/rule-center/extend-rule",
        component: RuleExtend,
      },
    ],
  },
  {
    menuTitle: "数据备份",
    menuIcon: <SaveOutlined />,
    menuKey: "/data-backup",
    children: [
      {
        title: "备份记录",
        path: "/data-backup/backup-record",
        component: BackupRecords,
      },
      {
        title: "备份策略",
        path: "/data-backup/backup-strategy",
        component: BackupStrategy,
      },
    ],
  },
  {
    menuTitle: "实用工具",
    menuIcon: <ToolOutlined />,
    menuKey: "/utilitie",
    children: [
      {
        title: "工具管理",
        path: "/utilitie/tool-management",
        component: ToolManagement,
      },
      {
        title: "工具详情",
        path: "/utilitie/tool-management/tool-management-detail/:id",
        notInMenu: true,
        component: ToolDetails,
      },
      {
        title: "工具执行",
        path: "/utilitie/tool-management/tool-execution/:id",
        notInMenu: true,
        component: ToolExecution,
      },
      {
        title: "执行结果",
        path: "/utilitie/tool-management/tool-execution-results/:id",
        notInMenu: true,
        component: ToolExecutionResults,
      },
      {
        title: "任务记录",
        path: "/utilitie/task-record",
        component: TaskRecord,
      },
    ],
  },
  {
    menuTitle: "操作记录",
    menuIcon: <SolutionOutlined />,
    menuKey: "/operation-record",
    children: [
      {
        title: "登录日志",
        path: "/operation-record/login-log",
        component: LoginLog,
      },
      {
        title: "系统记录",
        path: "/operation-record/system-log",
        component: SystemLog,
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
      {
        title: "邮件管理",
        path: "/system-settings/email-settings",
        component: EmailSettings,
      },
    ],
  },
];
