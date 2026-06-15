from pydantic import BaseModel, Field


class Chunk(BaseModel):
    chunk_id: str
    text: str
    section_title: str = ""
    page_start: int = 1
    page_end: int = 1
    chunk_index: int = 0


class Section(BaseModel):
    title: str
    content: str
    page_start: int = 1
    page_end: int = 1
    level: int = 1


class PaperDocument(BaseModel):
    doc_id: str
    file_path: str
    title: str = "Untitled"
    authors: list[str] = Field(default_factory=list)
    abstract: str = ""
    full_text: str = ""
    sections: list[Section] = Field(default_factory=list)
    chunks: list[Chunk] = Field(default_factory=list)
    page_count: int = 0
