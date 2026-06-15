# 论文对比报告

> 生成时间: 2026-06-15 16:11

## 对比论文

- Attention Is All You Need (arXiv:1706.03762v7)

- BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding (arXiv:1810.04805v2)


## 对比维度


### 问题定义

- **Attention Is All You Need (arXiv:1706.03762v7)**: 现有序列转导模型（如RNN、CNN）依赖循环或卷积结构，训练并行性差、耗时长，尤其在长序列下因内存限制难以批处理。

- **BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding (arXiv:1810.04805v2)**: 现有语言表示模型（如ELMo、GPT）受限于单向语言模型，无法充分利用深层双向上下文信息，限制了句子级和词元级任务的表现。



### 方法

- **Attention Is All You Need (arXiv:1706.03762v7)**: 提出Transformer架构，完全基于自注意力机制，摒弃循环和卷积。编码器和解码器各由6层堆叠，每层包含多头自注意力子层和前馈网络子层，采用残差连接和层归一化。注意力机制采用缩放点积注意力，并引入多头注意力以从不同子空间联合关注信息。

- **BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding (arXiv:1810.04805v2)**: 提出BERT模型，采用掩码语言模型（MLM）预训练目标，实现深度双向表示；同时引入下一句预测（NSP）任务联合预训练。微调时仅需一个额外输出层，适用于多种任务。



### 数据集

- **Attention Is All You Need (arXiv:1706.03762v7)**: WMT 2014英德翻译（约450万句对）和英法翻译（3600万句对）任务，使用BPE和word-piece词汇表；英语成分句法分析任务（含大规模和有限训练数据）。

- **BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding (arXiv:1810.04805v2)**: 11个NLP任务，包括GLUE基准测试（MNLI、QQP、QNLI、SST-2、CoLA、STS-B、MRPC、RTE等）、SQuAD v1.1、SQuAD v2.0和SWAG。



### 评估指标

- **Attention Is All You Need (arXiv:1706.03762v7)**: BLEU（英德、英法翻译任务），F1（英语成分句法分析任务）。

- **BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding (arXiv:1810.04805v2)**: GLUE得分、准确率（MultiNLI、SWAG）、F1（SQuAD）。



### 主要结论

- **Attention Is All You Need (arXiv:1706.03762v7)**: Transformer是首个完全基于注意力的序列转换模型，训练速度显著快于基于循环或卷积层的架构；在WMT 2014英德和英法翻译任务上均达到新最优水平，英德任务最佳模型超越所有先前报告的集成模型。

- **BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding (arXiv:1810.04805v2)**: 深度双向预训练模型能够成功处理广泛的NLP任务，包括低资源任务；主要贡献是将无监督预训练从单向推广到深度双向架构，同一预训练模型可处理多种NLP任务。




## 综合评述
两篇论文均基于Transformer架构，但关注点不同。第一篇（Attention Is All You Need）提出了Transformer这一基础架构，解决了序列转导模型中并行性差的问题，在机器翻译任务上取得突破性成果。第二篇（BERT）则在此基础上，通过掩码语言模型实现了深度双向预训练，克服了单向语言模型的局限，在多个NLP任务上取得显著提升。两者共同推动了NLP领域的发展：Transformer提供了高效的基础架构，BERT则展示了如何利用大规模无监督数据预训练来提升下游任务性能。

## 阅读建议
建议先阅读《Attention Is All You Need》以理解Transformer架构的核心原理和设计思想，再阅读《BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding》以了解如何将Transformer应用于预训练并实现深度双向表示。这两篇论文是理解现代NLP模型（如GPT系列、RoBERTa等）的基础，适合按时间顺序阅读。