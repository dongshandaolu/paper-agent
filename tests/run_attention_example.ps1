# 一键演示 Attention 论文阅读流程
# 用法: .\tests\run_attention_example.ps1
# 前提: .env 中已配置有效的 OPENAI_API_KEY

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Pdf = Join-Path $PSScriptRoot "attention.pdf"
if (-not (Test-Path $Pdf)) {
    Write-Error "找不到 $Pdf"
}

Write-Host "`n=== Paper Agent 完整流程演示 ===" -ForegroundColor Cyan
Write-Host "论文: $Pdf`n"

# Step 1: Upload
Write-Host "[1/6] 上传论文..." -ForegroundColor Yellow
$uploadOut = paper-agent upload $Pdf 2>&1 | Out-String
Write-Host $uploadOut

# 从输出中提取 paper_id（匹配 paper_id: xxxxxxxx）
$paperId = [regex]::Match($uploadOut, "paper_id:\s*([a-f0-9]+)").Groups[1].Value
if (-not $paperId) {
    Write-Error "无法获取 paper_id，请检查 API 配置或 upload 输出"
}
Write-Host "paper_id = $paperId`n" -ForegroundColor Green

# Step 2: Structure
Write-Host "[2/6] 总结论文结构..." -ForegroundColor Yellow
paper-agent structure $paperId

# Step 3: Research questions
Write-Host "`n[3/6] 提取研究问题..." -ForegroundColor Yellow
paper-agent questions $paperId

# Step 4: Terminology
Write-Host "`n[4/6] 解释专业术语..." -ForegroundColor Yellow
paper-agent terms $paperId -t "self-attention" -t "multi-head attention" -t "positional encoding"

# Step 5: Q&A
Write-Host "`n[5/6] RAG 问答..." -ForegroundColor Yellow
paper-agent ask "Transformer 相比 RNN 的核心优势是什么？" --paper $Pdf

# Step 6: Full report
$OutDir = Join-Path $Root "output\attention"
Write-Host "`n[6/6] 生成完整阅读报告 -> $OutDir ..." -ForegroundColor Yellow
paper-agent read $Pdf -o $OutDir

Write-Host "`n=== 完成 ===" -ForegroundColor Cyan
Write-Host "paper_id: $paperId"
Write-Host "报告目录: $OutDir"
Write-Host "详细说明见: tests\USAGE_EXAMPLE.md"
