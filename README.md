# Readme
# OMP-运维管理平台
OMP（Operation Management Platform）是云智慧公司自主设计、研发的轻量级、聚合型、智能运维管理平台。是一款为用户提供便捷运维能力和业务管理的综合平台。具备运维一应俱全的功能，目的是提升运维自动化、智能化，提高运维效率，提升业务连续性和安全性。

# OMP设计初衷
## 目前运维面临的痛点：
- 主机环境多样性，难以统一管理：如：混合云、私有云、跨IDC、虚拟化、容器化等
- 业务变更难度较大，自动编排能力较低
- 业务状态监控，多平台难以数据联动
- 业务出现异常，难以实现故障自愈
- 业务运行状态，难以评估，更难以分析
- 运维知识匮乏，缺少专家指导及专家解决方案

运维管理平台(OMP)的设计初衷就是想打造一应俱全的运维平台，降低交付难度，提升运维自动化、智能化，提高运维效率，提升业务连续性和安全性。

# OMP核心功能
- **主机纳管**：纳管主机资源，实时监控主机运行状态，可在线管理、在线连接终端等
- **应用管理**：平台已内置常用基础组件，也支持符合标准的自研服务发布到应用商店，从而提供便捷的应用管理，如：安装部署、变更发布、弹性扩缩容、在线配置、优化等
- **应用监控**：涵盖标准监控、定制监控、链路监控、智能监控等多种业务场景，通过大数据智能测算，可感知未来趋势，将异常控制在发生前
- **故障自愈**：当业务系统出现异常或故障时，可按照预定的自愈策略进行故障治理，极大降低故障对业务影响，减少企业损失
- **状态巡检**：自动、手动进行业务指标、运行状态汇总，支持自动发送报告到指定邮箱
- **备份/恢复**：针对核心数据进行本地+异地备份，支持自动执行备份并将数据发送至指定邮箱，达到异地的存储效果，确保数据安全
- **精简工具**：提供运维常用工具、命令、脚本、SQL等，为日常运维操作提供便利，减少误操作、减低技术门槛，支持自行维护、扩充更多工具
- **权限管理**：针对不同用户、角色，进行权限控制，及操作审计

# 架构设计
![./doc/architecture.png](./doc/architecture.png)

## Demo

通过浏览器访问页面，访问入口为：http://omp.cloudwise.com/#/login    \
默认用户名：admin     \
默认密码：Yunweiguanli@OMP  \
每晚 00:00 将重置数据



# 使用 OMP
## 安装部署
当前OMP安装包内部包含了其使用的所有组件，建议将OMP部署在 /data/ 下，当前版本部署流程如下：   \
step0：下载解压安装包

```shell
tar -xvf omp_open-*.tar.gz -C /data
```

step1：编辑文件，检查环境配置

```shell
vim /data/omp/config/omp.yaml
```

注意：当前版本已携带mysql、redis安装，配置信息如下，如需修改请在安装前修改

```yaml
# redis相关配置
redis:
  host: 127.0.0.1
  port: 6380
  password: common123
# mysql相关配置
mysql:
  host: 127.0.0.1
  port: 3307
  username: common
  password: Common@123
```

step2：执行安装脚本
```shell
cd /data/omp && bash scripts/install.sh
# 注意1：执行后根据提示选择本机ip，如主机上存在多网卡多IP情况，需要根据业务需求自行判断使用哪个ip地址
# 注意2：当前执行操作的用户即为OMP中各个服务进程的运行用户，在以后的维护中，也应使用此用户进行操作
```

## 管理OMP

注意：如需停止 OMP 相关服务，请先执行 “停止 OMP 定时保活任务” 操作

```shell
# [服务名称] 值为： all 为对所有组件操作
# all|mysql|redis|tengine|uwsgi|worker|cron|salt|prometheus|alertmanager|grafana|loki
bash /data/omp/scripts/omp [服务名称] [status|start|stop|restart]
```

停止 OMP 定时保活任务：

```Apache
# 查看定时任务
crontab -e

# 删除或注释如下内容，否则定时任务会将 OMP 自动拉起
# */5 * * * * bash /data/omp/scripts/omp all start &>/dev/null
```

## 卸载OMP

omp节点上卸载操作如下：
```shell
bash /data/omp/scripts/uninstall.sh
```
## 升级 & 回滚 OMP

```shell
# 升级命令
bash cmd_manager omp_upgrade [必填参数：升级目标路径(如:/data/omp，注意此处路径末尾无/)] [选填参数:从某个断点处升级,默认开头]
# 例如
bash 升级包路径/scripts/cmd_manager omp_upgrade /data/omp(当前正在运行的旧安装路径)

# 回滚命令
bash cmd_manager omp_upgrade [必填参数：升级目标路径(如:/data/omp，注意此处路径末尾无/)] [选填参数:从某个断点处升级,默认开头]
# 例如
bash 升级包路径/scripts/cmd_manager omp_rollback /data/omp(当前正在运行的旧安装路径)
```

## 断点执行

常用于执行过程中某一步骤失败时，期望从失败步骤处再次执行时使用，正常情况无需考虑此参数，参数默认下标为0

升级回滚可以理解成为jenkins的pipliene 是分步骤执行的，当我们在某一个位置出现异常时，手动修复后通过错误节点再次进行时使用，而跳过之前已经升级（回滚）正确的步骤

```shell
# 升级流程顺序如下：
# PreUpdate, Mysql, Redis, Grafana, Tengine, OmpWeb, OmpServer, Python, PostUpdate
```



# 环境依赖

## 技术栈

### 后端技术栈

- Python 3.8.7
- Django 3.1.4
- Saltstack 3002.2
- Uwsgi 2.0.19.1

### 数据库

- mysql 5.7.37
- redis 6.2.7

### 前端技术栈

- Tengine 1.22.0
- React 17.0.1

### 监控技术栈

- Prometheus 2.25.1
- Alertmanager 0.24.0
- Grafana  9.3.8
- Loki 2.4.1
- Promtail 2.2.0

## 内置组件概览

| **组件名称** | **组件作用**                                     | **端口**     |
| ------------ | ------------------------------------------------ | ------------ |
| tengine      | 平台访问入口，代理前端页面及后端uwsgi程序        | 19001        |
| uwsgi        | web容器，用于提供 python Django 后端程序访问入口 | 19003        |
| salt         | 开源组件，服务器控制程序，提供主机 Agent 通信    | 19004、19005 |
| worker       | 异步任务、定时任务执行程序，有进程无端口         | -            |
| prometheus   | 开源组件，提供监控数据                           | 19011        |
| grafana      | 开源组件，提供监控面板                           | 19014        |
| alertmanager | 开源组件，提供日志告警                           | 19013、9094  |
| loki         | 开源组件，提供日志采集                           | 19012、9095  |
| redis        | 开源组件，提供缓存，消息队列                     | 6380         |
| mysql        | 开源组件，数据存储                               | 3307         |
| ntpd         | 开源组件，提供时间同步功能                       | 123（udp）   |



# 关于应用商店

## 如何制作一个OMP应用商店中的应用

[OMP 社区版-应用商店发布说明文档](./doc/app_publish.md)
> 内含
 - 基础组件打包规范
 - 应用服务打包规范
 - 目录和配置说明
 - postgreSql、redis、rocketmq等应用Demo

## 卸载应用商店中已经发布的应用

>已支持界面操作

```shell
export LD_LIBRARY_PATH=/data/omp/component/env/lib && /data/omp/component/env/bin/python3.8 /data/omp/scripts/source/uninstall_app_store.py --product 产品名称 --app_name 组件/服务名称 --version 版本
```

 已经部署服务实例的安装包，无法卸载

 参数说明：

1.  ***--version*** 缺省时，卸载所有版本
2.  卸载基础组件 ***--app_name 基础组件名称***
3.  卸载应用/产品  ***--product 应用/产品名称***
4.  卸载应用下指定服务 ***--product 应用/产品名称 --app_name 服务名称***





欢迎加入
获取更多关于OMP的技术资料，或加入OMP开发者交流群，可扫描下方二维码咨询

<img src="./doc/contact-us.png" width="600px" height="400px" />
