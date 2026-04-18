---
name: notebooklm-workflow
description: NotebookLM 自动化研究工作流 - 深度研究、内容生成、Obsidian 导出和邮件报告
---

# NotebookLM Workflow Skill

自动化论文研究、分析和整理工作流。集成 NotebookLM Deep Research 功能，生成 Slide/Audio/Report，导出到 Obsidian，并发送邮件报告。

## 语言设置

本 skill 支持中英文报告。语言由配置文件中的 `language` 字段决定：

- **中文（默认）**: `language: "zh"`
- **英文**: `language: "en"`

配置文件位置：`$OBSIDIAN_VAULT_PATH/99_System/Config/research_interests.yaml`

---

## 工作流程

### 概述

```
用户触发 → Deep Research → 生成 Artifact → 导出 Obsidian → 发送邮件
```

### 详细步骤

1. **Deep Research**: 使用 NotebookLM 研究功能搜索和整理论文
2. **Artifact 生成**: 生成 Slide Deck、Audio Overview、Report
3. **Obsidian 导出**: 生成 Markdown 笔记并保存到 Vault
4. **邮件发送**: 发送 HTML 格式的研究摘要到指定邮箱

---

## 配置

### 步骤 1：设置环境变量

```bash
# macOS/Linux（添加到 ~/.zshrc 或 ~/.bashrc）
export OBSIDIAN_VAULT_PATH="/Users/yourname/Documents/Obsidian Vault"

# Windows PowerShell
$env:OBSIDIAN_VAULT_PATH = "C:/Users/YourName/Documents/Obsidian Vault"
```

### 步骤 2：配置 NotebookLM 认证

```bash
# 首次使用需要登录 NotebookLM
notebooklm login

# 验证登录状态
notebooklm status
```

### 步骤 3：配置邮件（可选）

获取 QQ 邮箱授权码：
1. 登录 https://mail.qq.com
2. 设置 → 账户
3. 开启 SMTP 服务
4. 生成授权码

设置环境变量：
```bash
export EMAIL_PASSWORD="your-authorization-code"
```

### 步骤 4：创建配置文件

复制并修改配置模板：
```bash
cp config.example.yaml "$OBSIDIAN_VAULT_PATH/99_System/Config/research_interests.yaml"
```

---

## 使用方法

### 1. 运行自定义主题研究

```bash
notebooklm-workflow "low cost inference chip design"
```

### 2. 使用预配置主题

```bash
notebooklm-workflow --topic "AI-Chip"
```

### 3. 从今日推荐处理

```bash
notebooklm-workflow --from-recommended --top 3
```

### 4. 指定研究模式

```bash
# 深度研究（更全面的来源发现）
notebooklm-workflow "KV cache compression" --mode deep

# 快速研究
notebooklm-workflow "speculative inference" --mode fast
```

### 5. 发送邮件报告

```bash
notebooklm-workflow "embodied AI chip" --send-email
```

### 6. 仅生成特定内容

```bash
# 只生成 Slide
notebooklm-workflow "AI chip" --generate slide

# 生成 Slide 和 Audio
notebooklm-workflow "AI chip" --generate slide audio

# 生成所有内容（默认）
notebooklm-workflow "AI chip" --generate all
```

### 7. 自定义 Notebook 管理

```bash
# 指定 Notebook 前缀
notebooklm-workflow "Research" --notebook-prefix "Chip-Archive"

# 指定轮换策略
notebooklm-workflow "Research" --rotation monthly
```

---

## 完整命令参考

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `topic` | 研究主题（必填其一） | - |
| `--topic` | 从配置读取的主题名 | - |
| `--from-recommended` | 从今日推荐获取 | false |
| `--mode` | 研究模式 (deep/fast) | deep |
| `--max-sources` | 最大来源数 | 20 |
| `--research-timeout` | 研究超时（秒） | 600 |
| `--notebook-prefix` | Notebook 标题前缀 | Research |
| `--rotation` | Notebook 轮换 (quarterly/monthly/weekly) | quarterly |
| `--generate` | 生成内容 (slide/audio/report/all) | all |
| `--artifact-timeout` | Artifact 超时（秒） | 600 |
| `--vault` | Obsidian Vault 路径 | 环境变量 |
| `--export-folder` | 导出文件夹 | NotebookLM/Exports |
| `--no-export` | 不导出到 Obsidian | false |
| `--send-email` | 发送邮件报告 | false |
| `--dry-run` | 只打印计划不执行 | false |
| `--verbose` | 详细输出 | false |

---

## 输出结构

### Obsidian 目录结构

```
你的 Vault/
├── 10_Daily/
│   └── YYYY-MM-DD_论文推荐.md
├── 20_Research/
│   └── Papers/
│       └── 大模型/
│           └── 论文标题.md
├── 99_System/
│   └── Config/
│       └── research_interests.yaml
└── NotebookLM/              # 新增
    ├── Exports/             # 研究报告
    │   └── 2026-01-18_主题.md
    └── artifacts/           # 生成的内容（可选）
        ├── slide_deck.pdf
        ├── audio.mp3
        └── report.md
```

### 生成的 Markdown 笔记结构

```markdown
---
created: "2026-01-18"
source: NotebookLM
topic: "AI Chips Low-Cost Inference"
notebook_id: "xxx-xxx-xxx"
tags:
  - notebooklm
  - research
  - ai-chip
---

# 研究报告：AI Chips Low-Cost Inference

## 基本信息
- **研究主题**: AI Chips Low-Cost Inference
- **生成时间**: 2026-01-18 12:00
- **Notebook ID**: `xxx-xxx-xxx`
- **研究模式**: deep

## 来源文献
| 标题 | 类型 | 链接 |
|------|------|------|
| Paper 1 | URL | [链接](https://...) |
...

## 研究报告
[NotebookLM 生成的研究报告]

## 生成的内容
- ✓ Slide Deck: `./exports/slide_deck.pdf`
- ✓ Audio Overview: `./exports/audio.mp3`
- ○ Report: `./exports/report.md`

## 关键发现
*[从 NotebookLM 对话中提取]*

## 后续行动
1. [ ] 审阅生成的 Slide Deck
2. [ ] 收听 Audio Overview
3. [ ] 整理关键发现

---
*由 notebooklm-workflow 自动生成*
```

### 邮件报告结构

HTML 格式邮件包含：
- 研究摘要
- 来源文献列表（前 15 篇）
- 生成内容状态
- Notebook 链接

---

## 配置示例

### config.example.yaml

```yaml
# 语言设置
language: "zh"

# Obsidian Vault 路径
vault_path: "/Users/yourname/Documents/Obsidian Vault"

# 研究领域配置
research_domains:
  "AI Chips Low-Cost Inference":
    keywords:
      - "low cost inference"
      - "quantization"
      - "pruning"
      - "KV cache compression"
      - "speculative inference"
      - "Diffusion LLM"
    arxiv_categories:
      - "cs.AI"
      - "cs.LG"
      - "cs.AR"
    priority: 10

  "Embodied AI Algorithms":
    keywords:
      - "embodied AI"
      - "robot learning"
      - "foundation model robotics"
    arxiv_categories:
      - "cs.RO"
      - "cs.AI"
    priority: 9

# NotebookLM 配置
notebooklm:
  enabled: true
  auth_method: "storage_state"
  storage_path: "~/.notebooklm/storage_state.json"

  notebook_naming: "{topic}-{year}-{quarter}"
  rotation: "quarterly"

  deep_research:
    mode: "deep"
    timeout: 600
    max_sources: 20
    auto_import: true

  generate:
    slide_deck:
      enabled: true
      format: "pdf"
    audio:
      enabled: true
      language: "en"
    report:
      enabled: true
      format: "briefing-doc"

  obsidian:
    vault_path: "/Users/yourname/Documents/Obsidian Vault"
    folder: "NotebookLM/Exports"
    include_sources: true

# 邮件配置
email:
  enabled: true
  smtp_server: "smtp.qq.com"
  smtp_port: 587
  sender: "qiaoshi.zheng@foxmail.com"
  recipients:
    - "zhengqiaoshi@huawei.com"
  use_ssl: true
  username: "qiaoshi.zheng@foxmail.com"
  # password: 从 EMAIL_PASSWORD 环境变量读取

  subject_template: "[NotebookLM Research] {topic} - {date}"
  send_on_completion: true
```

---

## 常见问题

### Q: 认证失败？
A: 运行 `notebooklm login` 重新认证

### Q: 研究超时？
A: 增加 `--research-timeout` 参数，deep 模式可能需要 10-15 分钟

### Q: 邮件发送失败？
A: 检查 EMAIL_PASSWORD 是否设置为 QQ 邮箱授权码（不是登录密码）

### Q: 如何查看已处理论文？
A: 查看数据库：`~/.notebooklm/workflow.db`

### Q: 如何更改生成内容类型？
A: 修改配置文件中的 `notebooklm.generate` 部分

---

## 脚本说明

| 脚本 | 功能 |
|------|------|
| `workflow_main.py` | 主入口，整合所有步骤 |
| `notebooklm_client.py` | NotebookLM API 封装 |
| `deep_research.py` | Deep Research 集成 |
| `generate_artifacts.py` | Slide/Audio/Report 生成 |
| `export_to_obsidian.py` | Obsidian Markdown 导出 |
| `send_email.py` | 邮件发送（QQ SMTP） |
| `workflow_db.py` | SQLite 论文追踪 |

---

## 依赖

```bash
pip install notebooklm-py PyYAML requests
```

---

## 与其他 Skill 集成

### 与 start-my-day 集成

```bash
# 先运行每日推荐
start my day

# 然后处理推荐的论文
notebooklm-workflow --from-recommended --top 3
```

### 与 paper-analyze 集成

```bash
# 先分析论文
paper-analyze 2402.12345

# 然后上传到 NotebookLM 深度研究
notebooklm-workflow "论文主题" --mode deep
```

---

*最后更新：2026-01-18*
