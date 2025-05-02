import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Modal, Button, Form, Alert } from 'react-bootstrap';
import { checkoutToolToUser } from '../../store/checkoutsSlice';
import { fetchUsers } from '../../store/usersSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const CheckoutModal = ({ show, onHide, tool }) => {
  const dispatch = useDispatch();
  const { users, loading: usersLoading } = useSelector((state) => state.users);
  const { loading: checkoutLoading, error } = useSelector((state) => state.checkouts);
  const { user: currentUser } = useSelector((state) => state.auth);
  
  const [selectedUserId, setSelectedUserId] = useState('');
  const [expectedReturnDate, setExpectedReturnDate] = useState('');
  const [validated, setValidated] = useState(false);
  
  // Fetch users when modal opens
  useEffect(() => {
    if (show) {
      dispatch(fetchUsers());
      
      // Set default expected return date to 7 days from now
      const date = new Date();
      date.setDate(date.getDate() + 7);
      setExpectedReturnDate(date.toISOString().split('T')[0]);
    }
  }, [dispatch, show]);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    
    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }
    
    setValidated(true);
    
    dispatch(checkoutToolToUser({
      toolId: tool.id,
      userId: selectedUserId,
      expectedReturnDate
    })).unwrap()
      .then(() => {
        onHide();
      })
      .catch((err) => {
        console.error('Checkout failed:', err);
      });
  };
  
  // Check if current user has permission to checkout tools to others
  const hasCheckoutPermission = currentUser?.is_admin || currentUser?.department === 'Materials';
  
  if (!hasCheckoutPermission) {
    return (
      <Modal show={show} onHide={onHide} centered>
        <Modal.Header closeButton>
          <Modal.Title>Permission Denied</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Alert variant="danger">
            You do not have permission to check out tools to other users. 
            Only administrators and Materials department users can perform this action.
          </Alert>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={onHide}>Close</Button>
        </Modal.Footer>
      </Modal>
    );
  }
  
  return (
    <Modal show={show} onHide={onHide} centered>
      <Modal.Header closeButton>
        <Modal.Title>Checkout Tool to User</Modal.Title>
      </Modal.Header>
      <Form noValidate validated={validated} onSubmit={handleSubmit}>
        <Modal.Body>
          {error && <Alert variant="danger">{error.message}</Alert>}
          
          <div className="mb-3">
            <strong>Tool:</strong> {tool?.tool_number} - {tool?.description}
          </div>
          
          <Form.Group className="mb-3" controlId="userId">
            <Form.Label>Select User</Form.Label>
            {usersLoading ? (
              <LoadingSpinner size="sm" />
            ) : (
              <Form.Select 
                value={selectedUserId}
                onChange={(e) => setSelectedUserId(e.target.value)}
                required
              >
                <option value="">Select a user...</option>
                {users.map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.name} ({user.employee_number}) - {user.department}
                  </option>
                ))}
              </Form.Select>
            )}
            <Form.Control.Feedback type="invalid">
              Please select a user.
            </Form.Control.Feedback>
          </Form.Group>
          
          <Form.Group className="mb-3" controlId="expectedReturnDate">
            <Form.Label>Expected Return Date</Form.Label>
            <Form.Control
              type="date"
              value={expectedReturnDate}
              onChange={(e) => setExpectedReturnDate(e.target.value)}
              required
            />
            <Form.Control.Feedback type="invalid">
              Please provide an expected return date.
            </Form.Control.Feedback>
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={onHide}>
            Cancel
          </Button>
          <Button 
            variant="primary" 
            type="submit"
            disabled={checkoutLoading}
          >
            {checkoutLoading ? 'Processing...' : 'Checkout Tool'}
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
};

export default CheckoutModal;
