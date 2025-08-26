from __future__ import annotations

from pathlib import Path

from docx import Document


def extract_text_from_docx(path: str | Path) -> str:
	"""Extract text from a DOCX file using python-docx."""
	document = Document(str(path))
	paragraphs = [p.text for p in document.paragraphs if p.text]
	return "\n".join(paragraphs)
