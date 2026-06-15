from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from paper_agent.agents.citation_verifier import verify_qa_citations
from paper_agent.llm import extract_json, get_llm
from paper_agent.models.outputs import CitationRef, QAAnswer
from paper_agent.prompts.qa import QA_SYSTEM, QA_USER
from paper_agent.state import PaperState
from paper_agent.tools.rcs import format_evidence_context, gather_evidence


def qa_node(state: PaperState) -> dict:
    query = state.get("user_query") or ""
    if not query:
        return {"qa_answer": QAAnswer(question="", answer="未提供问题", confidence="low")}

    documents = state["documents"]
    if not documents:
        return {"qa_answer": QAAnswer(question=query, answer="未找到论文文档", confidence="low")}

    doc = documents[0]
    evidence = gather_evidence(doc.doc_id, query, document=doc)

    if not evidence:
        return {
            "qa_answer": QAAnswer(
                question=query,
                answer="论文未提及相关内容或索引为空",
                confidence="low",
            )
        }

    llm = get_llm()
    response = llm.invoke(
        [
            SystemMessage(content=QA_SYSTEM),
            HumanMessage(
                content=QA_USER.format(
                    question=query,
                    context=format_evidence_context(evidence),
                )
            ),
        ]
    )
    data = extract_json(str(response.content))
    citations = [CitationRef(**c) for c in data.get("citations", [])]
    answer = QAAnswer(
        question=query,
        answer=data.get("answer", ""),
        citations=citations,
        confidence=data.get("confidence", "medium"),
    )
    answer = verify_qa_citations(answer, doc)
    return {"qa_answer": answer}
