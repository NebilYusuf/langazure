import azure.functions as func
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.sharepoint_storage import (
    upload_file_to_sharepoint,
    generate_unique_filename,
    MAX_FILE_SIZE,
    SUPPORTED_EXTENSIONS,
    get_sharepoint_folders
)

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Upload file to SharePoint folder."""
    
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
        
        # Get folder parameter (default to first available folder)
        folder_name = req.form.get('folder', get_sharepoint_folders()[0] if get_sharepoint_folders() else 'Shared Documents')
        
        # Validate folder
        if folder_name not in get_sharepoint_folders():
            return func.HttpResponse(
                json.dumps({'error': f'Invalid folder. Must be one of: {", ".join(get_sharepoint_folders())}'}),
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
        unique_filename = generate_unique_filename(original_filename, folder_name)
        
        # Read file content
        file_content = uploaded_file.read()
        
        # Check file size
        if len(file_content) > MAX_FILE_SIZE:
            return func.HttpResponse(
                json.dumps({'error': f'File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024):.1f}MB'}),
                status_code=400,
                mimetype='application/json',
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                }
            )
        
        # Upload to SharePoint
        result = upload_file_to_sharepoint(file_content, unique_filename, folder_name)
        
        if not result['success']:
            return func.HttpResponse(
                json.dumps({'error': f'Failed to upload file: {result["error"]}'}),
                status_code=500,
                mimetype='application/json',
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                }
            )
        
        response_data = {
            'success': True,
            'message': 'File uploaded successfully to SharePoint',
            'filename': unique_filename,
            'originalName': original_filename,
            'folder': folder_name,
            'size': len(file_content),
            'url': result.get('url', '')
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
            json.dumps({'error': 'Failed to upload file to SharePoint'}),
            status_code=500,
            mimetype='application/json',
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        )
