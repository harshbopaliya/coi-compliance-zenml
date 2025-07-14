"""
Parsing Step

This step parses insurance policy fields from extracted text using
regular expressions and NLP techniques with spaCy.
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import spacy
from zenml import step
from zenml.logger import get_logger

logger = get_logger(__name__)


@step
def parse_insurance_fields(
    extracted_texts: List[Dict[str, Any]],
    nlp_model: str = "en_core_web_sm"
) -> List[Dict[str, Any]]:
    """
    Parse insurance policy fields from extracted text
    
    Args:
        extracted_texts: List of extracted text dictionaries
        nlp_model: spaCy model name for NLP processing
        
    Returns:
        List of dictionaries containing parsed insurance fields
    """
    
    parsed_results = []
    
    # Load spaCy model
    try:
        nlp = spacy.load(nlp_model)
    except OSError:
        logger.warning(f"spaCy model {nlp_model} not found, using basic parsing")
        nlp = None
    
    for text_data in extracted_texts:
        logger.info(f"Parsing fields from {text_data['file_name']}")
        
        if text_data['extraction_method'] == 'error':
            parsed_results.append({
                "file_name": text_data['file_name'],
                "file_path": text_data['file_path'],
                "parsed_fields": {},
                "parsing_status": "error",
                "error": text_data.get('error', 'Unknown error during text extraction'),
                "original_metadata": text_data
            })
            continue
        
        text = text_data['extracted_text']
        
        # Parse insurance fields
        parsed_fields = _parse_insurance_fields(text, nlp)
        
        parsed_results.append({
            "file_name": text_data['file_name'],
            "file_path": text_data['file_path'],
            "parsed_fields": parsed_fields,
            "parsing_status": "success",
            "original_metadata": text_data
        })
    
    logger.info(f"Successfully parsed {len(parsed_results)} documents")
    return parsed_results


def _parse_insurance_fields(text: str, nlp=None) -> Dict[str, Any]:
    """Parse insurance fields from text using regex and NLP"""
    
    fields = {}
    
    # Parse policy number
    fields['policy_number'] = _extract_policy_number(text)
    
    # Parse policy dates
    fields['policy_period'] = _extract_policy_period(text)
    
    # Parse insurance company
    fields['insurance_company'] = _extract_insurance_company(text)
    
    # Parse insured name
    fields['insured_name'] = _extract_insured_name(text)
    
    # Parse coverage limits
    fields['coverage_limits'] = _extract_coverage_limits(text)
    
    # Parse certificate holder
    fields['certificate_holder'] = _extract_certificate_holder(text)
    
    # Parse additional insureds
    fields['additional_insureds'] = _extract_additional_insureds(text)
    
    # Parse cancellation clause
    fields['cancellation_clause'] = _extract_cancellation_clause(text)
    
    # Use NLP for enhanced parsing if available
    if nlp:
        fields.update(_enhance_parsing_with_nlp(text, nlp))
    
    return fields


def _extract_policy_number(text: str) -> Optional[str]:
    """Extract policy number from text"""
    patterns = [
        r"policy\s*(?:no|number|#)?\s*:?\s*([A-Z0-9\-]+)",
        r"pol\s*(?:no|number|#)?\s*:?\s*([A-Z0-9\-]+)",
        r"certificate\s*(?:no|number|#)?\s*:?\s*([A-Z0-9\-]+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None


def _extract_policy_period(text: str) -> Dict[str, Optional[str]]:
    """Extract policy effective and expiration dates"""
    period = {"effective_date": None, "expiration_date": None}
    
    # Common date patterns
    date_patterns = [
        r"\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}",
        r"\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{2,4}",
        r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,2},?\s+\d{2,4}"
    ]
    
    # Look for effective date
    effective_patterns = [
        r"effective\s*(?:date)?\s*:?\s*(" + "|".join(date_patterns) + ")",
        r"policy\s*period\s*:?\s*(" + "|".join(date_patterns) + ")"
    ]
    
    for pattern in effective_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            period["effective_date"] = match.group(1).strip()
            break
    
    # Look for expiration date
    expiration_patterns = [
        r"expir(?:ation|es?)\s*(?:date)?\s*:?\s*(" + "|".join(date_patterns) + ")",
        r"expires?\s*:?\s*(" + "|".join(date_patterns) + ")"
    ]
    
    for pattern in expiration_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            period["expiration_date"] = match.group(1).strip()
            break
    
    return period


def _extract_insurance_company(text: str) -> Optional[str]:
    """Extract insurance company name"""
    patterns = [
        r"company\s*:?\s*([A-Z][A-Za-z\s&.,]+(?:insurance|ins|assurance|mutual|company))",
        r"insurer\s*:?\s*([A-Z][A-Za-z\s&.,]+(?:insurance|ins|assurance|mutual|company))",
        r"carrier\s*:?\s*([A-Z][A-Za-z\s&.,]+(?:insurance|ins|assurance|mutual|company))"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None


def _extract_insured_name(text: str) -> Optional[str]:
    """Extract insured party name"""
    patterns = [
        r"insured\s*:?\s*([A-Z][A-Za-z\s&.,\-]+)",
        r"named\s*insured\s*:?\s*([A-Z][A-Za-z\s&.,\-]+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None


def _extract_coverage_limits(text: str) -> Dict[str, str]:
    """Extract coverage limits"""
    limits = {}
    
    # General liability limits
    gl_pattern = r"general\s*liability.*?(\$[\d,]+(?:\s*\/\s*\$[\d,]+)*)"
    match = re.search(gl_pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        limits["general_liability"] = match.group(1)
    
    # Professional liability limits
    pl_pattern = r"professional\s*liability.*?(\$[\d,]+(?:\s*\/\s*\$[\d,]+)*)"
    match = re.search(pl_pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        limits["professional_liability"] = match.group(1)
    
    # Workers compensation
    wc_pattern = r"workers?\s*comp(?:ensation)?.*?(\$[\d,]+(?:\s*\/\s*\$[\d,]+)*)"
    match = re.search(wc_pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        limits["workers_compensation"] = match.group(1)
    
    return limits


def _extract_certificate_holder(text: str) -> Optional[str]:
    """Extract certificate holder name"""
    patterns = [
        r"certificate\s*holder\s*:?\s*([A-Z][A-Za-z\s&.,\-]+)",
        r"holder\s*:?\s*([A-Z][A-Za-z\s&.,\-]+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None


def _extract_additional_insureds(text: str) -> List[str]:
    """Extract additional insured parties"""
    additional_insureds = []
    
    pattern = r"additional\s*insured\s*:?\s*([A-Z][A-Za-z\s&.,\-]+)"
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    for match in matches:
        additional_insureds.append(match.strip())
    
    return additional_insureds


def _extract_cancellation_clause(text: str) -> Optional[str]:
    """Extract cancellation clause information"""
    pattern = r"cancellation.*?(\d+\s*days?\s*written\s*notice)"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    
    if match:
        return match.group(1).strip()
    
    return None


def _enhance_parsing_with_nlp(text: str, nlp) -> Dict[str, Any]:
    """Use spaCy NLP to enhance field extraction"""
    enhanced_fields = {}
    
    try:
        doc = nlp(text)
        
        # Extract organizations
        organizations = []
        for ent in doc.ents:
            if ent.label_ == "ORG":
                organizations.append(ent.text)
        
        enhanced_fields["organizations"] = list(set(organizations))
        
        # Extract dates
        dates = []
        for ent in doc.ents:
            if ent.label_ == "DATE":
                dates.append(ent.text)
        
        enhanced_fields["dates"] = dates
        
        # Extract money amounts
        money_amounts = []
        for ent in doc.ents:
            if ent.label_ == "MONEY":
                money_amounts.append(ent.text)
        
        enhanced_fields["money_amounts"] = money_amounts
        
    except Exception as e:
        logger.warning(f"NLP enhancement failed: {e}")
    
    return enhanced_fields
