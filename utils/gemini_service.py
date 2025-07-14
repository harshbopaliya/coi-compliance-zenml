"""
Gemini AI Service for COI Document Analysis

This service integrates Google's Gemini 2.0 model to provide AI-powered
analysis and summarization of Certificate of Insurance documents.
"""

import os
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv
import json
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiService:
    """Service class for interacting with Google Gemini AI"""
    
    def __init__(self):
        """Initialize Gemini service with API key"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        logger.info("Gemini service initialized successfully")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for COI analysis"""
        return """
        You are an expert insurance document analyzer specializing in Certificate of Insurance (COI) documents.
        Your role is to analyze COI documents and provide comprehensive insights about insurance coverage, compliance, and risk assessment.
        
        Key responsibilities:
        1. Extract and analyze insurance policy information
        2. Identify compliance issues and risks
        3. Provide clear, actionable recommendations
        4. Summarize key findings in a professional manner
        
        Guidelines:
        - Be precise and accurate in your analysis
        - Use professional insurance terminology
        - Highlight critical compliance issues
        - Provide clear explanations for non-experts
        - Focus on risk assessment and recommendations
        """
    
    def analyze_coi_document(self, document_text: str, parsed_fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a COI document using Gemini AI
        
        Args:
            document_text: Raw text extracted from the COI document
            parsed_fields: Structured data parsed from the document
            
        Returns:
            Dictionary containing AI analysis results
        """
        try:
            prompt = self._build_analysis_prompt(document_text, parsed_fields)
            response = self.model.generate_content(prompt)
            
            return {
                "analysis": response.text,
                "status": "success",
                "model": "gemini-2.0-flash-exp"
            }
        except Exception as e:
            logger.error(f"Error analyzing COI document: {e}")
            return {
                "analysis": f"Error analyzing document: {str(e)}",
                "status": "error",
                "model": "gemini-2.0-flash-exp"
            }
    
    def generate_summary(self, document_text: str, compliance_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of the COI document
        
        Args:
            document_text: Raw text extracted from the COI document
            compliance_results: Results from compliance validation
            
        Returns:
            Dictionary containing summary and recommendations
        """
        try:
            prompt = self._build_summary_prompt(document_text, compliance_results)
            response = self.model.generate_content(prompt)
            
            return {
                "summary": response.text,
                "status": "success",
                "model": "gemini-2.0-flash-exp"
            }
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {
                "summary": f"Error generating summary: {str(e)}",
                "status": "error",
                "model": "gemini-2.0-flash-exp"
            }
    
    def _build_analysis_prompt(self, document_text: str, parsed_fields: Dict[str, Any]) -> str:
        """Build the analysis prompt for Gemini"""
        return f"""
        {self.get_system_prompt()}
        
        Please analyze the following Certificate of Insurance document:
        
        DOCUMENT TEXT:
        {document_text}
        
        PARSED FIELDS:
        {json.dumps(parsed_fields, indent=2)}
        
        Please provide a comprehensive analysis including:
        1. **Document Overview**: Summary of the insurance certificate
        2. **Coverage Analysis**: Detailed review of coverage types and limits
        3. **Policy Details**: Key policy information and terms
        4. **Risk Assessment**: Potential risks and coverage gaps
        5. **Compliance Notes**: Any compliance considerations
        6. **Recommendations**: Actionable recommendations for improvement
        
        Format your response in clear sections with markdown formatting.
        """
    
    def _build_summary_prompt(self, document_text: str, compliance_results: Dict[str, Any]) -> str:
        """Build the summary prompt for Gemini"""
        return f"""
        {self.get_system_prompt()}
        
        Please generate a comprehensive summary of this Certificate of Insurance document:
        
        DOCUMENT TEXT:
        {document_text}
        
        COMPLIANCE VALIDATION RESULTS:
        {json.dumps(compliance_results, indent=2)}
        
        Please provide:
        1. **Executive Summary**: Brief overview of the document
        2. **Key Findings**: Most important discoveries from the analysis
        3. **Compliance Status**: Summary of compliance validation results
        4. **Critical Issues**: Any urgent issues that need attention
        5. **Recommendations**: Top 3-5 actionable recommendations
        6. **Next Steps**: Suggested follow-up actions
        
        Keep the summary concise but comprehensive, suitable for stakeholders and decision-makers.
        Format your response in clear sections with markdown formatting.
        """
    
    def extract_key_insights(self, document_text: str) -> List[str]:
        """
        Extract key insights from the document
        
        Args:
            document_text: Raw text from the document
            
        Returns:
            List of key insights
        """
        try:
            prompt = f"""
            {self.get_system_prompt()}
            
            Extract the top 5 key insights from this Certificate of Insurance document:
            
            {document_text}
            
            Return insights as a JSON array of strings, focusing on:
            - Critical coverage information
            - Important policy terms
            - Potential risks or gaps
            - Compliance considerations
            - Notable features or limitations
            
            Format: ["insight 1", "insight 2", "insight 3", "insight 4", "insight 5"]
            """
            
            response = self.model.generate_content(prompt)
            
            # Try to parse as JSON, fallback to text split
            try:
                insights = json.loads(response.text)
                return insights if isinstance(insights, list) else [response.text]
            except:
                # Fallback: split by lines and clean
                lines = response.text.split('\n')
                insights = [line.strip('- ').strip() for line in lines if line.strip()]
                return insights[:5]
                
        except Exception as e:
            logger.error(f"Error extracting insights: {e}")
            return [f"Error extracting insights: {str(e)}"]
