#!/usr/bin/env python3
"""
Document Upload & Viewer Backend
A Flask-based backend for document management with Azure Blob Storage
"""

import os
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions, ContentSettings
from azure.core.exceptions import ResourceNotFoundError

# Import text extraction modules
from extractor.pdf_extractor import extract_text_from_pdf
from extractor.docx_extractor import extract_text_from_docx

app = Flask(__name__)
CORS(app)

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
        
        if file_extension not in {'.pdf', '.docx'}:
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


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'azure_connected': AZURE_CONNECTION_STRING is not None
    })


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload file to Azure Blob Storage."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': 'File too large. Maximum size is 50MB'}), 400
        
        # Validate file extension
        filename = secure_filename(file.filename)
        file_ext = Path(filename).suffix.lower()
        
        if file_ext not in SUPPORTED_EXTENSIONS:
            return jsonify({'error': f'Unsupported file type: {file_ext}'}), 400
        
        # Generate unique filename
        unique_filename = generate_unique_filename(filename)
        
        # Upload to Azure
        blob_client = container_client.get_blob_client(unique_filename)
        
        # Read file content
        file_content = file.read()
        
        blob_client.upload_blob(
            file_content,
            overwrite=True,
            content_settings=ContentSettings(
                content_type=file.content_type,
                content_disposition=f'attachment; filename="{filename}"'
            ),
            metadata={
                'originalName': filename,
                'uploadedAt': datetime.utcnow().isoformat()
            }
        )
        
        return jsonify({
            'success': True,
            'blobName': unique_filename,
            'name': unique_filename,
            'originalName': filename,
            'size': file_size,
            'type': file.content_type,
            'uploadedAt': datetime.utcnow().isoformat()
        })
        
    except Exception as error:
        print(f"Upload error: {error}")
        return jsonify({'error': 'Failed to upload file'}), 500


@app.route('/api/files', methods=['GET'])
def get_files():
    """Get all files from Azure Blob Storage."""
    try:
        files = []
        
        for blob in container_client.list_blobs():
            # Skip text files in the documents_text directory
            if blob.name.startswith('documents_text/'):
                continue
            
            blob_client = container_client.get_blob_client(blob.name)
            properties = blob_client.get_blob_properties()
            
            files.append({
                'id': blob.name,
                'name': blob.name,
                'originalName': properties.metadata.get('originalName', blob.name),
                'size': blob.size,
                'type': blob.content_settings.content_type,
                'uploadedAt': properties.metadata.get('uploadedAt', blob.creation_time.isoformat()),
                'lastModified': blob.last_modified.isoformat()
            })
        
        return jsonify(files)
        
    except Exception as error:
        print(f"Error fetching files: {error}")
        return jsonify({'error': 'Failed to fetch files'}), 500


@app.route('/api/extract-text/<blob_name>', methods=['POST'])
def extract_text(blob_name):
    """Extract text from document."""
    try:
        # First, try to get stored extracted text
        stored_text = get_stored_extracted_text(blob_name)
        
        if stored_text:
            return jsonify(stored_text)
        
        # If no stored text, extract from the original document
        blob_client = container_client.get_blob_client(blob_name)
        
        # Download to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(blob_name).suffix) as temp_file:
            download_stream = blob_client.download_blob()
            temp_file.write(download_stream.readall())
            temp_file_path = temp_file.name
        
        try:
            # Extract text
            extraction_result = extract_text_from_file(temp_file_path)
            
            if extraction_result['success']:
                # Store the extracted text in Azure
                try:
                    store_extracted_text(blob_name, extraction_result['text'])
                except Exception as store_error:
                    print(f"Failed to store extracted text for {blob_name}: {store_error}")
                
                return jsonify({
                    'success': True,
                    'text': extraction_result['text'],
                    'source': 'extracted',
                    'extractedAt': datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    'success': False,
                    'error': extraction_result['error']
                }), 400
                
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as error:
        print(f"Text extraction error: {error}")
        return jsonify({
            'success': False,
            'error': f'Failed to extract text: {str(error)}'
        }), 500


@app.route('/api/save-edited-text/<blob_name>', methods=['POST'])
def save_edited_text(blob_name):
    """Save edited text to Azure Blob Storage."""
    try:
        data = request.get_json()
        text = data.get('text')
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'No text provided'
            }), 400
        
        # Store the edited text in Azure
        store_extracted_text(blob_name, text)
        
        return jsonify({
            'success': True,
            'message': 'Edited text saved successfully',
            'savedAt': datetime.utcnow().isoformat()
        })
        
    except Exception as error:
        print(f"Save edited text error: {error}")
        return jsonify({
            'success': False,
            'error': f'Failed to save edited text: {str(error)}'
        }), 500


@app.route('/api/files/<blob_name>/download', methods=['GET'])
def get_download_url(blob_name):
    """Get secure download URL for a file."""
    try:
        blob_client = container_client.get_blob_client(blob_name)
        
        # Generate SAS token for secure access
        sas_token = generate_blob_sas(
            account_name=blob_service_client.account_name,
            container_name=AZURE_CONTAINER_NAME,
            blob_name=blob_name,
            account_key=blob_service_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        
        download_url = f"{blob_client.url}?{sas_token}"
        
        return jsonify({
            'success': True,
            'downloadUrl': download_url,
            'expiresAt': (datetime.utcnow() + timedelta(hours=1)).isoformat()
        })
        
    except Exception as error:
        print(f"Download URL error: {error}")
        return jsonify({'error': 'Failed to generate download URL'}), 500


@app.route('/api/files/<blob_name>', methods=['DELETE'])
def delete_file(blob_name):
    """Delete file from Azure Blob Storage."""
    try:
        blob_client = container_client.get_blob_client(blob_name)
        
        # Delete the original document
        blob_client.delete_blob()
        
        # Also delete the extracted text if it exists
        try:
            text_blob_name = f"documents_text/{blob_name}.txt"
            text_blob_client = container_client.get_blob_client(text_blob_name)
            text_blob_client.delete_blob()
            print(f"Deleted extracted text for {blob_name}")
        except ResourceNotFoundError:
            # Text blob doesn't exist, which is fine
            print(f"No extracted text to delete for {blob_name}")
        
        return jsonify({
            'success': True,
            'message': 'File and extracted text deleted successfully'
        })
        
    except Exception as error:
        print(f"Delete error: {error}")
        return jsonify({'error': 'Failed to delete file'}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
