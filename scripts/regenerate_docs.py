# -*- coding: utf-8 -*-
"""Regenerate docs SVG images. Chinese via unicode escapes to avoid encoding loss."""
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"
IMAGES = DOCS / "images"

# fmt: off
T = {
    "title_layers": "\u7cfb\u7edf\u5206\u5c42\u67b6\u6784",
    "entry": "\u5165\u53e3\u5c42",
    "service": "\u670d\u52a1\u5c42",
    "orch": "\u7f16\u6392\u5c42",
    "agent_layer": "Agent \u5c42",
    "tools": "\u5de5\u5177\u5c42",
    "models": "\u6a21\u578b\u5c42",
    "workflows5": "5 \u79cd\u5de5\u4f5c\u6d41",
    "compat": "OpenAI \u517c\u5bb9",
    "read_flow": "\u6807\u51c6\u9605\u8bfb\u5de5\u4f5c\u6d41",
    "read_out": "\u8f93\u51fa: output/*.md - IMRaD \u6458\u8981 + \u6279\u5224\u5206\u6790 + \u56db\u7ef4\u8bc4\u5206",
    "full_flow": "\u5b8c\u6574\u9605\u8bfb\u5de5\u4f5c\u6d41",
    "full_extra": "\u589e\u52a0: \u7ed3\u6784\u5927\u7eb2 / \u7814\u7a76\u95ee\u9898 / \u4e13\u4e1a\u672f\u8bed\u89e3\u91ca",
    "qa_flow": "\u95ee\u7b54\u5de5\u4f5c\u6d41 (ask) - \u542b\u53cd\u601d\u5faa\u73af",
    "pass": "\u901a\u8fc7",
    "fail": "\u4e0d\u901a\u8fc7: \u6539\u5199 query \u540e\u91cd\u68c0\u7d22 (\u6700\u591a 2 \u8f6e)",
    "qa_inner": "qa \u5185\u90e8: Hybrid Retriever - RCS - LLM - Citation Verifier",
    "cmp_flow": "\u591a\u7bc7\u5bf9\u6bd4\u5de5\u4f5c\u6d41",
    "cmp_out": "\u8f93\u5165 2+ \u7bc7\u8bba\u6587, \u8f93\u51fa\u5bf9\u6bd4\u77e9\u9635 + \u7efc\u5408\u8bc4\u8ff0 + \u9605\u8bfb\u5efa\u8bae",
    "rag_title": "Agentic RAG \u7ba1\u7ebf",
    "user_q": "\u7528\u6237\u95ee\u9898",
    "hybrid": "Hybrid Retriever (\u7ae0\u8282\u4f18\u5148 + TF-IDF/Embedding)",
    "topk": "Top-K \u521d\u7b5b (RCS_TOP_K=20)",
    "rcs": "RCS \u91cd\u6392 + \u4e0a\u4e0b\u6587\u6458\u8981",
    "topn": "Top-N \u7cbe\u6392 (RCS_FINAL_K=5)",
    "llm_ans": "LLM \u751f\u6210\u7b54\u6848 + Citation Verifier",
    "data_flow": "\u7aef\u5230\u7aef\u6570\u636e\u6d41",
    "pdf": "PDF \u6587\u4ef6",
    "parse": "PyMuPDF \u89e3\u6790",
    "index": "\u68c0\u7d22\u7d22\u5f15",
    "lg_flow": "LangGraph \u5de5\u4f5c\u6d41 (PaperState)",
    "struct_out": "\u7ed3\u6784\u5316\u8f93\u51fa",
    "pydantic": "Pydantic \u6a21\u578b",
    "md_report": "Markdown \u62a5\u544a",
}
# fmt: on


def write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8", newline="\n")


def svg_header(w: int, h: int) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        'font-family="Microsoft YaHei, Segoe UI, sans-serif">\n'
    )


def arrow_def() -> str:
    return (
        "  <defs>\n"
        '    <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">\n'
        '      <path d="M0,0 L0,6 L8,3 z" fill="#64748b"/>\n'
        "    </marker>\n"
        "  </defs>\n"
    )


def gen_system_layers() -> str:
    t = T
    return (
        svg_header(900, 520)
        + '  <rect width="900" height="520" fill="#f8fafc"/>\n'
        + f'  <text x="450" y="36" text-anchor="middle" font-size="20" font-weight="700" fill="#0f172a">Paper Agent - {t["title_layers"]}</text>\n'
        + arrow_def()
        + '  <rect x="40" y="55" width="820" height="70" rx="8" fill="#2563eb"/>\n'
        + f'  <text x="450" y="82" text-anchor="middle" fill="white" font-size="14" font-weight="600">{t["entry"]} (Entry)</text>\n'
        + '  <text x="260" y="110" text-anchor="middle" fill="white" font-size="12">CLI - Typer + Rich</text>\n'
        + '  <text x="640" y="110" text-anchor="middle" fill="white" font-size="12">MCP Server - FastMCP (stdio)</text>\n'
        + '  <path d="M450 125 L450 145" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + '  <rect x="40" y="150" width="820" height="70" rx="8" fill="#0d9488"/>\n'
        + f'  <text x="450" y="177" text-anchor="middle" fill="white" font-size="14" font-weight="600">{t["service"]} (PaperService + PaperRegistry)</text>\n'
        + '  <text x="450" y="200" text-anchor="middle" fill="#ccfbf1" font-size="11">upload / ask / read_full / compare / structure / questions / terms</text>\n'
        + '  <path d="M450 220 L450 240" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + '  <rect x="40" y="245" width="820" height="70" rx="8" fill="#7c3aed"/>\n'
        + f'  <text x="450" y="272" text-anchor="middle" fill="white" font-size="14" font-weight="600">{t["orch"]} (LangGraph StateGraph)</text>\n'
        + f'  <text x="450" y="295" text-anchor="middle" fill="#ede9fe" font-size="11">read / full_read / qa / compare / unified ({t["workflows5"]})</text>\n'
        + '  <path d="M450 315 L450 335" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + '  <rect x="40" y="340" width="820" height="70" rx="8" fill="#ea580c"/>\n'
        + f'  <text x="450" y="367" text-anchor="middle" fill="white" font-size="14" font-weight="600">{t["agent_layer"]} (Specialist Agents)</text>\n'
        + '  <text x="450" y="390" text-anchor="middle" fill="#ffedd5" font-size="10">Parser / Structure / Research / Terms / Analyst / Critic / QA / Reflection / Comparer / Writer</text>\n'
        + '  <path d="M450 410 L450 430" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + '  <rect x="40" y="435" width="400" height="60" rx="8" fill="#ca8a04"/>\n'
        + f'  <text x="240" y="462" text-anchor="middle" fill="white" font-size="13" font-weight="600">{t["tools"]} (Tools)</text>\n'
        + '  <text x="240" y="480" text-anchor="middle" fill="#fef9c3" font-size="10">PDF Parser / Chunker / Hybrid Retriever / RCS</text>\n'
        + '  <rect x="460" y="435" width="400" height="60" rx="8" fill="#475569"/>\n'
        + f'  <text x="660" y="462" text-anchor="middle" fill="white" font-size="13" font-weight="600">{t["models"]} (Models)</text>\n'
        + f'  <text x="660" y="480" text-anchor="middle" fill="#e2e8f0" font-size="10">LLM ({t["compat"]}) / TF-IDF / Chroma / FastEmbed</text>\n'
        + "</svg>\n"
    )


def gen_workflow_read() -> str:
    t = T
    return (
        svg_header(800, 200)
        + '  <rect width="800" height="200" fill="#f8fafc"/>\n'
        + f'  <text x="400" y="28" text-anchor="middle" font-size="16" font-weight="700" fill="#0f172a">{t["read_flow"]} (read)</text>\n'
        + arrow_def()
        + '  <circle cx="50" cy="100" r="28" fill="#22c55e"/><text x="50" y="105" text-anchor="middle" fill="white" font-size="11" font-weight="600">START</text>\n'
        + '  <path d="M78 100 L108 100" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + '  <rect x="110" y="72" width="90" height="56" rx="6" fill="#3b82f6"/><text x="155" y="100" text-anchor="middle" fill="white" font-size="11" font-weight="600">parser</text>\n'
        + '  <path d="M200 100 L230 100" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + '  <rect x="232" y="72" width="90" height="56" rx="6" fill="#8b5cf6"/><text x="277" y="100" text-anchor="middle" fill="white" font-size="11" font-weight="600">analyst</text>\n'
        + '  <path d="M322 100 L352 100" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + '  <rect x="354" y="72" width="90" height="56" rx="6" fill="#f59e0b"/><text x="399" y="100" text-anchor="middle" fill="white" font-size="11" font-weight="600">critic</text>\n'
        + '  <path d="M444 100 L474 100" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + '  <rect x="476" y="72" width="90" height="56" rx="6" fill="#0d9488"/><text x="521" y="100" text-anchor="middle" fill="white" font-size="11" font-weight="600">writer</text>\n'
        + '  <path d="M566 100 L596 100" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + '  <circle cx="628" cy="100" r="28" fill="#ef4444"/><text x="628" y="105" text-anchor="middle" fill="white" font-size="11" font-weight="600">END</text>\n'
        + f'  <text x="400" y="175" text-anchor="middle" fill="#64748b" font-size="11">{t["read_out"]}</text>\n'
        + "</svg>\n"
    )


def gen_workflow_full_read() -> str:
    t = T
    nodes = ["parser", "structure", "research", "terms", "analyst", "critic", "writer"]
    colors = ["#3b82f6", "#6366f1", "#6366f1", "#6366f1", "#8b5cf6", "#f59e0b", "#0d9488"]
    parts = [
        svg_header(1000, 200),
        '  <rect width="1000" height="200" fill="#f8fafc"/>\n',
        f'  <text x="500" y="28" text-anchor="middle" font-size="16" font-weight="700" fill="#0f172a">{t["full_flow"]} (read --full)</text>\n',
        arrow_def(),
        '  <circle cx="35" cy="100" r="24" fill="#22c55e"/><text x="35" y="104" text-anchor="middle" fill="white" font-size="10" font-weight="600">START</text>\n',
        '  <path d="M59 100 L75 100" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n',
    ]
    x = 78
    for name, color in zip(nodes, colors):
        parts.append(f'  <rect x="{x}" y="72" width="80" height="56" rx="6" fill="{color}"/>\n')
        parts.append(f'  <text x="{x+40}" y="104" text-anchor="middle" fill="white" font-size="10" font-weight="600">{name}</text>\n')
        if name != "writer":
            parts.append(f'  <path d="M{x+80} 100 L{x+98} 100" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n')
        x += 98
    parts.append('  <path d="M856 100 L876 100" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n')
    parts.append('  <circle cx="900" cy="100" r="24" fill="#ef4444"/><text x="900" y="104" text-anchor="middle" fill="white" font-size="10" font-weight="600">END</text>\n')
    parts.append(f'  <text x="500" y="175" text-anchor="middle" fill="#64748b" font-size="11">{t["full_extra"]}</text>\n')
    parts.append("</svg>\n")
    return "".join(parts)


def gen_workflow_qa() -> str:
    t = T
    return (
        svg_header(700, 280)
        + '  <rect width="700" height="280" fill="#f8fafc"/>\n'
        + f'  <text x="350" y="28" text-anchor="middle" font-size="16" font-weight="700" fill="#0f172a">{t["qa_flow"]}</text>\n'
        + arrow_def()
        + '  <circle cx="50" cy="120" r="26" fill="#22c55e"/><text x="50" y="125" text-anchor="middle" fill="white" font-size="10" font-weight="600">START</text>\n'
        + '  <path d="M76 120 L116 120" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + '  <rect x="118" y="92" width="88" height="56" rx="6" fill="#3b82f6"/><text x="162" y="125" text-anchor="middle" fill="white" font-size="11" font-weight="600">parser</text>\n'
        + '  <path d="M206 120 L246 120" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + '  <rect x="248" y="92" width="88" height="56" rx="6" fill="#ec4899"/><text x="292" y="125" text-anchor="middle" fill="white" font-size="11" font-weight="600">qa</text>\n'
        + '  <path d="M336 120 L376 120" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + '  <rect x="378" y="92" width="100" height="56" rx="6" fill="#a855f7"/><text x="428" y="125" text-anchor="middle" fill="white" font-size="11" font-weight="600">reflect</text>\n'
        + '  <path d="M478 120 L528 120" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + f'  <text x="503" y="108" text-anchor="middle" fill="#22c55e" font-size="9">{t["pass"]}</text>\n'
        + '  <circle cx="560" cy="120" r="26" fill="#ef4444"/><text x="560" y="125" text-anchor="middle" fill="white" font-size="10" font-weight="600">END</text>\n'
        + '  <path d="M428 148 L428 210 L292 210 L292 148" stroke="#ef4444" stroke-width="2" fill="none" marker-end="url(#arrow)"/>\n'
        + f'  <text x="360" y="235" text-anchor="middle" fill="#ef4444" font-size="10">{t["fail"]}</text>\n'
        + f'  <text x="350" y="265" text-anchor="middle" fill="#475569" font-size="10">{t["qa_inner"]}</text>\n'
        + "</svg>\n"
    )


def gen_workflow_compare() -> str:
    t = T
    return (
        svg_header(800, 200)
        + '  <rect width="800" height="200" fill="#f8fafc"/>\n'
        + f'  <text x="400" y="28" text-anchor="middle" font-size="16" font-weight="700" fill="#0f172a">{t["cmp_flow"]} (compare)</text>\n'
        + arrow_def()
        + '  <circle cx="50" cy="100" r="28" fill="#22c55e"/><text x="50" y="105" text-anchor="middle" fill="white" font-size="11" font-weight="600">START</text>\n'
        + '  <path d="M78 100 L108 100" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + '  <rect x="110" y="72" width="100" height="56" rx="6" fill="#3b82f6"/><text x="160" y="100" text-anchor="middle" fill="white" font-size="11" font-weight="600">parser</text>\n'
        + '  <path d="M210 100 L240 100" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + '  <rect x="242" y="72" width="100" height="56" rx="6" fill="#8b5cf6"/><text x="292" y="100" text-anchor="middle" fill="white" font-size="11" font-weight="600">analyst</text>\n'
        + '  <path d="M342 100 L372 100" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + '  <rect x="374" y="72" width="100" height="56" rx="6" fill="#14b8a6"/><text x="424" y="100" text-anchor="middle" fill="white" font-size="11" font-weight="600">comparer</text>\n'
        + '  <path d="M474 100 L504 100" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + '  <rect x="506" y="72" width="100" height="56" rx="6" fill="#0d9488"/><text x="556" y="100" text-anchor="middle" fill="white" font-size="11" font-weight="600">writer</text>\n'
        + '  <path d="M606 100 L636 100" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + '  <circle cx="668" cy="100" r="28" fill="#ef4444"/><text x="668" y="105" text-anchor="middle" fill="white" font-size="11" font-weight="600">END</text>\n'
        + f'  <text x="400" y="175" text-anchor="middle" fill="#64748b" font-size="11">{t["cmp_out"]}</text>\n'
        + "</svg>\n"
    )


def gen_rag_pipeline() -> str:
    t = T
    steps = [
        (t["user_q"], "#1e40af", 50, 40),
        (t["hybrid"], "#3b82f6", 118, 50),
        (t["topk"], "#6366f1", 190, 36),
        (t["rcs"], "#8b5cf6", 248, 50),
        (t["topn"], "#a855f7", 320, 36),
        (t["llm_ans"], "#ec4899", 378, 36),
    ]
    parts = [svg_header(720, 420), '  <rect width="720" height="420" fill="#f8fafc"/>\n', f'  <text x="360" y="30" text-anchor="middle" font-size="16" font-weight="700" fill="#0f172a">{t["rag_title"]}</text>\n', arrow_def()]
    for i, (label, color, box_y, h) in enumerate(steps):
        parts.append(f'  <rect x="160" y="{box_y}" width="400" height="{h}" rx="6" fill="{color}"/>\n')
        parts.append(f'  <text x="360" y="{box_y + h // 2 + 5}" text-anchor="middle" fill="white" font-size="12" font-weight="600">{label}</text>\n')
        if i < len(steps) - 1:
            nxt = steps[i + 1][2]
            parts.append(f'  <path d="M360 {box_y + h} L360 {nxt - 8}" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n')
    parts.append("</svg>\n")
    return "".join(parts)


def gen_data_flow() -> str:
    t = T
    return (
        svg_header(900, 360)
        + '  <rect width="900" height="360" fill="#f8fafc"/>\n'
        + f'  <text x="450" y="30" text-anchor="middle" font-size="16" font-weight="700" fill="#0f172a">{t["data_flow"]}</text>\n'
        + arrow_def()
        + f'  <rect x="30" y="55" width="120" height="50" rx="6" fill="#fef3c7" stroke="#f59e0b"/><text x="90" y="85" text-anchor="middle" fill="#92400e" font-size="11" font-weight="600">{t["pdf"]}</text>\n'
        + '  <path d="M150 80 L190 80" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + f'  <rect x="192" y="55" width="130" height="50" rx="6" fill="#dbeafe" stroke="#3b82f6"/><text x="257" y="85" text-anchor="middle" fill="#1e40af" font-size="11" font-weight="600">{t["parse"]}</text>\n'
        + '  <path d="M322 80 L362 80" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + '  <rect x="364" y="55" width="150" height="50" rx="6" fill="#e0e7ff" stroke="#6366f1"/><text x="439" y="85" text-anchor="middle" fill="#3730a3" font-size="11" font-weight="600">PaperDocument</text>\n'
        + '  <path d="M514 80 L554 80" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + f'  <rect x="556" y="55" width="140" height="50" rx="6" fill="#d1fae5" stroke="#10b981"/><text x="626" y="85" text-anchor="middle" fill="#065f46" font-size="11" font-weight="600">{t["index"]}</text>\n'
        + '  <path d="M696 80 L736 80" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + '  <rect x="738" y="55" width="130" height="50" rx="6" fill="#ccfbf1" stroke="#0d9488"/><text x="803" y="85" text-anchor="middle" fill="#115e59" font-size="11" font-weight="600">PaperRegistry</text>\n'
        + '  <path d="M439 105 L439 140" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + f'  <rect x="300" y="142" width="280" height="40" rx="6" fill="#7c3aed"/><text x="440" y="168" text-anchor="middle" fill="white" font-size="12" font-weight="600">{t["lg_flow"]}</text>\n'
        + f'  <rect x="120" y="220" width="160" height="45" rx="6" fill="#fce7f3" stroke="#ec4899"/><text x="200" y="248" text-anchor="middle" fill="#9d174d" font-size="10" font-weight="600">{t["struct_out"]}</text>\n'
        + f'  <rect x="370" y="220" width="160" height="45" rx="6" fill="#ffedd5" stroke="#ea580c"/><text x="450" y="248" text-anchor="middle" fill="#9a3412" font-size="10" font-weight="600">{t["pydantic"]}</text>\n'
        + f'  <rect x="620" y="220" width="160" height="45" rx="6" fill="#e2e8f0" stroke="#475569"/><text x="700" y="248" text-anchor="middle" fill="#1e293b" font-size="10" font-weight="600">{t["md_report"]}</text>\n'
        + '  <path d="M440 182 L200 220" stroke="#64748b" stroke-width="1.5" marker-end="url(#arrow)"/>\n'
        + '  <path d="M440 182 L450 220" stroke="#64748b" stroke-width="1.5" marker-end="url(#arrow)"/>\n'
        + '  <path d="M440 182 L700 220" stroke="#64748b" stroke-width="1.5" marker-end="url(#arrow)"/>\n'
        + '  <path d="M700 265 L700 295" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>\n'
        + '  <rect x="610" y="297" width="180" height="40" rx="6" fill="#f1f5f9" stroke="#94a3b8"/><text x="700" y="322" text-anchor="middle" fill="#334155" font-size="11" font-weight="600">output/*.md</text>\n'
        + "</svg>\n"
    )


def main() -> None:
    IMAGES.mkdir(parents=True, exist_ok=True)
    svgs = {
        "system-layers.svg": gen_system_layers(),
        "workflow-read.svg": gen_workflow_read(),
        "workflow-full-read.svg": gen_workflow_full_read(),
        "workflow-qa.svg": gen_workflow_qa(),
        "workflow-compare.svg": gen_workflow_compare(),
        "rag-pipeline.svg": gen_rag_pipeline(),
        "data-flow.svg": gen_data_flow(),
    }
    for name, content in svgs.items():
        write(IMAGES / name, content)
        raw = (IMAGES / name).read_bytes()
        bad = [b for b in raw if b < 32 and b not in (9, 10, 13)]
        assert not bad, f"{name}: invalid bytes {bad}"
    print("SVG OK:", len(svgs), "files")


if __name__ == "__main__":
    main()
