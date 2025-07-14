#!/usr/bin/env python3
"""
Main entry point for COI Compliance Validation Pipeline
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional

from config import get_config, validate_config
from pipelines.coi_compliance_pipeline import coi_compliance_pipeline

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_logging(log_level: str = "INFO"):
    """Configure logging for the application"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "pipeline.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def run_pipeline(
    data_path: Optional[str] = None,
    output_path: Optional[str] = None,
    rules_path: Optional[str] = None,
    enable_gemini: bool = True
):
    """Run the COI compliance validation pipeline"""
    
    logger.info("🚀 Starting COI Compliance Validation Pipeline")
    logger.info("=" * 60)
    
    # Validate configuration
    if not validate_config():
        logger.error("Configuration validation failed")
        return False
    
    # Get configuration
    config = get_config()
    
    # Use default paths if not provided
    data_path = data_path or config["pipeline"]["default_data_path"]
    output_path = output_path or config["pipeline"]["default_output_path"]
    rules_path = rules_path or config["pipeline"]["compliance_rules_path"]
    
    logger.info(f"📁 Data path: {data_path}")
    logger.info(f"📊 Output path: {output_path}")
    logger.info(f"📋 Rules path: {rules_path}")
    logger.info(f"🤖 Gemini AI: {'Enabled' if enable_gemini else 'Disabled'}")
    
    try:
        # Run the pipeline
        result = coi_compliance_pipeline(
            data_path=data_path,
            output_path=output_path,
            compliance_rules_path=rules_path
        )
        
        logger.info("✅ Pipeline executed successfully!")
        logger.info(f"📝 Pipeline Run ID: {result.id}")
        logger.info(f"🔗 Pipeline Run Name: {result.name}")
        logger.info(f"📈 Pipeline Status: {result.status}")
        
        # Check if reports were generated
        reports_path = Path(output_path)
        if reports_path.exists():
            logger.info("📊 Generated reports:")
            for report_file in reports_path.glob("*"):
                if report_file.is_file():
                    logger.info(f"  - {report_file.name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed with error: {e}")
        logger.exception("Full traceback:")
        return False

def main():
    """Main entry point with command line arguments"""
    parser = argparse.ArgumentParser(
        description="COI Compliance Validation Pipeline with AI Analysis"
    )
    
    parser.add_argument(
        "--data-path",
        type=str,
        help="Path to input COI documents (default: data/)"
    )
    
    parser.add_argument(
        "--output-path", 
        type=str,
        help="Path to save compliance reports (default: reports/)"
    )
    
    parser.add_argument(
        "--rules-path",
        type=str,
        help="Path to compliance rules JSON file (default: utils/compliance_rules.json)"
    )
    
    parser.add_argument(
        "--disable-gemini",
        action="store_true",
        help="Disable Gemini AI analysis"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Set logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Run the pipeline
    success = run_pipeline(
        data_path=args.data_path,
        output_path=args.output_path,
        rules_path=args.rules_path,
        enable_gemini=not args.disable_gemini
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
