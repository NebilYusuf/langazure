# Azure Functions Deployment Script
# This script deploys the Azure Functions to Azure

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$true)]
    [string]$FunctionAppName,
    
    [Parameter(Mandatory=$true)]
    [string]$StorageAccountName,
    
    [Parameter(Mandatory=$true)]
    [string]$Location = "East US"
)

Write-Host "Starting Azure Functions deployment..." -ForegroundColor Green

# Check if Azure CLI is installed
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Error "Azure CLI is not installed. Please install it from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
}

# Check if user is logged in
$account = az account show 2>$null
if (-not $account) {
    Write-Host "Please log in to Azure..." -ForegroundColor Yellow
    az login
}

# Create resource group if it doesn't exist
Write-Host "Creating resource group: $ResourceGroupName" -ForegroundColor Yellow
az group create --name $ResourceGroupName --location $Location

# Create storage account if it doesn't exist
Write-Host "Creating storage account: $StorageAccountName" -ForegroundColor Yellow
az storage account create --name $StorageAccountName --resource-group $ResourceGroupName --location $Location --sku Standard_LRS

# Create function app
Write-Host "Creating function app: $FunctionAppName" -ForegroundColor Yellow
az functionapp create --name $FunctionAppName --resource-group $ResourceGroupName --storage-account $StorageAccountName --consumption-plan-location $Location --runtime python --runtime-version 3.11 --functions-version 4

# Deploy the function app
Write-Host "Deploying function app..." -ForegroundColor Yellow
func azure functionapp publish $FunctionAppName

Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host "Function App URL: https://$FunctionAppName.azurewebsites.net" -ForegroundColor Cyan
