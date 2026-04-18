# 报告比较功能

报告比较功能可以对比新生成的报告和上一次生成的报告，高亮显示差异和重复部分。

## 功能特点

- **段落级比较**：使用 `difflib` 按段落分割并比较相似度
- **智能分类**：自动识别新增、删除、修改和重复的内容
- **可视化摘要**：生成比较摘要，显示各类内容的数量
- **Markdown 笔记**：自动生成比较笔记并保存到 Obsidian

## 使用方法

### 基本用法

在运行工作流时添加 `--compare` 参数：

```bash
cd notebooklm-workflow/scripts
python3 workflow_main.py "你的研究主题" --compare
```

### 完整示例

```bash
# 运行研究并比较
python3 workflow_main.py "low cost inference chip design" --compare --send-email

# 从预配置主题运行并比较
python3 workflow_main.py --topic "AI-Chip" --compare

# 从今日推荐处理并比较
python3 workflow_main.py --from-recommended --top 3 --compare
```

### 仅比较模式

如果只想进行比较而不执行新的研究（用于测试）：

```bash
python3 workflow_main.py --compare-only
```

## 比较逻辑

### 相似度阈值

系统使用文本相似度算法来分类内容：

| 相似度 | 分类 | 说明 |
|--------|------|------|
| ≥ 60% | 重复 | 内容基本相同 |
| 30% - 60% | 修改 | 内容有变化但保留部分原文 |
| < 30% | 新增 | 全新内容 |
| 未匹配 | 删除 | 上次报告中有，本次没有 |

### 比较流程

```
1. 从数据库读取上一次的报告
2. 将新旧报告按段落分割
3. 计算每个新段落与所有旧段落的相似度
4. 根据阈值分类（新增/修改/重复/删除）
5. 生成比较摘要和详细笔记
```

## 输出结果

### 1. 终端输出

工作流完成后会显示比较摘要：

```
--- Report Comparison ---
## 报告比较摘要

- 新报告段落数：25
- 旧报告段落数：22
- 新增内容：8 段
- 删除内容：5 段
- 修改内容：7 段
- 重复内容：10 段

- 内容变化比例：60.0%

### 新增内容
1. 新增的第一段内容...
2. 新增的第二段内容...
...
```

### 2. Obsidian 报告

生成两份独立的报告：

**完整报告**：`{Vault}/NotebookLM/Exports/{日期}_{主题}.md`
- 包含完整的研究结果、来源文献、生成的内容
- 标准的研究报告格式

**比较报告**：`{Vault}/NotebookLM/Exports/Comparisons/{主题}_comparison_{日期}.md`
- 专注于与上一次报告的差异
- 包含：
  - 比较摘要统计
  - 重复内容列表（相似度≥60%）
  - 修改内容列表（相似度 30%-60%）
  - 全新内容列表（相似度<30%）
  - 删除内容列表

### 3. 邮件报告

发送两封独立的邮件：

**邮件 1：完整报告**
- 主题：`[NotebookLM 研究报告] {主题}`
- 内容：完整的研究摘要、来源文献列表、生成的内容

**邮件 2：比较报告**
- 主题：`[NotebookLM 报告比较] {主题}`
- 内容：
  - 统计看板（新增/修改/重复/删除数量）
  - 内容变化比例
  - 新增内容详情（绿色高亮）
  - 修改内容详情（黄色高亮，显示新旧对比）
  - 重复内容列表（灰色）
  - 删除内容列表（红色高亮）

## 配置选项

### 调整相似度阈值

编辑 `report_comparator.py`：

```python
comparison_result = comparator.compare_reports(
    new_report=new_report,
    old_report=old_report,
    similarity_threshold=0.6  # 修改此值
)
```

推荐范围：0.5 - 0.7

- **降低阈值**（如 0.5）：更严格，更多内容会被分类为"修改"而非"重复"
- **提高阈值**（如 0.7）：更宽松，更多内容会被分类为"重复"

## 技术实现

### 核心模块

`notebooklm-workflow/scripts/report_comparator.py`

主要方法：
- `compare_reports()` - 比较两个报告
- `_compare_paragraphs()` - 段落级比较
- `_generate_summary()` - 生成摘要
- `generate_diff_html()` - 生成 HTML 差异视图
- `generate_comparison_note()` - 生成 Markdown 比较笔记

### 数据存储

报告历史存储在 SQLite 数据库中：
- 路径：`~/.notebooklm/workflow.db`
- 表：`execution_logs`
- 字段：`artifacts` (JSON 格式，包含 report content)

## 故障排查

### Q: 提示 "No previous report found"

**原因**：数据库中没有该主题的上一次报告

**解决**：
- 首次运行该主题时会出现此提示，属于正常现象
- 运行一次完整工作流后，下次即可比较

### Q: 比较结果不准确

**可能原因**：
1. 阈值设置不合适
2. 报告格式差异过大

**解决**：
- 调整 `similarity_threshold` 参数
- 确保报告格式一致

### Q: 比较笔记没有保存

**原因**：可能 `--no-export` 参数被使用

**解决**：
- 确保不使用 `--no-export` 参数
- 检查 Obsidian Vault 路径配置

## 使用场景

### 1. 追踪研究进展

每周运行同一主题的研究，通过比较功能追踪：
- 哪些内容是新增的研究发现
- 哪些内容被更新或 refined
- 哪些早期发现不再相关

### 2. 避免重复内容

在生成新报告前比较，识别：
- 重复的背景介绍
- 重复的方法描述
- 需要更新的实验结果

### 3. 邮件报告增量更新

通过邮件中的比较摘要，快速了解：
- 本次研究的新发现
- 与上次相比的主要变化
- 是否有必要深入阅读完整报告

## 最佳实践

1. **定期运行**：建议每周或每两周运行一次同一主题
2. **保留比较笔记**：比较笔记是宝贵的研究演进记录
3. **关注变化比例**：变化比例过低可能意味着研究进入平台期
4. **结合邮件功能**：比较摘要通过邮件发送，方便快速浏览

## 相关文件

- `notebooklm-workflow/scripts/report_comparator.py` - 比较核心模块
- `notebooklm-workflow/scripts/workflow_main.py` - 主工作流（集成比较）
- `notebooklm-workflow/scripts/workflow_db.py` - 数据库模块（存储报告历史）
- `notebooklm-workflow/scripts/send_email.py` - 邮件模块（发送比较摘要）

---

*最后更新：2026-04-18*
