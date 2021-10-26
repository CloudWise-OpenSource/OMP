# OMP 社区版-应用商店发布说明文档

[TOC]

## 1. 组件包 规范

### 1.1. 目录结构

**以mysql为例：**

```shell
$ tree ./mysql
./mysql
├── mysql.svg						# 平台展示组件图标，请使用 “组件名称.svg ” 命名
├── mysql_binary				# 组件包程序目录
├── mysql.yaml					# 组件配置文件, 记录该组件安装信息,请使用 “组件名称.yaml” 命名
└── scripts							# 组件的安装、启动等控制脚本
│   ├── Core.py
│   ├── bash
│   ├── init.py
│   ├── install.py
│   ├── mysql
│   ├── mysql_backup.sh
│   └── sql
```

**备注:**

1. 组件图标请使用svg格式图片，如不添加会显示平台缺省图标
2. 确保包名称(mysql)、包配置文件(mysql.yaml) 、包图标(mysql.svg) 名称统一, 上传安装包时，平台会校验 “包名.yaml”文件
3. 确保安装包解压后是一个整体目录

### 1.2. 发布包命名规范

请使用 `{packageName}-{packageVersion}-{others}-{packageMD5}.tar.gz`  格式进行打包命名

> packageName:   安装包名称，建议字符:  `英文`  `数字`   `_`
> packageVersion: 安装包版本，建议字符:  `英文` `数字` `_`   `.`
> others:  其他信息，建议字符:  `英文` `数字` `_`   `.`
> packageMD5:  安装包MD5 值
> 例如：`mysql-5.7.31-8e955b24fefe7061eb79cfc61a9a02a1.tar.gz`

```shell
$ tar czf mysql-5.7.31.tar.gz mysql
$ md5sum mysql-5.7.31.tar.gz
8e955b24fefe7061eb79cfc61a9a02a1
$ mv mysql-5.7.31.tar.gz mysql-5.7.31-8e955b24fefe7061eb79cfc61a9a02a1.tar.gz
```

### 1.3.  配置文件yaml说明

保留KEY值说明:

| KEY          | 说明         | 备注                                   |
| ------------ | ------------ | -------------------------------------- |
| service_port | 服务端口     | 供其他程序连接的端口号                 |
| base_dir     | 应用安装目录 |                                        |
| log_dir      | 应用日志目录 | 服务的日志采集会采集该目录下*.log 文件 |
| username     | 用户名       |                                        |
| password     | 密码         |                                        |

```yaml
# 类型 (必填)：
# - product 产品
  # - service 服务
  # - upgrade 升级
# - component 组件
kind: component
# 名称:  上传后显示的名称，请确保相同组件名称一致
name: mysql
# 版本:  上传后显示的版本，支持： 数字、字母、- 、.
version: 5.7.31
# 描述 长度256字符，请针对组件书写贴切的描述文字
description: "MySQL是一个关系型数据库管理系统，由瑞典MySQL AB 公司开发，属于 Oracle 旗下产品。MySQL 是最流行的关系型数据库管理系统之一，在 WEB 应用方面，MySQL是最好的 RDBMS (Relational Database Management System，关系数据库管理系统) 应用软件之一。"
# 标签 ，请针对组件功能设置准确标签
labels:
  - 数据库
# 自动启动 true/flase，安装完后是否需要启动服务
auto_launch: false
# 是否为基础环境组件，如 jdk,  该类组件以基础环境方式安装
base_env: flase
# 监控相关
monitor:
  # 监控进程名称
  process_name:  "mysqld"
  # 监控端口号，请根据 ports 中的变量设置
  metric_port: {service_port}
# 定义服务使用的端口号
ports:
    # 名称，在表单中显示的标题
  - name: 服务端口
    # 协议
    protocol: TCP
    # 关键词，传入到 安装脚本中
    key: service_port  # service_port 为保留关键词，表示 为 提供服务的端口
    # 服务默认端口
    default: 3306
# 部署方式
deploy:
  single:
    - name: 单实例
      key: single
  complex:
    - name: 主从模式
      key: master_slave
      nodes:
        start: 2    # 初始节点数量
        step: 1     # 增加节点步长
# 依赖项 选填
dependencies:
# 资源需求
resources:
  cpu: 1000m
  memory: 500m
# 脚本所需变量参数 选填
install:
  - name: "安装目录"
    key: base_dir
    default: "{data_path}/mysql"
  - name: "数据目录"
    key: data_dir
    default: "{data_path}/mysql/data"
  - name: "日志目录"
    key: log_dir
    default: "{data_path}/mysql/log"
  - name: "用户名"
    key: username
    default: root
  - name: "密码"
    key: password
    default: "123456"
# 程序控制脚本相对路径
control:
  start: "./bin/start.sh"
  stop: "./bin/stop.sh"
  restart: "./bin/restart.sh"
  reload: "./bin/reload.sh"
  install: "./scripts/install.sh"
  init:  "./scripts/init.sh"
```



## 2. 应用服务包规范

### 2.1. 目录结构

```shell
$ tree prod
prod
├── prod.svg  # 应用 图标svg
├── prod
│   └── service_name.yaml # 服务yaml配置文件
├── service_name-2.303.2-5d1ac8ce87323fc399506d1335ae5c98.tar.gz  # 服务压缩包
└── prod.yaml	# 应用yaml配置文件

1 directory, 3 files
```

### 2.2. 包命名规范

请使用 `{packageName}-{packageVersion}-{others}-{packageMD5}.tar.gz`  格式进行打包命名

> packageName:   安装包名称，建议字符:  `英文`  `数字`   `_`
> packageVersion: 安装包版本，建议字符:  `英文` `数字` `_`   `.`
> others:  其他信息，建议字符:  `英文` `数字` `_`   `.`
> packageMD5:  安装包MD5 值
> 例如：`prod-2.303.2-5d1ac8ce87323fc399506d1335ae5c98.tar.gz`

### 2.3. 配置文件yaml说明

#### 2.3.1. 应用包yaml说明

```yaml
kind: product     # 类型
name: prod     # 名称
version: 2.303.2  # 版本
description: "应用详细描述信息"
labels:          # 标签
  - 小程序服务
# 只能依赖 product 类型
dependencies:
service:  #  指定服务，按照安装启动顺序
  - name: service_name
    version: 2.303.2
```

#### 2.3.2. 服务包yaml说明

```yaml
# 类型 (必填)：
# - product 产品
  # - service 服务
  # - upgrade 升级
# - component 组件
kind: service
# 名称
name: service_name
# 版本
version: 2.303.2
# 描述
description: "服务描述内容..."
# 自动自动
auto_launch: true
base_env: false
# 进程名称，监控该名称
monitor:
  process_name: "service_name"
  metrics_port: {service_port}
# 使用端口号
ports:
    # 名称
  - name: 服务端口
    # 协议
    protocol: TCP
    # 关键词，传入到 install脚本
    key: service_port
    # 端口
    default: 8080
# 部署方式
# 依赖项 选填
dependencies:
  - name: jdk
    version: 8u211
# 资源需求
resources:
  cpu: 1000m
  memory: 2000m
# 脚本所需变量参数 选填
install:
  - name: "安装目录"
    key: base_dir
    default: "{data_path}/service_path"
  - name: "日志目录"
    key: log_dir
    default: "{data_path}/service_path/logs"
# 程序控制脚本路径
control:
  start: "./bin/start.sh"
  stop: "./bin/stop.sh"
  restart: "./bin/restart.sh"
  reload: "./bin/reload.sh"
  install: "./scripts/install.sh"
  init:  "./scripts/init.sh"
```

