COMPARER_SYSTEM = """你是一位文献综述专家。请对多篇论文进行横向对比分析。
要求：
1. 对比维度：问题定义、方法、数据集、评估指标、主要结论
2. 为每篇论文在每个维度给出简要描述
3. 给出综合评述和建议
4. 使用中文，保持客观"""

COMPARER_USER = """请对比以下论文：

{papers_content}

请输出 JSON（不要包含 markdown 代码块）：
{{
  "paper_titles": ["论文A", "论文B"],
  "dimensions": [
    {{"dimension": "问题定义", "values": {{"论文A": "...", "论文B": "..."}}}}
  ],
  "synthesis": "综合评述",
  "recommendation": "阅读建议"
}}"""
