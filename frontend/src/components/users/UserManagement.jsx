import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Card, Table, Button, Badge, Modal, Form, Alert, InputGroup
} from 'react-bootstrap';
import { fetchUsers, createUser, updateUser, deactivateUser } from '../../store/usersSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const UserManagement = () => {
  const dispatch = useDispatch();
  const { users, loading, error } = useSelector((state) => state.users);
  const { user: currentUser } = useSelector((state) => state.auth);

  // State for search and filter
  const [searchQuery, setSearchQuery] = useState('');
  const [showInactive, setShowInactive] = useState(false);

  // State for modals
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  // State for form data
  const [formData, setFormData] = useState({
    name: '',
    employee_number: '',
    department: '',
    password: '',
    is_admin: false,
    is_active: true
  });

  // State for selected user
  const [selectedUser, setSelectedUser] = useState(null);

  // Form validation
  const [validated, setValidated] = useState(false);

  // Load users on component mount
  useEffect(() => {
    dispatch(fetchUsers());
  }, [dispatch]);

  // Filter users based on search query and active status
  const filteredUsers = users.filter(user => {
    const matchesSearch =
      user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.employee_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.department.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus = showInactive ? true : user.is_active;

    return matchesSearch && matchesStatus;
  });

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  // Handle add user form submission
  const handleAddUser = (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    dispatch(createUser(formData))
      .unwrap()
      .then(() => {
        setShowAddModal(false);
        resetForm();
      })
      .catch(err => {
        console.error('Failed to create user:', err);
      });
  };

  // Handle edit user form submission
  const handleEditUser = (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    // If password is empty, remove it from the data to avoid changing it
    const userData = { ...formData };
    if (!userData.password) {
      delete userData.password;
    }

    dispatch(updateUser({ id: selectedUser.id, userData }))
      .unwrap()
      .then(() => {
        setShowEditModal(false);
        resetForm();
      })
      .catch(err => {
        console.error('Failed to update user:', err);
      });
  };

  // Handle deactivate user
  const handleDeactivateUser = () => {
    dispatch(deactivateUser(selectedUser.id))
      .unwrap()
      .then(() => {
        setShowDeleteModal(false);
      })
      .catch(err => {
        console.error('Failed to deactivate user:', err);
      });
  };

  // Reset form data
  const resetForm = () => {
    setFormData({
      name: '',
      employee_number: '',
      department: '',
      password: '',
      is_admin: false,
      is_active: true
    });
    setValidated(false);
  };

  // Open edit modal with user data
  const openEditModal = (user) => {
    setSelectedUser(user);
    setFormData({
      name: user.name,
      employee_number: user.employee_number,
      department: user.department,
      password: '', // Don't populate password
      is_admin: user.is_admin,
      is_active: user.is_active
    });
    setShowEditModal(true);
  };

  // Open delete modal with user data
  const openDeleteModal = (user) => {
    setSelectedUser(user);
    setShowDeleteModal(true);
  };

  // Check if user has permission to manage users
  const hasPermission = currentUser?.is_admin || currentUser?.department === 'Materials';

  if (!hasPermission) {
    return (
      <Alert variant="danger">
        You do not have permission to access this page. Only administrators and Materials department users can manage users.
      </Alert>
    );
  }

  if (loading && !users.length) {
    return <LoadingSpinner />;
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>User Management</h2>
        <Button variant="primary" onClick={() => setShowAddModal(true)}>
          Add New User
        </Button>
      </div>

      {error && (
        <Alert variant="danger" className="mb-4">
          {error.message || 'An error occurred while loading users.'}
        </Alert>
      )}

      <Card className="mb-4">
        <Card.Header>
          <div className="d-flex justify-content-between align-items-center">
            <h5 className="mb-0">Users</h5>
            <div className="d-flex align-items-center">
              <Form.Control
                type="text"
                placeholder="Search users..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="me-2"
                style={{ width: '200px' }}
              />
              <Form.Check
                type="switch"
                id="show-inactive"
                label="Show Inactive"
                checked={showInactive}
                onChange={(e) => setShowInactive(e.target.checked)}
              />
            </div>
          </div>
        </Card.Header>
        <Card.Body className="p-0">
          <div className="table-responsive">
            <Table striped bordered hover className="mb-0">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Employee Number</th>
                  <th>Department</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.length > 0 ? (
                  filteredUsers.map((user) => (
                    <tr key={user.id} className={!user.is_active ? 'table-secondary' : ''}>
                      <td>{user.name}</td>
                      <td>{user.employee_number}</td>
                      <td>{user.department}</td>
                      <td>
                        {user.is_admin ? (
                          <span className="status-badge" style={{backgroundColor: 'var(--bs-primary)', color: 'white'}}>Admin</span>
                        ) : (
                          <span className="status-badge" style={{backgroundColor: 'var(--bs-secondary)', color: 'white'}}>User</span>
                        )}
                      </td>
                      <td>
                        {user.is_active ? (
                          <span className="status-badge status-active">Active</span>
                        ) : (
                          <span className="status-badge status-inactive">Inactive</span>
                        )}
                      </td>
                      <td>
                        <div className="d-flex gap-2">
                          <Button
                            variant="info"
                            size="sm"
                            onClick={() => openEditModal(user)}
                          >
                            Edit
                          </Button>
                          {user.is_active && (
                            <Button
                              variant="danger"
                              size="sm"
                              onClick={() => openDeleteModal(user)}
                              disabled={user.id === currentUser.id} // Can't deactivate yourself
                            >
                              Deactivate
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="6" className="text-center py-4">
                      No users found.
                    </td>
                  </tr>
                )}
              </tbody>
            </Table>
          </div>
        </Card.Body>
      </Card>

      {/* Add User Modal */}
      <Modal show={showAddModal} onHide={() => setShowAddModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Add New User</Modal.Title>
        </Modal.Header>
        <Form noValidate validated={validated} onSubmit={handleAddUser}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Name</Form.Label>
              <Form.Control
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
              />
              <Form.Control.Feedback type="invalid">
                Name is required.
              </Form.Control.Feedback>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Employee Number</Form.Label>
              <Form.Control
                type="text"
                name="employee_number"
                value={formData.employee_number}
                onChange={handleInputChange}
                required
              />
              <Form.Control.Feedback type="invalid">
                Employee number is required.
              </Form.Control.Feedback>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Department</Form.Label>
              <Form.Select
                name="department"
                value={formData.department}
                onChange={handleInputChange}
                required
              >
                <option value="">Select Department</option>
                <option value="Maintenance">Maintenance</option>
                <option value="Materials">Materials</option>
                <option value="Engineering">Engineering</option>
                <option value="Quality">Quality</option>
                <option value="Production">Production</option>
                <option value="IT">IT</option>
              </Form.Select>
              <Form.Control.Feedback type="invalid">
                Department is required.
              </Form.Control.Feedback>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Password</Form.Label>
              <Form.Control
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                required
              />
              <Form.Control.Feedback type="invalid">
                Password is required.
              </Form.Control.Feedback>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Check
                type="checkbox"
                label="Admin User"
                name="is_admin"
                checked={formData.is_admin}
                onChange={handleInputChange}
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowAddModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              Add User
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Edit User Modal */}
      <Modal show={showEditModal} onHide={() => setShowEditModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Edit User</Modal.Title>
        </Modal.Header>
        <Form noValidate validated={validated} onSubmit={handleEditUser}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Name</Form.Label>
              <Form.Control
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
              />
              <Form.Control.Feedback type="invalid">
                Name is required.
              </Form.Control.Feedback>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Employee Number</Form.Label>
              <Form.Control
                type="text"
                name="employee_number"
                value={formData.employee_number}
                onChange={handleInputChange}
                required
                disabled // Employee number shouldn't be changed
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Department</Form.Label>
              <Form.Select
                name="department"
                value={formData.department}
                onChange={handleInputChange}
                required
              >
                <option value="">Select Department</option>
                <option value="Maintenance">Maintenance</option>
                <option value="Materials">Materials</option>
                <option value="Engineering">Engineering</option>
                <option value="Quality">Quality</option>
                <option value="Production">Production</option>
                <option value="IT">IT</option>
              </Form.Select>
              <Form.Control.Feedback type="invalid">
                Department is required.
              </Form.Control.Feedback>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Password (leave blank to keep current)</Form.Label>
              <Form.Control
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Check
                type="checkbox"
                label="Admin User"
                name="is_admin"
                checked={formData.is_admin}
                onChange={handleInputChange}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Check
                type="checkbox"
                label="Active"
                name="is_active"
                checked={formData.is_active}
                onChange={handleInputChange}
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowEditModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              Save Changes
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Deactivate User Modal */}
      <Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Deactivate User</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Are you sure you want to deactivate the user <strong>{selectedUser?.name}</strong>?</p>
          <p>This will prevent the user from logging in, but will preserve their history in the system.</p>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDeactivateUser}>
            Deactivate User
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default UserManagement;
