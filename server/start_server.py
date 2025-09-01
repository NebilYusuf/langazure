#!/usr/bin/env python3
"""
Startup script for SharePoint Document Manager Server
Automatically uses SharePoint backend without Azure Blob dependencies
"""

import os
import sys
import subprocess

def main():
    print("🚀 Starting SharePoint Document Manager Server...")
    print("=" * 60)
    
    # Check if we have the required SharePoint configuration
    sharepoint_url = os.getenv('SHAREPOINT_SITE_URL')
    
    if not sharepoint_url:
        print("⚠️  Warning: SHAREPOINT_SITE_URL not set in environment")
        print("   Using default: https://cpncorp.sharepoint.com/sites/askcal")
        print("   Set SHAREPOINT_SITE_URL in your .env file if different")
        print()
    
    # Check if required packages are installed
    try:
        import office365
        print("✅ Office365-REST-Python-Client: OK")
    except ImportError:
        print("❌ Office365-REST-Python-Client not found")
        print("   Run: pip install -r server/requirements.txt")
        return
    
    try:
        import msal
        print("✅ MSAL authentication: OK")
    except ImportError:
        print("❌ MSAL not found")
        print("   Run: pip install -r server/requirements.txt")
        return
    
    print("✅ All dependencies: OK")
    print()
    
    # Start the SharePoint server
    print("📍 Starting server on: http://localhost:5000")
    print("🔐 SharePoint authentication endpoints: /api/sharepoint-auth")
    print("📁 File operations: /api/files, /api/upload, etc.")
    print("=" * 60)
    
    # Import and run the SharePoint app
    try:
        from app_sharepoint import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"❌ Error importing SharePoint app: {e}")
        print("   Make sure app_sharepoint.py exists and is properly configured")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == '__main__':
    main()
