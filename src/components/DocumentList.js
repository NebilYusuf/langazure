import React from 'react';
import { Eye, Trash2, File, FileText, FileImage, FileSpreadsheet } from 'lucide-react';
import './DocumentList.css';

const DocumentList = ({ 
  documents, 
  onViewDocument, 
  onDeleteDocument, 
  isLoadingFiles,
  onRefresh 
}) => {
  const getFileIcon = (fileType, fileName) => {
    if (!fileType) return <File size={20} />;
    
    if (fileType.includes('image/')) return <FileImage size={20} />;
    if (fileType.includes('pdf')) return <FileText size={20} />;
    if (fileType.includes('spreadsheet') || (fileName && (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')))) {
      return <FileSpreadsheet size={20} />;
    }
    if (fileType.includes('word') || (fileName && (fileName.endsWith('.docx') || fileName.endsWith('.doc')))) {
      return <FileText size={20} />;
    }
    return <File size={20} />;
  };

  const formatFileSize = (bytes) => {
    if (!bytes || bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (timestamp) => {
    if (!timestamp) return 'Unknown Date';
    try {
      return new Date(timestamp).toLocaleDateString() + ' ' + new Date(timestamp).toLocaleTimeString();
    } catch (error) {
      return 'Invalid Date';
    }
  };

  if (isLoadingFiles) {
    return (
      <div className="card">
        <div className="loading">
          <p>Loading documents from Azure...</p>
        </div>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="card">
        <div style={{ textAlign: 'center', padding: '40px', color: '#6c757d' }}>
          <FileText size={64} style={{ marginBottom: '16px', opacity: 0.5 }} />
          <h3>No documents yet</h3>
          <p>Upload your first document to get started!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h2>Your Documents in Azure ({documents.length})</h2>
        <button 
          className="btn btn-secondary" 
          onClick={onRefresh}
          disabled={isLoadingFiles}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M23 4v6h-6M1 20v-6h6M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"/>
          </svg>
          Refresh
        </button>
      </div>
      <div className="document-list">
        {documents.map((doc, index) => (
          <div key={`${doc.id || doc.name || doc.originalName}-${index}`} className="document-item">
            <div className="document-info">
              <div className="document-icon">
                {getFileIcon(doc.type, doc.name)}
              </div>
              <div className="document-details">
                <h4>{doc.name || 'Unknown File'}</h4>
                <p>{formatFileSize(doc.size || 0)} • {formatDate(doc.uploadedAt || new Date())}</p>
                <p style={{ fontSize: '12px', color: '#28a745' }}>
                  ✓ Stored in Azure Blob Storage
                </p>
                {doc.hasExtractedText && (
                  <p style={{ fontSize: '12px', color: '#007bff' }}>
                    📄 Text extraction available
                  </p>
                )}
              </div>
            </div>
            <div className="document-actions">
              <button
                className="btn"
                onClick={() => onViewDocument(doc)}
              >
                <Eye size={16} />
                View
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => onDeleteDocument(doc.id || doc.name || doc.originalName)}
              >
                <Trash2 size={16} />
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DocumentList;
