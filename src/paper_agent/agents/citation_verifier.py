from __future__ import annotations

import re
from difflib import SequenceMatcher

from paper_agent.models.outputs import CitationRef, PaperCritique, PaperSummary, QAAnswer
from paper_agent.models.paper import PaperDocument


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def _fuzzy_match(excerpt: str, full_text: str, threshold: float = 0.55) -> bool:
    if not excerpt or not excerpt.strip():
        return False
    excerpt_norm = _normalize(excerpt)
    if len(excerpt_norm) < 10:
        return excerpt_norm in _normalize(full_text)

    full_norm = _normalize(full_text)
    if excerpt_norm in full_norm:
        return True

    window = len(excerpt_norm)
    step = max(1, window // 4)
    best = 0.0
    for i in range(0, max(1, len(full_norm) - window + 1), step):
        candidate = full_norm[i : i + window + 50]
        ratio = SequenceMatcher(None, excerpt_norm, candidate).ratio()
        best = max(best, ratio)
        if best >= threshold:
            return True
    return best >= threshold


def verify_citation(excerpt: str, document: PaperDocument, section: str = "") -> bool:
    if section:
        for sec in document.sections:
            if section.lower() in sec.title.lower():
                if _fuzzy_match(excerpt, sec.content):
                    return True
    return _fuzzy_match(excerpt, document.full_text)


def verify_qa_citations(answer: QAAnswer, document: PaperDocument) -> QAAnswer:
    verified_citations: list[CitationRef] = []
    for c in answer.citations:
        ok = verify_citation(c.excerpt, document, c.section)
        verified_citations.append(c.model_copy(update={"verified": ok}))
    all_ok = all(c.verified for c in verified_citations) if verified_citations else True
    confidence = answer.confidence
    if verified_citations and not all_ok:
        confidence = "low" if confidence == "high" else confidence
    return answer.model_copy(update={"citations": verified_citations, "confidence": confidence})


def verify_summary_citations(summary: PaperSummary, document: PaperDocument) -> PaperSummary:
    verified = [
        c.model_copy(update={"verified": verify_citation(c.excerpt, document, c.section)})
        for c in summary.citations
    ]
    return summary.model_copy(update={"citations": verified})


def verify_critique_evidence(critique: PaperCritique, document: PaperDocument) -> PaperCritique:
    updates: dict = {}
    for attr in ("innovation", "methodology_rigor", "experimental_adequacy", "reproducibility"):
        dim = getattr(critique, attr)
        if dim and dim.evidence and not verify_citation(dim.evidence, document):
            updates[attr] = dim.model_copy(update={"evidence": dim.evidence + " [未验证]"})
    if updates:
        return critique.model_copy(update=updates)
    return critique
