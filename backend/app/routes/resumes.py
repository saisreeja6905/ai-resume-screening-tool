import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from backend.extensions import db
from backend.app.models.candidate import Candidate
from backend.app.models.resume import Resume
from backend.app.models.skill import Skill, CandidateSkill
from backend.app.models.job_description import JobDescription
from backend.app.models.screening_history import ScreeningHistory
from backend.app.services.pdf_parser import PDFParser
from backend.app.services.resume_parser import resume_parser
from backend.app.services.matching_engine import matching_engine

resumes_bp = Blueprint("resumes", __name__)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


@resumes_bp.route("/")
@login_required
def list_resumes():
    search_query = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()
    page = request.args.get("page", 1, type=int)

    query = Resume.query.join(Candidate, Resume.candidate_id == Candidate.id, isouter=True)

    if search_query:
        query = query.filter(
            (Resume.original_filename.ilike(f"%{search_query}%"))
            | (Candidate.first_name.ilike(f"%{search_query}%"))
            | (Candidate.last_name.ilike(f"%{search_query}%"))
            | (Candidate.email.ilike(f"%{search_query}%"))
        )

    if status_filter:
        query = query.filter(Resume.processing_status == status_filter)

    pagination = query.order_by(Resume.upload_date.desc()).paginate(
        page=page, per_page=current_app.config.get("ITEMS_PER_PAGE", 15), error_out=False
    )

    return render_template(
        "resumes/list.html",
        resumes=pagination.items,
        pagination=pagination,
        search_query=search_query,
        status_filter=status_filter,
    )


@resumes_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        files = request.files.getlist("resumes")
        if not files or files[0].filename == "":
            flash("No resume files selected for upload.", "warning")
            return redirect(request.url)

        success_count = 0
        error_count = 0
        results_summary = []

        upload_dir = current_app.config["UPLOAD_FOLDER"]
        active_jobs = JobDescription.query.filter_by(is_active=True).all()

        for file in files:
            orig_filename = secure_filename(file.filename)
            if not orig_filename or not allowed_file(orig_filename):
                error_count += 1
                results_summary.append({"file": file.filename, "status": "Failed", "error": "Only PDF files are permitted."})
                continue

            unique_filename = f"{uuid.uuid4().hex[:12]}_{orig_filename}"
            file_path = os.path.join(upload_dir, unique_filename)

            try:
                file.save(file_path)
                file_size = os.path.getsize(file_path)

                # Step 1: Extract PDF text
                extraction = PDFParser.extract_text(file_path)
                raw_text = extraction.get("full_text", "")

                if not extraction["success"] or not raw_text.strip():
                    error_msg = extraction.get("error", "No text layer could be found in this PDF.")
                    resume_rec = Resume(
                        filename=unique_filename,
                        original_filename=orig_filename,
                        file_path=file_path,
                        file_size=file_size,
                        raw_text="",
                        parsed_data={},
                        processing_status="failed",
                        error_message=error_msg,
                        uploaded_by=current_user.id,
                    )
                    db.session.add(resume_rec)
                    db.session.commit()
                    error_count += 1
                    results_summary.append({"file": orig_filename, "status": "Failed", "error": error_msg})
                    continue

                # Step 2: NLP Parse
                parsed = resume_parser.parse(raw_text)
                cand_info = parsed.get("candidate", {})

                # Check if candidate exists by email or name
                email = cand_info.get("email")
                candidate = None
                if email:
                    candidate = Candidate.query.filter_by(email=email).first()

                if not candidate:
                    candidate = Candidate(
                        first_name=cand_info.get("first_name") or "Candidate",
                        last_name=cand_info.get("last_name"),
                        email=email,
                        phone=cand_info.get("phone"),
                        linkedin_url=cand_info.get("linkedin_url"),
                        summary=cand_info.get("summary"),
                        years_experience=float(cand_info.get("years_experience") or 0.0),
                        highest_education=cand_info.get("highest_education"),
                        current_title=cand_info.get("current_title"),
                        status="screening",
                    )
                    db.session.add(candidate)
                    db.session.flush()
                else:
                    # Update fields if previously empty
                    if not candidate.phone and cand_info.get("phone"):
                        candidate.phone = cand_info.get("phone")
                    if not candidate.highest_education and cand_info.get("highest_education"):
                        candidate.highest_education = cand_info.get("highest_education")
                    if candidate.years_experience == 0.0 and cand_info.get("years_experience"):
                        candidate.years_experience = float(cand_info.get("years_experience"))

                # Step 3: Create Resume Record
                resume_rec = Resume(
                    candidate_id=candidate.id,
                    filename=unique_filename,
                    original_filename=orig_filename,
                    file_path=file_path,
                    file_size=file_size,
                    raw_text=raw_text,
                    parsed_data=parsed,
                    processing_status="completed",
                    uploaded_by=current_user.id,
                )
                db.session.add(resume_rec)
                db.session.flush()

                # Step 4: Associate Skills
                extracted_skills = parsed.get("skills", [])
                for sk in extracted_skills:
                    s_name = sk.get("name")
                    s_cat = sk.get("category", "Technical")
                    if s_name:
                        skill_obj = Skill.get_or_create(s_name, s_cat)
                        # Check CandidateSkill link
                        existing_cs = CandidateSkill.query.filter_by(
                            candidate_id=candidate.id, skill_id=skill_obj.id
                        ).first()
                        if not existing_cs:
                            cs = CandidateSkill(
                                candidate_id=candidate.id,
                                skill_id=skill_obj.id,
                                source="resume",
                            )
                            db.session.add(cs)

                db.session.commit()

                # Step 5: Screen against all active job descriptions
                for job in active_jobs:
                    try:
                        matching_engine.match_candidate_to_job(
                            candidate=candidate,
                            job=job,
                            resume=resume_rec,
                            save_db=True,
                            user_id=current_user.id,
                        )
                    except Exception as me_err:
                        current_app.logger.error("Auto-matching failed for job %s: %s", job.id, str(me_err))

                # Step 6: Log Screening History
                ScreeningHistory.log(
                    action="upload",
                    details={
                        "filename": orig_filename,
                        "candidate_name": candidate.full_name,
                        "extracted_skills_count": len(extracted_skills),
                    },
                    user_id=current_user.id,
                    candidate_id=candidate.id,
                )
                db.session.commit()

                success_count += 1
                results_summary.append({
                    "file": orig_filename,
                    "status": "Success",
                    "candidate_id": candidate.id,
                    "candidate_name": candidate.full_name,
                    "skills_count": len(extracted_skills),
                })

            except Exception as e:
                db.session.rollback()
                current_app.logger.exception("Error processing resume upload: %s", str(e))
                error_count += 1
                results_summary.append({"file": orig_filename, "status": "Failed", "error": str(e)})

        if success_count > 0:
            flash(f"Successfully processed {success_count} resume(s).", "success")
        if error_count > 0:
            flash(f"{error_count} file(s) failed during parsing.", "warning")

        return render_template("resumes/upload.html", results_summary=results_summary)

    return render_template("resumes/upload.html", results_summary=None)


@resumes_bp.route("/<int:id>")
@login_required
def detail(id):
    resume = Resume.query.get_or_404(id)
    candidate = resume.candidate
    return render_template("resumes/detail.html", resume=resume, candidate=candidate)


@resumes_bp.route("/<int:id>/reparse", methods=["POST"])
@login_required
def reparse(id):
    resume = Resume.query.get_or_404(id)

    if not resume.raw_text:
        extraction = PDFParser.extract_text(resume.file_path)
        if extraction["success"]:
            resume.raw_text = extraction["full_text"]
        else:
            flash(f"Could not extract text: {extraction.get('error')}", "danger")
            return redirect(url_for("resumes.detail", id=id))

    parsed = resume_parser.parse(resume.raw_text)
    resume.parsed_data = parsed
    resume.processing_status = "completed"
    resume.error_message = None

    # Update candidate if exists
    if resume.candidate:
        cand = resume.candidate
        cand_info = parsed.get("candidate", {})
        if cand_info.get("years_experience"):
            cand.years_experience = float(cand_info.get("years_experience"))
        if cand_info.get("highest_education"):
            cand.highest_education = cand_info.get("highest_education")
        if cand_info.get("current_title"):
            cand.current_title = cand_info.get("current_title")

        # Update skills
        for sk in parsed.get("skills", []):
            skill_obj = Skill.get_or_create(sk["name"], sk.get("category", "Technical"))
            if not CandidateSkill.query.filter_by(candidate_id=cand.id, skill_id=skill_obj.id).first():
                db.session.add(CandidateSkill(candidate_id=cand.id, skill_id=skill_obj.id, source="resume"))

        # Re-run matches
        for job in JobDescription.query.filter_by(is_active=True).all():
            matching_engine.match_candidate_to_job(candidate=cand, job=job, resume=resume, save_db=True, user_id=current_user.id)

    db.session.commit()
    flash("Resume re-parsed and candidate scores updated successfully.", "success")
    return redirect(url_for("resumes.detail", id=id))


@resumes_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    resume = Resume.query.get_or_404(id)
    cand_id = resume.candidate_id

    # Try removing physical file
    try:
        if os.path.exists(resume.file_path):
            os.remove(resume.file_path)
    except Exception as e:
        current_app.logger.warning("Could not delete resume file %s: %s", resume.file_path, str(e))

    db.session.delete(resume)
    db.session.commit()

    flash("Resume removed successfully.", "info")
    if cand_id:
        return redirect(url_for("candidates.detail", id=cand_id))
    return redirect(url_for("resumes.list_resumes"))
