from datetime import datetime, timezone
from backend.extensions import db


class JobDescription(db.Model):
    __tablename__ = "job_descriptions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False, index=True)
    department = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.JSON, default=list, nullable=False)
    preferred_skills = db.Column(db.JSON, default=list, nullable=False)
    min_experience = db.Column(db.Float, default=0.0, nullable=False)
    max_experience = db.Column(db.Float, nullable=True)
    education_level = db.Column(db.String(100), nullable=True)  # e.g., Bachelor's, Master's, Ph.D.
    employment_type = db.Column(db.String(50), default="full-time", nullable=False)  # full-time, part-time, contract
    location = db.Column(db.String(150), nullable=True)
    salary_range = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)

    created_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    creator = db.relationship("User", back_populates="job_descriptions")
    match_results = db.relationship(
        "MatchResult",
        back_populates="job",
        cascade="all, delete-orphan",
        order_by="desc(MatchResult.overall_score)",
        lazy="dynamic",
    )
    recruiter_notes = db.relationship(
        "RecruiterNote",
        back_populates="job",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    screening_history = db.relationship(
        "ScreeningHistory",
        back_populates="job",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    @property
    def candidate_count(self) -> int:
        return self.match_results.count()

    @property
    def experience_display(self) -> str:
        if self.min_experience is not None and self.max_experience is not None:
            return f"{self.min_experience:g} - {self.max_experience:g} yrs"
        elif self.min_experience:
            return f"{self.min_experience:g}+ yrs"
        return "Any experience"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "department": self.department,
            "description": self.description,
            "required_skills": self.required_skills or [],
            "preferred_skills": self.preferred_skills or [],
            "min_experience": self.min_experience,
            "max_experience": self.max_experience,
            "education_level": self.education_level,
            "employment_type": self.employment_type,
            "location": self.location,
            "salary_range": self.salary_range,
            "is_active": self.is_active,
            "candidate_count": self.candidate_count,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<JobDescription {self.title} ({self.department})>"
