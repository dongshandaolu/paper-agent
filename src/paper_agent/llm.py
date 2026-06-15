from __future__ import annotations

import json
import re

from langchain_openai import ChatOpenAI

from paper_agent.config import get_settings


def get_llm() -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(
        model=settings.model_name,
        openai_api_key=settings.openai_api_key,
        openai_api_base=settings.openai_api_base,
        temperature=0.2,
    )


def get_summary_llm() -> ChatOpenAI:
    settings = get_settings()
    model = settings.summary_model or settings.model_name
    return ChatOpenAI(
        model=model,
        openai_api_key=settings.openai_api_key,
        openai_api_base=settings.openai_api_base,
        temperature=0.1,
    )


def extract_json(text: str) -> dict:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]
    return json.loads(text)
