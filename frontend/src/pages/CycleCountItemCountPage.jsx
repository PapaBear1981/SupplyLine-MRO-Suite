import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
  Card,
  Row,
  Col,
  Button,
  Alert,
  Spinner
} from 'react-bootstrap';
import CycleCountService from '../services/cycleCountService';

import { useHelp } from '../context/HelpContext';
import CycleCountItemForm from '../components/cycleCount/CycleCountItemForm';

const CycleCountItemCountPage = () => {
  const { id } = useParams();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { showHelp } = useHelp();

  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const controller = new AbortController();

    const fetchItem = async () => {
      try {
        setLoading(true);
        const data = await CycleCountService.getItemById(id, controller.signal);
        setItem(data);
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error('Error fetching item details:', err);
          setError(err.response?.data?.error || 'Failed to fetch item details');
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    };

    fetchItem();

    // Cleanup
    return () => controller.abort();
  }, [id]);

  const handleSuccess = () => {
    // Navigate back to the batch detail page
    if (item && item.batch_id) {
      navigate(`/cycle-counts/batches/${item.batch_id}`);
    } else {
      navigate('/cycle-counts');
    }
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '50vh' }}>
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Error Loading Item</Alert.Heading>
        <p>{error}</p>
        <Button as={Link} to="/cycle-counts" variant="primary">
          Back to Cycle Counts
        </Button>
      </Alert>
    );
  }

  if (!item) {
    return (
      <Alert variant="warning">
        <Alert.Heading>Item Not Found</Alert.Heading>
        <p>The requested cycle count item could not be found.</p>
        <Button as={Link} to="/cycle-counts" variant="primary">
          Back to Cycle Counts
        </Button>
      </Alert>
    );
  }

  return (
    <div className="w-100">
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
        <div>
          <h1 className="mb-0">Count Item: {item.item_name}</h1>
          <p className="text-muted mb-0">
            {item.item_type === 'tool' ? 'Tool' : 'Chemical'} from batch {item.batch_name}
          </p>
        </div>
        <div>
          <Button as={Link} to={`/cycle-counts/batches/${item.batch_id}`} variant="outline-secondary">
            <i className="bi bi-arrow-left me-2"></i>
            Back to Batch
          </Button>
        </div>
      </div>

      {showHelp && (
        <Alert variant="info" className="mb-4">
          <Alert.Heading>Count Item</Alert.Heading>
          <p>
            This page allows you to record the count result for an inventory item.
            Enter the actual quantity, location, and condition of the item.
            If there are discrepancies between the expected and actual values, they will be flagged for review.
          </p>
        </Alert>
      )}

      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light">
          <h5 className="mb-0">Count Form</h5>
        </Card.Header>
        <Card.Body>
          <CycleCountItemForm item={item} onSuccess={handleSuccess} />
        </Card.Body>
      </Card>
    </div>
  );
};

export default CycleCountItemCountPage;
