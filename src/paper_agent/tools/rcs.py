"""RCS — Re-rank + Contextual Summarize (PaperQA2 style Gather Evidence)."""

from __future__ import annotations

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

from paper_agent.config import get_settings
from paper_agent.llm import extract_json, get_summary_llm
from paper_agent.models.outputs import RCSEvidence
from paper_agent.tools.retriever import get_retriever

RCS_SYSTEM = """你是论文证据提取专家。给定用户问题和论文片段，提取与问题相关的关键信息摘要。
要求：
1. 只提取片段中与问题相关的内容，忽略无关部分
2. 给出 0-10 的相关性评分（relevance_score）
3. 保留关键术语和数值
4. 使用中文摘要"""

RCS_USER = """问题：{query}

片段 [{section}, p.{page}]：
{chunk_text}

输出 JSON（无 markdown）：
{{"summary": "与问题相关的摘要", "relevance_score": 8}}"""


def _summarize_chunk(query: str, doc: Document) -> RCSEvidence:
    meta = doc.metadata
    llm = get_summary_llm()
    try:
        response = llm.invoke(
            [
                SystemMessage(content=RCS_SYSTEM),
                HumanMessage(
                    content=RCS_USER.format(
                        query=query,
                        section=meta.get("section", ""),
                        page=meta.get("page_start", "?"),
                        chunk_text=doc.page_content[:2500],
                    )
                ),
            ]
        )
        data = extract_json(str(response.content))
        score = float(data.get("relevance_score", meta.get("score", 0) * 10))
    except Exception:
        data = {"summary": doc.page_content[:500]}
        score = float(meta.get("score", 0.5) * 10)

    return RCSEvidence(
        chunk_id=str(meta.get("chunk_id", "")),
        section=str(meta.get("section", "")),
        page=int(meta.get("page_start", 0) or 0),
        summary=data.get("summary", doc.page_content[:500]),
        relevance_score=score,
        original_text=doc.page_content,
    )


def gather_evidence(
    doc_id: str,
    query: str,
    *,
    document=None,
    top_k_initial: int | None = None,
    top_k_final: int | None = None,
) -> list[RCSEvidence]:
    settings = get_settings()
    retriever = get_retriever()
    k_initial = top_k_initial or settings.rcs_top_k
    k_final = top_k_final or settings.rcs_final_k

    if settings.retrieval_mode == "hybrid" and document is not None:
        chunks = retriever.retrieve_hybrid(doc_id, query, document, top_k=k_initial)
    else:
        chunks = retriever.retrieve(doc_id, query, top_k=k_initial)

    if not chunks:
        return []

    evidence = [_summarize_chunk(query, c) for c in chunks]
    evidence.sort(key=lambda e: e.relevance_score, reverse=True)
    return evidence[:k_final]


def format_evidence_context(evidence: list[RCSEvidence]) -> str:
    parts: list[str] = []
    for i, ev in enumerate(evidence, 1):
        parts.append(
            f"[证据{i}] [{ev.section}, p.{ev.page}] (相关度:{ev.relevance_score:.1f})\n{ev.summary}"
        )
    return "\n\n".join(parts)
