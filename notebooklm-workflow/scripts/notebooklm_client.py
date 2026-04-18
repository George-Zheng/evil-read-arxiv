#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotebookLM API 客户端封装
提供 NotebookLM 操作的统一接口
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from notebooklm import NotebookLMClient, NotebookLMError, AuthError
    HAS_NOTEBOOKLM = True
except ImportError:
    HAS_NOTEBOOKLM = False
    logger.warning("notebooklm-py not installed. Run: pip install notebooklm-py")


class NotebookLMWorkflowClient:
    """NotebookLM 工作流客户端"""

    def __init__(self, storage_path: Optional[str] = None):
        """
        初始化 NotebookLM 客户端

        Args:
            storage_path: storage_state.json 路径，None 则使用默认位置
        """
        if not HAS_NOTEBOOKLM:
            raise ImportError(
                "notebooklm-py is required. Install with: pip install notebooklm-py"
            )

        self.storage_path = storage_path
        self._client: Optional[NotebookLMClient] = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        self._client = await NotebookLMClient.from_storage(
            path=self.storage_path
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self._client:
            # NotebookLMClient 使用 httpx.AsyncClient，需要关闭
            pass  # httpx 会自动关闭

    async def connect(self):
        """连接到 NotebookLM"""
        if not self._client:
            self._client = await NotebookLMClient.from_storage(
                path=self.storage_path
            )
        return self._client

    def _require_client(self):
        """确保客户端已连接"""
        if not self._client:
            raise RuntimeError("NotebookLM client not connected. Call connect() first.")
        return self._client

    # ========== Notebook 管理 ==========

    async def get_or_create_notebook(
        self,
        title: str,
        rotation: str = "quarterly"
    ) -> str:
        """
        获取或创建 Notebook

        Args:
            title: Notebook 标题
            rotation: 轮换策略 (quarterly/monthly/weekly)

        Returns:
            Notebook ID
        """
        client = self._require_client()

        # 根据轮换策略生成完整标题
        now = datetime.now()
        if rotation == "quarterly":
            quarter = (now.month - 1) // 3 + 1
            title_suffix = f"{now.year}-Q{quarter}"
        elif rotation == "monthly":
            title_suffix = f"{now.year}-{now.month:02d}"
        elif rotation == "weekly":
            title_suffix = f"{now.year}-W{now.isocalendar()[1]:02d}"
        else:
            title_suffix = now.strftime("%Y")

        full_title = f"{title}-{title_suffix}"

        # 查找是否已存在
        notebooks = await client.notebooks.list()
        for nb in notebooks:
            if nb.title == full_title:
                logger.info(f"Found existing notebook: {nb.id} ({nb.title})")
                return nb.id

        # 创建新的 Notebook
        logger.info(f"Creating new notebook: {full_title}")
        nb = await client.notebooks.create(full_title)
        return nb.id

    async def list_notebooks(self) -> List[Dict[str, Any]]:
        """列出所有 Notebook"""
        client = self._require_client()
        notebooks = await client.notebooks.list()
        return [
            {"id": nb.id, "title": nb.title, "created_at": str(nb.created_at)}
            for nb in notebooks
        ]

    async def delete_notebook(self, notebook_id: str):
        """删除 Notebook"""
        client = self._require_client()
        await client.notebooks.delete(notebook_id)
        logger.info(f"Deleted notebook: {notebook_id}")

    # ========== Source 管理 ==========

    async def add_source_url(
        self,
        notebook_id: str,
        url: str,
        title: Optional[str] = None,
        wait: bool = True
    ) -> str:
        """
        添加 URL 来源

        Args:
            notebook_id: Notebook ID
            url: 来源 URL
            title: 可选的标题
            wait: 是否等待处理完成

        Returns:
            Source ID
        """
        client = self._require_client()

        logger.info(f"Adding source: {url}")
        source = await client.sources.add_url(notebook_id, url, wait=wait)

        if title and source.title != title:
            await client.sources.rename(notebook_id, source.id, title)

        logger.info(f"Added source: {source.id} ({source.title})")
        return source.id

    async def add_sources_batch(
        self,
        notebook_id: str,
        sources: List[Dict[str, str]],
        wait_each: bool = True
    ) -> List[str]:
        """
        批量添加来源

        Args:
            notebook_id: Notebook ID
            sources: 来源列表，每项包含 {"url": ..., "title": ...}
            wait_each: 是否等待每个来源处理完成

        Returns:
            Source ID 列表
        """
        source_ids = []
        for src in sources:
            try:
                source_id = await self.add_source_url(
                    notebook_id,
                    src["url"],
                    src.get("title"),
                    wait_each
                )
                source_ids.append(source_id)
            except Exception as e:
                logger.error(f"Failed to add source {src.get('url')}: {e}")
        return source_ids

    async def list_sources(self, notebook_id: str) -> List[Dict[str, Any]]:
        """列出 Notebook 中的所有来源"""
        client = self._require_client()
        sources = await client.sources.list(notebook_id)
        return [
            {
                "id": src.id,
                "title": src.title,
                "url": src.url,
                "type": str(src.kind),
                "status": str(src.status)
            }
            for src in sources
        ]

    # ========== Deep Research ==========

    async def start_research(
        self,
        notebook_id: str,
        query: str,
        mode: str = "deep",
        source: str = "web"
    ) -> Dict[str, Any]:
        """
        启动深度研究

        Args:
            notebook_id: Notebook ID
            query: 研究问题
            mode: "deep" 或 "fast"
            source: "web" 或 "drive"

        Returns:
            研究任务信息 {"task_id": ..., "status": ...}
        """
        client = self._require_client()

        logger.info(f"Starting {mode} research: {query}")
        result = await client.research.start(notebook_id, query, source, mode)
        logger.info(f"Research task started: {result.get('task_id')}")
        return result

    async def poll_research(
        self,
        notebook_id: str,
        timeout: int = 600,
        interval: int = 10
    ) -> Dict[str, Any]:
        """
        轮询研究状态直到完成

        Args:
            notebook_id: Notebook ID
            timeout: 超时时间（秒）
            interval: 轮询间隔（秒）

        Returns:
            研究结果
        """
        client = self._require_client()

        max_iterations = timeout // interval
        logger.info(f"Waiting for research to complete (timeout={timeout}s)...")

        for i in range(max_iterations):
            status = await client.research.poll(notebook_id)
            status_val = status.get("status", "unknown")

            if status_val == "completed":
                logger.info("Research completed!")
                return status
            elif status_val == "no_research":
                raise RuntimeError("No research task found")

            logger.debug(f"Research status: {status_val}")
            await asyncio.sleep(interval)

        raise TimeoutError(f"Research timed out after {timeout}s")

    async def import_research_sources(
        self,
        notebook_id: str,
        task_id: str,
        sources: List[Dict[str, Any]],
        max_sources: int = 20
    ) -> List[str]:
        """
        导入研究发现的来源

        Args:
            notebook_id: Notebook ID
            task_id: 研究任务 ID
            sources: 来源列表
            max_sources: 最大导入数量

        Returns:
            成功导入的来源 ID 列表
        """
        client = self._require_client()

        sources_to_import = sources[:max_sources]
        logger.info(f"Importing {len(sources_to_import)} sources...")

        imported = await client.research.import_sources(
            notebook_id, task_id, sources_to_import
        )

        logger.info(f"Imported {len(imported)} sources")
        return imported

    # ========== Artifact 生成 ==========

    async def generate_slide_deck(
        self,
        notebook_id: str,
        format: str = "detailed",
        instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成 Slide Deck"""
        client = self._require_client()

        slide_format = "detailed" if format == "detailed" else "presenter"
        logger.info(f"Generating slide deck (format={slide_format})...")

        status = await client.artifacts.generate_slide_deck(
            notebook_id,
            format=slide_format,
            instructions=instructions
        )
        return {"task_id": status.task_id, "status": str(status)}

    async def generate_audio(
        self,
        notebook_id: str,
        instructions: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """生成 Audio Overview"""
        client = self._require_client()

        logger.info(f"Generating audio overview (language={language})...")

        status = await client.artifacts.generate_audio(
            notebook_id,
            instructions=instructions
        )
        return {"task_id": status.task_id, "status": str(status)}

    async def generate_report(
        self,
        notebook_id: str,
        format: str = "briefing-doc",
        instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成 Report"""
        client = self._require_client()

        logger.info(f"Generating report (format={format})...")

        status = await client.artifacts.generate_report(
            notebook_id,
            format=format,
            instructions=instructions
        )
        return {"task_id": status.task_id, "status": str(status)}

    async def wait_for_artifact(
        self,
        notebook_id: str,
        task_id: str,
        timeout: int = 600,
        interval: int = 10
    ) -> Dict[str, Any]:
        """等待 Artifact 生成完成"""
        client = self._require_client()

        max_iterations = timeout // interval

        for i in range(max_iterations):
            artifacts = await client.artifacts.list(notebook_id)

            for artifact in artifacts:
                if artifact.id == task_id or task_id in artifact.id:
                    if artifact.is_complete:
                        return {
                            "id": artifact.id,
                            "type": artifact.kind,
                            "url": artifact.url,
                            "is_complete": True
                        }

            await asyncio.sleep(interval)

        raise TimeoutError(f"Artifact generation timed out after {timeout}s")

    # ========== 下载 ==========

    async def download_artifact(
        self,
        notebook_id: str,
        artifact_id: str,
        output_path: str,
        format: Optional[str] = None
    ) -> str:
        """
        下载 Artifact

        Args:
            notebook_id: Notebook ID
            artifact_id: Artifact ID
            output_path: 输出文件路径
            format: 输出格式（pdf/pptx/mp3/md 等）

        Returns:
            保存的文件路径
        """
        client = self._require_client()

        # 获取 artifact 类型
        artifacts = await client.artifacts.list(notebook_id)
        artifact = None
        for a in artifacts:
            if a.id == artifact_id or artifact_id in a.id:
                artifact = a
                break

        if not artifact:
            raise ValueError(f"Artifact not found: {artifact_id}")

        artifact_type = str(artifact.kind).lower()

        logger.info(f"Downloading {artifact_type} to {output_path}...")

        # 根据类型调用不同的下载方法
        if "slide" in artifact_type:
            await client.artifacts.download_slide_deck(
                notebook_id, artifact_id, output_path, format=format
            )
        elif "audio" in artifact_type:
            await client.artifacts.download_audio(
                notebook_id, artifact_id, output_path
            )
        elif "report" in artifact_type:
            await client.artifacts.download_report(
                notebook_id, artifact_id, output_path
            )
        else:
            raise ValueError(f"Unsupported artifact type: {artifact_type}")

        return output_path


async def main():
    """测试客户端"""
    async with NotebookLMWorkflowClient() as client:
        await client.connect()

        # 列出 Notebook
        notebooks = await client.list_notebooks()
        print(f"Found {len(notebooks)} notebooks:")
        for nb in notebooks:
            print(f"  - {nb['title']} ({nb['id']})")


if __name__ == "__main__":
    asyncio.run(main())
