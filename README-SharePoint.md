# SharePoint Document Manager

This application has been repurposed to work with SharePoint instead of Azure Blob Storage. It provides a comprehensive document management solution for the SharePoint site at `https://cpncorp.sharepoint.com/sites/askcal`.

## Features

- **Multi-Folder Support**: Works with 6 specific SharePoint folders:
  - Boarddeck
  - TRC
  - Human Resources
  - Etaf Contracts
  - PJM
  - Trading Compliance

- **Document Operations**:
  - Upload files to specific SharePoint folders
  - View and manage documents across folders
  - Extract text from PDF and Word documents
  - Delete documents and extracted text
  - Download files from SharePoint

- **Text Extraction**:
  - Automatic text extraction for PDF and Word documents
  - Caching of extracted text in SharePoint
  - Support for editing and saving extracted text

## Prerequisites

### SharePoint App Registration
1. Register a new app in Azure Active Directory
2. Grant the app appropriate permissions to SharePoint
3. Note down the following values:
   - Client ID
   - Client Secret
   - Tenant ID

### Environment Variables
Set the following environment variables:

```bash
SHAREPOINT_CLIENT_ID=your_client_id_here
SHAREPOINT_CLIENT_SECRET=your_client_secret_here
SHAREPOINT_TENANT_ID=your_tenant_id_here
```

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure SharePoint Authentication**:
   - Set the environment variables mentioned above
   - Ensure the SharePoint app has proper permissions

3. **Start the Application**:
   ```bash
   # For Azure Functions
   func start
   
   # For local development
   python server/start_python_server.py
   ```

## Usage

### Frontend Interface
The web interface allows users to:
- Select a SharePoint folder for uploads
- Drag and drop files for upload
- Browse documents by folder
- View document content and extracted text
- Delete documents

### API Endpoints

#### Get Files
```
GET /api/files?folder={folder_name}
```
Returns all files from the specified folder, or all folders if no folder specified.

#### Upload File
```
POST /api/upload
```
Upload a file to a specific SharePoint folder. Include `folder` in form data.

#### Extract Text
```
POST /api/extract-text/{file_url}?folder={folder_name}
```
Extract text from a document and store it in SharePoint.

#### Delete File
```
DELETE /api/files/{filename}?folder={folder_name}
```
Delete a file and its extracted text from SharePoint.

#### Get Download URL
```
GET /api/files/{file_url}/download
```
Get a download URL for a SharePoint file.

#### Save Edited Text
```
POST /api/save-edited-text/{filename}?folder={folder_name}
```
Save edited extracted text back to SharePoint.

## SharePoint Folder Structure

The application works with the following folder structure in SharePoint:

```
Shared Documents/
├── Boarddeck/
├── TRC/
├── Human Resources/
├── Etaf Contracts/
├── PJM/
└── Trading Compliance/
```

Each folder can contain:
- Original documents (PDF, Word, Excel, images, etc.)
- Extracted text files (with `_extracted.txt` suffix)

## Security Considerations

- **Authentication**: Uses Azure AD app authentication
- **Permissions**: App has read/write access to specified folders only
- **File Access**: Users must be authenticated to access SharePoint content
- **Data Privacy**: All operations are logged and auditable

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Verify environment variables are set correctly
   - Check app permissions in Azure AD
   - Ensure the app is registered in the correct tenant

2. **Folder Access Issues**:
   - Verify folder names match exactly (case-sensitive)
   - Check SharePoint permissions for the app
   - Ensure folders exist in the SharePoint site

3. **File Upload Failures**:
   - Check file size limits (50MB max)
   - Verify file type is supported
   - Check SharePoint storage quotas

### Logs
Check Azure Functions logs for detailed error information:
```bash
func logs
```

## Development

### Adding New Folders
To add new SharePoint folders:

1. Update `shared/sharepoint_config.py`
2. Add folder to `SHAREPOINT_FOLDERS` list
3. Add display name and description
4. Update frontend components if needed

### Customizing File Types
Modify `SUPPORTED_EXTENSIONS` in the configuration to support additional file types.

## Support

For technical support or questions about the SharePoint integration, contact your SharePoint administrator or the development team.

## License

This project is licensed under the same terms as the original Azure Blob Storage version.
