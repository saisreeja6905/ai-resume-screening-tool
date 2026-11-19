from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from backend.extensions import db
from backend.app.models.candidate import Candidate
from backend.app.models.job_description import JobDescription
from backend.app.models.match_result import MatchResult
from backend.app.models.recruiter_note import RecruiterNote
from backend.app.models.screening_history import ScreeningHistory
from backend.app.models.skill import Skill, CandidateSkill

candidates_bp = Blueprint("candidates", __name__)


@candidates_bp.route("/")
@login_required
def list_candidates():
    search_query = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()
    skill_filter = request.args.get("skill", "").strip()
    min_exp = request.args.get("min_exp", type=float)

    query = Candidate.query

    if search_query:
        query = query.filter(
            (Candidate.first_name.ilike(f"%{search_query}%"))
            | (Candidate.last_name.ilike(f"%{search_query}%"))
            | (Candidate.email.ilike(f"%{search_query}%"))
            | (Candidate.current_title.ilike(f"%{search_query}%"))
        )

    if status_filter:
        query = query.filter_by(status=status_filter)

    if min_exp is not None:
        query = query.filter(Candidate.years_experience >= min_exp)

    if skill_filter:
        query = query.join(Candidate.candidate_skills).join(CandidateSkill.skill).filter(
            Skill.name.ilike(f"%{skill_filter}%")
        )

    candidates = query.order_by(Candidate.created_at.desc()).all()

    return render_template(
        "candidates/list.html",
        candidates=candidates,
        search_query=search_query,
        status_filter=status_filter,
        skill_filter=skill_filter,
        min_exp=min_exp,
    )


@candidates_bp.route("/<int:id>")
@login_required
def detail(id):
    candidate = Candidate.query.get_or_404(id)

    # Active jobs for match dropdown / evaluation
    active_jobs = JobDescription.query.filter_by(is_active=True).all()

    # Match results for this candidate
    match_results = (
        MatchResult.query.filter_by(candidate_id=candidate.id)
        .join(JobDescription, MatchResult.job_id == JobDescription.id)
        .order_by(MatchResult.overall_score.desc())
        .all()
    )

    # Recruiter notes
    notes = (
        RecruiterNote.query.filter_by(candidate_id=candidate.id)
        .order_by(RecruiterNote.created_at.desc())
        .all()
    )

    # Screening history
    history = (
        ScreeningHistory.query.filter_by(candidate_id=candidate.id)
        .order_by(ScreeningHistory.created_at.desc())
        .limit(15)
        .all()
    )

    return render_template(
        "candidates/detail.html",
        candidate=candidate,
        match_results=match_results,
        notes=notes,
        history=history,
        active_jobs=active_jobs,
    )


@candidates_bp.route("/<int:id>/status", methods=["POST"])
@login_required
def update_status(id):
    candidate = Candidate.query.get_or_404(id)
    new_status = request.form.get("status") or (request.json.get("status") if request.is_json else None)

    valid_statuses = {"new", "screening", "shortlisted", "rejected", "hired"}
    if new_status and new_status in valid_statuses:
        old_status = candidate.status
        candidate.status = new_status
        db.session.commit()

        # Log history
        ScreeningHistory.log(
            action="status_change",
            details={"previous_status": old_status, "new_status": new_status},
            user_id=current_user.id,
            candidate_id=candidate.id,
        )
        db.session.commit()

        if request.is_json:
            return jsonify({"success": True, "new_status": new_status})

        flash(f"Candidate status updated to {new_status.capitalize()}.", "success")
    else:
        if request.is_json:
            return jsonify({"success": False, "error": "Invalid status value"}), 400
        flash("Invalid status selected.", "danger")

    return redirect(url_for("candidates.detail", id=id))


@candidates_bp.route("/<int:id>/notes", methods=["POST"])
@login_required
def add_note(id):
    candidate = Candidate.query.get_or_404(id)
    note_text = (
        request.form.get("note_text")
        or (request.json.get("note_text") if request.is_json else "")
    ).strip()
    job_id = request.form.get("job_id", type=int) or (request.json.get("job_id") if request.is_json else None)

    if not note_text:
        if request.is_json:
            return jsonify({"success": False, "error": "Note cannot be empty."}), 400
        flash("Note text cannot be empty.", "warning")
        return redirect(url_for("candidates.detail", id=id))

    note = RecruiterNote(
        user_id=current_user.id,
        candidate_id=candidate.id,
        job_id=job_id,
        note_text=note_text,
    )
    db.session.add(note)
    db.session.commit()

    ScreeningHistory.log(
        action="note_added",
        details={"note_snippet": note_text[:80]},
        user_id=current_user.id,
        candidate_id=candidate.id,
        job_id=job_id,
    )
    db.session.commit()

    if request.is_json:
        return jsonify({
            "success": True,
            "note": {
                "id": note.id,
                "author": current_user.full_name,
                "text": note.note_text,
                "created_at": note.created_at.strftime("%b %d, %Y %H:%M"),
            },
        })

    flash("Note added successfully.", "success")
    return redirect(url_for("candidates.detail", id=id))


@candidates_bp.route("/compare")
@login_required
def compare():
    ids_param = request.args.get("ids", "")
    id_list = []
    if ids_param:
        for x in ids_param.split(","):
            if x.strip().isdigit():
                id_list.append(int(x.strip()))

    candidates = Candidate.query.filter(Candidate.id.in_(id_list)).all() if id_list else []
    all_candidates = Candidate.query.order_by(Candidate.first_name).all()

    return render_template(
        "candidates/compare.html",
        candidates=candidates,
        all_candidates=all_candidates,
        selected_ids=id_list,
    )


@candidates_bp.route("/ranking/<int:job_id>")
@login_required
def ranking(job_id):
    job = JobDescription.query.get_or_404(job_id)
    matches = (
        MatchResult.query.filter_by(job_id=job.id)
        .join(Candidate, MatchResult.candidate_id == Candidate.id)
        .order_by(MatchResult.overall_score.desc())
        .all()
    )

    return render_template("candidates/ranking.html", job=job, matches=matches)
