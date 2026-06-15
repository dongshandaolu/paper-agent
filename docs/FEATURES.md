# Paper Agent - 功能分析汇总

> [架构](ARCHITECTURE.md) | [流程](FLOWS.md)

## 1. 功能全景（8 类）

| # | 能力 | 说明 |
|---|------|------|
| 1 | PDF 上传与索引 | 持久化论文库 |
| 2 | 论文结构总结 | IMRaD + 阅读指南 |
| 3 | 研究问题提取 | 主/子问题 + 假设 |
| 4 | 术语解释 | RAG + 通俗释义 |
| 5 | RAG 问答 | 引用 + 反思 |
| 6 | 标准阅读报告 | IMRaD + 批判 |
| 7 | 完整阅读报告 | +结构+问题+术语 |
| 8 | 多篇对比 | 矩阵 + 评述 |

## 2. CLI 命令

| 命令 | 功能 |
|------|------|
| `upload` | 上传并索引 |
| `structure` | 结构总结 |
| `questions` | 研究问题 |
| `terms` | 术语解释 |
| `ask` | RAG 问答 |
| `read` | 标准报告 |
| `read --full` | 完整报告 |
| `compare` | 多篇对比 |
| `mcp` | 启动 MCP |

## 3. MCP 工具

`upload_paper` | `upload_paper_content` | `list_papers` | `get_paper_info` | `summarize_structure` | `extract_research_questions` | `explain_terms` | `ask_paper` | `read_paper` | `compare_papers`

## 4. 能力矩阵

| 能力 | CLI | MCP | LangGraph |
|------|:---:|:---:|:---:|
| 上传 | Y | Y | N |
| 结构 | Y | Y | N |
| 问答 | Y | Y | Y |
| 报告 | Y | Y | Y |
| 对比 | Y | Y | Y |
| 跨论文 QA | N | N | - |

## 5. Agent 要点

- **Analyst**: Map-Reduce IMRaD
- **Critic**: 四维评分（创新/严谨/实验/可复现）
- **QA**: Hybrid + RCS + Citation Verifier
- **Reflection**: 最多 2 轮重试

## 6. 配置项

`OPENAI_API_BASE` | `OPENAI_API_KEY` | `MODEL_NAME` | `EMBEDDING_PROVIDER` | `RCS_TOP_K` | `RCS_FINAL_K` | `MAX_REFLECT_ITERATIONS` | `CHUNK_SIZE`

## 7. 已知限制

- 无跨论文 QA
- paper_id = 路径哈希
- 复杂 PDF 解析有限
