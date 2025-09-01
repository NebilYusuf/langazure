import azure.functions as func
import json
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.sharepoint_storage import store_extracted_text

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Save edited text to SharePoint."""
    
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
        # Extract filename from route parameters
        route_params = req.route_params
        filename = route_params.get('filename')
        
        if not filename:
            return func.HttpResponse(
                json.dumps({'error': 'filename parameter is required'}),
                status_code=400,
                mimetype='application/json'
            )
        
        # Get folder name from query parameters (default to first available folder)
        folder_name = req.params.get('folder', 'Shared Documents')
        
        # Parse JSON body
        try:
            body = req.get_json()
            text = body.get('text')
        except ValueError:
            return func.HttpResponse(
                json.dumps({
                    'success': False,
                    'error': 'Invalid JSON body'
                }),
                status_code=400,
                mimetype='application/json'
            )
        
        if not text:
            return func.HttpResponse(
                json.dumps({
                    'success': False,
                    'error': 'No text provided'
                }),
                status_code=400,
                mimetype='application/json'
            )
        
        # Store the edited text in SharePoint
        store_extracted_text(filename, text, folder_name)
        
        response_data = {
            'success': True,
            'message': 'Edited text saved successfully to SharePoint',
            'savedAt': datetime.utcnow().isoformat(),
            'folder': folder_name
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
        print(f"Save edited text error: {error}")
        return func.HttpResponse(
            json.dumps({
                'success': False,
                'error': f'Failed to save edited text: {str(error)}'
            }),
            status_code=500,
            mimetype='application/json',
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        )
