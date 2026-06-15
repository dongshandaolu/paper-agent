from paper_agent.state_defaults import _empty_state_fields

__all__ = ["make_initial_state"]


def make_initial_state(
    pdf_paths: list[str],
    task: str,
    user_query: str | None = None,
    output_dir: str | None = None,
    full_read: bool = False,
) -> dict:
    base = _empty_state_fields()
    base.update(
        {
            "pdf_paths": pdf_paths,
            "task": task,
            "full_read": full_read,
            "user_query": user_query,
            "documents": [],
            "summaries": [],
            "critiques": [],
            "comparison": None,
            "qa_answer": None,
            "report_path": None,
            "output_dir": output_dir,
            "messages": [],
        }
    )
    return base
