STRUCTURE_SYSTEM = """你是一位学术论文结构分析专家。请分析论文的章节结构，总结每个部分的核心内容。
要求：
1. 识别 IMRaD 结构（Introduction / Methods / Results / Discussion）及对应章节
2. 为每个主要章节提供 1-2 句摘要
3. 给出阅读顺序建议
4. 使用中文输出，基于原文，不要编造"""

STRUCTURE_USER = """请分析以下论文结构：

论文标题：{title}
摘要：{abstract}

章节列表（已解析）：
{section_list}

正文节选：
{sections}

请输出 JSON（不要 markdown 代码块）：
{{
  "outline": [
    {{"title": "章节名", "level": 1, "page_start": 1, "page_end": 2, "summary": "章节摘要"}}
  ],
  "imrad_mapping": {{
    "introduction": "对应章节名",
    "methods": "对应章节名",
    "results": "对应章节名",
    "discussion": "对应章节名"
  }},
  "reading_guide": "阅读顺序与重点建议"
}}"""
