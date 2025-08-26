"""
DOCX Text Extractor
Extracts text from DOCX files using python-docx library
"""

from docx import Document
from pathlib import Path
from typing import Optional


def extract_text_from_docx(file_path: Path) -> Optional[str]:
    """
    Extract text from a DOCX file.
    
    Args:
        file_path: Path to the DOCX file
        
    Returns:
        Extracted text as string, or None if extraction fails
    """
    try:
        doc = Document(file_path)
        text = ""
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + "\n"
        
        return text.strip() if text else None
        
    except Exception as e:
        print(f"Error extracting text from DOCX {file_path}: {e}")
        return None
