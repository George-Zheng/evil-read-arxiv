#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件发送脚本
支持 QQ 邮箱 SMTP 发送 HTML 邮件

敏感配置（邮箱地址、密码等）通过环境变量读取，不硬编码在代码中。
"""

import logging
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


# QQ 邮箱 SMTP 配置（非敏感，可硬编码）
QQ_SMTP_SERVER = "smtp.qq.com"
QQ_SMTP_PORT = 587  # 或 465 (SSL)


def get_email_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    获取邮件配置

    优先级：
    1. 传入的 config 参数
    2. 环境变量
    3. 默认值

    Args:
        config: 配置字典（可选）

    Returns:
        邮件配置
    """
    # 从环境变量读取敏感信息
    sender = os.environ.get("EMAIL_SENDER", "")
    recipients_str = os.environ.get("EMAIL_RECIPIENTS", "")
    username = os.environ.get("EMAIL_USERNAME", sender)  # 默认与 sender 相同
    password = os.environ.get("EMAIL_PASSWORD", "")
    smtp_server = os.environ.get("EMAIL_SMTP_SERVER", QQ_SMTP_SERVER)
    smtp_port = int(os.environ.get("EMAIL_SMTP_PORT", str(QQ_SMTP_PORT)))
    use_ssl = os.environ.get("EMAIL_USE_SSL", "true").lower() == "true"

    # 解析收件人列表（支持逗号分隔多个邮箱）
    recipients = [r.strip() for r in recipients_str.split(",") if r.strip()]

    # 默认配置
    default_config = {
        "enabled": True,
        "smtp_server": smtp_server,
        "smtp_port": smtp_port,
        "sender": sender,
        "recipients": recipients,
        "use_ssl": use_ssl,
        "username": username,
        "password": password,
    }

    # 从参数合并配置（参数优先级更高）
    if config:
        default_config.update(config)

    # 验证必要配置
    if not default_config.get("sender"):
        logger.error(
            "EMAIL_SENDER environment variable not set. "
            "Please set it to your QQ email (e.g., qiaoshi.zheng@foxmail.com)."
        )
        default_config["enabled"] = False

    if not default_config.get("recipients"):
        logger.error(
            "EMAIL_RECIPIENTS environment variable not set. "
            "Please set it to recipient emails (comma-separated)."
        )
        default_config["enabled"] = False

    if not default_config.get("password"):
        logger.warning(
            "EMAIL_PASSWORD environment variable not set. "
            "Please set it to your QQ email authorization code."
        )
        default_config["enabled"] = False

    return default_config

    return default_config


def generate_email_html(
    topic: str,
    research_result: Dict[str, Any],
    artifacts: Optional[Dict[str, Any]] = None,
    include_summary: bool = True,
    include_paper_list: bool = True,
    include_artifacts: bool = True
) -> str:
    """
    生成 HTML 邮件正文

    Args:
        topic: 研究主题
        research_result: 研究结果
        artifacts: Artifact 结果
        include_summary: 是否包含摘要
        include_paper_list: 是否包含论文列表
        include_artifacts: 是否包含生成的内容

    Returns:
        HTML 内容
    """
    # 基础样式
    style = """
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #1a1a1a; border-bottom: 2px solid #4a9eff; padding-bottom: 10px; }
        h2 { color: #4a9eff; margin-top: 30px; }
        .meta { background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 20px 0; }
        .meta-item { margin: 8px 0; }
        .label { font-weight: 600; color: #666; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; font-weight: 600; }
        tr:hover { background: #f8f9fa; }
        .status { display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: 600; }
        .status-success { background: #d4edda; color: #155724; }
        .status-pending { background: #fff3cd; color: #856404; }
        .status-error { background: #f8d7da; color: #721c24; }
        .artifact-list { list-style: none; padding: 0; }
        .artifact-list li { padding: 10px; margin: 8px 0; background: #f8f9fa; border-radius: 6px; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 14px; }
        a { color: #4a9eff; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
    """

    # 开始构建 HTML
    html = f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        {style}
    </head>
    <body>
    """

    # 标题
    html += f"<h1>📚 NotebookLM 研究报告</h1>"
    html += f"<p><strong>主题：</strong>{topic}</p>"

    # 元信息
    html += """<div class="meta">"""
    html += f"""<div class="meta-item"><span class="label">生成时间：</span>{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>"""
    html += f"""<div class="meta-item"><span class="label">Notebook ID：</span><code>{research_result.get('notebook_id', 'N/A')}</code></div>"""
    html += f"""<div class="meta-item"><span class="label">研究模式：</span>{research_result.get('mode', 'deep').upper()}</div>"""
    html += f"""<div class="meta-item"><span class="label">发现来源：</span>{research_result.get('sources_found', 0)} 篇</div>"""
    html += f"""<div class="meta-item"><span class="label">导入来源：</span>{research_result.get('sources_imported', 0)} 篇</div>"""
    html += """</div>"""

    # 研究摘要
    if include_summary and research_result.get("report"):
        html += "<h2>📋 研究摘要</h2>"
        html += f"<div>{research_result['report'][:2000]}{'...' if len(research_result['report']) > 2000 else ''}</div>"

    # 论文列表
    if include_paper_list:
        sources = research_result.get("all_sources", [])
        if sources:
            html += "<h2>📄 来源文献</h2>"
            html += """<table>
            <thead>
                <tr><th>#</th><th>标题</th><th>类型</th><th>链接</th></tr>
            </thead>
            <tbody>
            """
            for i, src in enumerate(sources[:15], 1):  # 限制显示 15 篇
                title = src.get("title", "Untitled")
                src_type = src.get("type", "Unknown")
                url = src.get("url", "")
                html += f"""<tr>
                    <td>{i}</td>
                    <td>{title[:50]}{'...' if len(title) > 50 else ''}</td>
                    <td>{src_type}</td>
                    <td><a href="{url}" target="_blank">查看</a></td>
                </tr>
                """
            html += """</tbody></table>"""
            if len(sources) > 15:
                html += f"<p><em>还有 {len(sources) - 15} 篇文献未在列表中显示</em></p>"

    # 生成的内容
    if include_artifacts and artifacts:
        artifacts_data = artifacts.get("artifacts", {})
        if artifacts_data:
            html += "<h2>🎨 生成的内容</h2>"
            html += '<ul class="artifact-list">'

            for artifact_type, data in artifacts_data.items():
                if "error" in data:
                    status = '<span class="status status-error">失败</span>'
                elif data.get("completed"):
                    status = '<span class="status status-success">完成</span>'
                else:
                    status = '<span class="status status-pending">处理中</span>'

                name_map = {
                    "slide_deck": "Slide Deck",
                    "audio": "Audio Overview",
                    "report": "Report"
                }
                name = name_map.get(artifact_type, artifact_type)
                html += f"<li><strong>{name}</strong> {status}</li>"

            html += "</ul>"

    # 脚注
    html += """<div class="footer">
    <p>此邮件由 notebooklm-workflow 自动生成</p>
    <p>如需更改邮件设置，请修改配置文件中的 email 部分</p>
    </div>"""

    html += """</body></html>"""

    return html


def generate_email_subject(topic: str, template: str = None) -> str:
    """生成邮件主题"""
    if template:
        return template.format(
            topic=topic,
            date=datetime.now().strftime("%Y-%m-%d")
        )
    return f"[NotebookLM Research] {topic} - {datetime.now().strftime('%Y-%m-%d')}"


def send_email(
    subject: str,
    html_content: str,
    config: Dict[str, Any],
    attachments: Optional[List[Path]] = None
) -> bool:
    """
    发送邮件

    Args:
        subject: 邮件主题
        html_content: HTML 正文
        config: 邮件配置
        attachments: 附件列表

    Returns:
        是否发送成功
    """
    sender = config.get("sender", "qiaoshi.zheng@foxmail.com")
    recipients = config.get("recipients", ["zhengqiaoshi@huawei.com"])
    password = config.get("password")

    if not password:
        logger.error("Email password not configured. Set EMAIL_PASSWORD environment variable.")
        return False

    # 创建邮件
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)

    # 添加 HTML 正文
    html_part = MIMEText(html_content, "html", "utf-8")
    msg.attach(html_part)

    # 添加附件
    if attachments:
        for file_path in attachments:
            if file_path.exists():
                with open(file_path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={file_path.name}"
                    )
                    msg.attach(part)
                logger.info(f"Attached: {file_path.name}")

    # 发送邮件
    try:
        if config.get("use_ssl"):
            # SSL 连接（端口 465）
            server = smtplib.SMTP_SSL(config["smtp_server"], config.get("smtp_port", 465))
        else:
            # STARTTLS（端口 587）
            server = smtplib.SMTP(config["smtp_server"], config.get("smtp_port", 587))
            server.starttls()

        server.login(config.get("username", sender), password)
        server.sendmail(sender, recipients, msg.as_string())
        server.quit()

        logger.info(f"Email sent successfully to {recipients}")
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed. Check your QQ email authorization code.")
        return False
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


async def send_research_email(
    topic: str,
    research_result: Dict[str, Any],
    artifacts: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    attachments: Optional[List[Path]] = None
) -> bool:
    """
    发送研究报告邮件

    Args:
        topic: 研究主题
        research_result: 研究结果
        artifacts: Artifact 结果
        config: 邮件配置
        attachments: 附件列表

    Returns:
        是否发送成功
    """
    # 获取配置
    email_config = get_email_config(config)

    if not email_config.get("enabled"):
        logger.info("Email sending is disabled")
        return False

    # 生成邮件内容
    html_content = generate_email_html(
        topic,
        research_result,
        artifacts,
        include_summary=True,
        include_paper_list=True,
        include_artifacts=True
    )

    subject = generate_email_subject(
        topic,
        email_config.get("subject_template")
    )

    # 发送邮件
    return send_email(subject, html_content, email_config, attachments)


async def main():
    """测试邮件发送"""
    import sys
    import json

    # 测试数据
    test_result = {
        "notebook_id": "test-123",
        "notebook_title": "Test Research",
        "topic": "AI Chip Design",
        "mode": "deep",
        "sources_found": 10,
        "sources_imported": 8,
        "report": "这是一份测试研究报告摘要...",
        "all_sources": [
            {"title": f"Test Paper {i}", "type": "URL", "url": f"https://example.com/{i}"}
            for i in range(5)
        ]
    }

    test_artifacts = {
        "artifacts": {
            "slide_deck": {"completed": True},
            "audio": {"completed": True},
            "report": {"completed": False}
        }
    }

    # 检查是否配置了密码
    if not os.environ.get("EMAIL_PASSWORD"):
        print("ERROR: EMAIL_PASSWORD environment variable not set")
        print("Please set it to your QQ email authorization code")
        print("\nTo get your authorization code:")
        print("1. Go to mail.qq.com")
        print("2. Settings -> Account")
        print("3. Enable SMTP service and generate authorization code")
        sys.exit(1)

    # 发送邮件
    success = await send_research_email(
        topic="Test Research",
        research_result=test_result,
        artifacts=test_artifacts
    )

    if success:
        print("Email sent successfully!")
    else:
        print("Failed to send email. Check logs for details.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
