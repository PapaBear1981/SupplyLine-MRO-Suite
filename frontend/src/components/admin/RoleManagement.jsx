import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Card, Table, Button, Badge, Modal, Form, Alert, InputGroup, Tabs, Tab, ListGroup
} from 'react-bootstrap';
import { fetchRoles, createRole, updateRole, deleteRole, fetchPermissions, fetchRoleById } from '../../store/rbacSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const RoleManagement = () => {
  const dispatch = useDispatch();
  // eslint-disable-next-line no-unused-vars -- permissions is used in modals below (lines 318-328, 386-396, 466-501)
  const { roles, permissions, permissionsByCategory, loading, error } = useSelector((state) => state.rbac);
  const { user: currentUser } = useSelector((state) => state.auth);

  // State for modals
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showPermissionsModal, setShowPermissionsModal] = useState(false);

  // State for form data
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    permissions: []
  });

  // State for validation
  const [validated, setValidated] = useState(false);

  // State for selected role
  const [selectedRole, setSelectedRole] = useState(null);

  // Fetch roles and permissions on component mount
  useEffect(() => {
    dispatch(fetchRoles());
    dispatch(fetchPermissions());
  }, [dispatch]);

  // Reset form data
  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      permissions: []
    });
    setValidated(false);
  };

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  // Handle permission selection
  const handlePermissionChange = (permissionId) => {
    const updatedPermissions = [...formData.permissions];

    if (updatedPermissions.includes(permissionId)) {
      // Remove permission if already selected
      const index = updatedPermissions.indexOf(permissionId);
      updatedPermissions.splice(index, 1);
    } else {
      // Add permission if not selected
      updatedPermissions.push(permissionId);
    }

    setFormData({
      ...formData,
      permissions: updatedPermissions
    });
  };

  // Handle add role form submission
  const handleAddRole = (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    dispatch(createRole(formData))
      .unwrap()
      .then(() => {
        setShowAddModal(false);
        resetForm();
        // Refresh the role list after adding a new role
        dispatch(fetchRoles());
      })
      .catch(err => {
        console.error('Failed to create role:', err);
      });
  };

  // Handle edit role form submission
  const handleEditRole = (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    dispatch(updateRole({ id: selectedRole.id, roleData: formData }))
      .unwrap()
      .then(() => {
        setShowEditModal(false);
        resetForm();
        // Refresh the role list after updating a role
        dispatch(fetchRoles());
      })
      .catch(err => {
        console.error('Failed to update role:', err);
      });
  };

  // Handle delete role
  const handleDeleteRole = () => {
    dispatch(deleteRole(selectedRole.id))
      .unwrap()
      .then(() => {
        setShowDeleteModal(false);
        // Refresh the role list after deleting a role
        dispatch(fetchRoles());
      })
      .catch(err => {
        console.error('Failed to delete role:', err);
      });
  };

  // Open edit modal with role data
  const openEditModal = (role) => {
    setSelectedRole(role);
    setFormData({
      name: role.name,
      description: role.description || '',
      permissions: role.permissions ? role.permissions.map(p => p.id) : []
    });
    setShowEditModal(true);
  };

  // Open delete modal with role data
  const openDeleteModal = (role) => {
    setSelectedRole(role);
    setShowDeleteModal(true);
  };

  // Fetch role permissions
  const fetchRolePermissions = (roleId) => {
    dispatch(fetchRoleById(roleId))
      .unwrap()
      .then((updatedRole) => {
        setSelectedRole(updatedRole);
      })
      .catch((err) => {
        console.error('Failed to fetch role permissions:', err);
      });
  };

  // Open permissions modal with role data
  const openPermissionsModal = (role) => {
    setSelectedRole(role);
    setShowPermissionsModal(true);

    // Fetch the latest role data to ensure we have the most up-to-date permissions
    fetchRolePermissions(role.id);
  };

  // Check if user has permission to manage roles
  // Admins (is_admin: true) have FULL access to role management
  const hasPermission = currentUser?.is_admin || currentUser?.permissions?.includes('role.manage');

  if (!hasPermission) {
    return (
      <Alert variant="danger">
        You do not have permission to access this page. Only administrators with role management permissions can manage roles.
      </Alert>
    );
  }

  if (loading && !roles.length) {
    return <LoadingSpinner />;
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Role Management</h2>
        <Button variant="primary" onClick={() => setShowAddModal(true)}>
          Add New Role
        </Button>
      </div>

      {error && (
        <Alert variant="danger" className="mb-4">
          {error.message || 'An error occurred while loading roles.'}
        </Alert>
      )}

      <Card className="mb-4">
        <Card.Header>
          <h5 className="mb-0">Roles</h5>
        </Card.Header>
        <Card.Body className="p-0">
          <div className="table-responsive">
            <Table striped bordered hover className="mb-0">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Description</th>
                  <th>System Role</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {roles.length > 0 ? (
                  roles.map((role) => (
                    <tr key={role.id}>
                      <td>{role.name}</td>
                      <td>{role.description || '-'}</td>
                      <td>
                        {role.is_system_role ? (
                          <Badge bg="info">System Role</Badge>
                        ) : (
                          <Badge bg="secondary">Custom Role</Badge>
                        )}
                      </td>
                      <td>
                        <div className="d-flex gap-2">
                          <Button
                            variant="info"
                            size="sm"
                            onClick={() => openPermissionsModal(role)}
                          >
                            Permissions
                          </Button>
                          {!role.is_system_role && (
                            <>
                              <Button
                                variant="primary"
                                size="sm"
                                onClick={() => openEditModal(role)}
                              >
                                Edit
                              </Button>
                              <Button
                                variant="danger"
                                size="sm"
                                onClick={() => openDeleteModal(role)}
                              >
                                Delete
                              </Button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="4" className="text-center py-4">
                      No roles found.
                    </td>
                  </tr>
                )}
              </tbody>
            </Table>
          </div>
        </Card.Body>
      </Card>

      {/* Add Role Modal */}
      <Modal show={showAddModal} onHide={() => setShowAddModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Add New Role</Modal.Title>
        </Modal.Header>
        <Form noValidate validated={validated} onSubmit={handleAddRole}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Role Name</Form.Label>
              <Form.Control
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
              />
              <Form.Control.Feedback type="invalid">
                Role name is required.
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
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Permissions</Form.Label>
              <div className="border rounded p-3" style={{ maxHeight: '300px', overflowY: 'auto' }}>
                <Tabs defaultActiveKey="User Management" id="permissions-tabs">
                  {Object.keys(permissionsByCategory).map((category) => (
                    <Tab key={category} eventKey={category} title={category}>
                      <ListGroup variant="flush">
                        {permissionsByCategory[category].map((permission) => (
                          <ListGroup.Item key={permission.id}>
                            <Form.Check
                              type="checkbox"
                              id={`permission-${permission.id}`}
                              label={`${permission.name} - ${permission.description}`}
                              checked={formData.permissions.includes(permission.id)}
                              onChange={() => handlePermissionChange(permission.id)}
                            />
                          </ListGroup.Item>
                        ))}
                      </ListGroup>
                    </Tab>
                  ))}
                </Tabs>
              </div>
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowAddModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              Add Role
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Edit Role Modal */}
      <Modal show={showEditModal} onHide={() => setShowEditModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Edit Role</Modal.Title>
        </Modal.Header>
        <Form noValidate validated={validated} onSubmit={handleEditRole}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Role Name</Form.Label>
              <Form.Control
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
              />
              <Form.Control.Feedback type="invalid">
                Role name is required.
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
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Permissions</Form.Label>
              <div className="border rounded p-3" style={{ maxHeight: '300px', overflowY: 'auto' }}>
                <Tabs defaultActiveKey="User Management" id="permissions-tabs-edit">
                  {Object.keys(permissionsByCategory).map((category) => (
                    <Tab key={category} eventKey={category} title={category}>
                      <ListGroup variant="flush">
                        {permissionsByCategory[category].map((permission) => (
                          <ListGroup.Item key={permission.id}>
                            <Form.Check
                              type="checkbox"
                              id={`edit-permission-${permission.id}`}
                              label={`${permission.name} - ${permission.description}`}
                              checked={formData.permissions.includes(permission.id)}
                              onChange={() => handlePermissionChange(permission.id)}
                            />
                          </ListGroup.Item>
                        ))}
                      </ListGroup>
                    </Tab>
                  ))}
                </Tabs>
              </div>
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

      {/* Delete Role Modal */}
      <Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Delete Role</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Are you sure you want to delete the role <strong>{selectedRole?.name}</strong>?</p>
          <p>This action cannot be undone. All users assigned to this role will lose the associated permissions.</p>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDeleteRole}>
            Delete Role
          </Button>
        </Modal.Footer>
      </Modal>

      {/* View Permissions Modal */}
      <Modal show={showPermissionsModal} onHide={() => setShowPermissionsModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Permissions for {selectedRole?.name}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {loading ? (
            <div className="text-center py-4">
              <div className="spinner-border" role="status">
                <span className="visually-hidden">Loading permissions...</span>
              </div>
              <p className="mt-2">Loading permissions...</p>
            </div>
          ) : error ? (
            <Alert variant="danger">
              <Alert.Heading>Error Loading Permissions</Alert.Heading>
              <p>{error}</p>
              <div className="d-flex justify-content-end">
                <Button
                  variant="outline-danger"
                  size="sm"
                  onClick={() => {
                    // Retry loading permissions
                    if (selectedRole) {
                      fetchRolePermissions(selectedRole.id);
                    }
                  }}
                >
                  Retry
                </Button>
              </div>
            </Alert>
          ) : selectedRole?.permissions?.length > 0 ? (
            <div>
              <Tabs defaultActiveKey="all" id="permissions-view-tabs">
                <Tab eventKey="all" title="All Permissions">
                  <ListGroup variant="flush" className="mt-3">
                    {selectedRole.permissions.map((permission) => (
                      <ListGroup.Item key={permission.id}>
                        <strong>{permission.name}</strong> - {permission.description}
                      </ListGroup.Item>
                    ))}
                  </ListGroup>
                </Tab>
                {Object.keys(permissionsByCategory).map((category) => {
                  const categoryPermissions = selectedRole.permissions.filter(
                    (p) => p.category === category
                  );
                  if (categoryPermissions.length === 0) return null;

                  return (
                    <Tab key={category} eventKey={category} title={category}>
                      <ListGroup variant="flush" className="mt-3">
                        {categoryPermissions.map((permission) => (
                          <ListGroup.Item key={permission.id}>
                            <strong>{permission.name}</strong> - {permission.description}
                          </ListGroup.Item>
                        ))}
                      </ListGroup>
                    </Tab>
                  );
                })}
              </Tabs>
            </div>
          ) : (
            <Alert variant="info">
              This role has no permissions assigned.
            </Alert>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowPermissionsModal(false)}>
            Close
          </Button>
          {!selectedRole?.is_system_role && (
            <Button
              variant="primary"
              onClick={() => {
                setShowPermissionsModal(false);
                openEditModal(selectedRole);
              }}
              disabled={loading || error}
            >
              Edit Permissions
            </Button>
          )}
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default RoleManagement;
