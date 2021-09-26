export const apiRequest = {
  environment: {
    //环境数据查询
    //queryEnvList: "/api/v1/env"
  },
  auth: {
    // 用户认证
    login: "/api/login/", // 登入
    // 首次请求用于验证登出
    users: "/api/users/users/",








    logout: "/api/v1/auth/logout", // 登出
    password: "/api/v1/auth/password", // 修改密码
  },
  homepage: {
    host: "/api/v1/home/host",
    service: "/api/v1/home/service",
    database: "/api/v1/home/database",
    component: "/api/v1/home/component",
    external: "/api/v1/home/external"
  },
  machineManagement: {
    // 主机管理
    hosts: "/api/hosts/hosts/",
    ipList:"/api/hosts/ips/",
    // 主机名和ip地址校验接口
    checkHost:"/api/hosts/fields/"
  },
  productsManagement: {
    // 产品管理-服务管理
    all: "/api/v1/services/all", // 全部服务
    getExternal: "/api/v1/services/external", // 第三方服务查询
    //addExternal: "/api/v1/services/external/add", // 第三方服务添加
    addExternal: "/api/v1/scheduler/external/services",
    //delExternal: "/api/v1/services/external/del", // 第三方服务添加
    delExternal: "/api/v1/scheduler/external/services",
    operation:"/api/v1/services/operation",

    serviceAdd_Delete:"/api/v1/ruban/service", // 服务的删除新增功能
    queryProduct:"/api/v1/ruban/product"//自研服务添加的select数据
  },
  log: {
    // 日志管理
    loginLog: "/api/v1/audits/loginLog", // 登录日志
    operateLog: "/api/v1/audits/operateLog", // 操作记录
  },
  userManagement: {
    // 用户管理
    user: "/api/v1/auth/getUser", // 获取用户数据
    allUsers: "/api/v1/auth/getAllUser", // 获取所有用户
    roleList: "/api/v1/auth/getRoleList", // 角色展示
  },
  systemSettings: {
    // 系统设置
    monitor: "/api/v1/monitor/setting", // 基础设置
    setting: "/api/v1/inspection/setting", // 巡检设置-任务设置
    saveSetting: "/api/v1/scheduler/inspection/setting", // 巡检设置-保存任务设置
    userPass: "/api/v1/inspection/userPass", // 巡检设置-账号设置
    hostThreshold: "/api/v1/monitor/hostThreshold", // 阈值设置-主机指标
    serviceThreshold: "/api/v1/monitor/serviceThreshold", // 阈值设置-服务指标

    selfHealingSetting: "/api/v1/self-healing/setting",//自愈设置

    // 维护模式查询/修改
    modeInfoChange: "/api/v1/maintenance/mode",

    // 告警推送/变更
    alertSend:"/api/v1/alert-send/setting"
  },
  productSettings: {
    // 产品设置
    uploadTaskFile: "/api/v1/hosts/file/upload", // 上传
    checkFiles: "/api/v1/hosts/file/check", // 校验
    writeFiles: "/api/v1/hosts/file/write", // 写入

    //版本管理
    downloadXlsxFile: "/download/deployments.xlsx", //下载xlsx文件
    uploadExcel: "/api/v1/ruban/uploadExcel", //上传xlsx文件
    versionHistoryList: "/api/v1/ruban/versionHistory", //版本管理列表展示
    executeScript: "/api/v1/ruban/executeScript", //安装操作
    installLog: "/api/v1/ruban/installLog", //安装进度

    //环境纳管
    //三个文件
    v2Upload: "/api/v2/file/upload",//文件上传
    v2Check: "/api/v2/file/check",//文件检查
    v2Write: "/api/v1/scheduler/file/write",//文件写入
    //xlsx
    v1UploadExcel: "/api/v1/file/uploadExcel",//xlsx上传
    v1CheckExcel: "/api/v1/file/checkExcel",//xlsx检查
    v1WriteExcel: "/api/v1/scheduler/file/writeExcel",//xlsx写入
  },
  operationManagement: {
    alertList: "/api/v1/monitor/alertRealtime", // 异常清单
    alertRecord: "/api/v1/monitor/alert", // 告警记录 put：已读记录
    deepInspection: "/api/v1/inspection/deep", // 深度分析报告列表
    executeDeepInspection: "/api/v1/scheduler/inspection/deep", // 深度分析 执行巡检
    normalInspection: "/api/v1/inspection/normal", // 主机巡检
    executeNormalInspection: "/api/v1/scheduler/inspection/normal", // 主机巡检  执行巡检
    serviceList: "/api/v1/inspection/service", // 左侧组件巡检-组件列表
    hostList: "/api/v1/inspection/host", // 左侧主机巡检-主机列表
    alertTendency: "/api/v1/monitor/alertTendency", // 趋势分析
    reportDeepDetail: "/api/v1/inspection/deep/report", // 巡检报告详情
    reportDetail: "/api/v1/inspection/normal/report", // 巡检报告详情

    selfHealingHistory: "/api/v1/self-healing/history", // 自愈记录列表查询
  },
};
