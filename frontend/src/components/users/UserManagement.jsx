import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Card, Table, Button, Badge, Modal, Form, Alert, InputGroup, ListGroup, OverlayTrigger, Tooltip
} from 'react-bootstrap';
import { fetchUsers, createUser, updateUser, deactivateUser, unlockUserAccount } from '../../store/usersSlice';
import { fetchRoles, fetchUserRoles, updateUserRoles } from '../../store/rbacSlice';
import LoadingSpinner from '../common/LoadingSpinner';
import PasswordStrengthMeter from '../common/PasswordStrengthMeter';

const UserManagement = () => {
  const dispatch = useDispatch();
  const { users, loading, error } = useSelector((state) => state.users);
  const { user: currentUser } = useSelector((state) => state.auth);
  const { roles, userRoles, loading: rbacLoading, error: rbacError } = useSelector((state) => state.rbac);

  // State for search and filter
  const [searchQuery, setSearchQuery] = useState('');
  const [showInactive, setShowInactive] = useState(false);

  // State for modals
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showRolesModal, setShowRolesModal] = useState(false);
  const [showUnlockModal, setShowUnlockModal] = useState(false);

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

  // State for role selection
  const [selectedRoles, setSelectedRoles] = useState([]);

  // Form validation
  const [validated, setValidated] = useState(false);
  const [passwordValid, setPasswordValid] = useState(false);

  // Load users and roles on component mount
  useEffect(() => {
    dispatch(fetchUsers());
    dispatch(fetchRoles());
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

    if (form.checkValidity() === false || !passwordValid) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    dispatch(createUser(formData))
      .unwrap()
      .then(() => {
        setShowAddModal(false);
        resetForm();
        // Refresh the user list after adding a new user
        dispatch(fetchUsers());
      })
      .catch(err => {
        console.error('Failed to create user:', err);
        // The error will be automatically set in the Redux store
        // and displayed in the UI via the error Alert component
      });
  };

  // Handle edit user form submission
  const handleEditUser = (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false || (formData.password && !passwordValid)) {
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
        // Refresh the user list after updating a user
        dispatch(fetchUsers());
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
        // Refresh the user list after deactivating a user
        dispatch(fetchUsers());
      })
      .catch(err => {
        console.error('Failed to deactivate user:', err);
      });
  };

  // Open unlock account modal
  const openUnlockModal = (user) => {
    setSelectedUser(user);
    setShowUnlockModal(true);
  };

  // Handle unlock user account
  const handleUnlockAccount = () => {
    dispatch(unlockUserAccount(selectedUser.id))
      .unwrap()
      .then(() => {
        setShowUnlockModal(false);
        // Refresh the user list after unlocking the account
        dispatch(fetchUsers());
      })
      .catch(err => {
        console.error('Failed to unlock user account:', err);
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
    setPasswordValid(false);
  };

  // Handle password validation change
  const handlePasswordValidationChange = (isValid) => {
    setPasswordValid(isValid);
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

  // Open roles modal with user data
  const openRolesModal = (user) => {
    setSelectedUser(user);

    // Fetch user roles if not already loaded
    if (!userRoles[user.id]) {
      dispatch(fetchUserRoles(user.id));
    } else {
      // Set selected roles from existing data
      setSelectedRoles(userRoles[user.id].map(role => role.id));
    }

    setShowRolesModal(true);
  };

  // Handle role selection
  const handleRoleChange = (roleId) => {
    if (selectedRoles.includes(roleId)) {
      setSelectedRoles(selectedRoles.filter(id => id !== roleId));
    } else {
      setSelectedRoles([...selectedRoles, roleId]);
    }
  };

  // Handle save roles
  const handleSaveRoles = () => {
    dispatch(updateUserRoles({ userId: selectedUser.id, roles: selectedRoles }))
      .unwrap()
      .then(() => {
        setShowRolesModal(false);
        // Refresh the user list after updating roles
        dispatch(fetchUsers());
      })
      .catch(err => {
        console.error('Failed to update user roles:', err);
      });
  };

  // Check if user has permission to manage users
  const hasPermission = currentUser?.permissions?.includes('user.view');
  const canEditUsers = currentUser?.permissions?.includes('user.edit');
  const canCreateUsers = currentUser?.permissions?.includes('user.create');
  const canDeleteUsers = currentUser?.permissions?.includes('user.delete');
  const canManageRoles = currentUser?.permissions?.includes('role.manage');

  if (!hasPermission) {
    return (
      <Alert variant="danger">
        You do not have permission to access this page. Only users with user management permissions can view users.
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
        {canCreateUsers && (
          <Button variant="primary" onClick={() => setShowAddModal(true)}>
            Add New User
          </Button>
        )}
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
                        {user.roles && user.roles.length > 0 ? (
                          <div className="d-flex flex-wrap gap-1">
                            {user.roles.map(role => (
                              <span
                                key={role.id}
                                className="status-badge"
                                style={{
                                  backgroundColor: role.name === 'Administrator' ? 'var(--bs-primary)' :
                                                  role.name === 'Materials Manager' ? 'var(--bs-success)' :
                                                  'var(--bs-secondary)',
                                  color: 'white'
                                }}
                              >
                                {role.name}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <span className="status-badge" style={{backgroundColor: 'var(--bs-secondary)', color: 'white'}}>No Roles</span>
                        )}
                      </td>
                      <td>
                        {!user.is_active ? (
                          <span className="status-badge status-inactive">Inactive</span>
                        ) : user.account_locked ? (
                          <OverlayTrigger
                            placement="top"
                            overlay={
                              <Tooltip>
                                Locked until: {new Date(user.account_locked_until).toLocaleString()}
                                <br />
                                Failed attempts: {user.failed_login_attempts}
                              </Tooltip>
                            }
                          >
                            <span className="status-badge" style={{backgroundColor: 'var(--bs-danger)', color: 'white'}}>Locked</span>
                          </OverlayTrigger>
                        ) : (
                          <span className="status-badge status-active">Active</span>
                        )}
                      </td>
                      <td>
                        <div className="d-flex gap-2">
                          {canManageRoles && (
                            <Button
                              variant="success"
                              size="sm"
                              onClick={() => openRolesModal(user)}
                            >
                              Roles
                            </Button>
                          )}
                          {canEditUsers && (
                            <Button
                              variant="info"
                              size="sm"
                              onClick={() => openEditModal(user)}
                            >
                              Edit
                            </Button>
                          )}
                          {canEditUsers && user.is_active && user.account_locked && (
                            <Button
                              variant="warning"
                              size="sm"
                              onClick={() => openUnlockModal(user)}
                            >
                              Unlock
                            </Button>
                          )}
                          {canDeleteUsers && user.is_active && (
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
                isInvalid={validated && !passwordValid}
              />
              <Form.Control.Feedback type="invalid">
                Please provide a valid password that meets all requirements.
              </Form.Control.Feedback>
              <PasswordStrengthMeter
                password={formData.password}
                onValidationChange={handlePasswordValidationChange}
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
                isInvalid={validated && formData.password && !passwordValid}
              />
              {formData.password && (
                <>
                  <Form.Control.Feedback type="invalid">
                    Please provide a valid password that meets all requirements.
                  </Form.Control.Feedback>
                  <PasswordStrengthMeter
                    password={formData.password}
                    onValidationChange={handlePasswordValidationChange}
                  />
                </>
              )}
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

      {/* Roles Modal */}
      <Modal show={showRolesModal} onHide={() => setShowRolesModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Manage Roles for {selectedUser?.name}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {rbacLoading ? (
            <LoadingSpinner />
          ) : rbacError ? (
            <Alert variant="danger">
              {rbacError.message || 'An error occurred while loading roles.'}
            </Alert>
          ) : (
            <>
              <p>Select the roles to assign to this user:</p>
              <ListGroup>
                {roles.map((role) => (
                  <ListGroup.Item key={role.id}>
                    <Form.Check
                      type="checkbox"
                      id={`role-${role.id}`}
                      label={`${role.name} - ${role.description || 'No description'}`}
                      checked={selectedRoles.includes(role.id)}
                      onChange={() => handleRoleChange(role.id)}
                    />
                  </ListGroup.Item>
                ))}
              </ListGroup>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowRolesModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleSaveRoles} disabled={rbacLoading}>
            Save Roles
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Unlock Account Modal */}
      <Modal show={showUnlockModal} onHide={() => setShowUnlockModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Unlock User Account</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedUser && (
            <>
              <p>Are you sure you want to unlock the account for <strong>{selectedUser.name}</strong>?</p>
              <Alert variant="info">
                <p className="mb-1"><strong>Account Details:</strong></p>
                <ul className="mb-0">
                  <li>Employee Number: {selectedUser.employee_number}</li>
                  <li>Failed Login Attempts: {selectedUser.failed_login_attempts}</li>
                  <li>Locked Until: {new Date(selectedUser.account_locked_until).toLocaleString()}</li>
                </ul>
              </Alert>
              <p className="mt-3">Unlocking this account will reset the failed login attempts counter and allow the user to log in immediately.</p>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowUnlockModal(false)}>
            Cancel
          </Button>
          <Button variant="warning" onClick={handleUnlockAccount}>
            Unlock Account
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default UserManagement;
