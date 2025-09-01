import azure.functions as func
import json
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.sharepoint_storage import get_files_from_sharepoint, get_sharepoint_folders

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Get list of files from SharePoint folders."""
    
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
        # Get query parameters
        folder_name = req.params.get('folder')
        
        # List all files from SharePoint folders
        files = get_files_from_sharepoint(folder_name)
        
        # Add folder information
        folders = get_sharepoint_folders()
        
        response_data = {
            'files': files,
            'folders': folders,
            'totalFiles': len(files)
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
        print(f"Get files error: {error}")
        return func.HttpResponse(
            json.dumps({'error': 'Failed to get files from SharePoint'}),
            status_code=500,
            mimetype='application/json',
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        )
