# -*- coding: utf-8 -*-
"""Regenerate docs/*.md with UTF-8. All Chinese via U() helper."""
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"


def U(s: str) -> str:
    return s.encode("utf-8").decode("unicode_escape") if "\\u" in s else s


def write_md(name: str, content: str) -> None:
    path = DOCS / name
    path.write_text(content, encoding="utf-8", newline="\n")
    text = path.read_text(encoding="utf-8")
    if name != "README.md":
        assert any("\u4e00" <= c <= "\u9fff" for c in text), f"{name} missing Chinese"
    print(f"OK {name} ({len(text)} chars)")


def gen_readme() -> str:
  u = U
  return f"""# Paper Agent {u("\u6587\u6863\u4e2d\u5fc3")}

{u("\u672c\u76ee\u5f55\u5305\u542b Paper Agent \u9879\u76ee\u7684\u5b8c\u6574\u67b6\u6784\u3001\u6d41\u7a0b\u4e0e\u529f\u80fd\u8bf4\u660e\u3002")}

## {u("\u6587\u6863\u7d22\u5f15")}

| {u("\u6587\u6863")} | {u("\u8bf4\u660e")} |
|------|------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | **{u("\u4e3b\u6587\u6863")}** - {u("\u7cfb\u7edf\u5206\u5c42\u3001\u6280\u672f\u6808\u3001\u6570\u636e\u6a21\u578b\u3001\u914d\u7f6e\u4e0e\u76ee\u5f55\u7ed3\u6784")} |
| [FLOWS.md](FLOWS.md) | **{u("\u6d41\u7a0b\u8be6\u89e3")}** - {u("5 \u79cd LangGraph \u5de5\u4f5c\u6d41\u3001\u8def\u7531\u903b\u8f91\u3001\u7aef\u5230\u7aef\u65f6\u5e8f")} |
| [FEATURES.md](FEATURES.md) | **{u("\u529f\u80fd\u6c47\u603b")}** - {u("CLI/MCP \u5168\u529f\u80fd\u5206\u6790\u3001\u80fd\u529b\u77e9\u9635\u3001\u8f93\u5165\u8f93\u51fa\u89c4\u683c")} |

## {u("\u67b6\u6784\u56fe (SVG)")}

| {u("\u56fe\u7247")} | {u("\u5185\u5bb9")} |
|------|------|
| [system-layers.svg](images/system-layers.svg) | {u("\u4e94\u5c42\u7cfb\u7edf\u67b6\u6784")} |
| [data-flow.svg](images/data-flow.svg) | {u("\u7aef\u5230\u7aef\u6570\u636e\u6d41")} |
| [workflow-read.svg](images/workflow-read.svg) | {u("\u6807\u51c6\u9605\u8bfb\u5de5\u4f5c\u6d41")} |
| [workflow-full-read.svg](images/workflow-full-read.svg) | {u("\u5b8c\u6574\u9605\u8bfb\u5de5\u4f5c\u6d41")} |
| [workflow-qa.svg](images/workflow-qa.svg) | {u("\u95ee\u7b54 + \u53cd\u601d\u5faa\u73af")} |
| [workflow-compare.svg](images/workflow-compare.svg) | {u("\u591a\u7bc7\u5bf9\u6bd4\u5de5\u4f5c\u6d41")} |
| [rag-pipeline.svg](images/rag-pipeline.svg) | Agentic RAG {u("\u7ba1\u7ebf")} |

## {u("\u5feb\u901f\u5bfc\u822a")}

- {u("\u5b89\u88c5\u4e0e\u4f7f\u7528")}: [README.md](../README.md)
- {u("\u5b8c\u6574\u793a\u4f8b")}: [tests/USAGE_EXAMPLE.md](../tests/USAGE_EXAMPLE.md)
- MCP {u("\u914d\u7f6e\u793a\u4f8b")}: [.mcp.json.example](../.mcp.json.example)
"""


def gen_architecture() -> str:
    u = U
    return f"""# Paper Agent - {u("\u67b6\u6784\u4e0e\u529f\u80fd\u8bf4\u660e")}

> **{u("\u6587\u6863\u5bfc\u822a")}**：[{u("\u6587\u6863\u4e2d\u5fc3")}](README.md) | [{u("\u6d41\u7a0b\u8be6\u89e3")}](FLOWS.md) | [{u("\u529f\u80fd\u6c47\u603b")}](FEATURES.md)

## 1. {u("\u9879\u76ee\u5b9a\u4f4d")}

Paper Agent {u("\u662f\u57fa\u4e8e")} **LangGraph {u("\u591a Agent \u7f16\u6392")}** {u("\u7684\u4e13\u4e1a\u8bba\u6587\u9605\u8bfb\u7cfb\u7edf\uff0c\u652f\u6301")}：

- **CLI** {u("\u547d\u4ee4\u884c")}（Typer + Rich）
- **MCP Server**（FastMCP，{u("\u4f9b Claude Code / Cursor \u7b49 AI \u7f16\u7a0b\u5de5\u5177\u8c03\u7528")}）

{u("\u6838\u5fc3\u80fd\u529b")}：**PDF {u("\u89e3\u6790")} -> {u("\u7ed3\u6784\u5316\u7406\u89e3")} -> RAG {u("\u95ee\u7b54")} -> {u("\u6279\u5224\u5206\u6790")} -> Markdown {u("\u62a5\u544a")} -> {u("\u591a\u7bc7\u5bf9\u6bd4")}**

---

## 2. {u("\u7cfb\u7edf\u5206\u5c42\u67b6\u6784")}

![{u("\u7cfb\u7edf\u5206\u5c42\u67b6\u6784")}](images/system-layers.svg)

| {u("\u5c42\u7ea7")} | {u("\u6838\u5fc3\u6a21\u5757")} | {u("\u804c\u8d23")} |
|------|---------|------|
| {u("\u5165\u53e3\u5c42")} | `main.py`、`mcp_server.py` | {u("\u53c2\u6570\u89e3\u6790\u3001\u8fdb\u5ea6\u5c55\u793a\u3001MCP \u5de5\u5177\u6ce8\u518c")} |
| {u("\u670d\u52a1\u5c42")} | `paper_service.py`、`registry.py` | {u("\u7edf\u4e00\u4e1a\u52a1 API\u3001\u8bba\u6587\u5e93 CRUD\u3001\u7f13\u5b58")} |
| {u("\u7f16\u6392\u5c42")} | `graph/builder.py`、`router.py` | {u("5 \u79cd\u5de5\u4f5c\u6d41\u56fe\u3001\u6761\u4ef6\u8def\u7531")} |
| Agent {u("\u5c42")} | `agents/*.py` | {u("\u4e13\u4e1a\u5316 LLM \u4efb\u52a1\u8282\u70b9")} |
| {u("\u5de5\u5177\u5c42")} | `tools/*.py` | PDF {u("\u89e3\u6790\u3001\u5206\u5757\u3001\u68c0\u7d22\u3001RCS")} |
| {u("\u6a21\u578b\u5c42")} | `llm.py`、`embeddings.py` | LLM {u("\u8c03\u7528\u3001\u5411\u91cf/TF-IDF \u7d22\u5f15")} |

---

## 3. {u("\u7aef\u5230\u7aef\u6570\u636e\u6d41")}

![{u("\u7aef\u5230\u7aef\u6570\u636e\u6d41")}](images/data-flow.svg)

**paper_id {u("\u89c4\u5219")}**：{u("\u6587\u4ef6\u7edd\u5bf9\u8def\u5f84 SHA256 \u7684\u524d 16 \u4f4d")}（{u("\u975e\u6587\u4ef6\u540d")}）。

---

## 4. LangGraph {u("\u5de5\u4f5c\u6d41")}

{u("\u8be6\u89c1")} [FLOWS.md](FLOWS.md)。

### 4.1 {u("\u6807\u51c6\u9605\u8bfb")} `read`

![{u("\u6807\u51c6\u9605\u8bfb")}](images/workflow-read.svg)

```
START -> parser -> analyst -> critic -> writer -> END
```

### 4.2 {u("\u5b8c\u6574\u9605\u8bfb")} `read --full`

![{u("\u5b8c\u6574\u9605\u8bfb")}](images/workflow-full-read.svg)

```
START -> parser -> structure -> research -> terms -> analyst -> critic -> writer -> END
```

### 4.3 {u("\u95ee\u7b54")} `ask`

![{u("\u95ee\u7b54\u5de5\u4f5c\u6d41")}](images/workflow-qa.svg)

### 4.4 {u("\u591a\u7bc7\u5bf9\u6bd4")} `compare`

![{u("\u591a\u7bc7\u5bf9\u6bd4")}](images/workflow-compare.svg)

---

## 5. Agentic RAG {u("\u7ba1\u7ebf")}

![Agentic RAG](images/rag-pipeline.svg)

---

## 6. Agent {u("\u804c\u8d23\u8868")}

| Agent | {u("\u6587\u4ef6")} | {u("\u804c\u8d23")} |
|-------|------|------|
| ParserAgent | `agents/parser.py` | PDF {u("\u89e3\u6790\u3001\u5206\u5757\u3001\u5efa\u7d22\u5f15")} |
| StructureAgent | `agents/specialist.py` | {u("\u7ae0\u8282\u5927\u7eb2\u3001IMRaD \u6620\u5c04\u3001\u9605\u8bfb\u6307\u5357")} |
| ResearchAgent | `agents/specialist.py` | {u("\u7814\u7a76\u95ee\u9898\u4e0e\u5047\u8bbe")} |
| TerminologyAgent | `agents/specialist.py` | {u("\u672f\u8bed\u89e3\u91ca")} |
| AnalystAgent | `agents/analyst.py` | Map-Reduce IMRaD {u("\u6458\u8981")} |
| CriticAgent | `agents/critic.py` | {u("\u56db\u7ef4\u6279\u5224\u8bc4\u5206")} |
| QAAgent | `agents/qa.py` | RAG {u("\u95ee\u7b54")} + {u("\u5f15\u7528")} |
| ReflectionAgent | `agents/reflection.py` | {u("\u53cd\u601d\u8bc4\u4f30\u4e0e\u91cd\u8bd5")} |
| ComparerAgent | `agents/comparer.py` | {u("\u591a\u7bc7\u5bf9\u6bd4\u77e9\u9635")} |
| WriterAgent | `agents/writer.py` | Markdown {u("\u62a5\u544a")} |
| CitationVerifier | `agents/citation_verifier.py` | {u("\u5f15\u7528\u9a8c\u8bc1")} |

---

## 7. {u("\u6570\u636e\u6a21\u578b")}

- `PaperDocument` / `Section` / `Chunk` - `models/paper.py`
- `PaperSummary` / `PaperCritique` / `QAAnswer` / `ComparisonResult` - `models/outputs.py`
- `PaperState` - `state.py`（LangGraph {u("\u72b6\u6001")}）

---

## 8. {u("\u5b58\u50a8\u4e0e\u6301\u4e45\u5316")}

| {u("\u8def\u5f84")} | {u("\u5185\u5bb9")} |
|------|------|
| `data/papers/*.pdf` | {u("\u4e0a\u4f20\u7684\u8bba\u6587\u526f\u672c")} |
| `data/papers/index.json` | paper_id {u("\u7d22\u5f15")} |
| `data/chroma/tfidf/*.pkl` | TF-IDF {u("\u7d22\u5f15")} |
| `data/chroma/` | Chroma {u("\u5411\u91cf\u5e93")} |
| `output/` | Markdown {u("\u62a5\u544a")} |

---

## 9. {u("\u529f\u80fd\u4e00\u89c8")}

{u("\u5b8c\u6574\u529f\u80fd\u5206\u6790\u89c1")} [FEATURES.md](FEATURES.md)。

### CLI（9 {u("\u4e2a\u547d\u4ee4")}）

`upload` | `structure` | `questions` | `terms` | `ask` | `read` | `read --full` | `compare` | `mcp`

### MCP（10 {u("\u4e2a\u5de5\u5177")}）

`upload_paper` | `list_papers` | `get_paper_info` | `summarize_structure` | `extract_research_questions` | `explain_terms` | `ask_paper` | `read_paper` | `compare_papers` | `upload_paper_content`

---

## 10. {u("\u6280\u672f\u6808")}

LangGraph | LangChain | PyMuPDF | Chroma + TF-IDF | Pydantic v2 | Typer + Rich | FastMCP | Jinja2

---

## 11. {u("\u5df2\u77e5\u9650\u5236")}

- paper_id {u("\u4e3a\u8def\u5f84\u54c8\u5e0c")}
- {u("\u65e0\u8de8\u8bba\u6587\u8054\u5408 QA")}
- {u("\u5206\u6790\u7ed3\u679c\u9ed8\u8ba4\u4e0d\u6301\u4e45\u5316\u5230\u78c1\u76d8")}
- {u("\u590d\u6742\u6392\u7248 PDF \u89e3\u6790\u7cbe\u5ea6\u6709\u9650")}
- DeepSeek {u("\u81ea\u52a8\u964d\u7ea7")} TF-IDF
"""


def gen_flows() -> str:
    u = U
    return f"""# Paper Agent - {u("\u6d41\u7a0b\u8be6\u89e3")}

> [{u("\u67b6\u6784")}](ARCHITECTURE.md) | [{u("\u529f\u80fd")}](FEATURES.md)

## 1. {u("\u5de5\u4f5c\u6d41\u603b\u89c8")}

| {u("\u56fe")} | {u("\u573a\u666f")} |
|----|------|
| `build_read_graph` | CLI `read` |
| `build_full_read_graph` | `read --full` / MCP `read_paper(full=True)` |
| `build_qa_graph` | CLI `ask` / MCP `ask_paper` |
| `build_compare_graph` | CLI `compare` |
| `build_unified_graph` | {u("\u7edf\u4e00\u56fe\uff08\u542b\u5168\u90e8\u8282\u70b9")} |

## 2. {u("\u6807\u51c6\u9605\u8bfb")}

![read](images/workflow-read.svg)

## 3. {u("\u5b8c\u6574\u9605\u8bfb")}

![full read](images/workflow-full-read.svg)

## 4. {u("\u95ee\u7b54")} + {u("\u53cd\u601d")}

![qa](images/workflow-qa.svg)

{u("\u53cd\u601d\u4e0a\u9650")}: `MAX_REFLECT_ITERATIONS=2`

## 5. {u("\u591a\u7bc7\u5bf9\u6bd4")}

![compare](images/workflow-compare.svg)

## 6. {u("\u8def\u7531\u89c4\u5219")} (`graph/router.py`)

| {u("\u51fd\u6570")} | {u("\u6761\u4ef6")} | {u("\u76ee\u6807")} |
|------|------|------|
| `route_after_parse` | task=qa | qa |
| | full_read | structure |
| | {u("\u9ed8\u8ba4")} | analyst |
| `route_after_analyst` | task=compare | comparer |
| | {u("\u9ed8\u8ba4")} | critic |
| `route_after_reflection` | {u("\u672a\u901a\u8fc7\u4e14\u672a\u8d85\u9650")} | qa |
| | {u("\u5426\u5219")} | end |

## 7. {u("\u6570\u636e\u6d41")}

![data flow](images/data-flow.svg)
"""


def gen_features() -> str:
    u = U
    return f"""# Paper Agent - {u("\u529f\u80fd\u5206\u6790\u6c47\u603b")}

> [{u("\u67b6\u6784")}](ARCHITECTURE.md) | [{u("\u6d41\u7a0b")}](FLOWS.md)

## 1. {u("\u529f\u80fd\u5168\u666f")}（8 {u("\u7c7b")}）

| # | {u("\u80fd\u529b")} | {u("\u8bf4\u660e")} |
|---|------|------|
| 1 | PDF {u("\u4e0a\u4f20\u4e0e\u7d22\u5f15")} | {u("\u6301\u4e45\u5316\u8bba\u6587\u5e93")} |
| 2 | {u("\u8bba\u6587\u7ed3\u6784\u603b\u7ed3")} | IMRaD + {u("\u9605\u8bfb\u6307\u5357")} |
| 3 | {u("\u7814\u7a76\u95ee\u9898\u63d0\u53d6")} | {u("\u4e3b/\u5b50\u95ee\u9898 + \u5047\u8bbe")} |
| 4 | {u("\u672f\u8bed\u89e3\u91ca")} | RAG + {u("\u901a\u4fd7\u91ca\u4e49")} |
| 5 | RAG {u("\u95ee\u7b54")} | {u("\u5f15\u7528")} + {u("\u53cd\u601d")} |
| 6 | {u("\u6807\u51c6\u9605\u8bfb\u62a5\u544a")} | IMRaD + {u("\u6279\u5224")} |
| 7 | {u("\u5b8c\u6574\u9605\u8bfb\u62a5\u544a")} | +{u("\u7ed3\u6784")}+{u("\u95ee\u9898")}+{u("\u672f\u8bed")} |
| 8 | {u("\u591a\u7bc7\u5bf9\u6bd4")} | {u("\u77e9\u9635")} + {u("\u8bc4\u8ff0")} |

## 2. CLI {u("\u547d\u4ee4")}

| {u("\u547d\u4ee4")} | {u("\u529f\u80fd")} |
|------|------|
| `upload` | {u("\u4e0a\u4f20\u5e76\u7d22\u5f15")} |
| `structure` | {u("\u7ed3\u6784\u603b\u7ed3")} |
| `questions` | {u("\u7814\u7a76\u95ee\u9898")} |
| `terms` | {u("\u672f\u8bed\u89e3\u91ca")} |
| `ask` | RAG {u("\u95ee\u7b54")} |
| `read` | {u("\u6807\u51c6\u62a5\u544a")} |
| `read --full` | {u("\u5b8c\u6574\u62a5\u544a")} |
| `compare` | {u("\u591a\u7bc7\u5bf9\u6bd4")} |
| `mcp` | {u("\u542f\u52a8 MCP")} |

## 3. MCP {u("\u5de5\u5177")}

`upload_paper` | `upload_paper_content` | `list_papers` | `get_paper_info` | `summarize_structure` | `extract_research_questions` | `explain_terms` | `ask_paper` | `read_paper` | `compare_papers`

## 4. {u("\u80fd\u529b\u77e9\u9635")}

| {u("\u80fd\u529b")} | CLI | MCP | LangGraph |
|------|:---:|:---:|:---:|
| {u("\u4e0a\u4f20")} | Y | Y | N |
| {u("\u7ed3\u6784")} | Y | Y | N |
| {u("\u95ee\u7b54")} | Y | Y | Y |
| {u("\u62a5\u544a")} | Y | Y | Y |
| {u("\u5bf9\u6bd4")} | Y | Y | Y |
| {u("\u8de8\u8bba\u6587 QA")} | N | N | - |

## 5. Agent {u("\u8981\u70b9")}

- **Analyst**: Map-Reduce IMRaD
- **Critic**: {u("\u56db\u7ef4\u8bc4\u5206")}（{u("\u521b\u65b0/\u4e25\u8c28/\u5b9e\u9a8c/\u53ef\u590d\u73b0")}）
- **QA**: Hybrid + RCS + Citation Verifier
- **Reflection**: {u("\u6700\u591a 2 \u8f6e\u91cd\u8bd5")}

## 6. {u("\u914d\u7f6e\u9879")}

`OPENAI_API_BASE` | `OPENAI_API_KEY` | `MODEL_NAME` | `EMBEDDING_PROVIDER` | `RCS_TOP_K` | `RCS_FINAL_K` | `MAX_REFLECT_ITERATIONS` | `CHUNK_SIZE`

## 7. {u("\u5df2\u77e5\u9650\u5236")}

- {u("\u65e0\u8de8\u8bba\u6587 QA")}
- paper_id = {u("\u8def\u5f84\u54c8\u5e0c")}
- {u("\u590d\u6742 PDF \u89e3\u6790\u6709\u9650")}
"""


def main() -> None:
    write_md("README.md", gen_readme())
    write_md("ARCHITECTURE.md", gen_architecture())
    write_md("FLOWS.md", gen_flows())
    write_md("FEATURES.md", gen_features())


if __name__ == "__main__":
    main()
