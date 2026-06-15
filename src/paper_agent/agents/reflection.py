from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from paper_agent.config import get_settings
from paper_agent.llm import extract_json, get_llm
from paper_agent.models.outputs import QAAnswer, ReflectResult
from paper_agent.state import PaperState

REFLECT_SYSTEM = """你是答案质量审查专家。评估论文问答的质量。
要求：
1. is_grounded: 答案是否能在引用证据中找到支撑（无编造）
2. is_complete: 是否完整回答了问题的所有方面
3. passed: 两者都满足时为 true
4. 若不通过，给出 revised_query（改写后的检索问题，更具体或换角度）
5. 使用中文"""

REFLECT_USER = """原问题：{question}

当前答案：{answer}

引用证据：
{citations}

请输出 JSON（无 markdown）：
{{
  "is_grounded": true,
  "is_complete": true,
  "passed": true,
  "revised_query": null,
  "feedback": "评估说明"
}}"""


def reflect_on_answer(question: str, answer: QAAnswer) -> ReflectResult:
    citations_text = "\n".join(
        f"- [{c.section}, p.{c.page}] {c.excerpt} (verified={c.verified})"
        for c in answer.citations
    ) or "（无引用）"

    llm = get_llm()
    response = llm.invoke(
        [
            SystemMessage(content=REFLECT_SYSTEM),
            HumanMessage(
                content=REFLECT_USER.format(
                    question=question,
                    answer=answer.answer,
                    citations=citations_text,
                )
            ),
        ]
    )
    data = extract_json(str(response.content))
    passed = bool(data.get("passed", False))
    if answer.confidence == "low" and not answer.citations:
        passed = False

    return ReflectResult(
        is_grounded=bool(data.get("is_grounded", passed)),
        is_complete=bool(data.get("is_complete", passed)),
        passed=passed,
        revised_query=data.get("revised_query"),
        feedback=data.get("feedback", ""),
    )


def reflection_node(state: PaperState) -> dict:
    answer = state.get("qa_answer")
    question = state.get("user_query") or ""
    iteration = state.get("iteration_count") or 0

    if not answer or not question:
        return {
            "reflect_result": ReflectResult(passed=True, feedback="无答案可评估"),
        }

    result = reflect_on_answer(question, answer)
    settings = get_settings()

    if not result.passed and iteration < settings.max_reflect_iterations:
        revised = result.revised_query or f"{question}（请提供更具体的证据）"
        return {
            "reflect_result": result,
            "user_query": revised,
            "iteration_count": iteration + 1,
        }

    return {"reflect_result": result}


def route_after_reflection(state: PaperState) -> str:
    result = state.get("reflect_result")
    iteration = state.get("iteration_count") or 0
    settings = get_settings()

    if result and not result.passed and iteration <= settings.max_reflect_iterations:
        if state.get("user_query") != (state.get("qa_answer") and state["qa_answer"].question):
            return "qa"
    return "end"
