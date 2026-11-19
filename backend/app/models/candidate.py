from datetime import datetime, timezone
from backend.extensions import db


class Candidate(db.Model):
    __tablename__ = "candidates"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    phone = db.Column(db.String(50), nullable=True)
    linkedin_url = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(150), nullable=True)
    summary = db.Column(db.Text, nullable=True)
    years_experience = db.Column(db.Float, default=0.0, nullable=False)
    highest_education = db.Column(db.String(150), nullable=True)
    current_title = db.Column(db.String(150), nullable=True)
    current_company = db.Column(db.String(150), nullable=True)

    # Status: new, screening, shortlisted, rejected, hired
    status = db.Column(db.String(30), default="new", nullable=False, index=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    resumes = db.relationship(
        "Resume",
        back_populates="candidate",
        cascade="all, delete-orphan",
        lazy="joined",
        order_by="desc(Resume.upload_date)",
    )
    candidate_skills = db.relationship(
        "CandidateSkill",
        back_populates="candidate",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    match_results = db.relationship(
        "MatchResult",
        back_populates="candidate",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    recruiter_notes = db.relationship(
        "RecruiterNote",
        back_populates="candidate",
        cascade="all, delete-orphan",
        order_by="desc(RecruiterNote.created_at)",
        lazy="dynamic",
    )
    screening_history = db.relationship(
        "ScreeningHistory",
        back_populates="candidate",
        cascade="all, delete-orphan",
        order_by="desc(ScreeningHistory.created_at)",
        lazy="dynamic",
    )

    @property
    def full_name(self) -> str:
        if self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.first_name

    @property
    def latest_resume(self):
        return self.resumes[0] if self.resumes else None

    @property
    def skill_names_list(self) -> list:
        return [cs.skill.name for cs in self.candidate_skills if cs.skill]

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "linkedin_url": self.linkedin_url,
            "location": self.location,
            "summary": self.summary,
            "years_experience": self.years_experience,
            "highest_education": self.highest_education,
            "current_title": self.current_title,
            "current_company": self.current_company,
            "status": self.status,
            "skills": [cs.to_dict() for cs in self.candidate_skills],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Candidate {self.full_name} ({self.status})>"
