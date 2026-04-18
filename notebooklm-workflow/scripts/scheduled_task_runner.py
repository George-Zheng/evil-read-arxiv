#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时任务执行器
用于执行 3 个研究方向的定时任务

使用方法:
    python3 scheduled_task_runner.py --direction A  # 自动驾驶芯片
    python3 scheduled_task_runner.py --direction B  # 自动驾驶算法
    python3 scheduled_task_runner.py --direction C  # 推理芯片
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

# 基础目录
BASE_DIR = Path(__file__).parent.parent
WORKFLOW_DIR = BASE_DIR / "notebooklm-workflow" / "scripts"
CONF_PAPERS_DIR = BASE_DIR / "conf-papers"
START_MY_DAY_DIR = BASE_DIR / "start-my-day"


def setup_environment():
    """设置环境变量"""
    # 加载 .env.local
    env_file = BASE_DIR / ".env.local"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if key.startswith('export '):
                        key = key[7:]
                    # 移除引号
                    value = value.strip('"\'')
                    os.environ[key] = value

    # 设置默认 Vault 路径
    if 'OBSIDIAN_VAULT_PATH' not in os.environ:
        os.environ['OBSIDIAN_VAULT_PATH'] = str(Path.home() / "Documents" / "Obsidian Vault")

    print(f"Using Vault: {os.environ['OBSIDIAN_VAULT_PATH']}")


def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    print(f"\n>>> 执行命令：{' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"执行失败：{e}", file=sys.stderr)
        return False


def direction_a_ad_chip():
    """
    方向 A：自动驾驶芯片设计
    NotebookLM 深度研究，每周执行
    """
    print("\n" + "=" * 60)
    print("方向 A：自动驾驶芯片设计 - NotebookLM 深度研究")
    print("=" * 60)

    topic = "autonomous driving chip design performance energy efficiency reliability"

    cmd = [
        "python3", "workflow_main.py",
        topic,
        "--compare",
        "--send-email"
    ]

    success = run_command(cmd, cwd=WORKFLOW_DIR)

    if success:
        print("\n✓ 方向 A 任务完成")
    else:
        print("\n✗ 方向 A 任务失败", file=sys.stderr)

    return success


def direction_b_ad_algo():
    """
    方向 B：自动驾驶算法演进
    顶会论文搜索，每周执行
    """
    print("\n" + "=" * 60)
    print("方向 B：自动驾驶算法演进 - 顶会论文搜索")
    print("=" * 60)

    # 步骤 1: 搜索顶会论文
    print("\n步骤 1: 搜索顶会论文...")
    output_json = CONF_PAPERS_DIR / "conf_papers_ad_filtered.json"

    cmd_search = [
        "python3", "scripts/search_conf_papers.py",
        "--config", "conf-papers-ad-algo.yaml",
        "--output", str(output_json),
        "--year", str(datetime.now().year),
        "--top-n", "10"
    ]

    success_search = run_command(cmd_search, cwd=CONF_PAPERS_DIR)

    if not success_search:
        print("\n✗ 顶会论文搜索失败", file=sys.stderr)
        return False

    # 步骤 2: 生成推荐笔记（需要调用 start-my-day 的脚本或 conf-papers skill）
    print("\n步骤 2: 生成推荐笔记...")
    print("提示：请使用 /conf-papers skill 生成推荐笔记")
    print(f"筛选结果已保存到：{output_json}")

    print("\n✓ 方向 B 任务完成（搜索部分）")
    return True


def direction_c_inference_chip():
    """
    方向 C：高性价比推理芯片
    NotebookLM 深度研究，每周执行
    """
    print("\n" + "=" * 60)
    print("方向 C：高性价比推理芯片 - NotebookLM 深度研究")
    print("=" * 60)

    topic = "cost effective inference chip design low precision quantization compression bandwidth hardware operator accelerator"

    cmd = [
        "python3", "workflow_main.py",
        topic,
        "--compare",
        "--send-email"
    ]

    success = run_command(cmd, cwd=WORKFLOW_DIR)

    if success:
        print("\n✓ 方向 C 任务完成")
    else:
        print("\n✗ 方向 C 任务失败", file=sys.stderr)

    return success


def main():
    parser = argparse.ArgumentParser(
        description="定时任务执行器 - 3 个研究方向"
    )
    parser.add_argument(
        "--direction",
        choices=["A", "B", "C", "all"],
        required=True,
        help="研究方向：A=自动驾驶芯片，B=自动驾驶算法，C=推理芯片，all=全部执行"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只打印计划，不实际执行"
    )

    args = parser.parse_args()

    print("\n" + "🧪 " * 20)
    print("定时任务执行器")
    print("🧪 " * 20)
    print(f"执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 设置环境变量
    setup_environment()

    if args.dry_run:
        print("\n=== Dry Run 模式 ===")
        print(f"Direction: {args.direction}")
        return 0

    success = True

    if args.direction in ["A", "all"]:
        if not direction_a_ad_chip():
            success = False

    if args.direction in ["B", "all"]:
        if not direction_b_ad_algo():
            success = False

    if args.direction in ["C", "all"]:
        if not direction_c_inference_chip():
            success = False

    print("\n" + "=" * 60)
    if success:
        print("✅ 所有任务完成!")
        return 0
    else:
        print("❌ 部分任务失败，请检查日志")
        return 1


if __name__ == "__main__":
    sys.exit(main())
