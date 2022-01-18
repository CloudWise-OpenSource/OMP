from .backup import BackupSetting, BackupHistory
from .email import EmailSMTPSetting, ModuleSendEmailSetting
from .env import Env
from .host import Host, HostOperateLog
from .inspection import InspectionHistory, InspectionCrontab, InspectionReport
from .install import MainInstallHistory, PreInstallHistory, \
    DetailInstallHistory, PostInstallHistory, DeploymentPlan
from .monitor import MonitorUrl, Alert, Maintain, GrafanaMainPage, \
    AlertSendWaySetting
from .product import Labels, UploadPackageHistory, ProductHub, \
    ApplicationHub, Product
from .service import ServiceConnectInfo, ClusterInfo, Service, ServiceHistory
from .threshold import HostThreshold, ServiceThreshold, ServiceCustomThreshold
from .user import UserProfile, OperateLog
from .upgrade import UpgradeHistory, UpgradeDetail, RollbackHistory,\
    RollbackDetail


__all__ = [
    # 邮箱设置
    EmailSMTPSetting,
    ModuleSendEmailSetting,
    # 环境
    Env,
    # 主机
    Host,
    HostOperateLog,
    # 巡检
    InspectionHistory,
    InspectionCrontab,
    InspectionReport,
    # 安装
    MainInstallHistory,
    PreInstallHistory,
    PostInstallHistory,
    DetailInstallHistory,
    DeploymentPlan,
    # 监控
    MonitorUrl,
    Alert,
    Maintain,
    GrafanaMainPage,
    AlertSendWaySetting,
    # 产品
    Labels,
    UploadPackageHistory,
    ProductHub,
    ApplicationHub,
    Product,
    # 服务
    ServiceConnectInfo,
    ClusterInfo,
    Service,
    ServiceHistory,
    # 阈值
    HostThreshold,
    ServiceThreshold,
    ServiceCustomThreshold,
    # 用户
    UserProfile,
    OperateLog,
    # 升级
    UpgradeHistory,
    UpgradeDetail,
    # 回滚
    RollbackHistory,
    RollbackDetail,
    # 备份
    BackupSetting,
    BackupHistory,
]
