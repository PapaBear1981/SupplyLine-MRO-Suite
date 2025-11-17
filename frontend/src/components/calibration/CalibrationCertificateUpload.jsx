import { useState } from 'react';
import { Form, Button, Alert, Spinner, Card } from 'react-bootstrap';
import api from '../../services/api';

const CalibrationCertificateUpload = ({ toolId, calibrationId, onSuccess }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file to upload');
      return;
    }
    
    // Check file type
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
    if (!allowedTypes.includes(file.type)) {
      setError('Only PDF, JPEG, JPG, and PNG files are allowed');
      return;
    }
    
    // Check file size (max 5MB)
    const maxSize = 5 * 1024 * 1024; // 5MB in bytes
    if (file.size > maxSize) {
      setError('File size must be less than 5MB');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Create form data
      const formData = new FormData();
      formData.append('certificate', file);
      
      // Upload certificate
      const response = await api.post(
        `/tools/${toolId}/calibrations/${calibrationId}/certificate`,
        formData
        // Don't set Content-Type header manually - axios will automatically
        // set it with the correct boundary when it detects FormData
      );
      
      setSuccess(true);
      
      // Call onSuccess callback if provided
      if (onSuccess && typeof onSuccess === 'function') {
        onSuccess(response.data);
      }
      
      // Reset form after successful upload
      setFile(null);
      
      // Reset success message after 3 seconds
      setTimeout(() => {
        setSuccess(false);
      }, 3000);
    } catch (err) {
      console.error('Error uploading certificate:', err);
      setError(err.response?.data?.error || 'Failed to upload certificate');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Card>
      <Card.Header>
        <h5 className="mb-0">Upload Calibration Certificate</h5>
      </Card.Header>
      <Card.Body>
        {error && (
          <Alert variant="danger" dismissible onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
        
        {success && (
          <Alert variant="success" dismissible onClose={() => setSuccess(false)}>
            Certificate uploaded successfully!
          </Alert>
        )}
        
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Certificate File</Form.Label>
            <Form.Control
              type="file"
              onChange={handleFileChange}
              accept=".pdf,.jpg,.jpeg,.png"
              disabled={loading}
            />
            <Form.Text className="text-muted">
              Upload calibration certificate (PDF, JPG, JPEG, PNG). Maximum file size: 5MB.
            </Form.Text>
          </Form.Group>
          
          <div className="d-flex justify-content-end">
            <Button
              type="submit"
              variant="primary"
              disabled={!file || loading}
            >
              {loading ? (
                <>
                  <Spinner
                    as="span"
                    animation="border"
                    size="sm"
                    role="status"
                    aria-hidden="true"
                    className="me-2"
                  />
                  Uploading...
                </>
              ) : (
                'Upload Certificate'
              )}
            </Button>
          </div>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default CalibrationCertificateUpload;
