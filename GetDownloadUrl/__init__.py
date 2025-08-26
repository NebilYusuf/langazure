import azure.functions as func
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.azure_storage import get_download_url

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Get secure download URL for a file."""
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
        result = get_download_url(blob_name)
        
        if result['success']:
            return func.HttpResponse(
                json.dumps(result),
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
                json.dumps(result),
                status_code=500,
                mimetype='application/json',
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                }
            )
        
    except Exception as error:
        print(f"Download URL error: {error}")
        return func.HttpResponse(
            json.dumps({'error': 'Failed to generate download URL'}),
            status_code=500,
            mimetype='application/json'
        )
