# Paper Agent 文档中心

本目录包含 Paper Agent 项目的完整架构、流程与功能说明。

## 文档索引

| 文档 | 说明 |
|------|------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | **主文档** - 系统分层、技术栈、数据模型、配置与目录结构 |
| [FLOWS.md](FLOWS.md) | **流程详解** - 5 种 LangGraph 工作流、路由逻辑、端到端时序 |
| [FEATURES.md](FEATURES.md) | **功能汇总** - CLI/MCP 全功能分析、能力矩阵、输入输出规格 |

## 架构图 (SVG)

| 图片 | 内容 |
|------|------|
| [system-layers.svg](images/system-layers.svg) | 五层系统架构 |
| [data-flow.svg](images/data-flow.svg) | 端到端数据流 |
| [workflow-read.svg](images/workflow-read.svg) | 标准阅读工作流 |
| [workflow-full-read.svg](images/workflow-full-read.svg) | 完整阅读工作流 |
| [workflow-qa.svg](images/workflow-qa.svg) | 问答 + 反思循环 |
| [workflow-compare.svg](images/workflow-compare.svg) | 多篇对比工作流 |
| [rag-pipeline.svg](images/rag-pipeline.svg) | Agentic RAG 管线 |

## 快速导航

- 安装与使用: [README.md](../README.md)
- 完整示例: [tests/USAGE_EXAMPLE.md](../tests/USAGE_EXAMPLE.md)
- MCP 配置示例: [.mcp.json.example](../.mcp.json.example)
