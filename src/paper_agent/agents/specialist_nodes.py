from __future__ import annotations

from paper_agent.agents.specialist import (
    analyze_structure,
    explain_terms,
    extract_research_questions,
)
from paper_agent.state import PaperState


def structure_node(state: PaperState) -> dict:
    structures = [analyze_structure(doc) for doc in state["documents"]]
    return {"structures": structures}


def research_node(state: PaperState) -> dict:
    results = [extract_research_questions(doc) for doc in state["documents"]]
    return {"research_questions_list": results}


def terms_node(state: PaperState) -> dict:
    terminologies = [explain_terms(doc, max_terms=8) for doc in state["documents"]]
    return {"terminologies": terminologies}
