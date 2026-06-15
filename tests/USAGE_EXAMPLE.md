# 完整使用流程示例 — Attention Is All You Need

本文以 `tests/attention.pdf`（Transformer 原论文）为例，演示 Paper Agent 从上传到深度阅读的完整流程。

---

## 0. 前置准备

```powershell
# 进入项目根目录
cd f:\agent

# 安装（若尚未安装）
pip install -e .

# 配置 API（必须填写有效的 Key，否则 embedding/LLM 会 401）
cp .env.example .env
# 编辑 .env，至少设置：
#   OPENAI_API_BASE=https://api.deepseek.com/v1
#   OPENAI_API_KEY=sk-你的真实密钥
#   MODEL_NAME=deepseek-chat
#   EMBEDDING_MODEL=text-embedding-3-small
```

确认论文文件存在：

```powershell
Test-Path tests\attention.pdf   # 应返回 True
```

---

## 1. CLI 完整流程（推荐顺序）

### Step 1 — 上传论文，获取 paper_id

```powershell
paper-agent upload tests\attention.pdf
```

**预期输出示例：**

```
╭──────────────────────────── Paper Agent ────────────────────────────╮
│ 已上传                                                              │
│ paper_id: a1b2c3d4e5f67890                                           │
│ 标题: Attention Is All You Need                                     │
│ 章节: 12 | 页数: 15                                                 │
╰─────────────────────────────────────────────────────────────────────╯
```

> 记下输出的 `paper_id`，后续命令均使用它。下文用 `<PAPER_ID>` 代替。

上传后文件会复制到 `data/papers/attention.pdf`，向量索引写入 `data/chroma/`。

---

### Step 2 — 总结论文结构

```powershell
paper-agent structure <PAPER_ID>
```

**你会得到：**
- 各章节大纲（Introduction / Model Architecture / Training / Results …）
- IMRaD 映射（Introduction → Methods → Results → Discussion）
- 阅读顺序建议（先读 Abstract + Figure 1，再读 Section 3.2 Multi-Head Attention …）

---

### Step 3 — 提取研究问题

```powershell
paper-agent questions <PAPER_ID>
```

**典型提取结果：**
- **主问题**：能否完全用注意力机制替代 RNN/CNN 做序列 transduction？
- **子问题**：自注意力 vs 循环层的计算复杂度？多头注意力的必要性？
- **假设**：并行化训练可显著缩短训练时间

---

### Step 4 — 解释专业术语

```powershell
# 自动提取 Top 10 术语
paper-agent terms <PAPER_ID>

# 或指定术语
paper-agent terms <PAPER_ID> -t "self-attention" -t "multi-head attention" -t "positional encoding"
```

**典型解释：**
| 术语 | 通俗解释 |
|------|----------|
| self-attention | 序列中每个位置直接与其他位置计算关联权重 |
| multi-head attention | 多组注意力并行运行，捕获不同子空间的关系 |
| positional encoding | 注入 token 位置信息，弥补无循环结构的缺陷 |

---

### Step 5 — 交互式问答

```powershell
paper-agent ask "Transformer Encoder 和 Decoder 各包含哪些子层？" --paper tests\attention.pdf

paper-agent ask "Scaled Dot-Product Attention 为什么要除以 sqrt(d_k)？" --paper tests\attention.pdf
```

> 使用 `--paper` 时无需 paper_id，每次会重新解析 PDF。若已 upload，也可在 MCP 中用 `ask_paper(paper_id, question)` 更快。

**预期回答格式：**

```
回答: Encoder 由 N=6 个相同层堆叠，每层含 multi-head self-attention 和 position-wise FFN...
置信度: high

引用:
  - [3.1 Encoder and Decoder Stacks, p.3] Each layer has two sub-layers...
```

---

### Step 6 — 生成完整阅读报告

```powershell
paper-agent read tests\attention.pdf -o output\attention
```

**产出文件：** `output\attention\Attention_Is_All_You_Need.md`

报告包含：
1. 结构化摘要（问题 / 方法 / 实验 / 结论）
2. 批判性分析（创新性、方法严谨性、实验充分性、可复现性 1–5 分）
3. 关键引用列表

---

### Step 7（可选）— 与其他论文对比

若 `tests/` 下还有第二篇 PDF（如 BERT、GPT 等）：

```powershell
paper-agent compare tests\attention.pdf tests\other_paper.pdf -o output\compare
```

产出 `output\compare\comparison_report.md`。

---

## 2. 一键脚本（PowerShell）

项目提供了可执行的示例脚本：

```powershell
.\tests\run_attention_example.ps1
```

脚本会依次执行 upload → structure → questions → terms → ask → read，并将 paper_id 打印到控制台。

---

## 3. Claude Code / Cursor MCP 流程

### 3.1 配置 MCP

```powershell
cp .mcp.json.example .mcp.json
# 编辑 .mcp.json 中的 OPENAI_API_KEY
```

`.mcp.json` 内容：

```json
{
  "mcpServers": {
    "paper-agent": {
      "command": "paper-agent-mcp",
      "env": {
        "OPENAI_API_BASE": "https://api.deepseek.com/v1",
        "OPENAI_API_KEY": "sk-你的密钥",
        "MODEL_NAME": "deepseek-chat",
        "EMBEDDING_MODEL": "text-embedding-3-small"
      }
    }
  }
}
```

重启 Claude Code / Cursor 使 MCP 生效。

### 3.2 在对话中的完整请求示例

**一次性完成全流程：**

> 请使用 paper-agent 阅读 `f:/agent/tests/attention.pdf`：
> 1. 上传并索引论文
> 2. 总结论文结构（章节 + IMRaD）
> 3. 提取主研究问题和子问题
> 4. 解释 self-attention、multi-head attention、positional encoding 三个术语
> 5. 回答：Transformer 相比 RNN 的核心优势是什么？
> 6. 最后生成完整阅读报告

**Agent 内部调用链：**

```
upload_paper("f:/agent/tests/attention.pdf")
    → paper_id: xxxx

summarize_structure(paper_id)
    → 章节大纲 + IMRaD + 阅读指南

extract_research_questions(paper_id)
    → 主/子研究问题 + 假设

explain_terms(paper_id, terms=["self-attention", "multi-head attention", "positional encoding"])
    → 术语解释 + 页码引用

ask_paper(paper_id, "Transformer 相比 RNN 的核心优势是什么？")
    → 带引用的答案

read_paper(paper_id)
    → output/Attention_Is_All_You_Need.md
```

### 3.3 分步对话示例

| 你说 | Agent 调用 |
|------|------------|
| 上传 attention 论文 | `upload_paper("f:/agent/tests/attention.pdf")` |
| 这篇论文结构是怎样的？ | `summarize_structure(paper_id)` |
| 研究问题是什么？ | `extract_research_questions(paper_id)` |
| 解释一下 Scaled Dot-Product Attention | `explain_terms(paper_id, terms=["Scaled Dot-Product Attention"])` |
| WMT 2014 英德翻译 BLEU 是多少？ | `ask_paper(paper_id, "WMT 2014 英德翻译 BLEU 是多少？")` |

---

## 4. 数据流示意

```
tests/attention.pdf
        │
        ▼
   upload_paper / paper-agent upload
        │
        ├──► data/papers/attention.pdf     （论文副本）
        ├──► data/chroma/paper_<id>/       （向量索引）
        └──► paper_id
                │
    ┌───────────┼───────────┬──────────────┐
    ▼           ▼           ▼              ▼
 structure   questions    terms         ask_paper
    │           │           │              │
    └───────────┴───────────┴──────┬───────┘
                                   ▼
                              read_paper
                                   │
                                   ▼
                    output/Attention_Is_All_You_Need.md
```

---

## 5. 常见问题

| 问题 | 处理 |
|------|------|
| `404 Not Found`（upload 时） | **DeepSeek 不提供 Embedding API**。保持 `EMBEDDING_PROVIDER=auto`（默认），系统会自动用本地 TF-IDF 检索 |
| `401 Authentication Fails` | 检查 `.env` 中 `OPENAI_API_KEY` 是否有效 |
| `未找到论文 paper_id=...` | 先执行 `upload`，或 `paper-agent upload tests\attention.pdf` |
| Embedding 模型不支持 | 将 `EMBEDDING_MODEL` 改为 provider 支持的模型（如 OpenAI 用 `text-embedding-3-small`） |
| 章节识别不准 | 双栏 PDF 可能解析不完美，可用 `ask_paper` 针对具体段落提问 |

---

## 6. 目录结构（运行后）

```
f:\agent\
├── tests\
│   └── attention.pdf              ← 输入论文
├── data\
│   ├── papers\attention.pdf       ← 上传副本
│   ├── chroma\                    ← 向量库
│   └── papers\index.json          ← 论文索引
└── output\
    └── attention\
        └── Attention_Is_All_You_Need.md   ← 阅读报告
```
