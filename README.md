# AntiGravity AI | Intelligent Resume Screening & Candidate Parsing Engine

An enterprise-grade, explainable talent acquisition platform engineered with **Python**, **Flask**, **NLTK**, **Scikit-learn (TF-IDF & Cosine Similarity)**, **pdfplumber**, **SQLAlchemy (PostgreSQL / SQLite)**, **ReportLab**, and **Bootstrap 5 + Chart.js**.

---

## 🌟 Executive Summary & Mission

Recruitment screening at scale often suffers from opaque algorithms, biased filtering, or brittle keyword matching. AntiGravity AI provides recruiters with an **auditable, explainable decision-support platform** that:

1. Ingests raw multi-page PDF resumes securely.
2. Extracts candidate contact information, work timelines, educational credentials, and over 500+ normalized technical skills via rule-based parsing and NLTK linguistic processing.
3. Computes multi-dimensional similarity and relevance scores against configurable Job Descriptions using TF-IDF vectorization and cosine similarity.
4. Explains exact scoring drivers (matched skills, missing required skills, experience gaps) in plain English.
5. Generates high-fidelity PDF evaluation reports and CSV rankings for hiring committees.

> ⚖️ **Ethical AI Disclaimer**: Matching scores serve strictly as **decision-support signals** for human recruiters, not automated rejection verdicts. The system does not infer or evaluate protected characteristics such as age, gender, race, or religion.

---

## 🧠 Explainable AI/ML Matching Engine Architecture

The matching engine avoids "black-box" classifications and computes a transparent, normalized index from **0 to 100**:

$$\text{Overall Score} = 0.35 \times S_{\text{skills}} + 0.25 \times S_{\text{tfidf}} + 0.20 \times S_{\text{exp}} + 0.10 \times S_{\text{edu}} + 0.10 \times S_{\text{keywords}}$$

### Scoring Component Breakdown

1. **Skill Overlap Score ($S_{\text{skills}}$, 35% Weight)**:
   - Evaluates direct overlap between candidate extracted skills and job description required skills.
   - Missing required skills result in strict penalties; preferred skills contribute auxiliary positive weighting.
2. **TF-IDF & Cosine Similarity ($S_{\text{tfidf}}$, 25% Weight)**:
   - Generates document-frequency vectors over cleaned resume text and job descriptions.
   - Computes angular cosine similarity in $n$-dimensional vocabulary space to capture contextual semantic alignment beyond isolated keywords.
3. **Experience Calibration ($S_{\text{exp}}$, 20% Weight)**:
   - Compares total verified professional years against job minimum and maximum experience thresholds.
4. **Education Qualification ($S_{\text{edu}}$, 10% Weight)**:
   - Matches candidate degree level (Associate, Bachelor's, Master's, Doctorate) against role requirements.
5. **Domain Keyword Coverage ($S_{\text{keywords}}$, 10% Weight)**:
   - Analyzes frequency of core technical keywords (e.g. CI/CD, microservices, unit testing) distributed throughout the resume.

---

## 🚀 Core Platform Features

### 1. Recruiter Authentication & Analytics Dashboard
- Secure authentication via Flask-Login with password hashing using Werkzeug scrypt.
- High-level KPIs: Total Resumes Processed, Active Open Requisitions, Total Candidate Pool, Average Match Score.
- Real-time Chart.js visual analytics:
  - Candidate recruitment funnel status distribution (Doughnut chart).
  - Skill frequency distribution across current candidate pool (Bar chart).
  - Chronological recent screening activity stream.

### 2. PDF Resume Ingestion & OCR Detection
- Batch multi-file drag-and-drop PDF upload with client-side file size and MIME-type validation.
- Deep text extraction via `pdfplumber` across complex multi-column resumes.
- Automated detection of scanned image-only PDFs with informative warning prompts.
- Sanitized, isolated storage of original PDF files in secured server storage.

### 3. NLTK Information Extraction
- **Text Preprocessing**: Lowercasing, punctuation stripping, NLTK sentence and word tokenization (`punkt_tab`), stop-word elimination (`stopwords`), and WordNet lemmatization (`wordnet`).
- **Entity Extraction**:
  - Full Name identification using capitalized structural heuristics and POS tagging.
  - Email extraction using RFC-compliant regular expression patterns.
  - Phone extraction supporting international, US, and regional telephone formats.
  - Education extraction parsing degrees (B.Tech, B.S., M.S., Ph.D., MBA) and graduation years.
  - Work history extraction computing total verifiable professional experience.
  - Comprehensive 500+ skill vocabulary matching with synonym normalization (e.g., `JS` $\rightarrow$ `JavaScript`, `K8s` $\rightarrow$ `Kubernetes`, `TF` $\rightarrow$ `TensorFlow`).

### 4. Job Requisition Management
- Full requisition lifecycle: Create, edit, activate, or archive job postings.
- Dynamic interactive tagging UI for required versus preferred competencies.
- Minimum and maximum experience limits, educational criteria, and departmental classifications.

### 5. Candidate Ranking & Comparison
- Job-centric ranking view sorting candidate applicants by overall score.
- Side-by-side comparative matrix evaluating up to 4 candidates simultaneously across matching criteria.
- Recruiter notes and candidate status progression (`New` $\rightarrow$ `Screening` $\rightarrow$ `Shortlisted` $\rightarrow$ `Hired` / `Rejected`).

### 6. Automated PDF & CSV Reporting
- **Candidate Evaluation PDF**: Multi-page report containing personal contact metadata, explainable score decomposition, matched/missing skill lists, and compliance certifications.
- **Job Summary PDF**: Role-wide screening digest ready for executive presentation.
- **CSV Data Export**: Tabular data download formatted for downstream applicant tracking systems (ATS).

---

## 🗄️ Database Schema & Data Models

Engineered with SQLAlchemy ORM, compatible with both **PostgreSQL** and **SQLite**:

- **Users**: Recruiter and administrator credentials (`username`, `email`, `password_hash`, `role`).
- **Candidates**: Profile metadata (`first_name`, `last_name`, `email`, `phone`, `years_experience`, `status`).
- **Resumes**: Uploaded file metadata and raw extracted text (`filename`, `file_path`, `raw_text`, `parsed_data`).
- **JobDescriptions**: Requisition specifications (`title`, `department`, `required_skills`, `preferred_skills`, `min_experience`).
- **Skills**: Canonical normalized skill lexicon (`name`, `category`, `normalized_name`).
- **CandidateSkills**: Association table storing proficiency and extraction source.
- **MatchResults**: Cached explainable scores and decompositions (`overall_score`, `skill_score`, `tfidf_similarity`, `matched_skills`, `missing_required_skills`, `score_explanation`).
- **ScreeningHistory**: Chronological audit trail logging recruiter actions (`upload`, `parse`, `match`, `status_change`).
- **RecruiterNotes**: Private recruiter annotations and feedback.

---

## 🛠️ Installation & Execution Instructions

### Prerequisites
- **Python** 3.10+ (Tested with Python 3.14)
- **pip** package manager

### 1. Setup Environment
```bash
cd ai-resume-screening-tool
cp .env.example .env
```
Default `.env` configuration uses SQLite for plug-and-play local execution:
```env
SECRET_KEY=your-secure-production-secret-key-2026
DATABASE_URL=sqlite:///resume_screener.db
FLASK_ENV=development
FLASK_DEBUG=1
UPLOAD_FOLDER=uploads
PORT=5001
```
*(To use PostgreSQL, simply update `DATABASE_URL=postgresql://user:password@localhost:5432/resume_screener`)*

### 2. Install Dependencies
```bash
python -m pip install -r backend/requirements.txt
```

### 3. Initialize & Seed Database
```bash
# Initialize schema and tables
python database/init_db.py

# Seed initial admin, recruiter, job descriptions, skills, and sample candidates
python backend/seed.py
```

### 4. Run Application
```bash
python backend/run.py
```
Access the application dashboard at **http://127.0.0.1:5001**.

---

## 🔑 Pre-Seeded Recruiter Credentials

| Role | Username / Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin` / `admin@example.com` | `Admin@123` | Full administrative control |
| **Lead Recruiter** | `recruiter` / `recruiter@example.com` | `Recruiter@123` | Upload resumes, post jobs, run AI matching, export reports |

---

## 📊 Scientific Methodology & Scoring Transparency

- **Distinction Between Similarity and Accuracy**:
  Cosine similarity scores indicate textual and conceptual alignment between resume content and job requisitions. High similarity does not guarantee job performance; low similarity highlights potential skill coverage gaps.
- **Handling Incomplete Documents**:
  Resumes lacking phone numbers, education dates, or explicit summary sections are parsed gracefully using fallback default values without throwing fatal parsing exceptions.
