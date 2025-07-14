"""
COI Compliance Validation Pipeline

This pipeline orchestrates the entire COI compliance validation workflow:
1. Ingest COI PDFs from S3/local storage
2. Extract text using OCR
3. Parse insurance policy fields
4. Validate compliance against business rules
5. Generate compliance reports
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from zenml import pipeline
from steps.ingest_step import ingest_coi_pdfs
from steps.ocr_step import extract_text_from_pdf
from steps.parsing_step import parse_insurance_fields
from steps.compliance_check_step import validate_compliance
from steps.gemini_analysis_step import analyze_with_gemini
from steps.report_step import generate_compliance_report


@pipeline
def coi_compliance_pipeline(
    data_path: str = "data/",
    output_path: str = "reports/",
    compliance_rules_path: str = "utils/compliance_rules.json"
):
    """
    COI Compliance Validation Pipeline
    
    Args:
        data_path: Path to input COI PDF files
        output_path: Path to save compliance reports
        compliance_rules_path: Path to compliance rules configuration
    """
    
    # Step 1: Ingest COI PDFs
    pdf_files = ingest_coi_pdfs(data_path=data_path)
    
    # Step 2: Extract text using OCR
    extracted_text = extract_text_from_pdf(pdf_files=pdf_files)
    
    # Step 3: Parse insurance fields
    parsed_fields = parse_insurance_fields(extracted_texts=extracted_text)
    
    # Step 4: Validate compliance
    compliance_results = validate_compliance(
        parsed_results=parsed_fields,
        rules_path=compliance_rules_path
    )
    
    # Step 5: Analyze with Gemini AI
    enhanced_results = analyze_with_gemini(
        compliance_results=compliance_results,
        enable_analysis=True,
        enable_summary=True
    )
    
    # Step 6: Generate compliance report
    report = generate_compliance_report(
        compliance_results=enhanced_results,
        output_path=output_path
    )
    
    return report


if __name__ == "__main__":
    # Change to the parent directory for proper execution
    os.chdir(parent_dir)
    
    print("🚀 Running COI Compliance Pipeline directly...")
    print("=" * 60)
    
    # Run the pipeline
    try:
        result = coi_compliance_pipeline()
        print("\n✅ Pipeline executed successfully!")
        print(f"📝 Pipeline Run ID: {result.id}")
        print(f"🔗 Pipeline Run Name: {result.name}")
        print(f"📈 Pipeline Status: {result.status}")
    except Exception as e:
        print(f"\n❌ Pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
