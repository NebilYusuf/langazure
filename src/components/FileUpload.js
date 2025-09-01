import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Folder } from 'lucide-react';
import './FileUpload.css';

const FileUpload = ({ onDrop, loading, selectedFolder, onFolderChange }) => {
  const [uploadFolder, setUploadFolder] = useState(selectedFolder || 'Boarddeck');

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (acceptedFiles) => {
      // Add folder information to each file
      const filesWithFolder = acceptedFiles.map(file => ({
        ...file,
        folder: uploadFolder
      }));
      onDrop(filesWithFolder);
    },
    accept: {
      'text/plain': ['.txt'],
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc']
    },
    multiple: true
  });

  const handleFolderChange = (e) => {
    const folder = e.target.value;
    setUploadFolder(folder);
    if (onFolderChange) {
      onFolderChange(folder);
    }
  };

  return (
    <div className="card">
      <h2>Upload Documents to SharePoint</h2>
      
      <div style={{ marginBottom: '20px' }}>
        <label htmlFor="upload-folder" style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
          Select SharePoint Folder:
        </label>
        <select
          id="upload-folder"
          value={uploadFolder}
          onChange={handleFolderChange}
          className="btn btn-secondary"
          style={{ padding: '8px 12px', minWidth: '200px' }}
        >
          <option value="Boarddeck">Boarddeck</option>
          <option value="TRC">TRC</option>
          <option value="Human Resources">Human Resources</option>
          <option value="Etaf Contracts">Etaf Contracts</option>
          <option value="PJM">PJM</option>
          <option value="Trading Compliance">Trading Compliance</option>
        </select>
        <p style={{ fontSize: '12px', marginTop: '4px', color: '#6c757d' }}>
          Files will be uploaded to the selected SharePoint folder
        </p>
      </div>

      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'drag-active' : ''}`}
      >
        <input {...getInputProps()} />
        <Upload size={48} color="#667eea" />
        <h3>Drop files here or click to select</h3>
        <p>Supports: PDF, TXT, Images, Excel, Word documents</p>
        <p style={{ fontSize: '12px', marginTop: '8px', color: '#999' }}>
          Files will be stored securely in SharePoint folder: <strong>{uploadFolder}</strong>
        </p>
      </div>
    </div>
  );
};

export default FileUpload;
