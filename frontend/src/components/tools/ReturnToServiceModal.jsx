import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Modal, Button, Form, Alert } from 'react-bootstrap';
import { returnToolToService } from '../../store/toolsSlice';

const ReturnToServiceModal = ({ show, onHide, tool }) => {
  const dispatch = useDispatch();
  const { serviceLoading, serviceError } = useSelector((state) => state.tools);
  
  const [reason, setReason] = useState('');
  const [comments, setComments] = useState('');
  const [validated, setValidated] = useState(false);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    
    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }
    
    setValidated(true);
    
    const data = {
      reason,
      comments
    };
    
    dispatch(returnToolToService({ id: tool.id, data }))
      .unwrap()
      .then(() => {
        onHide();
        // Reset form
        setReason('');
        setComments('');
        setValidated(false);
      })
      .catch((err) => {
        console.error('Failed to return tool to service:', err);
      });
  };
  
  return (
    <Modal show={show} onHide={onHide} centered>
      <Modal.Header closeButton>
        <Modal.Title>Return Tool to Service</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {serviceError && (
          <Alert variant="danger">
            {serviceError.error || 'Failed to return tool to service'}
          </Alert>
        )}
        
        <p>
          <strong>Tool:</strong> {tool?.tool_number} - {tool?.serial_number}
        </p>
        <p>
          <strong>Current Status:</strong> {tool?.status === 'maintenance' ? 'Maintenance/Calibration' : 'Retired'}
        </p>
        <p>
          <strong>Reason for Removal:</strong> {tool?.status_reason}
        </p>
        
        <Form noValidate validated={validated} onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Reason for Return*</Form.Label>
            <Form.Control
              as="textarea"
              rows={2}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              required
              placeholder="Enter reason for returning tool to service"
            />
            <Form.Control.Feedback type="invalid">
              Please provide a reason for returning this tool to service.
            </Form.Control.Feedback>
          </Form.Group>
          
          <Form.Group className="mb-3">
            <Form.Label>Additional Comments</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              placeholder="Enter any additional comments or details"
            />
          </Form.Group>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Cancel
        </Button>
        <Button 
          variant="success" 
          onClick={handleSubmit}
          disabled={serviceLoading}
        >
          {serviceLoading ? 'Processing...' : 'Return to Service'}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ReturnToServiceModal;
