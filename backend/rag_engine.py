"""
RAG Engine for OpenROAD AI Assistant
Pure Python TF-IDF search — no torch, no sentence-transformers, no faiss.
Zero downloads. Server starts in < 1 second.
"""

import json
import math
import re
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from collections import Counter

from backend.knowledge_base import get_all_docs


@dataclass
class SearchResult:
    doc_id: str
    title: str
    category: str
    content: str
    score: float
    tags: List[str] = field(default_factory=list)


class TFIDFIndex:
    """
    Lightweight TF-IDF index — pure Python + numpy only.
    No external ML libraries needed. Builds in milliseconds.
    """

    STOP_WORDS = {
        "a","an","and","are","as","at","be","by","do","for","from","has",
        "he","in","is","it","its","of","on","or","so","that","the","this",
        "to","was","were","we","will","with","you","your","not","can","if",
        "but","they","have","how","what","when","which","who","while","use",
        "used","using","also","been","their","then","than","these","those",
    }

    def __init__(self):
        self.docs: List[Dict] = []
        self.tf_matrix: Optional[np.ndarray] = None
        self.idf_vector: Optional[np.ndarray] = None
        self.vocab: Dict[str, int] = {}
        self._built = False

    def tokenize(self, text: str) -> List[str]:
        tokens = re.sub(r"[^a-z0-9_\-]", " ", text.lower()).split()
        return [t for t in tokens if len(t) > 1 and t not in self.STOP_WORDS]

    def _doc_text(self, doc: Dict, title_boost: int = 3, tag_boost: int = 2) -> str:
        """Concatenate doc fields with boosting via repetition."""
        title = (doc.get("title", "") + " ") * title_boost
        tags  = (" ".join(doc.get("tags", [])) + " ") * tag_boost
        cat   = doc.get("category", "")
        body  = doc.get("content", "")
        return title + tags + cat + " " + body

    def build(self, documents: List[Dict]):
        self.docs = documents
        N = len(documents)

        # Tokenize all docs and build vocabulary
        tokenized = [self.tokenize(self._doc_text(d)) for d in documents]
        df: Counter = Counter()
        for tokens in tokenized:
            df.update(set(tokens))

        # Only keep terms that appear in docs
        # Sort for deterministic indexing
        self.vocab = {term: i for i, term in enumerate(sorted(df.keys()))}
        V = len(self.vocab)

        # Build TF matrix (N x V)
        tf = np.zeros((N, V), dtype=np.float32)
        for i, tokens in enumerate(tokenized):
            freq = Counter(tokens)
            total = max(sum(freq.values()), 1)
            for term, cnt in freq.items():
                j = self.vocab.get(term)
                if j is not None:
                    tf[i, j] = cnt / total

        # Build IDF vector (V,)
        idf = np.array(
            [math.log((N + 1) / (df[term] + 1)) + 1.0 for term in sorted(self.vocab)],
            dtype=np.float32
        )

        # TF-IDF = tf * idf, then L2-normalize each doc row
        tfidf = tf * idf[np.newaxis, :]
        norms = np.linalg.norm(tfidf, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.tf_matrix  = tfidf / norms
        self.idf_vector = idf
        self._built = True

    def search(self, query: str, k: int = 5) -> List[SearchResult]:
        if not self._built or len(self.docs) == 0:
            return []

        q_tokens = self.tokenize(query)
        if not q_tokens:
            return []

        # Build query TF-IDF vector
        q_vec = np.zeros(len(self.vocab), dtype=np.float32)
        freq = Counter(q_tokens)
        total = max(sum(freq.values()), 1)
        for term, cnt in freq.items():
            j = self.vocab.get(term)
            if j is not None:
                q_vec[j] = (cnt / total) * self.idf_vector[j]

        norm = np.linalg.norm(q_vec)
        if norm == 0:
            return []
        q_vec /= norm

        # Cosine similarity via dot product (rows already normalized)
        scores = self.tf_matrix @ q_vec  # shape (N,)

        top_indices = np.argsort(scores)[::-1][:k]
        results = []
        for idx in top_indices:
            if scores[idx] <= 0:
                continue
            doc = self.docs[idx]
            results.append(SearchResult(
                doc_id=doc["id"],
                title=doc["title"],
                category=doc["category"],
                content=doc["content"],
                score=float(round(scores[idx], 4)),
                tags=doc.get("tags", []),
            ))
        return results


class RAGEngine:
    """
    RAG engine backed by TF-IDF cosine similarity search.
    No PyTorch, no sentence-transformers, no downloads needed.
    Instant startup. Good retrieval quality for domain-specific docs.
    """

    def __init__(self,
                 model_name: str = "all-MiniLM-L6-v2",  # kept for API compat
                 index_path: str = "./data/faiss_index",
                 top_k: int = 5):
        self.model_name  = model_name
        self.index_path  = Path(index_path)
        self.top_k       = top_k
        self._tfidf      = TFIDFIndex()
        self.documents: List[Dict] = []
        self._initialized = False

    def initialize(self):
        print("Initializing RAG Engine…")
        self.documents = get_all_docs()
        print(f"  ✓ Loaded {len(self.documents)} documentation chunks")
        self._tfidf.build(self.documents)
        print(f"  ✓ TF-IDF index built (vocab: {len(self._tfidf.vocab)} terms)")
        self._initialized = True
        print("  ✓ RAG Engine ready [TF-IDF search — instant mode]")

    def rebuild_index(self):
        self.documents = get_all_docs()
        self._tfidf.build(self.documents)
        print(f"  ✓ Index rebuilt: {len(self.documents)} docs")

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[SearchResult]:
        if not self._initialized:
            self.initialize()
        return self._tfidf.search(query, top_k or self.top_k)

    def format_context(self, results: List[SearchResult], max_chars: int = 8000) -> str:
        parts, total = [], 0
        for i, r in enumerate(results, 1):
            tags_str = ", ".join(r.tags[:6]) if r.tags else "—"
            section = (
                f"\n### [{i}] {r.title}\n"
                f"**Category:** {r.category} | **Tags:** {tags_str}\n\n"
                f"{r.content.strip()}\n---"
            )
            if total + len(section) > max_chars:
                break
            parts.append(section)
            total += len(section)
        return "\n".join(parts)

    @property
    def is_ready(self) -> bool:
        return self._initialized

    @property
    def search_mode(self) -> str:
        return "tfidf"
