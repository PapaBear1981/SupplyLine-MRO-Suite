import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { Form, Button, Card, Alert, Badge } from 'react-bootstrap';
import { fetchChemicalById, issueChemical } from '../../store/chemicalsSlice';
import { fetchUsers } from '../../store/usersSlice';
import LoadingSpinner from '../common/LoadingSpinner';
import ChemicalBarcode from './ChemicalBarcode';

const ChemicalIssueForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { currentChemical, loading: chemicalLoading, error: chemicalError } = useSelector((state) => state.chemicals);
  const { users, loading: usersLoading } = useSelector((state) => state.users);
  const { user: currentUser } = useSelector((state) => state.auth);

  const [issueData, setIssueData] = useState({
    quantity: '',
    hangar: '',
    purpose: '',
    user_id: ''
  });
  const [validated, setValidated] = useState(false);
  const [error, setError] = useState(null);
  const [showBarcodeModal, setShowBarcodeModal] = useState(false);
  const [childChemical, setChildChemical] = useState(null);

  useEffect(() => {
    if (id) {
      dispatch(fetchChemicalById(id));
      dispatch(fetchUsers());
    }
  }, [dispatch, id]);

  useEffect(() => {
    // Set current user as default if available
    if (currentUser) {
      setIssueData(prev => ({
        ...prev,
        user_id: currentUser.id
      }));
    }
  }, [currentUser]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setIssueData(prev => ({
      ...prev,
      [name]: value
    }));
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

    // Validate quantity - must be a whole number
    const quantity = parseInt(issueData.quantity);
    if (isNaN(quantity) || quantity <= 0) {
      setError('Quantity must be a positive whole number');
      return;
    }

    if (quantity > currentChemical.quantity) {
      setError(`Cannot issue more than available quantity (${currentChemical.quantity} ${currentChemical.unit})`);
      return;
    }

    // Clear any previous errors
    setError(null);

    // Format data for API
    const formattedData = {
      ...issueData,
      quantity: quantity,
      user_id: parseInt(issueData.user_id) // Ensure user_id is an integer
    };

    dispatch(issueChemical({ id, data: formattedData }))
      .unwrap()
      .then((response) => {
        // Check if a child lot was created (partial issue)
        if (response.child_chemical) {
          // Show barcode modal for the child lot
          setChildChemical(response.child_chemical);
          setShowBarcodeModal(true);
        } else {
          // Full consumption - navigate directly back
          navigate(`/chemicals/${id}`);
        }
      })
      .catch((err) => {
        console.error('Failed to issue chemical:', err);
        setError(err.message || 'Failed to issue chemical');
      });
  };

  if (chemicalLoading && !currentChemical) {
    return <LoadingSpinner />;
  }

  if (chemicalError) {
    return <Alert variant="danger">{chemicalError.message}</Alert>;
  }

  if (!currentChemical) {
    return <Alert variant="warning">Chemical not found</Alert>;
  }

  // Check if chemical can be issued
  if (currentChemical.status === 'out_of_stock') {
    return (
      <Alert variant="danger">
        This chemical is out of stock and cannot be issued.
      </Alert>
    );
  }

  if (currentChemical.status === 'expired') {
    return (
      <Alert variant="danger">
        This chemical has expired and cannot be issued.
      </Alert>
    );
  }

  // Format status for display
  const formatStatus = (status) => {
    return status
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <>
      <Card className="shadow-sm">
        <Card.Header>
          <h4>Issue Chemical: {currentChemical.part_number} - {currentChemical.lot_number}</h4>
        </Card.Header>
        <Card.Body>
          {error && <Alert variant="danger">{error}</Alert>}

        <div className="mb-4">
          <h5>Chemical Information</h5>
          <hr />
          <p>
            <strong>Part Number:</strong> {currentChemical.part_number}
          </p>
          <p>
            <strong>Lot Number:</strong> {currentChemical.lot_number}
          </p>
          <p>
            <strong>Description:</strong> {currentChemical.description || 'N/A'}
          </p>
          <p>
            <strong>Available Quantity:</strong> {currentChemical.quantity} {currentChemical.unit}
          </p>
          <p>
            <strong>Status:</strong>{' '}
            <Badge
              bg={
                currentChemical.status === 'available'
                  ? 'success'
                  : currentChemical.status === 'low_stock'
                  ? 'warning'
                  : 'danger'
              }
            >
              {formatStatus(currentChemical.status)}
            </Badge>
          </p>
          {currentChemical.status === 'low_stock' && (
            <Alert variant="warning">
              This chemical is running low. Current quantity is below the minimum stock level of{' '}
              {currentChemical.minimum_stock_level} {currentChemical.unit}.
            </Alert>
          )}
        </div>

        <Form noValidate validated={validated} onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Quantity to Issue*</Form.Label>
            <Form.Control
              type="number"
              step="1"
              min="1"
              max={currentChemical.quantity}
              name="quantity"
              value={issueData.quantity}
              onChange={handleChange}
              required
            />
            <Form.Control.Feedback type="invalid">
              Please enter a valid whole number quantity (greater than 0 and not more than available)
            </Form.Control.Feedback>
            <Form.Text className="text-muted">
              Maximum available: {currentChemical.quantity} {currentChemical.unit}. Only whole numbers allowed.
            </Form.Text>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Hangar/Location*</Form.Label>
            <Form.Control
              type="text"
              name="hangar"
              value={issueData.hangar}
              onChange={handleChange}
              required
            />
            <Form.Control.Feedback type="invalid">
              Please specify where this chemical will be used
            </Form.Control.Feedback>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Purpose</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              name="purpose"
              value={issueData.purpose}
              onChange={handleChange}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Issued To*</Form.Label>
            <Form.Select
              name="user_id"
              value={issueData.user_id}
              onChange={handleChange}
              required
              disabled={usersLoading}
            >
              <option value="">Select User</option>
              {users &&
                users.map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.name} ({user.department})
                  </option>
                ))}
            </Form.Select>
            <Form.Control.Feedback type="invalid">
              Please select a user
            </Form.Control.Feedback>
          </Form.Group>

          <div className="d-flex justify-content-end gap-2">
            <Button variant="secondary" onClick={() => navigate(`/chemicals/${id}`)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={chemicalLoading}>
              {chemicalLoading ? 'Processing...' : 'Issue Chemical'}
            </Button>
          </div>
        </Form>
      </Card.Body>
    </Card>

    {/* Barcode modal for child lot */}
    {childChemical && (
      <ChemicalBarcode
        show={showBarcodeModal}
        onHide={() => {
          setShowBarcodeModal(false);
          // Navigate back to the parent chemical detail page after closing modal
          navigate(`/chemicals/${id}`);
        }}
        chemical={childChemical}
      />
    )}
    </>
  );
};

export default ChemicalIssueForm;
