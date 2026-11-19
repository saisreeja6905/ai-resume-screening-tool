from datetime import datetime, timezone
from backend.extensions import db


class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id", ondelete="CASCADE"), nullable=True, index=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, default=0, nullable=False)  # in bytes
    upload_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    raw_text = db.Column(db.Text, nullable=True)
    parsed_data = db.Column(db.JSON, default=dict, nullable=True)

    # processing_status: uploaded, processing, completed, failed
    processing_status = db.Column(db.String(30), default="uploaded", nullable=False, index=True)
    error_message = db.Column(db.Text, nullable=True)

    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    candidate = db.relationship("Candidate", back_populates="resumes")
    uploader = db.relationship("User", back_populates="resumes_uploaded", foreign_keys=[uploaded_by])
    match_results = db.relationship("MatchResult", back_populates="resume", cascade="all, delete-orphan", lazy="dynamic")

    @property
    def formatted_file_size(self) -> str:
        size = self.file_size
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def to_dict(self):
        return {
            "id": self.id,
            "candidate_id": self.candidate_id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_size": self.formatted_file_size,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "processing_status": self.processing_status,
            "error_message": self.error_message,
            "uploaded_by": self.uploaded_by,
            "has_raw_text": bool(self.raw_text),
            "parsed_data": self.parsed_data or {},
        }

    def __repr__(self):
        return f"<Resume {self.original_filename} (status={self.processing_status})>"
