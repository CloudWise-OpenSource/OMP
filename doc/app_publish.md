# OMP 社区版-应用商店发布说明文档

[TOC]

## 1. 说明

用户可以在应用商店发布“基础组件”与“应用服务”两个维度的产品，在区分上，应用服务可以理解为完整的提供某一类服务的产品，产品内部可由一个或多个“服务”组成 ，比如gitlab、jenkins等。基础组件的角色更多是作为其他完成产品的一部分存在，以完成产品的某些功能需求，如mysql、redis等。

## 2. 基础组件打包规范

注：用户在发布基础组件安装包时，需按照以下规范打包上传才可以正常发布

### 2.1. 目录规范

以MySQL服务为例，需将涉及到的文件统一放在 mysql目录下，目录名称与该服务名称保持一致，目录中需要提供与该目录名称一致的配置文件(如：mysql.yaml)、产品图标（如：mysql.svg)  和其他所需文件（如安装脚本等）

**示例：**

```shell
$ tree ./mysql -L 2
./mysql                 # 目录名称，请与组件名称一致
├── mysql.svg           # 平台展示组件图标，请使用 “组件名称.svg ” 命名，与目录名称保持一致
├── mysql.yaml          # 组件配置文件, 记录该组件安装、升级等所需信息, 请使用 “组件名称.yaml” 命名，与目录名称保持一致
└── scripts             # 组件的安装、启动等控制脚本，该脚本在安装时会调用
│   ├── init.py         # 初始化脚本
│   ├── install.py      # 组件安装脚本
│   ├── mysql           # 组件启动、停止控制脚本，建议与服务名称一致
│   ├── mysql_backup.py # 其他动作脚本，如备份等
```

**备注:**

1. 组件图标请使用svg格式图片，如不添加会显示平台缺省图标；
2. 确保目录名称(mysql)、配置文件(mysql.yaml) 、图标(mysql.svg) 名称统一, 上传安装包时，平台将根据名称校验对应文件合法性，如名称不一致，可能会导致校验不通过等问题；
3. 确保安装包解压后是一个整体目录

### 2.2. 压缩包命名规范

请使用 `{name}-{version}-{others}-{package_md5}.tar.gz`  格式进行打包命名

1. name:   安装包名称，建议字符:  `英文`  `数字`   `_`
2. version: 安装包版本，建议字符:  `英文` `数字` `_`   `.`
3. others:  其他信息，建议字符:  `英文` `数字` `_`   `.`
4. package_md5:  安装包MD5 值

例如：`mysql-5.7.31-beta-8e955b24fefe7061eb79cfc61a9a02a1.tar.gz`

```shell
$ tar czf mysql-5.7.31.tar.gz mysql
$ md5sum mysql-5.7.31.tar.gz
8e955b24fefe7061eb79cfc61a9a02a1
$ mv mysql-5.7.31.tar.gz mysql-5.7.31-8e955b24fefe7061eb79cfc61a9a02a1.tar.gz
```

### 2.3.  配置文件(yaml)说明

平台预留KEY值（该KEY值存在指定定义，请准确使用）：

| KEY          | 说明         | 备注                                   |
| ------------ | ------------ | -------------------------------------- |
| service_port | 服务端口     | 供其他程序连接的端口号                 |
| base_dir     | 应用安装目录 |                                        |
| log_dir      | 应用日志目录 | 服务的日志采集会采集该目录下*.log 文件 |
| data_dir     | 应用数据目录 |                                        |
| username     | 用户名       |                                        |
| password     | 密码         |                                        |

```yaml
# 类型定义，发布基础组件时 ,指定类型为 component （类型：string）
kind: component
# 组件在平台显示的名称，请与组件目录名称保持一致，建议字符：英文、数字、_ （类型：string）
name: mysql
# 上传后显示的组件版本，建议字符： 数字、字母、_ 、. （类型：string）
version: 5.7.31
# 组件描述信息，建议长度256字符之内，请针对组件书写贴切的描述文字 （类型：string）
description: "MySQL是一个关系型数据库管理系统，由瑞典MySQL AB 公司开发，属于 Oracle 旗下产品。MySQL 是最流行的关系型数据库管理系统之一，在 WEB 应用方面，MySQL是最好的 RDBMS (Relational Database Management System，关系数据库管理系统) 应用软件之一。"
# 组件所属标签，请针对组件功能设置准确标签，平台会针对该标签对组件进行分类，（类型：list[string,string...]）
labels:
  - 数据库
# 指定该服务安装后是否需要启动 （类型：boolean)
auto_launch: false
# 指定组件是否为基础环境组件，如 jdk, 该类组件以基础环境方式安装 （类型：boolean)
base_env: flase
# 定义组件所需端口号，如不启用端口，可留空 （类型：list[map,map...])
ports:
    # 端口描述名称，用户在安装时会以该名称显示表单内容（类型：string)
  - name: 服务端口
    # 端口协议，支持 TCP/UDP
    protocol: TCP
    # 端口英文描述名称，该key会传入到安装脚本中 （类型： string）支持（英文、数字、_)
    key: service_port  # 注：service_port 为保留关键词，表示 为 提供服务的端口
    # 组件的默认端口号，在安装时，会以该值填入表单中（类型： int）
    default: 3306
# 组件监控相关配置，定义该组件在安装后如何监控 ，如果不需要监控可留空 （类型： map）
monitor:
  # 监控进程名称，如“mysqld”，平台在发现mysqld进程不存在后，会发送告警提醒 ，不需要监控可留空（类型：string）
  process_name:  "mysqld"
  # 监控端口号，请根据 ports 中的变量设置，不需要监控可留空 （类型： {string}）
  metric_port: {service_port}
---
# 设置集群模式方式，如果组件需要支持多种方式安装，可以在该字段中定义，如只支持单个实例安装，可留空（类型：map[list[map,map...]])
deploy:
  # 定义单实例模式安装 （类型：list[map,map...])
  single:
      # 部署方式的中文描述名称，该值会在表单中选择集群模式时显示 （类型：string）
    - name: 单实例
      # 该模式的key值 （类型：string）
      key: single
  # 定义多种集群模式安装 （类型：list[map,map...])
  complex:
      # 部署方式的中文描述名称，该值会在表单中选择集群模式时显示 （类型：string）
    - name: 主从模式
      # 该模式的key值 （类型：string）
      key: master_slave
      # 集群节点设置 （类型： map）
      nodes:
        # 初始节点数量 （类型：int）
        start: 2
        # 增加节点步长 （类型：int）
        step: 1
# 定义该组件安装所需依赖组件名称与版本,如不需其他组件依赖，可留空 （类型： list[map,map..])
#例：
#dependencies:
#  - name: jdk
#    version: 8u223
dependencies:
# 该组件所需最小资源需求 （类型：map)
resources:
  # cpu最小需求 ，1000m 表示 1核  （类型：string）
  cpu: 1000m
  # 内存最小需求， 500m 表示 500兆内存 （类型：string）
  memory: 500m

---
# 定义安装组件时所需参数，该参数会传入到 安装脚本中 （类型：list[map,map...]）
install:
    # 传入参数中文描述名称，该名称会在用户安装组件时显示到表单中 （类型： string）
  - name: "安装目录"
    # 传入参数key值，会将该key与值 传入到安装脚本中 （类型：string）
    key: base_dir
    # 上面key默认值 （类型： stirng）
    default: "{data_path}/mysql"  # 注： {data_path} 为主机数据目录占位符，请勿使用其他代替
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
# 程序控制脚本与服务目录的相对路径 （类型：map）
control:
  # 启动脚本路径，如没有可留空 （类型：string）
  start: "./scripts/mysql start"
  # 停止脚本路径，如没有可留空 （类型：stirng）
  stop: "./scripts/mysql stop"
  # 重启脚本路径，如没有可留空 （类型：stirng）
  restart: "./scripts/mysql restart"
  # 重载脚本路径，如没有可留空 （类型：stirng）
  reload:
  # 安装脚本路径，必填 （类型：stirng）
  install: "./scripts/install.py"
  # 初始化脚本路径，必填 （类型：stirng）
  init:  "./scripts/init.py"
```

### 2.4. 安装脚本编写说明

在安装包成功发布后，可通过平台进行安装，平台会调用配置文件中指定的安装脚本进行程序安装，平台将会把安装脚本所需参数以如下形式进行传参，需要脚本在编写时对此进行支持。

传参示例：

```shell
$ python ./scripts/install.py --local_ip 192.168.1.2 --data_json /data/LKJD82JDL.json
```

其中 local_ip 为安装主机的IP地址，data_json为安装所需数据文件路径

安装脚本需要根据data_json内数据进行组件的安装、替换其他文件内的占位符

data.json示例:

```json
[
    {
        "name":"nacos",
        "ip":"1.1.1.1",
        "version":"2.0.1",
        "ports":[
            {
                "key":"service_port",
                "name":"xxx端口",
                "default":8001
            }
        ],
        "install_arg":[
            {
                "key":"base_dir",
                "name":"服务目录",
                "default":"/data/app/nacos"
            },
            {
                "key":"data_dir",
                "name":"数据目录",
                "default":"/data/appData/nacos"
            },
            {
                "key":"username",
                "name":"用户名",
                "default":"admin"
            },
            {
                "key":"password",
                "name":"密码",
                "default":"admin123"
            }
        ],
        "deploy_mode":{

        },
        "cluster_name":"",
        "instance_name":"nacos-1",
        "dependence":[
            {
                "name":"mysql",
                "instance_name":"mysql-100",
                "cluster_name":"mysql-JDLK3KA"
            }
        ]
    },
    {
        "name":"mysql",
        "ip":"192.1.2.3",
        "version":"5.0.1",
        "ports":[
            {
                "key":"service_port",
                "name":"服务端口",
                "default":10601
            }
        ],
        "install_arg":[
            {
                "key":"base_dir",
                "name":"服务目录",
                "default":"/data/app/mysql"
            },
            {
                "key":"data_dir",
                "name":"数据目录",
                "default":"/data/appData/mysql"
            },
            {
                "key":"data_dir",
                "name":"日志目录",
                "default":"/data/appData/log"
            },
            {
                "key":"username",
                "name":"用户名",
                "default":"root"
            },
            {
                "key":"password",
                "name":"密码",
                "default":"root123"
            }
        ],
        "deploy_mode":{

        },
        "cluster_name":"",
        "instance_name":"mysql-100",
        "dependence":[

        ]
    }
]
```



## 3. 应用服务打包规范

### 3.1. 目录规范

在发布类别为应用服务的产品时，需要将产品名称、所属产品的服务名称、版本号做到全局统一

**目录示例：**

发布产品名称为“omp",其中包含 3个服务为“omp_server","omp_web","omp_component" 的目录结构如下

```shell
$ tree omp
omp
├── omp.svg # 定义产品图标，会在平台中展示，如果不创建则平台会展示缺省图标
├── omp     # 定义产品下服务配置文件目录，将所需服务的配置文件存在该目录
│   ├── omp_server.yaml  # 服务 omp_server 配置文件，文件名需要与服务名称一致
│   ├── omp_web.yaml  # 服务 omp_web 配置文件，文件名需要与服务名称一致
│   └── omp_component.yaml  # 服务 omp_agent 配置文件，文件名需要与服务名称一致
├── omp_server-0.1.0-5d1ac8ce87323fc399506d1335ae5c98.tar.gz  # 服务 omp_server 压缩包，以“-” 为分隔符，第一个为服务名称，需要与服务名称一致，格式为 {service_name}-{service_version}-{others}-{package_md5}.tar.gz
├── omp_web-0.1.0-5d1ac8ce87323fc399506d1335ae5c98.tar.gz  # 服务 omp_web 压缩包
├── omp_component-0.1.0-5d1ac8ce87323fc399506d1335ae5c98.tar.gz  # 服务 omp_agent 压缩包
└── omp.yaml        # 定义产品配置文件，文件名需要与产品名称一致
```

其中服务目录以omp_server为例：

```shell
$ tree omp_server
omp_server    # 服务包解压后目录名称，与服务名一致
├── bin     # 服务控制脚本目录，启动、停止等
│   └── omp_server    # 服务控制脚本，与服务名称一致
├── omp_server.yaml    # 服务配置文件，与产品包中保持一致
└── scripts            # 安装、升级脚本目录
    ├── init.py        # 初始化脚本
    ├── install.py     # 安装脚本
    └── update.py      # 升级脚本
```

### 3.2. 压缩包命名规范

请使用 `{name}-{version}-{others}-{package_md5}.tar.gz`  格式进行打包命名

1. name:   安装包名称，建议字符:  `英文`  `数字`   `_`
2. version: 安装包版本，建议字符:  `英文` `数字` `_`   `.`
3. others:  其他信息，建议字符:  `英文` `数字` `_`   `.`
4. package_md5:  安装包MD5 值

例如： omp-0.1.0-8e955b24fefe7061eb79cfc61a9a02a1.tar.gz

### 3.3. 配置文件yaml说明

发布类别为应用服务的产品时，需分别对 产品配置文件和产品下服务配置文件进行配置

#### 3.3.1. 产品配置文件（yaml）格式说明

```yaml
# 类型定义，发布应用服务时,产品指定类型为 product （类型：string）
kind: product
# 定义产品名称，此名称需要与产品目录名称、产品配置文件名称保持一致，建议字符：英文、数字、_  （类型: string)
name: omp
# 上传后显示的产品版本，建议字符： 数字、字母、_ 、. （类型：string）
version:
# 产品描述信息，建议长度256字符之内，请针对产品书写贴切的描述文字 （类型：string）
description: "运维管理平台（OperationManagementPlatform，以下简称OMP）以管理服务为中心，为服务的安装、管理提供便捷可靠的方式。"
# 组件所属标签，请针对组件功能设置准确标签，平台会针对该标签对组件进行分类，（类型：list[string,string...]）
labels:
  - omp
# 定义该产品安装所需依赖产品名称与版本,如不需其他产品依赖，可留空 （类型： list[map,map..])
dependencies:

# 定义该产品下包含的服务信息，请确保列表中的服务包都包含在目录中，并且名称保持一致 （类型： list[map,map...])
service:
    # 包含服务名称，请与服务包名保持一致 （类型： string）
  - name: omp_server
    # 服务版本，请与服务包版本一致 （类型：string）
    version: 0.1.0
  - name: omp_web
    version: 0.1.0
  - name: omp_component
    version: 0.1.0
```

#### 3.3.2. 服务配置文件（yaml）格式说明

```yaml
# 类型定义，发布应用服务时,产品包含的服务指定类型为 service （类型：string）
kind: service
# 服务在平台显示的名称，请与服务目录名称保持一致，建议字符：英文、数字、_ （类型：string）
name: omp_server
# 上传后显示的服务版本，建议字符： 数字、字母、_ 、. （类型：string）
version: 0.1.0
# 服务描述信息，建议长度256字符之内，请针对组件书写贴切的描述文字 （类型：string）
description: "服务描述内容..."
# 指定该服务安装后是否需要启动 （类型：boolean)
auto_launch: true
# 指定服务是否为基础环境组件，如 jdk, 该类组件以基础环境方式安装 （类型：boolean)
base_env: flase
# 定义服务所需端口号，如不启用端口，可留空 （类型：list[map,map...])
ports:
    # 端口描述名称，用户在安装时会以该名称显示表单内容（类型：string)
  - name: 服务端口
    # 端口协议，支持 TCP/UDP
    protocol: TCP
    # 端口英文描述名称，该key会传入到安装脚本中 （类型： string）支持（英文、数字、_)
    key: service_port  # 注：service_port 为保留关键词，表示 为 提供服务的端口
    # 组件的默认端口号，在安装时，会以该值填入表单中（类型： int）
    default: 19001
# 服务监控相关配置，定义该服务在安装后如何监控 ，如果不需要监控可留空 （类型： map）
monitor:
  # 监控进程名称，如“service_a”，平台在发现service_a进程不存在后，会发送告警提醒,不需要监控可留空（类型：string）
  process_name:  ""
  # 监控端口号，请根据 ports 中的变量设置，不需要监控可留空 （类型： {string}）
  metric_port: {service_port}
---
# 定义该组件安装所需依赖组件名称与版本,如不需其他组件依赖，可留空 （类型： list[map,map..])
dependencies:
  - name: mysql
    version: 5.7.31
  - name: redis
    version: 5.0.1
  - name: python
    version: 3.8.3
# 该组件所需最小资源需求 （类型：map)
resources:
  # cpu最小需求 ，1000m 表示 1核  （类型：string）
  cpu: 1000m
  # 内存最小需求， 500m 表示 500兆内存 （类型：string）
  memory: 500m
---
# 定义安装组件时所需参数，该参数会传入到 安装脚本中 （类型：list[map,map...]）
install:
    # 传入参数中文描述名称，该名称会在用户安装组件时显示到表单中 （类型： string）
  - name: "安装目录"
    # 传入参数key值，会将该key与值 传入到安装脚本中 （类型：string）
    key: base_dir
    # 上面key默认值 （类型： stirng）
    default: "{data_path}/omp_server"  # 注： {data_path} 为主机数据目录占位符，请勿使用其他代替
#  - name: "JVM设置"
#    key: jvm
#    default: "-XX:MaxPermSize=512m -Djava.awt.headless=true"
# 程序控制脚本与服务目录的相对路径 （类型：map）
control:
  # 启动脚本路径，如没有可留空,脚本名称建议与服务名称一致  （类型：string）
  start: "./bin/omp_server start"
  # 停止脚本路径，如没有可留空，脚本名称建议与服务名称一致 （类型：stirng）
  stop: "./bin/omp_server stop"
  # 重启脚本路径，如没有可留空，脚本名称建议与服务名称一致 （类型：stirng）
  restart: "./bin/omp_server restart"
  # 重载脚本路径，如没有可留空 （类型：stirng）
  reload:
  # 安装脚本路径，必填 （类型：stirng）
  install: "./scripts/install.py"
  # 初始化脚本路径，必填 （类型：stirng）
  init:  "./scripts/init.py"
```
