import azure.functions as func
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.azure_storage import (
    container_client, 
    get_stored_extracted_text, 
    extract_text_from_file, 
    store_extracted_text
)

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Extract text from document."""
    
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
        # Extract blob_name from route parameters
        route_params = req.route_params
        blob_name = route_params.get('blob_name')
        
        if not blob_name:
            return func.HttpResponse(
                json.dumps({'error': 'blob_name parameter is required'}),
                status_code=400,
                mimetype='application/json'
            )
        # First, try to get stored extracted text
        stored_text = get_stored_extracted_text(blob_name)
        
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
