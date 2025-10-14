import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { Form, Button, Card, Alert, Row, Col, Toast, ToastContainer } from 'react-bootstrap';
import { createChemical } from '../../store/chemicalsSlice';
import LotNumberInput from '../common/LotNumberInput';

const NewChemicalForm = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading, error } = useSelector((state) => state.chemicals);

  const [chemicalData, setChemicalData] = useState({
    part_number: '',
    lot_number: '',
    description: '',
    manufacturer: '',
    quantity: '',
    unit: 'each',
    location: '',
    category: 'General',
    expiration_date: '',
    minimum_stock_level: '',
    notes: ''
  });
  const [validated, setValidated] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

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

    // Convert quantity and minimum_stock_level to numbers
    const formattedData = {
      ...chemicalData,
      quantity: parseFloat(chemicalData.quantity),
      minimum_stock_level: chemicalData.minimum_stock_level ? parseFloat(chemicalData.minimum_stock_level) : null
    };

    dispatch(createChemical(formattedData))
      .unwrap()
      .then(() => {
        setShowSuccess(true);
        // Navigate after showing success message for a short time
        setTimeout(() => {
          navigate('/chemicals');
        }, 1500);
      })
      .catch((err) => {
        console.error('Failed to create chemical:', err);
      });
  };

  return (
    <>
      <ToastContainer position="top-end" className="p-3">
        <Toast
          show={showSuccess}
          onClose={() => setShowSuccess(false)}
          delay={3000}
          autohide
          bg="success"
        >
          <Toast.Header>
            <strong className="me-auto">Success</strong>
          </Toast.Header>
          <Toast.Body className="text-white">
            Chemical added successfully!
          </Toast.Body>
        </Toast>
      </ToastContainer>

      <Card className="shadow-sm">
        <Card.Header>
          <h4>Add New Chemical</h4>
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
              <LotNumberInput
                value={chemicalData.lot_number}
                onChange={(value) => setChemicalData(prev => ({ ...prev, lot_number: value }))}
                disabled={loading}
                required={true}
                label="Lot Number"
                helpText="Auto-generate a unique lot number or enter manually"
                showAutoGenerate={true}
              />
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
                  step="0.01"
                  min="0"
                  name="quantity"
                  value={chemicalData.quantity}
                  onChange={handleChange}
                  required
                />
                <Form.Control.Feedback type="invalid">
                  Quantity is required and must be a positive number
                </Form.Control.Feedback>
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
                <Form.Label>Expiration Date</Form.Label>
                <Form.Control
                  type="date"
                  name="expiration_date"
                  value={chemicalData.expiration_date}
                  onChange={handleChange}
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Minimum Stock Level</Form.Label>
                <Form.Control
                  type="number"
                  step="0.01"
                  min="0"
                  name="minimum_stock_level"
                  value={chemicalData.minimum_stock_level}
                  onChange={handleChange}
                />
                <Form.Text className="text-muted">
                  Set a threshold for low stock alerts
                </Form.Text>
              </Form.Group>
            </Col>
          </Row>

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
            <Button variant="secondary" onClick={() => navigate('/chemicals')}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={loading}>
              {loading ? 'Saving...' : 'Save Chemical'}
            </Button>
          </div>
        </Form>
      </Card.Body>
    </Card>
    </>
  );
};

export default NewChemicalForm;
