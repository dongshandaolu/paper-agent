from __future__ import annotations

from paper_agent.models.paper import PaperDocument


def format_sections(document: PaperDocument, max_chars: int = 12000) -> str:
    parts: list[str] = []
    total = 0
    for section in document.sections:
        block = (
            f"## {section.title} (p.{section.page_start}-{section.page_end})\n"
            f"{section.content}\n"
        )
        if total + len(block) > max_chars:
            remaining = max_chars - total
            if remaining > 200:
                parts.append(block[:remaining] + "\n...[truncated]")
            break
        parts.append(block)
        total += len(block)
    if not parts:
        return document.full_text[:max_chars]
    return "\n".join(parts)
