from typing import Dict, List, Set, Any, Optional
import re
from ml.similarity import calculate_overlap_ratio


class FeatureExtractor:
    """Extracts comparative features between a Candidate's profile/resume and a Job Description."""

    EDUCATION_LEVELS = {
        "phd": 5, "ph.d": 5, "doctorate": 5,
        "master": 4, "masters": 4, "ms": 4, "msc": 4, "m.tech": 4, "mba": 4,
        "bachelor": 3, "bachelors": 3, "bs": 3, "bsc": 3, "b.tech": 3, "b.e": 3,
        "associate": 2, "diploma": 2,
        "high school": 1,
    }

    @classmethod
    def get_education_rank(cls, edu_str: Optional[str]) -> int:
        """Map education text to numeric rank (1-5). Defaults to 3 (Bachelor's) if unspecified."""
        if not edu_str:
            return 3  # Neutral baseline
        edu_lower = edu_str.lower()
        for key, rank in cls.EDUCATION_LEVELS.items():
            if key in edu_lower:
                return rank
        return 3

    @classmethod
    def evaluate_skills(
        cls, candidate_skills: List[str], required_skills: List[str], preferred_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluate skill match between candidate skills and job required/preferred skills.
        Case-insensitive comparison with normalized keys.
        """
        # Build normalized lookups: lowercase -> original string
        cand_map = {s.strip().lower(): s.strip() for s in candidate_skills if s and s.strip()}
        req_map = {s.strip().lower(): s.strip() for s in required_skills if s and s.strip()}
        pref_map = {s.strip().lower(): s.strip() for s in preferred_skills if s and s.strip()}

        cand_set = set(cand_map.keys())
        req_set = set(req_map.keys())
        pref_set = set(pref_map.keys())

        # Matched required skills
        matched_req_keys = cand_set.intersection(req_set)
        matched_required = [req_map[k] for k in matched_req_keys]
        missing_required = [req_map[k] for k in req_set - matched_req_keys]

        # Matched preferred skills
        matched_pref_keys = cand_set.intersection(pref_set)
        matched_preferred = [pref_map[k] for k in matched_pref_keys]
        missing_preferred = [pref_map[k] for k in pref_set - matched_pref_keys]

        # Additional candidate skills not listed in job description
        job_all_keys = req_set.union(pref_set)
        additional_keys = cand_set - job_all_keys
        additional_skills = [cand_map[k] for k in additional_keys]

        # Compute skill overlap scores
        req_ratio = len(matched_req_keys) / len(req_set) if req_set else 1.0
        pref_ratio = len(matched_pref_keys) / len(pref_set) if pref_set else 1.0

        # Weighted skill score: 75% required skills, 25% preferred skills
        if req_set and pref_set:
            skill_score = (req_ratio * 0.75 + pref_ratio * 0.25) * 100.0
        elif req_set:
            skill_score = req_ratio * 100.0
        elif pref_set:
            skill_score = pref_ratio * 100.0
        else:
            skill_score = 100.0  # No skills specified in JD

        all_matched_skills = sorted(list(set(matched_required + matched_preferred)))

        return {
            "skill_score": round(min(skill_score, 100.0), 1),
            "matched_required_skills": matched_required,
            "missing_required_skills": missing_required,
            "matched_preferred_skills": matched_preferred,
            "missing_preferred_skills": missing_preferred,
            "matched_skills": all_matched_skills,
            "additional_skills": additional_skills,
            "required_match_ratio": round(req_ratio, 3),
            "preferred_match_ratio": round(pref_ratio, 3),
        }

    @classmethod
    def evaluate_experience(
        cls, candidate_years: float, min_years: float = 0.0, max_years: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Evaluate candidate years of experience against job min and max requirements.
        Returns a score (0 to 100) and an explanation.
        """
        candidate_years = float(candidate_years or 0.0)
        min_years = float(min_years or 0.0)

        # Baseline: if no minimum required
        if min_years <= 0.0 and (max_years is None or max_years <= 0.0):
            return {
                "experience_score": 100.0,
                "status": "Meets Requirements",
                "explanation": f"Candidate has {candidate_years:.1f} years of experience; position has no minimum requirement.",
            }

        # Candidate meets or exceeds minimum
        if candidate_years >= min_years:
            if max_years and candidate_years > (max_years + 3.0):
                # Significantly exceeds max range - slight overqualification adjustment
                score = 90.0
                status = "Senior / Overqualified"
                explanation = (
                    f"Candidate has {candidate_years:.1f} years experience, exceeding target upper bound "
                    f"({max_years:.1f} yrs). Strong background but may require senior alignment."
                )
            elif max_years and candidate_years > max_years:
                score = 95.0
                status = "Ideal Experience"
                explanation = f"Candidate has {candidate_years:.1f} years experience, closely matching target range ({min_years:.0f}-{max_years:.0f} yrs)."
            else:
                score = 100.0
                status = "Meets Requirements"
                explanation = f"Candidate has {candidate_years:.1f} years experience, meeting requirement ({min_years:.0f}+ yrs)."
        else:
            # Below minimum experience
            deficit = min_years - candidate_years
            if deficit <= 1.0:
                score = 80.0
                status = "Close to Target"
                explanation = f"Candidate has {candidate_years:.1f} years experience, slightly below the {min_years:.0f} year requirement (1 yr deficit)."
            elif deficit <= 2.0:
                score = 60.0
                status = "Moderate Deficit"
                explanation = f"Candidate has {candidate_years:.1f} years experience, 2 years below the {min_years:.0f} year requirement."
            elif deficit <= 4.0:
                score = 35.0
                status = "Significant Deficit"
                explanation = f"Candidate has {candidate_years:.1f} years experience, substantially below the {min_years:.0f} year requirement."
            else:
                score = 15.0
                status = "Below Minimum"
                explanation = f"Candidate has {candidate_years:.1f} years experience, well under the {min_years:.0f} year requirement."

        return {
            "experience_score": round(score, 1),
            "status": status,
            "explanation": explanation,
        }

    @classmethod
    def evaluate_education(
        cls, candidate_edu: Optional[str], required_edu: Optional[str]
    ) -> Dict[str, Any]:
        """
        Evaluate candidate education level against required education.
        Returns a score (0 to 100) and an explanation.
        """
        if not required_edu or required_edu.lower() in ["any", "not specified", "none"]:
            return {
                "education_score": 100.0,
                "explanation": f"Candidate holds {candidate_edu or 'an unlisted degree'}; no strict degree required.",
            }

        cand_rank = cls.get_education_rank(candidate_edu)
        req_rank = cls.get_education_rank(required_edu)

        if cand_rank >= req_rank:
            score = 100.0
            explanation = f"Candidate holds {candidate_edu or 'Bachelor’s degree'}, which meets or exceeds requirement ({required_edu})."
        elif cand_rank == req_rank - 1:
            score = 75.0
            explanation = f"Candidate holds {candidate_edu or 'lower degree'}, slightly below preferred ({required_edu})."
        else:
            score = 40.0
            explanation = f"Candidate degree ({candidate_edu or 'None'}) does not meet required degree level ({required_edu})."

        return {
            "education_score": round(score, 1),
            "explanation": explanation,
        }

    @classmethod
    def evaluate_keyword_coverage(cls, resume_text: str, job_text: str) -> Dict[str, Any]:
        """
        Evaluate lexical keyword coverage between resume text and job description text.
        """
        if not resume_text or not job_text:
            return {"keyword_score": 50.0, "covered_keywords": [], "missing_keywords": []}

        # Tokenize job text into meaningful keywords
        clean_job = re.sub(r"[^a-zA-Z0-9\s]", " ", job_text.lower())
        tokens = [t for t in clean_job.split() if len(t) > 3]

        # Count frequencies
        freq: Dict[str, int] = {}
        for t in tokens:
            freq[t] = freq.get(t, 0) + 1

        # Select top frequent domain words (excluding common filler words)
        ignore_words = {
            "with", "that", "this", "from", "have", "will", "your", "work", "team",
            "role", "join", "help", "about", "what", "more", "must", "well", "such"
        }
        domain_keywords = [
            w for w, count in sorted(freq.items(), key=lambda x: x[1], reverse=True)
            if w not in ignore_words
        ][:25]

        clean_resume = re.sub(r"[^a-zA-Z0-9\s]", " ", resume_text.lower())
        resume_words = set(clean_resume.split())

        covered = [k for k in domain_keywords if k in resume_words]
        missing = [k for k in domain_keywords if k not in resume_words]

        ratio = len(covered) / len(domain_keywords) if domain_keywords else 1.0
        score = round(ratio * 100.0, 1)

        return {
            "keyword_score": score,
            "covered_keywords": covered[:10],
            "missing_keywords": missing[:10],
            "coverage_ratio": round(ratio, 3),
        }
