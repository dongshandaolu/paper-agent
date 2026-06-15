from __future__ import annotations

from paper_agent.models.paper import PaperDocument
from paper_agent.state import PaperState
from paper_agent.tools.chunker import attach_chunks
from paper_agent.tools.pdf_parser import parse_pdf
from paper_agent.tools.retriever import get_retriever


def parser_node(state: PaperState) -> dict:
    documents: list[PaperDocument] = []
    retriever = get_retriever()

    for pdf_path in state["pdf_paths"]:
        doc = parse_pdf(pdf_path)
        doc = attach_chunks(doc)
        retriever.index_document(doc)
        documents.append(doc)

    return {"documents": documents}
