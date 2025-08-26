#!/usr/bin/env python3
"""
Startup script for the Python Flask backend
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Check if Azure connection string is set
if not os.getenv('AZURE_STORAGE_CONNECTION_STRING'):
    print("❌ Error: AZURE_STORAGE_CONNECTION_STRING environment variable is not set")
    print("Please create a .env file with your Azure connection string")
    print("Example:")
    print("AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=yourstorageaccount;AccountKey=yourstoragekey;EndpointSuffix=core.windows.net")
    print("AZURE_CONTAINER_NAME=documents")
    print("PORT=5000")
    sys.exit(1)

# Import and run the Flask app
from app import app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"🚀 Starting Python Flask backend on port {port}")
    print(f"📁 Azure Container: {os.getenv('AZURE_CONTAINER_NAME', 'documents')}")
    print(f"🔗 Health check: http://localhost:{port}/api/health")
    app.run(host='0.0.0.0', port=port, debug=True)
