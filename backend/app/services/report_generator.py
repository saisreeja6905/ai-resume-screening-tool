import csv
import io
from datetime import datetime
from typing import List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from backend.app.models.candidate import Candidate
from backend.app.models.job_description import JobDescription
from backend.app.models.match_result import MatchResult


class ReportGenerator:
    """Generates professional PDF screening reports and CSV ranking exports."""

    @staticmethod
    def generate_candidate_pdf(candidate: Candidate, match: Optional[MatchResult] = None) -> io.BytesIO:
        """Generate a complete PDF evaluation report for an individual candidate."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1e293b"),
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#64748b"),
            spaceAfter=12,
        )
        section_style = ParagraphStyle(
            "ReportSection",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=14,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#334155"),
        )
        bold_body = ParagraphStyle(
            "ReportBodyBold",
            parent=body_style,
            fontName="Helvetica-Bold",
        )

        elements = []

        # Header
        elements.append(Paragraph(f"Candidate Screening Report: {candidate.full_name}", title_style))
        elements.append(
            Paragraph(
                f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M UTC')} | AntiGravity AI Screener",
                subtitle_style,
            )
        )
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#cbd5e1"), spaceAfter=14))

        # Personal / Contact Information Table
        elements.append(Paragraph("Candidate Overview", section_style))
        overview_data = [
            [
                Paragraph("<b>Full Name:</b>", body_style),
                Paragraph(candidate.full_name, body_style),
                Paragraph("<b>Current Status:</b>", body_style),
                Paragraph(candidate.status.upper(), bold_body),
            ],
            [
                Paragraph("<b>Email:</b>", body_style),
                Paragraph(candidate.email or "Not Provided", body_style),
                Paragraph("<b>Phone:</b>", body_style),
                Paragraph(candidate.phone or "Not Provided", body_style),
            ],
            [
                Paragraph("<b>Experience:</b>", body_style),
                Paragraph(f"{candidate.years_experience:.1f} Years", body_style),
                Paragraph("<b>Education:</b>", body_style),
                Paragraph(candidate.highest_education or "Not Specified", body_style),
            ],
            [
                Paragraph("<b>Current Title:</b>", body_style),
                Paragraph(candidate.current_title or "Not Specified", body_style),
                Paragraph("<b>LinkedIn:</b>", body_style),
                Paragraph(candidate.linkedin_url or "Not Provided", body_style),
            ],
        ]

        overview_table = Table(overview_data, colWidths=[1.3 * inch, 2.2 * inch, 1.3 * inch, 2.2 * inch])
        overview_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("PADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ])
        )
        elements.append(overview_table)
        elements.append(Spacer(1, 10))

        # Candidate Summary
        if candidate.summary:
            elements.append(Paragraph("Executive Summary", section_style))
            elements.append(Paragraph(candidate.summary, body_style))
            elements.append(Spacer(1, 10))

        # Extracted Skills Table
        elements.append(Paragraph(f"Skills Extracted ({len(candidate.candidate_skills)})", section_style))
        skill_names = [cs.skill.name for cs in candidate.candidate_skills if cs.skill]
        if skill_names:
            skills_chunked = [skill_names[i:i + 4] for i in range(0, len(skill_names), 4)]
            skill_table_data = []
            for row in skills_chunked:
                padded = row + [""] * (4 - len(row))
                skill_table_data.append([Paragraph(f"• {s}" if s else "", body_style) for s in padded])

            sk_table = Table(skill_table_data, colWidths=[1.75 * inch] * 4)
            sk_table.setStyle(
                TableStyle([
                    ("PADDING", (0, 0), (-1, -1), 4),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ])
            )
            elements.append(sk_table)
        else:
            elements.append(Paragraph("No specific skills registered.", body_style))
        elements.append(Spacer(1, 10))

        # Match Result (if available)
        if match:
            elements.append(Paragraph(f"Job Match Analysis: {match.job.title}", section_style))

            score_color = "#16a34a" if match.overall_score >= 70 else ("#ca8a04" if match.overall_score >= 50 else "#dc2626")
            score_card_data = [
                [
                    Paragraph("<b>Overall Score</b>", body_style),
                    Paragraph("<b>Skill Match (35%)</b>", body_style),
                    Paragraph("<b>TF-IDF Alignment (25%)</b>", body_style),
                    Paragraph("<b>Experience Match (20%)</b>", body_style),
                    Paragraph("<b>Education (10%)</b>", body_style),
                ],
                [
                    Paragraph(f"<font color='{score_color}' size='14'><b>{match.overall_score:.1f}%</b></font>", body_style),
                    Paragraph(f"{match.skill_score:.1f}%", body_style),
                    Paragraph(f"{(match.tfidf_similarity * 100):.1f}%", body_style),
                    Paragraph(f"{match.experience_score:.1f}%", body_style),
                    Paragraph(f"{match.education_score:.1f}%", body_style),
                ],
            ]
            score_table = Table(score_card_data, colWidths=[1.4 * inch] * 5)
            score_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ])
            )
            elements.append(score_table)
            elements.append(Spacer(1, 10))

            # Matched & Missing Skills
            explanation = match.score_explanation or {}
            elements.append(Paragraph("<b>Skill Alignment Breakdown:</b>", bold_body))

            matched_skills_str = ", ".join(match.matched_skills) if match.matched_skills else "None"
            missing_req_str = ", ".join(match.missing_required_skills) if match.missing_required_skills else "None"
            missing_pref_str = ", ".join(match.missing_preferred_skills) if match.missing_preferred_skills else "None"

            elements.append(Paragraph(f"<b>Matched Skills:</b> {matched_skills_str}", body_style))
            elements.append(Paragraph(f"<b>Missing Required:</b> {missing_req_str}", body_style))
            elements.append(Paragraph(f"<b>Missing Preferred:</b> {missing_pref_str}", body_style))
            elements.append(Spacer(1, 8))

            # Recommendation
            rec = explanation.get("recommendation")
            if rec:
                elements.append(Paragraph("<b>Recommendation:</b>", bold_body))
                elements.append(Paragraph(rec, body_style))
                elements.append(Spacer(1, 8))

        # Disclaimer
        elements.append(Spacer(1, 15))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=6))
        elements.append(
            Paragraph(
                "<i>Notice: AntiGravity AI resume screening scores are algorithmic decision-support signals designed to "
                "facilitate human review. They must not replace holistic human evaluation or form the sole basis for hiring choices.</i>",
                ParagraphStyle("Disclaimer", parent=styles["Italic"], fontSize=8, textColor=colors.HexColor("#64748b")),
            )
        )

        doc.build(elements)
        buffer.seek(0)
        return buffer

    @staticmethod
    def generate_job_summary_pdf(job: JobDescription, matches: List[MatchResult]) -> io.BytesIO:
        """Generate a complete PDF summary report for a job opening and its ranked candidates."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "JobReportTitle",
            parent=styles["Heading1"],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "JobReportSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#64748b"),
            spaceAfter=12,
        )
        section_style = ParagraphStyle(
            "JobSectionTitle",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=10,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "JobBody",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#334155"),
        )
        header_table_style = ParagraphStyle(
            "HeaderCell",
            parent=body_style,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#0f172a"),
        )

        elements = []

        # Header
        elements.append(Paragraph(f"Job Screening Summary: {job.title}", title_style))
        elements.append(
            Paragraph(
                f"Department: {job.department} | Generated: {datetime.now().strftime('%B %d, %Y')} | AntiGravity AI",
                subtitle_style,
            )
        )
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#cbd5e1"), spaceAfter=10))

        # Job Overview Table
        req_skills_str = ", ".join(job.required_skills or [])
        pref_skills_str = ", ".join(job.preferred_skills or [])
        exp_range = f"{job.min_experience} - {job.max_experience or 'Any'} years"

        job_info_data = [
            [Paragraph("<b>Min Experience:</b>", body_style), Paragraph(exp_range, body_style),
             Paragraph("<b>Education:</b>", body_style), Paragraph(job.education_level or "Any", body_style)],
            [Paragraph("<b>Required Skills:</b>", body_style), Paragraph(req_skills_str or "None specified", body_style),
             Paragraph("<b>Preferred Skills:</b>", body_style), Paragraph(pref_skills_str or "None specified", body_style)],
        ]
        info_table = Table(job_info_data, colWidths=[1.3 * inch, 2.2 * inch, 1.3 * inch, 2.2 * inch])
        info_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("PADDING", (0, 0), (-1, -1), 5),
            ])
        )
        elements.append(info_table)
        elements.append(Spacer(1, 10))

        # Ranked Candidates Table
        elements.append(Paragraph(f"Candidate Screening Ranking ({len(matches)} Candidates Evaluated)", section_style))

        if matches:
            table_rows = [
                [
                    Paragraph("<b>Rank</b>", header_table_style),
                    Paragraph("<b>Candidate Name</b>", header_table_style),
                    Paragraph("<b>Overall</b>", header_table_style),
                    Paragraph("<b>Skills</b>", header_table_style),
                    Paragraph("<b>Experience</b>", header_table_style),
                    Paragraph("<b>Status</b>", header_table_style),
                ]
            ]

            for rank, m in enumerate(matches, start=1):
                cand = m.candidate
                cand_name = cand.full_name if cand else "Unknown"
                status = cand.status.capitalize() if cand else "-"
                score_str = f"<b>{m.overall_score:.1f}%</b>"

                table_rows.append([
                    Paragraph(f"#{rank}", body_style),
                    Paragraph(cand_name, body_style),
                    Paragraph(score_str, body_style),
                    Paragraph(f"{m.skill_score:.1f}%", body_style),
                    Paragraph(f"{m.experience_score:.1f}%", body_style),
                    Paragraph(status, body_style),
                ])

            rank_table = Table(table_rows, colWidths=[0.6 * inch, 2.4 * inch, 1.0 * inch, 1.0 * inch, 1.0 * inch, 1.0 * inch])
            rank_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                    ("PADDING", (0, 0), (-1, -1), 5),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ])
            )
            elements.append(rank_table)
        else:
            elements.append(Paragraph("No candidates evaluated for this job yet.", body_style))

        # Footer disclaimer
        elements.append(Spacer(1, 15))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=6))
        elements.append(
            Paragraph(
                "<i>AntiGravity AI Resume Screening Report — Designed for decision-support only.</i>",
                ParagraphStyle("Disclaimer", parent=styles["Italic"], fontSize=8, textColor=colors.HexColor("#64748b")),
            )
        )

        doc.build(elements)
        buffer.seek(0)
        return buffer

    @staticmethod
    def generate_candidate_ranking_csv(job: JobDescription, matches: List[MatchResult]) -> str:
        """Generate CSV string of candidate rankings for a job."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        writer.writerow([
            "Rank",
            "Candidate ID",
            "Full Name",
            "Email",
            "Phone",
            "Current Status",
            "Years Experience",
            "Education",
            "Overall Match Score (%)",
            "Skill Score (%)",
            "TF-IDF Alignment (%)",
            "Experience Score (%)",
            "Education Score (%)",
            "Keyword Score (%)",
            "Matched Skills",
            "Missing Required Skills",
            "Missing Preferred Skills",
        ])

        for rank, m in enumerate(matches, start=1):
            cand = m.candidate
            writer.writerow([
                rank,
                cand.id if cand else "",
                cand.full_name if cand else "Unknown",
                cand.email if cand else "",
                cand.phone if cand else "",
                cand.status if cand else "",
                cand.years_experience if cand else 0,
                cand.highest_education if cand else "",
                round(m.overall_score, 1),
                round(m.skill_score, 1),
                round(m.tfidf_similarity * 100, 1),
                round(m.experience_score, 1),
                round(m.education_score, 1),
                round(m.keyword_score, 1),
                "; ".join(m.matched_skills or []),
                "; ".join(m.missing_required_skills or []),
                "; ".join(m.missing_preferred_skills or []),
            ])

        return output.getvalue()


# Singleton instance
report_generator = ReportGenerator()
