#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotebookLM Workflow 主脚本
整合 Deep Research、Artifact 生成、Obsidian 导出和邮件发送
"""

import asyncio
import argparse
import logging
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# 导入模块
from notebooklm_client import NotebookLMWorkflowClient
from deep_research import DeepResearchWorkflow
from generate_artifacts import ArtifactGenerator
from export_to_obsidian import (
    get_vault_path,
    generate_note_content,
    export_to_obsidian,
    create_exports_folder
)
from send_email import send_research_email, get_email_config
from workflow_db import WorkflowDatabase, get_default_db_path
from report_comparator import ReportComparator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """加载配置文件"""
    import yaml

    # 默认配置路径
    if config_path is None:
        vault_path = Path(get_vault_path())
        config_path = vault_path / "99_System" / "Config" / "research_interests.yaml"

    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}")
        return {}

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="NotebookLM Workflow - 自动化研究和内容生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 运行自定义主题研究
  python workflow_main.py "low cost inference chip design"

  # 使用预配置主题
  python workflow_main.py --topic "AI-Chip"

  # 从今日推荐处理
  python workflow_main.py --from-recommended --top 3

  # 发送邮件报告
  python workflow_main.py "KV cache compression" --send-email
        """
    )

    # 输入源
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "topic",
        nargs='?',
        help="研究主题"
    )
    input_group.add_argument(
        "--topic",
        help="从配置中读取的研究主题名称"
    )
    input_group.add_argument(
        "--from-recommended",
        action="store_true",
        help="从今日推荐中获取论文"
    )

    # 研究配置
    parser.add_argument(
        "--mode",
        choices=["deep", "fast"],
        default="deep",
        help="研究模式 (default: deep)"
    )
    parser.add_argument(
        "--max-sources",
        type=int,
        default=20,
        help="最大来源数量 (default: 20)"
    )
    parser.add_argument(
        "--research-timeout",
        type=int,
        default=600,
        help="研究超时时间（秒）(default: 600)"
    )

    # Notebook 配置
    parser.add_argument(
        "--notebook-prefix",
        default="Research",
        help="Notebook 标题前缀 (default: Research)"
    )
    parser.add_argument(
        "--rotation",
        choices=["quarterly", "monthly", "weekly"],
        default="quarterly",
        help="Notebook 轮换策略 (default: quarterly)"
    )

    # 生成配置
    parser.add_argument(
        "--generate",
        nargs='*',
        choices=["slide", "audio", "report", "all"],
        default=["all"],
        help="生成的内容类型 (default: all)"
    )
    parser.add_argument(
        "--artifact-timeout",
        type=int,
        default=600,
        help="Artifact 生成超时（秒）(default: 600)"
    )

    # Obsidian 配置
    parser.add_argument(
        "--vault",
        help="Obsidian Vault 路径"
    )
    parser.add_argument(
        "--export-folder",
        default="NotebookLM/Exports",
        help="导出文件夹 (default: NotebookLM/Exports)"
    )
    parser.add_argument(
        "--no-export",
        action="store_true",
        help="不导出到 Obsidian"
    )

    # 邮件配置
    parser.add_argument(
        "--send-email",
        action="store_true",
        help="发送邮件报告"
    )
    parser.add_argument(
        "--email-config",
        help="邮件配置文件路径"
    )

    # 报告比较配置
    parser.add_argument(
        "--compare",
        action="store_true",
        help="与上一次报告进行比较"
    )
    parser.add_argument(
        "--compare-only",
        action="store_true",
        help="只进行比较，不执行研究"
    )

    # 其他配置
    parser.add_argument(
        "--config",
        help="配置文件路径"
    )
    parser.add_argument(
        "--db-path",
        help="数据库路径"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只打印计划，不执行"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="详细输出"
    )

    args = parser.parse_args()

    # 验证输入
    if not args.topic and not args.from_recommended:
        parser.error("需要指定研究主题或使用 --from-recommended")

    return args


async def run_workflow(args):
    """运行主工作流"""

    # 加载配置
    config = load_config(Path(args.config) if args.config else None)

    # 获取 Vault 路径
    vault_path = get_vault_path(args.vault)
    logger.info(f"Using vault: {vault_path}")

    # 初始化数据库
    db_path = Path(args.db_path) if args.db_path else get_default_db_path()
    db = WorkflowDatabase(db_path)
    logger.info(f"Using database: {db_path}")

    # 确定研究主题
    topic = args.topic
    if args.from_recommended:
        logger.info("Loading from recommended papers...")
        # TODO: 从 start-my-day 的输出加载
        topic = "Recommended Papers"

    notebook_title = f"{args.notebook_prefix} {topic}"

    if args.dry_run:
        print(f"\n=== Dry Run ===")
        print(f"Topic: {topic}")
        print(f"Notebook: {notebook_title}")
        print(f"Mode: {args.mode}")
        print(f"Max sources: {args.max_sources}")
        print(f"Vault: {vault_path}")
        print(f"Send email: {args.send_email}")
        return {"success": True, "dry_run": True}

    # 开始工作流
    logger.info(f"Starting workflow for: {topic}")

    try:
        async with NotebookLMWorkflowClient() as client:
            await client.connect()

            # ========== 1. Deep Research ==========
            logger.info("Step 1: Deep Research")
            workflow = DeepResearchWorkflow(client)

            research_result = await workflow.run_research(
                topic=topic,
                notebook_title=notebook_title,
                mode=args.mode,
                rotation=args.rotation,
                max_sources=args.max_sources,
                research_timeout=args.research_timeout
            )

            notebook_id = research_result["notebook_id"]
            logger.info(f"Research completed. Notebook: {notebook_id}")

            # ========== 2. 生成 Artifact ==========
            logger.info("Step 2: Generating Artifacts")
            generator = ArtifactGenerator(client)

            artifacts_result = await generator.generate_all(
                notebook_id=notebook_id,
                topic=topic,
                timeout=args.artifact_timeout
            )

            logger.info("Artifact generation completed")

            # ========== 3. 导出到 Obsidian ==========
            obsidian_path = None
            comparison_note_path = None
            comparison_result = None
            if not args.no_export:
                logger.info("Step 3: Exporting to Obsidian")

                # 创建导出文件夹
                exports_dir = create_exports_folder(vault_path, args.export_folder)

                # 生成完整笔记内容
                note_content = generate_note_content(
                    topic=topic,
                    research_result=research_result,
                    artifacts=artifacts_result,
                    language="zh"  # 从配置读取
                )

                # 导出完整报告
                obsidian_path = export_to_obsidian(
                    note_content, vault_path, topic, args.export_folder
                )
                logger.info(f"Exported full report to: {obsidian_path}")

                # ========== 3.5 与上一次报告比较 ==========
                if args.compare:
                    logger.info("Step 3.5: Comparing with previous report")
                    comparator = ReportComparator(db_path)

                    # 获取新报告内容
                    new_report = artifacts_result.get("artifacts", {}).get("report", {}).get("content", "")

                    # 获取上一次报告并比较
                    comparison_result = comparator.compare_reports(
                        new_report=new_report,
                        old_report=comparator.get_last_report(topic)
                    )

                    # 生成比较报告内容
                    from export_to_obsidian import generate_comparison_note_content
                    comparison_content = generate_comparison_note_content(
                        topic=topic,
                        comparison_result=comparison_result,
                        language="zh"
                    )

                    # 导出比较报告（使用不同的文件夹）
                    comparison_folder = f"{args.export_folder}/Comparisons"
                    comparison_note_path = export_to_obsidian(
                        comparison_content, vault_path, f"{topic}_comparison", comparison_folder
                    )
                    logger.info(f"Exported comparison report to: {comparison_note_path}")

            # ========== 4. 发送邮件 ==========
            if args.send_email:
                logger.info("Step 4: Sending email")

                email_config = get_email_config()
                if email_config.get("password"):
                    # 发送完整报告邮件
                    logger.info("Sending full report email...")
                    success_full = await send_research_email(
                        topic=topic,
                        research_result=research_result,
                        artifacts=artifacts_result,
                        config=email_config,
                        email_type="full"
                    )
                    if success_full:
                        logger.info("Full report email sent successfully")
                    else:
                        logger.warning("Failed to send full report email")

                    # 发送比较报告邮件（如果有比较结果）
                    if comparison_result and comparison_result.get("has_comparison"):
                        logger.info("Sending comparison report email...")
                        success_comparison = await send_research_email(
                            topic=topic,
                            research_result=research_result,
                            artifacts=artifacts_result,
                            config=email_config,
                            comparison_result=comparison_result,
                            email_type="comparison"
                        )
                        if success_comparison:
                            logger.info("Comparison report email sent successfully")
                        else:
                            logger.warning("Failed to send comparison report email")
                    else:
                        logger.info("No comparison available, skipping comparison email")
                else:
                    logger.warning("Email password not configured, skipping")

            # ========== 5. 记录到数据库 ==========
            logger.info("Step 5: Recording to database")

            db.add_research_topic(
                topic_name=topic,
                notebook_id=notebook_id
            )

            # 获取报告内容用于下次比较
            report_content = artifacts_result.get("artifacts", {}).get("report", {}).get("content", "")

            db.add_execution_log(
                topic=topic,
                notebook_id=notebook_id,
                status="success",
                sources_found=research_result.get("sources_found", 0),
                sources_imported=research_result.get("sources_imported", 0),
                artifacts=artifacts_result.get("artifacts", {}),
                report_content=report_content
            )

            # 记录处理的论文
            for src in research_result.get("all_sources", []):
                db.add_processed_paper(
                    paper_id=src.get("id", ""),
                    title=src.get("title", ""),
                    url=src.get("url", ""),
                    source_type=src.get("type", ""),
                    notebook_id=notebook_id,
                    topic=topic,
                    obsidian_note_path=str(obsidian_path) if obsidian_path else None
                )

            # ========== 完成 ==========
            logger.info("Workflow completed successfully!")

            # 输出结果摘要
            print("\n" + "=" * 50)
            print("Workflow Summary")
            print("=" * 50)
            print(f"Topic: {topic}")
            print(f"Notebook: {notebook_title} ({notebook_id})")
            print(f"Sources found: {research_result.get('sources_found', 0)}")
            print(f"Sources imported: {research_result.get('sources_imported', 0)}")
            print(f"Full report: {obsidian_path}")
            if comparison_note_path:
                print(f"Comparison report: {comparison_note_path}")
            print(f"Database: {db_path}")

            # 显示比较结果
            if comparison_result and comparison_result.get("has_comparison"):
                print("\n--- Report Comparison ---")
                print(comparison_result.get("summary", ""))

            print("=" * 50)

            return {
                "success": True,
                "notebook_id": notebook_id,
                "topic": topic,
                "obsidian_path": str(obsidian_path),
                "research": research_result,
                "artifacts": artifacts_result
            }

    except Exception as e:
        logger.exception(f"Workflow failed: {e}")

        # 记录错误
        db.add_execution_log(
            topic=topic,
            notebook_id="",
            status="error",
            error_message=str(e)
        )

        return {"success": False, "error": str(e)}


async def main():
    """主入口"""
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    result = await run_workflow(args)

    if result and result.get("success"):
        print("\n✓ Workflow completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Workflow failed")
        if result and result.get("error"):
            print(f"Error: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
