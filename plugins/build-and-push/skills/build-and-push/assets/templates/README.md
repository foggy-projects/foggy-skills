# 脚本模板目录

本目录包含可直接使用的脚本模板，用于快速配置和部署。

## 可用模板

| 模板文件 | 说明 |
|---------|------|
| `deploy-config-dev.yml` | 开发环境配置模板 |
| `deploy-config-test.yml` | 测试环境配置模板 |
| `deploy-config-prod.yml` | 生产环境配置模板 |
| `docker-compose.template.yml` | Docker Compose 模板 |

## 使用方法

1. 选择合适的模板文件
2. 复制到项目根目录并重命名为 `deploy-config.yml`
3. 根据实际情况修改配置项
4. 运行 `.\build-and-push.ps1`

## 注意事项

⚠️ **生产环境配置**
- 生产环境配置包含敏感信息，请妥善保管
- 不要将包含密码的配置文件提交到版本控制
- 建议使用 `.gitignore` 排除配置文件

⚠️ **SSH 密钥**
- 生产环境推荐使用 SSH 密钥认证而非密码
- 确保 SSH 密钥权限正确 (`chmod 600 ~/.ssh/id_rsa_prod`)

⚠️ **Harbor 项目**
- 首次使用时需要在 Harbor 手动创建对应项目
- 或者在脚本中自动创建（脚本已支持）