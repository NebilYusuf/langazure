import azure.functions as func
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.sharepoint_storage import get_sharepoint_context, get_folder_by_name

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Delete file from SharePoint."""
    
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
                mimetype='application/json',
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                }
            )
        
        # Get folder name from query parameters (default to first available folder)
        folder_name = req.params.get('folder', 'Shared Documents')
        
        # Get SharePoint context and folder
        ctx = get_sharepoint_context()
        folder = get_folder_by_name(folder_name)
        
        if not folder:
            return func.HttpResponse(
                json.dumps({'error': f'Folder {folder_name} not found'}),
                status_code=404,
                mimetype='application/json',
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                }
            )
        
        # Load folder files
        ctx.load(folder.files)
        ctx.execute_query()
        
        # Find and delete the main file
        file_to_delete = None
        for file in folder.files:
            if file.properties['Name'] == filename:
                file_to_delete = file
                break
        
        if not file_to_delete:
            return func.HttpResponse(
                json.dumps({'error': f'File {filename} not found in folder {folder_name}'}),
                status_code=404,
                mimetype='application/json',
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                }
            )
        
        # Delete the main file
        try:
            file_to_delete.delete_object()
            ctx.execute_query()
            print(f"Successfully deleted main file: {filename}")
        except Exception as delete_error:
            print(f"Error deleting main file {filename}: {delete_error}")
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
            text_filename = f"{filename}_extracted.txt"
            text_file_to_delete = None
            
            # Reload folder files to get updated list
            ctx.load(folder.files)
            ctx.execute_query()
            
            for file in folder.files:
                if file.properties['Name'] == text_filename:
                    text_file_to_delete = file
                    break
            
            if text_file_to_delete:
                text_file_to_delete.delete_object()
                ctx.execute_query()
                print(f"Deleted extracted text for {filename}")
            else:
                print(f"No extracted text to delete for {filename}")
                
        except Exception as text_delete_error:
            # Text file deletion failed, but main file was deleted successfully
            print(f"Warning: Failed to delete extracted text for {filename}: {text_delete_error}")
        
        response_data = {
            'success': True,
            'message': 'File and extracted text deleted successfully from SharePoint',
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
        print(f"Delete error: {error}")
        return func.HttpResponse(
            json.dumps({'error': 'Failed to delete file from SharePoint'}),
            status_code=500,
            mimetype='application/json',
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        )
