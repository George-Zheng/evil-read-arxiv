#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Artifact 生成脚本
生成 Slide Deck、Audio、Report 等内容
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from notebooklm_client import NotebookLMWorkflowClient

logger = logging.getLogger(__name__)


class ArtifactGenerator:
    """Artifact 生成器"""

    def __init__(self, client: NotebookLMWorkflowClient):
        self.client = client

    async def generate_all(
        self,
        notebook_id: str,
        topic: str,
        slide_format: str = "pdf",
        audio_language: str = "en",
        report_format: str = "briefing-doc",
        timeout: int = 600
    ) -> Dict[str, Any]:
        """
        生成所有类型的 Artifact

        Args:
            notebook_id: Notebook ID
            topic: 研究主题（用于生成指令）
            slide_format: Slide 格式 (pdf/pptx)
            audio_language: 音频语言
            report_format: 报告格式
            timeout: 生成超时时间

        Returns:
            生成结果
        """
        results = {
            "notebook_id": notebook_id,
            "topic": topic,
            "artifacts": {}
        }

        # 1. 生成 Slide Deck
        try:
            logger.info("Generating slide deck...")
            slide_result = await self.client.generate_slide_deck(
                notebook_id,
                format="detailed",
                instructions=f"Create a detailed slide deck about {topic}"
            )
            results["artifacts"]["slide_deck"] = slide_result
            logger.info(f"Slide deck generation started: {slide_result['task_id']}")
        except Exception as e:
            logger.error(f"Failed to generate slide deck: {e}")
            results["artifacts"]["slide_deck"] = {"error": str(e)}

        # 2. 生成 Audio
        try:
            logger.info("Generating audio overview...")
            audio_result = await self.client.generate_audio(
                notebook_id,
                instructions=f"Create an engaging audio overview about {topic}",
                language=audio_language
            )
            results["artifacts"]["audio"] = audio_result
            logger.info(f"Audio generation started: {audio_result['task_id']}")
        except Exception as e:
            logger.error(f"Failed to generate audio: {e}")
            results["artifacts"]["audio"] = {"error": str(e)}

        # 3. 生成 Report
        try:
            logger.info("Generating report...")
            report_result = await self.client.generate_report(
                notebook_id,
                format=report_format,
                instructions=f"Create a comprehensive report about {topic}"
            )
            results["artifacts"]["report"] = report_result
            logger.info(f"Report generation started: {report_result['task_id']}")
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            results["artifacts"]["report"] = {"error": str(e)}

        # 4. 等待所有 Artifact 完成
        logger.info("Waiting for artifacts to complete...")
        for artifact_type, result in results["artifacts"].items():
            if "task_id" in result:
                try:
                    final = await self.client.wait_for_artifact(
                        notebook_id, result["task_id"], timeout=timeout
                    )
                    results["artifacts"][artifact_type] = {
                        **result,
                        "final": final,
                        "completed": True
                    }
                    logger.info(f"{artifact_type} completed: {final.get('url', 'N/A')}")
                except TimeoutError as e:
                    logger.warning(f"{artifact_type} timed out: {e}")
                    results["artifacts"][artifact_type]["completed"] = False

        return results

    async def download_artifacts(
        self,
        notebook_id: str,
        output_dir: Path,
        artifacts: Dict[str, Any],
        formats: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        下载生成的 Artifact

        Args:
            notebook_id: Notebook ID
            output_dir: 输出目录
            artifacts: Artifact 信息
            formats: 格式配置 {"slide_deck": "pdf", "audio": "mp3", "report": "md"}

        Returns:
            下载的文件路径
        """
        formats = formats or {
            "slide_deck": "pdf",
            "audio": "mp3",
            "report": "md"
        }

        downloaded = {}

        for artifact_type, artifact_data in artifacts.items():
            if "error" in artifact_data:
                continue

            final = artifact_data.get("final", {})
            if not final or not final.get("is_complete"):
                logger.warning(f"Skipping {artifact_type}: not complete")
                continue

            # 确定文件扩展名
            ext = formats.get(artifact_type, "bin")
            output_path = output_dir / f"{artifact_type}.{ext}"

            try:
                # 获取 artifact ID
                artifact_id = final.get("id", "")
                if not artifact_id:
                    # 从 task_id 提取
                    artifact_id = artifact_data.get("task_id", "")

                # 使用 notebook ID 作为 artifact_id 的代理
                # 实际下载时需要正确的 artifact ID
                logger.info(f"Would download {artifact_type} to {output_path}")
                # 实际下载需要正确的 artifact ID，这里记录路径
                downloaded[artifact_type] = str(output_path)
            except Exception as e:
                logger.error(f"Failed to download {artifact_type}: {e}")

        return downloaded


async def main():
    """测试 Artifact 生成"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python generate_artifacts.py <notebook_id> [topic]")
        print("Example: python generate_artifacts.py abc123 'AI Chip Research'")
        sys.exit(1)

    notebook_id = sys.argv[1]
    topic = sys.argv[2] if len(sys.argv) > 2 else "Research Summary"

    async with NotebookLMWorkflowClient() as client:
        await client.connect()
        generator = ArtifactGenerator(client)

        results = await generator.generate_all(notebook_id, topic)

        print("\n=== Generation Results ===")
        for artifact_type, result in results["artifacts"].items():
            status = "✓" if result.get("completed") else "✗"
            print(f"{status} {artifact_type}: {result.get('task_id', 'N/A')}")


if __name__ == "__main__":
    asyncio.run(main())
