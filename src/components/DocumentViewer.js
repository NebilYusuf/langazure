import React, { useState } from 'react';
import { X, Download, FileText, FileImage, FileSpreadsheet, Edit, Save, RotateCcw } from 'lucide-react';
import { getDownloadUrl, saveEditedText } from '../services/api';
import './DocumentViewer.css';

const DocumentViewer = ({ document, onClose, onSave }) => {
  const [loading, setLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedText, setEditedText] = useState('');
  const [saving, setSaving] = useState(false);

  const handleDownload = async () => {
    try {
      setLoading(true);
      const downloadUrl = await getDownloadUrl(document.id);
      
      // Create a temporary link to download the file
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = document.name || 'download';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Download error:', error);
      alert('Failed to download file. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = () => {
    setEditedText(document.content.data);
    setIsEditing(true);
  };

  const handleSave = async () => {
    try {
      console.log('Starting to save edited text for:', document.id);
      console.log('Edited text length:', editedText.length);
      setSaving(true);
      
      const result = await saveEditedText(document.id, editedText);
      console.log('Save result:', result);
      
      // Update the document content with edited text
      document.content.data = editedText;
      document.content.source = 'edited';
      
      setIsEditing(false);
      alert('Text saved successfully!');
      
      // Call the onSave callback to refresh the file list
      if (onSave) {
        onSave();
      }
    } catch (error) {
      console.error('Save error:', error);
      alert('Failed to save changes. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditedText('');
  };

  const renderContent = () => {
    if (!document.content) {
      return <div className="error">No content available</div>;
    }

    switch (document.content.type) {
      case 'text':
        return (
          <div className="text-content">
            {document.content.source && (
              <div className="text-source-info">
                <span className={`source-badge ${document.content.source}`}>
                  {document.content.source === 'cached' ? '📋 Cached Text' : 
                   document.content.source === 'extracted' ? '🔄 Freshly Extracted' :
                   document.content.source === 'edited' ? '✏️ Edited Text' : '📄 Text'}
                </span>
              </div>
            )}
            {isEditing ? (
              <div className="text-editor">
                <textarea
                  value={editedText}
                  onChange={(e) => setEditedText(e.target.value)}
                  placeholder="Edit the extracted text..."
                  className="text-editor-textarea"
                />
                <div className="text-editor-actions">
                  <button 
                    onClick={handleSave} 
                    disabled={saving}
                    className="btn btn-primary"
                  >
                    <Save size={16} />
                    {saving ? 'Saving...' : 'Save'}
                  </button>
                  <button 
                    onClick={handleCancel}
                    className="btn btn-secondary"
                  >
                    <RotateCcw size={16} />
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-data">
                {document.content.data}
              </div>
            )}
          </div>
        );

      case 'pdf':
        return (
          <iframe
            src={document.content.data}
            className="pdf-viewer"
            title={document.name}
          />
        );

      case 'image':
        return (
          <div className="image-container">
            <img
              src={document.content.data}
              alt={document.name}
              className="image-viewer"
            />
          </div>
        );

      case 'spreadsheet':
      case 'word':
      case 'unknown':
        return (
          <div className="unsupported-content">
            <div className="unsupported-icon">
              {document.content.type === 'spreadsheet' && <FileSpreadsheet size={48} />}
              {document.content.type === 'word' && <FileText size={48} />}
              {document.content.type === 'unknown' && <FileText size={48} />}
            </div>
            <h3>Content Preview Not Available</h3>
            <p>{document.content.data}</p>
            <p>You can download the file to view it in your default application.</p>
          </div>
        );

      case 'error':
        return (
          <div className="error">
            <h3>Error Reading File</h3>
            <p>{document.content.data}</p>
          </div>
        );

      default:
        return (
          <div className="error">
            Unknown content type
          </div>
        );
    }
  };

  const getFileTypeIcon = () => {
    if (!document.type) return <FileText size={24} />;
    
    if (document.type.includes('image/')) return <FileImage size={24} />;
    if (document.type.includes('pdf')) return <FileText size={24} />;
    if (document.type.includes('spreadsheet') || (document.name && (document.name.endsWith('.xlsx') || document.name.endsWith('.xls')))) {
      return <FileSpreadsheet size={24} />;
    }
    if (document.type.includes('word') || (document.name && (document.name.endsWith('.docx') || document.name.endsWith('.doc')))) {
      return <FileText size={24} />;
    }
    return <FileText size={24} />;
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

  return (
    <div className="document-viewer-overlay">
      <div className="document-viewer-modal">
        <div className="document-viewer-header">
          <div className="document-viewer-info">
            <div className="document-viewer-icon">
              {getFileTypeIcon()}
            </div>
            <div className="document-viewer-details">
              <h2>{document.name || 'Unknown File'}</h2>
              <p>{formatFileSize(document.size || 0)} • {formatDate(document.uploadedAt || new Date())}</p>
              <p style={{ fontSize: '12px', color: '#28a745', margin: '4px 0 0 0' }}>
                ✓ Stored in Azure Blob Storage
              </p>
            </div>
          </div>
          <div className="document-viewer-actions">
            {document.content && document.content.type === 'text' && !isEditing && (
              <button 
                className="btn btn-primary" 
                onClick={handleEdit}
              >
                <Edit size={16} />
                Edit
              </button>
            )}
            <button 
              className="btn btn-secondary" 
              onClick={handleDownload}
              disabled={loading}
            >
              <Download size={16} />
              {loading ? 'Preparing...' : 'Download'}
            </button>
            <button className="btn btn-secondary" onClick={onClose}>
              <X size={16} />
              Close
            </button>
          </div>
        </div>

        <div className="document-viewer-content">
          {loading ? (
            <div className="loading">
              <p>Loading content...</p>
            </div>
          ) : (
            renderContent()
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentViewer;
