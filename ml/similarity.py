from typing import Set, List, Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def calculate_cosine_similarity(vec1, vec2) -> float:
    """
    Compute cosine similarity between two feature vectors.
    Returns float value between 0.0 and 1.0.
    """
    if vec1 is None or vec2 is None:
        return 0.0

    try:
        sim = cosine_similarity(vec1, vec2)[0][0]
        # Ensure bounded [0.0, 1.0]
        return float(np.clip(sim, 0.0, 1.0))
    except Exception:
        return 0.0


def calculate_jaccard_similarity(set1: Set[Any], set2: Set[Any]) -> float:
    """
    Compute Jaccard similarity coefficient: |A ∩ B| / |A ∪ B|.
    Returns float value between 0.0 and 1.0.
    """
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0

    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))

    if union == 0:
        return 0.0

    return float(intersection / union)


def calculate_overlap_ratio(candidate_items: Set[str], target_items: Set[str]) -> float:
    """
    Compute overlap ratio of required target items present in candidate items:
    |candidate ∩ target| / |target|.
    Returns float value between 0.0 and 1.0.
    """
    if not target_items:
        return 1.0
    if not candidate_items:
        return 0.0

    matched = len(target_items.intersection(candidate_items))
    return float(matched / len(target_items))
