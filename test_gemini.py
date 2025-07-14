"""
Test script for Gemini AI integration with COI document analysis
"""

import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
load_dotenv()

from utils.gemini_service import GeminiService

def test_gemini_analysis():
    """Test Gemini analysis with the demo COI document"""
    
    print("🤖 Testing Gemini AI Analysis")
    print("=" * 60)
    
    # Check if API key is set
    if not os.getenv('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY') == 'your_gemini_api_key_here':
        print("❌ Please set your actual Gemini API key in the .env file")
        return 1
    
    try:
        # Initialize Gemini service
        gemini_service = GeminiService()
        print("✅ Gemini service initialized successfully")
        
        # Read the demo COI document
        demo_file_path = Path("data/sample_coi.txt")
        if not demo_file_path.exists():
            print(f"❌ Demo file not found: {demo_file_path}")
            return 1
        
        with open(demo_file_path, 'r', encoding='utf-8') as f:
            document_text = f.read()
        
        print(f"📄 Loaded document: {demo_file_path.name}")
        print(f"📏 Document length: {len(document_text)} characters")
        
        # Sample parsed fields (from previous analysis)
        parsed_fields = {
            "policy_number": "SF-2024-001234",
            "insurance_company": "State Farm Insurance Company",
            "insured_name": "ABC Construction LLC",
            "policy_period": {
                "effective_date": "01/01/2024",
                "expiration_date": "01/01/2025"
            },
            "coverage_limits": {
                "general_liability": "$2,000,000",
                "professional_liability": "$1,000,000",
                "workers_compensation": "$1,000,000"
            },
            "certificate_holder": "Injala LLC",
            "additional_insureds": ["Injala LLC as additional insured"],
            "cancellation_clause": "30 days written notice"
        }
        
        # Test 1: Document Analysis
        print("\n🔍 Testing Document Analysis...")
        analysis_result = gemini_service.analyze_coi_document(document_text, parsed_fields)
        
        if analysis_result['status'] == 'success':
            print("✅ Document analysis completed successfully")
            print(f"📊 Analysis length: {len(analysis_result['analysis'])} characters")
            
            # Save analysis to file
            analysis_file = Path("reports/gemini_analysis.md")
            analysis_file.parent.mkdir(exist_ok=True)
            with open(analysis_file, 'w', encoding='utf-8') as f:
                f.write(analysis_result['analysis'])
            print(f"💾 Analysis saved to: {analysis_file}")
            
            # Display first 500 characters
            print("\n📝 Analysis Preview:")
            print("-" * 50)
            print(analysis_result['analysis'][:500] + "..." if len(analysis_result['analysis']) > 500 else analysis_result['analysis'])
            print("-" * 50)
        else:
            print(f"❌ Document analysis failed: {analysis_result['analysis']}")
        
        # Test 2: Summary Generation
        print("\n📋 Testing Summary Generation...")
        
        # Sample compliance results
        compliance_results = {
            "compliance_status": "non_compliant",
            "validation_results": {
                "required_fields": {"status": "pass"},
                "coverage_limits": {"status": "fail", "message": "Workers compensation coverage not found"},
                "policy_expiration": {"status": "fail", "message": "No expiration date found"}
            }
        }
        
        summary_result = gemini_service.generate_summary(document_text, compliance_results)
        
        if summary_result['status'] == 'success':
            print("✅ Summary generation completed successfully")
            print(f"📊 Summary length: {len(summary_result['summary'])} characters")
            
            # Save summary to file
            summary_file = Path("reports/gemini_summary.md")
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_result['summary'])
            print(f"💾 Summary saved to: {summary_file}")
            
            # Display first 500 characters
            print("\n📝 Summary Preview:")
            print("-" * 50)
            print(summary_result['summary'][:500] + "..." if len(summary_result['summary']) > 500 else summary_result['summary'])
            print("-" * 50)
        else:
            print(f"❌ Summary generation failed: {summary_result['summary']}")
        
        # Test 3: Key Insights Extraction
        print("\n💡 Testing Key Insights Extraction...")
        insights = gemini_service.extract_key_insights(document_text)
        
        if insights and not insights[0].startswith("Error"):
            print("✅ Key insights extraction completed successfully")
            print(f"📊 Number of insights: {len(insights)}")
            
            # Save insights to file
            insights_file = Path("reports/gemini_insights.json")
            with open(insights_file, 'w', encoding='utf-8') as f:
                json.dump(insights, f, indent=2)
            print(f"💾 Insights saved to: {insights_file}")
            
            print("\n💡 Key Insights:")
            for i, insight in enumerate(insights, 1):
                print(f"  {i}. {insight}")
        else:
            print(f"❌ Key insights extraction failed: {insights}")
        
        print("\n🎉 Gemini AI testing completed successfully!")
        print("\nGenerated files:")
        print("- reports/gemini_analysis.md - Full document analysis")
        print("- reports/gemini_summary.md - Executive summary")
        print("- reports/gemini_insights.json - Key insights")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error testing Gemini: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_gemini_analysis())
