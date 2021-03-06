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
    menuTitle: "????????????",
    menuIcon: <DesktopOutlined />,
    menuKey: "/resource-management",
    children: [
      {
        title: "????????????",
        path: "/resource-management/machine-management",
        component: MachineManagement,
      },
    ],
  },
  {
    menuTitle: "????????????",
    menuIcon: <AppstoreOutlined />,
    menuKey: "/application_management",
    children: [
      {
        title: "????????????",
        path: "/application_management/service_management",
        component: ServiceManagement,
      },
      {
        title: "????????????",
        path: "/application_management/app_store",
        component: AppStore,
      },
      {
        title: "????????????",
        path: "/application_management/app_store/component_installation/:name",
        notInMenu: true,
        component: ComponentInstallation,
      },
      {
        title: "????????????",
        path: "/application_management/app_store/application_installation/:name",
        notInMenu: true,
        component: ApplicationInstallation,
      },
      {
        title: "????????????????????????",
        path: "/application_management/app_store/app-service-detail/:name/:verson",
        notInMenu: true,
        component: AppStoreDetail,
      },
      {
        title: "????????????????????????",
        path: "/application_management/app_store/app-component-detail/:name/:verson",
        notInMenu: true,
        component: AppStoreDetail,
      },
      {
        title: "????????????",
        path: "/application_management/app_store/installation",
        notInMenu: true,
        component: Installation,
      },
      // {
      //   title: "????????????",
      //   path: "/application_management/app_store/installation-service",
      //   notInMenu: true,
      //   component: Installation,
      // },
      {
        title: "????????????",
        path: "/application_management/install-record",
        component: InstallationRecord,
      },
      {
        title: "????????????",
        path: "/application_management/app_store/service_upgrade",
        notInMenu: true,
        component: Upgrade,
      },
      {
        title: "????????????",
        path: "/application_management/app_store/service_rollback",
        notInMenu: true,
        component: Rollback,
      },
      {
        title: "????????????",
        path: "/application_management/deployment-plan",
        component: DeploymentPlan,
      },
    ],
  },
  {
    menuTitle: "????????????",
    menuIcon: <LineChartOutlined />,
    menuKey: "/application-monitoring",
    children: [
      {
        title: "????????????",
        path: "/application-monitoring/exception-list",
        component: ExceptionList,
      },
      {
        title: "????????????",
        path: "/application-monitoring/alarm-log",
        component: AlarmLog,
      },
      {
        title: "????????????",
        path: "/application-monitoring/monitoring-settings",
        component: MonitoringSettings,
      },
    ],
  },
  {
    menuTitle: "????????????",
    menuIcon: <InteractionOutlined />,
    menuKey: "/fault-selfHealing",
    children: [
      {
        title: "????????????",
        path: "/fault-selfHealing/selfHealing-record",
        component: SelfHealingRecord,
      },
      {
        title: "????????????",
        path: "/fault-selfHealing/selfHealing-strategy",
        component: SelfHealingStrategy,
      },
    ],
  },
  {
    menuTitle: "????????????",
    menuIcon: <EyeOutlined />,
    menuKey: "/status-patrol",
    children: [
      {
        title: "????????????",
        path: "/status-patrol/patrol-inspection-record",
        component: PatrolInspectionRecord,
      },
      {
        title: "??????????????????",
        path: "/status-patrol/patrol-inspection-record/status-patrol-detail/:id",
        notInMenu: true,
        component: PatrolInspectionDetail,
      },
      {
        title: "????????????",
        path: "/status-patrol/patrol-strategy",
        component: PatrolStrategy,
      },
    ],
  },
  {
    menuTitle: "????????????",
    menuIcon: <UnorderedListOutlined />,
    menuKey: "/rule-center",
    children: [
      // {
      //   title: "????????????",
      //   path: "/rule-center/default-rule",
      //   component: RuleCenter,
      // },
      {
        title: "????????????",
        path: "/rule-center/indicator-rule",
        component: RuleIndicator,
      },
      {
        title: "????????????",
        path: "/rule-center/extend-rule",
        component: RuleExtend,
      },
    ],
  },
  {
    menuTitle: "????????????",
    menuIcon: <SaveOutlined />,
    menuKey: "/data-backup",
    children: [
      {
        title: "????????????",
        path: "/data-backup/backup-record",
        component: BackupRecords,
      },
      {
        title: "????????????",
        path: "/data-backup/backup-strategy",
        component: BackupStrategy,
      },
    ],
  },
  {
    menuTitle: "????????????",
    menuIcon: <ToolOutlined />,
    menuKey: "/utilitie",
    children: [
      {
        title: "????????????",
        path: "/utilitie/tool-management",
        component: ToolManagement,
      },
      {
        title: "????????????",
        path: "/utilitie/tool-management/tool-management-detail/:id",
        notInMenu: true,
        component: ToolDetails,
      },
      {
        title: "????????????",
        path: "/utilitie/tool-management/tool-execution/:id",
        notInMenu: true,
        component: ToolExecution,
      },
      {
        title: "????????????",
        path: "/utilitie/tool-management/tool-execution-results/:id",
        notInMenu: true,
        component: ToolExecutionResults,
      },
      {
        title: "????????????",
        path: "/utilitie/task-record",
        component: TaskRecord,
      },
    ],
  },
  {
    menuTitle: "????????????",
    menuIcon: <SolutionOutlined />,
    menuKey: "/operation-record",
    children: [
      {
        title: "????????????",
        path: "/operation-record/login-log",
        component: LoginLog,
      },
      {
        title: "????????????",
        path: "/operation-record/system-log",
        component: SystemLog,
      },
    ],
  },
  {
    menuTitle: "????????????",
    menuIcon: <SettingOutlined />,
    menuKey: "/system-settings",
    children: [
      {
        title: "????????????",
        path: "/system-settings/user-management",
        component: UserManagement,
      },
      {
        title: "????????????",
        path: "/system-settings/system-management",
        component: SystemManagement,
      },
      {
        title: "????????????",
        path: "/system-settings/email-settings",
        component: EmailSettings,
      },
    ],
  },
];
