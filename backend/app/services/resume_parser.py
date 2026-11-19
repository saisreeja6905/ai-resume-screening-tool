import re
import string
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

from backend.app.services.skill_extractor import skill_extractor

# Try importing NLTK components gracefully
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import WordNetLemmatizer

    _STOPWORDS = set(stopwords.words("english"))
    _LEMMATIZER = WordNetLemmatizer()
except Exception:
    # Fallback if NLTK data is not yet downloaded
    _STOPWORDS = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
        "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between",
        "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do",
        "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from",
        "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd",
        "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his",
        "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't",
        "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
        "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our",
        "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll",
        "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the",
        "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they",
        "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too",
        "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're",
        "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's",
        "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
        "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself",
        "yourselves"
    }
    _LEMMATIZER = None


class ResumeParser:
    """Production NLP Resume Parser extracting structured data from raw resume text."""

    SECTION_PATTERNS = {
        "summary": re.compile(
            r"^(?:professional\s+summary|summary|profile|about\s+me|career\s+objective|objective|executive\s+summary)",
            re.IGNORECASE,
        ),
        "experience": re.compile(
            r"^(?:work\s+experience|professional\s+experience|experience|employment\s+history|work\s+history|career\s+history)",
            re.IGNORECASE,
        ),
        "education": re.compile(
            r"^(?:education|academic\s+background|academic\s+qualifications|educational\s+qualifications|academics|qualifications)",
            re.IGNORECASE,
        ),
        "skills": re.compile(
            r"^(?:technical\s+skills|core\s+competencies|skills\s+and\s+competencies|skills\s+summary|key\s+skills|skills|technologies)",
            re.IGNORECASE,
        ),
        "projects": re.compile(
            r"^(?:projects|key\s+projects|personal\s+projects|technical\s+projects|academic\s+projects)",
            re.IGNORECASE,
        ),
        "certifications": re.compile(
            r"^(?:certifications|licenses\s+and\s+certifications|certificates|professional\s+certifications|courses\s+and\s+certifications)",
            re.IGNORECASE,
        ),
    }

    DEGREE_HIERARCHY = {
        "phd": 5, "ph.d": 5, "doctorate": 5, "doctor of philosophy": 5,
        "master": 4, "masters": 4, "ms": 4, "m.s": 4, "m.sc": 4, "msc": 4, "m.tech": 4, "mtech": 4,
        "mba": 4, "mca": 4, "meng": 4, "m.eng": 4, "post graduate": 4,
        "bachelor": 3, "bachelors": 3, "bs": 3, "b.s": 3, "b.sc": 3, "bsc": 3, "b.tech": 3, "btech": 3,
        "b.e": 3, "be": 3, "bca": 3, "bba": 3, "b.com": 3, "bcom": 3, "undergraduate": 3,
        "associate": 2, "diploma": 2,
        "high school": 1, "secondary": 1,
    }

    COMMON_TITLES = [
        "Software Engineer", "Senior Software Engineer", "Full Stack Developer", "Backend Developer",
        "Frontend Developer", "Data Scientist", "Machine Learning Engineer", "DevOps Engineer",
        "Cloud Architect", "Product Manager", "Project Manager", "Data Engineer", "QA Engineer",
        "System Administrator", "Solutions Architect", "Technical Lead", "Engineering Manager",
        "Data Analyst", "Business Analyst", "Security Engineer", "Mobile Developer", "iOS Developer",
        "Android Developer", "Lead Developer", "Consultant", "Research Scientist", "Intern"
    ]

    MONTHS_REGEX = (
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    )

    def __init__(self):
        self.skill_extractor = skill_extractor

    def clean_text_nlp(self, text: str) -> str:
        """Tokenize, remove punctuation and stopwords, lemmatize."""
        if not text:
            return ""

        # Remove email, urls, phone numbers
        clean = re.sub(r"https?://\S+|www\.\S+", " ", text)
        clean = re.sub(r"\b[\w.-]+?@[\w.-]+?\.\w+\b", " ", clean)
        clean = re.sub(r"[^a-zA-Z0-9\s]", " ", clean)

        words = clean.lower().split()
        filtered = [w for w in words if w not in _STOPWORDS and len(w) > 1]

        if _LEMMATIZER:
            try:
                filtered = [_LEMMATIZER.lemmatize(w) for w in filtered]
            except Exception:
                pass

        return " ".join(filtered)

    def extract_email(self, text: str) -> Optional[str]:
        """Extract primary email address."""
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
        matches = re.findall(email_pattern, text)
        if matches:
            # Return first valid email, lowercased
            return matches[0].lower().strip()
        return None

    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number in various formats."""
        patterns = [
            # International with plus (+1, +91, etc.)
            r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
            # Indian 10 digits starting with 6-9
            r"(?:\+91[-.\s]?)?[6-9]\d{9}",
            # Standard 10 digits
            r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b",
        ]
        for pat in patterns:
            match = re.search(pat, text)
            if match:
                phone = match.group(0).strip()
                # Ensure it's not a year or zip code
                digits = re.sub(r"\D", "", phone)
                if len(digits) >= 10:
                    return phone
        return None

    def extract_linkedin(self, text: str) -> Optional[str]:
        """Extract LinkedIn profile URL or handle."""
        match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/([A-Za-z0-9_-]+)", text, re.IGNORECASE)
        if match:
            return f"https://linkedin.com/in/{match.group(1)}"
        return None

    def extract_name(self, text: str, email: Optional[str] = None) -> Tuple[str, Optional[str]]:
        """
        Extract candidate first and last name from top of resume.
        Returns (first_name, last_name).
        """
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        header_lines = lines[:8]  # First 8 lines usually have contact details

        # Common non-name words
        stopwords_headers = {
            "resume", "curriculum", "vitae", "cv", "profile", "contact", "email",
            "phone", "address", "page", "portfolio", "github", "linkedin", "summary",
            "developer", "engineer", "designer", "manager", "lead", "architect"
        }

        # Try to find a line with 2 to 4 capitalized words
        for line in header_lines:
            # Skip if contains email, URL, or phone
            if "@" in line or "http" in line or "www" in line:
                continue
            if re.search(r"\d{3}", line):
                continue

            words = line.split()
            if 2 <= len(words) <= 4:
                # Check if words look like names (letters only, start with uppercase)
                clean_words = [re.sub(r"[^A-Za-z]", "", w) for w in words]
                if all(w.istitle() or w.isupper() for w in clean_words if w):
                    # Make sure not in stopwords
                    if not any(w.lower() in stopwords_headers for w in clean_words):
                        first = clean_words[0].capitalize()
                        last = " ".join(w.capitalize() for w in clean_words[1:])
                        return first, last

        # Fallback from email address (e.g. john.doe@example.com -> John Doe)
        if email:
            local_part = email.split("@")[0]
            clean_part = re.sub(r"[^A-Za-z.]", "", local_part)
            parts = clean_part.split(".")
            if len(parts) >= 2:
                first = parts[0].capitalize()
                last = " ".join(p.capitalize() for p in parts[1:])
                return first, last
            elif parts:
                return parts[0].capitalize(), None

        return "Candidate", None

    def split_into_sections(self, text: str) -> Dict[str, str]:
        """Detect and split resume text into logical sections."""
        lines = text.split("\n")
        sections: Dict[str, List[str]] = {
            "header": [],
            "summary": [],
            "experience": [],
            "education": [],
            "skills": [],
            "projects": [],
            "certifications": [],
            "other": [],
        }

        current_section = "header"

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # Check if line is a section header (usually short, standalone)
            if len(line_stripped) <= 45:
                matched_section = None
                clean_header = re.sub(r"[:\-_|]", "", line_stripped).strip()

                for sec_key, pattern in self.SECTION_PATTERNS.items():
                    if pattern.match(clean_header):
                        matched_section = sec_key
                        break

                if matched_section:
                    current_section = matched_section
                    continue

            sections[current_section].append(line_stripped)

        return {k: "\n".join(v).strip() for k, v in sections.items()}

    def extract_education(self, text: str, edu_section: str = "") -> Dict[str, Any]:
        """Extract education credentials, degrees, institution, and graduation years."""
        target_text = f"{edu_section}\n{text}" if edu_section else text

        degree_matches = []
        highest_level = "Not Specified"
        highest_rank = 0

        # Patterns for degrees
        degree_patterns = [
            (r"\b(?:Ph\.?D|Doctor\s+of\s+Philosophy|Doctorate)\b", "Ph.D.", 5),
            (r"\b(?:Master\s+of\s+Science|M\.?S\.?|M\.?Sc\.?)\b", "Master of Science (M.S.)", 4),
            (r"\b(?:Master\s+of\s+Technology|M\.?Tech\.?)\b", "Master of Technology (M.Tech)", 4),
            (r"\b(?:Master\s+of\s+Business\s+Administration|MBA)\b", "MBA", 4),
            (r"\b(?:Master\s+of\s+Computer\s+Applications|MCA)\b", "MCA", 4),
            (r"\b(?:Master\s+of\s+Engineering|M\.?E\.?|M\.?Eng\.?)\b", "Master of Engineering (M.E.)", 4),
            (r"\b(?:Bachelor\s+of\s+Technology|B\.?Tech\.?)\b", "Bachelor of Technology (B.Tech)", 3),
            (r"\b(?:Bachelor\s+of\s+Engineering|B\.?E\.?)\b", "Bachelor of Engineering (B.E.)", 3),
            (r"\b(?:Bachelor\s+of\s+Science|B\.?S\.?|B\.?Sc\.?)\b", "Bachelor of Science (B.S.)", 3),
            (r"\b(?:Bachelor\s+of\s+Computer\s+Applications|BCA)\b", "BCA", 3),
            (r"\b(?:Bachelor\s+of\s+Arts|B\.?A\.?)\b", "Bachelor of Arts (B.A.)", 3),
            (r"\b(?:Bachelor\s+of\s+Commerce|B\.?Com\.?)\b", "Bachelor of Commerce (B.Com)", 3),
            (r"\b(?:Associate\s+Degree|Diploma)\b", "Associate / Diploma", 2),
        ]

        for pattern, label, rank in degree_patterns:
            if re.search(pattern, target_text, re.IGNORECASE):
                degree_matches.append(label)
                if rank > highest_rank:
                    highest_rank = rank
                    highest_level = label

        # Extract institutions
        institutions = []
        inst_pattern = r"(?:(?:at|from)\s+)?([A-Z][A-Za-z\s&]+(?:University|Institute|College|Academy|Polytechnic|School\s+of\s+[A-Za-z]+))"
        for match in re.findall(inst_pattern, target_text):
            cleaned = match.strip()
            if len(cleaned) > 5 and len(cleaned) < 80 and cleaned not in institutions:
                institutions.append(cleaned)

        # Extract graduation years
        years = re.findall(r"\b(19\d{2}|20[0-2]\d)\b", edu_section or text)
        valid_years = [int(y) for y in years if 1980 <= int(y) <= datetime.now().year + 5]
        latest_year = max(valid_years) if valid_years else None

        return {
            "highest_level": highest_level,
            "degrees": list(set(degree_matches)),
            "institutions": institutions[:3],
            "graduation_year": latest_year,
        }

    def extract_experience(self, text: str, exp_section: str = "") -> Dict[str, Any]:
        """
        Extract work experience details, company/title mentions, and calculate total years.
        """
        target_text = f"{exp_section}\n{text}" if exp_section else text
        current_year = datetime.now().year

        # 1. Look for explicit mentions like "7+ years of experience", "5 years experience"
        explicit_years = []
        explicit_patterns = [
            r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+experience",
            r"experience\s*(?:of)?\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
            r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s+in\s+software",
        ]
        for pattern in explicit_patterns:
            for match in re.findall(pattern, target_text, re.IGNORECASE):
                try:
                    val = float(match)
                    if 0.5 <= val <= 40:
                        explicit_years.append(val)
                except ValueError:
                    pass

        # 2. Extract date ranges (e.g., "Jan 2018 - Mar 2022", "2019 - Present", "06/2017 to 08/2021")
        date_range_pattern = (
            rf"(?:{self.MONTHS_REGEX}\s+)?(\b(?:19|20)\d{{2}}\b)\s*(?:-|–|—|to)\s*"
            rf"(?:(?:{self.MONTHS_REGEX}\s+)?(\b(?:19|20)\d{{2}}\b)|Present|Current|Now)"
        )

        total_calculated_months = 0
        spans = []

        for match in re.finditer(date_range_pattern, target_text, re.IGNORECASE):
            start_yr = int(match.group(1))
            end_match = match.group(2)
            if end_match:
                end_yr = int(end_match)
            else:
                end_yr = current_year

            if 1985 <= start_yr <= current_year and end_yr >= start_yr:
                span_years = min(end_yr - start_yr, 25)
                # Assume average 1 year if start and end are same year
                span_months = max(span_years * 12, 6)
                total_calculated_months += span_months
                spans.append((start_yr, end_yr))

        # Determine total years of experience
        if spans:
            # Overlapping spans simplified estimation
            min_year = min(s[0] for s in spans)
            max_year = max(s[1] for s in spans)
            span_total = max_year - min_year
            calculated_years = round(span_total, 1)
        else:
            calculated_years = round(total_calculated_months / 12.0, 1)

        # Reconcile explicit mentions vs calculated years
        if explicit_years:
            final_years = max(explicit_years)
        elif calculated_years > 0:
            final_years = calculated_years
        else:
            final_years = 0.0

        # Extract probable current title
        current_title = None
        for title in self.COMMON_TITLES:
            if re.search(rf"\b{re.escape(title)}\b", target_text, re.IGNORECASE):
                current_title = title
                break

        return {
            "total_years": float(final_years),
            "current_title": current_title,
            "has_experience_section": bool(exp_section),
        }

    def extract_certifications(self, text: str, cert_section: str = "") -> List[str]:
        """Extract professional certifications from resume."""
        target_text = f"{cert_section}\n{text}" if cert_section else text
        certs = []

        cert_keywords = [
            "AWS Certified Solutions Architect", "AWS Certified Developer", "AWS Certified SysOps",
            "AWS Certified Cloud Practitioner", "AWS Certified",
            "Microsoft Certified: Azure Fundamentals", "Microsoft Certified: Azure Solutions Architect",
            "Azure Certified", "Google Cloud Certified Professional", "GCP Certified",
            "Certified Kubernetes Administrator (CKA)", "Certified Kubernetes Application Developer (CKAD)",
            "PMP", "Project Management Professional", "Certified ScrumMaster (CSM)", "CSM",
            "Certified Ethical Hacker (CEH)", "CISSP", "CompTIA Security+", "CompTIA Network+",
            "Oracle Certified Professional", "HashiCorp Certified: Terraform Associate",
            "TensorFlow Developer Certificate", "Databricks Certified"
        ]

        for cert in cert_keywords:
            if re.search(rf"\b{re.escape(cert)}\b", target_text, re.IGNORECASE):
                if cert not in certs:
                    certs.append(cert)

        # Also extract lines from cert_section that look like credentials
        if cert_section:
            for line in cert_section.split("\n"):
                line = line.strip(" •*-·")
                if 5 < len(line) < 100:
                    if any(w in line.lower() for w in ["certified", "certification", "credential", "license"]):
                        if line not in certs:
                            certs.append(line)

        return certs[:10]

    def extract_projects(self, proj_section: str) -> List[Dict[str, str]]:
        """Extract projects from the projects section."""
        if not proj_section:
            return []

        projects = []
        chunks = re.split(r"\n(?=[A-Z0-9][A-Za-z0-9\s\-_]{3,40}(?::|\n))", proj_section)

        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk:
                continue
            lines = chunk.split("\n")
            title = lines[0].strip(" :•*-·")
            desc = " ".join([l.strip(" •*-·") for l in lines[1:] if l.strip()])
            if len(title) > 3:
                projects.append({
                    "title": title[:100],
                    "description": desc[:500] if desc else "Project details listed in resume.",
                })

        return projects[:6]

    def parse(self, raw_text: str) -> Dict[str, Any]:
        """
        Main entry point for parsing full resume text.
        Returns a rich structured dictionary.
        """
        if not raw_text or not raw_text.strip():
            return {
                "success": False,
                "error": "Empty text provided for parsing.",
                "candidate": {},
                "skills": [],
                "education": {},
                "experience": {},
                "certifications": [],
                "projects": [],
                "summary": "",
            }

        # 1. Section Segmentation
        sections = self.split_into_sections(raw_text)

        # 2. Extract Contact Info
        email = self.extract_email(raw_text)
        phone = self.extract_phone(raw_text)
        linkedin = self.extract_linkedin(raw_text)
        first_name, last_name = self.extract_name(raw_text, email)

        # 3. Extract Summary / Objective
        summary = sections.get("summary", "")
        if not summary:
            # First paragraph after header if under 500 chars
            header_lines = sections.get("header", "").split("\n")
            if len(header_lines) > 2:
                candidate_summary = " ".join(header_lines[2:5])
                if len(candidate_summary) > 40:
                    summary = candidate_summary

        # 4. Extract Skills (across entire text and skills section)
        skills_text = f"{sections.get('skills', '')}\n{raw_text}"
        extracted_skills = self.skill_extractor.extract_skills(skills_text)

        # 5. Extract Education
        education_data = self.extract_education(raw_text, sections.get("education", ""))

        # 6. Extract Experience
        experience_data = self.extract_experience(raw_text, sections.get("experience", ""))

        # 7. Extract Certifications
        certifications = self.extract_certifications(raw_text, sections.get("certifications", ""))

        # 8. Extract Projects
        projects = self.extract_projects(sections.get("projects", ""))

        # Assemble full result
        candidate_dict = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "linkedin_url": linkedin,
            "summary": summary[:1000] if summary else None,
            "years_experience": experience_data.get("total_years", 0.0),
            "highest_education": education_data.get("highest_level"),
            "current_title": experience_data.get("current_title"),
            "current_company": None,
        }

        return {
            "success": True,
            "candidate": candidate_dict,
            "skills": extracted_skills,
            "education": education_data,
            "experience": experience_data,
            "certifications": certifications,
            "projects": projects,
            "summary": summary,
            "sections_found": [k for k, v in sections.items() if v],
        }


# Singleton instance
resume_parser = ResumeParser()
