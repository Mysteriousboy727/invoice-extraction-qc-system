"""
PDF Reader Utility

Provides functionality to extract text from PDF files using pdfplumber.
"""

import pdfplumber
from pathlib import Path
from typing import Optional, List


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """
    Extract all text from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as a single string
        
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        Exception: If PDF cannot be read
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    if not pdf_path.suffix.lower() == '.pdf':
        raise ValueError(f"File is not a PDF: {pdf_path}")
    
    text_content = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
    except Exception as e:
        raise Exception(f"Error reading PDF {pdf_path}: {str(e)}")
    
    return "\n\n".join(text_content)


def extract_text_from_pdfs(pdf_dir: str | Path) -> List[tuple[str, str]]:
    """
    Extract text from all PDF files in a directory.
    
    Args:
        pdf_dir: Directory containing PDF files
        
    Returns:
        List of tuples (filename, extracted_text)
    """
    pdf_dir = Path(pdf_dir)
    
    if not pdf_dir.exists():
        raise FileNotFoundError(f"Directory not found: {pdf_dir}")
    
    if not pdf_dir.is_dir():
        raise ValueError(f"Path is not a directory: {pdf_dir}")
    
    results = []
    
    for pdf_file in pdf_dir.glob("*.pdf"):
        try:
            text = extract_text_from_pdf(pdf_file)
            results.append((pdf_file.name, text))
        except Exception as e:
            print(f"Warning: Could not extract text from {pdf_file.name}: {e}")
            continue
    
    return results

