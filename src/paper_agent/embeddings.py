from __future__ import annotations

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from paper_agent.config import Settings, get_settings


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
        return FastEmbedEmbeddings(model_name=settings.local_embedding_model)

    if provider == "tfidf":
        raise ValueError("tfidf provider uses PaperRetriever directly, not Embeddings API")

    api_base = settings.embedding_api_base or settings.openai_api_base
    api_key = settings.embedding_api_key or settings.openai_api_key
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=api_key,
        openai_api_base=api_base,
    )
