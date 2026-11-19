from flask import Blueprint, render_template, request, send_file, Response, redirect, url_for, flash
from flask_login import login_required, current_user

from backend.app.models.candidate import Candidate
from backend.app.models.job_description import JobDescription
from backend.app.models.match_result import MatchResult
from backend.app.models.screening_history import ScreeningHistory
from backend.app.services.report_generator import report_generator
from backend.extensions import db

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/candidate/<int:id>")
@login_required
def candidate_report(id):
    candidate = Candidate.query.get_or_404(id)
    job_id = request.args.get("job_id", type=int)

    match = None
    if job_id:
        match = MatchResult.query.filter_by(candidate_id=candidate.id, job_id=job_id).first()
    elif candidate.match_results.count() > 0:
        match = candidate.match_results.order_by(MatchResult.overall_score.desc()).first()

    return render_template(
        "reports/candidate_report.html",
        candidate=candidate,
        match=match,
    )


@reports_bp.route("/candidate/<int:id>/pdf")
@login_required
def candidate_pdf(id):
    candidate = Candidate.query.get_or_404(id)
    job_id = request.args.get("job_id", type=int)

    match = None
    if job_id:
        match = MatchResult.query.filter_by(candidate_id=candidate.id, job_id=job_id).first()
    elif candidate.match_results.count() > 0:
        match = candidate.match_results.order_by(MatchResult.overall_score.desc()).first()

    pdf_buffer = report_generator.generate_candidate_pdf(candidate, match)

    # Log report generation in screening history
    ScreeningHistory.log(
        action="report_generated",
        details={"type": "candidate_pdf", "candidate_name": candidate.full_name},
        user_id=current_user.id,
        candidate_id=candidate.id,
        job_id=job_id,
    )
    db.session.commit()

    safe_name = f"{candidate.first_name}_{candidate.last_name or ''}".strip().replace(" ", "_")
    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"Report_{safe_name}.pdf",
    )


@reports_bp.route("/job/<int:id>")
@login_required
def job_summary(id):
    job = JobDescription.query.get_or_404(id)
    matches = (
        MatchResult.query.filter_by(job_id=job.id)
        .order_by(MatchResult.overall_score.desc())
        .all()
    )

    return render_template(
        "reports/job_summary.html",
        job=job,
        matches=matches,
    )


@reports_bp.route("/job/<int:id>/pdf")
@login_required
def job_pdf(id):
    job = JobDescription.query.get_or_404(id)
    matches = (
        MatchResult.query.filter_by(job_id=job.id)
        .order_by(MatchResult.overall_score.desc())
        .all()
    )

    pdf_buffer = report_generator.generate_job_summary_pdf(job, matches)

    ScreeningHistory.log(
        action="report_generated",
        details={"type": "job_summary_pdf", "job_title": job.title},
        user_id=current_user.id,
        job_id=job.id,
    )
    db.session.commit()

    safe_title = job.title.strip().replace(" ", "_")
    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"Screening_Summary_{safe_title}.pdf",
    )


@reports_bp.route("/job/<int:id>/csv")
@login_required
def job_csv(id):
    job = JobDescription.query.get_or_404(id)
    matches = (
        MatchResult.query.filter_by(job_id=job.id)
        .order_by(MatchResult.overall_score.desc())
        .all()
    )

    csv_content = report_generator.generate_candidate_ranking_csv(job, matches)

    ScreeningHistory.log(
        action="report_generated",
        details={"type": "job_ranking_csv", "job_title": job.title},
        user_id=current_user.id,
        job_id=job.id,
    )
    db.session.commit()

    safe_title = job.title.strip().replace(" ", "_")
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=Ranking_{safe_title}.csv"},
    )
