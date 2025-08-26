# 📄 LangAzure Document Manager

A modern, full-stack document management application that combines a React frontend with Azure Functions backend for seamless document upload, storage, and text extraction.

## ✨ Features

### 🚀 **Core Functionality**
- **Drag & Drop Upload**: Intuitive file upload with visual feedback
- **Multi-Format Support**: PDF, Word documents, Excel files, images, and text files
- **Azure Blob Storage**: Secure cloud storage with original file names preserved
- **Text Extraction**: Automatic text extraction from PDFs and Word documents
- **Real-time Editing**: In-place text editing with save functionality
- **File Management**: View, delete, and organize documents

### 🎨 **User Experience**
- **Modern UI**: Clean, responsive design with Lucide React icons
- **Component Architecture**: Modular React components for maintainability
- **Custom Hooks**: Centralized state management with `useDocumentManager`
- **Auto-Extraction**: Text extraction happens automatically on upload
- **Instant Feedback**: Immediate UI updates without manual refresh

### 🔧 **Technical Stack**
- **Frontend**: React 18 with modern hooks and functional components
- **Backend**: Azure Functions (Python) with HTTP triggers
- **Storage**: Azure Blob Storage for document persistence
- **Text Processing**: Python libraries for PDF and Word document parsing
- **API**: RESTful endpoints with CORS support

## 🏗️ Architecture

### **Frontend Structure**
```
src/
├── components/           # Reusable UI components
│   ├── FileUpload.js     # Drag & drop upload component
│   ├── DocumentList.js   # Document listing and management
│   ├── DocumentViewer.js # Document viewing and editing
│   └── StatusMessage.js  # Loading, error, and success messages
├── hooks/                # Custom React hooks
│   └── useDocumentManager.js # Centralized document state management
├── services/             # API service layer
│   └── api.js           # HTTP client for Azure Functions
└── App.js               # Main application component
```

### **Backend Structure**
```
Azure Functions/
├── DeleteFile/          # Delete documents from blob storage
├── ExtractText/         # Extract text from various file formats
├── GetDownloadUrl/      # Generate secure download URLs
├── GetFiles/            # List all documents in storage
├── SaveEditedText/      # Save edited text back to storage
├── UploadFile/          # Upload files to blob storage
└── HealthCheck/         # API health monitoring
```

## 🚀 Getting Started

### **Prerequisites**
- Node.js 16+ and npm
- Python 3.8+
- Azure account with Blob Storage
- Azure Functions Core Tools

### **Frontend Setup**
```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

### **Backend Setup**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start Azure Functions locally
func start
```

### **Environment Configuration**
Create a `local.settings.json` file for Azure Functions:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_STORAGE_CONNECTION_STRING": "your_connection_string",
    "CONTAINER_NAME": "your_container_name"
  }
}
```

## 📁 Project Structure

```
langazure-document-manager/
├── src/                    # React frontend
│   ├── components/         # UI components
│   ├── hooks/             # Custom React hooks
│   ├── services/          # API services
│   └── App.js             # Main app component
├── Azure Functions/        # Python Azure Functions
│   ├── DeleteFile/
│   ├── ExtractText/
│   ├── GetDownloadUrl/
│   ├── GetFiles/
│   ├── SaveEditedText/
│   ├── UploadFile/
│   └── HealthCheck/
├── package.json           # Frontend dependencies
├── requirements.txt       # Backend dependencies
├── host.json             # Azure Functions config
└── README.md             # Project documentation
```

## 🔧 Configuration

### **Azure Storage Setup**
1. Create an Azure Storage Account
2. Create a blob container for documents
3. Get the connection string
4. Update environment variables

### **CORS Configuration**
The application is configured to handle CORS requests between the React frontend and Azure Functions backend.

### **File Type Support**
- **PDF**: Text extraction using PyPDF2
- **Word Documents**: Text extraction using python-docx
- **Excel Files**: Basic file information display
- **Images**: Direct display in browser
- **Text Files**: Direct content display

## 🛠️ Development

### **Adding New Features**
1. Create new React components in `src/components/`
2. Add custom hooks in `src/hooks/` if needed
3. Create new Azure Functions for backend logic
4. Update API services in `src/services/api.js`

### **Testing**
```bash
# Frontend tests
npm test

# Backend tests (manual testing with Azure Functions)
func start
# Test endpoints with tools like Postman or curl
```

### **Deployment**
1. **Frontend**: Deploy to Azure Static Web Apps or similar
2. **Backend**: Deploy Azure Functions to Azure
3. **Storage**: Ensure Azure Blob Storage is properly configured

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [React](https://reactjs.org/) for the frontend framework
- [Azure Functions](https://azure.microsoft.com/services/functions/) for serverless backend
- [Lucide React](https://lucide.dev/) for beautiful icons
- [React Dropzone](https://react-dropzone.js.org/) for file upload functionality

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/yourusername/langazure-document-manager/issues) page
2. Create a new issue with detailed information
3. Contact the maintainers

---

**Made with ❤️ using React and Azure Functions**
