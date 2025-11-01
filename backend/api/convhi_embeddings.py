#!/usr/bin/env python3
"""
ConvHi Embeddings Engine
In-memory semantic index using simple bag-of-words cosine similarity.
Designed as a zero-dependency fallback that can be replaced by real vector DB.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
import math
import re


_TOKEN_PATTERN = re.compile(r"[a-zà-ÿ0-9']+")


def _tokenize(text: str) -> List[str]:
    return _TOKEN_PATTERN.findall(text.lower())


def _build_vector(tokens: List[str]) -> Dict[str, float]:
    counts = Counter(tokens)
    norm = math.sqrt(sum(freq * freq for freq in counts.values())) or 1.0
    return {token: freq / norm for token, freq in counts.items()}


def _cosine_similarity(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
    if not vec_a or not vec_b:
        return 0.0
    # iterate over smaller vector
    if len(vec_a) > len(vec_b):
        vec_a, vec_b = vec_b, vec_a
    return sum(weight * vec_b.get(token, 0.0) for token, weight in vec_a.items())


@dataclass
class SemanticCandidate:
    item_id: str
    score: float
    highlights: List[str]


class ConvHiEmbeddingEngine:
    def __init__(self) -> None:
        # agent_id -> item_id -> vector
        self._vectors: Dict[str, Dict[str, Dict[str, float]]] = defaultdict(dict)
        # agent_id -> item_id -> cached sentences for highlights
        self._sentences: Dict[str, Dict[str, List[str]]] = defaultdict(dict)

    async def index_document(self, agent_id: str, item_id: str, content: str) -> None:
        tokens = _tokenize(content)
        self._vectors[agent_id][item_id] = _build_vector(tokens)
        sentences = re.split(r"[\\.!?\\n]+", content)
        self._sentences[agent_id][item_id] = [s.strip() for s in sentences if s.strip()]

    async def delete_document(self, agent_id: str, item_id: str) -> None:
        self._vectors.get(agent_id, {}).pop(item_id, None)
        self._sentences.get(agent_id, {}).pop(item_id, None)

    async def semantic_search(
        self,
        agent_id: str,
        query: str,
        top_k: int = 5,
        min_score: float = 0.05,
    ) -> List[SemanticCandidate]:
        query_vec = _build_vector(_tokenize(query))
        if not query_vec:
            return []

        results: List[Tuple[str, float]] = []
        for item_id, vector in self._vectors.get(agent_id, {}).items():
            score = _cosine_similarity(query_vec, vector)
            if score >= min_score:
                results.append((item_id, score))

        results.sort(key=lambda pair: pair[1], reverse=True)
        sliced = results[:max(1, top_k)]

        candidates: List[SemanticCandidate] = []
        for item_id, score in sliced:
            sentences = self._sentences.get(agent_id, {}).get(item_id, [])
            highlights = self._extract_highlights(sentences, query_vec.keys())
            candidates.append(SemanticCandidate(item_id=item_id, score=score, highlights=highlights))
        return candidates

    def _extract_highlights(self, sentences: List[str], keywords: List[str]) -> List[str]:
        if not sentences:
            return []
        lowers = [kw.lower() for kw in keywords]
        highlights: List[str] = []
        for sentence in sentences:
            low = sentence.lower()
            if any(kw in low for kw in lowers):
                highlights.append(sentence.strip())
            if len(highlights) >= 3:
                break
        return highlights[:3]


embedding_engine = ConvHiEmbeddingEngine()

