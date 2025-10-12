import { useState, useEffect } from 'react';
import { 
  Card, Table, Button, Form, InputGroup, Alert, Modal, Badge, Spinner 
} from 'react-bootstrap';
import { FaSearch, FaKey, FaCopy, FaCheck, FaExclamationTriangle } from 'react-icons/fa';
import api from '../../services/api';

const PasswordReset = () => {
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [departmentFilter, setDepartmentFilter] = useState('');
  const [includeInactive, setIncludeInactive] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Modal states
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [temporaryPassword, setTemporaryPassword] = useState('');
  const [copied, setCopied] = useState(false);
  const [resetting, setResetting] = useState(false);

  // Fetch users on component mount
  useEffect(() => {
    fetchUsers();
  }, [includeInactive]);

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams();
      if (searchQuery) params.append('q', searchQuery);
      if (departmentFilter) params.append('department', departmentFilter);
      if (includeInactive) params.append('include_inactive', 'true');
      
      const response = await api.get(`/admin/users/search?${params.toString()}`);
      setUsers(response.data);
      setFilteredUsers(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch users');
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle search
  const handleSearch = () => {
    fetchUsers();
  };

  // Handle reset password button click
  const handleResetClick = (user) => {
    setSelectedUser(user);
    setShowConfirmModal(true);
  };

  // Confirm and execute password reset
  const confirmPasswordReset = async () => {
    if (!selectedUser) return;
    
    setResetting(true);
    setError(null);
    
    try {
      const response = await api.post(`/admin/users/${selectedUser.id}/reset-password`);
      
      setTemporaryPassword(response.data.temporary_password);
      setShowConfirmModal(false);
      setShowPasswordModal(true);
      setSuccess(`Password reset successfully for ${selectedUser.name}`);
      
      // Refresh user list
      fetchUsers();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to reset password');
      console.error('Error resetting password:', err);
      setShowConfirmModal(false);
    } finally {
      setResetting(false);
    }
  };

  // Copy password to clipboard
  const copyToClipboard = () => {
    navigator.clipboard.writeText(temporaryPassword);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Close password modal
  const closePasswordModal = () => {
    setShowPasswordModal(false);
    setTemporaryPassword('');
    setSelectedUser(null);
    setCopied(false);
  };

  // Get unique departments for filter
  const departments = [...new Set(users.map(u => u.department).filter(Boolean))];

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div>
      <Card>
        <Card.Header>
          <h5 className="mb-0">Password Reset Management</h5>
        </Card.Header>
        <Card.Body>
          {/* Alert Messages */}
          {error && (
            <Alert variant="danger" dismissible onClose={() => setError(null)}>
              {error}
            </Alert>
          )}
          {success && (
            <Alert variant="success" dismissible onClose={() => setSuccess(null)}>
              {success}
            </Alert>
          )}

          {/* Search and Filter Controls */}
          <div className="mb-3">
            <div className="row g-2">
              <div className="col-md-5">
                <InputGroup>
                  <Form.Control
                    type="text"
                    placeholder="Search by employee number or name..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  />
                  <Button variant="primary" onClick={handleSearch}>
                    <FaSearch /> Search
                  </Button>
                </InputGroup>
              </div>
              <div className="col-md-3">
                <Form.Select
                  value={departmentFilter}
                  onChange={(e) => setDepartmentFilter(e.target.value)}
                >
                  <option value="">All Departments</option>
                  {departments.map(dept => (
                    <option key={dept} value={dept}>{dept}</option>
                  ))}
                </Form.Select>
              </div>
              <div className="col-md-4">
                <Form.Check
                  type="checkbox"
                  label="Include inactive users"
                  checked={includeInactive}
                  onChange={(e) => setIncludeInactive(e.target.checked)}
                />
              </div>
            </div>
          </div>

          {/* Users Table */}
          {loading ? (
            <div className="text-center py-4">
              <Spinner animation="border" role="status">
                <span className="visually-hidden">Loading...</span>
              </Spinner>
            </div>
          ) : filteredUsers.length === 0 ? (
            <Alert variant="info">
              No users found. Try adjusting your search criteria.
            </Alert>
          ) : (
            <Table striped bordered hover responsive>
              <thead>
                <tr>
                  <th>Employee Number</th>
                  <th>Name</th>
                  <th>Department</th>
                  <th>Last Password Change</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map(user => (
                  <tr key={user.id}>
                    <td>{user.employee_number}</td>
                    <td>
                      {user.name}
                      {user.is_admin && (
                        <Badge bg="danger" className="ms-2">Admin</Badge>
                      )}
                    </td>
                    <td>{user.department || 'N/A'}</td>
                    <td>{formatDate(user.password_changed_at)}</td>
                    <td>
                      {user.is_active ? (
                        <Badge bg="success">Active</Badge>
                      ) : (
                        <Badge bg="secondary">Inactive</Badge>
                      )}
                      {user.force_password_change && (
                        <Badge bg="warning" text="dark" className="ms-1">
                          Must Change Password
                        </Badge>
                      )}
                    </td>
                    <td>
                      <Button
                        variant="warning"
                        size="sm"
                        onClick={() => handleResetClick(user)}
                        disabled={!user.is_active}
                      >
                        <FaKey /> Reset Password
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card.Body>
      </Card>

      {/* Confirmation Modal */}
      <Modal show={showConfirmModal} onHide={() => setShowConfirmModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>
            <FaExclamationTriangle className="text-warning me-2" />
            Confirm Password Reset
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedUser && (
            <>
              <p>Are you sure you want to reset the password for:</p>
              <ul>
                <li><strong>Name:</strong> {selectedUser.name}</li>
                <li><strong>Employee Number:</strong> {selectedUser.employee_number}</li>
                <li><strong>Department:</strong> {selectedUser.department || 'N/A'}</li>
              </ul>
              <Alert variant="warning">
                <strong>Warning:</strong> This will generate a new temporary password and force the user to change it on next login.
              </Alert>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowConfirmModal(false)} disabled={resetting}>
            Cancel
          </Button>
          <Button variant="warning" onClick={confirmPasswordReset} disabled={resetting}>
            {resetting ? (
              <>
                <Spinner animation="border" size="sm" className="me-2" />
                Resetting...
              </>
            ) : (
              <>
                <FaKey className="me-2" />
                Reset Password
              </>
            )}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Temporary Password Display Modal */}
      <Modal show={showPasswordModal} onHide={closePasswordModal} backdrop="static">
        <Modal.Header closeButton>
          <Modal.Title>
            <FaCheck className="text-success me-2" />
            Password Reset Successful
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedUser && (
            <>
              <Alert variant="success">
                Password has been reset for <strong>{selectedUser.name}</strong>
              </Alert>
              
              <Alert variant="danger">
                <strong>⚠️ IMPORTANT:</strong> This temporary password will only be shown once. 
                Please copy it now and provide it to the user securely.
              </Alert>

              <div className="mb-3">
                <Form.Label><strong>Temporary Password:</strong></Form.Label>
                <InputGroup>
                  <Form.Control
                    type="text"
                    value={temporaryPassword}
                    readOnly
                    style={{ fontFamily: 'monospace', fontSize: '1.1rem' }}
                  />
                  <Button 
                    variant={copied ? 'success' : 'primary'} 
                    onClick={copyToClipboard}
                  >
                    {copied ? (
                      <>
                        <FaCheck /> Copied!
                      </>
                    ) : (
                      <>
                        <FaCopy /> Copy
                      </>
                    )}
                  </Button>
                </InputGroup>
              </div>

              <Alert variant="info">
                The user will be required to change this password on their next login.
              </Alert>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="primary" onClick={closePasswordModal}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default PasswordReset;

