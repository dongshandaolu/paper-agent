from __future__ import annotations

import hashlib

from paper_agent.config import get_settings
from paper_agent.models.paper import Chunk, PaperDocument


def _chunk_id(doc_id: str, index: int) -> str:
    return hashlib.sha256(f"{doc_id}:{index}".encode()).hexdigest()[:12]


def _split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        if end >= len(text):
            break
        start = max(start + 1, end - overlap)
    return chunks


def chunk_document(document: PaperDocument) -> list[Chunk]:
    settings = get_settings()
    chunks: list[Chunk] = []
    index = 0

    if document.sections:
        for section in document.sections:
            parts = _split_text(section.content, settings.chunk_size, settings.chunk_overlap)
            for part in parts:
                chunks.append(
                    Chunk(
                        chunk_id=_chunk_id(document.doc_id, index),
                        text=part,
                        section_title=section.title,
                        page_start=section.page_start,
                        page_end=section.page_end,
                        chunk_index=index,
                    )
                )
                index += 1
    else:
        parts = _split_text(document.full_text, settings.chunk_size, settings.chunk_overlap)
        for part in parts:
            chunks.append(
                Chunk(
                    chunk_id=_chunk_id(document.doc_id, index),
                    text=part,
                    section_title="Full Text",
                    page_start=1,
                    page_end=document.page_count or 1,
                    chunk_index=index,
                )
            )
            index += 1

    return chunks


def attach_chunks(document: PaperDocument) -> PaperDocument:
    document.chunks = chunk_document(document)
    return document
