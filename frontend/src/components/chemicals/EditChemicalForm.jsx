import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useParams } from 'react-router-dom';
import { Form, Button, Card, Alert, Row, Col } from 'react-bootstrap';
import { fetchChemicalById, updateChemical } from '../../store/chemicalsSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const EditChemicalForm = () => {
  const { id } = useParams();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { currentChemical, loading, error } = useSelector((state) => state.chemicals);

  const [chemicalData, setChemicalData] = useState({
    part_number: '',
    lot_number: '',
    description: '',
    manufacturer: '',
    quantity: '',
    unit: 'each',
    location: '',
    category: 'General',
    status: 'available',
    expiration_date: '',
    minimum_stock_level: '',
    notes: ''
  });
  const [validated, setValidated] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);

  useEffect(() => {
    if (id) {
      dispatch(fetchChemicalById(id))
        .unwrap()
        .then(() => {
          setInitialLoading(false);
        })
        .catch((err) => {
          console.error('Failed to fetch chemical:', err);
          setInitialLoading(false);
        });
    }
  }, [dispatch, id]);

  useEffect(() => {
    if (currentChemical) {
      setChemicalData({
        part_number: currentChemical.part_number || '',
        lot_number: currentChemical.lot_number || '',
        description: currentChemical.description || '',
        manufacturer: currentChemical.manufacturer || '',
        quantity: currentChemical.quantity || '',
        unit: currentChemical.unit || 'each',
        location: currentChemical.location || '',
        category: currentChemical.category || 'General',
        status: currentChemical.status || 'available',
        expiration_date: currentChemical.expiration_date 
          ? new Date(currentChemical.expiration_date).toISOString().split('T')[0]
          : '',
        minimum_stock_level: currentChemical.minimum_stock_level || '',
        notes: currentChemical.notes || ''
      });
    }
  }, [currentChemical]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setChemicalData(prev => ({
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

    // Convert quantity and minimum_stock_level to integers
    const formattedData = {
      ...chemicalData,
      quantity: parseInt(chemicalData.quantity),
      minimum_stock_level: chemicalData.minimum_stock_level ? parseInt(chemicalData.minimum_stock_level) : null
    };

    dispatch(updateChemical({ id, chemicalData: formattedData }))
      .unwrap()
      .then(() => {
        navigate(`/chemicals/${id}`);
      })
      .catch((err) => {
        console.error('Failed to update chemical:', err);
      });
  };

  if (initialLoading) {
    return <LoadingSpinner />;
  }

  return (
    <Card className="shadow-sm">
      <Card.Header>
        <h4>Edit Chemical</h4>
      </Card.Header>
      <Card.Body>
        {error && <Alert variant="danger">{error.message}</Alert>}

        <Form noValidate validated={validated} onSubmit={handleSubmit}>
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Part Number*</Form.Label>
                <Form.Control
                  type="text"
                  name="part_number"
                  value={chemicalData.part_number}
                  onChange={handleChange}
                  required
                />
                <Form.Control.Feedback type="invalid">
                  Part number is required
                </Form.Control.Feedback>
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Lot Number*</Form.Label>
                <Form.Control
                  type="text"
                  name="lot_number"
                  value={chemicalData.lot_number}
                  onChange={handleChange}
                  required
                />
                <Form.Control.Feedback type="invalid">
                  Lot number is required
                </Form.Control.Feedback>
              </Form.Group>
            </Col>
          </Row>

          <Form.Group className="mb-3">
            <Form.Label>Description</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              name="description"
              value={chemicalData.description}
              onChange={handleChange}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Manufacturer</Form.Label>
            <Form.Control
              type="text"
              name="manufacturer"
              value={chemicalData.manufacturer}
              onChange={handleChange}
            />
          </Form.Group>

          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Quantity*</Form.Label>
                <Form.Control
                  type="number"
                  step="1"
                  min="1"
                  name="quantity"
                  value={chemicalData.quantity}
                  onChange={handleChange}
                  required
                />
                <Form.Control.Feedback type="invalid">
                  Quantity is required and must be a whole number (no decimals)
                </Form.Control.Feedback>
                <Form.Text className="text-muted">
                  Only whole numbers allowed (e.g., 1, 5, 10)
                </Form.Text>
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Unit*</Form.Label>
                <Form.Select
                  name="unit"
                  value={chemicalData.unit}
                  onChange={handleChange}
                  required
                >
                  <option value="each">Each</option>
                  <option value="oz">Ounce (oz)</option>
                  <option value="ml">Milliliter (ml)</option>
                  <option value="l">Liter (l)</option>
                  <option value="g">Gram (g)</option>
                  <option value="kg">Kilogram (kg)</option>
                  <option value="lb">Pound (lb)</option>
                  <option value="gal">Gallon (gal)</option>
                  <option value="tubes">Tubes</option>
                </Form.Select>
              </Form.Group>
            </Col>
          </Row>

          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Location</Form.Label>
                <Form.Control
                  type="text"
                  name="location"
                  value={chemicalData.location}
                  onChange={handleChange}
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Category</Form.Label>
                <Form.Select
                  name="category"
                  value={chemicalData.category}
                  onChange={handleChange}
                >
                  <option value="General">General</option>
                  <option value="Sealant">Sealant</option>
                  <option value="Paint">Paint</option>
                  <option value="Adhesive">Adhesive</option>
                  <option value="Lubricant">Lubricant</option>
                  <option value="Solvent">Solvent</option>
                  <option value="Cleaner">Cleaner</option>
                </Form.Select>
              </Form.Group>
            </Col>
          </Row>

          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Status</Form.Label>
                <Form.Select
                  name="status"
                  value={chemicalData.status}
                  onChange={handleChange}
                >
                  <option value="available">Available</option>
                  <option value="low_stock">Low Stock</option>
                  <option value="out_of_stock">Out of Stock</option>
                  <option value="expired">Expired</option>
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Expiration Date</Form.Label>
                <Form.Control
                  type="date"
                  name="expiration_date"
                  value={chemicalData.expiration_date}
                  onChange={handleChange}
                />
              </Form.Group>
            </Col>
          </Row>

          <Form.Group className="mb-3">
            <Form.Label>Minimum Stock Level</Form.Label>
            <Form.Control
              type="number"
              step="1"
              min="1"
              name="minimum_stock_level"
              value={chemicalData.minimum_stock_level}
              onChange={handleChange}
            />
            <Form.Text className="text-muted">
              Set a threshold for low stock alerts (whole numbers only)
            </Form.Text>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Notes</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              name="notes"
              value={chemicalData.notes}
              onChange={handleChange}
            />
          </Form.Group>

          <div className="d-flex justify-content-end gap-2">
            <Button variant="secondary" onClick={() => navigate(`/chemicals/${id}`)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={loading}>
              {loading ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default EditChemicalForm;
