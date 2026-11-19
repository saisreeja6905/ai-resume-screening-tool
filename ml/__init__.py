"""
Machine Learning & Matching Engine Package for Resume Screening.
"""
from ml.tfidf_model import TFIDFModel
from ml.similarity import calculate_cosine_similarity, calculate_jaccard_similarity
from ml.feature_extractor import FeatureExtractor
from ml.score_calculator import ScoreCalculator

__all__ = [
    "TFIDFModel",
    "calculate_cosine_similarity",
    "calculate_jaccard_similarity",
    "FeatureExtractor",
    "ScoreCalculator",
]
