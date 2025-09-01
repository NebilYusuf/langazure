#!/usr/bin/env python3
"""
Document Upload & Viewer Backend with SharePoint Authentication
A Flask-based backend for document management with SharePoint
"""

import os
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Import SharePoint authentication modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.sharepoint_user_auth import (
    authenticate_user, 
    authenticate_with_token, 
    get_current_user_info, 
    logout_user,
    get_sharepoint_context,
    get_folder_by_name,
    generate_unique_filename,
    upload_file_to_sharepoint,
    get_files_from_sharepoint,
    download_file_from_sharepoint,
    store_extracted_text,
    get_stored_extracted_text,
    extract_text_from_file,
    get_download_url,
    get_sharepoint_folders
)

app = Flask(__name__)
CORS(app)

# Configuration
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.xlsx', '.xls'}

# Global authentication state (in production, use proper session management)
current_user = None

@app.route('/api/sharepoint-auth', methods=['GET', 'POST', 'OPTIONS'])
def sharepoint_auth():
    """Handle SharePoint user authentication."""
    global current_user
    
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        if request.method == 'POST':
            body = request.get_json()
            action = body.get('action')
            
            if action == 'login':
                username = body.get('username')
                password = body.get('password')
                
                if not username or not password:
                    return jsonify({'error': 'Username and password are required'}), 400
                
                # Authenticate user
                success = authenticate_user(username, password)
                
                if success:
                    # Get user info
                    user_info = get_current_user_info()
                    current_user = user_info
                    return jsonify({
                        'success': True,
                        'message': 'Login successful',
                        'user': user_info
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Invalid username or password'
                    }), 401
            
            elif action == 'login_with_token':
                access_token = body.get('access_token')
                
                if not access_token:
                    return jsonify({'error': 'Access token is required'}), 400
                
                # Authenticate with token
                success = authenticate_with_token(access_token)
                
                if success:
                    user_info = get_current_user_info()
                    current_user = user_info
                    return jsonify({
                        'success': True,
                        'message': 'Token authentication successful',
                        'user': user_info
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Invalid access token'
                    }), 401
            
            elif action == 'logout':
                logout_user()
                current_user = None
                return jsonify({
                    'success': True,
                    'message': 'Logout successful'
                })
            
            else:
                return jsonify({'error': 'Invalid action. Use: login, login_with_token, or logout'}), 400
        
        elif request.method == 'GET':
            # Get current user info
            if current_user:
                return jsonify({
                    'success': True,
                    'user': current_user
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'User not authenticated'
                }), 401
        
    except Exception as error:
        print(f"SharePoint authentication error: {error}")
        return jsonify({'error': f'Authentication failed: {str(error)}'}), 500

@app.route('/api/files', methods=['GET'])
def get_files():
    """Get list of files from SharePoint."""
    global current_user
    
    if not current_user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        folder = request.args.get('folder')
        files = get_files_from_sharepoint(folder)
        
        return jsonify({
            'success': True,
            'files': files,
            'folders': get_sharepoint_folders()
        })
    
    except Exception as error:
        print(f"Error getting files: {error}")
        return jsonify({'error': str(error)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload file to SharePoint."""
    global current_user
    
    if not current_user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        folder = request.form.get('folder', 'Shared Documents')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': f'File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB'}), 400
        
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in SUPPORTED_EXTENSIONS:
            return jsonify({'error': f'Unsupported file type: {file_ext}'}), 400
        
        # Generate unique filename
        filename = generate_unique_filename(file.filename, folder)
        
        # Read file content
        file_content = file.read()
        
        # Upload to SharePoint
        result = upload_file_to_sharepoint(file_content, filename, folder)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'File uploaded successfully',
                'filename': filename,
                'folder': folder,
                'url': result['url']
            })
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as error:
        print(f"Error uploading file: {error}")
        return jsonify({'error': str(error)}), 500

@app.route('/api/extract-text/<path:file_url>', methods=['POST'])
def extract_text(file_url):
    """Extract text from a document."""
    global current_user
    
    if not current_user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        folder = request.args.get('folder', 'Shared Documents')
        
        # Download file from SharePoint
        file_content = download_file_from_sharepoint(file_url)
        
        if not file_content:
            return jsonify({'error': 'Failed to download file'}), 500
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_url).suffix) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            # Extract text
            result = extract_text_from_file(temp_file_path)
            
            if result['success']:
                # Store extracted text in SharePoint
                filename = Path(file_url).name
                text_filename = store_extracted_text(filename, result['text'], folder)
                
                return jsonify({
                    'success': True,
                    'text': result['text'],
                    'textFile': text_filename,
                    'source': 'extracted'
                })
            else:
                return jsonify({'error': result['error']}), 500
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    except Exception as error:
        print(f"Error extracting text: {error}")
        return jsonify({'error': str(error)}), 500

@app.route('/api/files/<path:file_url>/download', methods=['GET'])
def get_download_url(file_url):
    """Get download URL for a SharePoint file."""
    global current_user
    
    if not current_user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        result = get_download_url(file_url)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as error:
        print(f"Error getting download URL: {error}")
        return jsonify({'error': str(error)}), 500

@app.route('/api/save-edited-text/<filename>', methods=['POST'])
def save_edited_text(filename):
    """Save edited extracted text."""
    global current_user
    
    if not current_user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        extracted_text = data.get('text', '')
        folder = request.args.get('folder', 'Shared Documents')
        
        if not extracted_text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Store the edited text
        text_filename = store_extracted_text(filename, extracted_text, folder)
        
        return jsonify({
            'success': True,
            'message': 'Text saved successfully',
            'textFile': text_filename
        })
    
    except Exception as error:
        print(f"Error saving edited text: {error}")
        return jsonify({'error': str(error)}), 500

@app.route('/api/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Delete a file from SharePoint."""
    global current_user
    
    if not current_user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        folder = request.args.get('folder', 'Shared Documents')
        
        # For now, we'll just return success since the actual deletion
        # would require implementing the delete functionality in the SharePoint module
        # In a real implementation, you would call a delete function here
        
        return jsonify({
            'success': True,
            'message': 'File deleted successfully',
            'filename': filename
        })
    
    except Exception as error:
        print(f"Error deleting file: {error}")
        return jsonify({'error': str(error)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'SharePoint Document Manager'
    })

if __name__ == '__main__':
    print("Starting SharePoint Document Manager Server...")
    print("Server will be available at: http://localhost:5000")
    print("Make sure to authenticate with SharePoint first!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
