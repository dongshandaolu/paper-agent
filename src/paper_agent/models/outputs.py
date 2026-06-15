from pydantic import BaseModel, Field


class CitationRef(BaseModel):
    section: str = ""
    page: int = 0
    excerpt: str = ""
    verified: bool = True


class PaperSummary(BaseModel):
    doc_id: str
    title: str
    problem: str = ""
    motivation: str = ""
    method: str = ""
    experiments: str = ""
    results: str = ""
    conclusions: str = ""
    key_contributions: list[str] = Field(default_factory=list)
    citations: list[CitationRef] = Field(default_factory=list)


class DimensionScore(BaseModel):
    dimension: str
    score: int = Field(ge=1, le=5)
    rationale: str = ""
    evidence: str = ""


class PaperCritique(BaseModel):
    doc_id: str
    title: str
    innovation: DimensionScore | None = None
    methodology_rigor: DimensionScore | None = None
    experimental_adequacy: DimensionScore | None = None
    reproducibility: DimensionScore | None = None
    strengths: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    overall_assessment: str = ""


class QAAnswer(BaseModel):
    question: str
    answer: str
    citations: list[CitationRef] = Field(default_factory=list)
    confidence: str = "medium"


class ComparisonDimension(BaseModel):
    dimension: str
    values: dict[str, str] = Field(default_factory=dict)


class ComparisonResult(BaseModel):
    paper_titles: list[str] = Field(default_factory=list)
    dimensions: list[ComparisonDimension] = Field(default_factory=list)
    synthesis: str = ""
    recommendation: str = ""


class ReadingReport(BaseModel):
    doc_id: str
    title: str
    summary: PaperSummary | None = None
    critique: PaperCritique | None = None
    report_path: str = ""


class SectionOutline(BaseModel):
    title: str
    level: int = 1
    page_start: int = 1
    page_end: int = 1
    summary: str = ""


class PaperStructure(BaseModel):
    doc_id: str
    title: str
    outline: list[SectionOutline] = Field(default_factory=list)
    imrad_mapping: dict[str, str] = Field(default_factory=dict)
    reading_guide: str = ""


class ResearchQuestion(BaseModel):
    question: str
    question_type: str = "main"
    evidence: str = ""
    section: str = ""
    page: int = 0


class ResearchQuestionsResult(BaseModel):
    doc_id: str
    title: str
    main_questions: list[ResearchQuestion] = Field(default_factory=list)
    sub_questions: list[ResearchQuestion] = Field(default_factory=list)
    hypotheses: list[str] = Field(default_factory=list)


class TermExplanation(BaseModel):
    term: str
    definition_in_paper: str = ""
    plain_explanation: str = ""
    related_terms: list[str] = Field(default_factory=list)
    section: str = ""
    page: int = 0


class TerminologyResult(BaseModel):
    doc_id: str
    title: str
    terms: list[TermExplanation] = Field(default_factory=list)


class RCSEvidence(BaseModel):
    chunk_id: str = ""
    section: str = ""
    page: int = 0
    summary: str = ""
    relevance_score: float = 0.0
    original_text: str = ""


class ReflectResult(BaseModel):
    is_grounded: bool = False
    is_complete: bool = False
    passed: bool = False
    revised_query: str | None = None
    feedback: str = ""
