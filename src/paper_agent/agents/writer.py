from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from jinja2 import Template

from paper_agent.config import get_settings
from paper_agent.models.outputs import (
    ComparisonResult,
    PaperCritique,
    PaperStructure,
    PaperSummary,
    ResearchQuestionsResult,
    TerminologyResult,
)
from paper_agent.state import PaperState

FULL_REPORT_TEMPLATE = """# {{ title }} — 阅读笔记

> 生成时间: {{ generated_at }}
> 源文件: {{ file_path }}

---

## 目录

{% if structure %}1. [论文结构](#论文结构){% endif %}
{% if research %}2. [研究问题](#研究问题){% endif %}
{% if terminology %}3. [术语解释](#术语解释){% endif %}
4. [结构化摘要](#结构化摘要)
5. [批判性分析](#批判性分析)
{% if comparison %}6. [论文对比](#论文对比){% endif %}

---

{% if structure %}
## 论文结构

{% for item in structure.outline %}
### {{ item.title }} (p.{{ item.page_start }}-{{ item.page_end }})
{{ item.summary }}

{% endfor %}
{% if structure.imrad_mapping %}
**IMRaD 映射**
{% for key, val in structure.imrad_mapping.items() %}
- {{ key }}: {{ val }}
{% endfor %}
{% endif %}
{% if structure.reading_guide %}
**阅读指南**: {{ structure.reading_guide }}
{% endif %}

---
{% endif %}

{% if research %}
## 研究问题

{% if research.main_questions %}
### 主研究问题
{% for q in research.main_questions %}
- {{ q.question }} [{{ q.section }}, p.{{ q.page }}]
{% endfor %}
{% endif %}
{% if research.sub_questions %}
### 子问题
{% for q in research.sub_questions %}
- {{ q.question }}
{% endfor %}
{% endif %}
{% if research.hypotheses %}
### 假设
{% for h in research.hypotheses %}
- {{ h }}
{% endfor %}
{% endif %}

---
{% endif %}

{% if terminology %}
## 术语解释

{% for t in terminology.terms %}
### {{ t.term }} [{{ t.section }}, p.{{ t.page }}]
{% if t.definition_in_paper %}- **论文表述**: {{ t.definition_in_paper }}{% endif %}
- **通俗解释**: {{ t.plain_explanation }}
{% if t.math_expression %}
- **数学表达式**:

$${{ t.math_expression }}$$

{% if t.math_explanation %}- **符号说明**: {{ t.math_explanation }}{% endif %}
{% endif %}
{% if t.related_terms %}- **相关术语**: {{ ', '.join(t.related_terms) }}{% endif %}

{% endfor %}
---
{% endif %}

## 结构化摘要

### 研究问题
{{ summary.problem }}

### 研究动机
{{ summary.motivation }}

### 核心方法
{{ summary.method }}

### 实验设置
{{ summary.experiments }}

### 主要结果
{{ summary.results }}

### 结论
{{ summary.conclusions }}

### 核心贡献
{% for item in summary.key_contributions %}
- {{ item }}
{% endfor %}

{% if summary.citations %}
### 关键引用
{% for c in summary.citations %}
- [{{ c.section }}, p.{{ c.page }}] {{ c.excerpt }}{% if not c.verified %} *(未验证)*{% endif %}
{% endfor %}
{% endif %}

---

## 批判性分析

{% if critique %}
| 维度 | 评分 | 理由 |
|------|------|------|
{% if critique.innovation %}
| 创新性 | {{ critique.innovation.score }}/5 | {{ critique.innovation.rationale }} |
{% endif %}
{% if critique.methodology_rigor %}
| 方法严谨性 | {{ critique.methodology_rigor.score }}/5 | {{ critique.methodology_rigor.rationale }} |
{% endif %}
{% if critique.experimental_adequacy %}
| 实验充分性 | {{ critique.experimental_adequacy.score }}/5 | {{ critique.experimental_adequacy.rationale }} |
{% endif %}
{% if critique.reproducibility %}
| 可复现性 | {{ critique.reproducibility.score }}/5 | {{ critique.reproducibility.rationale }} |
{% endif %}

### 优点
{% for s in critique.strengths %}
- {{ s }}
{% endfor %}

### 局限性
{% for l in critique.limitations %}
- {{ l }}
{% endfor %}

### 总体评价
{{ critique.overall_assessment }}
{% endif %}

{% if comparison %}
---

## 论文对比

{% for dim in comparison.dimensions %}
### {{ dim.dimension }}
{% for paper, value in dim.values.items() %}
- **{{ paper }}**: {{ value }}
{% endfor %}
{% endfor %}

### 综合评述
{{ comparison.synthesis }}

### 阅读建议
{{ comparison.recommendation }}
{% endif %}
"""

REPORT_TEMPLATE = """# {{ title }} — 阅读笔记

> 生成时间: {{ generated_at }}
> 源文件: {{ file_path }}

---

## 目录

1. [结构化摘要](#结构化摘要)
2. [批判性分析](#批判性分析)
{% if comparison %}3. [论文对比](#论文对比){% endif %}

---

## 结构化摘要

### 研究问题
{{ summary.problem }}

### 研究动机
{{ summary.motivation }}

### 核心方法
{{ summary.method }}

### 实验设置
{{ summary.experiments }}

### 主要结果
{{ summary.results }}

### 结论
{{ summary.conclusions }}

### 核心贡献
{% for item in summary.key_contributions %}
- {{ item }}
{% endfor %}

{% if summary.citations %}
### 关键引用
{% for c in summary.citations %}
- [{{ c.section }}, p.{{ c.page }}] {{ c.excerpt }}{% if not c.verified %} *(未验证)*{% endif %}
{% endfor %}
{% endif %}

---

## 批判性分析

{% if critique %}
| 维度 | 评分 | 理由 |
|------|------|------|
{% if critique.innovation %}
| 创新性 | {{ critique.innovation.score }}/5 | {{ critique.innovation.rationale }} |
{% endif %}
{% if critique.methodology_rigor %}
| 方法严谨性 | {{ critique.methodology_rigor.score }}/5 | {{ critique.methodology_rigor.rationale }} |
{% endif %}
{% if critique.experimental_adequacy %}
| 实验充分性 | {{ critique.experimental_adequacy.score }}/5 | {{ critique.experimental_adequacy.rationale }} |
{% endif %}
{% if critique.reproducibility %}
| 可复现性 | {{ critique.reproducibility.score }}/5 | {{ critique.reproducibility.rationale }} |
{% endif %}

### 优点
{% for s in critique.strengths %}
- {{ s }}
{% endfor %}

### 局限性
{% for l in critique.limitations %}
- {{ l }}
{% endfor %}

### 总体评价
{{ critique.overall_assessment }}
{% endif %}

{% if comparison %}
---

## 论文对比

{% for dim in comparison.dimensions %}
### {{ dim.dimension }}
{% for paper, value in dim.values.items() %}
- **{{ paper }}**: {{ value }}
{% endfor %}
{% endfor %}

### 综合评述
{{ comparison.synthesis }}

### 阅读建议
{{ comparison.recommendation }}
{% endif %}
"""

COMPARE_TEMPLATE = """# 论文对比报告

> 生成时间: {{ generated_at }}

## 对比论文
{% for t in comparison.paper_titles %}
- {{ t }}
{% endfor %}

## 对比维度

{% for dim in comparison.dimensions %}
### {{ dim.dimension }}
{% for paper, value in dim.values.items() %}
- **{{ paper }}**: {{ value }}
{% endfor %}

{% endfor %}

## 综合评述
{{ comparison.synthesis }}

## 阅读建议
{{ comparison.recommendation }}
"""


def _safe_filename(title: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', "_", title)
    name = re.sub(r"\s+", "_", name.strip())
    return name[:80] or "paper"


def _render_report(
    title: str,
    file_path: str,
    summary: PaperSummary | None,
    critique: PaperCritique | None,
    comparison: ComparisonResult | None = None,
    structure: PaperStructure | None = None,
    research: ResearchQuestionsResult | None = None,
    terminology: TerminologyResult | None = None,
    full: bool = False,
) -> str:
    template_str = FULL_REPORT_TEMPLATE if full else REPORT_TEMPLATE
    template = Template(template_str)
    return template.render(
        title=title,
        file_path=file_path,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        summary=summary,
        critique=critique,
        comparison=comparison,
        structure=structure,
        research=research,
        terminology=terminology,
    )


def _render_comparison(comparison: ComparisonResult) -> str:
    template = Template(COMPARE_TEMPLATE)
    return template.render(
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        comparison=comparison,
    )


def writer_node(state: PaperState) -> dict:
    settings = get_settings()
    output_dir = Path(state.get("output_dir") or settings.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    task = state.get("task", "read")
    report_paths: list[str] = []

    if task == "compare":
        comparison = state.get("comparison")
        if comparison:
            content = _render_comparison(comparison)
            path = output_dir / "comparison_report.md"
            path.write_text(content, encoding="utf-8")
            report_paths.append(str(path.resolve()))
        return {"report_path": report_paths[0] if report_paths else None}

    documents = state.get("documents") or []
    summaries = state.get("summaries") or []
    critiques = state.get("critiques") or []
    structures = state.get("structures") or []
    research_list = state.get("research_questions_list") or []
    terminologies = state.get("terminologies") or []

    summary_map = {s.doc_id: s for s in summaries}
    critique_map = {c.doc_id: c for c in critiques}
    structure_map = {s.doc_id: s for s in structures}
    research_map = {r.doc_id: r for r in research_list}
    terms_map = {t.doc_id: t for t in terminologies}

    is_full = bool(state.get("full_read") or task == "full_read")

    for doc in documents:
        content = _render_report(
            title=doc.title,
            file_path=doc.file_path,
            summary=summary_map.get(doc.doc_id),
            critique=critique_map.get(doc.doc_id),
            structure=structure_map.get(doc.doc_id),
            research=research_map.get(doc.doc_id),
            terminology=terms_map.get(doc.doc_id),
            full=is_full,
        )
        filename = _safe_filename(doc.title) + ".md"
        path = output_dir / filename
        path.write_text(content, encoding="utf-8")
        report_paths.append(str(path.resolve()))

    return {"report_path": report_paths[0] if report_paths else None}
