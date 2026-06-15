from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from paper_agent.agents.analyst import analyst_node
from paper_agent.agents.comparer import comparer_node
from paper_agent.agents.critic import critic_node
from paper_agent.agents.parser import parser_node
from paper_agent.agents.qa import qa_node
from paper_agent.agents.reflection import reflection_node
from paper_agent.agents.specialist_nodes import research_node, structure_node, terms_node
from paper_agent.agents.writer import writer_node
from paper_agent.graph.router import (
    route_after_analyst,
    route_after_parse,
    route_after_reflection,
)
from paper_agent.state import PaperState


def build_read_graph():
    graph = StateGraph(PaperState)
    graph.add_node("parser", parser_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("critic", critic_node)
    graph.add_node("writer", writer_node)

    graph.add_edge(START, "parser")
    graph.add_edge("parser", "analyst")
    graph.add_edge("analyst", "critic")
    graph.add_edge("critic", "writer")
    graph.add_edge("writer", END)
    return graph.compile()


def build_qa_graph():
    graph = StateGraph(PaperState)
    graph.add_node("parser", parser_node)
    graph.add_node("qa", qa_node)
    graph.add_node("reflect", reflection_node)

    graph.add_edge(START, "parser")
    graph.add_edge("parser", "qa")
    graph.add_edge("qa", "reflect")
    graph.add_conditional_edges(
        "reflect",
        route_after_reflection,
        {"qa": "qa", "end": END},
    )
    return graph.compile()


def build_compare_graph():
    graph = StateGraph(PaperState)
    graph.add_node("parser", parser_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("comparer", comparer_node)
    graph.add_node("writer", writer_node)

    graph.add_edge(START, "parser")
    graph.add_edge("parser", "analyst")
    graph.add_edge("analyst", "comparer")
    graph.add_edge("comparer", "writer")
    graph.add_edge("writer", END)
    return graph.compile()


def build_full_read_graph():
    graph = StateGraph(PaperState)
    graph.add_node("parser", parser_node)
    graph.add_node("structure", structure_node)
    graph.add_node("research", research_node)
    graph.add_node("terms", terms_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("critic", critic_node)
    graph.add_node("writer", writer_node)

    graph.add_edge(START, "parser")
    graph.add_edge("parser", "structure")
    graph.add_edge("structure", "research")
    graph.add_edge("research", "terms")
    graph.add_edge("terms", "analyst")
    graph.add_edge("analyst", "critic")
    graph.add_edge("critic", "writer")
    graph.add_edge("writer", END)
    return graph.compile()


def build_unified_graph():
    graph = StateGraph(PaperState)
    graph.add_node("parser", parser_node)
    graph.add_node("structure", structure_node)
    graph.add_node("research", research_node)
    graph.add_node("terms", terms_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("critic", critic_node)
    graph.add_node("comparer", comparer_node)
    graph.add_node("qa", qa_node)
    graph.add_node("reflect", reflection_node)
    graph.add_node("writer", writer_node)

    graph.add_edge(START, "parser")
    graph.add_conditional_edges(
        "parser",
        route_after_parse,
        {"analyst": "analyst", "qa": "qa", "structure": "structure"},
    )
    graph.add_edge("structure", "research")
    graph.add_edge("research", "terms")
    graph.add_edge("terms", "analyst")
    graph.add_conditional_edges(
        "analyst", route_after_analyst, {"critic": "critic", "comparer": "comparer"}
    )
    graph.add_edge("critic", "writer")
    graph.add_edge("comparer", "writer")
    graph.add_edge("writer", END)
    graph.add_edge("qa", "reflect")
    graph.add_conditional_edges(
        "reflect",
        route_after_reflection,
        {"qa": "qa", "end": END},
    )
    return graph.compile()
