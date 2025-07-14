"""
Configuration settings for COI Compliance Validation Pipeline
"""

import os
from pathlib import Path
from typing import Dict, Any

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"
UTILS_DIR = PROJECT_ROOT / "utils"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)
UTILS_DIR.mkdir(exist_ok=True)

# Pipeline configuration
PIPELINE_CONFIG = {
    "name": "coi_compliance_pipeline",
    "version": "1.0.0",
    "description": "COI Compliance Validation Pipeline with AI Analysis",
    "default_data_path": str(DATA_DIR),
    "default_output_path": str(REPORTS_DIR),
    "compliance_rules_path": str(UTILS_DIR / "compliance_rules.json"),
}

# Gemini AI configuration
GEMINI_CONFIG = {
    "api_key": os.getenv("GEMINI_API_KEY"),
    "model": "gemini-2.0-flash",
    "temperature": 0.1,
    "max_tokens": 8192,
    "safety_settings": {
        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
        "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
        "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
        "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
    }
}

# Flask configuration
FLASK_CONFIG = {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": os.getenv("FLASK_DEBUG", "False").lower() == "true",
    "env": os.getenv("FLASK_ENV", "production"),
}

# OCR configuration
OCR_CONFIG = {
    "languages": ["en"],
    "gpu": False,  # Set to True if GPU is available
    "detail": 1,
    "paragraph": False,
}

# Compliance rules
COMPLIANCE_RULES = {
    "required_fields": [
        "policy_number",
        "insurance_company", 
        "insured_name",
        "policy_period"
    ],
    "minimum_coverage_limits": {
        "general_liability": 1000000,
        "professional_liability": 1000000,
        "workers_compensation": 1000000,
    },
    "required_additional_insureds": ["Injala LLC"],
    "minimum_cancellation_notice_days": 30,
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": str(PROJECT_ROOT / "logs" / "pipeline.log"),
}

def get_config() -> Dict[str, Any]:
    """Get all configuration settings"""
    return {
        "pipeline": PIPELINE_CONFIG,
        "gemini": GEMINI_CONFIG,
        "flask": FLASK_CONFIG,
        "ocr": OCR_CONFIG,
        "compliance": COMPLIANCE_RULES,
        "logging": LOGGING_CONFIG,
    }

def validate_config() -> bool:
    """Validate configuration settings"""
    if not GEMINI_CONFIG["api_key"]:
        print("WARNING: GEMINI_API_KEY not found in environment variables")
        return False
    
    if not (UTILS_DIR / "compliance_rules.json").exists():
        print("WARNING: compliance_rules.json not found")
        return False
    
    return True
