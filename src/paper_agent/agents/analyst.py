from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from paper_agent.agents.citation_verifier import verify_summary_citations
from paper_agent.llm import extract_json, get_llm, get_summary_llm
from paper_agent.models.outputs import CitationRef, PaperSummary
from paper_agent.models.paper import PaperDocument, Section
from paper_agent.prompts.analyst import ANALYST_SYSTEM, ANALYST_USER
from paper_agent.state import PaperState

MAP_SYSTEM = """你是学术论文分析专家。请针对单个章节提取与 IMRaD 相关的要点。
输出 JSON（无 markdown）：
{
  "section_title": "章节名",
  "problem": "与本节相关的问题/动机要点（无则空）",
  "method": "方法要点",
  "experiments": "实验要点",
  "results": "结果要点",
  "conclusions": "结论要点",
  "key_points": ["要点1"],
  "citations": [{"section": "章节", "page": 1, "excerpt": "原文摘录"}]
}"""

MAP_USER = """论文：{title}
章节：{section_title} (p.{page_start}-{page_end})

内容：
{content}

请提取要点。"""

REDUCE_SYSTEM = """你是学术论文分析专家。请将各章节的 partial 摘要合并为完整的 IMRaD 结构化摘要。
要求：中文、学术严谨、不编造、合并重复内容。"""

REDUCE_USER = """论文标题：{title}
摘要：{abstract}

各章节 partial 摘要：
{partials}

请输出最终 JSON（无 markdown）：
{{
  "problem": "研究问题",
  "motivation": "研究动机",
  "method": "核心方法",
  "experiments": "实验设置",
  "results": "主要结果",
  "conclusions": "结论",
  "key_contributions": ["贡献1"],
  "citations": [{{"section": "章节", "page": 1, "excerpt": "摘录"}}]
}}"""


def _map_section(document: PaperDocument, section: Section) -> dict:
    if len(section.content.strip()) < 80:
        return {}
    llm = get_summary_llm()
    try:
        response = llm.invoke(
            [
                SystemMessage(content=MAP_SYSTEM),
                HumanMessage(
                    content=MAP_USER.format(
                        title=document.title,
                        section_title=section.title,
                        page_start=section.page_start,
                        page_end=section.page_end,
                        content=section.content[:6000],
                    )
                ),
            ]
        )
        return extract_json(str(response.content))
    except Exception:
        return {"section_title": section.title, "key_points": [section.content[:300]]}


def _reduce_partials(document: PaperDocument, partials: list[dict]) -> PaperSummary:
    partials_text = "\n\n".join(
        f"### {p.get('section_title', 'Section')}\n"
        f"问题: {p.get('problem', '')}\n方法: {p.get('method', '')}\n"
        f"实验: {p.get('experiments', '')}\n结果: {p.get('results', '')}\n"
        f"要点: {', '.join(p.get('key_points', []))}"
        for p in partials
        if p
    )
    llm = get_llm()
    response = llm.invoke(
        [
            SystemMessage(content=REDUCE_SYSTEM),
            HumanMessage(
                content=REDUCE_USER.format(
                    title=document.title,
                    abstract=document.abstract or "（未识别）",
                    partials=partials_text,
                )
            ),
        ]
    )
    data = extract_json(str(response.content))
    all_citations: list[CitationRef] = []
    for p in partials:
        all_citations.extend(CitationRef(**c) for c in p.get("citations", []))
    data_citations = [CitationRef(**c) for c in data.get("citations", [])]
    citations = data_citations or all_citations[:5]

    summary = PaperSummary(
        doc_id=document.doc_id,
        title=document.title,
        problem=data.get("problem", ""),
        motivation=data.get("motivation", ""),
        method=data.get("method", ""),
        experiments=data.get("experiments", ""),
        results=data.get("results", ""),
        conclusions=data.get("conclusions", ""),
        key_contributions=data.get("key_contributions", []),
        citations=citations,
    )
    return verify_summary_citations(summary, document)


def _summarize_document(document: PaperDocument) -> PaperSummary:
    sections = [s for s in document.sections if len(s.content.strip()) >= 80]
    if len(sections) >= 3:
        partials = [_map_section(document, s) for s in sections]
        partials = [p for p in partials if p]
        if partials:
            return _reduce_partials(document, partials)

    llm = get_llm()
    from paper_agent.utils.text import format_sections

    response = llm.invoke(
        [
            SystemMessage(content=ANALYST_SYSTEM),
            HumanMessage(
                content=ANALYST_USER.format(
                    title=document.title,
                    abstract=document.abstract or "（未识别到摘要）",
                    sections=format_sections(document),
                )
            ),
        ]
    )
    data = extract_json(str(response.content))
    citations = [CitationRef(**c) for c in data.get("citations", [])]
    summary = PaperSummary(
        doc_id=document.doc_id,
        title=document.title,
        problem=data.get("problem", ""),
        motivation=data.get("motivation", ""),
        method=data.get("method", ""),
        experiments=data.get("experiments", ""),
        results=data.get("results", ""),
        conclusions=data.get("conclusions", ""),
        key_contributions=data.get("key_contributions", []),
        citations=citations,
    )
    return verify_summary_citations(summary, document)


def analyst_node(state: PaperState) -> dict:
    summaries = [summarize_document(doc) for doc in state["documents"]]
    return {"summaries": summaries}


def summarize_document(document: PaperDocument) -> PaperSummary:
    return _summarize_document(document)
