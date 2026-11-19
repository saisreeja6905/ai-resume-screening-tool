import logging
from typing import Dict, Any, Optional, List

from backend.extensions import db
from backend.app.models.candidate import Candidate
from backend.app.models.resume import Resume
from backend.app.models.job_description import JobDescription
from backend.app.models.match_result import MatchResult
from backend.app.models.screening_history import ScreeningHistory

from ml.tfidf_model import TFIDFModel
from ml.similarity import calculate_cosine_similarity
from ml.feature_extractor import FeatureExtractor
from ml.score_calculator import ScoreCalculator

logger = logging.getLogger(__name__)


class MatchingEngine:
    """Service orchestrating candidate resume screening against job descriptions."""

    def __init__(self):
        self.tfidf_model = TFIDFModel()
        self.feature_extractor = FeatureExtractor()
        self.score_calculator = ScoreCalculator()

    def match_candidate_to_job(
        self,
        candidate: Candidate,
        job: JobDescription,
        resume: Optional[Resume] = None,
        save_db: bool = True,
        user_id: Optional[int] = None,
    ) -> MatchResult:
        """
        Run complete AI matching pipeline between a Candidate and a JobDescription.
        Updates or creates a MatchResult record.
        """
        if resume is None:
            resume = candidate.latest_resume

        resume_text = resume.raw_text if (resume and resume.raw_text) else ""
        if not resume_text and candidate.summary:
            resume_text = f"{candidate.full_name}\n{candidate.summary}\n{' '.join(candidate.skill_names_list)}"

        job_full_text = f"{job.title}\n{job.department}\n{job.description}\n{' '.join(job.required_skills or [])}\n{' '.join(job.preferred_skills or [])}"

        # 1. TF-IDF & Cosine Similarity
        try:
            tfidf_matrix = self.tfidf_model.fit_transform([resume_text, job_full_text])
            tfidf_similarity = calculate_cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        except Exception as e:
            logger.warning("TF-IDF vectorization failed: %s", str(e))
            tfidf_similarity = 0.0

        # 2. Skill Evaluation
        candidate_skills = candidate.skill_names_list
        if not candidate_skills and resume and resume.parsed_data:
            candidate_skills = [
                s.get("name") for s in resume.parsed_data.get("skills", []) if s.get("name")
            ]

        skill_eval = self.feature_extractor.evaluate_skills(
            candidate_skills=candidate_skills,
            required_skills=job.required_skills or [],
            preferred_skills=job.preferred_skills or [],
        )

        # 3. Experience Evaluation
        exp_eval = self.feature_extractor.evaluate_experience(
            candidate_years=candidate.years_experience,
            min_years=job.min_experience,
            max_years=job.max_experience,
        )

        # 4. Education Evaluation
        edu_eval = self.feature_extractor.evaluate_education(
            candidate_edu=candidate.highest_education,
            required_edu=job.education_level,
        )

        # 5. Keyword Coverage
        keyword_eval = self.feature_extractor.evaluate_keyword_coverage(
            resume_text=resume_text,
            job_text=job_full_text,
        )

        # 6. Overall Weighted Score
        skill_score = skill_eval["skill_score"]
        experience_score = exp_eval["experience_score"]
        education_score = edu_eval["education_score"]
        keyword_score = keyword_eval["keyword_score"]

        overall_score = self.score_calculator.calculate_overall_score(
            skill_score=skill_score,
            tfidf_similarity=tfidf_similarity,
            experience_score=experience_score,
            education_score=education_score,
            keyword_score=keyword_score,
        )

        # 7. Generate Explainable Breakdown
        explanation = self.score_calculator.generate_explanation(
            overall_score=overall_score,
            skill_eval=skill_eval,
            exp_eval=exp_eval,
            edu_eval=edu_eval,
            tfidf_similarity=tfidf_similarity,
            keyword_eval=keyword_eval,
        )

        # 8. Save or Update MatchResult
        match_record = MatchResult.query.filter_by(
            candidate_id=candidate.id, job_id=job.id
        ).first()

        if not match_record:
            match_record = MatchResult(
                candidate_id=candidate.id,
                job_id=job.id,
                resume_id=resume.id if resume else None,
            )
            db.session.add(match_record)

        match_record.resume_id = resume.id if resume else match_record.resume_id
        match_record.overall_score = overall_score
        match_record.skill_score = skill_score
        match_record.experience_score = experience_score
        match_record.education_score = education_score
        match_record.keyword_score = keyword_score
        match_record.tfidf_similarity = float(tfidf_similarity)

        match_record.matched_skills = skill_eval.get("matched_skills", [])
        match_record.missing_required_skills = skill_eval.get("missing_required_skills", [])
        match_record.missing_preferred_skills = skill_eval.get("missing_preferred_skills", [])
        match_record.additional_skills = skill_eval.get("additional_skills", [])
        match_record.score_explanation = explanation

        if save_db:
            db.session.commit()

            # Log history
            ScreeningHistory.log(
                action="match",
                details={
                    "job_title": job.title,
                    "candidate_name": candidate.full_name,
                    "overall_score": overall_score,
                },
                user_id=user_id,
                candidate_id=candidate.id,
                job_id=job.id,
            )
            db.session.commit()

        return match_record

    def match_all_candidates_for_job(self, job_id: int, user_id: Optional[int] = None) -> List[MatchResult]:
        """Match all registered candidates against a specific job description."""
        job = JobDescription.query.get(job_id)
        if not job:
            raise ValueError(f"Job with ID {job_id} not found.")

        candidates = Candidate.query.all()
        results = []

        for candidate in candidates:
            res = self.match_candidate_to_job(candidate, job, save_db=True, user_id=user_id)
            results.append(res)

        return results

    def match_candidate_across_active_jobs(
        self, candidate_id: int, user_id: Optional[int] = None
    ) -> List[MatchResult]:
        """Match a candidate against all active job descriptions."""
        candidate = Candidate.query.get(candidate_id)
        if not candidate:
            raise ValueError(f"Candidate with ID {candidate_id} not found.")

        active_jobs = JobDescription.query.filter_by(is_active=True).all()
        results = []

        for job in active_jobs:
            res = self.match_candidate_to_job(candidate, job, save_db=True, user_id=user_id)
            results.append(res)

        return results


# Singleton instance
matching_engine = MatchingEngine()
