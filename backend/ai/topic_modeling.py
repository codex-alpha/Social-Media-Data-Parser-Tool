"""Topic Modeling using TF-IDF + clustering."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation, NMF
from typing import List, Dict, Any, Optional
from models.schemas import TopicResult
import numpy as np
import re


class TopicModeler:
    """Topic discovery and modeling engine."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words="english",
            min_df=1,
            max_df=0.95,
            ngram_range=(1, 2),
        )
        self.stop_words = {
            "rt", "amp", "https", "http", "co", "via", "like",
            "just", "get", "got", "im", "dont", "ive", "thats",
            "would", "could", "one", "also", "really", "know",
        }

    def _preprocess(self, text: str) -> str:
        """Clean text for topic modeling."""
        text = text.lower()
        text = re.sub(r"http\S+|www\S+", "", text)
        text = re.sub(r"@\w+", "", text)
        text = re.sub(r"#(\w+)", r"\1", text)
        text = re.sub(r"[^a-zA-Z\s]", "", text)
        words = text.split()
        words = [w for w in words if w not in self.stop_words and len(w) > 2]
        return " ".join(words)

    def extract_topics(
        self, texts: List[str], n_topics: int = 5, method: str = "nmf"
    ) -> List[TopicResult]:
        """Extract topics from a collection of texts."""
        if len(texts) < 2:
            return [
                TopicResult(
                    topic_id=0,
                    label="Insufficient data",
                    keywords=["need", "more", "documents"],
                    score=0.0,
                    document_count=len(texts),
                )
            ]

        cleaned = [self._preprocess(t) for t in texts]
        cleaned = [t for t in cleaned if t.strip()]

        if len(cleaned) < 2:
            return [
                TopicResult(
                    topic_id=0,
                    label="No extractable content",
                    keywords=[],
                    score=0.0,
                    document_count=0,
                )
            ]

        n_topics = min(n_topics, len(cleaned))

        tfidf_matrix = self.vectorizer.fit_transform(cleaned)
        feature_names = self.vectorizer.get_feature_names_out()

        if method == "nmf":
            model = NMF(n_components=n_topics, random_state=42, max_iter=300)
        else:
            model = LatentDirichletAllocation(
                n_components=n_topics, random_state=42, max_iter=20
            )

        doc_topics = model.fit_transform(tfidf_matrix)
        results = []

        for idx, topic_vec in enumerate(model.components_):
            top_indices = topic_vec.argsort()[-8:][::-1]
            keywords = [feature_names[i] for i in top_indices]
            score = float(topic_vec[top_indices[0]])
            doc_count = int(np.sum(doc_topics.argmax(axis=1) == idx))

            # Auto-generate topic label from top keywords
            label = " / ".join(keywords[:3]).title()

            results.append(
                TopicResult(
                    topic_id=idx,
                    label=label,
                    keywords=keywords,
                    score=round(score, 4),
                    document_count=doc_count,
                )
            )

        return sorted(results, key=lambda x: x.document_count, reverse=True)

    def get_trending_keywords(self, texts: List[str], top_n: int = 20) -> List[Dict[str, Any]]:
        """Extract trending keywords with TF-IDF scores."""
        cleaned = [self._preprocess(t) for t in texts if t.strip()]
        if not cleaned:
            return []

        tfidf_matrix = self.vectorizer.fit_transform(cleaned)
        feature_names = self.vectorizer.get_feature_names_out()
        avg_scores = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
        top_indices = avg_scores.argsort()[-top_n:][::-1]

        return [
            {"keyword": feature_names[i], "score": round(float(avg_scores[i]), 4)}
            for i in top_indices
        ]


# Singleton
topic_modeler = TopicModeler()
