import { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Badge, Form, InputGroup, Alert, Modal } from 'react-bootstrap';
import { FaWarehouse, FaPlus, FaSearch, FaMapMarkerAlt, FaBox, FaFlask, FaEdit } from 'react-icons/fa';
import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import api from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';

const WarehousesManagement = () => {
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.is_admin;

  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedWarehouse, setSelectedWarehouse] = useState(null);
  const [showDetailsPanel, setShowDetailsPanel] = useState(false);

  // Create/Edit warehouse form
  const [formData, setFormData] = useState({
    name: '',
    address: '',
    city: '',
    state: '',
    zip_code: '',
    country: 'USA',
    warehouse_type: 'satellite',
    contact_person: '',
    contact_phone: '',
    contact_email: ''
  });
  const [validated, setValidated] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchWarehouses();
  }, []);

  const fetchWarehouses = async () => {
    setLoading(true);
    try {
      const response = await api.get('/warehouses');
      // Backend returns { warehouses: [...], pagination: {...} }
      const warehousesData = response.data.warehouses || response.data;
      setWarehouses(Array.isArray(warehousesData) ? warehousesData : []);
    } catch (err) {
      console.error('Failed to fetch warehouses:', err);
      setError('Failed to load warehouses. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWarehouse = async (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    setValidated(true);
    setSubmitting(true);
    setSubmitError(null);

    try {
      await api.post('/warehouses', formData);
      setShowCreateModal(false);
      resetForm();
      fetchWarehouses();
    } catch (err) {
      console.error('Failed to create warehouse:', err);
      setSubmitError(err.response?.data?.message || 'Failed to create warehouse');
    } finally {
      setSubmitting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      address: '',
      city: '',
      state: '',
      zip_code: '',
      country: 'USA',
      warehouse_type: 'satellite',
      contact_person: '',
      contact_phone: '',
      contact_email: ''
    });
    setValidated(false);
    setSubmitError(null);
  };

  const handleViewDetails = async (warehouse) => {
    setSelectedWarehouse(warehouse);
    setShowDetailsPanel(true);

    // Fetch warehouse stats
    try {
      const response = await api.get(`/warehouses/${warehouse.id}/stats`);
      setSelectedWarehouse(prev => ({ ...prev, stats: response.data }));
    } catch (err) {
      console.error('Failed to fetch warehouse stats:', err);
    }
  };

  const handleEditWarehouse = (warehouse) => {
    setFormData({
      name: warehouse.name || '',
      address: warehouse.address || '',
      city: warehouse.city || '',
      state: warehouse.state || '',
      zip_code: warehouse.zip_code || '',
      country: warehouse.country || 'USA',
      warehouse_type: warehouse.warehouse_type || 'satellite',
      contact_person: warehouse.contact_person || '',
      contact_phone: warehouse.contact_phone || '',
      contact_email: warehouse.contact_email || ''
    });
    setShowEditModal(true);
  };

  const handleUpdateWarehouse = async (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    setValidated(true);
    setSubmitting(true);
    setSubmitError(null);

    try {
      await api.put(`/warehouses/${selectedWarehouse.id}`, formData);
      setShowEditModal(false);
      resetForm();
      fetchWarehouses();
      setShowDetailsPanel(false);
    } catch (err) {
      console.error('Failed to update warehouse:', err);
      setSubmitError(err.response?.data?.error || 'Failed to update warehouse');
    } finally {
      setSubmitting(false);
    }
  };

  const filteredWarehouses = warehouses.filter(w =>
    w.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    w.city?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    w.state?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!isAdmin) {
    return <Navigate to="/" replace />;
  }

  if (loading) {
    return <LoadingSpinner />;
  }

  const WarehouseCard = ({ warehouse }) => (
    <Card 
      className="mb-3 shadow-sm hover-shadow" 
      style={{ cursor: 'pointer' }}
      onClick={() => handleViewDetails(warehouse)}
    >
      <Card.Body>
        <div className="d-flex justify-content-between align-items-start mb-2">
          <div>
            <h5 className="mb-1">
              <FaWarehouse className="me-2 text-primary" />
              {warehouse.name}
            </h5>
            <div className="text-muted small">
              <FaMapMarkerAlt className="me-1" />
              {warehouse.city}, {warehouse.state}
            </div>
          </div>
          <div>
            <Badge bg={warehouse.is_active ? 'success' : 'secondary'}>
              {warehouse.is_active ? 'Active' : 'Inactive'}
            </Badge>
            {warehouse.warehouse_type === 'main' && (
              <Badge bg="primary" className="ms-1">Main</Badge>
            )}
          </div>
        </div>

        {warehouse.address && (
          <p className="text-muted small mb-2">{warehouse.address}</p>
        )}

        <Row className="mt-3">
          <Col xs={6}>
            <div className="text-center">
              <FaBox className="text-info mb-1" />
              <div className="small text-muted">Tools</div>
              <div className="fw-bold">{warehouse.tools_count || 0}</div>
            </div>
          </Col>
          <Col xs={6}>
            <div className="text-center">
              <FaFlask className="text-warning mb-1" />
              <div className="small text-muted">Chemicals</div>
              <div className="fw-bold">{warehouse.chemicals_count || 0}</div>
            </div>
          </Col>
        </Row>
      </Card.Body>
    </Card>
  );

  return (
    <Container fluid className="py-4">
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h2 className="mb-1">
                <FaWarehouse className="me-2" />
                Warehouse Management
              </h2>
              <p className="text-muted mb-0">
                Manage warehouse locations and inventory
              </p>
            </div>
            {isAdmin && (
              <Button
                variant="primary"
                onClick={() => setShowCreateModal(true)}
              >
                <FaPlus className="me-2" />
                Create Warehouse
              </Button>
            )}
          </div>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Row className="mb-3">
        <Col md={6}>
          <InputGroup>
            <InputGroup.Text>
              <FaSearch />
            </InputGroup.Text>
            <Form.Control
              placeholder="Search warehouses by name, city, or state..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </InputGroup>
        </Col>
      </Row>

      <Row>
        <Col lg={showDetailsPanel ? 8 : 12}>
          <Row>
            {filteredWarehouses.length === 0 ? (
              <Col>
                <Card className="text-center py-5">
                  <Card.Body>
                    <FaWarehouse size={48} className="text-muted mb-3" />
                    <h5>No warehouses found</h5>
                    <p className="text-muted">
                      {searchTerm 
                        ? 'Try adjusting your search' 
                        : 'Create your first warehouse to get started'}
                    </p>
                    {!searchTerm && isAdmin && (
                      <Button variant="primary" onClick={() => setShowCreateModal(true)}>
                        <FaPlus className="me-2" />
                        Create Warehouse
                      </Button>
                    )}
                  </Card.Body>
                </Card>
              </Col>
            ) : (
              filteredWarehouses.map(warehouse => (
                <Col key={warehouse.id} md={showDetailsPanel ? 12 : 6} lg={showDetailsPanel ? 12 : 4}>
                  <WarehouseCard warehouse={warehouse} />
                </Col>
              ))
            )}
          </Row>
        </Col>

        {showDetailsPanel && selectedWarehouse && (
          <Col lg={4}>
            <Card className="shadow-sm sticky-top" style={{ top: '20px' }}>
              <Card.Header className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0">Warehouse Details</h5>
                <Button
                  variant="link"
                  size="sm"
                  onClick={() => setShowDetailsPanel(false)}
                >
                  ×
                </Button>
              </Card.Header>
              <Card.Body>
                <div className="d-flex justify-content-between align-items-start mb-3">
                  <h6>{selectedWarehouse.name}</h6>
                  {isAdmin && (
                    <Button
                      variant="outline-primary"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEditWarehouse(selectedWarehouse);
                      }}
                    >
                      <FaEdit className="me-1" />
                      Edit
                    </Button>
                  )}
                </div>
                <p className="text-muted small mb-3">
                  {selectedWarehouse.address}<br />
                  {selectedWarehouse.city}, {selectedWarehouse.state} {selectedWarehouse.zip_code}
                </p>

                <div className="mb-3">
                  <strong>Type:</strong> {selectedWarehouse.warehouse_type}
                </div>
                <div className="mb-3">
                  <strong>Status:</strong>{' '}
                  <Badge bg={selectedWarehouse.is_active ? 'success' : 'secondary'}>
                    {selectedWarehouse.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                </div>

                {(selectedWarehouse.contact_person || selectedWarehouse.contact_phone || selectedWarehouse.contact_email) && (
                  <>
                    <hr />
                    <h6>Contact Information</h6>
                    {selectedWarehouse.contact_person && (
                      <div className="mb-2">
                        <strong>Contact:</strong> {selectedWarehouse.contact_person}
                      </div>
                    )}
                    {selectedWarehouse.contact_phone && (
                      <div className="mb-2">
                        <strong>Phone:</strong> {selectedWarehouse.contact_phone}
                      </div>
                    )}
                    {selectedWarehouse.contact_email && (
                      <div className="mb-2">
                        <strong>Email:</strong> {selectedWarehouse.contact_email}
                      </div>
                    )}
                  </>
                )}

                <hr />

                <h6>Inventory Summary</h6>
                <div className="mb-2">
                  <FaBox className="me-2 text-info" />
                  <strong>Tools:</strong> {selectedWarehouse.tools_count || 0}
                </div>
                <div className="mb-2">
                  <FaFlask className="me-2 text-warning" />
                  <strong>Chemicals:</strong> {selectedWarehouse.chemicals_count || 0}
                </div>
              </Card.Body>
            </Card>
          </Col>
        )}
      </Row>

      {/* Create Warehouse Modal */}
      <Modal show={showCreateModal} onHide={() => { setShowCreateModal(false); resetForm(); }} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Create New Warehouse</Modal.Title>
        </Modal.Header>
        <Form noValidate validated={validated} onSubmit={handleCreateWarehouse}>
          <Modal.Body>
            {submitError && <Alert variant="danger">{submitError}</Alert>}
            
            <Form.Group className="mb-3">
              <Form.Label>Warehouse Name *</Form.Label>
              <Form.Control
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                placeholder="e.g., Main Warehouse, Satellite A"
              />
              <Form.Control.Feedback type="invalid">
                Warehouse name is required
              </Form.Control.Feedback>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Warehouse Type *</Form.Label>
              <Form.Select
                value={formData.warehouse_type}
                onChange={(e) => setFormData({ ...formData, warehouse_type: e.target.value })}
                required
              >
                <option value="main">Main Warehouse</option>
                <option value="satellite">Satellite Warehouse</option>
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Address</Form.Label>
              <Form.Control
                type="text"
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                placeholder="Street address"
              />
            </Form.Group>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>City</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.city}
                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  />
                </Form.Group>
              </Col>
              <Col md={3}>
                <Form.Group className="mb-3">
                  <Form.Label>State</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.state}
                    onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                    maxLength={2}
                  />
                </Form.Group>
              </Col>
              <Col md={3}>
                <Form.Group className="mb-3">
                  <Form.Label>Zip Code</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.zip_code}
                    onChange={(e) => setFormData({ ...formData, zip_code: e.target.value })}
                  />
                </Form.Group>
              </Col>
            </Row>

            <hr className="my-4" />
            <h6 className="mb-3">Contact Information (Optional)</h6>

            <Form.Group className="mb-3">
              <Form.Label>Contact Person</Form.Label>
              <Form.Control
                type="text"
                value={formData.contact_person}
                onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
                placeholder="Name of primary contact"
              />
            </Form.Group>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Contact Phone</Form.Label>
                  <Form.Control
                    type="tel"
                    value={formData.contact_phone}
                    onChange={(e) => setFormData({ ...formData, contact_phone: e.target.value })}
                    placeholder="(555) 123-4567"
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Contact Email</Form.Label>
                  <Form.Control
                    type="email"
                    value={formData.contact_email}
                    onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
                    placeholder="contact@example.com"
                  />
                </Form.Group>
              </Col>
            </Row>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => { setShowCreateModal(false); resetForm(); }}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" disabled={submitting}>
              {submitting ? 'Creating...' : 'Create Warehouse'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Edit Warehouse Modal */}
      <Modal show={showEditModal} onHide={() => { setShowEditModal(false); resetForm(); }} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Edit Warehouse</Modal.Title>
        </Modal.Header>
        <Form noValidate validated={validated} onSubmit={handleUpdateWarehouse}>
          <Modal.Body>
            {submitError && <Alert variant="danger">{submitError}</Alert>}

            <Form.Group className="mb-3">
              <Form.Label>Warehouse Name *</Form.Label>
              <Form.Control
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                placeholder="e.g., Main Warehouse, Satellite A"
              />
              <Form.Control.Feedback type="invalid">
                Warehouse name is required
              </Form.Control.Feedback>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Warehouse Type *</Form.Label>
              <Form.Select
                value={formData.warehouse_type}
                onChange={(e) => setFormData({ ...formData, warehouse_type: e.target.value })}
                required
              >
                <option value="main">Main Warehouse</option>
                <option value="satellite">Satellite Warehouse</option>
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Address</Form.Label>
              <Form.Control
                type="text"
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                placeholder="Street address"
              />
            </Form.Group>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>City</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.city}
                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  />
                </Form.Group>
              </Col>
              <Col md={3}>
                <Form.Group className="mb-3">
                  <Form.Label>State</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.state}
                    onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                    maxLength={2}
                  />
                </Form.Group>
              </Col>
              <Col md={3}>
                <Form.Group className="mb-3">
                  <Form.Label>Zip Code</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.zip_code}
                    onChange={(e) => setFormData({ ...formData, zip_code: e.target.value })}
                  />
                </Form.Group>
              </Col>
            </Row>

            <hr className="my-4" />
            <h6 className="mb-3">Contact Information (Optional)</h6>

            <Form.Group className="mb-3">
              <Form.Label>Contact Person</Form.Label>
              <Form.Control
                type="text"
                value={formData.contact_person}
                onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
                placeholder="Name of primary contact"
              />
            </Form.Group>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Contact Phone</Form.Label>
                  <Form.Control
                    type="tel"
                    value={formData.contact_phone}
                    onChange={(e) => setFormData({ ...formData, contact_phone: e.target.value })}
                    placeholder="(555) 123-4567"
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Contact Email</Form.Label>
                  <Form.Control
                    type="email"
                    value={formData.contact_email}
                    onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
                    placeholder="contact@example.com"
                  />
                </Form.Group>
              </Col>
            </Row>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => { setShowEditModal(false); resetForm(); }}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" disabled={submitting}>
              {submitting ? 'Saving...' : 'Save Changes'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      <style jsx>{`
        .hover-shadow {
          transition: box-shadow 0.3s ease-in-out;
        }
        .hover-shadow:hover {
          box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
        }
      `}</style>
    </Container>
  );
};

export default WarehousesManagement;

