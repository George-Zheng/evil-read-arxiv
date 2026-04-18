# 定时任务配置说明

本文档说明如何设置 3 个研究方向的定时任务。

## 研究方向和定时任务

| 方向 | 研究主题 | 任务类型 | 频率 | 执行时间 |
|------|----------|----------|------|----------|
| **A** | 自动驾驶芯片设计 | NotebookLM 深度研究 | 每周 | 周六 22:00 |
| **B** | 自动驾驶算法演进 | 顶会论文搜索 | 每周 | 周日 16:00 |
| **C** | 高性价比推理芯片 | NotebookLM 深度研究 | 每周 | 周日 13:00 |

## 配置方式

### 方式 1：使用 cron（推荐 macOS/Linux）

编辑 crontab：

```bash
crontab -e
```

添加以下任务：

```cron
# 每周六 22:00 - 方向 A：自动驾驶芯片设计 NotebookLM 研究
0 22 * * 6 cd /Users/zhengqiaoshi/workspace/notebooklm_obsidian && /opt/homebrew/bin/notebooklm status >/dev/null 2>&1 && source .env.local && python3 notebooklm-workflow/scripts/workflow_main.py "autonomous driving chip design" --compare --send-email

# 每周日 13:00 - 方向 C：高性价比推理芯片 NotebookLM 研究
0 13 * * 0 cd /Users/zhengqiaoshi/workspace/notebooklm_obsidian && /opt/homebrew/bin/notebooklm status >/dev/null 2>&1 && source .env.local && python3 notebooklm-workflow/scripts/workflow_main.py "cost effective inference chip" --compare --send-email

# 每周日 16:00 - 方向 B：自动驾驶算法顶会论文搜索
0 16 * * 0 cd /Users/zhengqiaoshi/workspace/notebooklm_obsidian/conf-papers && python3 scripts/search_conf_papers.py --config conf-papers-ad-algo.yaml --output conf_papers_ad_filtered.json && cd .. && python3 start-my-day/scripts/generate_conf_recommendation.py
```

### 方式 2：使用 macOS Shortcuts（快捷指令）

1. 打开「快捷指令」App
2. 创建新的快捷指令
3. 添加「运行 Shell 脚本」动作
4. 粘贴上述命令
5. 设置自动化触发时间

### 方式 3：使用 Python 定时任务

使用 `cron-schedule` 或 `schedule` 库：

```python
# scripts/schedule_tasks.py
import schedule
import subprocess
from pathlib import Path

BASE_DIR = Path("/Users/zhengqiaoshi/workspace/notebooklm_obsidian")

def run_ad_chip_research():
    """方向 A：自动驾驶芯片研究"""
    subprocess.run([
        "python3", "notebooklm-workflow/scripts/workflow_main.py",
        "autonomous driving chip design",
        "--compare", "--send-email"
    ], cwd=BASE_DIR)

def run_ad_algo_search():
    """方向 B：自动驾驶算法顶会搜索"""
    subprocess.run([
        "python3", "conf-papers/scripts/search_conf_papers.py",
        "--config", "conf-papers/conf-papers-ad-algo.yaml",
        "--output", "conf_papers_ad_filtered.json"
    ], cwd=BASE_DIR)

def run_inference_chip_research():
    """方向 C：高性价比推理芯片研究"""
    subprocess.run([
        "python3", "notebooklm-workflow/scripts/workflow_main.py",
        "cost effective inference chip",
        "--compare", "--send-email"
    ], cwd=BASE_DIR)

# 设置定时任务
schedule.every().monday.at("09:00").do(run_ad_chip_research)
schedule.every().tuesday.at("09:00").do(run_ad_algo_search)
schedule.every().wednesday.at("09:00").do(run_inference_chip_research)

# 运行
if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(60)
```

### 方式 4：使用 Claude Code 内置定时任务

使用 `/schedule` 命令（如果支持）或 cron 集成功能。

## 手动执行命令

### 方向 A：自动驾驶芯片设计

```bash
cd /Users/zhengqiaoshi/workspace/notebooklm_obsidian
source .env.local
export OBSIDIAN_VAULT_PATH="/Users/zhengqiaoshi/Documents/Obsidian Vault"

# 执行 NotebookLM 深度研究
python3 notebooklm-workflow/scripts/workflow_main.py \
  "autonomous driving chip design performance energy efficiency reliability" \
  --compare \
  --send-email
```

### 方向 B：自动驾驶算法演进

```bash
cd /Users/zhengqiaoshi/workspace/notebooklm_obsidian/conf-papers

# 执行顶会论文搜索
python3 scripts/search_conf_papers.py \
  --config conf-papers-ad-algo.yaml \
  --output conf_papers_ad_filtered.json \
  --year 2025

# 生成推荐笔记
cd ..
python3 start-my-day/scripts/generate_conf_recommendation.py \
  --input conf-papers/conf_papers_ad_filtered.json \
  --output "10_Daily/$(date +%Y)_自动驾驶算法顶会推荐.md"
```

### 方向 C：高性价比推理芯片

```bash
cd /Users/zhengqiaoshi/workspace/notebooklm_obsidian
source .env.local
export OBSIDIAN_VAULT_PATH="/Users/zhengqiaoshi/Documents/Obsidian Vault"

# 执行 NotebookLM 深度研究
python3 notebooklm-workflow/scripts/workflow_main.py \
  "cost effective inference chip design low precision compression bandwidth hardware operator" \
  --compare \
  --send-email
```

## 环境变量要求

确保以下环境变量已设置：

```bash
# Obsidian Vault 路径
export OBSIDIAN_VAULT_PATH="/Users/zhengqiaoshi/Documents/Obsidian Vault"

# 邮件配置（如需发送邮件）
source /Users/zhengqiaoshi/workspace/notebooklm_obsidian/.env.local
# 包含：EMAIL_SENDER, EMAIL_RECIPIENTS, EMAIL_USERNAME, EMAIL_PASSWORD
```

## 输出位置

### NotebookLM 报告
- 完整报告：`{Vault}/NotebookLM/Exports/{日期}_{主题}.md`
- 比较报告：`{Vault}/NotebookLM/Exports/Comparisons/{日期}_{主题}_comparison.md`

### 顶会论文推荐
- 推荐笔记：`{Vault}/10_Daily/{年份}_自动驾驶算法顶会推荐.md`

## 邮件通知

如需开启邮件通知：
1. 确保 `.env.local` 中配置了 `EMAIL_PASSWORD`
2. 在命令中添加 `--send-email` 参数
3. 每次执行后会发送两封邮件：
   - 完整报告邮件
   - 比较报告邮件（仅当有上一次报告时）

## 故障排查

### NotebookLM 未登录
```bash
notebooklm login
```

### 环境变量未加载
```bash
source .env.local
```

### 配置文件不存在
检查配置文件路径：
- `notebooklm-workflow/scripts/research_topics.yaml`
- `conf-papers/conf-papers-ad-algo.yaml`

---

*最后更新：2026-04-18*
