# COI Compliance Validation Pipeline using ZenML

## Overview
Automated pipeline for Injala to ingest Certificate of Insurance PDFs, extract fields using OCR and NLP, validate compliance based on business rules, and generate compliance reports using ZenML for artifact tracking and reproducibility.

## Features
- **PDF Ingestion**: Automatically ingest COI PDFs from S3/local storage
- **OCR Processing**: Extract text from PDFs using EasyOCR
- **Field Parsing**: Parse policy information, limits, and expiry dates
- **Compliance Validation**: Validate against business rules
- **Report Generation**: Generate compliance reports in JSON/CSV format
- **Artifact Tracking**: Track all artifacts and runs with ZenML dashboard
- **Rapid Iteration**: Enable fast development with warp watch

## Project Structure
```
├── pipelines/           # ZenML pipeline definitions
├── steps/              # Individual pipeline steps
├── utils/              # Utility functions and helpers
├── data/               # Sample data and test files
├── reports/            # Generated compliance reports
├── requirements.txt    # Project dependencies
└── README.md          # This file
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize ZenML
```bash
zenml init
```

### 3. Create ZenML Pipeline and Steps
```bash
zenml pipeline create coi_compliance_pipeline
zenml step create ingest_step
zenml step create ocr_step
zenml step create parsing_step
zenml step create compliance_check_step
zenml step create report_step
```

### 4. Format and Lint Code
```bash
warp fmt
warp lint
```

### 5. Initialize Git Repository
```bash
git init
git add .
git commit -m "Initial commit: Injala COI compliance pipeline scaffold with ZenML using Warp CLI"
```

### 6. Start Development with Watch Mode
```bash
warp watch pipelines/coi_compliance_pipeline.py
```

## Pipeline Tasks
1. **Ingest COI PDFs** from S3/local storage
2. **OCR extraction** using EasyOCR for text extraction
3. **Parse fields** including policy details, limits, and expiry dates
4. **Validate compliance** against predefined business rules
5. **Generate compliance report** in JSON/CSV format
6. **Track artifacts and runs** with ZenML dashboard for reproducibility
7. **Enable rapid iteration** with warp watch for development

## Goals
Showcase how Injala AI/ML team can use ZenML for reproducible, scalable compliance workflows and version-controlled pipeline orchestration.

## Usage
Run the pipeline:
```bash
python pipelines/coi_compliance_pipeline.py
```

View results in ZenML dashboard:
```bash
zenml up
```
