from datetime import datetime, timezone
from backend.extensions import db


class ScreeningHistory(db.Model):
    __tablename__ = "screening_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    # upload, parse, match, status_change, note_added, report_generated
    action = db.Column(db.String(50), nullable=False, index=True)
    details = db.Column(db.JSON, default=dict, nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id", ondelete="CASCADE"), nullable=True, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    user = db.relationship("User", back_populates="screening_history")
    candidate = db.relationship("Candidate", back_populates="screening_history")
    job = db.relationship("JobDescription", back_populates="screening_history")

    @classmethod
    def log(cls, action: str, details: dict, user_id=None, candidate_id=None, job_id=None):
        entry = cls(
            action=action,
            details=details or {},
            user_id=user_id,
            candidate_id=candidate_id,
            job_id=job_id,
        )
        db.session.add(entry)
        return entry

    def to_dict(self):
        return {
            "id": self.id,
            "action": self.action,
            "details": self.details,
            "user_id": self.user_id,
            "user_name": self.user.full_name if self.user else "System",
            "candidate_id": self.candidate_id,
            "candidate_name": self.candidate.full_name if self.candidate else None,
            "job_id": self.job_id,
            "job_title": self.job.title if self.job else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<ScreeningHistory action={self.action} time={self.created_at}>"
