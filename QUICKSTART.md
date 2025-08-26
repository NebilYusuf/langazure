# Quick Start Guide - Azure Functions

This guide will help you get the Azure Functions version of the Document Upload & Viewer application running quickly.

## 🚀 Prerequisites

1. **Azure Account**: You need an active Azure subscription
2. **Azure CLI**: Install from [https://docs.microsoft.com/en-us/cli/azure/install-azure-cli](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
3. **Azure Functions Core Tools**: Install with `npm install -g azure-functions-core-tools@4`
4. **Python 3.11**: Make sure Python 3.11 is installed

## 📦 Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create `local.settings.json`:

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

**Get your Azure Storage Connection String:**
1. Go to Azure Portal
2. Navigate to your Storage Account
3. Go to "Access keys"
4. Copy the connection string

### 3. Start Local Development

```bash
func start
```

The functions will be available at `http://localhost:7071`

### 4. Test the Functions

```bash
python test_azure_functions.py
```

## ☁️ Deploy to Azure

### Option 1: Quick Deploy (PowerShell)

```powershell
.\deploy.ps1 -ResourceGroupName "my-docs-app" -FunctionAppName "my-docs-functions" -StorageAccountName "mydocsstorage" -Location "East US"
```

### Option 2: Manual Deploy

```bash
# Create resource group
az group create --name my-docs-app --location East US

# Create storage account
az storage account create --name mydocsstorage --resource-group my-docs-app --location East US --sku Standard_LRS

# Create function app
az functionapp create --name my-docs-functions --resource-group my-docs-app --storage-account mydocsstorage --consumption-plan-location East US --runtime python --runtime-version 3.11 --functions-version 4

# Deploy functions
func azure functionapp publish my-docs-functions

# Configure environment variables
az functionapp config appsettings set --name my-docs-functions --resource-group my-docs-app --settings AZURE_STORAGE_CONNECTION_STRING="your_connection_string" AZURE_CONTAINER_NAME="documents"
```

## 🔗 API Endpoints

Once deployed, your functions will be available at:

- **Health Check**: `https://my-docs-functions.azurewebsites.net/api/health`
- **Upload File**: `https://my-docs-functions.azurewebsites.net/api/upload`
- **List Files**: `https://my-docs-functions.azurewebsites.net/api/files`
- **Extract Text**: `https://my-docs-functions.azurewebsites.net/api/extract-text/{blob_name}`
- **Save Edited Text**: `https://my-docs-functions.azurewebsites.net/api/save-edited-text/{blob_name}`
- **Download URL**: `https://my-docs-functions.azurewebsites.net/api/files/{blob_name}/download`
- **Delete File**: `https://my-docs-functions.azurewebsites.net/api/files/{blob_name}`

## 🧪 Testing

### Test Health Check

```bash
curl https://my-docs-functions.azurewebsites.net/api/health
```

### Test File Upload

```bash
curl -X POST -F "file=@test.pdf" https://my-docs-functions.azurewebsites.net/api/upload
```

### Test File Listing

```bash
curl https://my-docs-functions.azurewebsites.net/api/files
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_STORAGE_CONNECTION_STRING` | Azure Storage connection string | `DefaultEndpointsProtocol=https;AccountName=...` |
| `AZURE_CONTAINER_NAME` | Blob container name | `documents` |

### Azure Storage Setup

1. **Create Storage Account** (if not exists):
   ```bash
   az storage account create --name mystorageaccount --resource-group my-docs-app --location East US --sku Standard_LRS
   ```

2. **Get Connection String**:
   ```bash
   az storage account show-connection-string --name mystorageaccount --resource-group my-docs-app
   ```

3. **Create Container** (optional - app will create automatically):
   ```bash
   az storage container create --name documents --account-name mystorageaccount
   ```

## 📊 Monitoring

### View Logs

```bash
az functionapp logs tail --name my-docs-functions --resource-group my-docs-app
```

### Application Insights

Enable monitoring:
```bash
az monitor app-insights component create --app my-docs-insights --location East US --resource-group my-docs-app --application-type web
```

## 🚨 Troubleshooting

### Common Issues

1. **"Function not found"**: Make sure you deployed all functions
2. **"Azure connection failed"**: Check your connection string
3. **"Import error"**: Ensure all dependencies are installed
4. **"File upload failed"**: Check file size and format

### Debug Mode

Enable debug logging in Azure Portal:
1. Go to your Function App
2. Navigate to "Configuration"
3. Add setting: `FUNCTIONS_WORKER_RUNTIME_LOG_LEVEL` = `debug`

## 💰 Cost Optimization

- **Consumption Plan**: Pay only for execution time
- **Premium Plan**: For consistent performance
- **Dedicated Plan**: For high-volume usage

## 🔄 Next Steps

1. **Frontend Integration**: Update your React frontend to use the new Azure Functions endpoints
2. **Authentication**: Add Azure AD authentication
3. **Monitoring**: Set up Application Insights
4. **Scaling**: Configure auto-scaling rules

## 📞 Support

- **Documentation**: See `README-AzureFunctions.md` for detailed documentation
- **Issues**: Check the troubleshooting section
- **Azure Support**: Use Azure Portal support for Azure-specific issues
