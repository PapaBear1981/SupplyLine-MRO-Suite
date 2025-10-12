import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Card, Table, Button, Badge, Modal, Form, Alert, InputGroup
} from 'react-bootstrap';
import {
  fetchAircraftTypes,
  createAircraftType,
  updateAircraftType,
  deactivateAircraftType
} from '../../store/kitsSlice';
import LoadingSpinner from '../common/LoadingSpinner';
import { FaPlane, FaEdit, FaTrash, FaPlus, FaCheck, FaTimes } from 'react-icons/fa';

const AircraftTypeManagement = () => {
  const dispatch = useDispatch();
  const { aircraftTypes, loading, error } = useSelector((state) => state.kits);
  const { user: currentUser } = useSelector((state) => state.auth);

  // State for modals
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeactivateModal, setShowDeactivateModal] = useState(false);

  // State for form data
  const [formData, setFormData] = useState({
    name: '',
    description: ''
  });

  // State for validation
  const [validated, setValidated] = useState(false);

  // State for selected aircraft type
  const [selectedType, setSelectedType] = useState(null);

  // State for showing inactive types
  const [showInactive, setShowInactive] = useState(false);

  // State for success message
  const [successMessage, setSuccessMessage] = useState('');

  // Fetch aircraft types on component mount
  useEffect(() => {
    dispatch(fetchAircraftTypes(showInactive));
  }, [dispatch, showInactive]);

  // Clear success message after 3 seconds
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(''), 3000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  // Reset form data
  const resetForm = () => {
    setFormData({
      name: '',
      description: ''
    });
    setValidated(false);
  };

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  // Handle add aircraft type
  const handleAddType = (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    dispatch(createAircraftType(formData))
      .unwrap()
      .then(() => {
        setSuccessMessage('Aircraft type created successfully!');
        setShowAddModal(false);
        resetForm();
        dispatch(fetchAircraftTypes(showInactive));
      })
      .catch((err) => {
        console.error('Failed to create aircraft type:', err);
      });
  };

  // Handle edit aircraft type
  const handleEditType = (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    dispatch(updateAircraftType({ id: selectedType.id, data: formData }))
      .unwrap()
      .then(() => {
        setSuccessMessage('Aircraft type updated successfully!');
        setShowEditModal(false);
        resetForm();
        setSelectedType(null);
        dispatch(fetchAircraftTypes(showInactive));
      })
      .catch((err) => {
        console.error('Failed to update aircraft type:', err);
      });
  };

  // Handle deactivate aircraft type
  const handleDeactivateType = () => {
    dispatch(deactivateAircraftType(selectedType.id))
      .unwrap()
      .then(() => {
        setSuccessMessage('Aircraft type deactivated successfully!');
        setShowDeactivateModal(false);
        setSelectedType(null);
        dispatch(fetchAircraftTypes(showInactive));
      })
      .catch((err) => {
        console.error('Failed to deactivate aircraft type:', err);
      });
  };

  // Open add modal
  const openAddModal = () => {
    resetForm();
    setShowAddModal(true);
  };

  // Open edit modal
  const openEditModal = (type) => {
    setSelectedType(type);
    setFormData({
      name: type.name,
      description: type.description || ''
    });
    setValidated(false);
    setShowEditModal(true);
  };

  // Open deactivate modal
  const openDeactivateModal = (type) => {
    setSelectedType(type);
    setShowDeactivateModal(true);
  };

  // Check if user is admin
  const isAdmin = currentUser?.is_admin;

  if (!isAdmin) {
    return (
      <Card>
        <Card.Body>
          <Alert variant="danger">
            <Alert.Heading>Access Denied</Alert.Heading>
            <p>You must be an administrator to access this page.</p>
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  if (loading && aircraftTypes.length === 0) {
    return <LoadingSpinner />;
  }

  return (
    <div className="aircraft-type-management">
      <Card>
        <Card.Header className="d-flex justify-content-between align-items-center">
          <div>
            <h4 className="mb-0">
              <FaPlane className="me-2" />
              Aircraft Type Management
            </h4>
            <small className="text-muted">Manage aircraft types for kit organization</small>
          </div>
          <Button variant="primary" onClick={openAddModal}>
            <FaPlus className="me-2" />
            Add Aircraft Type
          </Button>
        </Card.Header>

        <Card.Body>
          {successMessage && (
            <Alert variant="success" dismissible onClose={() => setSuccessMessage('')}>
              {successMessage}
            </Alert>
          )}

          {error && (
            <Alert variant="danger">
              {error.message || 'An error occurred'}
            </Alert>
          )}

          <div className="mb-3">
            <Form.Check
              type="switch"
              id="show-inactive"
              label="Show inactive aircraft types"
              checked={showInactive}
              onChange={(e) => setShowInactive(e.target.checked)}
            />
          </div>

          <Table striped bordered hover responsive>
            <thead>
              <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Status</th>
                <th>Created</th>
                <th style={{ width: '150px' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {aircraftTypes.length === 0 ? (
                <tr>
                  <td colSpan="5" className="text-center text-muted">
                    No aircraft types found
                  </td>
                </tr>
              ) : (
                aircraftTypes.map((type) => (
                  <tr key={type.id}>
                    <td>
                      <strong>{type.name}</strong>
                    </td>
                    <td>{type.description || <span className="text-muted">No description</span>}</td>
                    <td>
                      {type.is_active ? (
                        <Badge bg="success">
                          <FaCheck className="me-1" />
                          Active
                        </Badge>
                      ) : (
                        <Badge bg="secondary">
                          <FaTimes className="me-1" />
                          Inactive
                        </Badge>
                      )}
                    </td>
                    <td>
                      {type.created_at
                        ? new Date(type.created_at).toLocaleDateString()
                        : 'N/A'}
                    </td>
                    <td>
                      <Button
                        variant="outline-primary"
                        size="sm"
                        className="me-2"
                        onClick={() => openEditModal(type)}
                      >
                        <FaEdit />
                      </Button>
                      {type.is_active && (
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={() => openDeactivateModal(type)}
                        >
                          <FaTrash />
                        </Button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </Table>
        </Card.Body>
      </Card>

      {/* Add Aircraft Type Modal */}
      <Modal show={showAddModal} onHide={() => setShowAddModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Add Aircraft Type</Modal.Title>
        </Modal.Header>
        <Form noValidate validated={validated} onSubmit={handleAddType}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Name *</Form.Label>
              <Form.Control
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="e.g., Q400, RJ85, CL415"
                required
              />
              <Form.Control.Feedback type="invalid">
                Please provide an aircraft type name.
              </Form.Control.Feedback>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                placeholder="Optional description of the aircraft type"
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowAddModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              Create Aircraft Type
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Edit Aircraft Type Modal */}
      <Modal show={showEditModal} onHide={() => setShowEditModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Edit Aircraft Type</Modal.Title>
        </Modal.Header>
        <Form noValidate validated={validated} onSubmit={handleEditType}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Name *</Form.Label>
              <Form.Control
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="e.g., Q400, RJ85, CL415"
                required
              />
              <Form.Control.Feedback type="invalid">
                Please provide an aircraft type name.
              </Form.Control.Feedback>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                placeholder="Optional description of the aircraft type"
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowEditModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              Update Aircraft Type
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Deactivate Confirmation Modal */}
      <Modal show={showDeactivateModal} onHide={() => setShowDeactivateModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Deactivate Aircraft Type</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Alert variant="warning">
            <strong>Warning:</strong> Are you sure you want to deactivate the aircraft type{' '}
            <strong>{selectedType?.name}</strong>?
          </Alert>
          <p>
            This will prevent new kits from being created for this aircraft type. Existing kits
            will not be affected.
          </p>
          <p className="text-muted mb-0">
            <small>
              Note: You cannot deactivate an aircraft type that has active kits.
            </small>
          </p>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDeactivateModal(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDeactivateType}>
            Deactivate
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default AircraftTypeManagement;

