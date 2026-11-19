from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from backend.extensions import db
from backend.app.models.job_description import JobDescription
from backend.app.models.match_result import MatchResult
from backend.app.models.screening_history import ScreeningHistory
from backend.app.services.matching_engine import matching_engine

jobs_bp = Blueprint("jobs", __name__)


def parse_skill_list(raw_input: str) -> list:
    """Parse comma, newline, or semicolon delimited skills into clean list."""
    if not raw_input:
        return []
    import re
    items = re.split(r"[,;\n]+", raw_input)
    return [s.strip() for s in items if s.strip()]


@jobs_bp.route("/")
@login_required
def list_jobs():
    search_query = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()
    dept_filter = request.args.get("dept", "").strip()

    query = JobDescription.query

    if search_query:
        query = query.filter(
            (JobDescription.title.ilike(f"%{search_query}%"))
            | (JobDescription.description.ilike(f"%{search_query}%"))
        )

    if status_filter == "active":
        query = query.filter_by(is_active=True)
    elif status_filter == "inactive":
        query = query.filter_by(is_active=False)

    if dept_filter:
        query = query.filter(JobDescription.department.ilike(f"%{dept_filter}%"))

    jobs = query.order_by(JobDescription.created_at.desc()).all()

    # Get unique departments for filter dropdown
    departments = [
        d[0] for d in db.session.query(JobDescription.department).distinct().order_by(JobDescription.department).all()
        if d[0]
    ]

    return render_template(
        "jobs/list.html",
        jobs=jobs,
        departments=departments,
        search_query=search_query,
        status_filter=status_filter,
        dept_filter=dept_filter,
    )


@jobs_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        department = request.form.get("department", "").strip()
        description = request.form.get("description", "").strip()
        req_skills_raw = request.form.get("required_skills", "")
        pref_skills_raw = request.form.get("preferred_skills", "")
        min_exp = float(request.form.get("min_experience", 0) or 0)
        max_exp = float(request.form.get("max_experience")) if request.form.get("max_experience") else None
        edu_level = request.form.get("education_level", "").strip()
        emp_type = request.form.get("employment_type", "full-time").strip()
        location = request.form.get("location", "").strip()
        salary_range = request.form.get("salary_range", "").strip()
        is_active = bool(request.form.get("is_active", True))

        if not title or not department or not description:
            flash("Job title, department, and description are required.", "danger")
            return render_template("jobs/create.html")

        required_skills = parse_skill_list(req_skills_raw)
        preferred_skills = parse_skill_list(pref_skills_raw)

        job = JobDescription(
            title=title,
            department=department,
            description=description,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            min_experience=min_exp,
            max_experience=max_exp,
            education_level=edu_level or "Bachelor's Degree",
            employment_type=emp_type,
            location=location,
            salary_range=salary_range,
            is_active=is_active,
            created_by=current_user.id,
        )
        db.session.add(job)
        db.session.commit()

        # Automatically screen existing candidates against this new job
        try:
            matching_engine.match_all_candidates_for_job(job.id, user_id=current_user.id)
        except Exception as e:
            flash(f"Job created, but initial candidate screening encountered: {str(e)}", "warning")

        flash(f"Job posting '{job.title}' created and initial screening completed!", "success")
        return redirect(url_for("jobs.detail", id=job.id))

    return render_template("jobs/create.html")


@jobs_bp.route("/<int:id>")
@login_required
def detail(id):
    job = JobDescription.query.get_or_404(id)

    # Fetch ranked match results
    ranked_matches = (
        MatchResult.query.filter_by(job_id=job.id)
        .order_by(MatchResult.overall_score.desc())
        .all()
    )

    return render_template("jobs/detail.html", job=job, matches=ranked_matches)


@jobs_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    job = JobDescription.query.get_or_404(id)

    if request.method == "POST":
        job.title = request.form.get("title", "").strip()
        job.department = request.form.get("department", "").strip()
        job.description = request.form.get("description", "").strip()
        job.required_skills = parse_skill_list(request.form.get("required_skills", ""))
        job.preferred_skills = parse_skill_list(request.form.get("preferred_skills", ""))
        job.min_experience = float(request.form.get("min_experience", 0) or 0)
        job.max_experience = float(request.form.get("max_experience")) if request.form.get("max_experience") else None
        job.education_level = request.form.get("education_level", "").strip()
        job.employment_type = request.form.get("employment_type", "full-time").strip()
        job.location = request.form.get("location", "").strip()
        job.salary_range = request.form.get("salary_range", "").strip()
        job.is_active = bool(request.form.get("is_active"))

        db.session.commit()

        # Re-screen candidates with updated requirements
        matching_engine.match_all_candidates_for_job(job.id, user_id=current_user.id)

        flash("Job description updated and candidates re-screened successfully.", "success")
        return redirect(url_for("jobs.detail", id=job.id))

    req_skills_str = ", ".join(job.required_skills or [])
    pref_skills_str = ", ".join(job.preferred_skills or [])

    return render_template(
        "jobs/edit.html",
        job=job,
        required_skills_str=req_skills_str,
        preferred_skills_str=pref_skills_str,
    )


@jobs_bp.route("/<int:id>/match", methods=["POST"])
@login_required
def run_matching(id):
    job = JobDescription.query.get_or_404(id)
    results = matching_engine.match_all_candidates_for_job(job.id, user_id=current_user.id)
    flash(f"Evaluated {len(results)} candidate(s) against '{job.title}'.", "success")
    return redirect(url_for("jobs.detail", id=job.id))


@jobs_bp.route("/<int:id>/toggle", methods=["POST"])
@login_required
def toggle(id):
    job = JobDescription.query.get_or_404(id)
    job.is_active = not job.is_active
    db.session.commit()
    status_label = "activated" if job.is_active else "deactivated"
    flash(f"Job '{job.title}' is now {status_label}.", "info")
    return redirect(url_for("jobs.list_jobs"))


@jobs_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    job = JobDescription.query.get_or_404(id)
    title = job.title
    db.session.delete(job)
    db.session.commit()
    flash(f"Job posting '{title}' deleted.", "info")
    return redirect(url_for("jobs.list_jobs"))
