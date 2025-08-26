# Document Upload & Viewer - Azure Functions

A serverless document management application built with Azure Functions, providing document upload, storage, text extraction, and editing capabilities using Azure Blob Storage.

## 🚀 Features

- **Document Upload**: Drag-and-drop file upload with automatic duplicate handling
- **Azure Blob Storage**: Secure cloud storage with automatic container management
- **Text Extraction**: Extract text from PDF and DOCX files using Python libraries
- **Text Caching**: Store extracted text in Azure Blob Storage for faster retrieval
- **Text Editing**: Edit extracted text directly in the UI and save changes
- **Progress Tracking**: Real-time progress bars for text extraction
- **Secure Downloads**: Generate secure SAS tokens for file downloads
- **File Management**: List, download, and delete files with automatic cleanup

## 🏗️ Architecture

### Azure Functions Structure

```
├── HealthCheck/           # Health check endpoint
├── UploadFile/           # File upload functionality
├── GetFiles/             # List all files
├── ExtractText/          # Text extraction from documents
├── SaveEditedText/       # Save edited text
├── GetDownloadUrl/       # Generate secure download URLs
├── DeleteFile/           # Delete files and extracted text
├── shared/               # Shared utilities and Azure Storage operations
│   └── azure_storage.py  # Core Azure Storage functionality
├── extractor/            # Text extraction modules
│   ├── pdf_extractor.py  # PDF text extraction
│   └── docx_extractor.py # DOCX text extraction
├── host.json             # Azure Functions host configuration
├── local.settings.json   # Local development settings
└── requirements.txt      # Python dependencies
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check and Azure connection status |
| POST | `/api/upload` | Upload a file to Azure Blob Storage |
| GET | `/api/files` | List all files in the container |
| POST | `/api/extract-text/{blob_name}` | Extract text from a document |
| POST | `/api/save-edited-text/{blob_name}` | Save edited text back to Azure |
| GET | `/api/files/{blob_name}/download` | Get secure download URL |
| DELETE | `/api/files/{blob_name}` | Delete file and extracted text |

## 🛠️ Prerequisites

- **Azure Account**: Active Azure subscription
- **Azure CLI**: For deployment and management
- **Azure Functions Core Tools**: For local development
- **Python 3.11**: Runtime environment
- **Azure Storage Account**: For blob storage

## 📦 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd langazure
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Azure Functions Core Tools

```bash
npm install -g azure-functions-core-tools@4 --unsafe-perm true
```

### 4. Configure Environment Variables

Create a `local.settings.json` file for local development:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_STORAGE_CONNECTION_STRING": "your_azure_storage_connection_string",
    "AZURE_CONTAINER_NAME": "documents"
  }
}
```

For production, configure these in Azure Function App settings:
- `AZURE_STORAGE_CONNECTION_STRING`
- `AZURE_CONTAINER_NAME`

## 🚀 Local Development

### Start Local Development Server

```bash
func start
```

The functions will be available at:
- Health Check: http://localhost:7071/api/health
- Upload: http://localhost:7071/api/upload
- Files: http://localhost:7071/api/files
- Extract Text: http://localhost:7071/api/extract-text/{blob_name}
- Save Edited Text: http://localhost:7071/api/save-edited-text/{blob_name}
- Download: http://localhost:7071/api/files/{blob_name}/download
- Delete: http://localhost:7071/api/files/{blob_name}

### Test the Functions

```bash
# Health check
curl http://localhost:7071/api/health

# List files
curl http://localhost:7071/api/files

# Upload a file
curl -X POST -F "file=@test.pdf" http://localhost:7071/api/upload
```

## ☁️ Azure Deployment

### Option 1: Using PowerShell Script

```powershell
.\deploy.ps1 -ResourceGroupName "my-resource-group" -FunctionAppName "my-function-app" -StorageAccountName "mystorageaccount" -Location "East US"
```

### Option 2: Manual Deployment

1. **Create Resource Group**:
   ```bash
   az group create --name my-resource-group --location East US
   ```

2. **Create Storage Account**:
   ```bash
   az storage account create --name mystorageaccount --resource-group my-resource-group --location East US --sku Standard_LRS
   ```

3. **Create Function App**:
   ```bash
   az functionapp create --name my-function-app --resource-group my-resource-group --storage-account mystorageaccount --consumption-plan-location East US --runtime python --runtime-version 3.11 --functions-version 4
   ```

4. **Deploy Functions**:
   ```bash
   func azure functionapp publish my-function-app
   ```

5. **Configure Environment Variables**:
   ```bash
   az functionapp config appsettings set --name my-function-app --resource-group my-resource-group --settings AZURE_STORAGE_CONNECTION_STRING="your_connection_string" AZURE_CONTAINER_NAME="documents"
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_STORAGE_CONNECTION_STRING` | Azure Storage connection string | Yes |
| `AZURE_CONTAINER_NAME` | Blob container name | No (default: "documents") |

### Azure Storage Setup

1. Create an Azure Storage Account
2. Create a blob container (or let the app create it automatically)
3. Get the connection string from Azure Portal
4. Configure the connection string in Function App settings

## 📁 File Structure

### Supported File Types

- **Documents**: PDF, DOCX, TXT
- **Images**: PNG, JPG, JPEG, GIF, BMP
- **Spreadsheets**: XLSX, XLS

### Storage Organization

```
Azure Blob Container/
├── document1.pdf          # Original documents
├── document2.docx
├── document1 (1).pdf      # Duplicate handling
├── documents_text/        # Extracted text cache
│   ├── document1.pdf.txt
│   └── document2.docx.txt
```

## 🔒 Security

- **Authentication**: Anonymous access (can be configured for Azure AD)
- **Authorization**: SAS tokens for secure file downloads
- **Data Protection**: All data stored in Azure Blob Storage with encryption
- **CORS**: Configured for web application access

## 📊 Monitoring

### Azure Application Insights

Enable Application Insights for monitoring:
```bash
az functionapp update --name my-function-app --resource-group my-resource-group --set kind=functionapp
az monitor app-insights component create --app my-function-app-insights --location East US --resource-group my-resource-group --application-type web
```

### Logs

View function logs:
```bash
az functionapp logs tail --name my-function-app --resource-group my-resource-group
```

## 🧪 Testing

### Unit Tests

```bash
python -m pytest tests/
```

### Integration Tests

```bash
# Test file upload
curl -X POST -F "file=@test.pdf" http://localhost:7071/api/upload

# Test text extraction
curl -X POST http://localhost:7071/api/extract-text/test.pdf

# Test file listing
curl http://localhost:7071/api/files
```

## 🔄 Migration from Flask

### Key Changes

1. **Function Structure**: Each endpoint is now a separate Azure Function
2. **Shared Code**: Common functionality moved to `shared/azure_storage.py`
3. **Configuration**: Environment variables configured in Azure Function App settings
4. **Deployment**: Uses Azure Functions deployment instead of traditional hosting

### Benefits

- **Serverless**: Pay only for execution time
- **Auto-scaling**: Automatic scaling based on demand
- **Managed**: No server management required
- **Integration**: Native Azure service integration
- **Cost-effective**: Consumption-based pricing

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `shared/` module is in Python path
2. **Azure Connection**: Verify connection string and permissions
3. **File Upload**: Check file size limits and supported formats
4. **Text Extraction**: Ensure required Python packages are installed

### Debug Mode

Enable debug logging in `host.json`:
```json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "excludedTypes": "Request"
      }
    },
    "logLevel": {
      "default": "Information",
      "Host.Results": "Error",
      "Function": "Information",
      "Host.Aggregator": "Information"
    }
  }
}
```

## 📈 Performance

### Optimization Tips

1. **Cold Start**: Use Premium plan for consistent performance
2. **Memory**: Configure appropriate memory allocation
3. **Timeout**: Set appropriate function timeout values
4. **Caching**: Leverage text caching for frequently accessed documents

### Scaling

- **Consumption Plan**: Automatic scaling, pay per execution
- **Premium Plan**: Pre-warmed instances, consistent performance
- **Dedicated Plan**: Full control over scaling and resources

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review Azure Functions documentation
3. Open an issue in the repository
4. Contact the development team

## 🔄 Updates

### Version History

- **v2.0**: Migrated to Azure Functions
- **v1.0**: Original Flask implementation

### Future Enhancements

- [ ] Azure AD authentication
- [ ] Advanced text processing
- [ ] Document versioning
- [ ] Batch operations
- [ ] Advanced search capabilities
