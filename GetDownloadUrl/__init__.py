import azure.functions as func
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.sharepoint_storage import get_download_url

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Get download URL for a SharePoint file."""
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
        result = get_download_url(file_url)
        
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
