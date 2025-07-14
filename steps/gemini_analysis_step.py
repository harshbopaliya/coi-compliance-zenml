"""
Gemini AI Analysis Step

This step integrates Google Gemini 2.0 to provide AI-powered analysis
and summarization of COI documents within the ZenML pipeline.
"""

from typing import List, Dict, Any
from zenml import step
from zenml.logger import get_logger
from utils.gemini_service import GeminiService

logger = get_logger(__name__)


@step
def analyze_with_gemini(
    compliance_results: List[Dict[str, Any]],
    enable_analysis: bool = True,
    enable_summary: bool = True
) -> List[Dict[str, Any]]:
    """
    Analyze COI documents using Google Gemini 2.0 AI
    
    Args:
        compliance_results: List of compliance validation results
        enable_analysis: Whether to perform detailed analysis
        enable_summary: Whether to generate summary
        
    Returns:
        List of results with AI-powered insights
    """
    
    enhanced_results = []
    
    try:
        # Initialize Gemini service
        gemini_service = GeminiService()
        logger.info("Gemini service initialized successfully")
        
        for result in compliance_results:
            logger.info(f"Analyzing document: {result['file_name']}")
            
            # Skip if there was an error in previous steps
            if result['compliance_status'] == 'error':
                enhanced_results.append({
                    **result,
                    "gemini_analysis": {
                        "status": "skipped",
                        "message": "Skipped due to previous errors"
                    }
                })
                continue
            
            # Extract document text and parsed fields
            original_metadata = result.get('original_metadata', {})
            document_text = original_metadata.get('original_metadata', {}).get('extracted_text', '')
            parsed_fields = original_metadata.get('parsed_fields', {})
            
            gemini_analysis = {}
            
            # Perform detailed analysis if enabled
            if enable_analysis:
                logger.info(f"Performing detailed analysis for {result['file_name']}")
                analysis_result = gemini_service.analyze_coi_document(document_text, parsed_fields)
                gemini_analysis['detailed_analysis'] = analysis_result
            
            # Generate summary if enabled
            if enable_summary:
                logger.info(f"Generating summary for {result['file_name']}")
                summary_result = gemini_service.generate_summary(document_text, result)
                gemini_analysis['summary'] = summary_result
            
            # Extract key insights
            logger.info(f"Extracting key insights for {result['file_name']}")
            insights = gemini_service.extract_key_insights(document_text)
            gemini_analysis['key_insights'] = insights
            
            # Add Gemini analysis to results
            enhanced_results.append({
                **result,
                "gemini_analysis": gemini_analysis
            })
            
        logger.info(f"Successfully analyzed {len(enhanced_results)} documents with Gemini")
        
    except Exception as e:
        logger.error(f"Error in Gemini analysis: {e}")
        # Return original results with error info if Gemini fails
        for result in compliance_results:
            enhanced_results.append({
                **result,
                "gemini_analysis": {
                    "status": "error",
                    "message": f"Gemini analysis failed: {str(e)}"
                }
            })
    
    return enhanced_results
