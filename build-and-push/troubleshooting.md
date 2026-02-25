# Build & Push 故障排查指南

## 目录

- [依赖问题](#依赖问题)
- [Docker 问题](#docker-问题)
- [Maven 问题](#maven-问题)
- [Harbor 问题](#harbor-问题)
- [部署问题](#部署问题)
- [网络问题](#网络问题)

---

## 依赖问题

### 问题 1: 未找到 PowerShell-Yaml 模块

**错误信息:**
```
[ERROR] 未找到PowerShell-Yaml模块
```

**原因:**
PowerShell-Yaml 模块未安装。

**解决方案:**
```powershell
# 安装 PowerShell-Yaml 模块
Install-Module -Name powershell-yaml -Force -Scope CurrentUser

# 验证安装
Get-Module -ListAvailable -Name powershell-yaml
```

如果安装失败，尝试以下方案：
```powershell
# 使用 NuGet 手动安装
Register-PSRepository -Default -ErrorAction SilentlyContinue
Install-Module -Name powershell-yaml -Force -Scope CurrentUser -Repository PSGallery
```

---

### 问题 2: Docker 未安装或未运行

**错误信息:**
```
[ERROR] Docker未安装或未运行,请先安装Docker Desktop
```

**原因:**
Docker Desktop 未安装或未运行。

**解决方案:**

**Windows:**
1. 下载并安装 Docker Desktop for Windows
2. 启动 Docker Desktop
3. 验证安装:
```powershell
docker --version
```

**Linux:**
```bash
sudo systemctl start docker
sudo systemctl enable docker
docker --version
```

---

### 问题 3: Maven 未安装

**错误信息:**
```
[ERROR] Maven未安装,请先安装Maven
```

**原因:**
Maven 未安装或未配置环境变量。

**解决方案:**

**Windows:**
1. 下载 Maven: https://maven.apache.org/download.cgi
2. 解压到 `C:\Program Files\Apache\Maven`
3. 添加到系统环境变量:
   - `MAVEN_HOME`: `C:\Program Files\Apache\Maven`
   - Path: 添加 `%MAVEN_HOME%\bin`
4. 验证安装:
```powershell
mvn --version
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install maven

# CentOS/RHEL
sudo yum install maven

# 验证
mvn --version
```

---

## Docker 问题

### 问题 4: Docker 镜像构建失败

**错误信息:**
```
[ERROR] Docker镜像构建失败
```

**可能原因:**
1. Dockerfile 不存在或语法错误
2. 基础镜像下载失败
3. 构建上下文有问题

**解决方案:**

1. 检查 Dockerfile 是否存在:
```powershell
cd shundao-terminal
ls Dockerfile
```

2. 手动测试构建:
```powershell
docker build -t test:latest .
```

3. 检查 Dockerfile 语法，特别注意:
   - `FROM` 命令的基础镜像是否正确
   - `COPY`/`ADD` 的文件路径是否正确
   - 多阶段构建的引用是否正确

4. 查看详细日志:
```powershell
docker build -t test:latest . --progress=plain
```

---

### 问题 5: Docker 推送失败

**错误信息:**
```
[ERROR] 镜像推送失败
```

**可能原因:**
1. 未登录 Harbor
2. 镜像标签错误
3. 网络连接问题
4. Harbor 存储空间不足

**解决方案:**

1. 确认已登录 Harbor:
```powershell
docker login test.synthoflow.com:8080
# 输入用户名和密码
```

2. 验证镜像标签:
```powershell
docker images | grep shundao
```

3. 手动推送测试:
```powershell
docker push test.synthoflow.com:8080/shundao-delivery-dev/shundao-terminal:1.0.0
```

4. 检查 Harbor 存储空间:
   - 登录 Harbor Web 界面
   - 检查项目存储使用情况
   - 必要时清理旧镜像

---

## Maven 问题

### 问题 6: Maven 构建失败

**错误信息:**
```
[ERROR] Maven构建失败
```

**可能原因:**
1. pom.xml 依赖问题
2. Maven 仓库连接失败
3. Java 版本不匹配
4. 测试用例失败

**解决方案:**

1. 检查 Maven 详细错误信息:
```powershell
cd shundao-terminal
mvn clean package -P docker-dev -X
```

2. 常见问题排查:

**依赖问题:**
```powershell
# 清理本地仓库
rm -rf ~/.m2/repository

# 强制重新下载依赖
mvn clean package -U -P docker-dev
```

**Java 版本问题:**
```powershell
# 检查 Java 版本
java -version

# 确保使用 JDK 11
set JAVA_HOME=C:\Program Files\Java\jdk-11
```

**测试用例失败:**
```powershell
# 跳过测试构建
mvn clean package -DskipTests -P docker-dev
```

---

### 问题 7: Maven Profile 不存在

**错误信息:**
```
[ERROR] Profile 'docker-dev' does not exist
```

**原因:**
`docker-dev` profile 未在 `pom.xml` 中定义。

**解决方案:**

检查 pom.xml 中的 profile 配置:
```xml
<profiles>
    <profile>
        <id>docker-dev</id>
        <properties>
            <docker.image.name>shundao-terminal</docker.image.name>
        </properties>
    </profile>
</profiles>
```

如果不存在，需要添加对应的 profile。

---

## Harbor 问题

### 问题 8: Harbor 登录失败

**错误信息:**
```
[ERROR] Harbor登录失败
```

**可能原因:**
1. 用户名或密码错误
2. Harbor 服务不可用
3. HTTPS 证书问题

**解决方案:**

1. 验证用户名和密码:
```powershell
# 手动登录测试
docker login test.synthoflow.com:8080
```

2. 检查 Harbor 服务状态:
```powershell
# 测试连通性
ping test.synthoflow.com
curl http://test.synthoflow.com:8080
```

3. HTTPS 证书问题（自签名证书）:
```powershell
# 添加到 Docker daemon 配置
# 编辑 %USERPROFILE%\.docker\daemon.json
{
  "insecure-registries": ["test.synthoflow.com:8080"]
}

# 重启 Docker
```

---

### 问题 9: Harbor 项目不存在

**错误信息:**
```
[WARNING] Harbor项目不存在,创建项目: shundao-delivery-dev
[ERROR] Harbor项目创建失败
```

**可能原因:**
1. Harbor API 权限不足
2. Harbor API 配置错误

**解决方案:**

1. 手动创建 Harbor 项目:
   - 登录 Harbor Web 界面
   - 创建项目 `shundao-delivery-dev`
   - 设置项目为公开或私有

2. 检查 API 配置:
```yaml
# deploy-config.yml
harbor:
  registry: "test.synthoflow.com:8080"  # 注意包含端口号
  username: "admin"
  password: "your-password"
```

3. 验证 API 访问:
```powershell
$headers = @{
    Authorization = "Basic " + [Convert]::ToBase64String(
        [Text.Encoding]::ASCII.GetBytes("admin:password")
    )
}
Invoke-RestMethod -Uri "http://test.synthoflow.com:8080/api/v2.0/projects" -Headers $headers
```

---

## 部署问题

### 问题 10: 远程部署失败

**错误信息:**
```
[WARNING] 自动部署过程中出现问题
```

**可能原因:**
1. SSH 连接失败
2. Docker Compose 命令失败
3. 服务健康检查失败

**解决方案:**

1. 检查 SSH 连接:
```powershell
ssh root@your-server.com
```

2. 检查服务器上的 Docker 状态:
```bash
ssh root@your-server.com
docker ps
docker-compose ps
```

3. 手动运行部署命令:
```bash
# 在服务器上执行
cd /home/project/
docker-compose pull
docker-compose up -d
docker-compose ps
```

4. 检查服务日志:
```bash
docker-compose logs -f shundao-terminal
```

---

### 问题 11: 服务健康检查失败

**错误信息:**
```
[ERROR] 健康检查超时: shundao-terminal
```

**可能原因:**
1. 服务启动慢
2. 健康检查路径错误
3. 服务启动失败

**解决方案:**

1. 调整健康检查超时时间:
```yaml
# deploy-config.yml
deploy:
  health_check:
    enabled: true
    timeout: 120  # 增加超时时间
    interval: 10
```

2. 检查服务是否正常启动:
```bash
docker-compose ps
docker logs shundao-terminal
```

3. 手动测试健康检查:
```bash
curl http://localhost:18030/actuator/health
```

4. 如果健康检查路径错误，修改 `deploy-config.yml`:
```yaml
modules:
  shundao-terminal:
    health_check: "/health"  # 或实际的健康检查路径
```

---

## 网络问题

### 问题 12: 无法连接到 Harbor

**错误信息:**
```
[ERROR] 连接 Harbor 超时
```

**可能原因:**
1. 网络连接问题
2. 防火墙阻止
3. DNS 解析失败

**解决方案:**

1. 测试网络连通性:
```powershell
ping test.synthoflow.com
telnet test.synthoflow.com 8080
```

2. 检查防火墙:
```powershell
# Windows
netsh advfirewall firewall show rule name=all

# Linux
sudo iptables -L
```

3. 检查 DNS 解析:
```powershell
nslookup test.synthoflow.com
```

4. 使用 IP 地址代替域名:
```yaml
# deploy-config.yml
harbor:
  registry: "192.168.1.100:8080"  # 使用 IP 地址
```

---

## 通用调试技巧

### 查看详细日志

```powershell
# 运行脚本时捕获详细输出
.\build-and-push.ps1 -Environment dev -Service all 2>&1 | Tee-Object -FilePath build.log
```

### 逐步执行

```powershell
# 1. 先只构建，不推送
# 修改脚本注释掉 docker push

# 2. 手动测试每一步
mvn clean package -P docker-dev
docker build -t test:latest .
docker login test.synthoflow.com:8080
docker push test.synthoflow.com:8080/xxx:xxx
```

### 检查配置文件

```powershell
# 验证 YAML 语法
Import-Module powershell-yaml
$config = Get-Content deploy-config.yml -Raw | ConvertFrom-Yaml
$config | ConvertTo-Json -Depth 10
```

---

## 获取帮助

如果以上方案都无法解决问题:

1. 查看完整日志文件
2. 记录错误信息
3. 收集环境信息:
   - OS 版本
   - PowerShell 版本: `$PSVersionTable.PSVersion`
   - Docker 版本: `docker --version`
   - Maven 版本: `mvn --version`
4. 联系技术支持团队