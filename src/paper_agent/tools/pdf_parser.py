from __future__ import annotations

import hashlib
import re
from pathlib import Path

import fitz

from paper_agent.models.paper import PaperDocument, Section

SECTION_PATTERNS = [
    (re.compile(r"^(abstract)\s*$", re.I), 1),
    (re.compile(r"^(1\.?\s*)?(introduction)\s*$", re.I), 1),
    (re.compile(r"^(2\.?\s*)?(related\s+work|background)\s*$", re.I), 1),
    (re.compile(r"^(3\.?\s*)?(method(s|ology)?|approach)\s*$", re.I), 1),
    (re.compile(r"^(3\.\d+\.?\s+.+)$", re.I), 2),
    (re.compile(r"^(4\.?\s*)?(experiment(s|al\s+setup)?|evaluation)\s*$", re.I), 1),
    (re.compile(r"^(5\.?\s*)?(result(s)?)\s*$", re.I), 1),
    (re.compile(r"^(6\.?\s*)?(discussion)\s*$", re.I), 1),
    (re.compile(r"^(7\.?\s*)?(conclusion(s)?)\s*$", re.I), 1),
    (re.compile(r"^(references|bibliography)\s*$", re.I), 1),
    (re.compile(r"^(appendix(\s+[a-z])?)\s*$", re.I), 1),
]

NOISE_PATTERNS = [
    re.compile(r"^(figure|fig\.|table|tab\.)\s*\d", re.I),
    re.compile(r"^(et al\.|pp\.|vol\.|doi:)", re.I),
    re.compile(r"^\d+$"),
    re.compile(r"^[\d\s\.]+$"),
    re.compile(r"^(Proceedings|Conference|Journal|arXiv)", re.I),
]

# 标题噪声：arXiv 版本号、日期行、版权声明等不应作为论文标题的文本模式
TITLE_NOISE_PATTERNS = [
    re.compile(r"arxiv\s*:", re.I),                          # arXiv:1706.xxxxx
    re.compile(r"\[\s*cs\.", re.I),                          # [cs.CL]
    re.compile(r"^\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)", re.I),  # 2 Aug 2023
    re.compile(r"\b(20\d{2}|19\d{2})\b.*\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b", re.I),
    re.compile(r"^v\d+\b", re.I),                            # v7, v2
    re.compile(r"preprint|under review|submitted to", re.I),
    re.compile(r"^copyright|\(c\)\s*\d{4}", re.I),
    re.compile(r"provided proper attribution", re.I),
    re.compile(r"google hereby grants", re.I),
    re.compile(r"^https?://", re.I),
    re.compile(r"^\*\s*equal contribution", re.I),
]

SUBSECTION_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.+)$")


def _doc_id_from_path(path: str) -> str:
    return hashlib.sha256(Path(path).resolve().as_posix().encode()).hexdigest()[:16]


def _is_title_noise(text: str) -> bool:
    """判断文本是否为标题区域的噪声（版本号、日期、版权声明等）"""
    for pat in TITLE_NOISE_PATTERNS:
        if pat.search(text):
            return True
    return False


def _extract_title(page: fitz.Page) -> str:
    blocks = page.get_text("dict")["blocks"]
    candidates: list[tuple[float, str]] = []
    for block in blocks:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                size = span.get("size", 0)
                if len(text) > 8 and size >= 12 and not _is_title_noise(text):
                    candidates.append((size, text))
    if not candidates:
        return "Untitled"
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1][:200]


def _parse_page_lines(page: fitz.Page, page_num: int) -> list[tuple[int, str, float]]:
    lines_out: list[tuple[int, str, float]] = []
    blocks = page.get_text("dict")["blocks"]
    for block in blocks:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            if not spans:
                continue
            text = "".join(s.get("text", "") for s in spans).strip()
            if not text:
                continue
            max_size = max(s.get("size", 10) for s in spans)
            lines_out.append((page_num, text, max_size))
    return lines_out


def _is_noise(line: str) -> bool:
    stripped = line.strip()
    if len(stripped) < 3:
        return True
    for pat in NOISE_PATTERNS:
        if pat.match(stripped):
            return True
    if stripped.endswith(".") and len(stripped) > 60:
        return True
    words = stripped.split()
    if len(words) > 12:
        return True
    return False


def _detect_heading(line: str, font_size: float, body_size: float) -> tuple[bool, int]:
    stripped = line.strip()
    if _is_noise(stripped):
        return False, 0

    for pattern, level in SECTION_PATTERNS:
        if pattern.match(stripped):
            return True, level

    sub = SUBSECTION_PATTERN.match(stripped)
    if sub and len(sub.group(2)) < 60:
        return True, 2

    if font_size >= body_size * 1.12 and len(stripped) < 80:
        if stripped[0].isupper() or stripped.startswith(("1", "2", "3", "4", "5", "6", "7", "8")):
            if not stripped.endswith("."):
                return True, 2

    return False, 0


def _split_sections_from_lines(all_lines: list[tuple[int, str, float]]) -> list[Section]:
    if not all_lines:
        return []

    sizes = [s for _, _, s in all_lines if s > 0]
    body_size = sorted(sizes)[len(sizes) // 2] if sizes else 10.0

    sections: list[Section] = []
    current_title = "Preamble"
    current_level = 1
    current_lines: list[str] = []
    current_page_start = all_lines[0][0]
    current_page_end = current_page_start

    def flush() -> None:
        nonlocal current_lines, current_title, current_level, current_page_start, current_page_end
        content = "\n".join(current_lines).strip()
        if content:
            sections.append(
                Section(
                    title=current_title,
                    content=content,
                    page_start=current_page_start,
                    page_end=current_page_end,
                    level=current_level,
                )
            )
        current_lines = []

    for page_num, line, font_size in all_lines:
        is_heading, level = _detect_heading(line, font_size, body_size)
        if is_heading and current_lines:
            flush()
            current_title = line.strip()
            current_level = level
            current_page_start = page_num
            current_page_end = page_num
        else:
            current_lines.append(line)
            current_page_end = page_num

    flush()
    return _merge_small_sections(sections)


def _merge_small_sections(sections: list[Section], min_chars: int = 150) -> list[Section]:
    if not sections:
        return sections
    merged: list[Section] = []
    buffer: Section | None = None
    for sec in sections:
        if buffer is None:
            buffer = sec
            continue
        if len(buffer.content) < min_chars and sec.level >= buffer.level:
            buffer = Section(
                title=buffer.title,
                content=buffer.content + "\n" + sec.content,
                page_start=buffer.page_start,
                page_end=sec.page_end,
                level=buffer.level,
            )
        else:
            merged.append(buffer)
            buffer = sec
    if buffer:
        merged.append(buffer)
    return merged


def _extract_abstract(sections: list[Section], full_text: str) -> str:
    for section in sections:
        if re.search(r"abstract", section.title, re.I):
            return section.content[:3000]
    match = re.search(
        r"(?is)abstract\s*\n(.{100,3000}?)\n\s*(introduction|1\.?\s*introduction)", full_text
    )
    if match:
        return match.group(1).strip()
    return ""


def parse_pdf(file_path: str) -> PaperDocument:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {file_path}")

    doc = fitz.open(path)
    all_lines: list[tuple[int, str, float]] = []
    for i, page in enumerate(doc):
        all_lines.extend(_parse_page_lines(page, i + 1))

    page_map: dict[int, list[str]] = {}
    for page_num, text, _ in all_lines:
        page_map.setdefault(page_num, []).append(text)
    full_text = "\n\n".join("\n".join(page_map[p]) for p in sorted(page_map))

    title = _extract_title(doc[0]) if doc.page_count else path.stem
    sections = _split_sections_from_lines(all_lines)
    abstract = _extract_abstract(sections, full_text)

    return PaperDocument(
        doc_id=_doc_id_from_path(str(path)),
        file_path=str(path.resolve()),
        title=title,
        abstract=abstract,
        full_text=full_text,
        sections=sections,
        page_count=doc.page_count,
    )
