# Azure Blob Storage Setup Guide

This guide will help you set up Azure Blob Storage for the Document Upload & Viewer application.

## Prerequisites

- Azure account (you can create a free account at [azure.com](https://azure.com))
- Basic knowledge of Azure Portal

## Step 1: Create Azure Storage Account

1. **Sign in to Azure Portal**
   - Go to [portal.azure.com](https://portal.azure.com)
   - Sign in with your Azure account

2. **Create Storage Account**
   - Click "Create a resource"
   - Search for "Storage account"
   - Click "Create" on the Storage account option

3. **Configure Storage Account**
   - **Subscription**: Choose your subscription
   - **Resource group**: Create new or use existing
   - **Storage account name**: Choose a unique name (e.g., `mydocumentstorage`)
   - **Region**: Choose a region close to you
   - **Performance**: Standard
   - **Redundancy**: Locally-redundant storage (LRS) for cost savings
   - Click "Review + create"
   - Click "Create"

4. **Wait for Deployment**
   - Wait for the storage account to be created (usually 1-2 minutes)
   - Click "Go to resource" when complete

## Step 2: Get Connection String

1. **Access Keys**
   - In your storage account, go to "Access keys" in the left menu
   - Click "Show" next to "Connection string" under "key1"
   - Copy the entire connection string

2. **Connection String Format**
   ```
   DefaultEndpointsProtocol=https;AccountName=yourstorageaccount;AccountKey=yourstoragekey;EndpointSuffix=core.windows.net
   ```

## Step 3: Configure Application

1. **Create Environment File**
   - In the `server` folder, create a file named `.env`
   - Add the following content:

   ```
   AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=yourstorageaccount;AccountKey=yourstoragekey;EndpointSuffix=core.windows.net
   AZURE_CONTAINER_NAME=documents
   PORT=5000
   ```

2. **Replace Placeholder Values**
   - Replace `yourstorageaccount` with your actual storage account name
   - Replace `yourstoragekey` with your actual storage key
   - The container name `documents` will be created automatically

## Step 4: Test Configuration

1. **Start the Backend Server**
   ```bash
   cd server
   npm start
   ```

2. **Check for Success**
   - You should see: `Container 'documents' is ready`
   - If you see errors, check your connection string

## Step 5: Start the Application

1. **Use the Startup Script**
   - Double-click `start.bat` in the root folder
   - This will start both backend and frontend servers

2. **Manual Start**
   ```bash
   # Terminal 1 - Backend
   cd server
   npm start

   # Terminal 2 - Frontend
   npm start
   ```

## Troubleshooting

### Common Issues

1. **"Container 'documents' is ready" not showing**
   - Check your connection string
   - Ensure your storage account is active
   - Verify you have proper permissions

2. **Upload failures**
   - Check file size (max 50MB)
   - Verify storage account has available space
   - Check network connectivity

3. **CORS errors**
   - The backend is configured to allow all origins in development
   - For production, configure CORS in Azure Storage Account settings

### Azure Storage Account Settings

1. **CORS Configuration (Optional)**
   - Go to your storage account
   - Click "CORS" in the left menu
   - Add a new CORS rule:
     - Allowed origins: `*` (for development)
     - Allowed methods: GET, POST, PUT, DELETE
     - Allowed headers: `*`
     - Exposed headers: `*`
     - Max age: 86400

2. **Container Access Level**
   - Go to "Containers" in your storage account
   - Click on the "documents" container
   - Set access level to "Private" for security

## Security Best Practices

1. **Use Managed Identity** (for production)
   - Instead of connection strings, use Azure Managed Identity
   - More secure and easier to manage

2. **SAS Tokens**
   - The application uses SAS tokens for secure downloads
   - Tokens expire after 1 hour for security

3. **Network Security**
   - Consider using Azure Private Endpoints for production
   - Restrict access to specific IP ranges if needed

## Cost Optimization

1. **Storage Tier**
   - Use "Hot" tier for frequently accessed files
   - Use "Cool" tier for infrequently accessed files
   - Use "Archive" tier for long-term storage

2. **Lifecycle Management**
   - Set up automatic tier transitions
   - Configure automatic deletion for old files

## Next Steps

Once your Azure setup is complete:

1. **Test the Application**
   - Upload a few test files
   - Verify they appear in Azure Storage
   - Test download functionality

2. **Monitor Usage**
   - Check Azure Storage metrics
   - Monitor costs in Azure Portal

3. **Scale as Needed**
   - Increase storage capacity as needed
   - Consider CDN for global access

## Support

If you encounter issues:

1. Check Azure Storage Account logs
2. Verify connection string format
3. Ensure storage account is in the same region as your application
4. Check Azure status page for any service issues
