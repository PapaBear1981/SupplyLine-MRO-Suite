import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useDispatch, useSelector } from 'react-redux';
import { Modal, Button, Form, Alert, InputGroup, Badge } from 'react-bootstrap';
import { checkoutTool, checkoutToolToUser } from '../../store/checkoutsSlice';
import { fetchUsers, searchUsersByEmployeeNumber } from '../../store/usersSlice';

const MobileCheckoutModal = ({ show, onHide, tool }) => {
  const dispatch = useDispatch();
  const { users, loading: usersLoading } = useSelector((state) => state.users);
  const { loading: checkoutLoading, error } = useSelector((state) => state.checkouts);
  const { user: currentUser } = useSelector((state) => state.auth);

  const [checkoutType, setCheckoutType] = useState('self'); // 'self' or 'other'
  const [selectedUserId, setSelectedUserId] = useState('');
  const [expectedReturnDate, setExpectedReturnDate] = useState('');
  const [validated, setValidated] = useState(false);
  const [employeeNumberSearch, setEmployeeNumberSearch] = useState('');
  const [searchError, setSearchError] = useState('');

  // Set default expected return date to 7 days from now
  useEffect(() => {
    const date = new Date();
    date.setDate(date.getDate() + 7);
    setExpectedReturnDate(date.toISOString().split('T')[0]);
  }, []);

  // Load users when modal opens and checkout type is 'other'
  useEffect(() => {
    if (show && checkoutType === 'other') {
      dispatch(fetchUsers());
    }
  }, [dispatch, show, checkoutType]);

  // Reset form when modal closes
  useEffect(() => {
    if (!show) {
      setCheckoutType('self');
      setSelectedUserId('');
      setEmployeeNumberSearch('');
      setSearchError('');
      setValidated(false);
    }
  }, [show]);

  // Handle employee number search
  const handleEmployeeNumberSearch = () => {
    setSearchError('');
    if (employeeNumberSearch.trim()) {
      dispatch(searchUsersByEmployeeNumber(employeeNumberSearch.trim()))
        .unwrap()
        .then((result) => {
          // If only one user is found, auto-select them
          if (result.length === 1) {
            setSelectedUserId(result[0].id.toString());
          } else if (result.length === 0) {
            setSearchError('No users found with that employee number');
          }
        })
        .catch((error) => {
          console.error('Error searching for users:', error);
          setSearchError('Failed to search for users. Please try again.');
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

    // Determine which checkout action to dispatch
    const checkoutAction = checkoutType === 'self'
      ? checkoutTool({
          toolId: tool.id,
          expectedReturnDate
        })
      : checkoutToolToUser({
          toolId: tool.id,
          userId: selectedUserId,
          expectedReturnDate
        });

    dispatch(checkoutAction)
      .unwrap()
      .then(() => {
        setValidated(false);
        onHide();
        // Optionally show success message or refresh data
      })
      .catch((err) => {
        console.error('Checkout failed:', err);
      });
  };

  if (!tool) return null;

  return (
    <Modal show={show} onHide={onHide} centered className="mobile-modal">
      <Modal.Header closeButton>
        <Modal.Title>
          <i className="bi bi-clipboard-check me-2"></i>
          Checkout Tool
        </Modal.Title>
      </Modal.Header>
      <Form noValidate validated={validated} onSubmit={handleSubmit}>
        <Modal.Body>
          {error && <Alert variant="danger">{error.message}</Alert>}

          {/* Tool Information */}
          <div className="mb-3 p-3 bg-body-secondary rounded border">
            <h6 className="mb-2">
              <i className="bi bi-tools me-2"></i>
              Tool Information
            </h6>
            <div className="mb-1">
              <strong>Tool:</strong> {tool.description}
            </div>
            <div className="mb-1">
              <strong>Number:</strong> {tool.tool_number} • {tool.serial_number}
            </div>
            <div className="mb-1">
              <strong>Location:</strong> {tool.location || 'Not specified'}
            </div>
            <div>
              <Badge bg="success">
                <i className="bi bi-check-circle me-1"></i>
                Available
              </Badge>
            </div>
          </div>

          {/* Checkout Type Selection */}
          <Form.Group className="mb-3">
            <Form.Label>
              <i className="bi bi-person me-2"></i>
              Checkout To
            </Form.Label>
            <div className="d-flex gap-2">
              <Button
                variant={checkoutType === 'self' ? 'primary' : 'outline-primary'}
                size="sm"
                className="flex-fill"
                onClick={() => setCheckoutType('self')}
                type="button"
              >
                <i className="bi bi-person-check me-1"></i>
                Myself
              </Button>
              <Button
                variant={checkoutType === 'other' ? 'primary' : 'outline-primary'}
                size="sm"
                className="flex-fill"
                onClick={() => setCheckoutType('other')}
                type="button"
              >
                <i className="bi bi-people me-1"></i>
                Another User
              </Button>
            </div>
          </Form.Group>

          {/* User Selection (only shown when checking out to another user) */}
          {checkoutType === 'other' && (
            <>
              <Form.Group className="mb-3">
                <Form.Label>Search by Employee Number</Form.Label>
                <InputGroup>
                  <Form.Control
                    type="text"
                    placeholder="Enter employee number..."
                    value={employeeNumberSearch}
                    onChange={(e) => setEmployeeNumberSearch(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleEmployeeNumberSearch()}
                  />
                  <Button
                    variant="outline-secondary"
                    onClick={handleEmployeeNumberSearch}
                    disabled={usersLoading}
                  >
                    <i className="bi bi-search"></i>
                  </Button>
                  <Button
                    variant="outline-secondary"
                    onClick={() => {
                      setEmployeeNumberSearch('');
                      dispatch(fetchUsers());
                    }}
                    disabled={usersLoading}
                  >
                    <i className="bi bi-x"></i>
                  </Button>
                </InputGroup>
                {searchError && (
                  <div className="text-danger small mt-1">
                    <i className="bi bi-exclamation-triangle me-1"></i>
                    {searchError}
                  </div>
                )}
              </Form.Group>

              <Form.Group className="mb-3" controlId="userId">
                <Form.Label>Select User</Form.Label>
                {usersLoading ? (
                  <div className="text-center py-2">
                    <div className="spinner-border spinner-border-sm" role="status">
                      <span className="visually-hidden">Loading...</span>
                    </div>
                  </div>
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
            </>
          )}

          {/* Expected Return Date */}
          <Form.Group className="mb-3" controlId="expectedReturnDate">
            <Form.Label>
              <i className="bi bi-calendar me-2"></i>
              Expected Return Date
            </Form.Label>
            <Form.Control
              type="date"
              value={expectedReturnDate}
              onChange={(e) => setExpectedReturnDate(e.target.value)}
              required
              min={new Date().toISOString().split('T')[0]}
              max={new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]}
            />
            <Form.Control.Feedback type="invalid">
              Please select a valid expected return date (today or later, within one year).
            </Form.Control.Feedback>
            <Form.Text className="text-muted">
              Default is 7 days from today. Maximum checkout period is one year.
            </Form.Text>
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={onHide} disabled={checkoutLoading}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="success"
            disabled={checkoutLoading || (checkoutType === 'other' && !selectedUserId)}
          >
            {checkoutLoading ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Checking out...
              </>
            ) : (
              <>
                <i className="bi bi-clipboard-check me-2"></i>
                Checkout Tool
              </>
            )}
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
};

MobileCheckoutModal.propTypes = {
  show: PropTypes.bool.isRequired,
  onHide: PropTypes.func.isRequired,
  tool: PropTypes.object,
};

export default MobileCheckoutModal;
