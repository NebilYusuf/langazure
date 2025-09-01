import azure.functions as func
import json
import os
from datetime import datetime, timedelta

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.sharepoint_user_auth import authenticate_user, authenticate_with_token, get_current_user_info, logout_user

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Handle SharePoint user authentication."""
    
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
        if req.method == 'POST':
            # Handle login
            try:
                body = req.get_json()
                action = body.get('action')
                
                if action == 'login':
                    username = body.get('username')
                    password = body.get('password')
                    
                    if not username or not password:
                        return func.HttpResponse(
                            json.dumps({'error': 'Username and password are required'}),
                            status_code=400,
                            mimetype='application/json',
                            headers={
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                            }
                        )
                    
                    # Authenticate user
                    success = authenticate_user(username, password)
                    
                    if success:
                        # Get user info
                        user_info = get_current_user_info()
                        return func.HttpResponse(
                            json.dumps({
                                'success': True,
                                'message': 'Login successful',
                                'user': user_info
                            }),
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
                            json.dumps({
                                'success': False,
                                'error': 'Invalid username or password'
                            }),
                            status_code=401,
                            mimetype='application/json',
                            headers={
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                            }
                        )
                
                elif action == 'login_with_token':
                    access_token = body.get('access_token')
                    
                    if not access_token:
                        return func.HttpResponse(
                            json.dumps({'error': 'Access token is required'}),
                            status_code=400,
                            mimetype='application/json',
                            headers={
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                            }
                        )
                    
                    # Authenticate with token
                    success = authenticate_with_token(access_token)
                    
                    if success:
                        user_info = get_current_user_info()
                        return func.HttpResponse(
                            json.dumps({
                                'success': True,
                                'message': 'Token authentication successful',
                                'user': user_info
                            }),
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
                            json.dumps({
                                'success': False,
                                'error': 'Invalid access token'
                            }),
                            status_code=401,
                            mimetype='application/json',
                            headers={
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                            }
                        )
                
                elif action == 'logout':
                    logout_user()
                    return func.HttpResponse(
                        json.dumps({
                            'success': True,
                            'message': 'Logout successful'
                        }),
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
                        json.dumps({'error': 'Invalid action. Use: login, login_with_token, or logout'}),
                        status_code=400,
                        mimetype='application/json',
                        headers={
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                        }
                    )
                    
            except ValueError:
                return func.HttpResponse(
                    json.dumps({'error': 'Invalid JSON body'}),
                    status_code=400,
                    mimetype='application/json',
                    headers={
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                    }
                )
        
        elif req.method == 'GET':
            # Get current user info
            user_info = get_current_user_info()
            
            if user_info:
                return func.HttpResponse(
                    json.dumps({
                        'success': True,
                        'user': user_info
                    }),
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
                    json.dumps({
                        'success': False,
                        'error': 'User not authenticated'
                    }),
                    status_code=401,
                    mimetype='application/json',
                    headers={
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                    }
                )
        
        else:
            return func.HttpResponse(
                json.dumps({'error': 'Method not allowed'}),
                status_code=405,
                mimetype='application/json',
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                }
            )
            
    except Exception as error:
        print(f"SharePoint authentication error: {error}")
        return func.HttpResponse(
            json.dumps({'error': f'Authentication failed: {str(error)}'}),
            status_code=500,
            mimetype='application/json',
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        )
