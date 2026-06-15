from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages

from paper_agent.models.outputs import (
    ComparisonResult,
    PaperCritique,
    PaperStructure,
    PaperSummary,
    QAAnswer,
    ReflectResult,
    ResearchQuestionsResult,
    TerminologyResult,
)
from paper_agent.models.paper import PaperDocument


class PaperState(TypedDict):
    pdf_paths: list[str]
    task: str
    full_read: bool
    user_query: str | None
    documents: list[PaperDocument]
    summaries: list[PaperSummary]
    critiques: list[PaperCritique]
    structures: list[PaperStructure]
    research_questions_list: list[ResearchQuestionsResult]
    terminologies: list[TerminologyResult]
    comparison: ComparisonResult | None
    qa_answer: QAAnswer | None
    reflect_result: ReflectResult | None
    iteration_count: int
    report_path: str | None
    output_dir: str | None
    messages: Annotated[list, add_messages]
