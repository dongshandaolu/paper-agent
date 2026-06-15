from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from paper_agent.agents.citation_verifier import verify_critique_evidence
from paper_agent.llm import extract_json, get_llm, get_summary_llm
from paper_agent.models.outputs import DimensionScore, PaperCritique, PaperSummary
from paper_agent.models.paper import PaperDocument, Section
from paper_agent.prompts.critic import CRITIC_SYSTEM, CRITIC_USER
from paper_agent.state import PaperState

CRITIC_MAP_SYSTEM = """你是论文评审专家。针对给定章节，提取与方法/实验/结果相关的评价要点。
输出 JSON：{"observations": ["观察1"], "evidence": ["证据摘录1"]}"""

CRITIC_MAP_USER = """论文：{title}
章节：{section_title}

内容：
{content}

请提取评价要点。"""


def _relevant_sections(document: PaperDocument) -> list[Section]:
    keywords = ("method", "approach", "experiment", "evaluation", "result", "discussion", "model")
    sections = [
        s for s in document.sections
        if any(k in s.title.lower() for k in keywords) and len(s.content.strip()) >= 80
    ]
    if sections:
        return sections[:6]
    return [s for s in document.sections if len(s.content.strip()) >= 80][:4]


def _method_sections_mapreduce(document: PaperDocument) -> str:
    sections = _relevant_sections(document)
    if len(sections) <= 1:
        return _method_sections_flat(document)

    llm = get_summary_llm()
    parts: list[str] = []
    for section in sections:
        try:
            response = llm.invoke(
                [
                    SystemMessage(content=CRITIC_MAP_SYSTEM),
                    HumanMessage(
                        content=CRITIC_MAP_USER.format(
                            title=document.title,
                            section_title=section.title,
                            content=section.content[:4000],
                        )
                    ),
                ]
            )
            data = extract_json(str(response.content))
            obs = data.get("observations", [])
            ev = data.get("evidence", [])
            parts.append(
                f"## {section.title} (p.{section.page_start})\n"
                f"观察: {'; '.join(obs)}\n证据: {'; '.join(ev)}"
            )
        except Exception:
            parts.append(f"## {section.title}\n{section.content[:2000]}")
    return "\n\n".join(parts)[:12000]


def _method_sections_flat(document: PaperDocument) -> str:
    keywords = ("method", "approach", "experiment", "evaluation", "result", "discussion")
    parts: list[str] = []
    for section in document.sections:
        title_lower = section.title.lower()
        if any(k in title_lower for k in keywords):
            parts.append(f"## {section.title} (p.{section.page_start})\n{section.content[:4000]}")
    if not parts:
        return document.full_text[:8000]
    return "\n\n".join(parts)[:12000]


def _critique_document(document: PaperDocument, summary: PaperSummary) -> PaperCritique:
    llm = get_llm()
    summary_text = (
        f"问题: {summary.problem}\n方法: {summary.method}\n"
        f"实验: {summary.experiments}\n结果: {summary.results}\n结论: {summary.conclusions}"
    )
    response = llm.invoke(
        [
            SystemMessage(content=CRITIC_SYSTEM),
            HumanMessage(
                content=CRITIC_USER.format(
                    title=document.title,
                    summary=summary_text,
                    method_sections=_method_sections_mapreduce(document),
                )
            ),
        ]
    )
    data = extract_json(str(response.content))

    def _score(key: str, label: str) -> DimensionScore | None:
        raw = data.get(key)
        if not raw:
            return None
        return DimensionScore(
            dimension=raw.get("dimension", label),
            score=int(raw.get("score", 3)),
            rationale=raw.get("rationale", ""),
            evidence=raw.get("evidence", ""),
        )

    critique = PaperCritique(
        doc_id=document.doc_id,
        title=document.title,
        innovation=_score("innovation", "创新性"),
        methodology_rigor=_score("methodology_rigor", "方法严谨性"),
        experimental_adequacy=_score("experimental_adequacy", "实验充分性"),
        reproducibility=_score("reproducibility", "可复现性"),
        strengths=data.get("strengths", []),
        limitations=data.get("limitations", []),
        overall_assessment=data.get("overall_assessment", ""),
    )
    return verify_critique_evidence(critique, document)


def critic_node(state: PaperState) -> dict:
    doc_map = {d.doc_id: d for d in state["documents"]}
    critiques = [
        critique_document(doc_map[s.doc_id], s)
        for s in state["summaries"]
        if s.doc_id in doc_map
    ]
    return {"critiques": critiques}


def critique_document(document: PaperDocument, summary: PaperSummary) -> PaperCritique:
    return _critique_document(document, summary)
