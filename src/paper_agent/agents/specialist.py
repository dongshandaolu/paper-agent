from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from paper_agent.llm import extract_json, get_llm
from paper_agent.models.outputs import (
    PaperStructure,
    ResearchQuestion,
    ResearchQuestionsResult,
    SectionOutline,
    TermExplanation,
    TerminologyResult,
)
from paper_agent.models.paper import PaperDocument
from paper_agent.prompts.research import RESEARCH_SYSTEM, RESEARCH_USER
from paper_agent.prompts.structure import STRUCTURE_SYSTEM, STRUCTURE_USER
from paper_agent.prompts.terminology import TERMINOLOGY_SYSTEM, TERMINOLOGY_USER
from paper_agent.tools.rcs import format_evidence_context, gather_evidence
from paper_agent.utils.text import format_sections


def _section_list(document: PaperDocument) -> str:
    if not document.sections:
        return "（未识别到章节，将按全文分析）"
    lines = [
        f"- {s.title} (p.{s.page_start}-{s.page_end}, level={s.level})"
        for s in document.sections
    ]
    return "\n".join(lines)


def analyze_structure(document: PaperDocument) -> PaperStructure:
    llm = get_llm()
    response = llm.invoke(
        [
            SystemMessage(content=STRUCTURE_SYSTEM),
            HumanMessage(
                content=STRUCTURE_USER.format(
                    title=document.title,
                    abstract=document.abstract or "（未识别）",
                    section_list=_section_list(document),
                    sections=format_sections(document),
                )
            ),
        ]
    )
    data = extract_json(str(response.content))
    outline = [SectionOutline(**item) for item in data.get("outline", [])]
    if not outline and document.sections:
        outline = [
            SectionOutline(
                title=s.title,
                level=s.level,
                page_start=s.page_start,
                page_end=s.page_end,
                summary=s.content[:200] + ("..." if len(s.content) > 200 else ""),
            )
            for s in document.sections
        ]
    return PaperStructure(
        doc_id=document.doc_id,
        title=document.title,
        outline=outline,
        imrad_mapping=data.get("imrad_mapping", {}),
        reading_guide=data.get("reading_guide", ""),
    )


def extract_research_questions(document: PaperDocument) -> ResearchQuestionsResult:
    llm = get_llm()
    response = llm.invoke(
        [
            SystemMessage(content=RESEARCH_SYSTEM),
            HumanMessage(
                content=RESEARCH_USER.format(
                    title=document.title,
                    abstract=document.abstract or "（未识别）",
                    sections=format_sections(document),
                )
            ),
        ]
    )
    data = extract_json(str(response.content))

    def _questions(key: str) -> list[ResearchQuestion]:
        return [ResearchQuestion(**q) for q in data.get(key, [])]

    return ResearchQuestionsResult(
        doc_id=document.doc_id,
        title=document.title,
        main_questions=_questions("main_questions"),
        sub_questions=_questions("sub_questions"),
        hypotheses=data.get("hypotheses", []),
    )


def explain_terms(
    document: PaperDocument,
    terms: list[str] | None = None,
    max_terms: int = 10,
) -> TerminologyResult:
    if terms:
        query = " ".join(terms)
        terms_hint = "、".join(terms)
    else:
        query = "key technical terms definitions abbreviations methodology"
        terms_hint = "（自动提取，最多 {} 个）".format(max_terms)

    evidence = gather_evidence(document.doc_id, query, document=document, top_k_final=8)
    context = format_evidence_context(evidence)
    if not context:
        context = format_sections(document, max_chars=10000)

    llm = get_llm()
    response = llm.invoke(
        [
            SystemMessage(content=TERMINOLOGY_SYSTEM),
            HumanMessage(
                content=TERMINOLOGY_USER.format(
                    title=document.title,
                    abstract=document.abstract or "（未识别）",
                    terms_hint=terms_hint,
                    context=context,
                )
            ),
        ]
    )
    data = extract_json(str(response.content))
    term_items = [TermExplanation(**t) for t in data.get("terms", [])][:max_terms]
    return TerminologyResult(
        doc_id=document.doc_id,
        title=document.title,
        terms=term_items,
    )
