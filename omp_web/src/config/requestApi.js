export const apiRequest = {
  environment: {
    //环境数据查询
    //queryEnvList: "/api/v1/env"
    // 查询全局维护模式
    queryMaintainState: "/api/promemonitor/globalMaintain/",
  },
  auth: {
    // 用户认证
    login: "/api/login/", // 登入
    // 首次请求用于验证登出
    users: "/api/users/users/",
    // 修改密码
    changePassword: "/api/users/updatePassword/",
  },
  homepage: {
    instrumentPanel: "/api/promemonitor/instrumentPanel/",
  },
  machineManagement: {
    // 主机管理
    hosts: "/api/hosts/hosts/",
    ipList: "/api/hosts/ips/",
    // 主机详情
    hostDetail: "/api/hosts/hostsDetail/",
    // 主机名和ip地址校验接口
    checkHost: "/api/hosts/fields/",
    operateLog: "/api/hosts/operateLog/",
    // 重启主机agent
    restartHostAgent: "/api/hosts/restartHostAgent/",
    // 重启监控agent
    restartMonitorAgent: "/api/promemonitor/restartMonitorAgent/",
    // 主机进入退出维护模式
    hostsMaintain: "/api/hosts/maintain/",

    // 主机批量导入模版下载地址
    downTemplate: "/api/hosts/batchValidate/",
    // 主机批量导入文件解析后的校验接口(post)
    batchValidate: "/api/hosts/batchValidate/",
    // 主机批量导入创建主机
    batchImport: "/api/hosts/batchImport/",
  },
  MonitoringSettings: {
    // 配置初始查询监控
    monitorurl: "/api/promemonitor/monitorurl/",
    // 修改配置监控
    multiple_update: "/api/promemonitor/monitorurl/multiple_update/",
    // 查询推送配置
    queryPushConfig: "/api/promemonitor/getSendAlertSetting/",
    // 更新邮件配置
    updatePushConfig: "/api/promemonitor/updateSendAlertSetting/",
  },
  Alert: {
    // 告警记录页面查询
    listAlert: "/api/promemonitor/listAlert/",
    // 告警记录已读
    updateAlert: "/api/promemonitor/updateAlert/",
    // 告警记录筛选实例名称
    instanceNameList: "/api/promemonitor/instanceNameList/",
  },
  ExceptionList: {
    // 异常清单列表查询
    exceptionList: "/api/promemonitor/grafanaurl/",
  },
  appStore: {
    // 组件查询
    queryComponents: "/api/appStore/components/",
    // 服务查询
    queryServices: "/api/appStore/services/",
    // 服务筛选条件列表
    queryLabels: "/api/appStore/labels/",
    // 基础组件详情
    ProductDetail: "/api/appStore/componentDetail/",
    // 应用服务详情
    ApplicationDetail: "/api/appStore/serviceDetail/",
    // 安装包删除
    remove: "/api/appStore/remove/",
    // 安装包校验结果
    pack_verification_results: "/api/appStore/pack_verification_results/",
    // 发布命令下发
    publish: "/api/appStore/publish/",
    // 扫描服务端命令下发
    executeLocalPackageScan: "/api/appStore/executeLocalPackageScan/",
    // 扫描状态查询
    localPackageScanResult: "/api/appStore/localPackageScanResult/",

    // 服务列表
    services: "/api/services/services/",
    // 服务详情查询
    servicesDetail: "/api/services/services",
    // 服务的操作
    servicesAction: "/api/services/action/",
    // 服务的删除提示信息
    servicesDeleteMsg: "/api/services/delete/",
    // 模版下载
    applicationTemplate: "/api/appStore/applicationTemplate/",
    // 组件安装查询接口
    componentEntrance: "/api/appStore/componentEntrance/",
    // 产品安装查询接口
    productEntrance: "/api/appStore/productEntrance/",

    // 服务安装校验
    executeInstall: "/api/appStore/executeInstall/",
    // 服务校验通过后的状态查询接口
    installHistory: "/api/appStore/installHistory/",

    // 服务查询安装记录
    serviceInstallHistoryDetail: "/api/appStore/serviceInstallHistoryDetail/",

    // 服务批量安装选择应用服务列表
    queryBatchInstallationServiceList: "/api/appStore/batchInstallEntrance/",
    // 服务批量安装选择应用确认操作
    createInstallInfo: "/api/appStore/createInstallInfo/",
    // 批量安装
    checkInstallInfo: "/api/appStore/checkInstallInfo/",
    // 服务分布数据查询
    createServiceDistribution: "/api/appStore/createServiceDistribution/",
    // 服务分布已安装服务查询
    queryListServiceByIp: "/api/appStore/listServiceByIp",
    // 服务批量安装服务分布确认操作
    checkServiceDistribution: "/api/appStore/checkServiceDistribution/",

    // 服务批量安装修改配置ip初始查询
    getInstallHostRange: "/api/appStore/getInstallHostRange/",
    // 服务批量安装根据ip查询安装相应参数
    getInstallArgsByIp: "/api/appStore/getInstallArgsByIp/",
    // 服务批量安装开始安装操作
    createInstallPlan: "/api/appStore/createInstallPlan/",
    // 批量安装-开始安装信息查询
    queryInstallProcess: "/api/appStore/showInstallProcess",
    // 批量安装-服务安装进度详情查询
    showSingleServiceInstallLog:"/api/appStore/showSingleServiceInstallLog"
  },
  installHistoryPage:{
    queryInstallHistoryList:"/api/appStore/mainInstallHistory"
  },
  inspection: {
    inspectionList: "/api/inspection/history/",
    // 巡检记录详情
    reportDetail: "/api/inspection/report",
    // 巡检策略查询
    queryPatrolStrategy: "/api/inspection/crontab/0/",
    // 创建巡检任务
    createPatrolStrategy: "/api/inspection/crontab/",
    // 修改巡检任务
    updatePatrolStrategy: "/api/inspection/crontab/0/",
    // 深度分析｜主机巡检｜组件巡检 任务下发
    taskDistribution: "/api/inspection/history/",
    // 巡检渲染组件列表
    servicesList: "/api/inspection/services/",
    // 巡检导出
    download: "/download-inspection",
    // 查询推送配置
    queryPushConfig: "/api/inspection/inspectionSendEmailSetting/",
    // 更新邮件配置
    updatePushConfig: "/api/inspection/inspectionSendEmailSetting/",
    // 推送邮件
    pushEmail: "/api/inspection/inspectionSendEmail/",
  },
  emailSetting: {
    // 查询邮件全局设置
    querySetting: "/api/promemonitor/getSendEmailConfig/",
    // 更新邮件全局设置
    updateSetting: "/api/promemonitor/updateSendEmailConfig/",
  },
  ruleCenter: {
    hostThreshold: "/api/promemonitor/hostThreshold/",
    serviceThreshold: "/api/promemonitor/serviceThreshold/",
    queryCustomThreshold: "/api/promemonitor/customThreshold/",
  },
};
