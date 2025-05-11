import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Modal, Button, Form, Alert, InputGroup } from 'react-bootstrap';
import { checkoutToolToUser } from '../../store/checkoutsSlice';
import { fetchUsers, searchUsersByEmployeeNumber } from '../../store/usersSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const CheckoutModal = ({ show, onHide, tool }) => {
  const dispatch = useDispatch();
  const { users, loading: usersLoading } = useSelector((state) => state.users);
  const { loading: checkoutLoading, error } = useSelector((state) => state.checkouts);
  const { user: currentUser } = useSelector((state) => state.auth);

  const [selectedUserId, setSelectedUserId] = useState('');
  const [expectedReturnDate, setExpectedReturnDate] = useState('');
  const [validated, setValidated] = useState(false);
  const [employeeNumberSearch, setEmployeeNumberSearch] = useState('');

  // Fetch users when modal opens
  useEffect(() => {
    if (show) {
      dispatch(fetchUsers());

      // Set default expected return date to 7 days from now
      const date = new Date();
      date.setDate(date.getDate() + 7);
      setExpectedReturnDate(date.toISOString().split('T')[0]);

      // Reset search and selection when modal opens
      setEmployeeNumberSearch('');
      setSelectedUserId('');
    }
  }, [dispatch, show]);

  // Handle employee number search
  const handleEmployeeNumberSearch = () => {
    if (employeeNumberSearch.trim()) {
      dispatch(searchUsersByEmployeeNumber(employeeNumberSearch.trim()))
        .unwrap()
        .then((result) => {
          // If only one user is found, auto-select them
          if (result.length === 1) {
            setSelectedUserId(result[0].id.toString());
          }
        })
        .catch((error) => {
          console.error('Error searching for users:', error);
        });
    } else {
      dispatch(fetchUsers());
    }
  };

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

          <Form.Group className="mb-3" controlId="employeeNumberSearch">
            <Form.Label>Search by Employee Number</Form.Label>
            <InputGroup className="mb-2">
              <Form.Control
                type="text"
                placeholder="Enter employee number"
                value={employeeNumberSearch}
                onChange={(e) => setEmployeeNumberSearch(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleEmployeeNumberSearch();
                  }
                }}
              />
              <Button
                variant="outline-secondary"
                onClick={handleEmployeeNumberSearch}
                disabled={usersLoading}
              >
                Search
              </Button>
              <Button
                variant="outline-secondary"
                onClick={() => {
                  setEmployeeNumberSearch('');
                  dispatch(fetchUsers());
                }}
                disabled={usersLoading}
              >
                Clear
              </Button>
            </InputGroup>
            <Form.Text className="text-muted">
              Search for a specific employee number or leave blank to see all users
            </Form.Text>
          </Form.Group>

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
