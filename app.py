# COI Compliance Flask App

from flask import Flask, jsonify, request
from utils.gemini_service import GeminiService
import os

app = Flask(__name__)

# Initialize Gemini Service
gemini_service = GeminiService()

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

