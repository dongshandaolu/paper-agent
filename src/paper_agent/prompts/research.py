RESEARCH_SYSTEM = """你是一位学术研究方法专家。请从论文中提取研究问题与假设。
要求：
1. 区分主研究问题（main）与子问题（sub）
2. 识别显式与隐式研究问题
3. 提取可检验的假设（如有）
4. 每条问题附证据引用（章节、页码、原文摘录）
5. 使用中文，仅基于论文内容"""

RESEARCH_USER = """请提取以下论文的研究问题：

论文标题：{title}
摘要：{abstract}

正文：
{sections}

请输出 JSON（不要 markdown 代码块）：
{{
  "main_questions": [
    {{"question": "主研究问题", "question_type": "main", "evidence": "证据", "section": "章节", "page": 1}}
  ],
  "sub_questions": [
    {{"question": "子问题", "question_type": "sub", "evidence": "证据", "section": "章节", "page": 2}}
  ],
  "hypotheses": ["假设1"]
}}"""
