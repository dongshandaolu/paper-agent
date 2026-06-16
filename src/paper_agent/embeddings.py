from __future__ import annotations

import os
from pathlib import Path

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from paper_agent.config import Settings, get_settings


def _is_local_path(model_name: str) -> bool:
    """判断是否为本地路径：含路径分隔符或盘符（Windows/Linux 均兼容）"""
    p = Path(model_name)
    return (
        os.sep in model_name
        or "/" in model_name
        or "\\" in model_name
        or (len(model_name) >= 2 and model_name[1] == ":")  # Windows 盘符 D:\...
    ) and p.exists()


class SentenceTransformerEmbeddings(Embeddings):
    """使用 sentence-transformers 直接加载本地路径模型"""

    def __init__(self, model_path: str) -> None:
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_path, local_files_only=True)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(texts, convert_to_numpy=True).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self._model.encode([text], convert_to_numpy=True)[0].tolist()


class FastEmbedEmbeddings(Embeddings):
    def __init__(self, model_name: str) -> None:
        from fastembed import TextEmbedding

        self._model = TextEmbedding(model_name=model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [vec.tolist() for vec in self._model.embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        return next(self._model.embed([text])).tolist()


def get_embeddings(settings: Settings | None = None) -> Embeddings:
    settings = settings or get_settings()
    provider = settings.resolved_embedding_provider()

    if provider == "local":
        model_name = settings.local_embedding_model
        # 本地路径：使用 sentence-transformers 直接加载，跳过 fastembed 模型名校验
        if _is_local_path(model_name):
            return SentenceTransformerEmbeddings(model_path=model_name)
        # HuggingFace 模型名：使用 fastembed 在线下载
        return FastEmbedEmbeddings(model_name=model_name)

    if provider == "tfidf":
        raise ValueError("tfidf provider uses PaperRetriever directly, not Embeddings API")

    api_base = settings.embedding_api_base or settings.openai_api_base
    api_key = settings.embedding_api_key or settings.openai_api_key
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=api_key,
        openai_api_base=api_base,
    )
