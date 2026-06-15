from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_base: str = "https://api.openai.com/v1"
    openai_api_key: str = ""
    model_name: str = "gpt-4o-mini"

    # embedding: auto=DeepSeek 自动用 tfidf | openai=远程 API | local=fastembed | tfidf=本地 TF-IDF
    embedding_provider: str = "auto"
    embedding_model: str = "text-embedding-3-small"
    embedding_api_base: str = ""
    embedding_api_key: str = ""
    local_embedding_model: str = "BAAI/bge-small-en-v1.5"

    chroma_persist_dir: str = "./data/chroma"
    papers_dir: str = "./data/papers"
    output_dir: str = "./output"
    retrieval_top_k: int = 5
    rcs_top_k: int = 20
    rcs_final_k: int = 5
    retrieval_mode: str = "hybrid"
    max_reflect_iterations: int = 2
    summary_model: str = ""
    chunk_size: int = 1200
    chunk_overlap: int = 200

    def resolved_embedding_provider(self) -> str:
        if self.embedding_provider != "auto":
            return self.embedding_provider
        base = (self.embedding_api_base or self.openai_api_base).lower()
        if "deepseek" in base:
            return "tfidf"
        return "openai"


@lru_cache
def get_settings() -> Settings:
    return Settings()
