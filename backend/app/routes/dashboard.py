from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func

from backend.extensions import db
from backend.app.models.candidate import Candidate
from backend.app.models.resume import Resume
from backend.app.models.job_description import JobDescription
from backend.app.models.match_result import MatchResult
from backend.app.models.screening_history import ScreeningHistory
from backend.app.models.skill import Skill, CandidateSkill

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    # Key Metrics
    total_resumes = Resume.query.count()
    total_active_jobs = JobDescription.query.filter_by(is_active=True).count()
    total_candidates = Candidate.query.count()

    avg_score_query = db.session.query(func.avg(MatchResult.overall_score)).scalar()
    avg_match_score = round(float(avg_score_query), 1) if avg_score_query is not None else 0.0

    # Candidates by Status Distribution
    status_counts_raw = (
        db.session.query(Candidate.status, func.count(Candidate.id))
        .group_by(Candidate.status)
        .all()
    )
    status_map = {status: count for status, count in status_counts_raw}
    candidate_statuses = {
        "new": status_map.get("new", 0),
        "screening": status_map.get("screening", 0),
        "shortlisted": status_map.get("shortlisted", 0),
        "rejected": status_map.get("rejected", 0),
        "hired": status_map.get("hired", 0),
    }

    # Top Skills Distribution (Top 8 most frequent skills)
    top_skills_raw = (
        db.session.query(Skill.name, func.count(CandidateSkill.id).label("skill_count"))
        .join(CandidateSkill, Skill.id == CandidateSkill.skill_id)
        .group_by(Skill.id, Skill.name)
        .order_by(func.count(CandidateSkill.id).desc())
        .limit(8)
        .all()
    )
    skill_chart_labels = [s[0] for s in top_skills_raw]
    skill_chart_counts = [s[1] for s in top_skills_raw]

    # Recent Activity (Last 10 screening history logs)
    recent_activity = (
        ScreeningHistory.query.order_by(ScreeningHistory.created_at.desc())
        .limit(10)
        .all()
    )

    # Top Matching Candidates
    top_matches = (
        MatchResult.query.order_by(MatchResult.overall_score.desc())
        .limit(6)
        .all()
    )

    return render_template(
        "dashboard/index.html",
        total_resumes=total_resumes,
        total_active_jobs=total_active_jobs,
        total_candidates=total_candidates,
        avg_match_score=avg_match_score,
        candidate_statuses=candidate_statuses,
        skill_chart_labels=skill_chart_labels,
        skill_chart_counts=skill_chart_counts,
        recent_activity=recent_activity,
        top_matches=top_matches,
    )
