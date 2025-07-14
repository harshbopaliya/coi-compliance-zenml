"""
PDF Ingestion Step

This step handles ingesting COI PDF files from various sources:
- Local file system
- S3 bucket
- Other cloud storage providers
"""

import os
from typing import List, Dict, Any
from pathlib import Path
from zenml import step
from zenml.logger import get_logger
import boto3
from botocore.exceptions import ClientError

logger = get_logger(__name__)


@step
def ingest_coi_pdfs(
    data_path: str,
    s3_bucket: str = None,
    s3_prefix: str = "coi-pdfs/",
    file_extensions: List[str] = [".pdf"]
) -> List[Dict[str, Any]]:
    """
    Ingest COI PDF files from local storage or S3
    
    Args:
        data_path: Local path to PDF files
        s3_bucket: Optional S3 bucket name
        s3_prefix: S3 prefix for PDF files
        file_extensions: List of allowed file extensions
        
    Returns:
        List of dictionaries containing file metadata
    """
    
    pdf_files = []
    
    # Ingest from local file system
    if os.path.exists(data_path):
        logger.info(f"Ingesting PDFs from local path: {data_path}")
        pdf_files.extend(_ingest_local_files(data_path, file_extensions))
    
    # Ingest from S3 if bucket is specified
    if s3_bucket:
        logger.info(f"Ingesting PDFs from S3 bucket: {s3_bucket}")
        pdf_files.extend(_ingest_s3_files(s3_bucket, s3_prefix, file_extensions))
    
    logger.info(f"Successfully ingested {len(pdf_files)} PDF files")
    return pdf_files


def _ingest_local_files(data_path: str, file_extensions: List[str]) -> List[Dict[str, Any]]:
    """Ingest PDF files from local file system"""
    pdf_files = []
    data_dir = Path(data_path)
    
    for file_path in data_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in file_extensions:
            pdf_files.append({
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
                "source": "local",
                "last_modified": file_path.stat().st_mtime
            })
    
    return pdf_files


def _ingest_s3_files(s3_bucket: str, s3_prefix: str, file_extensions: List[str]) -> List[Dict[str, Any]]:
    """Ingest PDF files from S3 bucket"""
    pdf_files = []
    
    try:
        s3_client = boto3.client('s3')
        
        # List objects in S3 bucket with prefix
        response = s3_client.list_objects_v2(
            Bucket=s3_bucket,
            Prefix=s3_prefix
        )
        
        if 'Contents' in response:
            for obj in response['Contents']:
                key = obj['Key']
                file_extension = Path(key).suffix.lower()
                
                if file_extension in file_extensions:
                    # Download file to local temp directory
                    local_path = f"/tmp/{Path(key).name}"
                    s3_client.download_file(s3_bucket, key, local_path)
                    
                    pdf_files.append({
                        "file_path": local_path,
                        "file_name": Path(key).name,
                        "file_size": obj['Size'],
                        "source": "s3",
                        "s3_bucket": s3_bucket,
                        "s3_key": key,
                        "last_modified": obj['LastModified'].timestamp()
                    })
        
    except ClientError as e:
        logger.error(f"Error accessing S3 bucket {s3_bucket}: {e}")
        raise
    
    return pdf_files
