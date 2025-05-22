import { useState } from 'react';
import { Modal, Button, Form, Alert, Spinner } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faExclamationTriangle, faTrash, faArchive } from '@fortawesome/free-solid-svg-icons';

const DeleteToolModal = ({ show, onHide, tool, onDelete, onRetire }) => {
  const [step, setStep] = useState(1); // 1: initial warning, 2: choose action, 3: confirm delete, 4: confirm retire
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [retireReason, setRetireReason] = useState('');
  const [retireComments, setRetireComments] = useState('');
  const [forceDelete, setForceDelete] = useState(false);
  const [toolHistory, setToolHistory] = useState(null);

  const handleClose = () => {
    setStep(1);
    setLoading(false);
    setError('');
    setRetireReason('');
    setRetireComments('');
    setForceDelete(false);
    setToolHistory(null);
    onHide();
  };

  const checkToolHistory = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`/api/tools/${tool.id}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ force_delete: false })
      });

      const data = await response.json();
      
      if (response.ok) {
        // Tool can be deleted without issues
        setStep(3);
      } else if (data.has_history) {
        // Tool has history, show options
        setToolHistory(data);
        setStep(2);
      } else {
        setError(data.error || 'Failed to check tool history');
      }
    } catch (err) {
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`/api/tools/${tool.id}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ force_delete: forceDelete })
      });

      const data = await response.json();
      
      if (response.ok) {
        onDelete(tool.id);
        handleClose();
      } else {
        setError(data.error || 'Failed to delete tool');
      }
    } catch (err) {
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleRetire = async () => {
    if (!retireReason.trim()) {
      setError('Please provide a reason for retiring the tool');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`/api/tools/${tool.id}/retire`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          reason: retireReason,
          comments: retireComments
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        onRetire(data.tool);
        handleClose();
      } else {
        setError(data.error || 'Failed to retire tool');
      }
    } catch (err) {
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const renderStep1 = () => (
    <>
      <Modal.Header closeButton>
        <Modal.Title>
          <FontAwesomeIcon icon={faExclamationTriangle} className="text-warning me-2" />
          Delete Tool
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Alert variant="warning">
          <FontAwesomeIcon icon={faExclamationTriangle} className="me-2" />
          <strong>Warning!</strong> You are about to delete tool "{tool?.tool_number}".
        </Alert>
        <p>
          <strong>Tool Details:</strong>
        </p>
        <ul>
          <li><strong>Tool Number:</strong> {tool?.tool_number}</li>
          <li><strong>Serial Number:</strong> {tool?.serial_number}</li>
          <li><strong>Description:</strong> {tool?.description || 'N/A'}</li>
          <li><strong>Category:</strong> {tool?.category || 'General'}</li>
        </ul>
        <p className="text-muted">
          We need to check if this tool has any history before proceeding.
        </p>
        {error && <Alert variant="danger">{error}</Alert>}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Cancel
        </Button>
        <Button 
          variant="warning" 
          onClick={checkToolHistory}
          disabled={loading}
        >
          {loading ? (
            <>
              <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" className="me-1" />
              Checking...
            </>
          ) : 'Continue'}
        </Button>
      </Modal.Footer>
    </>
  );

  const renderStep2 = () => (
    <>
      <Modal.Header closeButton>
        <Modal.Title>
          <FontAwesomeIcon icon={faExclamationTriangle} className="text-warning me-2" />
          Tool Has History
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Alert variant="info">
          <FontAwesomeIcon icon={faExclamationTriangle} className="me-2" />
          This tool has history and cannot be safely deleted without losing data.
        </Alert>
        
        <p><strong>Tool History Found:</strong></p>
        <ul>
          {toolHistory?.has_checkouts && <li>Checkout history</li>}
          {toolHistory?.has_calibrations && <li>Calibration records</li>}
          {toolHistory?.has_service_records && <li>Service records</li>}
        </ul>

        <p className="text-info">
          <FontAwesomeIcon icon={faArchive} className="me-2" />
          <strong>Recommended:</strong> Retire the tool instead to preserve its history.
        </p>

        {error && <Alert variant="danger">{error}</Alert>}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Cancel
        </Button>
        <Button 
          variant="info" 
          onClick={() => setStep(4)}
        >
          <FontAwesomeIcon icon={faArchive} className="me-1" />
          Retire Tool (Recommended)
        </Button>
        <Button 
          variant="danger" 
          onClick={() => {
            setForceDelete(true);
            setStep(3);
          }}
        >
          <FontAwesomeIcon icon={faTrash} className="me-1" />
          Force Delete (Loses History)
        </Button>
      </Modal.Footer>
    </>
  );

  const renderStep3 = () => (
    <>
      <Modal.Header closeButton>
        <Modal.Title>
          <FontAwesomeIcon icon={faTrash} className="text-danger me-2" />
          Confirm Deletion
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Alert variant="danger">
          <FontAwesomeIcon icon={faExclamationTriangle} className="me-2" />
          <strong>FINAL WARNING!</strong> This action cannot be undone.
        </Alert>
        
        {forceDelete && (
          <Alert variant="warning">
            <strong>Force Delete:</strong> This will permanently delete the tool and ALL its history including:
            <ul className="mb-0 mt-2">
              <li>All checkout records</li>
              <li>All calibration records</li>
              <li>All service records</li>
            </ul>
          </Alert>
        )}

        <p>
          Are you absolutely sure you want to delete tool "{tool?.tool_number}"?
        </p>

        {error && <Alert variant="danger">{error}</Alert>}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={() => setStep(forceDelete ? 2 : 1)}>
          Go Back
        </Button>
        <Button 
          variant="danger" 
          onClick={handleDelete}
          disabled={loading}
        >
          {loading ? (
            <>
              <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" className="me-1" />
              Deleting...
            </>
          ) : (
            <>
              <FontAwesomeIcon icon={faTrash} className="me-1" />
              Yes, Delete Tool
            </>
          )}
        </Button>
      </Modal.Footer>
    </>
  );

  const renderStep4 = () => (
    <>
      <Modal.Header closeButton>
        <Modal.Title>
          <FontAwesomeIcon icon={faArchive} className="text-info me-2" />
          Retire Tool
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Alert variant="info">
          <FontAwesomeIcon icon={faArchive} className="me-2" />
          Retiring the tool will preserve all history while marking it as no longer in service.
        </Alert>
        
        <Form>
          <Form.Group className="mb-3">
            <Form.Label>Reason for Retirement <span className="text-danger">*</span></Form.Label>
            <Form.Control
              type="text"
              value={retireReason}
              onChange={(e) => setRetireReason(e.target.value)}
              placeholder="e.g., End of life, Replaced by newer model, Damaged beyond repair"
              required
            />
          </Form.Group>
          
          <Form.Group className="mb-3">
            <Form.Label>Additional Comments</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              value={retireComments}
              onChange={(e) => setRetireComments(e.target.value)}
              placeholder="Any additional notes about the retirement..."
            />
          </Form.Group>
        </Form>

        {error && <Alert variant="danger">{error}</Alert>}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={() => setStep(2)}>
          Go Back
        </Button>
        <Button 
          variant="info" 
          onClick={handleRetire}
          disabled={loading || !retireReason.trim()}
        >
          {loading ? (
            <>
              <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" className="me-1" />
              Retiring...
            </>
          ) : (
            <>
              <FontAwesomeIcon icon={faArchive} className="me-1" />
              Retire Tool
            </>
          )}
        </Button>
      </Modal.Footer>
    </>
  );

  return (
    <Modal show={show} onHide={handleClose} size="lg">
      {step === 1 && renderStep1()}
      {step === 2 && renderStep2()}
      {step === 3 && renderStep3()}
      {step === 4 && renderStep4()}
    </Modal>
  );
};

export default DeleteToolModal;
