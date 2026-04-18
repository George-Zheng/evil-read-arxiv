# NotebookLM 认证设置指南

本指南说明如何设置 NotebookLM 认证，以便执行定时任务。

## 问题说明

NotebookLM 使用 Google 认证，需要有效的 cookies 才能访问 API。认证信息存储在 `~/.notebooklm/storage_state.json` 文件中。

## 方法 1：使用 notebooklm login 命令（推荐）

这是最简单的方法，但需要安装 Playwright。

### 步骤

1. **安装 notebooklm-py 和 Playwright**

   ```bash
   pip install notebooklm[browser]
   playwright install chromium
   ```

2. **运行登录命令**

   ```bash
   notebooklm login
   ```

3. **在浏览器中登录**

   - 会自动打开一个浏览器窗口
   - 使用你的 Google 账号登录 NotebookLM
   - 等待进入 NotebookLM 主页

4. **保存认证**

   - 回到终端
   - 按 Enter 键保存认证信息
   - 认证将保存到 `~/.notebooklm/storage_state.json`

### 验证

```bash
notebooklm status
notebooklm list
```

如果看到你的 Notebook 列表，说明认证成功。

## 方法 2：手动创建 storage_state.json

如果无法安装 Playwright，可以手动创建认证文件。

### 步骤

1. **打开 Chrome 浏览器访问 NotebookLM**

   访问 https://notebooklm.google.com 并登录

2. **打开开发者工具**

   - macOS: `Cmd + Option + I`
   - Windows/Linux: `F12`

3. **查看 Cookies**

   - 进入 `Application` 标签
   - 展开 `Storage` > `Cookies`
   - 选择 `https://notebooklm.google.com`

4. **复制关键 Cookies**

   需要复制以下 cookies 的 `Value`:
   - `SID`
   - `HSID`
   - `SSID`
   - `APISID`
   - `SAPISID`

5. **创建 storage_state.json**

   创建文件 `~/.notebooklm/storage_state.json`，内容格式如下：

   ```json
   {
     "cookies": [
       {
         "name": "SID",
         "value": "你的 SID 值",
         "domain": ".google.com",
         "path": "/",
         "expires": 9999999999,
         "httpOnly": true,
         "secure": true,
         "sameSite": "Lax"
       },
       {
         "name": "HSID",
         "value": "你的 HSID 值",
         "domain": ".google.com",
         "path": "/",
         "expires": 9999999999,
         "httpOnly": true,
         "secure": true,
         "sameSite": "Lax"
       },
       {
         "name": "SSID",
         "value": "你的 SSID 值",
         "domain": ".google.com",
         "path": "/",
         "expires": 9999999999,
         "httpOnly": true,
         "secure": true,
         "sameSite": "Lax"
       },
       {
         "name": "APISID",
         "value": "你的 APISID 值",
         "domain": ".google.com",
         "path": "/",
         "expires": 9999999999,
         "httpOnly": true,
         "secure": true,
         "sameSite": "Lax"
       },
       {
         "name": "SAPISID",
         "value": "你的 SAPISID 值",
         "domain": ".google.com",
         "path": "/",
         "expires": 9999999999,
         "httpOnly": false,
         "secure": true,
         "sameSite": "Lax"
       }
     ]
   }
   ```

6. **设置文件权限**

   ```bash
   chmod 600 ~/.notebooklm/storage_state.json
   ```

### 验证

```bash
python3 -c "from notebooklm.auth import load_auth_from_storage; print(load_auth_from_storage())"
```

如果看到 cookie 字典输出，说明配置正确。

## 方法 3：使用环境变量（适合 CI/CD）

如果不想创建文件，可以使用环境变量。

### 步骤

1. **获取 cookies JSON**

   按照方法 2 的步骤获取 cookies，创建完整的 JSON 对象。

2. **设置环境变量**

   在 `~/.zshrc` 或 `~/.bashrc` 中添加：

   ```bash
   export NOTEBOOKLM_AUTH_JSON='{"cookies":[{"name":"SID","value":"...","domain":".google.com","path":"/","expires":9999999999},...]}'
   ```

3. **加载环境变量**

   ```bash
   source ~/.zshrc
   ```

### 验证

```bash
echo $NOTEBOOKLM_AUTH_JSON  # 应该显示 JSON 内容
```

## 故障排查

### 问题 1: storage_state.json not found

**症状**: `FileNotFoundError: Storage file not found`

**解决**:
- 确认文件路径正确：`~/.notebooklm/storage_state.json`
- 运行 `notebooklm login` 创建文件

### 问题 2: 认证过期

**症状**: API 请求返回 401 或 403 错误

**解决**:
- 重新运行 `notebooklm login`
- 或者手动更新 cookies 值

### 问题 3: Playwright 安装失败

**症状**: `playwright install chromium` 失败

**解决**:
- 尝试方法 2（手动创建）
- 或者使用方法 3（环境变量）

### 问题 4: Cookie 提取失败

**症状**: Chrome 开发者工具中看不到 cookie 值（显示为加密）

**解决**:
- 这是正常行为，Chrome 加密了 cookie 值
- 需要通过其他方式获取 cookies
- 推荐使用方法 1（notebooklm login）

## 定时任务配置

认证成功后，定时任务会自动执行：

```bash
# 查看已配置的定时任务
crontab -l

# 手动执行一次
python3 notebooklm-workflow/scripts/scheduled_task_runner.py --direction all
```

## 相关文件

- `~/.notebooklm/storage_state.json` - 认证文件
- `notebooklm-workflow/scripts/scheduled_task_runner.py` - 定时任务执行器
- `notebooklm-workflow/scripts/workflow_main.py` - 主工作流脚本

## 安全提示

1. **保护认证文件**: `storage_state.json` 包含敏感的认证信息，不要分享给他人
2. **文件权限**: 确保文件权限为 600（只有所有者可读写）
3. **不要提交到 Git**: `.gitignore` 已配置，不要手动添加
4. **定期更新**: Google cookies 可能过期，建议每月更新一次

---

*最后更新：2026-04-18*
