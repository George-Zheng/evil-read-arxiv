#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Obsidian 导出脚本
生成 Markdown 笔记并保存到 Obsidian Vault
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


def get_vault_path(cli_vault: Optional[str] = None) -> Path:
    """从 CLI 参数或环境变量获取 vault 路径"""
    if cli_vault:
        return Path(cli_vault)

    import os
    env_path = os.environ.get('OBSIDIAN_VAULT_PATH')
    if env_path:
        return Path(env_path)

    # 默认路径
    default_vault = Path.home() / "Documents" / "Obsidian Vault"
    if default_vault.exists():
        return default_vault

    raise ValueError(
        "未指定 Obsidian Vault 路径。\n"
        "请设置 OBSIDIAN_VAULT_PATH 环境变量或通过 --vault 参数指定。"
    )


def generate_note_content(
    topic: str,
    research_result: Dict[str, Any],
    artifacts: Optional[Dict[str, Any]] = None,
    language: str = "zh"
) -> str:
    """
    生成 Obsidian 笔记内容

    Args:
        topic: 研究主题
        research_result: 研究结果
        artifacts: Artifact 结果
        language: 语言 (zh/en)

    Returns:
        Markdown 内容
    """
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")

    notebook_id = research_result.get("notebook_id", "")
    notebook_title = research_result.get("notebook_title", "")
    sources = research_result.get("all_sources", [])
    report = research_result.get("report", "")

    # 生成 frontmatter
    tags = ["notebooklm", "research", topic.replace(" ", "-").lower()]
    tags_yaml = "\n".join(f"  - {tag}" for tag in tags)

    frontmatter = f'''---
created: "{date_str}"
source: NotebookLM
topic: "{topic}"
notebook_id: "{notebook_id}"
notebook_title: "{notebook_title}"
tags:
{tags_yaml}
---

'''

    # 生成正文
    if language == "zh":
        body = _generate_chinese_body(
            topic, research_result, artifacts, report
        )
    else:
        body = _generate_english_body(
            topic, research_result, artifacts, report
        )

    return frontmatter + body


def _generate_chinese_body(
    topic: str,
    research_result: Dict[str, Any],
    artifacts: Optional[Dict[str, Any]],
    report: str
) -> str:
    """生成中文正文"""
    lines = []

    # 标题
    lines.append(f"# 研究报告：{topic}\n")

    # 基本信息
    lines.append("## 基本信息\n")
    lines.append(f"- **研究主题**: {topic}")
    lines.append(f"- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"- **Notebook ID**: `{research_result.get('notebook_id', 'N/A')}`")
    lines.append(f"- **研究模式**: {research_result.get('mode', 'deep')}\n")

    # 来源文献
    lines.append("## 来源文献\n")
    sources = research_result.get("all_sources", [])
    if sources:
        lines.append("| 标题 | 类型 | 链接 |")
        lines.append("|------|------|------|")
        for src in sources[:20]:  # 限制显示数量
            title = src.get("title", "Untitled")[:50]
            src_type = src.get("type", "Unknown")
            url = src.get("url", "")
            if url:
                lines.append(f"| {title} | {src_type} | [链接]({url}) |")
    else:
        lines.append("*暂无来源*\n")

    lines.append("")

    # 研究报告
    if report:
        lines.append("## 研究报告\n")
        lines.append(report)
        lines.append("")

    # 生成的内容
    if artifacts:
        lines.append("## 生成的内容\n")
        artifacts_data = artifacts.get("artifacts", {})

        if "slide_deck" in artifacts_data:
            status = "✓" if artifacts_data["slide_deck"].get("completed") else "○"
            lines.append(f"- {status} Slide Deck: `./exports/slide_deck.pdf`")

        if "audio" in artifacts_data:
            status = "✓" if artifacts_data["audio"].get("completed") else "○"
            lines.append(f"- {status} Audio Overview: `./exports/audio.mp3`")

        if "report" in artifacts_data:
            status = "✓" if artifacts_data["report"].get("completed") else "○"
            lines.append(f"- {status} Report: `./exports/report.md`")

        lines.append("")

    # 关键发现（如果有）
    lines.append("## 关键发现\n")
    lines.append("*[在此处添加从 NotebookLM 对话中提取的关键发现]*\n")

    # 后续行动
    lines.append("## 后续行动\n")
    lines.append("1. [ ] 审阅生成的 Slide Deck")
    lines.append("2. [ ] 收听 Audio Overview")
    lines.append("3. [ ] 整理关键发现到相关笔记")
    lines.append("4. [ ] 更新知识图谱\n")

    # 脚注
    lines.append("---")
    lines.append(f"*由 notebooklm-workflow 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    return "\n".join(lines)


def generate_comparison_note_content(
    topic: str,
    comparison_result: Dict[str, Any],
    language: str = "zh"
) -> str:
    """
    生成比较报告的 Obsidian 笔记内容

    Args:
        topic: 研究主题
        comparison_result: 比较结果
        language: 语言 (zh/en)

    Returns:
        Markdown 内容
    """
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")

    # 生成 frontmatter
    tags = ["notebooklm", "research", "comparison", topic.replace(" ", "-").lower()]
    tags_yaml = "\n".join(f"  - {tag}" for tag in tags)

    frontmatter = f'''---
created: "{date_str}"
source: NotebookLM
topic: "{topic}"
type: report-comparison
tags:
{tags_yaml}
---

'''

    # 生成正文
    if language == "zh":
        body = _generate_comparison_chinese_body(topic, comparison_result)
    else:
        body = _generate_comparison_english_body(topic, comparison_result)

    return frontmatter + body


def _generate_comparison_chinese_body(
    topic: str,
    comparison_result: Dict[str, Any]
) -> str:
    """生成中文比较报告正文"""
    lines = []

    # 标题
    lines.append(f"# 报告比较：{topic}\n")
    lines.append(f"*生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

    # 比较摘要
    if not comparison_result.get("has_comparison"):
        lines.append("> ⚠️ 没有找到上一次的报告，无法进行比较")
        return "\n".join(lines)

    lines.append("## 📊 比较摘要\n")

    comparison_data = comparison_result.get("comparison", {})
    summary = comparison_result.get("summary", "")

    lines.append(summary)
    lines.append("")

    # 计算变化比例
    total_new = comparison_data.get("total_new", 0)
    new_count = len(comparison_data.get("new", []))
    modified_count = len(comparison_data.get("modified", []))

    if total_new > 0:
        change_ratio = (new_count + modified_count) / total_new * 100
        lines.append(f"**内容变化比例：{change_ratio:.1f}%**\n")

    # 详细内容
    if comparison_data.get("duplicate"):
        lines.append("## 📋 重复内容")
        lines.append("")
        lines.append(f"共 {len(comparison_data['duplicate'])} 段内容与上一次报告基本相同：")
        lines.append("")
        for i, item in enumerate(comparison_data["duplicate"], 1):
            lines.append(f"{i}. {item['content']}")
            lines.append(f"   *相似度：{item['similarity']:.0%}*")
            lines.append("")

    if comparison_data.get("modified"):
        lines.append("## ✏️ 修改内容")
        lines.append("")
        lines.append(f"共 {len(comparison_data['modified'])} 段内容相比上一次有修改：")
        lines.append("")
        for i, item in enumerate(comparison_data["modified"], 1):
            lines.append(f"{i}. **相似度 {item['similarity']:.0%}**")
            lines.append(f"   - 新：{item['new_content']}")
            lines.append(f"   - 旧：{item['old_content']}")
            lines.append("")

    if comparison_data.get("new"):
        lines.append("## ➕ 新增内容")
        lines.append("")
        lines.append(f"共 {len(comparison_data['new'])} 段新增内容：")
        lines.append("")
        for i, item in enumerate(comparison_data["new"], 1):
            lines.append(f"{i}. {item['content']}")
            lines.append("")

    if comparison_data.get("deleted"):
        lines.append("## ➖ 删除内容")
        lines.append("")
        lines.append(f"共 {len(comparison_data['deleted'])} 段内容在上一次报告中存在，本次已删除：")
        lines.append("")
        for i, item in enumerate(comparison_data["deleted"], 1):
            lines.append(f"{i}. {item['content']}")
            lines.append("")

    # 脚注
    lines.append("---")
    lines.append(f"*此比较报告由 notebooklm-workflow 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    return "\n".join(lines)


def _generate_comparison_english_body(
    topic: str,
    comparison_result: Dict[str, Any]
) -> str:
    """生成英文比较报告正文"""
    lines = []

    lines.append(f"# Report Comparison: {topic}\n")
    lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

    if not comparison_result.get("has_comparison"):
        lines.append("> ⚠️ No previous report found for comparison")
        return "\n".join(lines)

    lines.append("## 📊 Comparison Summary\n")

    comparison_data = comparison_result.get("comparison", {})
    summary = comparison_result.get("summary", "")

    lines.append(summary)
    lines.append("")

    total_new = comparison_data.get("total_new", 0)
    new_count = len(comparison_data.get("new", []))
    modified_count = len(comparison_data.get("modified", []))

    if total_new > 0:
        change_ratio = (new_count + modified_count) / total_new * 100
        lines.append(f"**Change Ratio: {change_ratio:.1f}%**\n")

    if comparison_data.get("duplicate"):
        lines.append("## 📋 Duplicate Content")
        lines.append("")
        lines.append(f"Total {len(comparison_data['duplicate'])} paragraphs are similar to previous report:")
        lines.append("")
        for i, item in enumerate(comparison_data["duplicate"], 1):
            lines.append(f"{i}. {item['content']}")
            lines.append(f"   *Similarity: {item['similarity']:.0%}*")
            lines.append("")

    if comparison_data.get("modified"):
        lines.append("## ✏️ Modified Content")
        lines.append("")
        lines.append(f"Total {len(comparison_data['modified'])} paragraphs have been modified:")
        lines.append("")
        for i, item in enumerate(comparison_data["modified"], 1):
            lines.append(f"{i}. **Similarity {item['similarity']:.0%}**")
            lines.append(f"   - New: {item['new_content']}")
            lines.append(f"   - Old: {item['old_content']}")
            lines.append("")

    if comparison_data.get("new"):
        lines.append("## ➕ New Content")
        lines.append("")
        lines.append(f"Total {len(comparison_data['new'])} new paragraphs:")
        lines.append("")
        for i, item in enumerate(comparison_data["new"], 1):
            lines.append(f"{i}. {item['content']}")
            lines.append("")

    if comparison_data.get("deleted"):
        lines.append("## ➖ Deleted Content")
        lines.append("")
        lines.append(f"Total {len(comparison_data['deleted'])} paragraphs were removed:")
        lines.append("")
        for i, item in enumerate(comparison_data["deleted"], 1):
            lines.append(f"{i}. {item['content']}")
            lines.append("")

    lines.append("---")
    lines.append(f"*Automatically generated by notebooklm-workflow at {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    return "\n".join(lines)


def _generate_english_body(
    topic: str,
    research_result: Dict[str, Any],
    artifacts: Optional[Dict[str, Any]],
    report: str
) -> str:
    """生成英文正文"""
    lines = []

    lines.append(f"# Research Report: {topic}\n")

    lines.append("## Basic Information\n")
    lines.append(f"- **Topic**: {topic}")
    lines.append(f"- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"- **Notebook ID**: `{research_result.get('notebook_id', 'N/A')}`")
    lines.append(f"- **Mode**: {research_result.get('mode', 'deep')}\n")

    lines.append("## Sources\n")
    sources = research_result.get("all_sources", [])
    if sources:
        lines.append("| Title | Type | Link |")
        lines.append("|-------|------|------|")
        for src in sources[:20]:
            title = src.get("title", "Untitled")[:50]
            src_type = src.get("type", "Unknown")
            url = src.get("url", "")
            if url:
                lines.append(f"| {title} | {src_type} | [Link]({url}) |")
    else:
        lines.append("*No sources*\n")

    lines.append("")

    if report:
        lines.append("## Research Report\n")
        lines.append(report)
        lines.append("")

    if artifacts:
        lines.append("## Generated Artifacts\n")
        artifacts_data = artifacts.get("artifacts", {})

        if "slide_deck" in artifacts_data:
            status = "✓" if artifacts_data["slide_deck"].get("completed") else "○"
            lines.append(f"- {status} Slide Deck: `./exports/slide_deck.pdf`")

        if "audio" in artifacts_data:
            status = "✓" if artifacts_data["audio"].get("completed") else "○"
            lines.append(f"- {status} Audio Overview: `./exports/audio.mp3`")

        if "report" in artifacts_data:
            status = "✓" if artifacts_data["report"].get("completed") else "○"
            lines.append(f"- {status} Report: `./exports/report.md`")

        lines.append("")

    lines.append("## Key Findings\n")
    lines.append("*[Add key findings extracted from NotebookLM chat]*\n")

    lines.append("## Next Steps\n")
    lines.append("1. [ ] Review generated Slide Deck")
    lines.append("2. [ ] Listen to Audio Overview")
    lines.append("3. [ ] Extract key findings to related notes")
    lines.append("4. [ ] Update knowledge graph\n")

    lines.append("---")
    lines.append(f"*Automatically generated by notebooklm-workflow at {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    return "\n".join(lines)


def export_to_obsidian(
    content: str,
    vault_path: Path,
    topic: str,
    folder: str = "NotebookLM/Exports"
) -> Path:
    """
    导出内容到 Obsidian

    Args:
        content: Markdown 内容
        vault_path: Vault 路径
        topic: 研究主题
        folder: 目标文件夹

    Returns:
        保存的文件路径
    """
    # 创建目标目录
    output_dir = vault_path / folder
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成文件名（使用 topic 和日期）
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_topic = topic.replace(" ", "_").replace("/", "_")[:50]
    filename = f"{date_str}_{safe_topic}.md"

    output_path = output_dir / filename

    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    logger.info(f"Exported to: {output_path}")
    return output_path


def create_exports_folder(vault_path: Path, folder: str = "NotebookLM/Exports") -> Path:
    """创建导出文件夹（用于保存 PDF/音频等）"""
    exports_dir = vault_path / folder
    exports_dir.mkdir(parents=True, exist_ok=True)
    return exports_dir


async def main():
    """测试导出功能"""
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python export_to_obsidian.py <research_result_json> [topic]")
        sys.exit(1)

    # 从 JSON 文件加载研究结果
    with open(sys.argv[1], 'r') as f:
        research_result = json.load(f)

    topic = sys.argv[2] if len(sys.argv) > 2 else "Research"

    # 生成内容
    content = generate_note_content(topic, research_result, language="zh")

    # 获取 vault 路径
    vault = get_vault_path()
    print(f"Using vault: {vault}")

    # 导出
    output_path = export_to_obsidian(content, vault, topic)
    print(f"Exported to: {output_path}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
