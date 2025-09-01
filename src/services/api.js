const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Helper function to make API calls using fetch (like the working debug page)
const apiCall = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const url = `${API_BASE_URL}/upload`;
  const response = await fetch(url, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.status}`);
  }

  return await response.json();
};

export const getFiles = async () => {
  return await apiCall('/files');
};

export const deleteFile = async (blobName) => {
  console.log('API: deleteFile called with blobName:', blobName);
  console.log('API: Full URL will be:', `${API_BASE_URL}/files/${blobName}`);
  
  try {
    const result = await apiCall(`/files/${encodeURIComponent(blobName)}`, {
      method: 'DELETE'
    });
    console.log('API: Delete response:', result);
    return result;
  } catch (error) {
    console.error('API: Delete error:', error);
    throw error;
  }
};

export const getDownloadUrl = async (blobName) => {
  const result = await apiCall(`/files/${blobName}/download`);
  return result.downloadUrl;
};

export const extractText = async (blobName) => {
  return await apiCall(`/extract-text/${encodeURIComponent(blobName)}`, {
    method: 'POST'
  });
};

export const saveEditedText = async (blobName, editedText) => {
  console.log('API: saveEditedText called with blobName:', blobName);
  console.log('API: Edited text length:', editedText.length);
  console.log('API: Full URL will be:', `${API_BASE_URL}/save-edited-text/${blobName}`);
  
  try {
    const result = await apiCall(`/save-edited-text/${encodeURIComponent(blobName)}`, {
      method: 'POST',
      body: JSON.stringify({ text: editedText })
    });
    console.log('API: Save response:', result);
    return result;
  } catch (error) {
    console.error('API: Save error:', error);
    throw error;
  }
};

export const healthCheck = async () => {
  return await apiCall('/health');
};
