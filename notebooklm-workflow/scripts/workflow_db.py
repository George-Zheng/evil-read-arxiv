#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Workflow 数据库模块
使用 SQLite 追踪已处理的论文
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class WorkflowDatabase:
    """论文处理追踪数据库"""

    def __init__(self, db_path: Path):
        """
        初始化数据库

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化数据库表"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 已处理论文表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_papers (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT,
                source_type TEXT,
                notebook_id TEXT,
                topic TEXT,
                processed_at TEXT NOT NULL,
                artifacts_generated TEXT,
                obsidian_note_path TEXT,
                email_sent INTEGER DEFAULT 0,
                metadata TEXT
            )
        """)

        # 研究主题表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS research_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_name TEXT UNIQUE NOT NULL,
                notebook_id TEXT,
                created_at TEXT NOT NULL,
                last_run_at TEXT,
                run_count INTEGER DEFAULT 0,
                config TEXT
            )
        """)

        # 执行记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                notebook_id TEXT,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                status TEXT,
                sources_found INTEGER,
                sources_imported INTEGER,
                artifacts TEXT,
                error_message TEXT
            )
        """)

        conn.commit()
        conn.close()

    def add_processed_paper(
        self,
        paper_id: str,
        title: str,
        url: str,
        source_type: str,
        notebook_id: str,
        topic: str,
        artifacts_generated: Optional[List[str]] = None,
        obsidian_note_path: Optional[str] = None
    ):
        """添加已处理的论文"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO processed_papers
            (id, title, url, source_type, notebook_id, topic, processed_at,
             artifacts_generated, obsidian_note_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            paper_id, title, url, source_type, notebook_id, topic,
            datetime.now().isoformat(),
            json.dumps(artifacts_generated) if artifacts_generated else None,
            obsidian_note_path
        ))

        conn.commit()
        conn.close()
        logger.debug(f"Added processed paper: {paper_id}")

    def is_paper_processed(self, paper_id: str) -> bool:
        """检查论文是否已处理"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM processed_papers WHERE id = ?",
            (paper_id,)
        )
        count = cursor.fetchone()[0]
        conn.close()

        return count > 0

    def get_processed_papers(
        self,
        topic: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取已处理的论文列表"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if topic:
            cursor.execute("""
                SELECT * FROM processed_papers
                WHERE topic = ?
                ORDER BY processed_at DESC
                LIMIT ?
            """, (topic, limit))
        else:
            cursor.execute("""
                SELECT * FROM processed_papers
                ORDER BY processed_at DESC
                LIMIT ?
            """, (limit,))

        papers = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return papers

    def add_research_topic(
        self,
        topic_name: str,
        notebook_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """添加研究主题"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO research_topics
            (topic_name, notebook_id, created_at, last_run_at, run_count, config)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            topic_name, notebook_id, datetime.now().isoformat(),
            datetime.now().isoformat(), 1, json.dumps(config)
        ))

        conn.commit()
        conn.close()

    def update_topic_run(
        self,
        topic_name: str,
        notebook_id: Optional[str] = None
    ):
        """更新主题运行记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE research_topics
            SET last_run_at = ?, run_count = run_count + 1
            WHERE topic_name = ?
        """, (datetime.now().isoformat(), topic_name))

        if notebook_id:
            cursor.execute("""
                UPDATE research_topics
                SET notebook_id = ?
                WHERE topic_name = ?
            """, (notebook_id, topic_name))

        conn.commit()
        conn.close()

    def add_execution_log(
        self,
        topic: str,
        notebook_id: str,
        status: str,
        sources_found: int = 0,
        sources_imported: int = 0,
        artifacts: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ):
        """添加执行日志"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO execution_logs
            (topic, notebook_id, started_at, completed_at, status,
             sources_found, sources_imported, artifacts, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            topic, notebook_id, datetime.now().isoformat(),
            datetime.now().isoformat(), status,
            sources_found, sources_imported,
            json.dumps(artifacts) if artifacts else None,
            error_message
        ))

        conn.commit()
        conn.close()

    def get_execution_history(
        self,
        topic: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取执行历史"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if topic:
            cursor.execute("""
                SELECT * FROM execution_logs
                WHERE topic = ?
                ORDER BY started_at DESC
                LIMIT ?
            """, (topic, limit))
        else:
            cursor.execute("""
                SELECT * FROM execution_logs
                ORDER BY started_at DESC
                LIMIT ?
            """, (limit,))

        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return logs

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        stats = {}

        # 总论文数
        cursor.execute("SELECT COUNT(*) FROM processed_papers")
        stats["total_papers"] = cursor.fetchone()[0]

        # 主题数
        cursor.execute("SELECT COUNT(*) FROM research_topics")
        stats["total_topics"] = cursor.fetchone()[0]

        # 执行次数
        cursor.execute("SELECT COUNT(*) FROM execution_logs")
        stats["total_executions"] = cursor.fetchone()[0]

        conn.close()
        return stats


def get_default_db_path() -> Path:
    """获取默认数据库路径"""
    import os
    home = Path.home()
    notebooklm_dir = home / ".notebooklm"
    notebooklm_dir.mkdir(parents=True, exist_ok=True)
    return notebooklm_dir / "workflow.db"


async def main():
    """测试数据库功能"""
    db = WorkflowDatabase(get_default_db_path())

    # 测试添加论文
    db.add_processed_paper(
        paper_id="2402.12345",
        title="Test Paper",
        url="https://arxiv.org/abs/2402.12345",
        source_type="arXiv",
        notebook_id="test-nb",
        topic="AI Chip"
    )

    # 检查是否已处理
    print(f"Is processed: {db.is_paper_processed('2402.12345')}")

    # 获取统计
    stats = db.get_stats()
    print(f"Stats: {stats}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
