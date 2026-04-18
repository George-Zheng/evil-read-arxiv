#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试工作流的 Obsidian 导出和邮件生成功能
"""

import sys
from pathlib import Path

# 添加脚本路径
sys.path.insert(0, str(Path(__file__).parent))

from export_to_obsidian import (
    generate_note_content,
    generate_comparison_note_content,
    export_to_obsidian,
    get_vault_path
)
from report_comparator import ReportComparator
from send_email import generate_email_html, generate_comparison_email_html


def test_obsidian_export():
    """测试 Obsidian 导出功能"""
    print("=" * 60)
    print("测试 1: Obsidian 报告导出")
    print("=" * 60)

    # 模拟研究结果
    research_result = {
        'notebook_id': 'test-123',
        'notebook_title': 'Research 测试主题',
        'mode': 'deep',
        'sources_found': 5,
        'sources_imported': 3,
        'all_sources': [
            {'title': 'Attention Is All You Need', 'type': 'arXiv', 'url': 'https://arxiv.org/1706.03762', 'id': '1'},
            {'title': 'BERT: Pre-training of Deep Bidirectional Transformers', 'type': 'arXiv', 'url': 'https://arxiv.org/1904.09237', 'id': '2'},
        ],
        'report': '''
这是研究报告的摘要部分。

## 研究背景

Transformer 架构自 2017 年提出以来，已经成为自然语言处理领域的主流架构。

## 研究方法

我们采用了基于 Transformer 的编码器 - 解码器架构进行实验。

## 实验结果

在多个基准数据集上取得了 state-of-the-art 的结果。

## 结论

本研究为后续工作奠定了基础。
'''
    }

    artifacts = {
        'artifacts': {
            'slide_deck': {'completed': True},
            'audio': {'completed': True},
            'report': {'content': research_result['report'], 'completed': True}
        }
    }

    # 生成完整报告
    content = generate_note_content('测试主题', research_result, artifacts, language='zh')

    # 获取 vault 路径
    try:
        vault_path = get_vault_path()
        print(f"Vault 路径：{vault_path}")

        # 导出完整报告
        output_path = export_to_obsidian(content, vault_path, '测试主题', 'NotebookLM/Exports')
        print(f"✓ 完整报告已导出：{output_path}")

    except Exception as e:
        print(f"⚠ 导出测试（需要 Obsidian Vault）: {e}")
        # 即使无法导出，也打印生成的内容
        print("\n生成的内容预览:")
        print(content[:500])

    return research_result, artifacts


def test_comparison(research_result, artifacts):
    """测试报告比较功能"""
    print("\n" + "=" * 60)
    print("测试 2: 报告比较")
    print("=" * 60)

    # 创建比较器
    comparator = ReportComparator()

    # 模拟上一次报告
    old_report = '''
这是研究报告的摘要部分。

## 研究背景

Transformer 架构自 2017 年提出以来，已经成为自然语言处理领域的主流架构。

## 旧的研究方法

我们采用了传统的 RNN 架构进行实验。

## 旧结论

初步实验结果尚可。
'''

    # 获取新报告内容
    new_report = artifacts['artifacts']['report']['content']

    # 执行比较
    comparison = comparator.compare_reports(new_report, old_report)

    print("\n比较结果:")
    print(f"- 新增：{len(comparison['comparison']['new'])} 段")
    print(f"- 修改：{len(comparison['comparison']['modified'])} 段")
    print(f"- 重复：{len(comparison['comparison']['duplicate'])} 段")
    print(f"- 删除：{len(comparison['comparison']['deleted'])} 段")

    print("\n比较摘要:")
    print(comparison.get('summary', ''))

    # 生成比较报告
    comparison_content = generate_comparison_note_content('测试主题', comparison, language='zh')

    # 导出比较报告
    try:
        vault_path = get_vault_path()
        comparison_path = export_to_obsidian(
            comparison_content, vault_path, '测试主题_comparison', 'NotebookLM/Exports/Comparisons'
        )
        print(f"\n✓ 比较报告已导出：{comparison_path}")
    except Exception as e:
        print(f"\n⚠ 比较报告导出测试（需要 Obsidian Vault）: {e}")
        print("\n生成的比较报告预览:")
        print(comparison_content[:500])

    return comparison


def test_email_generation(research_result, artifacts, comparison):
    """测试邮件生成"""
    print("\n" + "=" * 60)
    print("测试 3: 邮件生成")
    print("=" * 60)

    # 生成完整报告邮件
    full_email = generate_email_html(
        '测试主题',
        research_result,
        artifacts,
        include_summary=True,
        include_paper_list=True,
        include_artifacts=True
    )

    print(f"\n✓ 完整报告邮件已生成")
    print(f"  邮件大小：{len(full_email)} 字节")

    # 生成比较报告邮件
    comparison_email = generate_comparison_email_html(
        '测试主题',
        comparison,
        research_result
    )

    print(f"✓ 比较报告邮件已生成")
    print(f"  邮件大小：{len(comparison_email)} 字节")

    # 预览邮件主题
    print("\n邮件主题预览:")
    print(f"  完整报告：[NotebookLM 研究报告] 测试主题 - 2026-04-18")
    print(f"  比较报告：[NotebookLM 报告比较] 测试主题 - 2026-04-18")


def main():
    """运行所有测试"""
    print("\n" + "🧪 " * 20)
    print("NotebookLM Workflow 测试")
    print("🧪 " * 20 + "\n")

    # 测试 1: Obsidian 导出
    research_result, artifacts = test_obsidian_export()

    # 测试 2: 报告比较
    comparison = test_comparison(research_result, artifacts)

    # 测试 3: 邮件生成
    test_email_generation(research_result, artifacts, comparison)

    print("\n" + "=" * 60)
    print("✅ 所有测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
