# 邮件配置指南

本指南说明如何安全地配置 notebooklm-workflow 的邮件发送功能。

## 安全提示

**重要**：邮箱地址、密码等敏感信息**不应该**明文存储在代码或配置文件中。本项目使用环境变量来保护敏感信息。

## 配置步骤

### 步骤 1：复制环境变量模板

```bash
cd /path/to/evil-read-arxiv
cp .env.example .env.local
```

### 步骤 2：编辑 .env.local

```bash
# 发件人邮箱地址（你的 QQ 邮箱，可使用 foxmail 别名）
export EMAIL_SENDER="your-qq-number@foxmail.com"

# 收件人邮箱地址（多个收件人用逗号分隔）
export EMAIL_RECIPIENTS="recipient1@company.com,recipient2@example.com"

# SMTP 登录用户名（通常与发件人相同）
export EMAIL_USERNAME="your-qq-number@foxmail.com"

# SMTP 授权码（不是 QQ 密码！）
export EMAIL_PASSWORD="your-authorization-code-here"

# SMTP 服务器（QQ 邮箱固定为 smtp.qq.com）
export EMAIL_SMTP_SERVER="smtp.qq.com"

# SMTP 端口（587 使用 STARTTLS，465 使用 SSL）
export EMAIL_SMTP_PORT="587"

# 是否使用 SSL（true 或 false）
export EMAIL_USE_SSL="true"
```

### 步骤 3：获取 QQ 邮箱授权码

1. 登录 https://mail.qq.com
2. 点击"设置" → "账户"
3. 找到 "POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV 服务"
4. 开启 "POP3/SMTP 服务"
5. 点击"生成授权码"
6. 按提示发送短信验证
7. 复制生成的授权码到 `.env.local` 的 `EMAIL_PASSWORD` 字段

### 步骤 4：加载环境变量

#### 临时生效（当前终端会话）

```bash
source .env.local
```

#### 永久生效（推荐）

将加载命令添加到你的 shell 配置文件：

```bash
# macOS/Linux (zsh)
echo 'source /absolute/path/to/evil-read-arxiv/.env.local' >> ~/.zshrc
source ~/.zshrc

# macOS/Linux (bash)
echo 'source /absolute/path/to/evil-read-arxiv/.env.local' >> ~/.bashrc
source ~/.bashrc

# Windows PowerShell
Add-Content -Path $PROFILE -Value 'source "C:/path/to/evil-read-arxiv/.env.local"'
```

### 步骤 5：验证配置

运行测试脚本验证配置是否正确：

```bash
cd notebooklm-workflow/scripts
python3 send_email.py
```

如果配置正确，会提示邮件发送成功（需要有 NotebookLM 研究数据）。

## 环境变量说明

| 变量名 | 说明 | 是否必需 | 示例 |
|--------|------|---------|------|
| `EMAIL_SENDER` | 发件人邮箱地址 | ✅ 必需 | `qiaoshi.zheng@foxmail.com` |
| `EMAIL_RECIPIENTS` | 收件人列表（逗号分隔） | ✅ 必需 | `zhengqiaoshi@huawei.com` |
| `EMAIL_USERNAME` | SMTP 登录用户名 | ✅ 必需 | `qiaoshi.zheng@foxmail.com` |
| `EMAIL_PASSWORD` | SMTP 授权码 | ✅ 必需 | `xyz123abc456` |
| `EMAIL_SMTP_SERVER` | SMTP 服务器 | ❌ 默认 `smtp.qq.com` | `smtp.qq.com` |
| `EMAIL_SMTP_PORT` | SMTP 端口 | ❌ 默认 `587` | `587` 或 `465` |
| `EMAIL_USE_SSL` | 是否使用 SSL | ❌ 默认 `true` | `true` 或 `false` |

## 安全最佳实践

### ✅ 推荐做法

1. **使用 `.env.local` 文件**：已添加到 `.gitignore`，不会意外提交
2. **限制文件权限**：
   ```bash
   chmod 600 .env.local
   ```
3. **定期更换授权码**：在 QQ 邮箱设置中重新生成
4. **使用 foxmail 别名**：隐藏 QQ 号码

### ❌ 避免的做法

1. **不要将 `.env.local` 提交到 Git**（已自动忽略）
2. **不要在代码中硬编码邮箱地址**（已移至环境变量）
3. **不要在公开场合分享授权码**
4. **不要使用 QQ 登录密码**（必须使用授权码）

## 故障排查

### Q: 提示 "EMAIL_PASSWORD not set"

**原因**：环境变量未加载

**解决**：
```bash
source .env.local
echo $EMAIL_PASSWORD  # 验证是否设置
```

### Q: 提示 "Authentication failed"

**原因**：授权码错误或已过期

**解决**：
1. 登录 QQ 邮箱重新生成授权码
2. 更新 `.env.local` 中的 `EMAIL_PASSWORD`
3. 重新加载：`source .env.local`

### Q: 提示 "Connection timeout"

**原因**：SMTP 服务器连接超时

**解决**：
1. 检查网络连接
2. 确认 SMTP 服务器地址正确
3. 尝试切换端口（587 ↔ 465）
4. 检查防火墙设置

### Q: 邮件发送成功但没有收到

**解决**：
1. 检查垃圾邮件文件夹
2. 确认收件人地址正确
3. 检查 QQ 邮箱是否开启了发送限制

## 多收件人配置

如果需要发送多个收件人，用逗号分隔：

```bash
export EMAIL_RECIPIENTS="user1@company.com,user2@example.com,user3@org.com"
```

## 使用其他邮箱服务商

虽然本指南以 QQ 邮箱为例，但你可以修改配置使用其他邮箱：

```bash
# Gmail
export EMAIL_SMTP_SERVER="smtp.gmail.com"
export EMAIL_SMTP_PORT="587"
export EMAIL_SENDER="your-email@gmail.com"

# 163 邮箱
export EMAIL_SMTP_SERVER="smtp.163.com"
export EMAIL_SMTP_PORT="587"
export EMAIL_SENDER="your-email@163.com"

# 公司邮箱
export EMAIL_SMTP_SERVER="smtp.yourcompany.com"
export EMAIL_SMTP_PORT="587"
export EMAIL_SENDER="your-email@yourcompany.com"
```

## 相关文件

- `.env.example` - 环境变量模板
- `.env.local` - 你的个人配置（不要提交到 Git）
- `.gitignore` - Git 忽略规则
- `notebooklm-workflow/scripts/send_email.py` - 邮件发送脚本

---

*最后更新：2026-04-18*
