# COI Compliance Flask App

from flask import Flask, jsonify, request
from utils.gemini_service import GeminiService
from config import get_config, validate_config
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
config = get_config()

# Initialize Gemini Service
gemini_service = GeminiService()

# Validate configuration on startup
if not validate_config():
    logger.error("Configuration validation failed")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check Gemini service
        gemini_status = "healthy" if gemini_service else "unhealthy"
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "gemini": gemini_status,
                "api": "healthy"
            },
            "version": config["pipeline"]["version"]
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }), 500

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API information"""
    return jsonify({
        "name": "COI Compliance Validation API",
        "version": config["pipeline"]["version"],
        "description": "API for analyzing Certificate of Insurance documents",
        "endpoints": {
            "GET /health": "Health check endpoint",
            "POST /analyze": "Analyze COI document",
            "POST /summary": "Generate COI summary"
        }
    })

@app.route('/analyze', methods=['POST'])
def analyze_document():
    """
    Endpoint to analyze a COI document
    """
    try:
        content = request.json
        document_text = content.get('document_text')
        parsed_fields = content.get('parsed_fields', {})
        
        # Perform analysis
        analysis_result = gemini_service.analyze_coi_document(document_text, parsed_fields)
        return jsonify(analysis_result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/summary', methods=['POST'])
def generate_summary():
    """
    Endpoint to generate a summary of a COI document
    """
    try:
        content = request.json
        document_text = content.get('document_text')
        compliance_results = content.get('compliance_results', {})
        
        # Generate summary
        summary_result = gemini_service.generate_summary(document_text, compliance_results)
        return jsonify(summary_result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() in ['true', '1', 't']
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.getenv('PORT', 8000)))

