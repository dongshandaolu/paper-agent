from __future__ import annotations

import base64
from pathlib import Path

from paper_agent.agents.analyst import summarize_document
from paper_agent.agents.critic import critique_document
from paper_agent.agents.specialist import (
    analyze_structure,
    explain_terms,
    extract_research_questions,
)
from paper_agent.agents.writer import writer_node
from paper_agent.config import get_settings
from paper_agent.graph.builder import build_compare_graph, build_full_read_graph, build_qa_graph
from paper_agent.models.outputs import (
    ComparisonResult,
    PaperCritique,
    PaperStructure,
    PaperSummary,
    QAAnswer,
    ResearchQuestionsResult,
    TerminologyResult,
)
from paper_agent.services.registry import PaperRecord, get_registry, ingest_pdf
from paper_agent.state_factory import make_initial_state


class PaperService:
    def upload(self, pdf_path: str) -> dict:
        record = ingest_pdf(pdf_path)
        return self._paper_info(record)

    def upload_base64(self, filename: str, content_base64: str) -> dict:
        settings = get_settings()
        papers_dir = Path(settings.papers_dir)
        papers_dir.mkdir(parents=True, exist_ok=True)

        if not filename.lower().endswith(".pdf"):
            filename = f"{filename}.pdf"

        target = papers_dir / filename
        target.write_bytes(base64.b64decode(content_base64))
        return self.upload(str(target))

    def list_papers(self) -> list[dict]:
        return get_registry().list_papers()

    def get_paper(self, paper_id: str) -> dict:
        record = get_registry().require(paper_id)
        return self._paper_info(record)

    def summarize_structure(self, paper_id: str, use_cache: bool = True) -> PaperStructure:
        registry = get_registry()
        record = registry.require(paper_id)
        if use_cache and record.structure:
            return record.structure
        structure = analyze_structure(record.document)
        record.structure = structure
        return structure

    def extract_research_questions(
        self, paper_id: str, use_cache: bool = True
    ) -> ResearchQuestionsResult:
        registry = get_registry()
        record = registry.require(paper_id)
        if use_cache and record.research_questions:
            return record.research_questions
        result = extract_research_questions(record.document)
        record.research_questions = result
        return result

    def explain_terms(
        self,
        paper_id: str,
        terms: list[str] | None = None,
        max_terms: int = 10,
        use_cache: bool = False,
    ) -> TerminologyResult:
        registry = get_registry()
        record = registry.require(paper_id)
        if use_cache and record.terminology and not terms:
            return record.terminology
        result = explain_terms(record.document, terms=terms, max_terms=max_terms)
        if not terms:
            record.terminology = result
        return result

    def ask(self, paper_id: str, question: str) -> QAAnswer:
        record = get_registry().require(paper_id)
        state = make_initial_state(
            pdf_paths=[record.file_path],
            task="qa",
            user_query=question,
        )
        state["documents"] = [record.document]
        graph = build_qa_graph()
        result = graph.invoke(state)
        answer = result.get("qa_answer")
        if not answer:
            return QAAnswer(question=question, answer="无法生成回答", confidence="low")
        return answer

    def read_full(
        self, paper_id: str, output_dir: str | None = None, full: bool = False
    ) -> dict:
        record = get_registry().require(paper_id)
        settings = get_settings()
        out_dir = output_dir or settings.output_dir

        if full:
            state = make_initial_state(
                pdf_paths=[record.file_path],
                task="full_read",
                output_dir=out_dir,
                full_read=True,
            )
            state["documents"] = [record.document]
            graph = build_full_read_graph()
            result = graph.invoke(state)
            summaries = result.get("summaries") or []
            critiques = result.get("critiques") or []
            structures = result.get("structures") or []
            research = result.get("research_questions_list") or []
            terms = result.get("terminologies") or []
            return {
                "paper_id": paper_id,
                "title": record.document.title,
                "report_path": result.get("report_path"),
                "summary": summaries[0].model_dump() if summaries else None,
                "critique": critiques[0].model_dump() if critiques else None,
                "structure": structures[0].model_dump() if structures else None,
                "research_questions": research[0].model_dump() if research else None,
                "terminology": terms[0].model_dump() if terms else None,
            }

        summary = record.summary or summarize_document(record.document)
        record.summary = summary

        critique = record.critique or critique_document(record.document, summary)
        record.critique = critique

        state = make_initial_state(
            pdf_paths=[record.file_path],
            task="read",
            output_dir=out_dir,
        )
        state["documents"] = [record.document]
        state["summaries"] = [summary]
        state["critiques"] = [critique]
        write_result = writer_node(state)
        return {
            "paper_id": paper_id,
            "title": record.document.title,
            "report_path": write_result.get("report_path"),
            "summary": summary.model_dump(),
            "critique": critique.model_dump(),
        }

    def compare(self, paper_ids: list[str], output_dir: str | None = None) -> dict:
        if len(paper_ids) < 2:
            raise ValueError("对比至少需要 2 篇论文")

        registry = get_registry()
        records = [registry.require(pid) for pid in paper_ids]
        settings = get_settings()
        out_dir = output_dir or settings.output_dir

        summaries: list[PaperSummary] = []
        for record in records:
            summary = record.summary or summarize_document(record.document)
            record.summary = summary
            summaries.append(summary)

        state = make_initial_state(
            pdf_paths=[r.file_path for r in records],
            task="compare",
            output_dir=out_dir,
        )
        state["documents"] = [r.document for r in records]
        state["summaries"] = summaries

        from paper_agent.agents.comparer import comparer_node

        compare_result = comparer_node(state)
        comparison: ComparisonResult | None = compare_result.get("comparison")
        state["comparison"] = comparison
        write_result = writer_node(state)

        return {
            "paper_ids": paper_ids,
            "report_path": write_result.get("report_path"),
            "comparison": comparison.model_dump() if comparison else None,
        }

    def _paper_info(self, record: PaperRecord) -> dict:
        doc = record.document
        return {
            "paper_id": doc.doc_id,
            "title": doc.title,
            "file_path": record.file_path,
            "page_count": doc.page_count,
            "section_count": len(doc.sections),
            "sections": [s.title for s in doc.sections],
            "abstract_preview": doc.abstract[:300] if doc.abstract else "",
            "uploaded_at": record.uploaded_at,
        }


_service: PaperService | None = None


def get_paper_service() -> PaperService:
    global _service
    if _service is None:
        _service = PaperService()
    return _service
