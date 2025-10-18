import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Modal, Button, Table, Badge, Form, Alert, InputGroup, Tabs, Tab } from 'react-bootstrap';
import {
  FaPencilAlt,
  FaTrash,
  FaPlusCircle,
  FaSearch,
  FaShieldAlt,
  FaExclamationTriangle,
  FaInfoCircle
} from 'react-icons/fa';
import {
  fetchRoles,
  createRole,
  updateRole,
  deleteRole,
  fetchPermissions,
  fetchRole
} from '../../store/rbacSlice';
import LoadingSpinner from '../common/LoadingSpinner';
import PermissionTreeSelector from '../rbac/PermissionTreeSelector';
import PropTypes from 'prop-types';
import './RolesManagementModal.css';

const RolesManagementModal = ({ show, onHide }) => {
  const dispatch = useDispatch();
  const { roles, permissionsByCategory, loading, error } = useSelector(state => state.rbac);

  const [searchTerm, setSearchTerm] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [showEditDetailsForm, setShowEditDetailsForm] = useState(false);
  const [showEditPermissionsForm, setShowEditPermissionsForm] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [selectedRole, setSelectedRole] = useState(null);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    permissions: []
  });

  const [validated, setValidated] = useState(false);

  useEffect(() => {
    if (show) {
      dispatch(fetchRoles());
      dispatch(fetchPermissions());
    }
  }, [show, dispatch]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePermissionsChange = (permissions) => {
    setFormData(prev => ({
      ...prev,
      permissions
    }));
  };

  const resetForm = () => {
    setFormData({ name: '', description: '', permissions: [] });
    setValidated(false);
  };

  const handleAddRole = (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    dispatch(createRole({
      name: formData.name,
      description: formData.description,
      permissions: formData.permissions
    }))
      .unwrap()
      .then(() => {
        setShowAddForm(false);
        resetForm();
        dispatch(fetchRoles());
      })
      .catch(err => {
        console.error('Failed to create role:', err);
      });
  };

  const handleEditDetails = (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    // Build the update payload - include both details and permissions
    const roleData = {
      name: formData.name,
      description: formData.description,
      permissions: formData.permissions
    };

    dispatch(updateRole({
      id: selectedRole.id,
      roleData
    }))
      .unwrap()
      .then(() => {
        setShowEditDetailsForm(false);
        setSelectedRole(null);
        resetForm();
        dispatch(fetchRoles());
      })
      .catch(err => {
        console.error('Failed to update role:', err);
      });
  };

  const handleEditPermissions = () => {
    dispatch(updateRole({ 
      id: selectedRole.id, 
      roleData: {
        permissions: formData.permissions
      }
    }))
      .unwrap()
      .then(() => {
        setShowEditPermissionsForm(false);
        setSelectedRole(null);
        resetForm();
        dispatch(fetchRoles());
      })
      .catch(err => {
        console.error('Failed to update role permissions:', err);
      });
  };

  const openEditDetailsForm = (role) => {
    setSelectedRole(role);

    // Fetch full role details with permissions
    dispatch(fetchRole(role.id))
      .unwrap()
      .then((roleData) => {
        setFormData({
          name: roleData.name,
          description: roleData.description || '',
          permissions: roleData.permissions ? roleData.permissions.map(p => p.id) : []
        });
        setShowEditDetailsForm(true);
      })
      .catch(err => {
        console.error('Failed to fetch role details:', err);
      });
  };

  const openEditPermissionsForm = (role) => {
    setSelectedRole(role);
    
    // Fetch full role details with permissions
    dispatch(fetchRole(role.id))
      .unwrap()
      .then((roleData) => {
        setFormData({
          name: roleData.name,
          description: roleData.description || '',
          permissions: roleData.permissions ? roleData.permissions.map(p => p.id) : []
        });
        setShowEditPermissionsForm(true);
      })
      .catch(err => {
        console.error('Failed to fetch role details:', err);
      });
  };

  const openDeleteConfirm = (role) => {
    setSelectedRole(role);
    setShowDeleteConfirm(true);
  };

  const handleDelete = () => {
    dispatch(deleteRole(selectedRole.id))
      .unwrap()
      .then(() => {
        setShowDeleteConfirm(false);
        setSelectedRole(null);
        dispatch(fetchRoles());
      })
      .catch(err => {
        console.error('Failed to delete role:', err);
      });
  };

  const getPermissionCount = (role) => {
    if (role.permissions && Array.isArray(role.permissions)) {
      return role.permissions.length;
    }
    return 0;
  };

  const filteredRoles = roles.filter(role =>
    role.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (role.description && role.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <>
      <Modal show={show} onHide={onHide} size="xl" className="roles-management-modal">
        <Modal.Header closeButton>
          <Modal.Title>
            <FaShieldAlt className="me-2" />
            Roles Management
          </Modal.Title>
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
                placeholder="Search roles..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </InputGroup>

            <Button
              variant="success"
              onClick={() => setShowAddForm(true)}
              className="add-role-btn"
            >
              <FaPlusCircle className="me-2" />
              Add New Role
            </Button>
          </div>

          {loading ? (
            <LoadingSpinner />
          ) : (
            <div className="roles-table-wrapper">
              <Table hover responsive>
                <thead>
                  <tr>
                    <th>Role Name</th>
                    <th>Description</th>
                    <th>Permissions</th>
                    <th>Type</th>
                    <th style={{ width: '250px' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredRoles.length > 0 ? (
                    filteredRoles.map(role => (
                      <tr key={role.id}>
                        <td>
                          <strong>{role.name}</strong>
                        </td>
                        <td>
                          <span className="text-muted">
                            {role.description || <em>No description</em>}
                          </span>
                        </td>
                        <td>
                          <Badge bg="info">
                            {getPermissionCount(role)} permissions
                          </Badge>
                        </td>
                        <td>
                          {role.is_system_role && (
                            <Badge bg="warning" text="dark">
                              System Role
                            </Badge>
                          )}
                        </td>
                        <td>
                          <div className="d-flex gap-2">
                            <Button
                              variant="outline-success"
                              size="sm"
                              onClick={() => openEditPermissionsForm(role)}
                              title="Edit Permissions"
                            >
                              <FaShieldAlt /> Permissions
                            </Button>
                            {!role.is_system_role && (
                              <>
                                <Button
                                  variant="outline-primary"
                                  size="sm"
                                  onClick={() => openEditDetailsForm(role)}
                                  title="Edit Details"
                                >
                                  <FaPencilAlt />
                                </Button>
                                <Button
                                  variant="outline-danger"
                                  size="sm"
                                  onClick={() => openDeleteConfirm(role)}
                                  title="Delete Role"
                                >
                                  <FaTrash />
                                </Button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="5" className="text-center py-4">
                        {searchTerm ? 'No roles found matching your search.' : 'No roles found.'}
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

      {/* Add Role Modal */}
      <Modal show={showAddForm} onHide={() => { setShowAddForm(false); resetForm(); }} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Add New Role</Modal.Title>
        </Modal.Header>
        <Form noValidate validated={validated} onSubmit={handleAddRole}>
          <Modal.Body>
            <Tabs defaultActiveKey="details" className="mb-3">
              <Tab eventKey="details" title="Role Details">
                <Form.Group className="mb-3">
                  <Form.Label>Role Name *</Form.Label>
                  <Form.Control
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    placeholder="Enter role name"
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
                    placeholder="Enter role description (optional)"
                  />
                </Form.Group>
              </Tab>

              <Tab eventKey="permissions" title="Permissions">
                <Alert variant="info">
                  <FaInfoCircle className="me-2" />
                  Select the permissions to assign to this role. You can also add permissions later.
                </Alert>
                {Object.keys(permissionsByCategory).length > 0 ? (
                  <PermissionTreeSelector
                    permissionsByCategory={permissionsByCategory}
                    selectedPermissions={formData.permissions}
                    onChange={handlePermissionsChange}
                  />
                ) : (
                  <p className="text-muted">Loading permissions...</p>
                )}
              </Tab>
            </Tabs>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => { setShowAddForm(false); resetForm(); }}>
              Cancel
            </Button>
            <Button variant="success" type="submit" disabled={loading}>
              Add Role
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Edit Role Details Modal */}
      <Modal show={showEditDetailsForm} onHide={() => { setShowEditDetailsForm(false); setSelectedRole(null); resetForm(); }} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Edit Role: {selectedRole?.name}</Modal.Title>
        </Modal.Header>
        <Form noValidate validated={validated} onSubmit={handleEditDetails}>
          <Modal.Body>
            {selectedRole?.is_system_role && (
              <Alert variant="warning">
                <FaExclamationTriangle className="me-2" />
                This is a system role. You cannot modify its name or description, but you can edit its permissions.
              </Alert>
            )}

            <Tabs defaultActiveKey="details" className="mb-3">
              <Tab eventKey="details" title="Role Details">
                <Form.Group className="mb-3">
                  <Form.Label>Role Name *</Form.Label>
                  <Form.Control
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    placeholder="Enter role name"
                    disabled={selectedRole?.is_system_role}
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
                    placeholder="Enter role description (optional)"
                    disabled={selectedRole?.is_system_role}
                  />
                </Form.Group>
              </Tab>

              <Tab eventKey="permissions" title="Permissions">
                <Alert variant="info">
                  <FaInfoCircle className="me-2" />
                  {selectedRole?.is_system_role
                    ? 'You can modify permissions for this system role to customize access levels.'
                    : 'Select the permissions to assign to this role.'}
                </Alert>
                {Object.keys(permissionsByCategory).length > 0 ? (
                  <PermissionTreeSelector
                    permissionsByCategory={permissionsByCategory}
                    selectedPermissions={formData.permissions}
                    onChange={handlePermissionsChange}
                  />
                ) : (
                  <p className="text-muted">Loading permissions...</p>
                )}
              </Tab>
            </Tabs>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => { setShowEditDetailsForm(false); setSelectedRole(null); resetForm(); }}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" disabled={loading}>
              Save Changes
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Edit Role Permissions Modal */}
      <Modal
        show={showEditPermissionsForm}
        onHide={() => { setShowEditPermissionsForm(false); setSelectedRole(null); resetForm(); }}
        size="lg"
      >
        <Modal.Header closeButton>
          <Modal.Title>
            <FaShieldAlt className="me-2" />
            Edit Permissions for {selectedRole?.name}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedRole?.is_system_role && (
            <Alert variant="info">
              <FaInfoCircle className="me-2" />
              This is a system role. You can modify its permissions to customize access levels.
            </Alert>
          )}

          {Object.keys(permissionsByCategory).length > 0 ? (
            <PermissionTreeSelector
              permissionsByCategory={permissionsByCategory}
              selectedPermissions={formData.permissions}
              onChange={handlePermissionsChange}
            />
          ) : (
            <LoadingSpinner />
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => { setShowEditPermissionsForm(false); setSelectedRole(null); resetForm(); }}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleEditPermissions} disabled={loading}>
            Save Permissions
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal show={showDeleteConfirm} onHide={() => { setShowDeleteConfirm(false); setSelectedRole(null); }}>
        <Modal.Header closeButton>
          <Modal.Title>
            <FaExclamationTriangle className="text-warning me-2" />
            Confirm Delete
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>
            Are you sure you want to delete the role <strong>&quot;{selectedRole?.name}&quot;</strong>?
          </p>
          <Alert variant="warning">
            <strong>Warning:</strong> This action cannot be undone. All users assigned to this role will lose these permissions.
          </Alert>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => { setShowDeleteConfirm(false); setSelectedRole(null); }}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDelete} disabled={loading}>
            Delete Role
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

RolesManagementModal.propTypes = {
  show: PropTypes.bool.isRequired,
  onHide: PropTypes.func.isRequired
};

export default RolesManagementModal;

