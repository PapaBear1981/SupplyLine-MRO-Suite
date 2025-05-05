import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Modal, Button, Form, Alert } from 'react-bootstrap';
import { removeToolFromService } from '../../store/toolsSlice';

const RemoveFromServiceModal = ({ show, onHide, tool }) => {
  const dispatch = useDispatch();
  const { serviceLoading, serviceError } = useSelector((state) => state.tools);
  
  const [actionType, setActionType] = useState('remove_maintenance');
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
      action_type: actionType,
      reason,
      comments
    };
    
    dispatch(removeToolFromService({ id: tool.id, data }))
      .unwrap()
      .then(() => {
        onHide();
        // Reset form
        setActionType('remove_maintenance');
        setReason('');
        setComments('');
        setValidated(false);
      })
      .catch((err) => {
        console.error('Failed to remove tool from service:', err);
      });
  };
  
  return (
    <Modal show={show} onHide={onHide} centered>
      <Modal.Header closeButton>
        <Modal.Title>Remove Tool from Service</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {serviceError && (
          <Alert variant="danger">
            {serviceError.error || 'Failed to remove tool from service'}
          </Alert>
        )}
        
        <p>
          <strong>Tool:</strong> {tool?.tool_number} - {tool?.serial_number}
        </p>
        
        <Form noValidate validated={validated} onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Action Type</Form.Label>
            <Form.Select
              value={actionType}
              onChange={(e) => setActionType(e.target.value)}
              required
            >
              <option value="remove_maintenance">Temporary Removal (Maintenance/Calibration)</option>
              <option value="remove_permanent">Permanent Removal (Retired)</option>
            </Form.Select>
            <Form.Text className="text-muted">
              {actionType === 'remove_maintenance' 
                ? 'Tool will be temporarily removed from service for maintenance or calibration.' 
                : 'Tool will be permanently removed from service (retired).'}
            </Form.Text>
          </Form.Group>
          
          <Form.Group className="mb-3">
            <Form.Label>Reason*</Form.Label>
            <Form.Control
              as="textarea"
              rows={2}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              required
              placeholder="Enter reason for removing tool from service"
            />
            <Form.Control.Feedback type="invalid">
              Please provide a reason for removing this tool from service.
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
          variant="danger" 
          onClick={handleSubmit}
          disabled={serviceLoading}
        >
          {serviceLoading ? 'Processing...' : 'Remove from Service'}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default RemoveFromServiceModal;
