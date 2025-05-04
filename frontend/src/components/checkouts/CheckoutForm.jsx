import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { Form, Button, Card, Alert } from 'react-bootstrap';
import { fetchToolById } from '../../store/toolsSlice';
import { checkoutTool } from '../../store/checkoutsSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const CheckoutForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { currentTool, loading: toolLoading } = useSelector((state) => state.tools);
  const { loading: checkoutLoading, error } = useSelector((state) => state.checkouts);

  const [expectedReturnDate, setExpectedReturnDate] = useState('');
  const [validated, setValidated] = useState(false);

  useEffect(() => {
    if (id) {
      dispatch(fetchToolById(id));
    }
  }, [dispatch, id]);

  // Set default expected return date to 7 days from now
  useEffect(() => {
    const date = new Date();
    date.setDate(date.getDate() + 7);
    setExpectedReturnDate(date.toISOString().split('T')[0]);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    setValidated(true);

    dispatch(checkoutTool({
      toolId: id,
      expectedReturnDate
    })).unwrap()
      .then(() => {
        navigate('/my-checkouts');
      })
      .catch((err) => {
        console.error('Checkout failed:', err);
      });
  };

  if (toolLoading || !currentTool) {
    return <LoadingSpinner />;
  }

  if (currentTool.status !== 'available') {
    return (
      <Alert variant="warning">
        This tool is currently not available for checkout. Please select another tool.
      </Alert>
    );
  }

  return (
    <Card>
      <Card.Header>
        <h4>Checkout Tool: {currentTool.name}</h4>
      </Card.Header>
      <Card.Body>
        {error && <Alert variant="danger">{error.message}</Alert>}

        <Form noValidate validated={validated} onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Tool Information</Form.Label>
            <div className="mb-3">
              <strong>ID:</strong> {currentTool.id}
            </div>
            <div className="mb-3">
              <strong>Category:</strong> {currentTool.category}
            </div>
            <div className="mb-3">
              <strong>Location:</strong> {currentTool.location}
            </div>
            <div className="mb-3">
              <strong>Condition:</strong> {currentTool.condition}
            </div>
          </Form.Group>

          <Form.Group className="mb-3" controlId="expectedReturnDate">
            <Form.Label>Expected Return Date</Form.Label>
            <Form.Control
              type="date"
              value={expectedReturnDate}
              onChange={(e) => setExpectedReturnDate(e.target.value)}
              min={new Date().toISOString().split('T')[0]}
              required
            />
            <Form.Control.Feedback type="invalid">
              Please provide a valid return date.
            </Form.Control.Feedback>
            <Form.Text className="text-muted">
              Please return the tool by this date.
            </Form.Text>
          </Form.Group>

          <div className="d-flex justify-content-between">
            <Button variant="secondary" onClick={() => navigate(-1)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" disabled={checkoutLoading}>
              {checkoutLoading ? 'Processing...' : 'Checkout Tool'}
            </Button>
          </div>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default CheckoutForm;
