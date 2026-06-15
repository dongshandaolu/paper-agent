from __future__ import annotations

from typing import Literal

from paper_agent.state import PaperState


def route_after_parse(state: PaperState) -> Literal["analyst", "qa", "structure"]:
    task = state.get("task", "")
    if task == "qa":
        return "qa"
    if task == "full_read" or state.get("full_read"):
        return "structure"
    return "analyst"


def route_after_analyst(state: PaperState) -> Literal["critic", "comparer"]:
    if state.get("task") == "compare":
        return "comparer"
    return "critic"


def route_after_reflection(state: PaperState) -> Literal["qa", "end"]:
    from paper_agent.config import get_settings

    result = state.get("reflect_result")
    iteration = state.get("iteration_count") or 0
    settings = get_settings()

    if result and not result.passed and iteration < settings.max_reflect_iterations:
        return "qa"
    return "end"
