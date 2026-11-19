from datetime import datetime, timezone
from backend.extensions import db


class MatchResult(db.Model):
    __tablename__ = "match_results"

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True)

    # Component Scores (0 to 100)
    overall_score = db.Column(db.Float, default=0.0, nullable=False, index=True)
    skill_score = db.Column(db.Float, default=0.0, nullable=False)
    experience_score = db.Column(db.Float, default=0.0, nullable=False)
    education_score = db.Column(db.Float, default=0.0, nullable=False)
    keyword_score = db.Column(db.Float, default=0.0, nullable=False)
    tfidf_similarity = db.Column(db.Float, default=0.0, nullable=False)

    # Structured Explainable Breakdown
    matched_skills = db.Column(db.JSON, default=list, nullable=False)
    missing_required_skills = db.Column(db.JSON, default=list, nullable=False)
    missing_preferred_skills = db.Column(db.JSON, default=list, nullable=False)
    additional_skills = db.Column(db.JSON, default=list, nullable=False)
    score_explanation = db.Column(db.JSON, default=dict, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("candidate_id", "job_id", name="uq_candidate_job_match"),
    )

    # Relationships
    candidate = db.relationship("Candidate", back_populates="match_results")
    job = db.relationship("JobDescription", back_populates="match_results")
    resume = db.relationship("Resume", back_populates="match_results")

    @property
    def score_badge_class(self) -> str:
        if self.overall_score >= 80:
            return "success"
        elif self.overall_score >= 60:
            return "primary"
        elif self.overall_score >= 40:
            return "warning"
        return "danger"

    @property
    def score_label(self) -> str:
        if self.overall_score >= 80:
            return "Strong Match"
        elif self.overall_score >= 65:
            return "Good Match"
        elif self.overall_score >= 50:
            return "Moderate Match"
        elif self.overall_score >= 35:
            return "Low Match"
        return "Poor Match"

    def to_dict(self):
        return {
            "id": self.id,
            "candidate_id": self.candidate_id,
            "candidate_name": self.candidate.full_name if self.candidate else None,
            "job_id": self.job_id,
            "job_title": self.job.title if self.job else None,
            "resume_id": self.resume_id,
            "overall_score": round(self.overall_score, 1),
            "skill_score": round(self.skill_score, 1),
            "experience_score": round(self.experience_score, 1),
            "education_score": round(self.education_score, 1),
            "keyword_score": round(self.keyword_score, 1),
            "tfidf_similarity": round(self.tfidf_similarity, 3),
            "matched_skills": self.matched_skills or [],
            "missing_required_skills": self.missing_required_skills or [],
            "missing_preferred_skills": self.missing_preferred_skills or [],
            "additional_skills": self.additional_skills or [],
            "score_explanation": self.score_explanation or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<MatchResult cand={self.candidate_id} job={self.job_id} score={self.overall_score:.1f}>"
