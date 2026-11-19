import os
import sys

# Ensure root directory is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app import create_app
from backend.extensions import db
from backend.app.models.user import User
from backend.app.models.job_description import JobDescription
from backend.app.models.skill import Skill
from backend.app.models.candidate import Candidate
from backend.app.models.candidate import CandidateSkill
from backend.app.models.match_result import MatchResult
from backend.app.models.screening_history import ScreeningHistory

def seed_database():
    app = create_app()
    with app.app_context():
        print("[Seed] Initializing database schema...")
        db.create_all()

        # 1. Create Users
        print("[Seed] Seeding administrative & recruiter users...")
        if not User.query.filter_by(email="admin@example.com").first():
            admin = User(
                username="admin",
                email="admin@example.com",
                first_name="Alexander",
                last_name="Vance",
                role="admin",
            )
            admin.set_password("Admin@123")
            db.session.add(admin)

        if not User.query.filter_by(email="recruiter@example.com").first():
            recruiter = User(
                username="recruiter",
                email="recruiter@example.com",
                first_name="Sarah",
                last_name="Connor",
                role="recruiter",
            )
            recruiter.set_password("Recruiter@123")
            db.session.add(recruiter)

        db.session.commit()
        recruiter_user = User.query.filter_by(email="recruiter@example.com").first()

        # 2. Seed Standard Skill Vocabulary
        skills_data = [
            ("Python", "language"), ("JavaScript", "language"), ("TypeScript", "language"),
            ("Java", "language"), ("C++", "language"), ("Go", "language"), ("SQL", "language"),
            ("React", "framework"), ("Node.js", "framework"), ("Express", "framework"),
            ("Flask", "framework"), ("Django", "framework"), ("FastAPI", "framework"),
            ("Next.js", "framework"), ("PostgreSQL", "database"), ("MongoDB", "database"),
            ("Redis", "database"), ("MySQL", "database"), ("Docker", "tool"),
            ("Kubernetes", "tool"), ("AWS", "cloud"), ("GCP", "cloud"), ("Azure", "cloud"),
            ("Git", "tool"), ("CI/CD", "tool"), ("Machine Learning", "technical"),
            ("Scikit-learn", "tool"), ("TensorFlow", "tool"), ("PyTorch", "tool"),
            ("Pandas", "tool"), ("NumPy", "tool"), ("NLTK", "tool"), ("NLP", "technical"),
            ("REST APIs", "technical"), ("GraphQL", "technical"), ("Tailwind CSS", "framework"),
            ("HTML5", "language"), ("CSS3", "language"), ("Statistics", "technical"),
        ]

        print(f"[Seed] Seeding {len(skills_data)} standard industry skills...")
        skill_objects = {}
        for name, category in skills_data:
            s = Skill.get_or_create(name=name, category=category)
            skill_objects[name] = s
        db.session.commit()

        # 3. Create Realistic Job Descriptions
        print("[Seed] Seeding job descriptions...")
        jobs_data = [
            {
                "title": "Senior Python & Backend Engineer",
                "department": "Platform Engineering",
                "description": "Architect scalable cloud microservices, develop clean REST APIs, optimize PostgreSQL database queries, and establish automated CI/CD pipelines.",
                "required_skills": ["Python", "Flask", "PostgreSQL", "REST APIs", "Docker"],
                "preferred_skills": ["AWS", "Redis", "CI/CD", "Kubernetes"],
                "min_experience": 4,
                "max_experience": 8,
                "education_level": "Bachelor's Degree",
                "employment_type": "Full-time",
                "location": "San Francisco, CA (Remote)",
                "salary_range": "$140,000 - $175,000",
            },
            {
                "title": "Frontend React UI/UX Specialist",
                "department": "Product Engineering",
                "description": "Deliver responsive modern web applications using React, TypeScript, and state management architectures. Collaborate with design teams to craft accessible interfaces.",
                "required_skills": ["React", "JavaScript", "HTML5", "CSS3"],
                "preferred_skills": ["TypeScript", "Next.js", "Tailwind CSS", "Git"],
                "min_experience": 3,
                "max_experience": 6,
                "education_level": "Bachelor's Degree",
                "employment_type": "Full-time",
                "location": "New York, NY (Hybrid)",
                "salary_range": "$125,000 - $155,000",
            },
            {
                "title": "Lead Data Scientist / NLP Engineer",
                "department": "Artificial Intelligence",
                "description": "Develop state-of-the-art NLP pipelines, train machine learning predictive models, implement explainable information extraction systems, and analyze massive text datasets.",
                "required_skills": ["Python", "Machine Learning", "Scikit-learn", "NLP", "SQL"],
                "preferred_skills": ["PyTorch", "TensorFlow", "NLTK", "Pandas", "Docker"],
                "min_experience": 4,
                "max_experience": 9,
                "education_level": "Master's Degree",
                "employment_type": "Full-time",
                "location": "Seattle, WA (Remote)",
                "salary_range": "$160,000 - $195,000",
            },
        ]

        created_jobs = []
        for jd_info in jobs_data:
            existing = JobDescription.query.filter_by(title=jd_info["title"]).first()
            if not existing:
                job = JobDescription(
                    created_by=recruiter_user.id if recruiter_user else 1,
                    **jd_info
                )
                db.session.add(job)
                created_jobs.append(job)
            else:
                created_jobs.append(existing)

        db.session.commit()

        # 4. Seed Realistic Candidates and Match Results
        print("[Seed] Seeding sample candidate evaluations for analytics dashboard...")
        candidates_data = [
            {
                "first_name": "Eleanor",
                "last_name": "Rigby",
                "email": "eleanor.rigby@devmail.org",
                "phone": "+1-555-019-2834",
                "location": "San Francisco, CA",
                "current_title": "Senior Backend Architect",
                "current_company": "CloudScale Systems",
                "years_experience": 6,
                "highest_education": "B.S. in Computer Science",
                "status": "shortlisted",
                "skills": ["Python", "Flask", "PostgreSQL", "REST APIs", "Docker", "AWS", "Redis", "Git"],
                "matches": [
                    {
                        "job_index": 0,
                        "overall_score": 92.5,
                        "skill_score": 95.0,
                        "tfidf_similarity": 0.88,
                        "experience_score": 95.0,
                        "education_score": 90.0,
                        "keyword_score": 85.0,
                        "matched_skills": ["Python", "Flask", "PostgreSQL", "REST APIs", "Docker", "AWS", "Redis"],
                        "missing_required": [],
                        "missing_preferred": ["Kubernetes", "CI/CD"],
                    }
                ]
            },
            {
                "first_name": "Marcus",
                "last_name": "Chen",
                "email": "marcus.chen@reactdev.io",
                "phone": "+1-555-024-8831",
                "location": "Austin, TX",
                "current_title": "Senior Frontend Engineer",
                "current_company": "Apex UI Labs",
                "years_experience": 4,
                "highest_education": "B.S. in Software Engineering",
                "status": "screening",
                "skills": ["React", "JavaScript", "TypeScript", "HTML5", "CSS3", "Next.js", "Git"],
                "matches": [
                    {
                        "job_index": 1,
                        "overall_score": 89.0,
                        "skill_score": 92.0,
                        "tfidf_similarity": 0.82,
                        "experience_score": 90.0,
                        "education_score": 90.0,
                        "keyword_score": 88.0,
                        "matched_skills": ["React", "JavaScript", "HTML5", "CSS3", "TypeScript", "Next.js", "Git"],
                        "missing_required": [],
                        "missing_preferred": ["Tailwind CSS"],
                    }
                ]
            },
            {
                "first_name": "Aria",
                "last_name": "Patel",
                "email": "aria.patel@datascience.ai",
                "phone": "+1-555-038-7712",
                "location": "Boston, MA",
                "current_title": "AI / NLP Research Engineer",
                "current_company": "Cognitive Insights",
                "years_experience": 5,
                "highest_education": "M.S. in Data Analytics",
                "status": "new",
                "skills": ["Python", "Machine Learning", "Scikit-learn", "NLP", "SQL", "Pandas", "NLTK", "PyTorch"],
                "matches": [
                    {
                        "job_index": 2,
                        "overall_score": 94.0,
                        "skill_score": 96.0,
                        "tfidf_similarity": 0.91,
                        "experience_score": 95.0,
                        "education_score": 100.0,
                        "keyword_score": 90.0,
                        "matched_skills": ["Python", "Machine Learning", "Scikit-learn", "NLP", "SQL", "Pandas", "NLTK", "PyTorch"],
                        "missing_required": [],
                        "missing_preferred": ["TensorFlow", "Docker"],
                    }
                ]
            },
            {
                "first_name": "David",
                "last_name": "Miller",
                "email": "david.miller@generalist.dev",
                "phone": "+1-555-049-3321",
                "location": "Denver, CO",
                "current_title": "Junior Web Developer",
                "current_company": "TechStart Agency",
                "years_experience": 1,
                "highest_education": "Associate Degree",
                "status": "new",
                "skills": ["JavaScript", "HTML5", "CSS3", "Git"],
                "matches": [
                    {
                        "job_index": 1,
                        "overall_score": 52.0,
                        "skill_score": 60.0,
                        "tfidf_similarity": 0.45,
                        "experience_score": 40.0,
                        "education_score": 60.0,
                        "keyword_score": 50.0,
                        "matched_skills": ["JavaScript", "HTML5", "CSS3", "Git"],
                        "missing_required": ["React"],
                        "missing_preferred": ["TypeScript", "Next.js", "Tailwind CSS"],
                    }
                ]
            }
        ]

        for c_data in candidates_data:
            existing_c = Candidate.query.filter_by(email=c_data["email"]).first()
            if not existing_c:
                candidate = Candidate(
                    first_name=c_data["first_name"],
                    last_name=c_data["last_name"],
                    email=c_data["email"],
                    phone=c_data["phone"],
                    location=c_data["location"],
                    current_title=c_data["current_title"],
                    current_company=c_data["current_company"],
                    years_experience=c_data["years_experience"],
                    highest_education=c_data["highest_education"],
                    status=c_data["status"],
                )
                db.session.add(candidate)
                db.session.flush()

                # Add Candidate Skills
                for sk_name in c_data["skills"]:
                    sk_obj = skill_objects.get(sk_name)
                    if sk_obj:
                        cs = CandidateSkill(
                            candidate_id=candidate.id,
                            skill_id=sk_obj.id,
                            proficiency_level="advanced" if candidate.years_experience > 3 else "intermediate",
                            source="resume",
                        )
                        db.session.add(cs)

                # Add Match Results
                for m_data in c_data["matches"]:
                    job_obj = created_jobs[m_data["job_index"]]
                    match = MatchResult(
                        candidate_id=candidate.id,
                        job_id=job_obj.id,
                        overall_score=m_data["overall_score"],
                        skill_score=m_data["skill_score"],
                        tfidf_similarity=m_data["tfidf_similarity"],
                        experience_score=m_data["experience_score"],
                        education_score=m_data["education_score"],
                        keyword_score=m_data["keyword_score"],
                        matched_skills=m_data["matched_skills"],
                        missing_required_skills=m_data["missing_required"],
                        missing_preferred_skills=m_data["missing_preferred"],
                        additional_skills=[s for s in c_data["skills"] if s not in m_data["matched_skills"]],
                        score_explanation={
                            "summary": f"Calculated candidate score of {m_data['overall_score']}% based on {len(m_data['matched_skills'])} matched competencies and {c_data['years_experience']} verified years of experience.",
                            "skill_ratio": f"{len(m_data['matched_skills'])}/{len(job_obj.required_skills or [])}",
                        }
                    )
                    db.session.add(match)

                # Log Screening history
                ScreeningHistory.log(
                    action="match",
                    details={"action": "Automated pipeline seed evaluation completed"},
                    user_id=recruiter_user.id if recruiter_user else 1,
                    candidate_id=candidate.id,
                    job_id=created_jobs[0].id,
                )

        db.session.commit()
        print("[Seed] Successfully completed database seeding with realistic accounts, jobs, skills, and candidates.")

if __name__ == "__main__":
    seed_database()
