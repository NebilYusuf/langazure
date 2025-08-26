import { useState, useCallback } from 'react';
import { uploadFile, getFiles, deleteFile, getDownloadUrl, extractText } from '../services/api';

export const useDocumentManager = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isLoadingFiles, setIsLoadingFiles] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [forceUpdate, setForceUpdate] = useState(0);

  const loadFiles = useCallback(async () => {
    try {
      setIsLoadingFiles(true);
      const files = await getFiles();
      
      // Map the API response to include all necessary fields for the frontend
      const mappedFiles = files.map(file => ({
        id: file.name || file.id || file.originalName,
        name: file.name || file.originalName,
        originalName: file.originalName || file.name,
        size: file.size,
        type: file.type || 'application/octet-stream',
        blobUrl: file.blobUrl || null,
        uploadedAt: file.uploadedAt,
        lastModified: file.lastModified || file.uploadedAt,
        content: null,
        hasExtractedText: false
      }));
      
      setDocuments(mappedFiles);
    } catch (err) {
      console.error('Error loading files:', err);
      setError('Failed to load files from storage');
    } finally {
      setIsLoadingFiles(false);
    }
  }, []);

  const handleUpload = useCallback(async (acceptedFiles) => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const uploadPromises = acceptedFiles.map(async (file) => {
        const result = await uploadFile(file);
        return {
          id: result.filename || result.blobName || result.name,
          name: result.filename || result.blobName || result.name,
          originalName: result.originalName || result.originalName || file.name,
          size: result.size || file.size,
          type: file.type || 'application/octet-stream',
          blobUrl: null,
          uploadedAt: new Date().toISOString(),
          lastModified: new Date().toISOString(),
          content: null,
          hasExtractedText: false
        };
      });

      const newDocuments = await Promise.all(uploadPromises);
      console.log('Uploaded documents:', newDocuments);
      
      setDocuments(prev => {
        const updated = [...prev, ...newDocuments];
        console.log('Documents after upload:', updated);
        return updated;
      });
      
      setSuccess(`${newDocuments.length} document(s) uploaded successfully to Azure!`);
      
      // Force a re-render to ensure UI updates
      setForceUpdate(prev => prev + 1);
      
      // Automatically extract text for each uploaded document
      for (const doc of newDocuments) {
        const docId = doc.id || doc.name || doc.originalName;
        
        // Check if this file type supports text extraction
        const supportsExtraction = doc.type && (
          doc.type.includes('pdf') ||
          doc.type.includes('word') ||
          doc.type.includes('document') ||
          doc.type.includes('text/plain') ||
          doc.originalName.endsWith('.docx') ||
          doc.originalName.endsWith('.doc') ||
          doc.originalName.endsWith('.pdf') ||
          doc.originalName.endsWith('.txt')
        );
        
        if (supportsExtraction) {
          try {
            const extractionResult = await extractText(docId);
            console.log('Auto-extraction result for', docId, ':', extractionResult);
            
            // Update document to show it has extracted text
            setDocuments(prev => prev.map(d => 
              (d.id || d.name || d.originalName) === docId 
                ? { ...d, hasExtractedText: true }
                : d
            ));
            
          } catch (extractionError) {
            console.error('Auto-extraction failed for', docId, ':', extractionError);
          }
        }
      }
      
    } catch (err) {
      console.error('Upload error:', err);
      setError('Error uploading documents to Azure. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleDeleteDocument = useCallback(async (id) => {
    if (!id) {
      console.error('Delete: No ID provided!');
      setError('Cannot delete: No document ID provided');
      return;
    }
    
    // Add confirmation dialog
    const confirmed = window.confirm(`Are you sure you want to delete "${id}"?`);
    if (!confirmed) {
      return;
    }
    
    try {
      const result = await deleteFile(id);
      
      // Remove from local state immediately for better UX
      setDocuments(prev => {
        const filtered = prev.filter(doc => (doc.id || doc.name || doc.originalName) !== id);
        console.log('Documents after delete:', filtered);
        return filtered;
      });
      
      if (selectedDocument && (selectedDocument.id || selectedDocument.name || selectedDocument.originalName) === id) {
        setSelectedDocument(null);
      }
      setSuccess('Document deleted successfully from Azure!');
      
      // Force a re-render to ensure UI updates
      setForceUpdate(prev => prev + 1);
      
      // Also refresh from backend after a short delay to ensure sync
      setTimeout(() => {
        loadFiles();
      }, 100);
      
    } catch (err) {
      console.error('Delete error:', err);
      setError('Failed to delete document from Azure');
    }
  }, [selectedDocument, loadFiles]);

  const handleViewDocument = useCallback(async (doc) => {
    try {
      // Get download URL if not available
      if (!doc.blobUrl) {
        try {
          const downloadUrl = await getDownloadUrl(doc.id || doc.name || doc.originalName);
          doc.blobUrl = downloadUrl;
        } catch (urlError) {
          console.warn('Failed to get download URL:', urlError);
        }
      }

      // For text files, fetch the content
      if (doc.type === 'text/plain') {
        if (doc.blobUrl) {
          const response = await fetch(doc.blobUrl);
          const text = await response.text();
          doc.content = { type: 'text', data: text };
        } else {
          throw new Error('No download URL available');
        }
      } else if (doc.type === 'application/pdf') {
        // Check if text has already been extracted
        if (doc.hasExtractedText) {
          console.log('Text already extracted for PDF, fetching cached text');
          try {
            const extractionResult = await extractText(doc.id || doc.name || doc.originalName);
            if (extractionResult.success) {
              doc.content = { 
                type: 'text', 
                data: extractionResult.text,
                source: extractionResult.source || 'cached'
              };
            } else {
              // Fallback to PDF viewer
              doc.content = { type: 'pdf', data: doc.blobUrl };
            }
          } catch (error) {
            console.warn('Failed to fetch cached text, using PDF viewer:', error);
            doc.content = { type: 'pdf', data: doc.blobUrl };
          }
        } else {
          // Try to extract text from PDF
          try {
            console.log('Starting text extraction for:', doc.id || doc.name || doc.originalName);
            const extractionResult = await extractText(doc.id || doc.name || doc.originalName);
            console.log('Extraction result:', extractionResult);
            
            if (extractionResult.success) {
              console.log('Extraction successful, text length:', extractionResult.text?.length);
              doc.content = { 
                type: 'text', 
                data: extractionResult.text,
                source: extractionResult.source || 'extracted'
              };
              
              // Update the document in the list to show extracted text is available
              setDocuments(prev => prev.map(d => 
                (d.id || d.name || d.originalName) === (doc.id || doc.name || doc.originalName) ? { ...d, hasExtractedText: true } : d
              ));
              
              // Force a re-render to ensure UI updates
              setForceUpdate(prev => prev + 1);
              
              // Also refresh from backend after a short delay to ensure sync
              setTimeout(() => {
                loadFiles();
              }, 100);
              
            } else {
              // Fallback to PDF viewer if text extraction fails
              doc.content = { type: 'pdf', data: doc.blobUrl };
            }
          } catch (extractionError) {
            console.warn('Text extraction failed, using PDF viewer:', extractionError);
            doc.content = { type: 'pdf', data: doc.blobUrl };
            
            // Show error to user
            setError(`Text extraction failed: ${extractionError.message}`);
          }
        }
      } else if (doc.type && doc.type.includes('image/')) {
        doc.content = { type: 'image', data: doc.blobUrl };
      } else if ((doc.type && doc.type.includes('spreadsheet')) || (doc.name && (doc.name.endsWith('.xlsx') || doc.name.endsWith('.xls')))) {
        doc.content = { type: 'spreadsheet', data: 'Excel file - content preview not available' };
      } else if ((doc.type && doc.type.includes('word')) || (doc.name && (doc.name.endsWith('.docx') || doc.name.endsWith('.doc')))) {
        // Check if text has already been extracted
        if (doc.hasExtractedText) {
          console.log('Text already extracted for Word document, fetching cached text');
          try {
            const extractionResult = await extractText(doc.id || doc.name || doc.originalName);
            if (extractionResult.success) {
              doc.content = { 
                type: 'text', 
                data: extractionResult.text,
                source: extractionResult.source || 'cached'
              };
            } else {
              doc.content = { type: 'word', data: 'Word document - content preview not available' };
            }
          } catch (error) {
            console.warn('Failed to fetch cached text:', error);
            doc.content = { type: 'word', data: 'Word document - content preview not available' };
          }
        } else {
          // Try to extract text from Word documents
          try {
            console.log('Starting Word text extraction for:', doc.id || doc.name || doc.originalName);
            const extractionResult = await extractText(doc.id || doc.name || doc.originalName);
            console.log('Word extraction result:', extractionResult);
            
            if (extractionResult.success) {
              console.log('Word extraction successful, text length:', extractionResult.text?.length);
              doc.content = { 
                type: 'text', 
                data: extractionResult.text,
                source: extractionResult.source || 'extracted'
              };
              
              // Update the document in the list to show extracted text is available
              setDocuments(prev => prev.map(d => 
                (d.id || d.name || d.originalName) === (doc.id || doc.name || doc.originalName) ? { ...d, hasExtractedText: true } : d
              ));
              
              // Force a re-render to ensure UI updates
              setForceUpdate(prev => prev + 1);
              
              // Also refresh from backend after a short delay to ensure sync
              setTimeout(() => {
                loadFiles();
              }, 100);
              
            } else {
              doc.content = { type: 'word', data: 'Word document - content preview not available' };
            }
          } catch (extractionError) {
            console.warn('Text extraction failed:', extractionError);
            doc.content = { type: 'word', data: 'Word document - content preview not available' };
            
            // Show error to user
            setError(`Text extraction failed: ${extractionError.message}`);
          }
        }
      } else {
        doc.content = { type: 'unknown', data: 'File type not supported for preview' };
      }
      
      setSelectedDocument(doc);
      
    } catch (err) {
      console.error('Error loading document content:', err);
      setError('Failed to load document content');
    }
  }, [loadFiles]);

  const clearMessages = useCallback(() => {
    setError(null);
    setSuccess(null);
  }, []);

  return {
    // State
    documents,
    selectedDocument,
    loading,
    isLoadingFiles,
    error,
    success,
    forceUpdate,
    
    // Actions
    loadFiles,
    handleUpload,
    handleDeleteDocument,
    handleViewDocument,
    setSelectedDocument,
    clearMessages
  };
};
