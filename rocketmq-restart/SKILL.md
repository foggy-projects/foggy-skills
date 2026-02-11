---
name: rocketmq-restart
description: 重启 192.168.31.238 上的 RocketMQ（NameServer 和 Broker）。当用户需要重启 RocketMQ、排查 RocketMQ 问题、或使用 /rocketmq-restart 时使用。
---

# RocketMQ 重启操作

通过 SSH 连接 192.168.31.238，安全重启 RocketMQ NameServer 和 Broker。

## 连接信息

| 参数 | 值 |
|------|-----|
| 主机 | 192.168.31.238 |
| 端口 | 22 |
| 用户 | root |
| 密码 | @Shundao888 |

## 环境信息

| 参数 | 值 |
|------|-----|
| JAVA_HOME | /usr/java/jdk-12.0.2 |
| RocketMQ 目录 | /home/rocketmq |
| Broker 配置 | /home/rocketmq/conf/broker.conf |
| 数据目录 | /root/store |
| 日志目录 | /home/rocketmq-log/logs |
| NameServer 端口 | 9876 |
| Broker 端口 | 10911 |
| Dashboard 端口 | 8080（jar: rocketmq-dashboard-2.0.0.jar） |

## SSH 连接方式

使用 Python paramiko 库（Windows 环境无 sshpass）：

```python
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.31.238', 22, 'root', '@Shundao888')
```

注意事项：
- 启动类命令（mqbroker/mqnamesrv）会阻塞 stdout，使用 `exec_command` 后不要 `read()`，改用 fire-and-forget 模式
- 所有 mqadmin/mqbroker/mqnamesrv 命令前需 `export JAVA_HOME=/usr/java/jdk-12.0.2`

## 执行流程

### 1. 检查当前状态

```bash
ps aux | grep -E '(NamesrvStartup|BrokerStartup|rocketmq-dashboard)' | grep -v grep
```

### 2. 停止 Broker（先停 Broker，后停 NameServer）

```bash
export JAVA_HOME=/usr/java/jdk-12.0.2
/home/rocketmq/bin/mqshutdown broker
```

等待进程退出，轮询检查：
```bash
ps aux | grep BrokerStartup | grep -v grep | wc -l
```

如果 30 秒内未退出 → `kill -9 <pid>`

### 3. 停止 NameServer（如需重启 NameServer）

```bash
export JAVA_HOME=/usr/java/jdk-12.0.2
/home/rocketmq/bin/mqshutdown namesrv
```

同样轮询等待退出。

### 4. 启动 NameServer（如已停止）

```bash
export JAVA_HOME=/usr/java/jdk-12.0.2
setsid /home/rocketmq/bin/mqnamesrv </dev/null >/dev/null 2>&1 &
```

等待 5 秒，验证端口 9876 已监听：
```bash
ss -tlnp | grep 9876
```

### 5. 启动 Broker

```bash
export JAVA_HOME=/usr/java/jdk-12.0.2
setsid /home/rocketmq/bin/mqbroker -c /home/rocketmq/conf/broker.conf </dev/null >/dev/null 2>&1 &
```

**关键**：必须带 `-c /home/rocketmq/conf/broker.conf`，否则 Broker 不会读取 `namesrvAddr` 配置，导致不注册到 NameServer。

等待 10 秒，验证进程启动：
```bash
ps aux | grep BrokerStartup | grep -v grep
```

### 6. 验证 Broker 注册到 NameServer

等待 5 秒后执行：
```bash
export JAVA_HOME=/usr/java/jdk-12.0.2
/home/rocketmq/bin/mqadmin clusterList -n localhost:9876 2>&1
```

应看到 `broker-a` 行数据，而不是仅有表头。

### 7. 验证 Topic 路由（可选）

```bash
export JAVA_HOME=/usr/java/jdk-12.0.2
/home/rocketmq/bin/mqadmin topicRoute -n localhost:9876 -t topic_payment 2>&1
```

应返回包含 `brokerDatas` 的 JSON。

## 决策规则

- 如果用户只说"重启 Broker" → 仅重启 Broker（步骤 2、5、6），不动 NameServer
- 如果用户说"重启 RocketMQ" → 全部重启（步骤 2-7）
- 如果 Broker 启动后 clusterList 为空 → 检查 broker.conf 是否包含 `namesrvAddr = localhost:9876`
- 如果 mqadmin 输出为空 → 可能是 JAVA_HOME 未设置，检查命令前缀
- 如果 Dashboard 也需要重启 → `kill` 旧进程后：`setsid java -Drocketmq.namesrv.addr=localhost:9876 -jar /path/to/rocketmq-dashboard-2.0.0.jar </dev/null >/dev/null 2>&1 &`

## broker.conf 关键配置

```properties
brokerClusterName = DefaultCluster
brokerName = broker-a
brokerId = 0
deleteWhen = 04
fileReservedTime = 48
brokerRole = ASYNC_MASTER
flushDiskType = ASYNC_FLUSH
namesrvAddr = localhost:9876
```

如果 `namesrvAddr` 缺失，必须补上，否则 Broker 不会注册到 NameServer。

## 常用诊断命令

```bash
# 查看所有 topic
/home/rocketmq/bin/mqadmin topicList -n localhost:9876

# 查看指定 topic 路由
/home/rocketmq/bin/mqadmin topicRoute -n localhost:9876 -t <topic_name>

# 查看集群信息
/home/rocketmq/bin/mqadmin clusterList -n localhost:9876

# 查看 Broker 状态
/home/rocketmq/bin/mqadmin brokerStatus -n localhost:9876 -b localhost:10911

# 创建 topic
/home/rocketmq/bin/mqadmin updateTopic -n localhost:9876 -b localhost:10911 -t <topic_name>

# 查看 broker 本地存储的 topic 列表
cat /root/store/config/topics.json
```

所有命令前需 `export JAVA_HOME=/usr/java/jdk-12.0.2`。
