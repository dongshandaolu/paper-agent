"""
Paper Agent - 专业论文智能阅读助手 (Streamlit Web UI)
基于 src/paper_agent 核心系统构建
"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# 确保能导入 src/paper_agent
sys.path.insert(0, str(Path(__file__).parent / "src"))

# ─── 页面配置（必须最先调用）──────────────────────────────────────────────────
st.set_page_config(
    page_title="Paper Agent - 论文智能助手",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── 全局 CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.main-header{font-size:2.2rem;color:#1f77b4;text-align:center;
             margin-bottom:1.5rem;font-weight:bold;}
.sub-header{font-size:1.3rem;color:#ff7f0e;margin-top:1.2rem;
            margin-bottom:.8rem;border-bottom:2px solid #ff7f0e;
            padding-bottom:.4rem;}
.info-box{background:#e8f4f8;padding:1.2rem;border-radius:8px;
          border-left:5px solid #1f77b4;margin:.8rem 0;}
.success-box{background:#d4edda;padding:1.2rem;border-radius:8px;
             border-left:5px solid #28a745;margin:.8rem 0;}
.warn-box{background:#fff3cd;padding:1.2rem;border-radius:8px;
          border-left:5px solid #ffc107;margin:.8rem 0;}
.card{padding:1.2rem;border-radius:10px;margin:.4rem 0;
      box-shadow:0 2px 6px rgba(0,0,0,.1);}
</style>
""", unsafe_allow_html=True)

# ─── Session State 初始化 ──────────────────────────────────────────────────────
_defaults: dict = {
    "paper_id": None,          # 当前论文 paper_id
    "paper_info": None,        # upload 返回的基本信息 dict
    "summary": None,           # PaperSummary.model_dump()
    "critique": None,          # PaperCritique.model_dump()
    "structure": None,         # PaperStructure.model_dump()
    "research_questions": None,# ResearchQuestionsResult.model_dump()
    "terminology": None,       # TerminologyResult.model_dump()
    "qa_history": [],          # [(question, answer_obj)]
    "report_path": None,       # 最近生成的报告路径
    "uploaded_papers": [],     # list[dict] 已上传论文列表
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def _svc():
    """懒加载 PaperService（只在第一次调用时初始化）"""
    from paper_agent.services.paper_service import get_paper_service
    return get_paper_service()


def _refresh_paper_list():
    st.session_state.uploaded_papers = _svc().list_papers()


# ─── 主标题 ───────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="main-header">📚 Paper Agent — 专业论文智能阅读助手</div>',
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════════════════════════════
# 侧边栏
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1.5rem 0;
         background:linear-gradient(135deg,#667eea,#764ba2);
         border-radius:12px;margin-bottom:1rem;">
      <h1 style="color:white;font-size:2.5rem;margin:0;">📚</h1>
      <h3 style="color:white;margin:.5rem 0 0 0;">Paper Agent</h3>
      <p style="color:rgba(255,255,255,.8);font-size:.85rem;margin:.2rem 0 0 0;">
        多 Agent 专业论文阅读系统
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎯 核心功能")
    st.markdown("""
    - 📤 上传 / 管理论文 PDF
    - 📊 论文结构分析（IMRaD）
    - ❓ RAG 问答（附页码引用）
    - 📝 结构化摘要生成
    - 🔍 批判性评估
    - 💬 专业术语解释
    - 🔬 研究问题提取
    - 📄 Markdown 报告导出
    """)

    st.markdown("---")

    # 当前论文信息
    if st.session_state.paper_info:
        info = st.session_state.paper_info
        st.markdown("### 📌 当前论文")
        st.markdown(f"""
        <div class="info-box" style="font-size:.9rem;">
          <b>{info.get('title','Untitled')[:50]}</b><br/>
          📄 {info.get('page_count',0)} 页 &nbsp;|&nbsp;
          📚 {info.get('section_count',0)} 章节<br/>
          <small style="color:#555;">ID: {info.get('paper_id','')[:12]}…</small>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("尚未选择论文，请在「上传」标签页上传或选择。")

    st.markdown("---")
    st.markdown("### 📊 论文库")
    if st.button("🔄 刷新论文列表", use_container_width=True):
        _refresh_paper_list()

    papers = st.session_state.uploaded_papers
    if papers:
        st.markdown(f"共 **{len(papers)}** 篇已上传")
        for p in papers:
            if st.button(
                f"📄 {p['title'][:25]}…" if len(p["title"]) > 25 else f"📄 {p['title']}",
                key=f"sel_{p['paper_id']}",
                use_container_width=True,
            ):
                st.session_state.paper_id = p["paper_id"]
                st.session_state.paper_info = p
                # 清除上一篇的分析缓存
                for key in ("summary", "critique", "structure", "research_questions",
                            "terminology", "qa_history", "report_path"):
                    st.session_state[key] = [] if key == "qa_history" else None
                st.rerun()
    else:
        st.caption("暂无已上传论文，请先上传。")

# ═══════════════════════════════════════════════════════════════════════════════
# 主区域：标签页
# ═══════════════════════════════════════════════════════════════════════════════
tab_upload, tab_structure, tab_summary, tab_qa, tab_terms, tab_report = st.tabs([
    "📤 上传论文",
    "📊 结构分析",
    "📝 摘要 & 评估",
    "❓ 论文问答",
    "💬 术语 & 研究问题",
    "📄 生成报告",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — 上传论文
# ─────────────────────────────────────────────────────────────────────────────
with tab_upload:
    st.markdown('<div class="sub-header">📤 上传 PDF 论文</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
      <b>💡 使用说明</b><br/>
      1. 在下方输入 PDF 文件的完整路径，点击「上传并解析」<br/>
      2. 解析完成后论文会自动进入论文库，左侧可切换当前论文<br/>
      3. 切换到其他标签页使用 AI 分析功能
    </div>
    """, unsafe_allow_html=True)

    col_input, col_btn = st.columns([4, 1])
    with col_input:
        pdf_path_input = st.text_input(
            "📁 PDF 文件路径",
            placeholder="例如: D:\\papers\\my_paper.pdf",
            label_visibility="collapsed",
        )
    with col_btn:
        upload_btn = st.button("🚀 上传并解析", type="primary", use_container_width=True)

    if upload_btn:
        if not pdf_path_input.strip():
            st.error("❌ 请输入 PDF 路径")
        elif not Path(pdf_path_input.strip()).exists():
            st.error(f"❌ 文件不存在: {pdf_path_input}")
        else:
            with st.spinner("📖 正在解析并索引论文，请稍候..."):
                try:
                    info = _svc().upload(pdf_path_input.strip())
                    st.session_state.paper_id = info["paper_id"]
                    st.session_state.paper_info = info
                    for key in ("summary", "critique", "structure", "research_questions",
                                "terminology", "qa_history", "report_path"):
                        st.session_state[key] = [] if key == "qa_history" else None
                    _refresh_paper_list()
                    st.success(f"✅ 上传成功！标题：{info['title']}")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ 上传失败: {e}")

    # 已上传论文列表
    st.markdown("---")
    st.markdown("### 📚 已上传论文库")
    if st.button("🔄 刷新", key="refresh_main"):
        _refresh_paper_list()

    papers = st.session_state.uploaded_papers
    if not papers:
        _refresh_paper_list()
        papers = st.session_state.uploaded_papers

    if papers:
        import pandas as pd
        df = pd.DataFrame([{
            "标题": p["title"],
            "页数": p["page_count"],
            "章节": p["section_count"],
            "上传时间": p.get("uploaded_at", "")[:19],
            "paper_id": p["paper_id"],
        } for p in papers])
        st.dataframe(df.drop(columns=["paper_id"]), use_container_width=True)
    else:
        st.info("暂无论文，请先上传。")

    # 显示当前论文基本信息
    if st.session_state.paper_info:
        info = st.session_state.paper_info
        st.markdown("---")
        st.markdown("### 📋 当前论文基本信息")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📄 页数", info.get("page_count", 0))
        c2.metric("📚 章节", info.get("section_count", 0))
        c3.metric("🔑 Paper ID", info.get("paper_id", "")[:8] + "…")
        c4.metric("📑 摘要预览", "✅" if info.get("abstract_preview") else "—")

        if info.get("abstract_preview"):
            with st.expander("📝 摘要预览"):
                st.write(info["abstract_preview"])

        if info.get("sections"):
            with st.expander(f"📑 章节列表（{len(info['sections'])} 个）"):
                for i, sec in enumerate(info["sections"], 1):
                    st.write(f"{i}. {sec}")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — 结构分析
# ─────────────────────────────────────────────────────────────────────────────
with tab_structure:
    st.markdown('<div class="sub-header">📊 论文结构分析</div>', unsafe_allow_html=True)

    if not st.session_state.paper_id:
        st.markdown('<div class="warn-box">⚠️ 请先在「上传论文」标签页上传并选择一篇论文。</div>',
                    unsafe_allow_html=True)
    else:
        if st.button("🔍 分析论文结构", type="primary"):
            with st.spinner("正在分析结构（IMRaD 映射）…"):
                try:
                    result = _svc().summarize_structure(st.session_state.paper_id, use_cache=False)
                    st.session_state.structure = result.model_dump()
                except Exception as e:
                    st.error(f"❌ 分析失败: {e}")

        structure = st.session_state.structure
        if structure:
            st.markdown(f"### 📑 {structure.get('title', '')}")

            # 章节大纲
            outline = structure.get("outline", [])
            if outline:
                st.markdown("#### 📚 章节大纲")
                for sec in outline:
                    indent = "　" * (sec.get("level", 1) - 1)
                    st.markdown(
                        f"{indent}**{sec['title']}** (p.{sec['page_start']}–{sec['page_end']})"
                    )
                    if sec.get("summary"):
                        st.caption(f"{indent}　{sec['summary']}")

            st.markdown("---")

            # IMRaD 映射
            imrad = structure.get("imrad_mapping", {})
            if imrad:
                st.markdown("#### 🗺️ IMRaD 映射")
                cols = st.columns(len(imrad))
                for i, (k, v) in enumerate(imrad.items()):
                    with cols[i]:
                        st.markdown(f"""
                        <div style="background:linear-gradient(135deg,#667eea,#764ba2);
                                    padding:1rem;border-radius:10px;text-align:center;color:white;">
                          <b>{k}</b><br/><small>{v[:60]}</small>
                        </div>""", unsafe_allow_html=True)

            # 阅读指南
            guide = structure.get("reading_guide", "")
            if guide:
                st.markdown("---")
                st.markdown("#### 🧭 阅读指南")
                st.markdown(f"""
                <div class="success-box">{guide}</div>
                """, unsafe_allow_html=True)
        else:
            st.info("点击上方按钮开始结构分析。")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — 摘要 & 批判性评估
# ─────────────────────────────────────────────────────────────────────────────
with tab_summary:
    st.markdown('<div class="sub-header">📝 结构化摘要 & 批判性评估</div>', unsafe_allow_html=True)

    if not st.session_state.paper_id:
        st.markdown('<div class="warn-box">⚠️ 请先上传并选择一篇论文。</div>', unsafe_allow_html=True)
    else:
        col_full, col_std = st.columns(2)
        with col_full:
            full_read_btn = st.button("🚀 完整阅读（含结构/问题/术语）", type="primary",
                                      use_container_width=True)
        with col_std:
            std_read_btn = st.button("📝 标准阅读（摘要 + 批判）",
                                     use_container_width=True)

        if full_read_btn or std_read_btn:
            with st.spinner("AI 正在深度阅读论文，可能需要 1–3 分钟…"):
                try:
                    result = _svc().read_full(
                        st.session_state.paper_id,
                        full=bool(full_read_btn),
                    )
                    if result.get("summary"):
                        st.session_state.summary = result["summary"]
                    if result.get("critique"):
                        st.session_state.critique = result["critique"]
                    if result.get("structure"):
                        st.session_state.structure = result["structure"]
                    if result.get("research_questions"):
                        st.session_state.research_questions = result["research_questions"]
                    if result.get("terminology"):
                        st.session_state.terminology = result["terminology"]
                    if result.get("report_path"):
                        st.session_state.report_path = result["report_path"]
                    st.success("✅ 阅读完成！")
                except Exception as e:
                    st.error(f"❌ 阅读失败: {e}")

        # 摘要展示
        summary = st.session_state.summary
        if summary:
            st.markdown("---")
            st.markdown(f"### 📋 {summary.get('title', '')}")
            st.markdown("#### 🔬 结构化摘要（IMRaD）")

            fields = [
                ("🎯 研究问题", "problem"),
                ("💡 研究动机", "motivation"),
                ("🛠️ 核心方法", "method"),
                ("🧪 实验设置", "experiments"),
                ("📈 主要结果", "results"),
                ("✅ 结论", "conclusions"),
            ]
            for label, key in fields:
                val = summary.get(key, "")
                if val:
                    st.markdown(f"**{label}**")
                    st.markdown(f"""
                    <div class="info-box" style="margin:.3rem 0 .8rem 0;">{val}</div>
                    """, unsafe_allow_html=True)

            contribs = summary.get("key_contributions", [])
            if contribs:
                st.markdown("**🏆 主要贡献**")
                for i, c in enumerate(contribs, 1):
                    st.markdown(f"- {i}. {c}")

            citations = summary.get("citations", [])
            if citations:
                with st.expander(f"📎 引用依据（{len(citations)} 条）"):
                    for cite in citations:
                        st.markdown(
                            f"- [{cite.get('section','')} p.{cite.get('page',0)}] "
                            f"_{cite.get('excerpt','')}_"
                        )

        # 批判性评估展示
        critique = st.session_state.critique
        if critique:
            st.markdown("---")
            st.markdown("#### 🔍 批判性评估")
            st.write(f"**总体评价：** {critique.get('overall_assessment', '')}")

            dim_keys = [
                ("innovation", "🚀 创新性"),
                ("methodology_rigor", "⚙️ 方法严谨性"),
                ("experimental_adequacy", "🧪 实验充分性"),
                ("reproducibility", "🔄 可复现性"),
            ]
            score_cols = st.columns(4)
            for i, (k, label) in enumerate(dim_keys):
                dim = critique.get(k)
                if dim:
                    with score_cols[i]:
                        score = dim.get("score", 0)
                        color = "#4caf50" if score >= 4 else ("#ff9800" if score >= 3 else "#f44336")
                        st.markdown(f"""
                        <div style="background:{color};padding:1rem;border-radius:10px;
                                    text-align:center;color:white;margin:.3rem 0;">
                          <div style="font-size:2rem;font-weight:bold;">{score}/5</div>
                          <div style="font-size:.85rem;">{label}</div>
                        </div>""", unsafe_allow_html=True)
                        with st.expander("详情"):
                            st.write(dim.get("rationale", ""))

            col_s, col_l = st.columns(2)
            with col_s:
                strengths = critique.get("strengths", [])
                if strengths:
                    st.markdown("**✅ 优势**")
                    for s in strengths:
                        st.markdown(f"- {s}")
            with col_l:
                limitations = critique.get("limitations", [])
                if limitations:
                    st.markdown("**⚠️ 局限**")
                    for l in limitations:
                        st.markdown(f"- {l}")

        if not summary and not critique:
            st.info("点击上方按钮开始阅读分析。")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — RAG 论文问答
# ─────────────────────────────────────────────────────────────────────────────
with tab_qa:
    st.markdown('<div class="sub-header">❓ 基于论文内容的 RAG 问答</div>', unsafe_allow_html=True)

    if not st.session_state.paper_id:
        st.markdown('<div class="warn-box">⚠️ 请先上传并选择一篇论文。</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="info-box">
          提问后 AI 会从论文中检索相关段落并生成回答，附章节和页码引用。
        </div>
        """, unsafe_allow_html=True)

        with st.form("qa_form", clear_on_submit=True):
            question = st.text_input(
                "💬 输入问题",
                placeholder="例如：这篇论文提出了什么方法？实验结果如何？",
            )
            submitted = st.form_submit_button("🔍 提问", use_container_width=True)

        if submitted and question.strip():
            with st.spinner("检索论文内容并生成回答…"):
                try:
                    answer = _svc().ask(st.session_state.paper_id, question.strip())
                    st.session_state.qa_history.insert(0, (question.strip(), answer))
                except Exception as e:
                    st.error(f"❌ 问答失败: {e}")

        # 历史对话
        history = st.session_state.qa_history
        if history:
            st.markdown("---")
            for i, (q, a) in enumerate(history):
                confidence_color = {
                    "high": "#4caf50", "medium": "#ff9800", "low": "#f44336"
                }.get(getattr(a, "confidence", "medium"), "#ff9800")

                st.markdown(f"""
                <div class="card" style="background:#f0f4ff;border-left:4px solid #3f51b5;">
                  <b>❓ Q{i+1}:</b> {q}
                </div>""", unsafe_allow_html=True)

                answer_text = getattr(a, "answer", str(a))
                confidence = getattr(a, "confidence", "medium")
                st.markdown(f"""
                <div class="card" style="background:#f1f8e9;border-left:4px solid #4caf50;">
                  <b>💡 回答</b>
                  <span style="float:right;background:{confidence_color};color:white;
                        padding:.15rem .6rem;border-radius:10px;font-size:.8rem;">
                    {confidence}
                  </span><br/>{answer_text}
                </div>""", unsafe_allow_html=True)

                citations = getattr(a, "citations", [])
                if citations:
                    with st.expander(f"📎 引用来源（{len(citations)} 条）"):
                        for cite in citations:
                            section = getattr(cite, "section", "")
                            page = getattr(cite, "page", 0)
                            excerpt = getattr(cite, "excerpt", "")
                            st.markdown(f"- **[{section}, p.{page}]** _{excerpt}_")

                st.markdown("")
        else:
            st.info("向论文提问，AI 会基于原文内容回答。")

        if history:
            if st.button("🗑️ 清空问答历史"):
                st.session_state.qa_history = []
                st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — 术语解释 & 研究问题
# ─────────────────────────────────────────────────────────────────────────────
with tab_terms:
    st.markdown('<div class="sub-header">💬 术语解释 & 研究问题提取</div>', unsafe_allow_html=True)

    if not st.session_state.paper_id:
        st.markdown('<div class="warn-box">⚠️ 请先上传并选择一篇论文。</div>', unsafe_allow_html=True)
    else:
        col_t, col_q = st.columns(2)

        # ── 术语解释 ─────────────────────────────────────────────
        with col_t:
            st.markdown("#### 📖 术语解释")
            terms_input = st.text_input(
                "指定术语（逗号分隔，留空自动提取）",
                placeholder="例如: LSTM, attention mechanism",
                key="terms_input",
            )
            max_terms = st.slider("自动提取最大术语数", 3, 20, 10)

            if st.button("🔍 提取 & 解释术语", use_container_width=True):
                with st.spinner("提取术语中…"):
                    try:
                        terms_list = (
                            [t.strip() for t in terms_input.split(",") if t.strip()]
                            if terms_input.strip()
                            else None
                        )
                        result = _svc().explain_terms(
                            st.session_state.paper_id,
                            terms=terms_list,
                            max_terms=max_terms,
                            use_cache=False,
                        )
                        st.session_state.terminology = result.model_dump()
                    except Exception as e:
                        st.error(f"❌ 术语提取失败: {e}")

            terminology = st.session_state.terminology
            if terminology:
                terms = terminology.get("terms", [])
                for term_item in terms:
                    term_name = term_item.get("term", "")
                    section = term_item.get("section", "")
                    page = term_item.get("page", 0)
                    definition = term_item.get("definition_in_paper", "")
                    plain = term_item.get("plain_explanation", "")
                    math_expr = term_item.get("math_expression", "")
                    math_exp = term_item.get("math_explanation", "")
                    related = term_item.get("related_terms", [])

                    with st.expander(f"🔑 {term_name}  [{section}, p.{page}]"):
                        if definition:
                            st.markdown(f"**论文表述:** {definition}")
                        if plain:
                            st.markdown(f"**通俗解释:** {plain}")
                        if math_expr:
                            st.markdown(f"**数学表达:** `{math_expr}`")
                        if math_exp:
                            st.markdown(f"**符号说明:** {math_exp}")
                        if related:
                            st.markdown(f"**相关术语:** {', '.join(related)}")
            else:
                st.caption("点击上方按钮提取术语。")

        # ── 研究问题 ─────────────────────────────────────────────
        with col_q:
            st.markdown("#### 🎯 研究问题提取")

            if st.button("🔍 提取研究问题", use_container_width=True):
                with st.spinner("提取研究问题中…"):
                    try:
                        result = _svc().extract_research_questions(
                            st.session_state.paper_id, use_cache=False
                        )
                        st.session_state.research_questions = result.model_dump()
                    except Exception as e:
                        st.error(f"❌ 提取失败: {e}")

            rq = st.session_state.research_questions
            if rq:
                main_qs = rq.get("main_questions", [])
                sub_qs = rq.get("sub_questions", [])
                hypotheses = rq.get("hypotheses", [])

                if main_qs:
                    st.markdown("**🎯 主研究问题**")
                    for q in main_qs:
                        st.markdown(f"""
                        <div class="card" style="background:#e8eaf6;border-left:4px solid #3f51b5;">
                          {q.get('question','')}
                          <br/><small style="color:#666;">[{q.get('section','')} p.{q.get('page',0)}]</small>
                        </div>""", unsafe_allow_html=True)

                if sub_qs:
                    st.markdown("**🔍 子问题**")
                    for q in sub_qs:
                        st.markdown(f"- {q.get('question', '')}")

                if hypotheses:
                    st.markdown("**💭 假设**")
                    for h in hypotheses:
                        st.markdown(f"- {h}")
            else:
                st.caption("点击上方按钮提取研究问题。")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6 — 生成报告
# ─────────────────────────────────────────────────────────────────────────────
with tab_report:
    st.markdown('<div class="sub-header">📄 生成 & 下载报告</div>', unsafe_allow_html=True)

    if not st.session_state.paper_id:
        st.markdown('<div class="warn-box">⚠️ 请先上传并选择一篇论文。</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="info-box">
          点击下方按钮生成完整的 Markdown 阅读报告（含结构化摘要、批判性评估等），
          可直接下载保存。
        </div>
        """, unsafe_allow_html=True)

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            gen_std = st.button("📝 生成标准报告", use_container_width=True)
        with col_b2:
            gen_full = st.button("🚀 生成完整报告（推荐）", type="primary", use_container_width=True)

        if gen_std or gen_full:
            with st.spinner("正在生成报告…"):
                try:
                    result = _svc().read_full(
                        st.session_state.paper_id, full=bool(gen_full)
                    )
                    if result.get("summary"):
                        st.session_state.summary = result["summary"]
                    if result.get("critique"):
                        st.session_state.critique = result["critique"]
                    if result.get("structure"):
                        st.session_state.structure = result["structure"]
                    if result.get("research_questions"):
                        st.session_state.research_questions = result["research_questions"]
                    if result.get("terminology"):
                        st.session_state.terminology = result["terminology"]
                    if result.get("report_path"):
                        st.session_state.report_path = result["report_path"]
                        st.success(f"✅ 报告已生成: {result['report_path']}")
                    else:
                        st.warning("⚠️ 报告内容已生成，但未写入文件。")
                except Exception as e:
                    st.error(f"❌ 生成失败: {e}")

        # 报告文件下载
        report_path = st.session_state.report_path
        if report_path and Path(report_path).exists():
            st.markdown("---")
            st.markdown(f"**📂 报告路径：** `{report_path}`")
            report_content = Path(report_path).read_text(encoding="utf-8")

            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button(
                    label="📥 下载 Markdown 报告",
                    data=report_content,
                    file_name=Path(report_path).name,
                    mime="text/markdown",
                    use_container_width=True,
                )
            with col_dl2:
                txt_content = (
                    report_content
                    .replace("#", "").replace("**", "").replace("*", "")
                    .replace("_", "").replace("`", "")
                )
                st.download_button(
                    label="📥 下载纯文本报告",
                    data=txt_content,
                    file_name=Path(report_path).stem + ".txt",
                    mime="text/plain",
                    use_container_width=True,
                )

            st.markdown("---")
            st.markdown("### 👁️ 报告预览")
            with st.expander("展开查看完整报告", expanded=False):
                st.markdown(report_content)

        elif not report_path:
            # 如果已有 session 数据，在页面上实时渲染摘要和评估
            summary = st.session_state.summary
            critique = st.session_state.critique

            if summary or critique:
                st.markdown("---")
                st.markdown("### 📋 当前分析结果（尚未生成文件）")
                if summary:
                    st.markdown(f"**论文：** {summary.get('title', '')}")
                    for label, key in [("研究问题", "problem"), ("方法", "method"),
                                       ("结果", "results"), ("结论", "conclusions")]:
                        if summary.get(key):
                            st.markdown(f"**{label}：** {summary[key]}")
                if critique and critique.get("overall_assessment"):
                    st.markdown(f"**总体评价：** {critique['overall_assessment']}")
            else:
                st.info("点击上方按钮生成报告。")

# ─────────────────────────────────────────────────────────────────────────────
# 页脚
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#888;padding:1rem 0 .5rem;">
  <b>Paper Agent</b> — 多 Agent 专业论文阅读系统 &nbsp;|&nbsp;
  LangGraph · ChromaDB · LLM
</div>
""", unsafe_allow_html=True)
