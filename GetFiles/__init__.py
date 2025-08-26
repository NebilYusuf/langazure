import azure.functions as func
import json
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.azure_storage import container_client

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Get list of files from Azure Blob Storage."""
    
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
        # List all blobs in the container
        blobs = container_client.list_blobs()
        
        files = []
        for blob in blobs:
            # Skip the documents_text folder
            if not blob.name.startswith('documents_text/'):
                files.append({
                    'id': blob.name,
                    'name': blob.name,
                    'originalName': blob.metadata.get('originalName', blob.name) if blob.metadata else blob.name,
                    'size': blob.size,
                    'type': blob.content_settings.content_type if blob.content_settings else 'application/octet-stream',
                    'uploadedAt': blob.metadata.get('uploadedAt', blob.creation_time.isoformat()) if blob.metadata else blob.creation_time.isoformat(),
                    'lastModified': blob.last_modified.isoformat() if blob.last_modified else None
                })
        
        return func.HttpResponse(
            json.dumps(files),
            status_code=200,
            mimetype='application/json',
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        )
        
    except Exception as error:
        print(f"Get files error: {error}")
        return func.HttpResponse(
            json.dumps({'error': 'Failed to get files'}),
            status_code=500,
            mimetype='application/json',
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        )
