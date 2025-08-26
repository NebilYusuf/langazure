import React, { useEffect } from 'react';
import { FileText } from 'lucide-react';
import { useDocumentManager } from './hooks/useDocumentManager';
import FileUpload from './components/FileUpload';
import DocumentList from './components/DocumentList';
import StatusMessage from './components/StatusMessage';
import DocumentViewer from './components/DocumentViewer';
import './App.css';

function App() {
  const {
    documents,
    selectedDocument,
    loading,
    isLoadingFiles,
    error,
    success,
    loadFiles,
    handleUpload,
    handleDeleteDocument,
    handleViewDocument,
    setSelectedDocument,
    clearMessages
  } = useDocumentManager();

  // Load files on component mount
  useEffect(() => {
    loadFiles();
  }, [loadFiles]);

  return (
    <div className="container">
      <div className="card">
        <h1>📄 Document Upload & Viewer</h1>
        <p>Upload your documents to Azure Blob Storage and view their content instantly</p>
      </div>

      <FileUpload onDrop={handleUpload} loading={loading} />

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
        onRefresh={loadFiles}
      />

      {selectedDocument && (
        <DocumentViewer
          document={selectedDocument}
          onClose={() => setSelectedDocument(null)}
          onSave={loadFiles}
        />
      )}
    </div>
  );
}

export default App;
