import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Modal, Button, Table, Badge, Form, Alert, InputGroup } from 'react-bootstrap';
import {
  FaPencilAlt,
  FaTrash,
  FaPlusCircle,
  FaSearch,
  FaToggleOff,
  FaToggleOn,
  FaExclamationTriangle
} from 'react-icons/fa';
import {
  fetchDepartments,
  createDepartment,
  updateDepartment,
  deleteDepartment,
  hardDeleteDepartment
} from '../../store/departmentsSlice';
import LoadingSpinner from '../common/LoadingSpinner';
import PropTypes from 'prop-types';
import './DepartmentsManagementModal.css';

const DepartmentsManagementModal = ({ show, onHide }) => {
  const dispatch = useDispatch();
  const { departments, loading, error } = useSelector(state => state.departments);

  const [searchTerm, setSearchTerm] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [selectedDepartment, setSelectedDepartment] = useState(null);
  const [deleteType, setDeleteType] = useState('soft'); // 'soft' or 'hard'

  const [formData, setFormData] = useState({
    name: '',
    description: ''
  });

  const [validated, setValidated] = useState(false);

  useEffect(() => {
    if (show) {
      // Fetch all departments including inactive ones
      dispatch(fetchDepartments(true));
    }
  }, [show, dispatch]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const resetForm = () => {
    setFormData({ name: '', description: '' });
    setValidated(false);
  };

  const handleAddDepartment = (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    dispatch(createDepartment(formData))
      .unwrap()
      .then(() => {
        setShowAddForm(false);
        resetForm();
        dispatch(fetchDepartments(true));
      })
      .catch(err => {
        console.error('Failed to create department:', err);
      });
  };

  const handleEditDepartment = (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    dispatch(updateDepartment({ 
      id: selectedDepartment.id, 
      data: formData 
    }))
      .unwrap()
      .then(() => {
        setShowEditForm(false);
        setSelectedDepartment(null);
        resetForm();
        dispatch(fetchDepartments(true));
      })
      .catch(err => {
        console.error('Failed to update department:', err);
      });
  };

  const openEditForm = (department) => {
    setSelectedDepartment(department);
    setFormData({
      name: department.name,
      description: department.description || ''
    });
    setShowEditForm(true);
  };

  const handleToggleActive = (department) => {
    dispatch(updateDepartment({
      id: department.id,
      data: { is_active: !department.is_active }
    }))
      .unwrap()
      .then(() => {
        dispatch(fetchDepartments(true));
      })
      .catch(err => {
        console.error('Failed to toggle department status:', err);
      });
  };

  const openDeleteConfirm = (department, type = 'soft') => {
    setSelectedDepartment(department);
    setDeleteType(type);
    setShowDeleteConfirm(true);
  };

  const handleDelete = () => {
    const action = deleteType === 'hard' 
      ? hardDeleteDepartment(selectedDepartment.id)
      : deleteDepartment(selectedDepartment.id);

    dispatch(action)
      .unwrap()
      .then(() => {
        setShowDeleteConfirm(false);
        setSelectedDepartment(null);
        dispatch(fetchDepartments(true));
      })
      .catch(err => {
        console.error('Failed to delete department:', err);
      });
  };

  const filteredDepartments = departments.filter(dept =>
    dept.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (dept.description && dept.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <>
      <Modal show={show} onHide={onHide} size="lg" className="departments-management-modal">
        <Modal.Header closeButton>
          <Modal.Title>Departments Management</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {error && (
            <Alert variant="danger" dismissible>
              {error.message || 'An error occurred'}
            </Alert>
          )}

          <div className="mb-3 d-flex justify-content-between align-items-center">
            <InputGroup style={{ maxWidth: '400px' }}>
              <InputGroup.Text>
                <FaSearch />
              </InputGroup.Text>
              <Form.Control
                type="text"
                placeholder="Search departments..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </InputGroup>

            <Button
              variant="success"
              onClick={() => setShowAddForm(true)}
              className="add-department-btn"
            >
              <FaPlusCircle className="me-2" />
              Add New Department
            </Button>
          </div>

          {loading ? (
            <LoadingSpinner />
          ) : (
            <div className="departments-table-wrapper">
              <Table hover responsive>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Status</th>
                    <th style={{ width: '200px' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredDepartments.length > 0 ? (
                    filteredDepartments.map(dept => (
                      <tr key={dept.id} className={!dept.is_active ? 'inactive-row' : ''}>
                        <td>
                          <strong>{dept.name}</strong>
                        </td>
                        <td>
                          <span className="text-muted">
                            {dept.description || <em>No description</em>}
                          </span>
                        </td>
                        <td>
                          <Badge bg={dept.is_active ? 'success' : 'secondary'}>
                            {dept.is_active ? 'Active' : 'Inactive'}
                          </Badge>
                        </td>
                        <td>
                          <div className="d-flex gap-2">
                            <Button
                              variant="outline-primary"
                              size="sm"
                              onClick={() => openEditForm(dept)}
                              title="Edit"
                            >
                              <FaPencilAlt />
                            </Button>
                            <Button
                              variant={dept.is_active ? 'outline-warning' : 'outline-success'}
                              size="sm"
                              onClick={() => handleToggleActive(dept)}
                              title={dept.is_active ? 'Deactivate' : 'Activate'}
                            >
                              {dept.is_active ? <FaToggleOff /> : <FaToggleOn />}
                            </Button>
                            <Button
                              variant="outline-danger"
                              size="sm"
                              onClick={() => openDeleteConfirm(dept, 'hard')}
                              title="Delete Permanently"
                            >
                              <FaTrash />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="4" className="text-center py-4">
                        {searchTerm ? 'No departments found matching your search.' : 'No departments found.'}
                      </td>
                    </tr>
                  )}
                </tbody>
              </Table>
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={onHide}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Add Department Modal */}
      <Modal show={showAddForm} onHide={() => { setShowAddForm(false); resetForm(); }}>
        <Modal.Header closeButton>
          <Modal.Title>Add New Department</Modal.Title>
        </Modal.Header>
        <Form noValidate validated={validated} onSubmit={handleAddDepartment}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Department Name *</Form.Label>
              <Form.Control
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                placeholder="Enter department name"
              />
              <Form.Control.Feedback type="invalid">
                Department name is required.
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
                placeholder="Enter department description (optional)"
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => { setShowAddForm(false); resetForm(); }}>
              Cancel
            </Button>
            <Button variant="success" type="submit" disabled={loading}>
              Add Department
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Edit Department Modal */}
      <Modal show={showEditForm} onHide={() => { setShowEditForm(false); setSelectedDepartment(null); resetForm(); }}>
        <Modal.Header closeButton>
          <Modal.Title>Edit Department</Modal.Title>
        </Modal.Header>
        <Form noValidate validated={validated} onSubmit={handleEditDepartment}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Department Name *</Form.Label>
              <Form.Control
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                placeholder="Enter department name"
              />
              <Form.Control.Feedback type="invalid">
                Department name is required.
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
                placeholder="Enter department description (optional)"
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => { setShowEditForm(false); setSelectedDepartment(null); resetForm(); }}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" disabled={loading}>
              Save Changes
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal show={showDeleteConfirm} onHide={() => { setShowDeleteConfirm(false); setSelectedDepartment(null); }}>
        <Modal.Header closeButton>
          <Modal.Title>
            <FaExclamationTriangle className="text-warning me-2" />
            Confirm Delete
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>
            Are you sure you want to <strong>permanently delete</strong> the department{' '}
            <strong>&quot;{selectedDepartment?.name}&quot;</strong>?
          </p>
          <Alert variant="warning">
            <strong>Warning:</strong> This action cannot be undone. The department will be permanently removed from the database.
          </Alert>
          <p className="text-muted mb-0">
            <small>
              If you want to temporarily disable this department instead, use the Deactivate button.
            </small>
          </p>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => { setShowDeleteConfirm(false); setSelectedDepartment(null); }}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDelete} disabled={loading}>
            Delete Permanently
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

DepartmentsManagementModal.propTypes = {
  show: PropTypes.bool.isRequired,
  onHide: PropTypes.func.isRequired
};

export default DepartmentsManagementModal;

