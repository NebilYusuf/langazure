#!/usr/bin/env python3
"""
Startup script for SharePoint Document Manager Server
"""

import os
import sys

# Add the server directory to the Python path
server_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server')
sys.path.insert(0, server_dir)

# Import and run the SharePoint server
from app_sharepoint import app

if __name__ == '__main__':
    print("🚀 Starting SharePoint Document Manager Server...")
    print("📍 Server will be available at: http://localhost:5000")
    print("🔐 Make sure to authenticate with SharePoint first!")
    print("📁 Available folders: Boarddeck, TRC, Human Resources, Etaf Contracts, PJM, Trading Compliance")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
