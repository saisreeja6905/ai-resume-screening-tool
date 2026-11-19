from datetime import datetime, timezone
from backend.extensions import db


class RecruiterNote(db.Model):
    __tablename__ = "recruiter_notes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job_descriptions.id", ondelete="SET NULL"), nullable=True, index=True)
    note_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user = db.relationship("User", back_populates="recruiter_notes")
    candidate = db.relationship("Candidate", back_populates="recruiter_notes")
    job = db.relationship("JobDescription", back_populates="recruiter_notes")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "author_name": self.user.full_name if self.user else "Unknown Recruiter",
            "candidate_id": self.candidate_id,
            "job_id": self.job_id,
            "job_title": self.job.title if self.job else None,
            "note_text": self.note_text,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<RecruiterNote id={self.id} author={self.user_id} cand={self.candidate_id}>"
