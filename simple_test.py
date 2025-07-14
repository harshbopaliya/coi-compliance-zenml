"""
Simple test script for the COI Compliance Validation Pipeline
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from pipelines.coi_compliance_pipeline import coi_compliance_pipeline

def main():
    """Run the COI compliance pipeline with test data"""
    
    print("🚀 Starting COI Compliance Validation Pipeline Test")
    print("=" * 60)
    
    try:
        # Run the pipeline with test configuration
        pipeline = coi_compliance_pipeline(
            data_path="data/",
            output_path="reports/",
            compliance_rules_path="utils/compliance_rules.json"
        )
        
        # Execute the pipeline
        pipeline.run()
        
        print("\n✅ Pipeline executed successfully!")
        
        # Check if reports were generated
        reports_path = Path("reports/")
        if reports_path.exists():
            print(f"\n📊 Generated reports:")
            for report_file in reports_path.glob("*"):
                print(f"  - {report_file.name}")
                
        print("\n🎉 Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
