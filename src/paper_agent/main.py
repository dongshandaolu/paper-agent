from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from paper_agent.config import get_settings
from paper_agent.graph.builder import build_compare_graph, build_full_read_graph, build_qa_graph, build_read_graph
from paper_agent.services.paper_service import get_paper_service
from paper_agent.state_factory import make_initial_state

app = typer.Typer(
    name="paper-agent",
    help="Multi-agent professional paper reading system",
    no_args_is_help=True,
)
console = Console()


def _validate_pdf(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.exists():
        raise typer.BadParameter(f"文件不存在: {path}")
    if resolved.suffix.lower() != ".pdf":
        raise typer.BadParameter(f"需要 PDF 文件: {path}")
    return resolved


def _initial_state(
    pdf_paths: list[Path],
    task: str,
    user_query: str | None = None,
    output_dir: str | None = None,
    full_read: bool = False,
) -> dict:
    return make_initial_state(
        pdf_paths=[str(p) for p in pdf_paths],
        task=task,
        user_query=user_query,
        output_dir=output_dir,
        full_read=full_read,
    )


@app.command("read")
def read_command(
    pdf: Path = typer.Argument(..., help="PDF 论文路径", exists=False),
    output: Path | None = typer.Option(None, "--output", "-o", help="报告输出目录"),
    full: bool = typer.Option(False, "--full", help="完整报告：结构+研究问题+术语+摘要+批判"),
) -> None:
    """阅读流程：解析 → 摘要 → 批判分析 → Markdown 笔记（--full 含结构/问题/术语）"""
    pdf_path = _validate_pdf(pdf)
    settings = get_settings()
    out_dir = str(output.resolve()) if output else settings.output_dir

    mode = "完整阅读" if full else "标准阅读"
    console.print(Panel(f"[bold]{mode}[/bold]\n{pdf_path}", title="Paper Agent"))

    graph = build_full_read_graph() if full else build_read_graph()
    task = "full_read" if full else "read"
    state = _initial_state([pdf_path], task=task, output_dir=out_dir, full_read=full)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("正在处理...", total=None)
        result = graph.invoke(state)
        progress.update(task, description="完成")

    report_path = result.get("report_path")
    if report_path:
        console.print(f"\n[green]报告已保存:[/green] {report_path}")
        content = Path(report_path).read_text(encoding="utf-8")
        preview = content[:3000] + ("..." if len(content) > 3000 else "")
        console.print(Markdown(preview))
    else:
        console.print("[yellow]未生成报告[/yellow]")


@app.command("ask")
def ask_command(
    question: str = typer.Argument(..., help="要问的问题"),
    paper: Path = typer.Option(..., "--paper", "-p", help="PDF 论文路径", exists=False),
) -> None:
    """基于论文内容的 RAG 问答"""
    pdf_path = _validate_pdf(paper)

    console.print(Panel(f"[bold]问答[/bold]\n{question}", title="Paper Agent"))

    graph = build_qa_graph()
    state = _initial_state([pdf_path], task="qa", user_query=question)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("检索并回答...", total=None)
        result = graph.invoke(state)
        progress.update(task, description="完成")

    answer = result.get("qa_answer")
    if not answer:
        console.print("[yellow]未获得回答[/yellow]")
        return

    console.print(f"\n[bold]回答:[/bold] {answer.answer}")
    console.print(f"[dim]置信度: {answer.confidence}[/dim]")
    if answer.citations:
        console.print("\n[bold]引用:[/bold]")
        for c in answer.citations:
            console.print(f"  - [{c.section}, p.{c.page}] {c.excerpt}")


@app.command("compare")
def compare_command(
    pdfs: list[Path] = typer.Argument(..., help="至少 2 篇 PDF 论文路径"),
    output: Path | None = typer.Option(None, "--output", "-o", help="报告输出目录"),
) -> None:
    """多篇论文横向对比"""
    if len(pdfs) < 2:
        raise typer.BadParameter("compare 命令至少需要 2 篇 PDF")

    pdf_paths = [_validate_pdf(p) for p in pdfs]
    settings = get_settings()
    out_dir = str(output.resolve()) if output else settings.output_dir

    names = "\n".join(f"- {p}" for p in pdf_paths)
    console.print(Panel(f"[bold]对比论文[/bold]\n{names}", title="Paper Agent"))

    graph = build_compare_graph()
    state = _initial_state(pdf_paths, task="compare", output_dir=out_dir)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("对比分析中...", total=None)
        result = graph.invoke(state)
        progress.update(task, description="完成")

    report_path = result.get("report_path")
    comparison = result.get("comparison")

    if report_path:
        console.print(f"\n[green]对比报告已保存:[/green] {report_path}")

    if comparison:
        console.print(f"\n[bold]综合评述:[/bold]\n{comparison.synthesis}")
        console.print(f"\n[bold]阅读建议:[/bold]\n{comparison.recommendation}")


@app.command("upload")
def upload_command(
    pdf: Path = typer.Argument(..., help="PDF 论文路径", exists=False),
) -> None:
    """上传论文到 Agent 库，返回 paper_id（供 MCP / 后续命令使用）"""
    pdf_path = _validate_pdf(pdf)
    result = get_paper_service().upload(str(pdf_path))
    console.print(Panel(
        f"[green]已上传[/green]\n"
        f"paper_id: [bold]{result['paper_id']}[/bold]\n"
        f"标题: {result['title']}\n"
        f"章节: {result['section_count']} | 页数: {result['page_count']}",
        title="Paper Agent",
    ))


@app.command("structure")
def structure_command(
    paper_id: str = typer.Argument(..., help="paper_id（upload 命令返回）"),
) -> None:
    """总结论文结构（章节大纲 + IMRaD + 阅读指南）"""
    structure = get_paper_service().summarize_structure(paper_id)
    console.print(Panel(f"[bold]{structure.title}[/bold]", title="论文结构"))
    for item in structure.outline:
        console.print(f"\n[cyan]{item.title}[/cyan] (p.{item.page_start}-{item.page_end})")
        console.print(item.summary)
    if structure.imrad_mapping:
        console.print("\n[bold]IMRaD 映射:[/bold]")
        for key, val in structure.imrad_mapping.items():
            console.print(f"  {key}: {val}")
    if structure.reading_guide:
        console.print(f"\n[bold]阅读指南:[/bold]\n{structure.reading_guide}")


@app.command("questions")
def questions_command(
    paper_id: str = typer.Argument(..., help="paper_id"),
) -> None:
    """提取研究问题与假设"""
    result = get_paper_service().extract_research_questions(paper_id)
    console.print(Panel(f"[bold]{result.title}[/bold]", title="研究问题"))
    if result.main_questions:
        console.print("\n[bold]主研究问题:[/bold]")
        for q in result.main_questions:
            console.print(f"  • {q.question} [{q.section}, p.{q.page}]")
    if result.sub_questions:
        console.print("\n[bold]子问题:[/bold]")
        for q in result.sub_questions:
            console.print(f"  • {q.question}")
    if result.hypotheses:
        console.print("\n[bold]假设:[/bold]")
        for h in result.hypotheses:
            console.print(f"  • {h}")


@app.command("terms")
def terms_command(
    paper_id: str = typer.Argument(..., help="paper_id"),
    term: list[str] = typer.Option(None, "--term", "-t", help="指定术语，可多次使用"),
    max_terms: int = typer.Option(10, "--max", help="自动提取时的最大术语数"),
) -> None:
    """解释论文中的专业术语"""
    result = get_paper_service().explain_terms(
        paper_id, terms=term or None, max_terms=max_terms
    )
    console.print(Panel(f"[bold]{result.title}[/bold]", title="术语解释"))
    for item in result.terms:
        console.print(f"\n[cyan]{item.term}[/cyan] [{item.section}, p.{item.page}]")
        if item.definition_in_paper:
            console.print(f"  论文表述: {item.definition_in_paper}")
        console.print(f"  通俗解释: {item.plain_explanation}")
        if item.related_terms:
            console.print(f"  相关术语: {', '.join(item.related_terms)}")


@app.command("mcp")
def mcp_command() -> None:
    """启动 MCP Server（stdio 模式，供 Claude Code / Cursor 调用）"""
    from paper_agent.mcp_server import main

    main()


if __name__ == "__main__":
    app()
