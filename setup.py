"""
Setup script for the COI Compliance Validation Pipeline
"""

import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and print the result"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def main():
    """Setup the COI compliance pipeline environment"""
    
    print("🚀 Setting up COI Compliance Validation Pipeline")
    print("=" * 60)
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent
    print(f"📁 Project root: {project_root}")
    
    # Create necessary directories
    directories = ["data", "reports", "utils"]
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(exist_ok=True)
        print(f"📁 Created/verified directory: {directory}")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return 1
    
    # Initialize ZenML (if not already initialized)
    if not (project_root / ".zenml").exists():
        if not run_command("zenml init", "Initializing ZenML"):
            return 1
    else:
        print("✅ ZenML already initialized")
    
    # Download spaCy model
    if not run_command("python -m spacy download en_core_web_sm", "Downloading spaCy model"):
        print("⚠️  spaCy model download failed, but pipeline can still run with basic parsing")
    
    # Test the pipeline
    print("\n🧪 Testing the pipeline...")
    if not run_command("python test_pipeline.py", "Testing pipeline"):
        print("⚠️  Pipeline test failed, but setup is complete")
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Place your COI PDF files in the 'data/' directory")
    print("2. Run the pipeline: python pipelines/coi_compliance_pipeline.py")
    print("3. Check the results in the 'reports/' directory")
    print("4. View ZenML dashboard: zenml up")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
