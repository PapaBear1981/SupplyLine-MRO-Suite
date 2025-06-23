import { useState, useRef } from 'react';
import { Card, Button, Alert, ProgressBar, Form } from 'react-bootstrap';
import './FileUpload.css';

const FileUpload = ({ 
  onFileSelect, 
  acceptedTypes = '.csv', 
  maxSize = 5 * 1024 * 1024, // 5MB default
  title = 'Upload File',
  description = 'Drag and drop your file here, or click to browse',
  disabled = false,
  showProgress = false,
  progress = 0
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (disabled) return;
    
    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFileSelection(files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (disabled) return;
    
    const files = e.target.files;
    if (files && files[0]) {
      handleFileSelection(files[0]);
    }
  };

  const handleFileSelection = (file) => {
    setError('');
    
    // Check file type
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    const acceptedExtensions = acceptedTypes.split(',').map(type => type.trim().toLowerCase());
    
    if (!acceptedExtensions.includes(fileExtension)) {
      setError(`Invalid file type. Accepted types: ${acceptedTypes}`);
      return;
    }
    
    // Check file size
    if (file.size > maxSize) {
      const maxSizeMB = (maxSize / (1024 * 1024)).toFixed(1);
      setError(`File size too large. Maximum size: ${maxSizeMB}MB`);
      return;
    }
    
    setSelectedFile(file);
    if (onFileSelect) {
      onFileSelect(file);
    }
  };

  const handleBrowseClick = () => {
    if (disabled) return;
    fileInputRef.current?.click();
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    if (onFileSelect) {
      onFileSelect(null);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Card className={`file-upload-card ${disabled ? 'disabled' : ''}`}>
      <Card.Body>
        <div className="file-upload-container">
          <input
            ref={fileInputRef}
            type="file"
            accept={acceptedTypes}
            onChange={handleFileInput}
            style={{ display: 'none' }}
            disabled={disabled}
          />
          
          {!selectedFile ? (
            <div
              className={`file-upload-dropzone ${dragActive ? 'drag-active' : ''} ${disabled ? 'disabled' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={handleBrowseClick}
            >
              <div className="file-upload-content">
                <i className="bi bi-cloud-upload file-upload-icon"></i>
                <h5 className="file-upload-title">{title}</h5>
                <p className="file-upload-description">{description}</p>
                <Button 
                  variant="outline-primary" 
                  size="sm"
                  disabled={disabled}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleBrowseClick();
                  }}
                >
                  <i className="bi bi-folder2-open me-2"></i>
                  Browse Files
                </Button>
                <div className="file-upload-info mt-2">
                  <small className="text-muted">
                    Accepted: {acceptedTypes} • Max size: {(maxSize / (1024 * 1024)).toFixed(1)}MB
                  </small>
                </div>
              </div>
            </div>
          ) : (
            <div className="file-upload-selected">
              <div className="d-flex align-items-center justify-content-between">
                <div className="d-flex align-items-center">
                  <i className="bi bi-file-earmark-text file-selected-icon me-3"></i>
                  <div>
                    <div className="file-selected-name">{selectedFile.name}</div>
                    <div className="file-selected-size text-muted">
                      {formatFileSize(selectedFile.size)}
                    </div>
                  </div>
                </div>
                <Button
                  variant="outline-danger"
                  size="sm"
                  onClick={handleRemoveFile}
                  disabled={disabled}
                >
                  <i className="bi bi-trash"></i>
                </Button>
              </div>
              
              {showProgress && (
                <div className="mt-3">
                  <div className="d-flex justify-content-between align-items-center mb-1">
                    <small className="text-muted">Upload Progress</small>
                    <small className="text-muted">{progress}%</small>
                  </div>
                  <ProgressBar now={progress} variant={progress === 100 ? 'success' : 'primary'} />
                </div>
              )}
            </div>
          )}
          
          {error && (
            <Alert variant="danger" className="mt-3 mb-0">
              <i className="bi bi-exclamation-triangle me-2"></i>
              {error}
            </Alert>
          )}
        </div>
      </Card.Body>
    </Card>
  );
};

export default FileUpload;
