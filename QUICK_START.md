# Quick Start Guide

## 🚀 Get Your Document Upload App Running in 5 Minutes

### Prerequisites
- Node.js installed
- Azure Storage Account (optional for testing)

### Step 1: Install Dependencies

```bash
# Install frontend dependencies
npm install

# Install backend dependencies
cd server
npm install
cd ..
```

### Step 2: Configure Azure (Optional for Testing)

If you want to test with Azure Blob Storage:

1. Create a `.env` file in the `server` folder:
```
AZURE_STORAGE_CONNECTION_STRING=your_connection_string_here
AZURE_CONTAINER_NAME=documents
PORT=5000
```

2. Replace `your_connection_string_here` with your Azure connection string

**Note**: If you don't configure Azure, the backend will show an error but the frontend will still work for testing the UI.

### Step 3: Start the Application

#### Option A: Use the Startup Script (Windows)
```bash
# Double-click start.bat or run:
start.bat
```

#### Option B: Manual Start
```bash
# Terminal 1 - Start Backend
cd server
npm start

# Terminal 2 - Start Frontend (in a new terminal)
npm start
```

### Step 4: Access the Application

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:5000

### Step 5: Test the Application

1. **Upload Files**: Drag and drop files or click to select
2. **View Files**: Click "View" to see document content
3. **Delete Files**: Click "Delete" to remove files
4. **Download Files**: Use the download button in the viewer

## 🛠️ Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Run `npm install` in both root and server directories

2. **"AZURE_STORAGE_CONNECTION_STRING is not set"**
   - This is expected if you haven't configured Azure
   - The frontend will still work for UI testing

3. **Port already in use**
   - Change the PORT in server/.env file
   - Or kill the process using the port

4. **CORS errors**
   - The backend is configured to allow all origins in development
   - Check that both servers are running

### Testing Without Azure

If you don't have Azure set up yet, you can still test the frontend:

1. Start only the frontend: `npm start`
2. The UI will work but uploads will fail
3. You can test the drag-and-drop and UI components

## 📁 File Structure

```
langazure/
├── src/                    # React frontend
│   ├── components/         # React components
│   ├── services/           # API services
│   └── App.js             # Main app component
├── server/                 # Node.js backend
│   ├── server.js          # Express server
│   └── package.json       # Backend dependencies
├── package.json           # Frontend dependencies
├── start.bat             # Windows startup script
└── README.md             # Full documentation
```

## 🎯 What's Working

✅ **Frontend**: React app with drag-and-drop upload  
✅ **Backend**: Express server with Azure integration  
✅ **File Management**: Upload, view, delete, download  
✅ **Filename Preservation**: Original names with duplicate handling  
✅ **Document Viewer**: PDF, text, image preview  
✅ **Responsive Design**: Works on desktop and mobile  

## 🔧 Next Steps

1. **Configure Azure**: Follow the Azure setup guide for full functionality
2. **Customize**: Modify the UI or add new features
3. **Deploy**: Deploy to production using the deployment guide

## 📞 Need Help?

- Check the full README.md for detailed documentation
- Review AZURE_SETUP.md for Azure configuration
- Check browser console and terminal for error messages
