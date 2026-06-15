"""MCP Server — 供 Claude Code / Cursor 等 AI 编程工具调用论文阅读 Agent。"""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from paper_agent.services.paper_service import get_paper_service

mcp = FastMCP(
    "paper-agent",
    instructions=(
        "专业论文阅读 Agent。先 upload_paper 上传 PDF，再使用 "
        "summarize_structure / extract_research_questions / explain_terms / "
        "ask_paper / read_paper / compare_papers 等工具分析论文。"
    ),
)


def _json(data: Any) -> str:
    if hasattr(data, "model_dump"):
        return json.dumps(data.model_dump(), ensure_ascii=False, indent=2)
    return json.dumps(data, ensure_ascii=False, indent=2)


@mcp.tool()
def upload_paper(pdf_path: str) -> str:
    """上传并索引本地 PDF 论文。返回 paper_id，供后续工具使用。

    Args:
        pdf_path: PDF 文件的绝对或相对路径（Claude Code 可将用户提供的论文路径传入）
    """
    result = get_paper_service().upload(pdf_path)
    return _json(result)


@mcp.tool()
def upload_paper_content(filename: str, content_base64: str) -> str:
    """通过 Base64 内容上传 PDF 论文（适用于二进制传输场景）。

    Args:
        filename: 文件名，如 my_paper.pdf
        content_base64: PDF 文件的 Base64 编码内容
    """
    result = get_paper_service().upload_base64(filename, content_base64)
    return _json(result)


@mcp.tool()
def list_papers() -> str:
    """列出已上传/索引的所有论文。"""
    return _json(get_paper_service().list_papers())


@mcp.tool()
def get_paper_info(paper_id: str) -> str:
    """获取已上传论文的基本信息（标题、章节、页数等）。"""
    return _json(get_paper_service().get_paper(paper_id))


@mcp.tool()
def summarize_structure(paper_id: str) -> str:
    """自动总结论文结构：章节大纲、IMRaD 映射、阅读指南。"""
    return _json(get_paper_service().summarize_structure(paper_id))


@mcp.tool()
def extract_research_questions(paper_id: str) -> str:
    """提取论文的研究问题、子问题与假设，附证据引用。"""
    return _json(get_paper_service().extract_research_questions(paper_id))


@mcp.tool()
def explain_terms(
    paper_id: str,
    terms: list[str] | None = None,
    max_terms: int = 10,
) -> str:
    """解释论文中的专业术语。可指定术语列表，或自动提取重要术语。

    Args:
        paper_id: 论文 ID（upload_paper 返回）
        terms: 要解释的术语列表，留空则自动提取
        max_terms: 自动提取时的最大术语数
    """
    return _json(get_paper_service().explain_terms(paper_id, terms=terms, max_terms=max_terms))


@mcp.tool()
def ask_paper(paper_id: str, question: str) -> str:
    """基于论文内容的 RAG 问答，回答附章节/页码引用。"""
    return _json(get_paper_service().ask(paper_id, question))


@mcp.tool()
def read_paper(paper_id: str, full: bool = False) -> str:
    """完整阅读流程：结构化摘要 + 批判性分析 + Markdown 报告。full=True 含结构/研究问题/术语。"""
    result = get_paper_service().read_full(paper_id, full=full)
    def _dump(v):
        return v.model_dump() if hasattr(v, "model_dump") else v
    return _json({k: _dump(v) for k, v in result.items()})


@mcp.tool()
def compare_papers(paper_ids: list[str]) -> str:
    """横向对比多篇论文（至少 2 篇），生成对比报告。"""
    return _json(get_paper_service().compare(paper_ids))


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
