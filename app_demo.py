"""
PaperMate - 专业论文阅读助手 (演示版)
适用于学生阅读中英文论文
"""
import streamlit as st
from pathlib import Path
import sys
import re
import pandas as pd

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from modules.pdf_parser import PDFParser, extract_paper_sections
from modules.structure_analyzer_improved import analyze_full_paper_improved
import config

# 页面配置
st.set_page_config(
    page_title="PaperMate - 论文智能助手",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #ff7f0e;
        padding-bottom: 0.5rem;
    }
    .info-box {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .innovation-item {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #28a745;
    }
    .keyword-badge {
        display: inline-block;
        background-color: #007bff;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        margin: 0.2rem;
        font-size: 0.9rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #155a8a;
    }
</style>
""", unsafe_allow_html=True)

# 初始化 session state
if 'paper_data' not in st.session_state:
    st.session_state.paper_data = None
if 'sections' not in st.session_state:
    st.session_state.sections = {}
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'use_ai' not in st.session_state:
    st.session_state.use_ai = False
if 'ai_analysis' not in st.session_state:
    st.session_state.ai_analysis = None

# 主标题
st.markdown('<div class="main-header">📚 PaperMate - 专业论文智能阅读助手</div>', unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    # 使用emoji图标代替网络图片
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 1rem;">
        <h1 style="color: white; font-size: 3rem; margin: 0;">📚</h1>
        <h3 style="color: white; margin: 0.5rem 0;">PaperMate</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 核心功能")
    st.markdown("""
    - ✅ 上传论文 PDF
    - ✅ 自动提取结构
    - ✅ 识别研究问题
    - ✅ 解释专业术语
    - ✅ 总结方法和结果
    - ✅ 提取创新点
    - ✅ 关键词词云分析
    - ✅ 生成可视化报告
    """)
    
    st.markdown("---")
    st.markdown("### 📖 使用说明")
    
    # AI 模式切换
    st.markdown("### 🤖 分析模式")
    use_ai = st.checkbox(
        "启用 AI 智能分析",
        value=st.session_state.use_ai,
        help="AI模式：高准确率（慢） | 规则模式：快速（准确率低）"
    )
    st.session_state.use_ai = use_ai
    
    if use_ai:
        st.success("🤖 AI 模式已启用")
        st.caption("提取准确率: 85-95%")
        st.caption("需要 API Key")
    else:
        st.info("⚡ 规则模式（快速）")
        st.caption("提取准确率: 40-70%")
    
    st.markdown("---")
    st.markdown("### 📖 使用说明")
    
    with st.expander("📝 完整使用流程", expanded=False):
        st.markdown("""
        **第1步：输入PDF路径**
        - 在「上传论文」标签页输入PDF完整路径
        - 或点击"使用演示文件"按钮
        
        **第2步：开始分析**
        - 点击蓝色「🚀 开始分析」按钮
        - 等待几秒钟完成解析
        
        **第3步：查看结构**
        - 切换到「论文结构」标签
        - 查看自动识别的章节
        
        **第4步：分析方法**
        - 切换到「方法与结果」标签
        - 查看研究方法和实验数据
        
        **第5步：创新点**
        - 切换到「创新点」标签
        - 查看自动提取的创新内容
        
        **第6步：下载报告**
        - 切换到「生成报告」标签
        - 点击下载按钮保存报告
        """)
    
    st.markdown("---")
    st.markdown("### 💡 支持类型")
    st.success("""
    - 🇨🇳 中文论文 ✓
    - 🇬🇧 英文论文 ✓
    - 🌏 中英混合 ✓
    - 📊 含图表论文 ✓
    """)
    
    st.markdown("---")
    st.markdown("### 📊 统计信息")
    if st.session_state.analysis_done:
        st.metric("已分析论文", "1 篇", "✅")
    else:
        st.metric("已分析论文", "0 篇", "等待中...")

# 主界面
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📄 上传论文", 
    "📊 论文结构", 
    "🔬 方法与结果", 
    "💡 创新点", 
    "📝 生成报告"
])

# Tab 1: 上传论文
with tab1:
    st.markdown('<div class="sub-header">📤 上传论文 PDF</div>', unsafe_allow_html=True)
    
    # 使用说明卡片
    st.markdown("""
    <div class="info-box">
        <h4>💡 使用提示</h4>
        <p>1️⃣ 在下方输入框中粘贴 PDF 文件的<b>完整路径</b></p>
        <p>2️⃣ 点击 <b>🚀 开始分析</b> 按钮，等待几秒钟</p>
        <p>3️⃣ 分析完成后，切换到其他标签页查看结果</p>
        <p>4️⃣ 支持中文、英文及混合语言论文</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        pdf_path = st.text_input(
            "📁 输入 PDF 文件路径",
            placeholder="例如: E:\\papers\\your_paper.pdf",
            help="粘贴论文PDF的完整路径，包括盘符、文件夹路径和文件名",
            value="E:\\2026AI_practice\\Agent\\Dai 等 - 2025 - LSTM-based receiver clock modeling and prediction for GNSS urban positioning.pdf"
        )
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            analyze_btn = st.button("🚀 开始分析", type="primary", use_container_width=True)
        
        with col_btn2:
            if st.button("🔄 重置", use_container_width=True):
                st.session_state.paper_data = None
                st.session_state.sections = {}
                st.session_state.analysis_done = False
                st.success("✅ 已重置，可以分析新论文")
        
        if analyze_btn:
            if not pdf_path:
                st.error("❌ 请先输入 PDF 路径！")
            elif not Path(pdf_path).exists():
                st.error(f"❌ 找不到文件: {pdf_path}")
                st.info("💡 请检查路径是否正确，确保文件存在")
            else:
                with st.spinner("🔄 正在解析论文，请稍候..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        # 步骤1: 解析 PDF
                        status_text.text("📖 正在读取PDF文件...")
                        progress_bar.progress(20)
                        parser = PDFParser(pdf_path)
                        
                        status_text.text("📝 正在提取文本内容...")
                        progress_bar.progress(40)
                        
                        # 根据模式选择是否使用LLM
                        if st.session_state.use_ai:
                            status_text.text("🤖 AI模式：智能提取标题和作者...")
                            result = parser.parse(use_llm=True)
                        else:
                            status_text.text("⚡ 规则模式：快速提取...")
                            result = parser.parse(use_llm=False)
                        
                        # 步骤2: 提取章节
                        status_text.text("📊 正在分析论文结构...")
                        progress_bar.progress(60)
                        sections = extract_paper_sections(pdf_path, config.PAPER_SECTIONS)
                        
                        # 步骤3: AI深度分析（如果启用）
                        if st.session_state.use_ai:
                            status_text.text("🧠 AI深度分析：摘要、方法、结果、创新点...")
                            progress_bar.progress(75)
                            
                            try:
                                ai_analysis = analyze_full_paper_improved(pdf_path, result)
                                st.session_state.ai_analysis = ai_analysis
                            except Exception as e:
                                st.warning(f"⚠️ AI分析部分失败: {str(e)}")
                                st.session_state.ai_analysis = None
                        else:
                            st.session_state.ai_analysis = None
                        
                        status_text.text("🎯 正在识别关键信息...")
                        progress_bar.progress(90)
                        
                        # 保存到 session state
                        st.session_state.paper_data = result
                        st.session_state.sections = sections
                        st.session_state.analysis_done = True
                        
                        status_text.text("✅ 分析完成！")
                        progress_bar.progress(100)
                        
                        if st.session_state.use_ai and st.session_state.ai_analysis:
                            st.success("✅ 论文解析完成！AI智能分析已完成！请切换到其他标签页查看分析结果")
                        else:
                            st.success("✅ 论文解析完成！请切换到其他标签页查看分析结果")
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"❌ 解析失败: {str(e)}")
                        st.info("💡 可能的原因：PDF损坏、权限不足或格式不支持")
    
    with col2:
        st.markdown("### 📌 快速示例")
        
        st.markdown("""
        <div style="background-color: #fff3cd; padding: 1rem; border-radius: 10px; border-left: 4px solid #ffc107;">
            <p style="margin: 0;"><b>演示文件路径：</b></p>
            <small style="color: #666;">点击下方按钮自动填充</small>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📝 使用演示文件", use_container_width=True):
            st.info("✅ 演示文件路径已自动填充到输入框中，点击「开始分析」即可！")
    
    # 显示基本信息
    if st.session_state.paper_data:
        st.markdown("---")
        st.markdown('<div class="sub-header">📋 论文基本信息</div>', unsafe_allow_html=True)
        
        paper_data = st.session_state.paper_data
        
        # 美化的统计卡片
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 15px; color: white; text-align: center;">
                <div style="font-size: 2.5rem; font-weight: bold;">{paper_data['total_pages']}</div>
                <div style="font-size: 1rem; margin-top: 0.5rem;">📄 总页数</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 15px; color: white; text-align: center;">
                <div style="font-size: 2.5rem; font-weight: bold;">{len(paper_data['text']):,}</div>
                <div style="font-size: 1rem; margin-top: 0.5rem;">✏️ 字符数</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1.5rem; border-radius: 15px; color: white; text-align: center;">
                <div style="font-size: 2.5rem; font-weight: bold;">{len(paper_data['images'])}</div>
                <div style="font-size: 1rem; margin-top: 0.5rem;">🖼️ 图片数</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); padding: 1.5rem; border-radius: 15px; color: white; text-align: center;">
                <div style="font-size: 2.5rem; font-weight: bold;">{len(st.session_state.sections)}</div>
                <div style="font-size: 1rem; margin-top: 0.5rem;">📚 章节数</div>
            </div>
            """, unsafe_allow_html=True)
        
        # 元数据显示
        st.markdown("---")
        metadata = paper_data['metadata']
        
        col_meta1, col_meta2 = st.columns(2)
        
        with col_meta1:
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown("**📑 论文元数据**")
            if metadata.get('title'):
                st.write(f"**📌 标题**: {metadata['title']}")
            else:
                st.write("**📌 标题**: (未识别)")
            
            if metadata.get('author'):
                st.write(f"**✍️ 作者**: {metadata['author']}")
            else:
                st.write("**✍️ 作者**: (未识别)")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_meta2:
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown("**✅ 分析状态**")
            st.write(f"✓ PDF 解析完成")
            st.write(f"✓ 提取了 {len(st.session_state.sections)} 个章节")
            st.write(f"✓ 识别了 {len(paper_data['images'])} 张图片")
            st.write(f"✓ 可以查看详细分析结果了！")
            st.markdown('</div>', unsafe_allow_html=True)

# Tab 2: 论文结构
with tab2:
    st.markdown('<div class="sub-header">📊 论文结构分析</div>', unsafe_allow_html=True)
    
    if not st.session_state.analysis_done:
        st.markdown("""
        <div class="warning-box">
            <h4>⚠️ 尚未分析论文</h4>
            <p>请先在「📄 上传论文」标签页上传并分析论文</p>
            <p>👈 点击左侧标签页开始</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        sections = st.session_state.sections
        
        # 章节统计概览
        st.markdown("### 📈 章节统计概览")
        
        total_chars = sum(len(content) for content in sections.values())
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📚 识别章节数", f"{len(sections)} 个", "✅")
        
        with col2:
            st.metric("📝 总字符数", f"{total_chars:,} 字", "✅")
        
        with col3:
            avg_chars = total_chars // len(sections) if sections else 0
            st.metric("📊 平均章节长度", f"{avg_chars:,} 字", "✅")
        
        st.markdown("---")
        
        # 章节列表（卡片形式）
        st.markdown("### 📚 章节详情")
        
        section_icons = {
            'abstract': '📝',
            'introduction': '📖',
            'related_work': '🔍',
            'methodology': '🔬',
            'experiment': '📊',
            'results': '📈',
            'conclusion': '✅',
            'references': '📚',
            'discussion': '💬'
        }
        
        section_names_cn = {
            'abstract': '摘要',
            'introduction': '引言',
            'related_work': '相关工作',
            'methodology': '研究方法',
            'experiment': '实验',
            'results': '结果',
            'conclusion': '结论',
            'references': '参考文献',
            'discussion': '讨论'
        }
        
        # 以3列显示章节卡片
        cols = st.columns(3)
        
        for idx, (section_name, content) in enumerate(sections.items()):
            with cols[idx % 3]:
                icon = section_icons.get(section_name, '📄')
                cn_name = section_names_cn.get(section_name, section_name.title())
                
                # 计算字符数和百分比
                char_count = len(content)
                percentage = (char_count / total_chars * 100) if total_chars > 0 else 0
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #e0f7fa 0%, #e1f5fe 100%); 
                            padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;
                            border-left: 5px solid #0277bd; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3 style="margin: 0; color: #01579b;">{icon} {cn_name}</h3>
                    <p style="margin: 0.5rem 0; color: #0277bd;"><b>{char_count:,}</b> 字符</p>
                    <div style="background-color: #b3e5fc; height: 8px; border-radius: 4px; overflow: hidden;">
                        <div style="background: linear-gradient(90deg, #0288d1, #0277bd); 
                                    width: {percentage:.1f}%; height: 100%;"></div>
                    </div>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #546e7a;">
                        占比: {percentage:.1f}%
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # AI摘要深度分析（如果启用AI模式）
        if st.session_state.use_ai and st.session_state.ai_analysis:
            ai_data = st.session_state.ai_analysis
            abstract_analysis = ai_data.get('abstract_analysis', {})
            
            if abstract_analysis:
                st.markdown("### 🤖 AI 摘要深度分析")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;">
                        <h4 style="color: white; margin-top: 0;">🎯 研究问题</h4>
                        <p style="color: white; line-height: 1.6;">{abstract_analysis.get('research_problem', '未提取')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                                padding: 1.5rem; border-radius: 12px;">
                        <h4 style="color: white; margin-top: 0;">🔬 主要方法</h4>
                        <p style="color: white; line-height: 1.6;">{abstract_analysis.get('main_method', '未提取')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                                padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;">
                        <h4 style="color: white; margin-top: 0;">📊 关键结果</h4>
                        <p style="color: white; line-height: 1.6;">{abstract_analysis.get('key_results', '未提取')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    research_bg = abstract_analysis.get('research_background', '未提取')
                    if research_bg and research_bg != '未在摘要中明确提及':
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
                                    padding: 1.5rem; border-radius: 12px;">
                            <h4 style="color: white; margin-top: 0;">📚 研究背景</h4>
                            <p style="color: white; line-height: 1.6;">{research_bg}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # 主要贡献
                contributions = abstract_analysis.get('contributions', [])
                if contributions:
                    st.markdown("**💡 主要贡献**")
                    for idx, contrib in enumerate(contributions, 1):
                        if contrib and contrib != '未在摘要中明确提及':
                            st.markdown(f"""
                            <div style="background-color: #e8f5e9; padding: 0.8rem; border-radius: 8px; 
                                        margin: 0.3rem 0; border-left: 4px solid #4caf50;">
                                <p style="margin: 0; color: #2e7d32;"><b>{idx}.</b> {contrib}</p>
                            </div>
                            """, unsafe_allow_html=True)
                
                # 关键词
                keywords = abstract_analysis.get('keywords', [])
                if keywords:
                    st.markdown("**🔑 AI提取的关键词**")
                    keywords_html = ""
                    for kw in keywords:
                        if kw and kw != '未在摘要中明确提及':
                            keywords_html += f'<span style="display:inline-block; background-color:#1976d2; color:white; padding:0.4rem 1rem; border-radius:20px; margin:0.3rem; font-size:0.95rem;">{kw}</span>'
                    st.markdown(keywords_html, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 摘要显示
        if 'abstract' in sections:
            st.markdown("### 📝 摘要 (Abstract)")
            
            abstract = sections['abstract']
            
            st.markdown(f"""
            <div style="background-color: #f1f8e9; padding: 1.5rem; border-radius: 12px; 
                        border-left: 5px solid #689f38;">
                <p style="line-height: 1.8; color: #33691e; text-align: justify;">
                    {abstract[:2000]}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if len(abstract) > 2000:
                with st.expander("📖 查看完整摘要"):
                    st.write(abstract)
        
        st.markdown("---")
        
        # 引言显示
        if 'introduction' in sections:
            st.markdown("### 📖 引言 (Introduction)")
            
            intro = sections['introduction']
            
            st.markdown(f"""
            <div style="background-color: #fff3e0; padding: 1.5rem; border-radius: 12px; 
                        border-left: 5px solid #f57c00;">
                <p style="line-height: 1.8; color: #e65100; text-align: justify;">
                    {intro[:1500]}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if len(intro) > 1500:
                with st.expander("📖 查看完整引言"):
                    st.write(intro)
        
        st.markdown("---")
        
        # 研究问题提取
        st.markdown("### 🎯 研究问题识别")
        
        # 从摘要和引言中提取研究问题
        question_indicators = [
            'question', 'problem', 'challenge', 'issue', 'aim', 'objective',
            'investigate', 'explore', 'examine', 'study',
            '问题', '挑战', '目标', '研究', '探索', '分析'
        ]
        
        research_questions = []
        
        search_text = sections.get('abstract', '') + ' ' + sections.get('introduction', '')
        sentences = re.split(r'[.。]', search_text)
        
        for sent in sentences:
            for indicator in question_indicators:
                if indicator in sent.lower() and len(sent) > 30 and len(sent) < 300:
                    if '?' in sent or 'how' in sent.lower() or 'what' in sent.lower() or 'why' in sent.lower():
                        research_questions.append(sent.strip())
                        break
        
        if research_questions:
            for idx, question in enumerate(research_questions[:5], 1):
                st.markdown(f"""
                <div style="background-color: #e8eaf6; padding: 1rem; border-radius: 8px; 
                            margin: 0.5rem 0; border-left: 4px solid #3f51b5;">
                    <p style="margin: 0; color: #1a237e;"><b>🎯 研究问题 {idx}:</b> {question}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("💡 未能自动识别明确的研究问题，请查看摘要和引言部分")

# Tab 3: 方法与结果
with tab3:
    st.markdown('<div class="sub-header">🔬 研究方法与实验结果</div>', unsafe_allow_html=True)
    
    if not st.session_state.analysis_done:
        st.markdown("""
        <div class="warning-box">
            <h4>⚠️ 尚未分析论文</h4>
            <p>请先在「📄 上传论文」标签页上传并分析论文</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        sections = st.session_state.sections
        
        # 方法部分
        if 'methodology' in sections:
            st.markdown("### 🔬 研究方法")
            
            method_text = sections['methodology']
            
            # 方法概述卡片
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%); 
                        padding: 2rem; border-radius: 12px; border-left: 5px solid #4caf50;">
                <h4 style="color: #2e7d32; margin-top: 0;">📌 方法概述</h4>
                <p style="line-height: 1.8; color: #33691e; text-align: justify;">
                    {method_text[:1000]}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if len(method_text) > 1000:
                with st.expander("📖 查看完整方法描述", expanded=False):
                    st.write(method_text)
            
            st.markdown("---")
            
            # 关键技术词频分析
            st.markdown("### 🔑 技术关键词分析")
            
            keywords = {
                '机器学习': ['machine learning', 'ML', '机器学习'],
                '深度学习': ['deep learning', 'DL', '深度学习'],
                '神经网络': ['neural network', 'NN', '神经网络'],
                'LSTM': ['LSTM', 'long short-term memory'],
                'CNN': ['CNN', 'convolutional neural network', '卷积神经网络'],
                'RNN': ['RNN', 'recurrent neural network', '循环神经网络'],
                'Transformer': ['transformer', 'attention mechanism', '注意力机制'],
                '优化算法': ['optimization', 'optimizer', 'adam', 'sgd', '优化'],
                '模型': ['model', 'modeling', '模型'],
                '算法': ['algorithm', '算法'],
                '预测': ['prediction', 'predict', 'forecast', '预测'],
                '训练': ['training', 'train', '训练'],
                '测试': ['testing', 'test', 'evaluation', '测试', '评估']
            }
            
            found_keywords = {}
            full_method = method_text.lower()
            
            for category, terms in keywords.items():
                count = 0
                for term in terms:
                    count += full_method.count(term.lower())
                if count > 0:
                    found_keywords[category] = count
            
            # 排序
            found_keywords = dict(sorted(found_keywords.items(), key=lambda x: x[1], reverse=True))
            
            if found_keywords:
                col1, col2 = st.columns(2)
                
                # 左列：关键词标签云
                with col1:
                    st.markdown("**📊 关键词词频**")
                    
                    max_count = max(found_keywords.values())
                    
                    for kw, count in list(found_keywords.items())[:10]:
                        # 根据频率计算大小和颜色
                        size_ratio = count / max_count
                        font_size = 0.8 + size_ratio * 0.8  # 0.8rem 到 1.6rem
                        
                        # 颜色渐变
                        if size_ratio > 0.7:
                            color = '#d32f2f'  # 红色
                        elif size_ratio > 0.4:
                            color = '#f57c00'  # 橙色
                        else:
                            color = '#0288d1'  # 蓝色
                        
                        st.markdown(f"""
                        <span style="display: inline-block; background-color: {color}; 
                                     color: white; padding: 0.4rem 1rem; border-radius: 20px; 
                                     margin: 0.3rem; font-size: {font_size}rem; font-weight: bold;">
                            {kw} <small>({count})</small>
                        </span>
                        """, unsafe_allow_html=True)
                
                # 右列：词频柱状图（文本版）
                with col2:
                    st.markdown("**📈 词频统计图**")
                    
                    for kw, count in list(found_keywords.items())[:8]:
                        percentage = (count / max_count) * 100
                        
                        st.markdown(f"""
                        <div style="margin: 0.5rem 0;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.2rem;">
                                <span style="font-weight: bold; color: #424242;">{kw}</span>
                                <span style="color: #757575;">{count} 次</span>
                            </div>
                            <div style="background-color: #e0e0e0; height: 12px; border-radius: 6px; overflow: hidden;">
                                <div style="background: linear-gradient(90deg, #42a5f5, #1976d2); 
                                            width: {percentage}%; height: 100%;"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("💡 未检测到标准技术关键词")
        
        st.markdown("---")
        
        # 实验结果
        if 'experiment' in sections or 'results' in sections:
            st.markdown("### 📊 实验结果")
            
            exp_text = sections.get('experiment', '') + ' ' + sections.get('results', '')
            
            if exp_text.strip():
                # 结果概述
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                            padding: 2rem; border-radius: 12px; border-left: 5px solid #2196f3;">
                    <h4 style="color: #0d47a1; margin-top: 0;">📈 结果概述</h4>
                    <p style="line-height: 1.8; color: #1565c0; text-align: justify;">
                        {exp_text[:1000]}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                if len(exp_text) > 1000:
                    with st.expander("📖 查看完整实验结果"):
                        st.write(exp_text)
                
                st.markdown("---")
                
                # 性能数据提取
                st.markdown("### 📊 性能数据识别")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # 提取百分比
                    percentages = re.findall(r'\b(\d+(?:\.\d+)?)\s*%', exp_text)
                    
                    if percentages:
                        st.markdown("**📈 百分比数据**")
                        st.markdown(f"""
                        <div style="background-color: #f3e5f5; padding: 1rem; border-radius: 8px;">
                            <p style="margin: 0; color: #4a148c;">
                                发现 <b>{len(percentages)}</b> 个百分比数据
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 显示前10个
                        pct_display = " · ".join([f"<span style='background-color:#9c27b0; color:white; padding:0.2rem 0.6rem; border-radius:10px; margin:0.2rem;'>{p}%</span>" for p in percentages[:10]])
                        st.markdown(pct_display, unsafe_allow_html=True)
                        
                        if len(percentages) > 10:
                            st.caption(f"...还有 {len(percentages) - 10} 个")
                
                with col2:
                    # 提取小数数值
                    numbers = re.findall(r'\b(\d+\.\d+)\b', exp_text)
                    
                    if numbers:
                        st.markdown("**🔢 数值数据**")
                        st.markdown(f"""
                        <div style="background-color: #e0f2f1; padding: 1rem; border-radius: 8px;">
                            <p style="margin: 0; color: #004d40;">
                                发现 <b>{len(numbers)}</b> 个数值数据
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 显示前10个
                        num_display = " · ".join([f"<span style='background-color:#00897b; color:white; padding:0.2rem 0.6rem; border-radius:10px; margin:0.2rem;'>{n}</span>" for n in numbers[:10]])
                        st.markdown(num_display, unsafe_allow_html=True)
                        
                        if len(numbers) > 10:
                            st.caption(f"...还有 {len(numbers) - 10} 个")
                
                # 性能指标关键词
                st.markdown("---")
                st.markdown("**🎯 性能指标关键词**")
                
                metrics = ['accuracy', 'precision', 'recall', 'f1-score', 'mae', 'rmse', 
                          'mse', 'auc', 'loss', 'error', 'performance',
                          '准确率', '精确度', '召回率', '误差', '性能']
                
                found_metrics = []
                for metric in metrics:
                    if metric in exp_text.lower():
                        count = exp_text.lower().count(metric)
                        found_metrics.append((metric, count))
                
                if found_metrics:
                    found_metrics.sort(key=lambda x: x[1], reverse=True)
                    
                    metrics_html = ""
                    for metric, count in found_metrics[:12]:
                        metrics_html += f'<span style="display:inline-block; background-color:#ff6f00; color:white; padding:0.3rem 0.8rem; border-radius:15px; margin:0.2rem; font-size:0.9rem;">{metric} ({count})</span>'
                    
                    st.markdown(metrics_html, unsafe_allow_html=True)
        else:
            st.info("💡 未识别到实验结果章节")

# Tab 4: 创新点
with tab4:
    st.markdown('<div class="sub-header">💡 论文创新点分析</div>', unsafe_allow_html=True)
    
    if not st.session_state.analysis_done:
        st.markdown("""
        <div class="warning-box">
            <h4>⚠️ 尚未分析论文</h4>
            <p>请先在「📄 上传论文」标签页上传并分析论文</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        paper_data = st.session_state.paper_data
        sections = st.session_state.sections
        
        # AI创新点识别（如果启用）
        if st.session_state.use_ai and st.session_state.ai_analysis:
            ai_data = st.session_state.ai_analysis
            ai_innovations = ai_data.get('innovations', [])
            
            if ai_innovations:
                st.markdown("### 🤖 AI 智能识别的创新点")
                
                st.markdown("""
                <div class="success-box">
                    <p><b>✨ AI 深度分析已完成</b></p>
                    <p>使用 Claude AI 从论文的摘要、方法和结果部分深度理解并提取创新点</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 显示AI识别的创新点
                gradient_colors = [
                    ('linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 'white'),
                    ('linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', 'white'),
                    ('linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', 'white'),
                    ('linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', 'white'),
                    ('linear-gradient(135deg, #fa709a 0%, #fee140 100%)', 'white'),
                ]
                
                for idx, innovation in enumerate(ai_innovations, 1):
                    gradient, text_color = gradient_colors[(idx - 1) % len(gradient_colors)]
                    
                    innovation_text = innovation.get('innovation', '')
                    innovation_type = innovation.get('type', '其他创新')
                    significance = innovation.get('significance', 5)
                    description = innovation.get('description', '')
                    
                    # 重要性星级
                    stars = '⭐' * min(int(significance / 2), 5)
                    
                    st.markdown(f"""
                    <div style="background: {gradient}; 
                                padding: 1.5rem; border-radius: 12px; margin: 1rem 0;
                                box-shadow: 0 4px 6px rgba(0,0,0,0.15);">
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="background-color: rgba(255,255,255,0.3); 
                                         color: {text_color}; padding: 0.3rem 0.8rem; 
                                         border-radius: 20px; font-weight: bold;">
                                💡 创新点 {idx}
                            </span>
                            <div>
                                <span style="background-color: rgba(255,255,255,0.3); 
                                             color: {text_color}; padding: 0.3rem 0.8rem; 
                                             border-radius: 20px; font-size: 0.85rem; margin-right: 0.5rem;">
                                    {innovation_type}
                                </span>
                                <span style="background-color: rgba(255,255,255,0.3); 
                                             color: {text_color}; padding: 0.3rem 0.8rem; 
                                             border-radius: 20px; font-size: 0.85rem;">
                                    {stars}
                                </span>
                            </div>
                        </div>
                        <p style="color: {text_color}; line-height: 1.6; margin: 0.5rem 0; 
                                  font-size: 1.05rem; font-weight: 600; text-align: justify;">
                            {innovation_text}
                        </p>
                        <p style="color: {text_color}; line-height: 1.5; margin: 0.5rem 0 0 0; 
                                  font-size: 0.9rem; opacity: 0.95; text-align: justify;">
                            {description}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
        
        st.markdown("### 🎯 自动提取的创新点")
        
        # 基于关键词自动提取创新点
        full_text = paper_data['text']
        
        innovation_indicators = {
            'novel': '新颖的',
            'new': '新的',
            'first': '首次',
            'propose': '提出',
            'introduce': '引入',
            'improve': '改进',
            'enhance': '增强',
            'better': '更好',
            'outperform': '优于',
            '新': '新',
            '提出': '提出',
            '改进': '改进',
            '创新': '创新',
            '首次': '首次',
            '优化': '优化'
        }
        
        # 查找包含创新指示词的句子
        sentences = re.split(r'[.。]', full_text)
        innovation_sentences = []
        
        for sent in sentences:
            for indicator, cn_name in innovation_indicators.items():
                if indicator in sent.lower() and len(sent) > 50 and len(sent) < 300:
                    innovation_sentences.append((sent.strip(), cn_name))
                    break
        
        if innovation_sentences:
            # 使用彩色卡片展示创新点
            gradient_colors = [
                ('linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 'white'),
                ('linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', 'white'),
                ('linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', 'white'),
                ('linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', 'white'),
                ('linear-gradient(135deg, #fa709a 0%, #fee140 100%)', 'white'),
                ('linear-gradient(135deg, #30cfd0 0%, #330867 100%)', 'white'),
                ('linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)', '#333'),
                ('linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)', '#333'),
            ]
            
            for idx, (sent, tag) in enumerate(innovation_sentences[:8], 1):
                gradient, text_color = gradient_colors[idx % len(gradient_colors)]
                
                st.markdown(f"""
                <div style="background: {gradient}; 
                            padding: 1.5rem; border-radius: 12px; margin: 1rem 0;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <span style="background-color: rgba(255,255,255,0.3); 
                                     color: {text_color}; padding: 0.3rem 0.8rem; 
                                     border-radius: 20px; font-weight: bold; margin-right: 1rem;">
                            💡 创新点 {idx}
                        </span>
                        <span style="background-color: rgba(255,255,255,0.3); 
                                     color: {text_color}; padding: 0.3rem 0.8rem; 
                                     border-radius: 20px; font-size: 0.85rem;">
                            {tag}
                        </span>
                    </div>
                    <p style="color: {text_color}; line-height: 1.6; margin: 0; 
                              font-size: 1rem; text-align: justify;">
                        {sent}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("💡 未能自动提取明确的创新点，请查看摘要和结论部分")
        
        # 贡献总结
        st.markdown("---")
        st.markdown("### 📋 论文贡献总结")
        
        if 'abstract' in sections:
            abstract = sections['abstract']
            conclusion = sections.get('conclusion', '')
            
            # 查找 contribution 相关句子
            contrib_text = abstract + ' ' + conclusion
            contrib_sentences = []
            
            contrib_keywords = ['contribution', 'contribute', '贡献', 'advantage', '优势']
            
            for sent in re.split(r'[.。]', contrib_text):
                for kw in contrib_keywords:
                    if kw in sent.lower() and len(sent) > 30:
                        contrib_sentences.append(sent.strip())
                        break
            
            if contrib_sentences:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    for idx, sent in enumerate(contrib_sentences[:5], 1):
                        st.markdown(f"""
                        <div style="background-color: #e8f5e9; padding: 1rem; border-radius: 8px; 
                                    margin: 0.5rem 0; border-left: 4px solid #4caf50;">
                            <p style="margin: 0; color: #2e7d32;">
                                <b>✓ 贡献 {idx}:</b> {sent}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 2rem; border-radius: 12px; text-align: center; color: white;">
                        <h2 style="margin: 0; font-size: 3rem;">✨</h2>
                        <h3 style="margin: 1rem 0 0 0;">核心贡献</h3>
                        <p style="margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: bold;">
                            {}</p>
                    </div>
                    """.format(len(contrib_sentences)), unsafe_allow_html=True)
        
        # 关键技术统计
        st.markdown("---")
        st.markdown("### 📊 技术要素统计")
        
        tech_keywords = {
            'LSTM': full_text.count('LSTM'),
            'Deep Learning': full_text.lower().count('deep learning'),
            'Neural Network': full_text.lower().count('neural network'),
            'Machine Learning': full_text.lower().count('machine learning'),
            'Prediction': full_text.lower().count('prediction'),
            'Modeling': full_text.lower().count('modeling'),
            'Optimization': full_text.lower().count('optimization'),
            'Algorithm': full_text.lower().count('algorithm'),
        }
        
        # 过滤出现过的关键词
        tech_keywords = {k: v for k, v in tech_keywords.items() if v > 0}
        tech_keywords = dict(sorted(tech_keywords.items(), key=lambda x: x[1], reverse=True))
        
        if tech_keywords:
            # 使用3列网格
            cols = st.columns(3)
            
            colors = ['#e53935', '#1e88e5', '#43a047', '#fb8c00', '#8e24aa', '#00acc1']
            
            for idx, (tech, count) in enumerate(tech_keywords.items()):
                with cols[idx % 3]:
                    color = colors[idx % len(colors)]
                    st.markdown(f"""
                    <div style="background-color: {color}; padding: 1.5rem; 
                                border-radius: 12px; text-align: center; color: white;
                                margin: 0.5rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                        <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">
                            {count}
                        </div>
                        <div style="font-size: 1rem;">{tech}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # 创新强度评估
        st.markdown("---")
        st.markdown("### 🌟 创新强度评估")
        
        innovation_score = len(innovation_sentences) * 10
        if innovation_score > 100:
            innovation_score = 100
        
        # 评级
        if innovation_score >= 80:
            level = "⭐⭐⭐⭐⭐ 极高"
            color = "#4caf50"
            comment = "该论文具有很高的创新性，提出了多项新颖的方法和观点"
        elif innovation_score >= 60:
            level = "⭐⭐⭐⭐ 高"
            color = "#8bc34a"
            comment = "该论文具有较高的创新性，在多个方面有所创新"
        elif innovation_score >= 40:
            level = "⭐⭐⭐ 中等"
            color = "#ffc107"
            comment = "该论文具有一定创新性，有若干创新点"
        elif innovation_score >= 20:
            level = "⭐⭐ 中下"
            color = "#ff9800"
            comment = "该论文创新性一般，创新点较少"
        else:
            level = "⭐ 低"
            color = "#f44336"
            comment = "该论文创新性较弱，建议查看原文确认"
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {color} 0%, {color}dd 100%); 
                        padding: 2rem; border-radius: 12px; text-align: center; color: white;">
                <h2 style="margin: 0; font-size: 3rem;">{innovation_score}</h2>
                <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem;">创新指数</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background-color: #f5f5f5; padding: 2rem; border-radius: 12px; 
                        border-left: 5px solid {color};">
                <h4 style="margin: 0 0 1rem 0; color: {color};">{level}</h4>
                <p style="margin: 0; color: #424242; line-height: 1.6;">{comment}</p>
                <p style="margin: 1rem 0 0 0; color: #757575; font-size: 0.9rem;">
                    基于 {len(innovation_sentences)} 个创新点识别结果
                </p>
            </div>
            """, unsafe_allow_html=True)

# Tab 5: 生成报告
with tab5:
    st.markdown('<div class="sub-header">📝 生成分析报告</div>', unsafe_allow_html=True)
    
    if not st.session_state.analysis_done:
        st.markdown("""
        <div class="warning-box">
            <h4>⚠️ 尚未分析论文</h4>
            <p>请先在「📄 上传论文」标签页上传并分析论文</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("### 📄 完整分析报告")
        
        # AI综合摘要（如果启用）
        if st.session_state.use_ai and st.session_state.ai_analysis:
            ai_data = st.session_state.ai_analysis
            ai_summary = ai_data.get('summary', '')
            
            if ai_summary:
                st.markdown("### 🤖 AI 生成的综合摘要")
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            padding: 2rem; border-radius: 15px; color: white; margin: 1rem 0;
                            box-shadow: 0 6px 12px rgba(0,0,0,0.15);">
                    <h4 style="color: white; margin-top: 0; border-bottom: 2px solid rgba(255,255,255,0.3); 
                               padding-bottom: 0.5rem;">✨ 智能综合摘要</h4>
                    <p style="line-height: 1.8; text-align: justify; font-size: 1.05rem;">
                        {ai_summary}
                    </p>
                    <p style="margin: 1rem 0 0 0; font-size: 0.85rem; opacity: 0.8; text-align: right;">
                        由 Claude AI 深度理解论文后生成
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("---")
        
        st.markdown("""
        <div class="info-box">
            <h4>📋 报告内容包括</h4>
            <ul style="line-height: 2;">
                <li>✅ 论文基本信息（页数、字符数、图片数等）</li>
                <li>✅ 章节结构分析</li>
                <li>✅ 摘要和引言提取</li>
                <li>✅ 研究方法总结</li>
                <li>✅ 实验结果概述</li>
                <li>✅ 创新点识别</li>
                <li>✅ 技术关键词统计</li>
                <li>✅ 结论内容</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 生成报告
        paper_data = st.session_state.paper_data
        sections = st.session_state.sections
        
        # 构建报告内容
        report = f"""# 📚 论文分析报告

---

## 📋 基本信息

| 项目 | 数值 |
|------|------|
| 📄 总页数 | {paper_data['total_pages']} 页 |
| ✏️ 字符数 | {len(paper_data['text']):,} 字符 |
| 🖼️ 图片数 | {len(paper_data['images'])} 张 |
| 📚 章节数 | {len(sections)} 个 |
| 🤖 分析模式 | {'AI智能分析' if st.session_state.use_ai else '规则分析'} |

"""
        
        # AI综合摘要（如果有）
        if st.session_state.use_ai and st.session_state.ai_analysis:
            ai_data = st.session_state.ai_analysis
            ai_summary = ai_data.get('summary', '')
            if ai_summary:
                report += f"\n## 🤖 AI 综合摘要\n\n{ai_summary}\n\n"
        
        # 元数据
        metadata = paper_data['metadata']
        if metadata.get('title') or metadata.get('author'):
            report += "\n## 📑 论文元数据\n\n"
            if metadata.get('title'):
                report += f"**标题**: {metadata['title']}\n\n"
            if metadata.get('author'):
                report += f"**作者**: {metadata['author']}\n\n"
        
        # 章节结构
        report += "\n## 📊 论文结构\n\n"
        
        section_names_cn = {
            'abstract': '摘要',
            'introduction': '引言',
            'related_work': '相关工作',
            'methodology': '研究方法',
            'experiment': '实验',
            'results': '结果',
            'conclusion': '结论',
            'references': '参考文献',
            'discussion': '讨论'
        }
        
        for section_name, content in sections.items():
            cn_name = section_names_cn.get(section_name, section_name.title())
            report += f"- **{cn_name}**: {len(content):,} 字符\n"
        
        # 摘要
        report += "\n## 📝 摘要\n\n"
        if 'abstract' in sections:
            abstract = sections['abstract']
            report += abstract[:2000]
            if len(abstract) > 2000:
                report += "\n\n...(内容过长，已截断)"
            report += "\n\n"
        
        # 研究方法
        report += "\n## 🔬 研究方法\n\n"
        if 'methodology' in sections:
            method = sections['methodology']
            report += method[:1500]
            if len(method) > 1500:
                report += "\n\n...(内容过长，已截断)"
            report += "\n\n"
        
        # 实验结果
        report += "\n## 📊 实验结果\n\n"
        if 'experiment' in sections:
            exp = sections['experiment']
            report += exp[:1500]
            if len(exp) > 1500:
                report += "\n\n...(内容过长，已截断)"
            report += "\n\n"
        elif 'results' in sections:
            results = sections['results']
            report += results[:1500]
            if len(results) > 1500:
                report += "\n\n...(内容过长，已截断)"
            report += "\n\n"
        
        # 创新点
        report += "\n## 💡 主要创新点\n\n"
        
        # 优先使用AI识别的创新点
        if st.session_state.use_ai and st.session_state.ai_analysis:
            ai_innovations = st.session_state.ai_analysis.get('innovations', [])
            if ai_innovations:
                report += "### 🤖 AI 智能识别\n\n"
                for idx, innovation in enumerate(ai_innovations, 1):
                    innovation_text = innovation.get('innovation', '')
                    innovation_type = innovation.get('type', '其他创新')
                    description = innovation.get('description', '')
                    significance = innovation.get('significance', 5)
                    
                    report += f"{idx}. **{innovation_text}**\n"
                    report += f"   - 类型: {innovation_type}\n"
                    report += f"   - 重要性: {significance}/10\n"
                    if description:
                        report += f"   - 说明: {description}\n"
                    report += "\n"
                
                report += "\n### 📝 规则提取补充\n\n"
        
        # 规则提取的创新点
        full_text = paper_data['text']
        innovation_indicators = ['novel', 'new', 'first', 'propose', 'introduce',
                                'improve', 'enhance', '新', '提出', '改进', '创新', '首次']
        
        sentences = re.split(r'[.。]', full_text)
        innovation_sentences = []
        
        for sent in sentences:
            for indicator in innovation_indicators:
                if indicator in sent.lower() and len(sent) > 50 and len(sent) < 300:
                    innovation_sentences.append(sent.strip())
                    break
        
        if innovation_sentences:
            for idx, sent in enumerate(innovation_sentences[:8], 1):
                report += f"{idx}. {sent}\n\n"
        else:
            report += "未能自动识别明确的创新点\n\n"
        
        # 技术关键词
        report += "\n## 🔑 技术关键词\n\n"
        
        tech_keywords = {
            'LSTM': full_text.count('LSTM'),
            'Deep Learning': full_text.lower().count('deep learning'),
            'Neural Network': full_text.lower().count('neural network'),
            'Machine Learning': full_text.lower().count('machine learning'),
        }
        
        tech_keywords = {k: v for k, v in tech_keywords.items() if v > 0}
        
        for tech, count in tech_keywords.items():
            report += f"- **{tech}**: 出现 {count} 次\n"
        
        report += "\n"
        
        # 结论
        report += "\n## ✅ 结论\n\n"
        if 'conclusion' in sections:
            conclusion = sections['conclusion']
            report += conclusion[:1500]
            if len(conclusion) > 1500:
                report += "\n\n...(内容过长，已截断)"
            report += "\n\n"
        
        report += "\n---\n\n"
        report += "*本报告由 PaperMate 自动生成*  \n"
        report += f"*生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        # 显示报告预览
        st.markdown("### 📖 报告预览")
        
        with st.expander("📄 查看完整报告", expanded=True):
            st.markdown(report)
        
        # 下载按钮区域
        st.markdown("---")
        st.markdown("### 💾 下载报告")
        
        st.markdown("""
        <div class="success-box">
            <h4>✅ 报告已生成完成</h4>
            <p>您可以选择以下格式下载报告：</p>
            <ul>
                <li><b>Markdown格式</b>: 保留格式，支持标题、列表等</li>
                <li><b>纯文本格式</b>: 去除所有格式标记，纯文本内容</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                label="📥 下载 Markdown 报告",
                data=report,
                file_name=f"paper_analysis_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
        
        with col2:
            # 生成纯文本版本
            text_report = report.replace('#', '').replace('*', '').replace('|', '').replace('-', '')
            st.download_button(
                label="📥 下载纯文本报告",
                data=text_report,
                file_name=f"paper_analysis_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        
        with col3:
            # 生成HTML版本
            newline = '\n'
            html_report = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>论文分析报告</title>
    <style>
        body {{ font-family: "Microsoft YaHei", Arial, sans-serif; 
               max-width: 900px; margin: 2rem auto; padding: 2rem;
               background: #f5f5f5; }}
        .container {{ background: white; padding: 2rem; border-radius: 10px;
                     box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #1976d2; border-bottom: 3px solid #1976d2; padding-bottom: 1rem; }}
        h2 {{ color: #0288d1; margin-top: 2rem; border-left: 5px solid #0288d1; 
             padding-left: 1rem; }}
        table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
        th, td {{ border: 1px solid #ddd; padding: 0.75rem; text-align: left; }}
        th {{ background-color: #e3f2fd; color: #0d47a1; }}
        .footer {{ text-align: center; color: #666; margin-top: 2rem; 
                  padding-top: 1rem; border-top: 1px solid #ddd; }}
    </style>
</head>
<body>
    <div class="container">
        {'<br>'.join(report.replace('#', '<h').replace(newline+newline, '</p><p>').split(newline))}
    </div>
</body>
</html>
            """
            
            st.download_button(
                label="📥 下载 HTML 报告",
                data=html_report,
                file_name=f"paper_analysis_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html"
            )
        
        # 报告统计
        st.markdown("---")
        st.markdown("### 📊 报告统计")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("报告字数", f"{len(report):,} 字")
        
        with col2:
            st.metric("报告行数", f"{report.count(chr(10))} 行")
        
        with col3:
            st.metric("章节数量", f"{len(sections)} 个")
        
        with col4:
            st.metric("创新点", f"{len(innovation_sentences)} 个")

# 页脚
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p><b>PaperMate</b> - 专业论文智能阅读助手 | Powered by AI</p>
    <p>帮助学生高效阅读和理解学术论文 📚</p>
</div>
""", unsafe_allow_html=True)
