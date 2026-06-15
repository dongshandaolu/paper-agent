# Paper Agent - 流程详解

> [架构](ARCHITECTURE.md) | [功能](FEATURES.md)

## 1. 工作流总览

| 图 | 场景 |
|----|------|
| `build_read_graph` | CLI `read` |
| `build_full_read_graph` | `read --full` / MCP `read_paper(full=True)` |
| `build_qa_graph` | CLI `ask` / MCP `ask_paper` |
| `build_compare_graph` | CLI `compare` |
| `build_unified_graph` | 统一图（含全部节点 |

## 2. 标准阅读

![read](images/workflow-read.svg)

## 3. 完整阅读

![full read](images/workflow-full-read.svg)

## 4. 问答 + 反思

![qa](images/workflow-qa.svg)

反思上限: `MAX_REFLECT_ITERATIONS=2`

## 5. 多篇对比

![compare](images/workflow-compare.svg)

## 6. 路由规则 (`graph/router.py`)

| 函数 | 条件 | 目标 |
|------|------|------|
| `route_after_parse` | task=qa | qa |
| | full_read | structure |
| | 默认 | analyst |
| `route_after_analyst` | task=compare | comparer |
| | 默认 | critic |
| `route_after_reflection` | 未通过且未超限 | qa |
| | 否则 | end |

## 7. 数据流

![data flow](images/data-flow.svg)
