# SharePoint Document Manager Server

This server provides a SharePoint-based backend for document management without requiring Azure Blob Storage.

## 🚀 Quick Start

### Option 1: Python Script
```bash
cd server
python start_server.py
```

### Option 2: Windows Batch File
```bash
cd server
start_sharepoint.bat
```

### Option 3: Direct Flask
```bash
cd server
python app_sharepoint.py
```

## 📋 Requirements

Install dependencies:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

Create a `.env` file in the server directory:

```env
# SharePoint Configuration
SHAREPOINT_SITE_URL=https://cpncorp.sharepoint.com/sites/askcal
SHAREPOINT_CLIENT_ID=your_client_id_here
SHAREPOINT_CLIENT_SECRET=your_client_secret_here
SHAREPOINT_TENANT_ID=your_tenant_id_here

# Server Configuration
PORT=5000
FLASK_ENV=development
FLASK_DEBUG=True
```

## 🔐 Authentication

The server supports two authentication methods:

1. **Interactive User Login** (Username/Password)
2. **Access Token Authentication**

## 📁 Available Endpoints

- `GET /api/health` - Health check
- `GET/POST /api/sharepoint-auth` - Authentication
- `GET /api/files` - List files
- `POST /api/upload` - Upload files
- `GET /api/files/<filename>/download` - Download files
- `POST /api/extract-text/<filename>` - Extract text
- `POST /api/save-edited-text/<filename>` - Save edited text
- `DELETE /api/files/<filename>` - Delete files

## 🎯 What's Different from Azure Blob

- ✅ **No Azure Storage connection string required**
- ✅ **No Azure container setup needed**
- ✅ **Uses SharePoint for all file operations**
- ✅ **User-based authentication instead of service principal**
- ✅ **Simpler configuration and setup**

## 🚨 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### SharePoint authentication fails
- Check your credentials
- Verify SharePoint site access
- Ensure proper permissions

### Server won't start
- Check if port 5000 is available
- Verify Python version (3.7+)
- Check console for error messages
