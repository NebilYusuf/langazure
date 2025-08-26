import React from 'react';
import './StatusMessage.css';

const StatusMessage = ({ error, success, loading }) => {
  if (loading) {
    return (
      <div className="card">
        <div className="loading">
          <p>Uploading to Azure Blob Storage...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="error">{error}</div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="card">
        <div className="success">{success}</div>
      </div>
    );
  }

  return null;
};

export default StatusMessage;
