import azure.functions as func
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.azure_storage import (
    container_client, 
    generate_unique_filename, 
    ContentSettings, 
    MAX_FILE_SIZE, 
    SUPPORTED_EXTENSIONS
)

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Upload file to Azure Blob Storage."""
    
    # Handle CORS preflight requests
    if req.method == 'OPTIONS':
        return func.HttpResponse(
            status_code=200,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Max-Age': '86400'
            }
        )
    
    try:
        # Get the uploaded file
        uploaded_file = req.files.get('file')
        
        if not uploaded_file:
            return func.HttpResponse(
                json.dumps({'error': 'No file provided'}),
                status_code=400,
                mimetype='application/json',
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                }
            )
        
        # Generate unique filename
        original_filename = uploaded_file.filename
        unique_filename = generate_unique_filename(original_filename)
        
        # Upload to Azure Blob Storage
        blob_client = container_client.get_blob_client(unique_filename)
        
        # Read file content
        file_content = uploaded_file.read()
        
        # Upload with metadata
        blob_client.upload_blob(
            file_content,
            overwrite=True,
            metadata={
                'originalName': original_filename,
                'uploadedAt': datetime.utcnow().isoformat()
            }
        )
        
        response_data = {
            'success': True,
            'message': 'File uploaded successfully',
            'filename': unique_filename,
            'originalName': original_filename,
            'size': len(file_content)
        }
        
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype='application/json',
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        )
        
    except Exception as error:
        print(f"Upload error: {error}")
        return func.HttpResponse(
            json.dumps({'error': 'Failed to upload file'}),
            status_code=500,
            mimetype='application/json',
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        )
