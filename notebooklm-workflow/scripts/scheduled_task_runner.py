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
BASE_DIR = Path(__file__).parent.parent.parent  # repo 根目录
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

    # 检查 NotebookLM 是否已登录
    print("\n检查 NotebookLM 登录状态...")
    try:
        from notebooklm.auth import load_auth_from_storage
        from pathlib import Path
        # 尝试从浏览器 profile 加载认证
        browser_profile = Path.home() / ".notebooklm" / "profiles" / "default" / "browser_profile"
        if browser_profile.exists():
            print(f"发现浏览器配置文件：{browser_profile}")
            # 尝试使用浏览器配置文件创建 storage_state.json
            storage_path = Path.home() / ".notebooklm" / "storage_state.json"
            if not storage_path.exists():
                print("创建 storage_state.json...")
                # 复制浏览器配置的认证信息
                import shutil
                # 查找 Local Storage 中的认证信息
                local_storage = browser_profile / "Default" / "Local Storage" / "leveldb"
                if local_storage.exists():
                    print(f"找到 Local Storage: {local_storage}")
                    # 尝试从浏览器 profile 提取认证
                    print("提示：请使用 'notebooklm login' 命令进行登录")
                    print("或者手动创建 ~/.notebooklm/storage_state.json 文件")
        else:
            print("未找到浏览器配置文件")
    except Exception as e:
        print(f"检查失败：{e}")

    cmd = [
        "python3", "workflow_main.py",
        topic,
        "--compare",
        "--send-email",
        "--dry-run"  # 暂时使用 dry-run 模式
    ]

    success = run_command(cmd, cwd=WORKFLOW_DIR)

    if success:
        print("\n✓ 方向 A 任务完成（Dry Run 模式）")
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

    # 使用 2025 年（2026 年还没有会议论文）
    from datetime import datetime
    current_year = datetime.now().year
    search_year = current_year - 1  # 搜索上一年

    print(f"搜索年份：{search_year}（{current_year}年的会议论文还未发布）")

    cmd_search = [
        "python3", "scripts/search_conf_papers.py",
        "--config", "conf-papers-ad-algo.yaml",
        "--output", str(output_json),
        "--year", str(search_year),
        "--top-n", "10"
    ]

    success_search = run_command(cmd_search, cwd=CONF_PAPERS_DIR)

    if not success_search:
        print("\n✗ 顶会论文搜索失败", file=sys.stderr)
        return False

    # 步骤 2: 读取结果并显示
    print("\n步骤 2: 读取搜索结果...")
    try:
        import json
        with open(output_json, 'r') as f:
            result = json.load(f)

        print(f"\n搜索完成:")
        print(f"  - 搜索的会议：{', '.join(result.get('conferences_searched', []))}")
        print(f"  - 找到论文总数：{result.get('total_found', 0)}")
        print(f"  - 筛选后论文数：{len(result.get('top_papers', []))}")

        if result.get('top_papers'):
            print(f"\n推荐的论文:")
            for i, paper in enumerate(result['top_papers'][:5], 1):
                print(f"  {i}. {paper.get('title', 'Untitled')[:60]}...")
    except Exception as e:
        print(f"读取结果失败：{e}")

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
        "--send-email",
        "--dry-run"  # 暂时使用 dry-run 模式
    ]

    success = run_command(cmd, cwd=WORKFLOW_DIR)

    if success:
        print("\n✓ 方向 C 任务完成（Dry Run 模式）")
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
