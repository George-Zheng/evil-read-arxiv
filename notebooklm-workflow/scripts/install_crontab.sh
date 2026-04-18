#!/bin/bash
# 安装定时任务脚本
# 将 3 个研究方向的定时任务添加到 crontab

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

echo "=============================================="
echo "安装定时任务"
echo "=============================================="
echo ""
echo "仓库目录：$REPO_DIR"
echo ""

# 创建 cron 脚本内容
CRON_SCRIPT="# NotebookLM Workflow 定时任务
# 3 个研究方向的自动研究任务
# 由 $REPO_DIR/docs/scheduled-tasks-setup.md 生成

# 环境变量设置
SHELL=/bin/zsh
PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin
OBSIDIAN_VAULT_PATH=\"/Users/zhengqiaoshi/Documents/Obsidian Vault\"

# 每周一 9:00 - 方向 A：自动驾驶芯片设计 NotebookLM 研究
0 9 * * 1 cd $REPO_DIR && source .env.local && python3 notebooklm-workflow/scripts/scheduled_task_runner.py --direction A

# 每周二 9:00 - 方向 B：自动驾驶算法演进 顶会论文搜索
0 9 * * 2 cd $REPO_DIR && python3 notebooklm-workflow/scripts/scheduled_task_runner.py --direction B

# 每周三 9:00 - 方向 C：高性价比推理芯片 NotebookLM 研究
0 9 * * 3 cd $REPO_DIR && source .env.local && python3 notebooklm-workflow/scripts/scheduled_task_runner.py --direction C
"

# 备份现有 crontab
if crontab -l 2>/dev/null; then
    echo "备份现有 crontab..."
    crontab -l > "$REPO_DIR/crontab.backup.$(date +%Y%m%d_%H%M%S)"
fi

# 安装新的 crontab
echo "$CRON_SCRIPT" | crontab -

echo ""
echo "=============================================="
echo "✅ 定时任务已安装!"
echo "=============================================="
echo ""
echo "已添加的任务:"
echo "  - 周一 9:00: 自动驾驶芯片设计 (方向 A)"
echo "  - 周二 9:00: 自动驾驶算法演进 (方向 B)"
echo "  - 周三 9:00: 高性价比推理芯片 (方向 C)"
echo ""
echo "查看已安装的任务：crontab -l"
echo "编辑任务：crontab -e"
echo "删除任务：crontab -r"
echo ""
