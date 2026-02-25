# Build & Push 项目构建部署技能

## 简介

顺道配送项目的自动构建、推送和部署流程指导。

## 📚 文档导航

- [使用方法](#使用方法)
- [代码示例](./examples.md) - 常见场景的代码示例
- [脚本模板](./templates/) - 可直接使用的脚本模板
- [故障排查](./troubleshooting.md) - 常见问题及解决方案

## 适用场景

- 需要构建并推送服务到 Harbor 镜像仓库
- 需要构建并推送后自动部署到远程服务器
- 需要批量构建多个服务

## 使用方法

### 1. 交互模式（推荐）

```powershell
.\build-and-push.ps1
```

脚本会引导你：
1. 选择构建环境 (dev/test/prod)
2. 选择服务 (all/单个/多个)
3. 可选输入版本号
4. 是否自动部署

### 2. 命令行模式

```powershell
# 构建并推送所有服务到开发环境
.\build-and-push.ps1 -Environment dev -Service all

# 构建、推送并部署（一键完成）
.\build-and-push.ps1 -Environment dev -Service all -Deploy

# 构建单个服务到测试环境
.\build-and-push.ps1 -Environment test -Service shundao-user

# 构建多个服务
.\build-and-push.ps1 -Environment dev -Service "shundao-user,shundao-terminal"

# 指定版本构建到生产环境
.\build-and-push.ps1 -Environment prod -Service all -Version v1.0.0
```

### 3. 查看帮助

```powershell
.\build-and-push.ps1 -Help
```

## 环境对应关系

| 环境 | Harbor 项目 | 镜像标签 |
|------|-------------|----------|
| dev  | shundao-delivery-dev | `{version}-dev-{timestamp}` |
| test | shundao-delivery-test | `{version}-test-{timestamp}` |
| prod | shundao-delivery-prod | `{version}` |

## 支持的服务

根据 `deploy-config.yml` 中 `modules` 配置，所有 `enabled: true` 的服务都可以构建。

| 服务名 | 显示名称 | 端口 | 健康检查 |
|--------|----------|------|----------|
| shundao-user | 用户服务 | 18026 | /actuator/health |
| shundao-admin | 管理后台 | 18020 | /actuator/health |
| shundao-storeman | 网点/仓管端 | 18023 | /actuator/health |
| shundao-shipment | 收发货核心服务 | 18022 | /actuator/health |
| shundao-terminal | 外部运力对接服务 | 18030 | /actuator/health |
| shundao-cashier | 支付中心 | 18021 | /actuator/health |
| shundao-thirdparty | 第三方服务 | 18025 | /actuator/health |
| shundao-gateway | 网关服务 | 18028 | /actuator/health |
| shundao-shortlink | 短链服务 | 18031 | /actuator/health |
| shundao-task | 任务服务 | 18027 | /actuator/health |

## 构建流程

```
┌─────────────────────────────────────────────────────────────┐
│                    1. 检查依赖                              │
│    Docker, Maven, PowerShell-Yaml                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    2. 登录 Harbor                           │
│    docker login {registry}                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    3. 检查/创建 Harbor 项目                 │
│    API: /api/v2.0/projects/{project_name}                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    4. 构建依赖模块                          │
│    shundao-common → shundao-framework                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    5. Maven 构建                           │
│    mvn clean package -P docker-{env}                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    6. Docker 镜像构建                      │
│    docker build -t temp-image:latest .                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    7. 标记并推送                            │
│    docker tag → docker push                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    8. 自动部署 (可选)                       │
│    调用 remote-deploy.ps1                                  │
└─────────────────────────────────────────────────────────────┘
```

## 配置文件

脚本使用 `deploy-config.yml` 配置文件，主要配置项：

### Harbor 配置
```yaml
harbor:
  registry: "test.synthoflow.com:8080"
  username: "admin"
  password: "@Shundao888"
```

### 环境配置
```yaml
environments:
  dev:
    harbor_project: "shundao-delivery-dev"
    spring_profile: "dev"
    use_timestamp: true  # 是否使用时间戳标签
    environment_vars:
      JAVA_OPTS: "-Xms512m -Xmx1024m"
```

### 模块配置
```yaml
modules:
  shundao-terminal:
    enabled: true
    display_name: "终端服务"
    port: 18030
    health_check: "/actuator/health"
```

更多配置详情请查看 [examples.md](./examples.md)

## 快速开始

```powershell
# 1. 首次运行，安装依赖（如需）
Install-Module -Name powershell-yaml -Force -Scope CurrentUser

# 2. 一键构建并部署所有服务到开发环境
.\build-and-push.ps1 -Environment dev -Service all -Deploy

# 3. 查看部署结果
# 检查 Harbor 仓库: http://test.synthoflow.com:8080
# 检查服务器服务状态
```

## 相关脚本

| 脚本 | 作用 |
|------|------|
| `build-and-push.ps1` | 主脚本：构建、推送、部署 |
| `remote-deploy.ps1` | 远程部署脚本（由主脚本自动调用） |
| `deploy-config.yml` | 配置文件 |

## 更多资源

- 📖 [完整示例参考](./examples.md)
- 🛠️ [脚本模板](./templates/)
- 🔧 [故障排查指南](./troubleshooting.md)