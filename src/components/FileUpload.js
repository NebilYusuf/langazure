import React from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload } from 'lucide-react';
import './FileUpload.css';

const FileUpload = ({ onDrop, loading }) => {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
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

  return (
    <div className="card">
      <h2>Upload Documents</h2>
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'drag-active' : ''}`}
      >
        <input {...getInputProps()} />
        <Upload size={48} color="#667eea" />
        <h3>Drop files here or click to select</h3>
        <p>Supports: PDF, TXT, Images, Excel, Word documents</p>
        <p style={{ fontSize: '12px', marginTop: '8px', color: '#999' }}>
          Files will be stored securely in Azure Blob Storage with original names preserved
        </p>
      </div>
    </div>
  );
};

export default FileUpload;
