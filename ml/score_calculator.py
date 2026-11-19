from typing import Dict, Any, List


class ScoreCalculator:
    """Calculates weighted match score and generates clear, explainable breakdowns."""

    # Explicit Weights
    WEIGHT_SKILLS = 0.35
    WEIGHT_TFIDF = 0.25
    WEIGHT_EXPERIENCE = 0.20
    WEIGHT_EDUCATION = 0.10
    WEIGHT_KEYWORDS = 0.10

    @classmethod
    def calculate_overall_score(
        cls,
        skill_score: float,
        tfidf_similarity: float,
        experience_score: float,
        education_score: float,
        keyword_score: float,
    ) -> float:
        """
        Compute weighted composite score (0 to 100).
        TF-IDF similarity is given as 0.0 - 1.0 (scaled to 100).
        """
        tfidf_scaled = min(tfidf_similarity * 100.0, 100.0)

        overall = (
            (skill_score * cls.WEIGHT_SKILLS)
            + (tfidf_scaled * cls.WEIGHT_TFIDF)
            + (experience_score * cls.WEIGHT_EXPERIENCE)
            + (education_score * cls.WEIGHT_EDUCATION)
            + (keyword_score * cls.WEIGHT_KEYWORDS)
        )

        return round(float(min(max(overall, 0.0), 100.0)), 1)

    @classmethod
    def generate_explanation(
        cls,
        overall_score: float,
        skill_eval: Dict[str, Any],
        exp_eval: Dict[str, Any],
        edu_eval: Dict[str, Any],
        tfidf_similarity: float,
        keyword_eval: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate comprehensive, human-readable explanations of the match score.
        Adheres to ethical AI guidelines (decision-support signal, not automated decision).
        """
        matched_req = skill_eval.get("matched_required_skills", [])
        missing_req = skill_eval.get("missing_required_skills", [])
        matched_pref = skill_eval.get("matched_preferred_skills", [])

        # Construct summary statements
        strengths: List[str] = []
        gaps: List[str] = []

        # Skills breakdown
        if matched_req:
            strengths.append(f"Possesses core required skills: {', '.join(matched_req[:5])}.")
        if matched_pref:
            strengths.append(f"Brings preferred qualifications: {', '.join(matched_pref[:4])}.")
        if missing_req:
            gaps.append(f"Missing key required skills: {', '.join(missing_req[:5])}.")

        # Experience breakdown
        exp_score = exp_eval.get("experience_score", 0.0)
        if exp_score >= 85:
            strengths.append(exp_eval.get("explanation", "Experience aligns with job profile."))
        else:
            gaps.append(exp_eval.get("explanation", "Experience deficit compared to requirements."))

        # Education breakdown
        edu_score = edu_eval.get("education_score", 0.0)
        if edu_score >= 85:
            strengths.append(edu_eval.get("explanation", "Education meets role requirements."))
        else:
            gaps.append(edu_eval.get("explanation", "Education profile differs from preferred degree."))

        # Content similarity
        similarity_pct = round(tfidf_similarity * 100, 1)
        if similarity_pct >= 60:
            strengths.append(f"High semantic overlap ({similarity_pct}%) with job description terminology.")
        elif similarity_pct < 30:
            gaps.append(f"Low semantic resume-to-job text alignment ({similarity_pct}%).")

        # Plain english recommendation
        if overall_score >= 80:
            recommendation = (
                "Highly recommended for interview screening. Candidate exhibits strong skill alignment "
                "and relevant professional background for this role."
            )
        elif overall_score >= 65:
            recommendation = (
                "Recommended for recruiter review. Candidate demonstrates core competency with few minor gaps "
                "that can be evaluated during an initial screening call."
            )
        elif overall_score >= 50:
            recommendation = (
                "Borderline match. Candidate fulfills some basic requirements but lacks multiple core or preferred "
                "competencies required for this position."
            )
        else:
            recommendation = (
                "Low alignment with job criteria. Significant discrepancies in required skills or experience level."
            )

        return {
            "overall_score": overall_score,
            "weights": {
                "skills_weight": f"{int(cls.WEIGHT_SKILLS * 100)}%",
                "tfidf_weight": f"{int(cls.WEIGHT_TFIDF * 100)}%",
                "experience_weight": f"{int(cls.WEIGHT_EXPERIENCE * 100)}%",
                "education_weight": f"{int(cls.WEIGHT_EDUCATION * 100)}%",
                "keywords_weight": f"{int(cls.WEIGHT_KEYWORDS * 100)}%",
            },
            "scores": {
                "skill_score": skill_eval.get("skill_score", 0.0),
                "tfidf_similarity_percent": round(tfidf_similarity * 100.0, 1),
                "experience_score": exp_eval.get("experience_score", 0.0),
                "education_score": edu_eval.get("education_score", 0.0),
                "keyword_score": keyword_eval.get("keyword_score", 0.0),
            },
            "strengths": strengths,
            "gaps": gaps,
            "recommendation": recommendation,
            "methodology_disclaimer": (
                "Scores represent algorithmic similarity and keyword/feature overlap between the candidate's "
                "resume and the job requirements. This metric serves strictly as a decision-support aid for human "
                "reviewers and must not be used as an autonomous hiring decision."
            ),
        }
