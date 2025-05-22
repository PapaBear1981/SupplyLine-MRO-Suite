import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { Card, Form, Button, Badge, Spinner, Alert } from 'react-bootstrap';
import { submitCountResult } from '../../../store/cycleCountSlice';

const MobileCycleCountItem = ({ item, onComplete }) => {
  const dispatch = useDispatch();
  
  const [formData, setFormData] = useState({
    actual_quantity: item.expected_quantity,
    actual_location: item.expected_location,
    condition: '',
    notes: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [validated, setValidated] = useState(false);
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'actual_quantity' ? parseFloat(value) || 0 : value
    }));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const form = e.currentTarget;
    if (!form.checkValidity()) {
      e.stopPropagation();
      setValidated(true);
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      await dispatch(submitCountResult({
        itemId: item.id,
        resultData: formData
      })).unwrap();
      
      if (onComplete) {
        onComplete(item.id);
      }
    } catch (err) {
      setError(err.error || 'Failed to submit count result');
    } finally {
      setLoading(false);
    }
  };
  
  // Helper function to get item details
  const getItemDetails = () => {
    if (item.item_type === 'tool') {
      return {
        title: `Tool: ${item.tool?.tool_number || 'Unknown'}`,
        description: item.tool?.description || 'No description',
        location: item.tool?.location || 'Unknown location',
        showCondition: true
      };
    } else if (item.item_type === 'chemical') {
      return {
        title: `Chemical: ${item.chemical?.part_number || 'Unknown'}`,
        description: item.chemical?.description || 'No description',
        location: item.chemical?.location || 'Unknown location',
        showCondition: false
      };
    }
    
    return {
      title: 'Unknown Item',
      description: 'No description available',
      location: 'Unknown location',
      showCondition: false
    };
  };
  
  const itemDetails = getItemDetails();
  
  return (
    <Card className="mb-3">
      <Card.Header className="d-flex justify-content-between align-items-center">
        <div>
          <h5 className="mb-0">{itemDetails.title}</h5>
          <Badge bg={item.item_type === 'tool' ? 'primary' : 'info'}>
            {item.item_type}
          </Badge>
        </div>
      </Card.Header>
      <Card.Body>
        <p>{itemDetails.description}</p>
        
        {error && (
          <Alert variant="danger" className="mb-3">
            {error}
          </Alert>
        )}
        
        <Form noValidate validated={validated} onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Expected Location</Form.Label>
            <Form.Control
              type="text"
              value={item.expected_location || ''}
              disabled
              className="bg-light"
            />
          </Form.Group>
          
          <Form.Group className="mb-3">
            <Form.Label>Expected Quantity</Form.Label>
            <Form.Control
              type="number"
              value={item.expected_quantity || 0}
              disabled
              className="bg-light"
            />
          </Form.Group>
          
          <hr />
          
          <Form.Group className="mb-3">
            <Form.Label>Actual Location</Form.Label>
            <Form.Control
              type="text"
              name="actual_location"
              value={formData.actual_location || ''}
              onChange={handleChange}
              required
            />
            <Form.Control.Feedback type="invalid">
              Please enter the actual location
            </Form.Control.Feedback>
          </Form.Group>
          
          <Form.Group className="mb-3">
            <Form.Label>Actual Quantity</Form.Label>
            <Form.Control
              type="number"
              step="0.01"
              name="actual_quantity"
              value={formData.actual_quantity || 0}
              onChange={handleChange}
              required
            />
            <Form.Control.Feedback type="invalid">
              Please enter the actual quantity
            </Form.Control.Feedback>
          </Form.Group>
          
          {itemDetails.showCondition && (
            <Form.Group className="mb-3">
              <Form.Label>Condition</Form.Label>
              <Form.Select
                name="condition"
                value={formData.condition}
                onChange={handleChange}
              >
                <option value="">Select condition...</option>
                <option value="excellent">Excellent</option>
                <option value="good">Good</option>
                <option value="fair">Fair</option>
                <option value="poor">Poor</option>
                <option value="damaged">Damaged</option>
              </Form.Select>
            </Form.Group>
          )}
          
          <Form.Group className="mb-3">
            <Form.Label>Notes</Form.Label>
            <Form.Control
              as="textarea"
              rows={2}
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              placeholder="Add any notes about this item..."
            />
          </Form.Group>
          
          <div className="d-grid">
            <Button 
              type="submit" 
              variant="primary" 
              disabled={loading}
              className="py-2"
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
                  Submitting...
                </>
              ) : (
                'Submit Count'
              )}
            </Button>
          </div>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default MobileCycleCountItem;
