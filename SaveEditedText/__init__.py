import azure.functions as func
import json
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.azure_storage import store_extracted_text

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Save edited text to Azure Blob Storage."""
    
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
        
        # Store the edited text in Azure
        store_extracted_text(blob_name, text)
        
        response_data = {
            'success': True,
            'message': 'Edited text saved successfully',
            'savedAt': datetime.utcnow().isoformat()
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
