import React, { useEffect, useState } from 'react';
import { FileText } from 'lucide-react';
import { useDocumentManager } from './hooks/useDocumentManager';
import SharePointLogin from './components/SharePointLogin';
import FileUpload from './components/FileUpload';
import DocumentList from './components/DocumentList';
import StatusMessage from './components/StatusMessage';
import DocumentViewer from './components/DocumentViewer';
import './App.css';

function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  const {
    documents,
    selectedDocument,
    loading,
    isLoadingFiles,
    error,
    success,
    selectedFolder,
    loadFiles,
    handleUpload,
    handleDeleteDocument,
    handleViewDocument,
    handleFolderChange,
    setSelectedDocument,
    clearMessages
  } = useDocumentManager();

  // Load files on component mount and when user authenticates
  useEffect(() => {
    if (isAuthenticated) {
      loadFiles();
    }
  }, [loadFiles, isAuthenticated]);

  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
    setIsAuthenticated(true);
    console.log('User logged in:', user);
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setIsAuthenticated(false);
    console.log('User logged out');
  };

  // Show login screen if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="container">
        <div className="card" style={{ textAlign: 'center', marginBottom: '24px' }}>
          <h1>📄 SharePoint Document Manager</h1>
          <p>Access and manage documents across multiple SharePoint folders</p>
          <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
            <h4 style={{ margin: '0 0 8px 0', color: '#495057' }}>Available SharePoint Folders:</h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', justifyContent: 'center' }}>
              {['Boarddeck', 'TRC', 'Human Resources', 'Etaf Contracts', 'PJM', 'Trading Compliance'].map(folder => (
                <span 
                  key={folder}
                  style={{ 
                    padding: '4px 8px', 
                    backgroundColor: '#e9ecef', 
                    color: '#495057',
                    borderRadius: '4px',
                    fontSize: '12px',
                    fontWeight: '500'
                  }}
                >
                  {folder}
                </span>
              ))}
            </div>
          </div>
        </div>

        <SharePointLogin 
          onLoginSuccess={handleLoginSuccess}
          onLogout={handleLogout}
        />
      </div>
    );
  }

  // Show main application when authenticated
  return (
    <div className="container">
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1>📄 SharePoint Document Manager</h1>
            <p>Welcome, <strong>{currentUser?.displayName || currentUser?.username}</strong>! Manage your documents across multiple SharePoint folders</p>
            <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
              <h4 style={{ margin: '0 0 8px 0', color: '#495057' }}>Available SharePoint Folders:</h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {['Boarddeck', 'TRC', 'Human Resources', 'Etaf Contracts', 'PJM', 'Trading Compliance'].map(folder => (
                  <span 
                    key={folder}
                    style={{ 
                      padding: '4px 8px', 
                      backgroundColor: selectedFolder === folder ? '#007bff' : '#e9ecef', 
                      color: selectedFolder === folder ? 'white' : '#495057',
                      borderRadius: '4px',
                      fontSize: '12px',
                      fontWeight: '500'
                    }}
                  >
                    {folder}
                  </span>
                ))}
              </div>
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <p style={{ margin: '0 0 8px 0', fontSize: '0.9rem', color: '#6c757d' }}>
              Signed in as: <strong>{currentUser?.username}</strong>
            </p>
            <button 
              className="btn btn-secondary" 
              onClick={handleLogout}
              style={{ fontSize: '0.9rem', padding: '6px 12px' }}
            >
              Sign Out
            </button>
          </div>
        </div>
      </div>

      <FileUpload 
        onDrop={handleUpload} 
        loading={loading} 
        selectedFolder={selectedFolder}
        onFolderChange={handleFolderChange}
      />

      <StatusMessage 
        error={error} 
        success={success} 
        loading={loading} 
      />

      <DocumentList
        documents={documents}
        onViewDocument={handleViewDocument}
        onDeleteDocument={handleDeleteDocument}
        isLoadingFiles={isLoadingFiles}
        onRefresh={() => loadFiles(selectedFolder)}
        selectedFolder={selectedFolder}
        onFolderChange={handleFolderChange}
      />

      {selectedDocument && (
        <DocumentViewer
          document={selectedDocument}
          onClose={() => setSelectedDocument(null)}
          onSave={() => loadFiles(selectedFolder)}
        />
      )}
    </div>
  );
}

export default App;
