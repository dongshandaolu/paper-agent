from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from paper_agent.llm import extract_json, get_llm
from paper_agent.models.outputs import ComparisonDimension, ComparisonResult, PaperSummary
from paper_agent.prompts.comparer import COMPARER_SYSTEM, COMPARER_USER
from paper_agent.state import PaperState


def _format_papers_for_compare(summaries: list[PaperSummary]) -> str:
    parts: list[str] = []
    for s in summaries:
        parts.append(
            f"### {s.title}\n"
            f"- 问题: {s.problem}\n"
            f"- 方法: {s.method}\n"
            f"- 实验: {s.experiments}\n"
            f"- 结果: {s.results}\n"
            f"- 结论: {s.conclusions}\n"
            f"- 贡献: {', '.join(s.key_contributions)}\n"
        )
    return "\n".join(parts)


def comparer_node(state: PaperState) -> dict:
    summaries = state.get("summaries") or []
    if len(summaries) < 2:
        return {
            "comparison": ComparisonResult(
                synthesis="需要至少两篇论文的摘要才能对比",
                recommendation="请提供 2 篇以上 PDF",
            )
        }

    llm = get_llm()
    response = llm.invoke(
        [
            SystemMessage(content=COMPARER_SYSTEM),
            HumanMessage(
                content=COMPARER_USER.format(
                    papers_content=_format_papers_for_compare(summaries),
                )
            ),
        ]
    )
    data = extract_json(str(response.content))
    dimensions = [ComparisonDimension(**d) for d in data.get("dimensions", [])]
    return {
        "comparison": ComparisonResult(
            paper_titles=data.get("paper_titles", [s.title for s in summaries]),
            dimensions=dimensions,
            synthesis=data.get("synthesis", ""),
            recommendation=data.get("recommendation", ""),
        )
    }
