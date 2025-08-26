from __future__ import annotations

from pathlib import Path
from typing import Optional

from pypdf import PdfReader


def extract_text_from_pdf(path: str | Path, password: Optional[str] = None) -> str:
	"""Extract text from a PDF file using pypdf.

	Args:
		path: Path to the PDF file.
		password: Optional password for encrypted PDFs.

	Returns:
		Extracted text as a single string. Returns empty string if nothing could be extracted.
	"""
	pdf_path = Path(path)
	with pdf_path.open("rb") as file_obj:
		reader = PdfReader(file_obj)
		if reader.is_encrypted:
			if password:
				try:
					reader.decrypt(password)
				except Exception:
					return ""
			else:
				return ""
		texts: list[str] = []
		for page in reader.pages:
			try:
				texts.append(page.extract_text() or "")
			except Exception:
				continue
		return "\n".join(filter(None, texts))
