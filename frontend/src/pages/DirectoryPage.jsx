import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Form, InputGroup, Table, Badge, Button, Card, Spinner } from 'react-bootstrap';
import { toast } from 'react-toastify';
import api from '../services/api';
import UserProfileModal from '../components/users/UserProfileModal';

const DirectoryPage = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

  // Helper function to get department badge color
  const getDepartmentBadgeVariant = (department) => {
    const departmentColors = {
      'Materials': 'primary',
      'Engineering': 'info',
      'Maintenance': 'warning',
      'Quality': 'success',
      'Production': 'danger',
      'Safety': 'dark',
      'Administration': 'secondary',
    };
    return departmentColors[department] || 'secondary';
  };

  // Fetch current user permissions
  useEffect(() => {
    const fetchCurrentUser = async () => {
      try {
        const response = await api.get('/auth/me');
        setCurrentUser(response.data);
      } catch (error) {
        console.error('Error fetching current user:', error);
      }
    };
    fetchCurrentUser();
  }, []);

  // Fetch users list
  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true);
      try {
        const endpoint = searchQuery
          ? `/users?q=${encodeURIComponent(searchQuery)}`
          : '/users';

        const response = await api.get(endpoint);
        setUsers(response.data);
      } catch (error) {
        console.error('Error fetching users:', error);
        toast.error('Failed to load directory. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    // Debounce search
    const timeoutId = setTimeout(() => {
      fetchUsers();
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  const handleUserClick = (user) => {
    setSelectedUser(user);
    setShowProfileModal(true);
  };

  const handleCloseModal = () => {
    setShowProfileModal(false);
    setSelectedUser(null);
  };

  const handleUserUpdated = (updatedUser) => {
    setUsers(users.map(u => u.id === updatedUser.id ? updatedUser : u));
  };

  return (
    <Container fluid className="p-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="mb-1">Employee Directory</h1>
          <p className="text-muted mb-0">
            Search and view employee profiles, checkouts, and history.
          </p>
        </div>
      </div>

      <Card className="shadow-sm border-0">
        <Card.Body className="p-0">
          <div className="p-3 border-bottom">
            <Row>
              <Col md={6} lg={4}>
                <InputGroup>
                  <InputGroup.Text className="border-end-0">
                    <i className="bi bi-search text-muted"></i>
                  </InputGroup.Text>
                  <Form.Control
                    placeholder="Search by name or badge ID..."
                    className="border-start-0 ps-0"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </InputGroup>
              </Col>
            </Row>
          </div>

          {loading ? (
            <div className="text-center p-5">
              <Spinner animation="border" variant="primary" />
              <p className="mt-2 text-muted">Loading directory...</p>
            </div>
          ) : users.length === 0 ? (
            <div className="text-center p-5">
              <div className="display-1 text-muted mb-3">
                <i className="bi bi-people"></i>
              </div>
              <h3>No employees found</h3>
              <p className="text-muted">
                Try adjusting your search terms.
              </p>
            </div>
          ) : (
            <Table hover responsive className="mb-0 align-middle">
              <thead>
                <tr>
                  <th className="ps-4">Employee</th>
                  <th>Badge ID</th>
                  <th>Department</th>
                  <th>Status</th>
                  <th className="text-end pe-4">Action</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr
                    key={user.id}
                    onClick={() => handleUserClick(user)}
                    style={{ cursor: 'pointer' }}
                  >
                    <td className="ps-4">
                      <div className="d-flex align-items-center">
                        <div
                          className="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center me-3"
                          style={{ width: '40px', height: '40px', fontSize: '1.2rem' }}
                        >
                          {user.name.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <div className="fw-bold">{user.name}</div>
                          <div className="small text-muted">{user.email || 'No email'}</div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className="font-monospace">{user.employee_number}</span>
                    </td>
                    <td>
                      <Badge bg={getDepartmentBadgeVariant(user.department)}>
                        {user.department || 'Unassigned'}
                      </Badge>
                    </td>
                    <td>
                      {user.is_active ? (
                        <Badge bg="success-subtle" text="success" className="d-inline-flex align-items-center gap-1">
                          <i className="bi bi-check-circle-fill" style={{ fontSize: '0.8em' }}></i>
                          Active
                        </Badge>
                      ) : (
                        <Badge bg="secondary-subtle" text="secondary">Inactive</Badge>
                      )}
                      {user.is_admin && (
                        <Badge bg="primary-subtle" text="primary" className="ms-2">Admin</Badge>
                      )}
                    </td>
                    <td className="text-end pe-4">
                      <Button
                        variant="link"
                        className="text-decoration-none p-0"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleUserClick(user);
                        }}
                      >
                        View Profile <i className="bi bi-arrow-right ms-1"></i>
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card.Body>
        <Card.Footer className="text-muted small">
          Showing {users.length} employees
        </Card.Footer>
      </Card>

      {selectedUser && (
        <UserProfileModal
          show={showProfileModal}
          onHide={handleCloseModal}
          userId={selectedUser.id}
          onUserUpdated={handleUserUpdated}
        />
      )}
    </Container>
  );
};

export default DirectoryPage;
