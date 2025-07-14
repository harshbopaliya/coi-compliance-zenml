"""
Report Generation Step

This step generates compliance validation reports in JSON and CSV format
based on the compliance validation results.
"""

import os
import json
import csv
from typing import List, Dict, Any
from pathlib import Path
from zenml import step
from zenml.logger import get_logger

logger = get_logger(__name__)


@step
def generate_compliance_report(
    compliance_results: List[Dict[str, Any]],
    output_path: str = "reports/"
) -> None:
    """
    Generate compliance validation reports
    
    Args:
        compliance_results: List of compliance validation result dictionaries
        output_path: Path to save the generated reports
    """
    
    logger.info("Generating compliance reports...")
    
    # Ensure output directory exists
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    # JSON Report
    json_report_path = os.path.join(output_path, "compliance_report.json")
    with open(json_report_path, 'w') as json_file:
        json.dump(compliance_results, json_file, indent=2)
    logger.info(f"JSON compliance report saved to {json_report_path}")
    
    # CSV Report
    csv_report_path = os.path.join(output_path, "compliance_report.csv")
    _generate_csv_report(compliance_results, csv_report_path)
    logger.info(f"CSV compliance report saved to {csv_report_path}")


def _generate_csv_report(compliance_results: List[Dict[str, Any]], csv_report_path: str) -> None:
    """Generate CSV report from compliance results"""
    
    try:
        with open(csv_report_path, 'w', newline='') as csvfile:
            fieldnames = [
                "file_name",
                "compliance_status",
                "issues",
                "warnings",
                "missing_fields",
                "policy_expiration"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in compliance_results:
                validation = result.get('validation_results', {})
                # Flatten issues and warnings for CSV
                issues = _flatten_issues_warnings(validation)
                
                writer.writerow({
                    "file_name": result.get("file_name", ""),
                    "compliance_status": result.get("compliance_status", ""),
                    "issues": issues.get("issues", ""),
                    "warnings": issues.get("warnings", ""),
                    "missing_fields": issues.get("missing_fields", ""),
                    "policy_expiration": issues.get("policy_expiration", "")
                })
    except Exception as e:
        logger.error(f"Error generating CSV report: {e}")


def _flatten_issues_warnings(validation: Dict[str, Any]) -> Dict[str, str]:
    """Flatten issues and warnings into strings for CSV reporting"""
    
    issues = []
    warnings = []
    
    required_fields = validation.get("required_fields", {})
    if required_fields.get("status") == "fail":
        issues.extend(required_fields.get("missing_fields", []))
    
    coverage_checks = validation.get("coverage_limits", {})
    issues.extend([
        issue.get("message", "")
        for issue in coverage_checks.get("issues", [])
    ])
    
    expiration_check = validation.get("policy_expiration", {})
    exp_status = expiration_check.get("status", "")
    if exp_status == "fail":
        issues.append(expiration_check.get("message", ""))
    elif exp_status == "warning":
        warnings.append(expiration_check.get("message", ""))
    
    additional_insureds = validation.get("additional_insureds", {})
    if additional_insureds.get("status") == "fail":
        issues.append(additional_insureds.get("message", ""))
    
    return {
        "issues": "; ".join(issues),
        "warnings": "; ".join(warnings),
        "missing_fields": ", ".join(required_fields.get("missing_fields", [])),
        "policy_expiration": expiration_check.get("expiration_date", "")
    }



