"""
Compliance Check Step

This step validates parsed insurance fields against business rules
and compliance requirements.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from zenml import step
from zenml.logger import get_logger

logger = get_logger(__name__)


@step
def validate_compliance(
    parsed_results: List[Dict[str, Any]],
    rules_path: str = "utils/compliance_rules.json"
) -> List[Dict[str, Any]]:
    """
    Validate parsed insurance fields against compliance rules
    
    Args:
        parsed_results: List of parsed insurance field dictionaries
        rules_path: Path to compliance rules JSON file
        
    Returns:
        List of dictionaries containing compliance validation results
    """
    
    compliance_results = []
    
    # Load compliance rules
    rules = _load_compliance_rules(rules_path)
    
    for result in parsed_results:
        logger.info(f"Validating compliance for {result['file_name']}")
        
        if result['parsing_status'] == 'error':
            compliance_results.append({
                "file_name": result['file_name'],
                "file_path": result['file_path'],
                "compliance_status": "error",
                "error": result.get('error', 'Unknown parsing error'),
                "validation_results": {},
                "original_metadata": result
            })
            continue
        
        # Run compliance checks
        validation_results = _run_compliance_checks(result['parsed_fields'], rules)
        
        # Determine overall compliance status
        overall_status = _determine_compliance_status(validation_results)
        
        compliance_results.append({
            "file_name": result['file_name'],
            "file_path": result['file_path'],
            "compliance_status": overall_status,
            "validation_results": validation_results,
            "original_metadata": result
        })
    
    logger.info(f"Completed compliance validation for {len(compliance_results)} documents")
    return compliance_results


def _load_compliance_rules(rules_path: str) -> Dict[str, Any]:
    """Load compliance rules from JSON file"""
    
    # Default rules if file doesn't exist
    default_rules = {
        "required_fields": [
            "policy_number",
            "insurance_company",
            "insured_name",
            "policy_period"
        ],
        "minimum_coverage_limits": {
            "general_liability": 1000000,
            "professional_liability": 1000000,
            "workers_compensation": 1000000
        },
        "policy_expiration_warning_days": 30,
        "required_additional_insureds": [],
        "required_cancellation_notice_days": 30
    }
    
    try:
        if Path(rules_path).exists():
            with open(rules_path, 'r') as f:
                rules = json.load(f)
                logger.info(f"Loaded compliance rules from {rules_path}")
        else:
            rules = default_rules
            logger.info("Using default compliance rules")
            
            # Create default rules file
            Path(rules_path).parent.mkdir(parents=True, exist_ok=True)
            with open(rules_path, 'w') as f:
                json.dump(default_rules, f, indent=2)
                logger.info(f"Created default compliance rules file at {rules_path}")
                
    except Exception as e:
        logger.error(f"Error loading compliance rules: {e}")
        rules = default_rules
    
    return rules


def _run_compliance_checks(fields: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    """Run individual compliance checks"""
    
    validation_results = {}
    
    # Check required fields
    validation_results["required_fields"] = _check_required_fields(fields, rules)
    
    # Check coverage limits
    validation_results["coverage_limits"] = _check_coverage_limits(fields, rules)
    
    # Check policy expiration
    validation_results["policy_expiration"] = _check_policy_expiration(fields, rules)
    
    # Check additional insureds
    validation_results["additional_insureds"] = _check_additional_insureds(fields, rules)
    
    # Check cancellation clause
    validation_results["cancellation_clause"] = _check_cancellation_clause(fields, rules)
    
    return validation_results


def _check_required_fields(fields: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    """Check if all required fields are present"""
    
    required_fields = rules.get("required_fields", [])
    missing_fields = []
    present_fields = []
    
    for field in required_fields:
        if field in fields and fields[field] is not None and fields[field] != "":
            present_fields.append(field)
        else:
            missing_fields.append(field)
    
    return {
        "status": "pass" if not missing_fields else "fail",
        "missing_fields": missing_fields,
        "present_fields": present_fields,
        "message": f"Missing required fields: {', '.join(missing_fields)}" if missing_fields else "All required fields present"
    }


def _check_coverage_limits(fields: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    """Check if coverage limits meet minimum requirements"""
    
    minimum_limits = rules.get("minimum_coverage_limits", {})
    coverage_limits = fields.get("coverage_limits", {})
    
    issues = []
    passed_checks = []
    
    for coverage_type, min_amount in minimum_limits.items():
        if coverage_type in coverage_limits:
            # Extract numeric value from coverage limit string
            limit_value = _extract_numeric_value(coverage_limits[coverage_type])
            
            if limit_value and limit_value >= min_amount:
                passed_checks.append({
                    "coverage_type": coverage_type,
                    "current_limit": limit_value,
                    "minimum_required": min_amount
                })
            else:
                issues.append({
                    "coverage_type": coverage_type,
                    "current_limit": limit_value or 0,
                    "minimum_required": min_amount,
                    "message": f"Coverage limit ${limit_value or 0:,} is below minimum ${min_amount:,}"
                })
        else:
            issues.append({
                "coverage_type": coverage_type,
                "current_limit": 0,
                "minimum_required": min_amount,
                "message": f"Required coverage type '{coverage_type}' not found"
            })
    
    return {
        "status": "pass" if not issues else "fail",
        "issues": issues,
        "passed_checks": passed_checks,
        "message": f"Coverage limit issues: {len(issues)}" if issues else "All coverage limits meet requirements"
    }


def _check_policy_expiration(fields: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    """Check policy expiration date"""
    
    warning_days = rules.get("policy_expiration_warning_days", 30)
    policy_period = fields.get("policy_period", {})
    expiration_date_str = policy_period.get("expiration_date")
    
    if not expiration_date_str:
        return {
            "status": "fail",
            "message": "No expiration date found",
            "expiration_date": None,
            "days_until_expiration": None
        }
    
    try:
        # Parse expiration date
        expiration_date = _parse_date(expiration_date_str)
        
        if expiration_date:
            today = datetime.now().date()
            days_until_expiration = (expiration_date - today).days
            
            if days_until_expiration < 0:
                status = "fail"
                message = f"Policy expired {abs(days_until_expiration)} days ago"
            elif days_until_expiration <= warning_days:
                status = "warning"
                message = f"Policy expires in {days_until_expiration} days"
            else:
                status = "pass"
                message = f"Policy expires in {days_until_expiration} days"
            
            return {
                "status": status,
                "message": message,
                "expiration_date": expiration_date.isoformat(),
                "days_until_expiration": days_until_expiration
            }
        else:
            return {
                "status": "fail",
                "message": f"Unable to parse expiration date: {expiration_date_str}",
                "expiration_date": expiration_date_str,
                "days_until_expiration": None
            }
            
    except Exception as e:
        return {
            "status": "fail",
            "message": f"Error checking expiration date: {e}",
            "expiration_date": expiration_date_str,
            "days_until_expiration": None
        }


def _check_additional_insureds(fields: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    """Check for required additional insureds"""
    
    required_insureds = rules.get("required_additional_insureds", [])
    additional_insureds = fields.get("additional_insureds", [])
    
    if not required_insureds:
        return {
            "status": "pass",
            "message": "No additional insureds required",
            "required": [],
            "found": additional_insureds
        }
    
    missing_insureds = []
    for required in required_insureds:
        found = False
        for actual in additional_insureds:
            if required.lower() in actual.lower():
                found = True
                break
        if not found:
            missing_insureds.append(required)
    
    return {
        "status": "pass" if not missing_insureds else "fail",
        "message": f"Missing additional insureds: {', '.join(missing_insureds)}" if missing_insureds else "All required additional insureds present",
        "required": required_insureds,
        "found": additional_insureds,
        "missing": missing_insureds
    }


def _check_cancellation_clause(fields: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    """Check cancellation clause requirements"""
    
    required_notice_days = rules.get("required_cancellation_notice_days", 30)
    cancellation_clause = fields.get("cancellation_clause")
    
    if not cancellation_clause:
        return {
            "status": "fail",
            "message": "No cancellation clause found",
            "required_notice_days": required_notice_days,
            "found_notice_days": None
        }
    
    # Extract notice days from clause
    import re
    match = re.search(r"(\d+)\s*days?", cancellation_clause, re.IGNORECASE)
    
    if match:
        found_notice_days = int(match.group(1))
        
        if found_notice_days >= required_notice_days:
            return {
                "status": "pass",
                "message": f"Cancellation notice requirement met: {found_notice_days} days",
                "required_notice_days": required_notice_days,
                "found_notice_days": found_notice_days
            }
        else:
            return {
                "status": "fail",
                "message": f"Insufficient cancellation notice: {found_notice_days} days (required: {required_notice_days})",
                "required_notice_days": required_notice_days,
                "found_notice_days": found_notice_days
            }
    else:
        return {
            "status": "fail",
            "message": "Unable to determine cancellation notice period",
            "required_notice_days": required_notice_days,
            "found_notice_days": None
        }


def _determine_compliance_status(validation_results: Dict[str, Any]) -> str:
    """Determine overall compliance status"""
    
    has_failures = False
    has_warnings = False
    
    for check_name, check_result in validation_results.items():
        status = check_result.get("status", "unknown")
        
        if status == "fail":
            has_failures = True
        elif status == "warning":
            has_warnings = True
    
    if has_failures:
        return "non_compliant"
    elif has_warnings:
        return "compliant_with_warnings"
    else:
        return "compliant"


def _extract_numeric_value(value_str: str) -> Optional[int]:
    """Extract numeric value from string like '$1,000,000'"""
    if not value_str:
        return None
    
    import re
    # Remove currency symbols and commas, extract first number
    numbers = re.findall(r'[\d,]+', str(value_str))
    if numbers:
        try:
            return int(numbers[0].replace(',', ''))
        except ValueError:
            return None
    return None


def _parse_date(date_str: str) -> Optional[datetime.date]:
    """Parse date string into datetime.date object"""
    if not date_str:
        return None
    
    # Common date formats
    formats = [
        "%m/%d/%Y",
        "%m-%d-%Y",
        "%m/%d/%y",
        "%m-%d-%y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    
    return None
