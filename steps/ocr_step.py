"""
OCR Step

This step handles text extraction from COI PDF files using EasyOCR
and PyPDF2 for both scanned and text-based PDFs.
"""

import os
from typing import List, Dict, Any
from pathlib import Path
import easyocr
import PyPDF2
from PIL import Image
import pdf2image
from zenml import step
from zenml.logger import get_logger

logger = get_logger(__name__)


@step
def extract_text_from_pdf(
    pdf_files: List[Dict[str, Any]],
    use_ocr: bool = True,
    languages: List[str] = ['en']
) -> List[Dict[str, Any]]:
    """
    Extract text from COI PDF files using OCR and text extraction
    
    Args:
        pdf_files: List of PDF file metadata dictionaries
        use_ocr: Whether to use OCR for scanned PDFs
        languages: List of languages for OCR recognition
        
    Returns:
        List of dictionaries containing extracted text and metadata
    """
    
    extracted_texts = []
    
    # Initialize EasyOCR reader if OCR is enabled
    if use_ocr:
        logger.info(f"Initializing EasyOCR reader for languages: {languages}")
        reader = easyocr.Reader(languages)
    else:
        reader = None
    
    for pdf_file in pdf_files:
        logger.info(f"Processing PDF: {pdf_file['file_name']}")
        
        try:
            # First, try to extract text directly from PDF
            direct_text = _extract_text_direct(pdf_file['file_path'])
            
            # If direct text extraction yields little content, use OCR
            if len(direct_text.strip()) < 100 and use_ocr:
                logger.info(f"Direct text extraction insufficient, using OCR for {pdf_file['file_name']}")
                ocr_text = _extract_text_ocr(pdf_file['file_path'], reader)
                extracted_text = ocr_text
                extraction_method = "ocr"
            else:
                extracted_text = direct_text
                extraction_method = "direct"
            
            extracted_texts.append({
                "file_name": pdf_file['file_name'],
                "file_path": pdf_file['file_path'],
                "extracted_text": extracted_text,
                "extraction_method": extraction_method,
                "text_length": len(extracted_text),
                "source": pdf_file.get('source', 'unknown'),
                "original_metadata": pdf_file
            })
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_file['file_name']}: {e}")
            extracted_texts.append({
                "file_name": pdf_file['file_name'],
                "file_path": pdf_file['file_path'],
                "extracted_text": "",
                "extraction_method": "error",
                "text_length": 0,
                "error": str(e),
                "source": pdf_file.get('source', 'unknown'),
                "original_metadata": pdf_file
            })
    
    logger.info(f"Successfully processed {len(extracted_texts)} PDF files")
    return extracted_texts


def _extract_text_direct(pdf_path: str) -> str:
    """Extract text directly from PDF using PyPDF2"""
    text = ""
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
                
    except Exception as e:
        logger.warning(f"Direct text extraction failed for {pdf_path}: {e}")
        
    return text


def _extract_text_ocr(pdf_path: str, reader) -> str:
    """Extract text from PDF using OCR"""
    text = ""
    
    try:
        # Convert PDF to images
        images = pdf2image.convert_from_path(pdf_path)
        
        for i, image in enumerate(images):
            logger.info(f"Processing page {i+1} with OCR")
            
            # Use EasyOCR to extract text
            results = reader.readtext(image, detail=0)
            page_text = " ".join(results)
            text += page_text + "\n"
            
    except Exception as e:
        logger.error(f"OCR extraction failed for {pdf_path}: {e}")
        raise
        
    return text
