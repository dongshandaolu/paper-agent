from __future__ import annotations

import pickle
import re
from pathlib import Path

import chromadb
from langchain_core.documents import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from paper_agent.config import get_settings
from paper_agent.embeddings import get_embeddings
from paper_agent.models.paper import Chunk, PaperDocument

SECTION_QUERY_KEYWORDS: dict[str, list[str]] = {
    "introduction": ["introduction", "background", "motivation", "problem", "related"],
    "methods": ["method", "approach", "model", "architecture", "algorithm", "framework"],
    "experiments": ["experiment", "evaluation", "setup", "dataset", "training", "baseline"],
    "results": ["result", "performance", "bleu", "accuracy", "metric", "table"],
    "discussion": ["discussion", "analysis", "limitation", "conclusion", "future"],
}


class _TfidfIndex:
    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(max_features=8000)
        self.matrix = None
        self.chunks: list[Chunk] = []

    def fit(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        texts = [c.text for c in chunks]
        self.matrix = self.vectorizer.fit_transform(texts)

    def query(self, text: str, top_k: int, chunk_filter: set[str] | None = None) -> list[tuple[float, Chunk]]:
        if self.matrix is None or not self.chunks:
            return []
        q = self.vectorizer.transform([text])
        scores = cosine_similarity(q, self.matrix).flatten()

        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        results: list[tuple[float, Chunk]] = []
        for idx, _ in ranked:
            chunk = self.chunks[idx]
            if chunk_filter and chunk.chunk_id not in chunk_filter:
                continue
            results.append((float(scores[idx]), chunk))
            if len(results) >= top_k:
                break
        return results


class PaperRetriever:
    def __init__(self) -> None:
        settings = get_settings()
        self.top_k = settings.retrieval_top_k
        self._provider = settings.resolved_embedding_provider()
        self._embeddings = None
        if self._provider in ("openai", "local"):
            self._embeddings = get_embeddings(settings)
        self._client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self._tfidf: dict[str, _TfidfIndex] = {}
        self._documents: dict[str, PaperDocument] = {}
        self._tfidf_dir = Path(settings.chroma_persist_dir) / "tfidf"
        self._tfidf_dir.mkdir(parents=True, exist_ok=True)
        self._load_tfidf_indexes()

    def _tfidf_path(self, doc_id: str) -> Path:
        return self._tfidf_dir / f"{doc_id}.pkl"

    def _load_tfidf_indexes(self) -> None:
        for path in self._tfidf_dir.glob("*.pkl"):
            doc_id = path.stem
            try:
                self._tfidf[doc_id] = pickle.loads(path.read_bytes())
            except Exception:
                continue

    def _persist_tfidf(self, doc_id: str, index: _TfidfIndex) -> None:
        self._tfidf_path(doc_id).write_bytes(pickle.dumps(index))

    def _collection_name(self, doc_id: str) -> str:
        return f"paper_{doc_id}"

    def _index_with_vectors(self, document: PaperDocument) -> None:
        if not document.chunks or self._embeddings is None:
            return
        name = self._collection_name(document.doc_id)
        try:
            self._client.delete_collection(name)
        except Exception:
            pass
        collection = self._client.create_collection(name=name)
        texts = [c.text for c in document.chunks]
        vectors = self._embeddings.embed_documents(texts)
        collection.add(
            ids=[c.chunk_id for c in document.chunks],
            embeddings=vectors,
            documents=texts,
            metadatas=[
                {
                    "doc_id": document.doc_id,
                    "section": c.section_title,
                    "page_start": c.page_start,
                    "page_end": c.page_end,
                    "chunk_index": c.chunk_index,
                }
                for c in document.chunks
            ],
        )

    def _index_with_tfidf(self, document: PaperDocument) -> None:
        if not document.chunks:
            return
        index = _TfidfIndex()
        index.fit(document.chunks)
        self._tfidf[document.doc_id] = index
        self._documents[document.doc_id] = document
        self._persist_tfidf(document.doc_id, index)

    def index_document(self, document: PaperDocument) -> None:
        self._documents[document.doc_id] = document
        if not document.chunks:
            return
        if self._provider == "openai":
            try:
                self._index_with_vectors(document)
                return
            except Exception:
                pass
        if self._provider == "local":
            try:
                self._index_with_vectors(document)
                return
            except Exception:
                pass
        self._index_with_tfidf(document)

    def _get_tfidf_index(self, doc_id: str) -> _TfidfIndex | None:
        index = self._tfidf.get(doc_id)
        if index:
            return index
        path = self._tfidf_path(doc_id)
        if path.exists():
            index = pickle.loads(path.read_bytes())
            self._tfidf[doc_id] = index
            return index
        return None

    def _match_sections(self, query: str, document: PaperDocument) -> set[str]:
        query_lower = query.lower()
        matched_titles: set[str] = set()
        for _group, keywords in SECTION_QUERY_KEYWORDS.items():
            if any(kw in query_lower for kw in keywords):
                for section in document.sections:
                    title_lower = section.title.lower()
                    if any(kw in title_lower for kw in keywords):
                        matched_titles.add(section.title)
        return matched_titles

    def _chunk_ids_for_sections(self, document: PaperDocument, section_titles: set[str]) -> set[str]:
        if not section_titles:
            return set()
        return {
            c.chunk_id
            for c in document.chunks
            if c.section_title in section_titles
        }

    def _boost_section_scores(
        self, results: list[tuple[float, Chunk]], section_titles: set[str], boost: float = 0.3
    ) -> list[tuple[float, Chunk]]:
        if not section_titles:
            return results
        boosted: list[tuple[float, Chunk]] = []
        for score, chunk in results:
            if chunk.section_title in section_titles:
                score = min(1.0, score + boost)
            boosted.append((score, chunk))
        boosted.sort(key=lambda x: x[1].section_title in section_titles, reverse=True)
        boosted.sort(key=lambda x: x[0], reverse=True)
        return boosted

    def _chunks_to_documents(self, doc_id: str, scored: list[tuple[float, Chunk]]) -> list[Document]:
        return [
            Document(
                page_content=chunk.text,
                metadata={
                    "doc_id": doc_id,
                    "chunk_id": chunk.chunk_id,
                    "section": chunk.section_title,
                    "page_start": chunk.page_start,
                    "page_end": chunk.page_end,
                    "score": score,
                },
            )
            for score, chunk in scored
        ]

    def _retrieve_tfidf(
        self,
        doc_id: str,
        query: str,
        top_k: int,
        chunk_filter: set[str] | None = None,
        section_boost: set[str] | None = None,
    ) -> list[Document]:
        index = self._get_tfidf_index(doc_id)
        if not index:
            return []
        fetch_k = top_k * 2 if section_boost else top_k
        scored = index.query(query, fetch_k, chunk_filter=chunk_filter)
        if section_boost:
            all_scored = index.query(query, fetch_k * 2)
            merged: dict[str, tuple[float, Chunk]] = {c.chunk_id: (s, c) for s, c in all_scored}
            for s, c in scored:
                merged[c.chunk_id] = (s, c)
            scored = list(merged.values())
            scored = self._boost_section_scores(scored, section_boost)
        return self._chunks_to_documents(doc_id, scored[:top_k])

    def _retrieve_vectors(self, doc_id: str, query: str, top_k: int) -> list[Document]:
        if self._embeddings is None:
            return []
        name = self._collection_name(doc_id)
        try:
            collection = self._client.get_collection(name=name)
        except Exception:
            return []
        query_vec = self._embeddings.embed_query(query)
        results = collection.query(query_embeddings=[query_vec], n_results=top_k)
        documents: list[Document] = []
        if not results or not results.get("documents"):
            return documents
        for i, text in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i] if results.get("metadatas") else {}
            distance = results["distances"][0][i] if results.get("distances") else None
            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "doc_id": doc_id,
                        "chunk_id": results["ids"][0][i] if results.get("ids") else "",
                        "section": meta.get("section", ""),
                        "page_start": meta.get("page_start", 0),
                        "page_end": meta.get("page_end", 0),
                        "score": 1 - distance if distance is not None else 0,
                    },
                )
            )
        return documents

    def retrieve(self, doc_id: str, query: str, top_k: int | None = None) -> list[Document]:
        k = top_k or self.top_k
        if self._provider in ("openai", "local"):
            docs = self._retrieve_vectors(doc_id, query, k)
            if docs:
                return docs
        return self._retrieve_tfidf(doc_id, query, k)

    def retrieve_hybrid(
        self,
        doc_id: str,
        query: str,
        document: PaperDocument,
        top_k: int | None = None,
    ) -> list[Document]:
        k = top_k or get_settings().rcs_top_k
        section_titles = self._match_sections(query, document)
        section_chunk_ids = self._chunk_ids_for_sections(document, section_titles)

        section_docs: list[Document] = []
        if section_chunk_ids:
            section_docs = self._retrieve_tfidf(
                doc_id, query, k, chunk_filter=section_chunk_ids, section_boost=section_titles
            )

        global_docs = self.retrieve(doc_id, query, top_k=k)

        seen: set[str] = set()
        merged: list[Document] = []
        for doc in section_docs + global_docs:
            cid = doc.metadata.get("chunk_id", "")
            if cid and cid in seen:
                continue
            if cid:
                seen.add(cid)
            merged.append(doc)
            if len(merged) >= k:
                break
        return merged

    def has_index(self, doc_id: str) -> bool:
        if self._provider in ("openai", "local"):
            try:
                self._client.get_collection(name=self._collection_name(doc_id))
                return True
            except Exception:
                pass
        return doc_id in self._tfidf or self._tfidf_path(doc_id).exists()


_retriever: PaperRetriever | None = None


def get_retriever() -> PaperRetriever:
    global _retriever
    if _retriever is None:
        _retriever = PaperRetriever()
    return _retriever
