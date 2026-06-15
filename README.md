# Paper Agent

基于 LangGraph 的多 Agent 专业论文阅读系统，支持 **CLI** 与 **MCP**（Claude Code / Cursor 等 AI 编程工具）两种调用方式。

> 完整文档见 **[docs/README.md](docs/README.md)**（架构 · 流程图 · 功能汇总）

## 功能

| 能力 | CLI | MCP Tool |
|------|-----|----------|
| 上传 PDF | `upload` | `upload_paper` / `upload_paper_content` |
| 论文结构总结 | `structure` | `summarize_structure` |
| 提取研究问题 | `questions` | `extract_research_questions` |
| 解释专业术语 | `terms` | `explain_terms` |
| RAG 问答 | `ask` | `ask_paper` |
| 完整阅读报告 | `read` | `read_paper` |
| 多篇对比 | `compare` | `compare_papers` |

## 安装

```bash
pip install -e .
cp .env.example .env
# 编辑 .env 填入 API 配置
```

## CLI 使用

```bash
# 上传论文，获取 paper_id
paper-agent upload paper.pdf

# 结构总结 / 研究问题 / 术语解释
paper-agent structure <paper_id>
paper-agent questions <paper_id>
paper-agent terms <paper_id>
paper-agent terms <paper_id> -t Transformer -t "self-attention"

# 标准阅读
paper-agent read tests\attention.pdf -o output\attention

# 完整报告（结构 + 研究问题 + 术语 + 摘要 + 批判）
paper-agent read tests\attention.pdf --full -o output\attention
paper-agent ask "核心方法是什么？" --paper paper.pdf
paper-agent compare paper_a.pdf paper_b.pdf
```

## 在 Claude Code / Cursor 中使用（MCP）

### 1. 配置 MCP Server

复制示例配置并按需修改 API Key：

```bash
cp .mcp.json.example .mcp.json
```

**Claude Code**（项目根目录 `.mcp.json`）：

```json
{
  "mcpServers": {
    "paper-agent": {
      "command": "paper-agent-mcp",
      "env": {
        "OPENAI_API_BASE": "https://api.deepseek.com/v1",
        "OPENAI_API_KEY": "your-api-key",
        "MODEL_NAME": "deepseek-chat"
      }
    }
  }
}
```

**Cursor**（Settings → MCP → Add Server，或 `.cursor/mcp.json`）使用相同配置。

### 2. 在对话中使用

配置完成后，AI 助手可自动调用 MCP 工具，例如：

> 请阅读 `f:/papers/transformer.pdf`，总结论文结构并解释其中的专业术语。

Agent 将依次调用 `upload_paper` → `summarize_structure` → `explain_terms`。

### 3. MCP 工具一览

- `upload_paper(pdf_path)` — 上传本地 PDF，返回 `paper_id`
- `upload_paper_content(filename, content_base64)` — Base64 上传
- `list_papers()` — 列出已索引论文
- `summarize_structure(paper_id)` — 章节大纲 + IMRaD 映射
- `extract_research_questions(paper_id)` — 研究问题与假设
- `explain_terms(paper_id, terms?, max_terms?)` — 术语解释
- `ask_paper(paper_id, question)` — 带引用的问答
- `read_paper(paper_id)` — 完整阅读报告
- `compare_papers(paper_ids)` — 多篇对比

也可手动启动 MCP Server：

```bash
paper-agent mcp
# 或
paper-agent-mcp
```

## 配置

| 变量 | 说明 |
|------|------|
| `OPENAI_API_BASE` | OpenAI 兼容 API 地址 |
| `OPENAI_API_KEY` | API Key |
| `MODEL_NAME` | 对话模型 |
| `EMBEDDING_MODEL` | Embedding 模型（仅 `openai` 模式） |
| `EMBEDDING_PROVIDER` | `auto` / `tfidf` / `openai` / `local`（DeepSeek 用户保持 `auto` 即可） |
| `CHROMA_PERSIST_DIR` | 向量库持久化目录 |
| `PAPERS_DIR` | 上传论文存储目录 |
| `RETRIEVAL_TOP_K` | 检索返回数量 |
| `RCS_TOP_K` / `RCS_FINAL_K` | RCS 初筛/精排数量 |
| `RETRIEVAL_MODE` | `hybrid`（章节优先+全局） |
| `MAX_REFLECT_ITERATIONS` | QA 反思最大重试次数 |

## 完整示例

以 `tests/attention.pdf`（Transformer 原论文）为例的 **CLI + MCP 全流程** 见：

👉 **[tests/USAGE_EXAMPLE.md](tests/USAGE_EXAMPLE.md)**

快速一键运行（需有效 API Key）：

```powershell
.\tests\run_attention_example.ps1
```
