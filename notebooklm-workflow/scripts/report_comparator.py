#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告比较模块
比较新生成的报告和上一次生成的报告，高亮显示差异和重复部分
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from datetime import datetime
import difflib

logger = logging.getLogger(__name__)


class ReportComparator:
    """报告比较器"""

    def __init__(self, db_path: Optional[Path] = None):
        """
        初始化比较器

        Args:
            db_path: 数据库路径，用于获取上一次报告
        """
        self.db_path = db_path
        self._last_report = None

    def get_last_report(self, topic: str) -> Optional[str]:
        """
        从数据库获取上一次的研究报

        Args:
            topic: 研究主题

        Returns:
            上一次的报告内容，如果没有则返回 None
        """
        if not self.db_path or not self.db_path.exists():
            return None

        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 获取最近一次的执行记录
            cursor.execute("""
                SELECT artifacts FROM execution_logs
                WHERE topic = ?
                ORDER BY started_at DESC
                LIMIT 1
            """, (topic,))

            row = cursor.fetchone()
            conn.close()

            if row and row["artifacts"]:
                import json
                artifacts = json.loads(row["artifacts"])
                # 尝试从 artifacts 中提取 report
                if "report" in artifacts:
                    return artifacts["report"].get("content", "")

            return None

        except Exception as e:
            logger.warning(f"Failed to get last report: {e}")
            return None

    def compare_reports(
        self,
        new_report: str,
        old_report: str,
        similarity_threshold: float = 0.6
    ) -> Dict[str, Any]:
        """
        比较两个报告

        Args:
            new_report: 新生成的报告
            old_report: 上一次的报告
            similarity_threshold: 相似度阈值（大于此值视为重复）

        Returns:
            比较结果
        """
        if not old_report:
            return {
                "has_comparison": False,
                "new_report": new_report,
                "message": "No previous report found"
            }

        # 按段落分割
        new_paragraphs = self._split_into_paragraphs(new_report)
        old_paragraphs = self._split_into_paragraphs(old_report)

        # 比较段落
        comparison_result = self._compare_paragraphs(
            new_paragraphs, old_paragraphs, similarity_threshold
        )

        # 生成差异摘要
        summary = self._generate_summary(comparison_result)

        return {
            "has_comparison": True,
            "new_report": new_report,
            "old_report": old_report,
            "comparison": comparison_result,
            "summary": summary,
            "generated_at": datetime.now().isoformat()
        }

    def _split_into_paragraphs(self, text: str) -> List[str]:
        """将文本分割成段落"""
        # 按空行分割
        paragraphs = text.split("\n\n")
        return [p.strip() for p in paragraphs if p.strip()]

    def _compare_paragraphs(
        self,
        new_paragraphs: List[str],
        old_paragraphs: List[str],
        threshold: float
    ) -> Dict[str, Any]:
        """
        比较段落列表

        Returns:
            比较结果，包含新增、删除、修改、重复的段落
        """
        result = {
            "new": [],      # 新增的段落
            "deleted": [],  # 删除的段落
            "modified": [], # 修改的段落
            "duplicate": [], # 重复/相同的段落
            "total_new": len(new_paragraphs),
            "total_old": len(old_paragraphs),
        }

        # 为每个新段落查找最相似的旧段落
        used_old_indices = set()

        for new_idx, new_para in enumerate(new_paragraphs):
            best_match_idx = -1
            best_similarity = 0.0

            for old_idx, old_para in enumerate(old_paragraphs):
                if old_idx in used_old_indices:
                    continue

                similarity = difflib.SequenceMatcher(
                    None, new_para, old_para
                ).ratio()

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match_idx = old_idx

            # 根据相似度分类
            if best_similarity >= threshold:
                # 视为重复
                result["duplicate"].append({
                    "index": new_idx,
                    "content": new_para[:200] + "..." if len(new_para) > 200 else new_para,
                    "similarity": round(best_similarity, 2)
                })
                used_old_indices.add(best_match_idx)
            elif best_similarity > 0.3:
                # 视为修改
                result["modified"].append({
                    "index": new_idx,
                    "new_content": new_para[:200] + "..." if len(new_para) > 200 else new_para,
                    "old_content": old_paragraphs[best_match_idx][:200] + "..." if best_match_idx >= 0 else "",
                    "similarity": round(best_similarity, 2)
                })
                used_old_indices.add(best_match_idx)
            else:
                # 视为新增
                result["new"].append({
                    "index": new_idx,
                    "content": new_para[:200] + "..." if len(new_para) > 200 else new_para
                })

        # 找出被删除的段落（未匹配的旧段落）
        for old_idx, old_para in enumerate(old_paragraphs):
            if old_idx not in used_old_indices:
                result["deleted"].append({
                    "index": old_idx,
                    "content": old_para[:200] + "..." if len(old_para) > 200 else old_para
                })

        return result

    def _generate_summary(self, comparison: Dict[str, Any]) -> str:
        """生成比较摘要"""
        lines = []

        total_new = comparison.get("total_new", 0)
        total_old = comparison.get("total_old", 0)

        new_count = len(comparison.get("new", []))
        deleted_count = len(comparison.get("deleted", []))
        modified_count = len(comparison.get("modified", []))
        duplicate_count = len(comparison.get("duplicate", []))

        lines.append("## 报告比较摘要")
        lines.append("")
        lines.append(f"- 新报告段落数：{total_new}")
        lines.append(f"- 旧报告段落数：{total_old}")
        lines.append(f"- 新增内容：{new_count} 段")
        lines.append(f"- 删除内容：{deleted_count} 段")
        lines.append(f"- 修改内容：{modified_count} 段")
        lines.append(f"- 重复内容：{duplicate_count} 段")
        lines.append("")

        # 计算变化比例
        if total_new > 0:
            change_ratio = (new_count + modified_count) / total_new * 100
            lines.append(f"- 内容变化比例：{change_ratio:.1f}%")

        # 显示新增内容摘要
        if comparison.get("new"):
            lines.append("")
            lines.append("### 新增内容")
            for i, item in enumerate(comparison["new"][:5], 1):  # 最多显示 5 条
                lines.append(f"{i}. {item['content']}")
            if len(comparison["new"]) > 5:
                lines.append(f"... 还有 {len(comparison['new']) - 5} 条新增")

        # 显示修改内容摘要
        if comparison.get("modified"):
            lines.append("")
            lines.append("### 修改内容")
            for i, item in enumerate(comparison["modified"][:5], 1):  # 最多显示 5 条
                lines.append(f"{i}. 相似度：{item['similarity']:.0%}")
                lines.append(f"   新：{item['new_content']}")
                lines.append(f"   旧：{item['old_content']}")
            if len(comparison["modified"]) > 5:
                lines.append(f"... 还有 {len(comparison['modified']) - 5} 条修改")

        return "\n".join(lines)

    def generate_diff_html(
        self,
        new_report: str,
        old_report: str
    ) -> str:
        """
        生成 HTML 格式的差异对比

        Args:
            new_report: 新报告
            old_report: 旧报告

        Returns:
            HTML 格式的差异对比
        """
        # 按行分割
        new_lines = new_report.splitlines(keepends=True)
        old_lines = old_report.splitlines(keepends=True)

        # 生成差异
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile='Previous Report',
            tofile='Current Report',
            n=3
        )

        # 转换为 HTML
        diff_text = ''.join(diff)

        html = f"""
        <div class="diff-container">
            <style>
                .diff-container {{
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 12px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    overflow: hidden;
                }}
                .diff-header {{
                    background: #f6f8fa;
                    padding: 8px 12px;
                    border-bottom: 1px solid #ddd;
                    font-weight: 600;
                }}
                .diff-content {{
                    max-height: 500px;
                    overflow-y: auto;
                }}
                .diff-line {{
                    padding: 2px 12px;
                    white-space: pre-wrap;
                }}
                .diff-add {{
                    background: #e6ffec;
                    color: #24292e;
                }}
                .diff-remove {{
                    background: #ffebe9;
                    color: #24292e;
                }}
                .diff-context {{
                    background: #fff;
                    color: #666;
                }}
                .diff-highlight {{
                    font-weight: 600;
                }}
            </style>
            <div class="diff-header">📊 报告差异对比</div>
            <div class="diff-content">
                <pre>{self._escape_html(diff_text)}</pre>
            </div>
        </div>
        """
        return html

    def _escape_html(self, text: str) -> str:
        """转义 HTML 特殊字符"""
        return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))

    def generate_comparison_note(
        self,
        comparison: Dict[str, Any],
        output_path: Optional[Path] = None
    ) -> str:
        """
        生成比较笔记（Markdown 格式）

        Args:
            comparison: 比较结果
            output_path: 输出文件路径（可选）

        Returns:
            Markdown 内容
        """
        if not comparison.get("has_comparison"):
            return "*没有找到上一次的报告，跳过比较*\n"

        content = []
        content.append("---")
        content.append("type: report-comparison")
        content.append(f"generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        content.append("---")
        content.append("")
        content.append("# 📊 报告比较")
        content.append("")

        # 摘要
        summary = comparison.get("summary", "")
        content.append(summary)
        content.append("")

        # 详细说明
        comparison_data = comparison.get("comparison", {})

        if comparison_data.get("duplicate"):
            content.append("## 重复内容")
            content.append("")
            content.append("以下内容与上一次报告基本相同：")
            content.append("")
            for item in comparison_data["duplicate"]:
                content.append(f"- {item['content']}")
            content.append("")

        if comparison_data.get("modified"):
            content.append("## 修改内容")
            content.append("")
            content.append("以下内容相比上一次有修改：")
            content.append("")
            for item in comparison_data["modified"]:
                content.append(f"- **相似度 {item['similarity']:.0%}**: {item['new_content']}")
            content.append("")

        if comparison_data.get("new"):
            content.append("## 全新内容")
            content.append("")
            content.append("以下是新增的内容：")
            content.append("")
            for item in comparison_data["new"]:
                content.append(f"- {item['content']}")
            content.append("")

        if comparison_data.get("deleted"):
            content.append("## 删除内容")
            content.append("")
            content.append("以下内容在上一次报告中存在，本次已删除：")
            content.append("")
            for item in comparison_data["deleted"]:
                content.append(f"- {item['content']}")
            content.append("")

        markdown = "\n".join(content)

        # 保存到文件
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            logger.info(f"Comparison note saved to: {output_path}")

        return markdown


async def main():
    """测试比较功能"""
    # 测试数据
    old_report = """
    这是第一段，介绍研究背景。
    这是第二段，描述研究方法。
    这是第三段，展示实验结果。
    这是第四段，讨论研究意义。
    """

    new_report = """
    这是第一段，介绍研究背景。（保持不变）
    这是第二段，描述了新的研究方法。（修改）
    这是新增的第三段，添加了更多内容。（新增）
    这是第四段，讨论研究意义。（保持不变）
    """

    comparator = ReportComparator()
    result = comparator.compare_reports(new_report, old_report)

    print("=== 比较结果 ===")
    print(result.get("summary", ""))

    print("\n=== 比较笔记 ===")
    note = comparator.generate_comparison_note(result)
    print(note)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
