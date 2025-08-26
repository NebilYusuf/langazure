import azure.functions as func
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.azure_storage import container_client
from azure.core.exceptions import ResourceNotFoundError

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Delete file from Azure Blob Storage."""
    
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
                mimetype='application/json',
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                }
            )
        
        blob_client = container_client.get_blob_client(blob_name)
        
        # Delete the original document
        try:
            blob_client.delete_blob()
            print(f"Successfully deleted main blob: {blob_name}")
        except Exception as delete_error:
            print(f"Error deleting main blob {blob_name}: {delete_error}")
            return func.HttpResponse(
                json.dumps({
                    'success': False,
                    'error': f'Failed to delete main file: {str(delete_error)}'
                }),
                status_code=500,
                mimetype='application/json',
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                }
            )
        
        # Also delete the extracted text if it exists
        try:
            text_blob_name = f"documents_text/{blob_name}.txt"
            text_blob_client = container_client.get_blob_client(text_blob_name)
            text_blob_client.delete_blob()
            print(f"Deleted extracted text for {blob_name}")
        except ResourceNotFoundError:
            # Text blob doesn't exist, which is fine
            print(f"No extracted text to delete for {blob_name}")
        
        response_data = {
            'success': True,
            'message': 'File and extracted text deleted successfully'
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
        print(f"Delete error: {error}")
        return func.HttpResponse(
            json.dumps({'error': 'Failed to delete file'}),
            status_code=500,
            mimetype='application/json',
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        )
