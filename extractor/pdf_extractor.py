"""
PDF Text Extractor
Extracts text from PDF files using pypdf library
"""

import pypdf
from pathlib import Path
from typing import Optional


def extract_text_from_pdf(file_path: Path) -> Optional[str]:
    """
    Extract text from a PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text as string, or None if extraction fails
    """
    try:
        text = ""
        
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        return text.strip() if text else None
        
    except Exception as e:
        print(f"Error extracting text from PDF {file_path}: {e}")
        return None
