from backend.extensions import db


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    # technical, soft, tool, language, framework, database, cloud, devops, etc.
    category = db.Column(db.String(50), default="technical", nullable=False, index=True)
    normalized_name = db.Column(db.String(100), nullable=False, index=True)

    candidate_skills = db.relationship("CandidateSkill", back_populates="skill", cascade="all, delete-orphan", lazy="dynamic")

    @classmethod
    def get_or_create(cls, name: str, category: str = "technical"):
        normalized = name.strip().lower()
        skill = cls.query.filter_by(normalized_name=normalized).first()
        if not skill:
            skill = cls(name=name.strip(), category=category, normalized_name=normalized)
            db.session.add(skill)
            db.session.flush()
        return skill

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "normalized_name": self.normalized_name,
        }

    def __repr__(self):
        return f"<Skill {self.name} [{self.category}]>"


class CandidateSkill(db.Model):
    __tablename__ = "candidate_skills"

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    # beginner, intermediate, advanced, expert
    proficiency_level = db.Column(db.String(30), nullable=True)
    years_used = db.Column(db.Float, nullable=True)
    # resume, manual, assessment
    source = db.Column(db.String(30), default="resume", nullable=False)

    __table_args__ = (
        db.UniqueConstraint("candidate_id", "skill_id", name="uq_candidate_skill"),
    )

    candidate = db.relationship("Candidate", back_populates="candidate_skills")
    skill = db.relationship("Skill", back_populates="candidate_skills", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "skill_id": self.skill_id,
            "name": self.skill.name if self.skill else None,
            "category": self.skill.category if self.skill else "technical",
            "proficiency_level": self.proficiency_level,
            "years_used": self.years_used,
            "source": self.source,
        }

    def __repr__(self):
        skill_name = self.skill.name if self.skill else self.skill_id
        return f"<CandidateSkill candidate={self.candidate_id} skill={skill_name}>"
