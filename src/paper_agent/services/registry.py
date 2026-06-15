from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from paper_agent.config import get_settings
from paper_agent.models.outputs import (
    PaperCritique,
    PaperStructure,
    PaperSummary,
    ResearchQuestionsResult,
    TerminologyResult,
)
from paper_agent.models.paper import PaperDocument
from paper_agent.tools.chunker import attach_chunks
from paper_agent.tools.pdf_parser import parse_pdf
from paper_agent.tools.retriever import get_retriever


@dataclass
class PaperRecord:
    document: PaperDocument
    file_path: str
    uploaded_at: str
    summary: PaperSummary | None = None
    critique: PaperCritique | None = None
    structure: PaperStructure | None = None
    research_questions: ResearchQuestionsResult | None = None
    terminology: TerminologyResult | None = None


@dataclass
class PaperRegistry:
    records: dict[str, PaperRecord] = field(default_factory=dict)

    def get(self, paper_id: str) -> PaperRecord | None:
        return self.records.get(paper_id)

    def require(self, paper_id: str) -> PaperRecord:
        record = self.get(paper_id)
        if not record:
            raise KeyError(f"未找到论文 paper_id={paper_id}，请先调用 upload_paper")
        return record

    def list_papers(self) -> list[dict]:
        return [
            {
                "paper_id": doc_id,
                "title": rec.document.title,
                "file_path": rec.file_path,
                "page_count": rec.document.page_count,
                "section_count": len(rec.document.sections),
                "uploaded_at": rec.uploaded_at,
            }
            for doc_id, rec in self.records.items()
        ]

    def register(self, record: PaperRecord) -> str:
        self.records[record.document.doc_id] = record
        self._persist_index()
        return record.document.doc_id

    def _index_path(self) -> Path:
        settings = get_settings()
        path = Path(settings.papers_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path / "index.json"

    def _persist_index(self) -> None:
        payload = {
            doc_id: {
                "file_path": rec.file_path,
                "uploaded_at": rec.uploaded_at,
                "title": rec.document.title,
            }
            for doc_id, rec in self.records.items()
        }
        self._index_path().write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load_from_disk(self) -> None:
        index_path = self._index_path()
        if not index_path.exists():
            return
        try:
            data = json.loads(index_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return
        retriever = get_retriever()
        for doc_id, meta in data.items():
            if doc_id in self.records:
                continue
            file_path = meta.get("file_path", "")
            if not file_path or not Path(file_path).exists():
                continue
            doc = attach_chunks(parse_pdf(file_path))
            if not retriever.has_index(doc.doc_id):
                retriever.index_document(doc)
            self.records[doc_id] = PaperRecord(
                document=doc,
                file_path=file_path,
                uploaded_at=meta.get("uploaded_at", ""),
            )


_registry: PaperRegistry | None = None


def get_registry() -> PaperRegistry:
    global _registry
    if _registry is None:
        _registry = PaperRegistry()
        _registry.load_from_disk()
    return _registry


def ingest_pdf(source_path: str, copy_to_library: bool = True) -> PaperRecord:
    path = Path(source_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"PDF 不存在: {source_path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"需要 PDF 文件: {source_path}")

    settings = get_settings()
    stored_path = path

    if copy_to_library:
        papers_dir = Path(settings.papers_dir)
        papers_dir.mkdir(parents=True, exist_ok=True)
        target = papers_dir / path.name
        if path != target.resolve():
            shutil.copy2(path, target)
        stored_path = target

    doc = attach_chunks(parse_pdf(str(stored_path)))
    retriever = get_retriever()
    retriever.index_document(doc)

    record = PaperRecord(
        document=doc,
        file_path=str(stored_path),
        uploaded_at=datetime.now().isoformat(timespec="seconds"),
    )
    get_registry().register(record)
    return record
