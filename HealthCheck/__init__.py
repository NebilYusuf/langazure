import azure.functions as func
import json
import os
from datetime import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint."""
    try:
        azure_connected = os.getenv('AZURE_STORAGE_CONNECTION_STRING') is not None
        
        response_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'azure_connected': azure_connected
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
        
    except Exception as e:
        return func.HttpResponse(
            json.dumps({'error': str(e)}),
            status_code=500,
            mimetype='application/json'
        )
