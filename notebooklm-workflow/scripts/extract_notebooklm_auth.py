#!/usr/bin/env python3
"""
NotebookLM 认证设置脚本

使用方法:
    python3 extract_notebooklm_auth.py

这脚本将帮助您设置 NotebookLM 认证
"""

import json
import os
from pathlib import Path
import sys

def main():
    print("NotebookLM 认证设置")
    print("=" * 60)

    # 检查是否已有 storage_state.json
    storage_path = Path.home() / ".notebooklm" / "storage_state.json"
    if storage_path.exists():
        print(f"✓ storage_state.json 已存在：{storage_path}")
        try:
            with open(storage_path) as f:
                data = json.load(f)
                if data.get("cookies"):
                    print(f"✓ 包含 {len(data['cookies'])} 个 cookies")
                    print("\n认证已配置，可以运行定时任务")
                    return 0
        except Exception as e:
            print(f"✗ 文件可能已损坏：{e}")

    print("\nNotebookLM 需要认证才能执行任务")
    print("\n请选择设置方式:")
    print("\n方法 1: 使用 notebooklm login 命令（推荐，需要 Playwright）")
    print("  步骤:")
    print("    1. 安装：pip install notebooklm[browser]")
    print("    2. 安装浏览器：playwright install chromium")
    print("    3. 登录：notebooklm login")
    print("    4. 在打开的浏览器中登录 Google 账号")
    print("    5. 按 Enter 保存认证")

    print("\n方法 2: 手动创建 storage_state.json")
    print("  1. 打开 Chrome 访问 https://notebooklm.google.com")
    print("  2. 登录你的 Google 账号")
    print("  3. 打开开发者工具 (F12 或 Cmd+Option+I)")
    print("  4. 进入 Application > Storage > Cookies > https://notebooklm.google.com")
    print("  5. 复制以下 cookies 的值：SID, HSID, SSID, APISID, SAPISID")
    print("  6. 创建文件 ~/.notebooklm/storage_state.json，内容格式:")
    print('''
{
  "cookies": [
    {"name": "SID", "value": "你的 SID 值", "domain": ".google.com", "path": "/", "expires": 9999999999},
    {"name": "HSID", "value": "你的 HSID 值", "domain": ".google.com", "path": "/", "expires": 9999999999},
    {"name": "SSID", "value": "你的 SSID 值", "domain": ".google.com", "path": "/", "expires": 9999999999},
    {"name": "APISID", "value": "你的 APISID 值", "domain": ".google.com", "path": "/", "expires": 9999999999},
    {"name": "SAPISID", "value": "你的 SAPISID 值", "domain": ".google.com", "path": "/", "expires": 9999999999}
  ]
}
''')

    print("\n方法 3: 使用 NOTEBOOKLM_AUTH_JSON 环境变量")
    print("  将上面的 JSON 内容放入环境变量:")
    print('  export NOTEBOOKLM_AUTH_JSON=\'{"cookies":[...]}\''
