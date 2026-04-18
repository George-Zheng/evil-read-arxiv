#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotebookLM Deep Research 集成
支持深度和快速两种研究模式
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from notebooklm_client import NotebookLMWorkflowClient

logger = logging.getLogger(__name__)


class DeepResearchWorkflow:
    """NotebookLM Deep Research 工作流"""

    def __init__(self, client: NotebookLMWorkflowClient):
        self.client = client

    async def run_research(
        self,
        topic: str,
        notebook_title: str,
        mode: str = "deep",
        rotation: str = "quarterly",
        max_sources: int = 20,
        research_timeout: int = 600,
        auto_import: bool = True
    ) -> Dict[str, Any]:
        """
        运行完整的研究工作流

        Args:
            topic: 研究主题
            notebook_title: Notebook 标题
            mode: "deep" 或 "fast"
            rotation: Notebook 轮换策略
            max_sources: 最大来源数量
            research_timeout: 研究超时（秒）
            auto_import: 是否自动导入来源

        Returns:
            研究结果
        """
        logger.info(f"Starting research workflow for: {topic}")
        logger.info(f"Mode: {mode}, Notebook: {notebook_title}")

        # 1. 获取或创建 Notebook
        notebook_id = await self.client.get_or_create_notebook(
            notebook_title, rotation
        )
        logger.info(f"Using notebook: {notebook_id}")

        # 2. 启动研究
        research_result = await self.client.start_research(
            notebook_id, topic, mode
        )
        task_id = research_result.get("task_id")
        logger.info(f"Research task: {task_id}")

        # 3. 等待研究完成
        research_status = await self.client.poll_research(
            notebook_id, timeout=research_timeout
        )

        sources = research_status.get("sources", [])
        report = research_status.get("report", "")

        logger.info(f"Research completed: found {len(sources)} sources")

        # 4. 导入来源
        imported_sources = []
        if auto_import and sources and task_id:
            imported_sources = await self.client.import_research_sources(
                notebook_id, task_id, sources, max_sources
            )
            logger.info(f"Imported {len(imported_sources)} sources")

        # 5. 列出导入的来源
        all_sources = await self.client.list_sources(notebook_id)

        return {
            "notebook_id": notebook_id,
            "notebook_title": notebook_title,
            "topic": topic,
            "mode": mode,
            "task_id": task_id,
            "sources_found": len(sources),
            "sources_imported": len(imported_sources),
            "sources": sources,
            "imported_sources": imported_sources,
            "all_sources": all_sources,
            "report": report
        }

    async def research_with_existing_sources(
        self,
        notebook_id: str,
        topic: str,
        sources: List[Dict[str, str]],
        mode: str = "deep"
    ) -> Dict[str, Any]:
        """
        使用已有来源运行研究

        Args:
            notebook_id: Notebook ID
            topic: 研究主题
            sources: 来源列表 [{"url": "...", "title": "..."}]
            mode: 研究模式

        Returns:
            研究结果
        """
        # 添加来源
        logger.info(f"Adding {len(sources)} sources...")
        source_ids = await self.client.add_sources_batch(
            notebook_id, sources, wait_each=True
        )
        logger.info(f"Added {len(source_ids)} sources")

        # 启动研究
        research_result = await self.client.start_research(
            notebook_id, topic, mode
        )

        # 等待完成
        research_status = await self.client.poll_research(notebook_id)

        return {
            "notebook_id": notebook_id,
            "topic": topic,
            "sources_added": len(source_ids),
            "task_id": research_result.get("task_id"),
            "report": research_status.get("report", "")
        }


async def main():
    """测试 Deep Research"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python deep_research.py <research_topic>")
        print("Example: python deep_research.py 'low cost inference chip design'")
        sys.exit(1)

    topic = " ".join(sys.argv[1:])

    async with NotebookLMWorkflowClient() as client:
        await client.connect()
        workflow = DeepResearchWorkflow(client)

        result = await workflow.run_research(
            topic=topic,
            notebook_title="Research",
            mode="deep"
        )

        print("\n=== Research Result ===")
        print(f"Notebook: {result['notebook_title']} ({result['notebook_id']})")
        print(f"Topic: {result['topic']}")
        print(f"Sources found: {result['sources_found']}")
        print(f"Sources imported: {result['sources_imported']}")

        if result['report']:
            print(f"\nReport preview:\n{result['report'][:500]}...")


if __name__ == "__main__":
    asyncio.run(main())
