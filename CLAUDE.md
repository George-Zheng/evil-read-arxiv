# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**evil-read-arxiv** is a Claude Code Skills collection for automated paper research workflow:
- Search arXiv and Semantic Scholar for papers
- Generate daily recommendations with scoring
- Deep analysis and note generation
- Image extraction from papers
- Conference paper search (CVPR/ICCV/ICLR/etc.)
- **New**: NotebookLM integration for deep research, artifact generation, and email reports

## Repository Structure

```
evil-read-arxiv/
├── config.example.yaml         # Configuration template
├── requirements.txt            # Python dependencies
├── README.md                   # Main documentation
├── QUICKSTART.md               # Quick start guide
│
├── start-my-day/               # Daily paper recommendations
│   ├── SKILL.md
│   └── scripts/
│       ├── search_arxiv.py     # arXiv + S2 search
│       ├── scan_existing_notes.py
│       └── link_keywords.py
│
├── conf-papers/                # Conference paper search
│   ├── SKILL.md
│   ├── conf-papers.yaml        # Conference-specific config
│   └── scripts/
│       └── search_conf_papers.py  # DBLP + S2 search
│
├── paper-analyze/              # Paper deep analysis
│   ├── SKILL.md
│   └── scripts/
│       ├── generate_note.py    # Generate markdown note
│       └── update_graph.py     # Update knowledge graph
│
├── extract-paper-images/       # Image extraction
│   ├── SKILL.md
│   └── scripts/
│       └── extract_images.py
│
├── paper-search/               # Search existing papers
│   └── SKILL.md
│
└── notebooklm-workflow/        # NEW: NotebookLM integration
    ├── SKILL.md
    └── scripts/
        ├── workflow_main.py        # Main workflow entry
        ├── notebooklm_client.py    # NotebookLM API wrapper
        ├── deep_research.py        # Deep Research integration
        ├── generate_artifacts.py   # Slide/Audio/Report generation
        ├── export_to_obsidian.py   # Markdown export
        ├── send_email.py           # Email sending (QQ SMTP)
        └── workflow_db.py          # SQLite tracking
```

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run individual scripts
python start-my-day/scripts/search_arxiv.py --config config.yaml
python paper-analyze/scripts/generate_note.py --vault /path/to/vault --paper-id 2402.12345
python notebooklm-workflow/scripts/workflow_main.py "research topic"

# Test NotebookLM workflow
python notebooklm-workflow/scripts/workflow_main.py "test topic" --dry-run
```

## Key Configuration Files

### config.example.yaml
Main configuration file for research domains, keywords, arXiv categories, and NotebookLM/email settings.

### conf-papers/conf-papers.yaml
Conference paper skill specific configuration (keywords, excluded keywords, default year/conferences).

### notebooklm-workflow/SKILL.md
Complete documentation for the NotebookLM workflow skill.

## NotebookLM Integration

The `notebooklm-workflow/` directory provides:

1. **Deep Research**: Uses NotebookLM's research API to discover papers
2. **Artifact Generation**: Generates Slide Deck, Audio Overview, Report
3. **Obsidian Export**: Creates markdown notes with research summaries
4. **Email Reports**: Sends HTML email via QQ SMTP

### Usage Example

```bash
# Run research workflow
python notebooklm-workflow/scripts/workflow_main.py "low cost inference chip"

# With email report
python notebooklm-workflow/scripts/workflow_main.py "KV cache compression" --send-email

# Dry run (no execution)
python notebooklm-workflow/scripts/workflow_main.py "test" --dry-run
```

### Prerequisites

1. **NotebookLM Authentication**:
   ```bash
   notebooklm login
   notebooklm status
   ```

2. **Email Configuration** (QQ email):
   - Set `EMAIL_PASSWORD` env var to your QQ authorization code
   - Configure recipients in `config.example.yaml`

3. **Obsidian Vault**:
   - Set `OBSIDIAN_VAULT_PATH` env var

## Conference List Configuration

To modify the list of conferences in `conf-papers`:

Edit `conf-papers/conf-papers.yaml`:
```yaml
default_conferences:
  - "CVPR"
  - "ICCV"
  - "ECCV"
  - "ICLR"
  - "NeurIPS"
  - "ICML"
  - "AAAI"
  - "ACL"
  - "EMNLP"
  - "IROS"
  - "RSS"
  - "CoRL"
```

## Scoring System

### start-my-day (Daily Recommendations)
| Dimension | Weight |
|-----------|--------|
| Relevance | 40% |
| Recency | 20% |
| Popularity | 30% |
| Quality | 10% |

### conf-papers (Conference Papers)
| Dimension | Weight |
|-----------|--------|
| Relevance | 40% |
| Popularity | 40% |
| Quality | 20% |

(Note: No recency since year is user-specified)

## Important Notes

1. **Environment Variables**: All scripts use `OBSIDIAN_VAULT_PATH` for vault path
2. **Language**: Configurable via `language` in config (zh/en)
3. **Rate Limiting**: Semantic Scholar API may rate limit; add delays between requests
4. **NotebookLM API**: Uses unofficial RPC API that can change without notice

## Testing Checklist

Before committing changes:
```bash
# 1. Check Python syntax
python -m py_compile scripts/*.py

# 2. Test arXiv search
python start-my-day/scripts/search_arxiv.py --config config.yaml --top-n 5

# 3. Test NotebookLM workflow (dry-run)
python notebooklm-workflow/scripts/workflow_main.py "test" --dry-run
```

## Common Issues

1. **"NotebookLM client not connected"**: Run `notebooklm login` first
2. **"EMAIL_PASSWORD not set"**: Set env var to QQ email authorization code
3. **"Vault path not found"**: Set `OBSIDIAN_VAULT_PATH` environment variable
4. **arXiv API rate limit**: Add delays between requests in search scripts
