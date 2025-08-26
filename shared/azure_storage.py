"""
Shared Azure Storage utilities for Azure Functions
"""

import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions, ContentSettings
from azure.core.exceptions import ResourceNotFoundError

# Import text extraction modules
import sys
import os
# Add the parent directory to the Python path for Azure Functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractor.pdf_extractor import extract_text_from_pdf
from extractor.docx_extractor import extract_text_from_docx

# Configuration
AZURE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
AZURE_CONTAINER_NAME = os.getenv('AZURE_CONTAINER_NAME', 'documents')
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Initialize Azure Blob Service Client
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)

# Ensure container exists
try:
    container_client.get_container_properties()
except ResourceNotFoundError:
    container_client.create_container()
    print(f"Created container: {AZURE_CONTAINER_NAME}")

SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.xlsx', '.xls'}


def generate_unique_filename(original_name: str) -> str:
    """Generate a unique filename to handle duplicates."""
    name, ext = os.path.splitext(original_name)
    counter = 1
    new_name = original_name
    
    while True:
        try:
            # Check if blob exists
            blob_client = container_client.get_blob_client(new_name)
            blob_client.get_blob_properties()
            # If we get here, the blob exists, so increment the counter
            new_name = f"{name} ({counter}){ext}"
            counter += 1
        except ResourceNotFoundError:
            # Blob doesn't exist, we can use this name
            break
    
    return new_name


def store_extracted_text(blob_name: str, extracted_text: str) -> str:
    """Store extracted text in Azure Blob Storage."""
    try:
        text_blob_name = f"documents_text/{blob_name}.txt"
        blob_client = container_client.get_blob_client(text_blob_name)
        
        # Store the extracted text
        blob_client.upload_blob(
            extracted_text,
            overwrite=True,
            content_settings=ContentSettings(
                content_type='text/plain',
                content_disposition=f'attachment; filename="{blob_name}.txt"'
            ),
            metadata={
                'originalDocument': blob_name,
                'extractedAt': datetime.utcnow().isoformat(),
                'contentType': 'extracted_text'
            }
        )
        
        print(f"Stored extracted text for {blob_name} in {text_blob_name}")
        return text_blob_name
    except Exception as error:
        print(f"Error storing extracted text for {blob_name}: {error}")
        raise error


def get_stored_extracted_text(blob_name: str) -> Optional[Dict[str, Any]]:
    """Retrieve stored extracted text from Azure Blob Storage."""
    try:
        text_blob_name = f"documents_text/{blob_name}.txt"
        blob_client = container_client.get_blob_client(text_blob_name)
        
        # Check if the text blob exists
        properties = blob_client.get_blob_properties()
        
        # Download the stored text
        download_stream = blob_client.download_blob()
        extracted_text = download_stream.readall().decode('utf-8')
        
        print(f"Retrieved stored extracted text for {blob_name}")
        return {
            'success': True,
            'text': extracted_text,
            'source': 'cached',
            'extractedAt': properties.metadata.get('extractedAt', datetime.utcnow().isoformat())
        }
    except ResourceNotFoundError:
        print(f"No stored extracted text found for {blob_name}")
        return None
    except Exception as error:
        print(f"Error retrieving stored text for {blob_name}: {error}")
        return None


def extract_text_from_file(file_path: str) -> Dict[str, Any]:
    """Extract text from a file using the appropriate extractor."""
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                'success': False,
                'text': '',
                'error': f'File not found: {file_path}'
            }
        
        file_extension = file_path.suffix.lower()
        
        if file_extension not in {'.pdf', '.docx', '.txt'}:
            return {
                'success': False,
                'text': '',
                'error': f'Unsupported file type for text extraction: {file_extension}'
            }
        
        # Extract text based on file type
        if file_extension == '.pdf':
            text = extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            text = extract_text_from_docx(file_path)
        elif file_extension == '.txt':
            # For text files, just read the content directly
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            return {
                'success': False,
                'text': '',
                'error': f'Unsupported file type: {file_extension}'
            }
        
        # Check if text was extracted successfully
        if not text or text.strip() == '':
            return {
                'success': False,
                'text': '',
                'error': 'No text could be extracted from the file'
            }
        
        return {
            'success': True,
            'text': text,
            'error': None
        }
        
    except Exception as error:
        print(f"Error extracting text from {file_path}: {error}")
        return {
            'success': False,
            'text': '',
            'error': f'Extraction failed: {str(error)}'
        }


def get_download_url(blob_name: str) -> Dict[str, Any]:
    """Get secure download URL for a file."""
    try:
        blob_client = container_client.get_blob_client(blob_name)
        
        # Since we're using a connection string with SAS token, 
        # we can use the blob URL directly with the existing SAS token
        # Extract the SAS token from the connection string
        connection_string = AZURE_CONNECTION_STRING
        if 'SharedAccessSignature=' in connection_string:
            # Extract the SAS token part
            sas_part = connection_string.split('SharedAccessSignature=')[1]
            download_url = f"{blob_client.url}?{sas_part}"
        else:
            # Fallback: try to generate a new SAS token
            try:
                sas_token = generate_blob_sas(
                    account_name=blob_service_client.account_name,
                    container_name=AZURE_CONTAINER_NAME,
                    blob_name=blob_name,
                    account_key=blob_service_client.credential.account_key,
                    permission=BlobSasPermissions(read=True),
                    expiry=datetime.utcnow() + timedelta(hours=1)
                )
                download_url = f"{blob_client.url}?{sas_token}"
            except Exception:
                # If SAS generation fails, return the blob URL without SAS
                download_url = blob_client.url
        
        return {
            'success': True,
            'downloadUrl': download_url,
            'expiresAt': (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
    except Exception as error:
        print(f"Download URL error: {error}")
        return {
            'success': False,
            'error': 'Failed to generate download URL'
        }
