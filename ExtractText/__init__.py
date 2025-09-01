import azure.functions as func
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.sharepoint_storage import (
    get_stored_extracted_text, 
    extract_text_from_file, 
    store_extracted_text,
    download_file_from_sharepoint
)

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Extract text from document in SharePoint."""
    
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
        # Extract file_url from route parameters
        route_params = req.route_params
        file_url = route_params.get('file_url')
        
        if not file_url:
            return func.HttpResponse(
                json.dumps({'error': 'file_url parameter is required'}),
                status_code=400,
                mimetype='application/json'
            )
        
        # Get folder name from query parameters (default to first available folder)
        folder_name = req.params.get('folder', 'Shared Documents')
        
        # Extract filename from URL for storage purposes
        filename = Path(file_url).name
        
        # First, try to get stored extracted text
        stored_text = get_stored_extracted_text(filename, folder_name)
        
        if stored_text:
            return func.HttpResponse(
                json.dumps(stored_text),
                status_code=200,
                mimetype='application/json',
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                }
            )
        
        # If no stored text, extract from the original document
        file_content = download_file_from_sharepoint(file_url)
        
        if not file_content:
            return func.HttpResponse(
                json.dumps({'error': 'Failed to download file from SharePoint'}),
                status_code=400,
                mimetype='application/json',
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                }
            )
        
        # Download to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            # Extract text
            extraction_result = extract_text_from_file(temp_file_path)
            
            if extraction_result['success']:
                # Store the extracted text in SharePoint
                try:
                    store_extracted_text(filename, extraction_result['text'], folder_name)
                except Exception as store_error:
                    print(f"Failed to store extracted text for {filename}: {store_error}")
                
                response_data = {
                    'success': True,
                    'text': extraction_result['text'],
                    'source': 'extracted',
                    'extractedAt': datetime.utcnow().isoformat()
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
            else:
                return func.HttpResponse(
                    json.dumps({
                        'success': False,
                        'error': extraction_result['error']
                    }),
                    status_code=400,
                    mimetype='application/json',
                    headers={
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                    }
                )
                
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as error:
        print(f"Text extraction error: {error}")
        return func.HttpResponse(
            json.dumps({
                'success': False,
                'error': f'Failed to extract text: {str(error)}'
            }),
            status_code=500,
            mimetype='application/json',
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        )
