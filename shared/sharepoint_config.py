"""
SharePoint Configuration for the Document Manager
"""

import os

# SharePoint Site Configuration
SHAREPOINT_SITE_URL = "https://cpncorp.sharepoint.com/sites/askcal"

# SharePoint Folders Configuration
SHAREPOINT_FOLDERS = [
    "Boarddeck",
    "TRC", 
    "Human Resources",
    "Etaf Contracts",
    "PJM",
    "Trading Compliance"
]

# Environment Variables for Authentication
SHAREPOINT_CLIENT_ID = os.getenv('SHAREPOINT_CLIENT_ID')
SHAREPOINT_CLIENT_SECRET = os.getenv('SHAREPOINT_CLIENT_SECRET')
SHAREPOINT_TENANT_ID = os.getenv('SHAREPOINT_TENANT_ID')

# File Upload Configuration
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
SUPPORTED_EXTENSIONS = {
    '.pdf', '.docx', '.txt', '.png', '.jpg', '.jpeg', 
    '.gif', '.bmp', '.xlsx', '.xls', '.doc'
}

# Text Extraction Configuration
TEXT_EXTRACTION_SUPPORTED = {'.pdf', '.docx', '.txt'}

# SharePoint API Configuration
SHAREPOINT_API_VERSION = "v1.0"
SHAREPOINT_TIMEOUT = 30  # seconds

# Folder Display Names (for UI)
FOLDER_DISPLAY_NAMES = {
    "Boarddeck": "Board Deck",
    "TRC": "TRC",
    "Human Resources": "Human Resources",
    "Etaf Contracts": "ETAF Contracts",
    "PJM": "PJM",
    "Trading Compliance": "Trading Compliance"
}

# Folder Descriptions (for UI)
FOLDER_DESCRIPTIONS = {
    "Boarddeck": "Board meeting materials and presentations",
    "TRC": "Technical Review Committee documents",
    "Human Resources": "HR policies, procedures, and employee documents",
    "Etaf Contracts": "ETAF contract documentation and agreements",
    "PJM": "PJM-related documents and reports",
    "Trading Compliance": "Trading compliance documentation and policies"
}

def get_folder_info(folder_name):
    """Get folder information including display name and description."""
    return {
        'name': folder_name,
        'display_name': FOLDER_DISPLAY_NAMES.get(folder_name, folder_name),
        'description': FOLDER_DESCRIPTIONS.get(folder_name, ''),
        'path': f"Shared Documents/{folder_name}"
    }

def get_all_folders_info():
    """Get information for all configured folders."""
    return [get_folder_info(folder) for folder in SHAREPOINT_FOLDERS]

def validate_folder_name(folder_name):
    """Validate if a folder name is in the configured list."""
    return folder_name in SHAREPOINT_FOLDERS

def get_folder_path(folder_name):
    """Get the full SharePoint path for a folder."""
    if not validate_folder_name(folder_name):
        raise ValueError(f"Invalid folder name: {folder_name}")
    return f"Shared Documents/{folder_name}"
