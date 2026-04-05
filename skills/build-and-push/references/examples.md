# Build & Push 使用示例

## 目录

- [基础使用示例](#基础使用示例)
- [常用场景](#常用场景)
- [进阶用法](#进阶用法)
- [配置文件示例](#配置文件示例)

---

## 基础使用示例

### 1. 交互式构建

适用于不熟悉参数的用户，脚本会逐步引导输入：

```powershell
.\build-and-push.ps1
```

交互流程示例：
```
========================================
  顺道配送项目构建推送向导
========================================
请根据提示输入参数,直接回车使用默认值

1. 选择构建环境:
   1. dev   - 开发环境 (默认)
   2. test  - 测试环境
   3. prod  - 生产环境
请选择环境 [1/dev]: 1

2. 选择服务:
   1. all - 所有已启用的服务 (默认)
   2. shundao-user - 用户服务
   3. shundao-cashier - 收银台服务
   4. shundao-shipment - 运单服务
   ...
请选择服务 [1/all]: 1

3. 输入版本号 (可选):
   留空将使用pom.xml中的默认版本
请输入版本号 [默认]:

========================================
  构建配置确认
========================================
构建环境: dev
选择服务: all
版本管理: 使用pom.xml默认版本
Harbor项目: shundao-delivery-dev
========================================

确认以上配置并开始构建? (Y/n): Y
```

---

## 常用场景

### 场景 1: 开发环境快速部署

**需求**: 开发完成后，快速部署到开发环境验证功能

```powershell
# 一键完成：构建 + 推送 + 部署
.\build-and-push.ps1 -Environment dev -Service all -Deploy
```

**执行结果示例**：
```
[2026-02-26 10:30:00] [INFO] 检查依赖...
[2026-02-26 10:30:05] [SUCCESS] Docker检查通过: Docker version 24.0.0
[2026-02-26 10:30:05] [SUCCESS] Maven检查通过: Apache Maven 3.6.3
[2026-02-26 10:30:08] [SUCCESS] 配置文件读取成功: deploy-config.yml
[2026-02-26 10:30:10] [INFO] 登录Harbor仓库: test.synthoflow.com:8080
[2026-02-26 10:30:12] [SUCCESS] Harbor登录成功
[2026-02-26 10:30:15] [INFO] 检查Harbor项目: shundao-delivery-dev
[2026-02-26 10:30:18] [SUCCESS] Harbor项目已存在: shundao-delivery-dev
...
[2026-02-26 10:45:30] [SUCCESS] shundao-terminal 镜像推送成功:
    test.synthoflow.com:8080/shundao-delivery-dev/shundao-terminal:1.0.0-SNAPSHOT-dev-20260226104430
...
[2026-02-26 10:45:35] [SUCCESS] 所有服务构建推送成功

========================================
  开始自动部署到远程服务器
========================================

[2026-02-26 10:45:40] [INFO] 部署版本: 1.0.0-SNAPSHOT-dev-20260226104430
[2026-02-26 10:45:45] [SUCCESS] 自动部署完成
```

---

### 场景 2: 单个服务调试部署

**需求**: 只修改了 `shundao-terminal` 服务，只部署这一个

```powershell
# 只构建推送，不自动部署（便于验证镜像）
.\build-and-push.ps1 -Environment dev -Service shundao-terminal

# 验证镜像后，再部署
```

或者直接：
```powershell
# 一键完成单个服务的构建+推送+部署
.\build-and-push.ps1 -Environment dev -Service shundao-terminal -Deploy
```

---

### 场景 3: 多个服务组合部署

**需求**: 修改了用户服务和终端服务，需要一起部署

```powershell
# 使用逗号分隔多个服务名
.\build-and-push.ps1 -Environment dev -Service "shundao-user,shundao-terminal" -Deploy
```

---

### 场景 4: 测试环境验证

**需求**: 功能开发完成，部署到测试环境进行联调

```powershell
.\build-and-push.ps1 -Environment test -Service all -Deploy
```

**注意事项**:
- 测试环境使用 `shundao-delivery-test` Harbor 项目
- 镜像标签格式：`{version}-test-{timestamp}`
- 部署服务器：`192.168.1.200` (test-server-1)

---

### 场景 5: 生产环境发布

**需求**: 正式版本发布到生产环境

```powershell
# 指定发布版本号（重要！）
.\build-and-push.ps1 -Environment prod -Service all -Version v1.2.0 -Deploy
```

**注意事项**:
- 生产环境使用 `shundao-delivery-prod` Harbor 项目
- 镜像标签格式：`{version}`（无时间戳，使用语义化版本号）
- `use_timestamp: false` 确保使用固定版本号
- 部署前务必确认版本号！

---

### 场景 6: 只构建不推送（开发调试）

**需求**: 本地构建调试，不推送到远程仓库

当前脚本不支持只构建不推送。如需此功能，可以：

**方案一**: 手动执行构建命令
```powershell
cd shundao-terminal
mvn clean package -P docker-dev
docker build -t shundao-terminal:local .
# 测试镜像
docker run -p 18030:18030 shundao-terminal:local
```

**方案二**: 修改脚本，添加 `-NoPush` 参数

---

## 进阶用法

### 1. 使用自定义配置文件

```powershell
# 使用自定义配置文件（如不同环境的配置）
.\build-and-push.ps1 -Environment dev -Service all -ConfigFile "deploy-config-test.yml"
```

### 2. 强制交互模式

```powershell
# 即使提供了参数，也强制进入交互模式
.\build-and-push.ps1 -Environment dev -Service all -Interactive
```

### 3. 查看帮助信息

```powershell
# 显示完整的使用说明
.\build-and-push.ps1 -Help
```

---

## 配置文件示例

### 完整的 deploy-config.yml 示例

```yaml
# ===================================
# Harbor镜像仓库配置
# ===================================
harbor:
  registry: "test.synthoflow.com:8080"
  username: "admin"
  password: "@Shundao888"

# ===================================
# 环境配置
# ===================================
environments:
  dev:
    harbor_project: "shundao-delivery-dev"
    spring_profile: "dev"
    use_timestamp: true
    environment_vars:
      JAVA_OPTS: "-Xms512m -Xmx1024m"
    servers:
      - name: "dev-server"
        host: "sdopen-test.foggysource.com"
        user: "root"
        port: 22
        auth_type: "password"
        password: "@Shundao888"
        compose_path: "/home/project2/"

  test:
    harbor_project: "shundao-delivery-test"
    spring_profile: "test"
    use_timestamp: true
    environment_vars:
      NACOS_SERVER_ADDR: "nacos-test.example.com:8848"
      JAVA_OPTS: "-Xms1024m -Xmx2048m"
    servers:
      - name: "test-server"
        host: "192.168.1.200"
        user: "root"
        port: 22
        auth_type: "password"
        password: "your-password"
        compose_path: "/opt/shundao-delivery"

  prod:
    harbor_project: "shundao-delivery-prod"
    spring_profile: "prod"
    use_timestamp: false  # 生产环境使用固定版本号
    environment_vars:
      JAVA_OPTS: "-Xms2048m -Xmx4096m"
    servers:
      - name: "prod-server-1"
        host: "192.168.1.10"
        user: "root"
        port: 22
        auth_type: "ssh_key"
        ssh_key: "~/.ssh/id_rsa_prod"
        compose_path: "/opt/shundao-delivery"

# ===================================
# 模块配置
# ===================================
modules:
  shundao-terminal:
    enabled: true
    display_name: "终端服务"
    port: 18030
    health_check: "/actuator/health"
  # ... 其他模块

# ===================================
# 构建配置
# ===================================
build:
  maven:
    skip_tests: true
    opts: "-DskipTests -Dmaven.javadoc.skip=true"
  docker:
    dockerfile: "Dockerfile"
    build_args: {}

# ===================================
# 部署配置
# ===================================
deploy:
  network_mode: "host"
  health_check:
    enabled: true
    timeout: 60
    interval: 5
```

---

## 常用命令速查表

| 场景 | 命令 |
|------|------|
| 交互式构建 | `.\build-and-push.ps1` |
| 所有服务到dev | `.\build-and-push.ps1 -Environment dev -Service all` |
| 单个服务到dev | `.\build-and-push.ps1 -Environment dev -Service shundao-terminal` |
| 多个服务到dev | `.\build-and-push.ps1 -Environment dev -Service "user,terminal"` |
| dev环境一键部署 | `.\build-and-push.ps1 -Environment dev -Service all -Deploy` |
| test环境部署 | `.\build-and-push.ps1 -Environment test -Service all -Deploy` |
| prod环境发布 | `.\build-and-push.ps1 -Environment prod -Service all -Version v1.0.0 -Deploy` |
| 查看帮助 | `.\build-and-push.ps1 -Help` |