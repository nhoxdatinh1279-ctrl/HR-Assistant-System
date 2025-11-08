"""
CV Text Extractor Module
Extracts text from various file formats (PDF, DOCX, TXT)
"""

import base64
import io
import re
from typing import Tuple

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None


def extract_pdf_text(pdf_base64: str) -> str:
    """
    Extract text from PDF (base64 encoded)
    
    Args:
        pdf_base64: Base64 encoded PDF string
        
    Returns:
        Extracted text from PDF
    """
    if not PdfReader:
        return ""
    
    try:
        # Decode base64 to bytes
        pdf_bytes = base64.b64decode(pdf_base64)
        
        # Create PDF reader from bytes
        pdf_file = io.BytesIO(pdf_bytes)
        pdf_reader = PdfReader(pdf_file)
        
        # Extract text from all pages
        extracted_text = ""
        for page in pdf_reader.pages:
            extracted_text += page.extract_text() + "\n"
        
        return extracted_text.strip()
    except Exception as e:
        print(f"[WARNING] Failed to extract PDF: {str(e)}")
        return ""


def extract_docx_text(docx_base64: str) -> str:
    """
    Extract text from DOCX (base64 encoded)
    
    Args:
        docx_base64: Base64 encoded DOCX string
        
    Returns:
        Extracted text from DOCX
    """
    if not Document:
        return ""
    
    try:
        # Decode base64 to bytes
        docx_bytes = base64.b64decode(docx_base64)
        
        # Create Document from bytes
        docx_file = io.BytesIO(docx_bytes)
        doc = Document(docx_file)
        
        # Extract text from all paragraphs
        extracted_text = ""
        for paragraph in doc.paragraphs:
            extracted_text += paragraph.text + "\n"
        
        return extracted_text.strip()
    except Exception as e:
        print(f"[WARNING] Failed to extract DOCX: {str(e)}")
        return ""


def extract_text_file(txt_base64: str) -> str:
    """
    Extract text from plain text file (base64 encoded)
    
    Args:
        txt_base64: Base64 encoded text string
        
    Returns:
        Extracted text
    """
    try:
        # Decode base64 to string
        text_bytes = base64.b64decode(txt_base64)
        text = text_bytes.decode('utf-8', errors='ignore')
        return text.strip()
    except Exception as e:
        print(f"[WARNING] Failed to extract text file: {str(e)}")
        return ""


def extract_cv_content(file_content: str, file_type: str) -> str:
    """
    Extract CV content based on file type
    
    Args:
        file_content: Base64 encoded file content
        file_type: File type (pdf, docx, doc, txt)
        
    Returns:
        Extracted text content from CV
    """
    file_type = file_type.lower()
    
    print(f"[CV_EXTRACTOR] Extracting from {file_type} file...")
    
    if file_type in ['pdf']:
        extracted = extract_pdf_text(file_content)
    elif file_type in ['docx']:
        extracted = extract_docx_text(file_content)
    elif file_type in ['doc']:
        # For older DOC format, try DOCX extraction as fallback
        extracted = extract_docx_text(file_content)
    elif file_type in ['txt']:
        extracted = extract_text_file(file_content)
    else:
        # Default to text extraction
        extracted = extract_text_file(file_content)
    
    if not extracted:
        print(f"[WARNING] No text extracted from {file_type} file")
        return ""
    
    print(f"[OK] Extracted {len(extracted)} characters from CV")
    return extracted


def parse_cv_for_skills(cv_text: str) -> dict:
    """
    Parse CV text to extract key information
    
    Args:
        cv_text: Full CV text content
        
    Returns:
        Dictionary with parsed CV information
    """
    cv_lower = cv_text.lower()
    
    # Extract years of experience
    years_match = re.search(r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience|exp)', cv_lower)
    years_experience = int(years_match.group(1)) if years_match else 0
    
    # Detect level (Junior, Mid, Senior)
    level = "Junior"
    if "senior" in cv_lower or "lead" in cv_lower or "principal" in cv_lower:
        level = "Senior"
    elif "mid" in cv_lower or "mid-level" in cv_lower:
        level = "Mid"
    
    # Extract education level
    education_level = "None"
    if "phd" in cv_lower or "doctorate" in cv_lower:
        education_level = "PhD"
    elif "master" in cv_lower or "m.s." in cv_lower or "msc" in cv_lower:
        education_level = "Master's"
    elif "bachelor" in cv_lower or "b.s." in cv_lower or "bsc" in cv_lower:
        education_level = "Bachelor's"
    
    return {
        "years_experience": years_experience,
        "level": level,
        "education_level": education_level,
        "raw_text": cv_text
    }
