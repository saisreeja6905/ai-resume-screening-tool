import logging
import os
import re
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class PDFParser:
    """Extracts and normalizes text from PDF resumes using pdfplumber."""

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return ""

        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Replace non-breaking spaces and other odd unicode spaces with standard space
        text = re.sub(r"[\u00a0\u1680\u180e\u2000-\u200b\u202f\u205f\u3000\ufeff]", " ", text)

        # Normalize multiple spaces on the same line to single space
        text = re.sub(r"[ \t]+", " ", text)

        # Remove excessive blank lines (more than 2 consecutive newlines -> 2 newlines)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    @classmethod
    def extract_text(cls, file_path: str) -> Dict[str, Any]:
        """
        Extract text from a PDF file page by page.

        Returns a dictionary with:
            success: bool
            full_text: str
            pages: List[Dict[str, Any]]
            total_pages: int
            metadata: Dict[str, Any]
            error: Optional[str]
        """
        if not os.path.exists(file_path):
            return {
                "success": False,
                "full_text": "",
                "pages": [],
                "total_pages": 0,
                "metadata": {},
                "error": f"File not found: {file_path}",
            }

        try:
            import pdfplumber
        except ImportError:
            logger.error("pdfplumber is not installed.")
            return {
                "success": False,
                "full_text": "",
                "pages": [],
                "total_pages": 0,
                "metadata": {},
                "error": "pdfplumber library is not installed.",
            }

        extracted_pages: List[Dict[str, Any]] = []
        all_text_parts: List[str] = []
        metadata: Dict[str, Any] = {}

        try:
            with pdfplumber.open(file_path) as pdf:
                metadata = {
                    "pages": len(pdf.pages),
                    "author": pdf.metadata.get("Author") if pdf.metadata else None,
                    "creator": pdf.metadata.get("Creator") if pdf.metadata else None,
                    "producer": pdf.metadata.get("Producer") if pdf.metadata else None,
                }

                for idx, page in enumerate(pdf.pages):
                    page_number = idx + 1
                    raw_page_text = page.extract_text(layout=False) or ""
                    cleaned_page_text = cls.clean_text(raw_page_text)

                    extracted_pages.append({
                        "page_number": page_number,
                        "text": cleaned_page_text,
                        "character_count": len(cleaned_page_text),
                    })

                    if cleaned_page_text:
                        all_text_parts.append(cleaned_page_text)

            full_text = "\n\n".join(all_text_parts).strip()

            if not full_text:
                return {
                    "success": False,
                    "full_text": "",
                    "pages": extracted_pages,
                    "total_pages": len(extracted_pages),
                    "metadata": metadata,
                    "error": (
                        "No readable text could be extracted from this PDF. The document may be a scanned image "
                        "or image-only PDF without an embedded text layer. Please provide a text-searchable PDF."
                    ),
                }

            return {
                "success": True,
                "full_text": full_text,
                "pages": extracted_pages,
                "total_pages": len(extracted_pages),
                "metadata": metadata,
                "error": None,
            }

        except Exception as e:
            logger.exception("Error extracting PDF text from %s: %s", file_path, str(e))
            return {
                "success": False,
                "full_text": "",
                "pages": [],
                "total_pages": 0,
                "metadata": {},
                "error": f"Failed to parse PDF document: {str(e)}",
            }
