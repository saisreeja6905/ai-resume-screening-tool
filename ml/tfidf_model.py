import re
from typing import List, Tuple, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer


class TFIDFModel:
    """TF-IDF Vectorizer wrapper tailored for technical resume and job description text matching."""

    def __init__(self, max_features: int = 5000, ngram_range: Tuple[int, int] = (1, 2)):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=ngram_range,
            max_features=max_features,
            sublinear_tf=True,
            token_pattern=r"(?u)\b[a-zA-Z0-9_+#.]{2,}\b",  # Retain C++, C#, .NET
        )
        self.is_fitted = False

    def preprocess_text(self, text: str) -> str:
        """Preprocess text before vectorization while preserving technical tokens."""
        if not text:
            return ""

        # Normalize common symbol terms
        cleaned = text.replace("C++", " cplusplus ").replace("c++", " cplusplus ")
        cleaned = cleaned.replace("C#", " csharp ").replace("c#", " csharp ")
        cleaned = cleaned.replace(".NET", " dotnet ").replace(".net", " dotnet ")
        cleaned = cleaned.replace("CI/CD", " cicd ").replace("ci/cd", " cicd ")

        # Remove URLs and emails
        cleaned = re.sub(r"https?://\S+|www\.\S+", " ", cleaned)
        cleaned = re.sub(r"\b[\w.-]+?@[\w.-]+?\.\w+\b", " ", cleaned)

        # Replace punctuation except alphanumerics
        cleaned = re.sub(r"[^\w\s]", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned)

        return cleaned.strip().lower()

    def fit_transform(self, documents: List[str]):
        """Fit vectorizer on a corpus of documents and return sparse matrix."""
        preprocessed = [self.preprocess_text(doc) for doc in documents]
        tfidf_matrix = self.vectorizer.fit_transform(preprocessed)
        self.is_fitted = True
        return tfidf_matrix

    def transform(self, documents: List[str]):
        """Transform documents using fitted vectorizer."""
        preprocessed = [self.preprocess_text(doc) for doc in documents]
        if not self.is_fitted:
            return self.fit_transform(documents)
        return self.vectorizer.transform(preprocessed)

    def extract_top_keywords(self, text: str, top_n: int = 15) -> List[Dict[str, Any]]:
        """Extract the most significant TF-IDF keywords/n-grams from a document."""
        if not text or not text.strip():
            return []

        doc_clean = self.preprocess_text(text)
        if not doc_clean:
            return []

        local_vec = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=1000,
            token_pattern=r"(?u)\b[a-zA-Z0-9_+#.]{2,}\b",
        )
        try:
            tfidf_matrix = local_vec.fit_transform([doc_clean])
            feature_names = local_vec.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]

            scored_words = sorted(
                zip(feature_names, scores),
                key=lambda x: x[1],
                reverse=True
            )

            # Map back cplusplus -> C++, csharp -> C#, etc.
            reverse_map = {
                "cplusplus": "C++",
                "csharp": "C#",
                "dotnet": ".NET",
                "cicd": "CI/CD",
            }

            results = []
            for word, score in scored_words[:top_n]:
                display_word = reverse_map.get(word, word)
                results.append({
                    "keyword": display_word,
                    "score": round(float(score), 4),
                })
            return results
        except Exception:
            return []
