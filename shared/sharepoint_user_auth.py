"""
SharePoint User Authentication Module
Uses interactive user login instead of app-only authentication
"""

import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
import requests
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint import files, folders

# Import text extraction modules
import sys
import os
# Add the parent directory to the Python path for Azure Functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractor.pdf_extractor import extract_text_from_pdf
from extractor.docx_extractor import extract_text_from_docx

# SharePoint Configuration
SHAREPOINT_SITE_URL = "https://cpncorp.sharepoint.com/sites/askcal"
SHAREPOINT_CLIENT_ID = os.getenv('SHAREPOINT_CLIENT_ID')
SHAREPOINT_CLIENT_SECRET = os.getenv('SHAREPOINT_CLIENT_SECRET')
SHAREPOINT_TENANT_ID = os.getenv('SHAREPOINT_TENANT_ID')

# SharePoint folders to work with
SHAREPOINT_FOLDERS = [
    "Boarddeck",
    "TRC", 
    "Human Resources",
    "Etaf Contracts",
    "PJM",
    "Trading Compliance"
]

SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.xlsx', '.xls'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

class SharePointUserAuth:
    """SharePoint authentication using user credentials"""
    
    def __init__(self, username: str = None, password: str = None):
        self.username = username
        self.password = password
        self.context = None
        self.is_authenticated = False
    
    def authenticate_with_credentials(self, username: str, password: str) -> bool:
        """Authenticate using username and password"""
        try:
            self.username = username
            self.password = password
            
            # Create user credential
            user_credential = UserCredential(username, password)
            
            # Create SharePoint context
            self.context = ClientContext(SHAREPOINT_SITE_URL).with_credentials(user_credential)
            
            # Test authentication by loading web properties
            web = self.context.web
            self.context.load(web)
            self.context.execute_query()
            
            self.is_authenticated = True
            print(f"Successfully authenticated as: {username}")
            return True
            
        except Exception as error:
            print(f"Authentication failed for {username}: {error}")
            self.is_authenticated = False
            return False
    
    def authenticate_with_token(self, access_token: str) -> bool:
        """Authenticate using an access token (for web apps)"""
        try:
            # Create context with access token
            self.context = ClientContext(SHAREPOINT_SITE_URL).with_access_token(access_token)
            
            # Test authentication
            web = self.context.web
            self.context.load(web)
            self.context.execute_query()
            
            self.is_authenticated = True
            print("Successfully authenticated with access token")
            return True
            
        except Exception as error:
            print(f"Token authentication failed: {error}")
            self.is_authenticated = False
            return False
    
    def get_context(self) -> Optional[ClientContext]:
        """Get the authenticated SharePoint context"""
        if not self.is_authenticated or not self.context:
            raise Exception("Not authenticated. Please authenticate first.")
        return self.context
    
    def is_user_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.is_authenticated

# Global authentication instance
sharepoint_auth = SharePointUserAuth()

def authenticate_user(username: str, password: str) -> bool:
    """Authenticate a user with SharePoint"""
    return sharepoint_auth.authenticate_with_credentials(username, password)

def authenticate_with_token(access_token: str) -> bool:
    """Authenticate using an access token"""
    return sharepoint_auth.authenticate_with_token(access_token)

def get_sharepoint_context() -> ClientContext:
    """Get authenticated SharePoint client context"""
    if not sharepoint_auth.is_user_authenticated():
        raise Exception("User not authenticated. Please log in first.")
    return sharepoint_auth.get_context()

def get_folder_by_name(folder_name: str):
    """Get SharePoint folder by name."""
    try:
        ctx = get_sharepoint_context()
        web = ctx.web
        ctx.load(web)
        ctx.execute_query()
        
        # Get the root folder
        root_folder = web.get_folder_by_server_relative_url("Shared Documents")
        ctx.load(root_folder)
        ctx.execute_query()
        
        # Try to get the specific folder
        try:
            folder = root_folder.folders.get_by_name(folder_name)
            ctx.load(folder)
            ctx.execute_query()
            return folder
        except:
            # Folder doesn't exist, create it
            folder = root_folder.folders.add(folder_name)
            ctx.execute_query()
            return folder
            
    except Exception as error:
        print(f"Error getting folder {folder_name}: {error}")
        return None

def generate_unique_filename(original_name: str, folder_name: str = "Shared Documents") -> str:
    """Generate a unique filename to handle duplicates in SharePoint."""
    try:
        ctx = get_sharepoint_context()
        folder = get_folder_by_name(folder_name)
        if not folder:
            return original_name
            
        ctx.load(folder.files)
        ctx.execute_query()
        
        existing_files = [f.properties['Name'] for f in folder.files]
        
        name, ext = os.path.splitext(original_name)
        counter = 1
        new_name = original_name
        
        while new_name in existing_files:
            new_name = f"{name} ({counter}){ext}"
            counter += 1
        
        return new_name
        
    except Exception as error:
        print(f"Error generating unique filename: {error}")
        return original_name

def upload_file_to_sharepoint(file_content: bytes, filename: str, folder_name: str = "Shared Documents") -> Dict[str, Any]:
    """Upload file to SharePoint folder."""
    try:
        ctx = get_sharepoint_context()
        folder = get_folder_by_name(folder_name)
        
        if not folder:
            raise Exception(f"Folder {folder_name} not found")
        
        # Upload the file
        target_file = folder.upload_file(filename, file_content)
        ctx.execute_query()
        
        return {
            'success': True,
            'filename': filename,
            'folder': folder_name,
            'url': target_file.serverRelativeUrl
        }
        
    except Exception as error:
        print(f"Error uploading file to SharePoint: {error}")
        return {
            'success': False,
            'error': str(error)
        }

def get_files_from_sharepoint(folder_name: str = None) -> List[Dict[str, Any]]:
    """Get list of files from SharePoint folder(s)."""
    try:
        ctx = get_sharepoint_context()
        files_list = []
        
        if folder_name:
            # Get files from specific folder
            folder = get_folder_by_name(folder_name)
            if folder:
                ctx.load(folder.files)
                ctx.execute_query()
                
                for file in folder.files:
                    files_list.append({
                        'id': file.properties['ServerRelativeUrl'],
                        'name': file.properties['Name'],
                        'originalName': file.properties['Name'],
                        'size': file.properties.get('Length', 0),
                        'type': file.properties.get('ContentType', 'application/octet-stream'),
                        'uploadedAt': file.properties.get('TimeCreated', datetime.utcnow()).isoformat(),
                        'lastModified': file.properties.get('TimeLastModified', datetime.utcnow()).isoformat(),
                        'folder': folder_name,
                        'url': file.properties['ServerRelativeUrl']
                    })
        else:
            # Get files from all configured folders
            for folder_name in SHAREPOINT_FOLDERS:
                folder = get_folder_by_name(folder_name)
                if folder:
                    ctx.load(folder.files)
                    ctx.execute_query()
                    
                    for file in folder.files:
                        files_list.append({
                            'id': file.properties['ServerRelativeUrl'],
                            'name': file.properties['Name'],
                            'originalName': file.properties['Name'],
                            'size': file.properties.get('Length', 0),
                            'type': file.properties.get('ContentType', 'application/octet-stream'),
                            'uploadedAt': file.properties.get('TimeCreated', datetime.utcnow()).isoformat(),
                            'lastModified': file.properties.get('TimeLastModified', datetime.utcnow()).isoformat(),
                            'folder': folder_name,
                            'url': file.properties['ServerRelativeUrl']
                        })
        
        return files_list
        
    except Exception as error:
        print(f"Error getting files from SharePoint: {error}")
        return []

def download_file_from_sharepoint(file_url: str) -> Optional[bytes]:
    """Download file content from SharePoint."""
    try:
        ctx = get_sharepoint_context()
        file = ctx.web.get_file_by_server_relative_url(file_url)
        ctx.load(file)
        ctx.execute_query()
        
        # Download file content
        response = file.download()
        ctx.execute_query()
        
        return response.content
        
    except Exception as error:
        print(f"Error downloading file from SharePoint: {error}")
        return None

def store_extracted_text(filename: str, extracted_text: str, folder_name: str = "Shared Documents") -> str:
    """Store extracted text in SharePoint as a text file."""
    try:
        text_filename = f"{filename}_extracted.txt"
        text_content = extracted_text.encode('utf-8')
        
        result = upload_file_to_sharepoint(text_content, text_filename, folder_name)
        
        if result['success']:
            print(f"Stored extracted text for {filename} in {text_filename}")
            return text_filename
        else:
            raise Exception(f"Failed to store extracted text: {result['error']}")
            
    except Exception as error:
        print(f"Error storing extracted text for {filename}: {error}")
        raise error

def get_stored_extracted_text(filename: str, folder_name: str = "Shared Documents") -> Optional[Dict[str, Any]]:
    """Retrieve stored extracted text from SharePoint."""
    try:
        text_filename = f"{filename}_extracted.txt"
        
        # Try to find the extracted text file
        ctx = get_sharepoint_context()
        folder = get_folder_by_name(folder_name)
        
        if not folder:
            return None
            
        ctx.load(folder.files)
        ctx.execute_query()
        
        # Look for the extracted text file
        text_file = None
        for file in folder.files:
            if file.properties['Name'] == text_filename:
                text_file = file
                break
        
        if not text_file:
            return None
            
        # Download the text content
        response = text_file.download()
        ctx.execute_query()
        
        extracted_text = response.content.decode('utf-8')
        
        print(f"Retrieved stored extracted text for {filename}")
        return {
            'success': True,
            'text': extracted_text,
            'source': 'cached',
            'extractedAt': datetime.utcnow().isoformat()
        }
        
    except Exception as error:
        print(f"Error retrieving stored text for {filename}: {error}")
        return None

def extract_text_from_file(file_path: str) -> Dict[str, Any]:
    """Extract text from a file using the appropriate extractor."""
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                'success': False,
                'text': '',
                'error': f'File not found: {file_path}'
            }
        
        file_extension = file_path.suffix.lower()
        
        if file_extension not in {'.pdf', '.docx', '.txt'}:
            return {
                'success': False,
                'text': '',
                'error': f'Unsupported file type for text extraction: {file_extension}'
            }
        
        # Extract text based on file type
        if file_extension == '.pdf':
            text = extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            text = extract_text_from_docx(file_path)
        elif file_extension == '.txt':
            # For text files, just read the content directly
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            return {
                'success': False,
                'text': '',
                'error': f'Unsupported file type: {file_extension}'
            }
        
        # Check if text was extracted successfully
        if not text or text.strip() == '':
            return {
                'success': False,
                'text': '',
                'error': 'No text could be extracted from the file'
            }
        
        return {
            'success': True,
            'text': text,
            'error': None
        }
        
    except Exception as error:
        print(f"Error extracting text from {file_path}: {error}")
        return {
            'success': False,
            'text': '',
            'error': f'Extraction failed: {str(error)}'
        }

def get_download_url(file_url: str) -> Dict[str, Any]:
    """Get download URL for a SharePoint file."""
    try:
        # For SharePoint, we can return the server relative URL
        # The client will need to authenticate to download
        return {
            'success': True,
            'downloadUrl': file_url,
            'expiresAt': (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
    except Exception as error:
        print(f"Download URL error: {error}")
        return {
            'success': False,
            'error': 'Failed to generate download URL'
        }

def get_sharepoint_folders() -> List[str]:
    """Get list of available SharePoint folders."""
    return SHAREPOINT_FOLDERS

def get_current_user_info() -> Optional[Dict[str, Any]]:
    """Get information about the currently authenticated user."""
    try:
        if not sharepoint_auth.is_user_authenticated():
            return None
            
        ctx = get_sharepoint_context()
        current_user = ctx.web.current_user
        ctx.load(current_user)
        ctx.execute_query()
        
        return {
            'username': current_user.properties.get('LoginName', ''),
            'displayName': current_user.properties.get('Title', ''),
            'email': current_user.properties.get('Email', ''),
            'isAuthenticated': True
        }
        
    except Exception as error:
        print(f"Error getting current user info: {error}")
        return None

def logout_user():
    """Logout the current user"""
    global sharepoint_auth
    sharepoint_auth = SharePointUserAuth()
    print("User logged out successfully")
