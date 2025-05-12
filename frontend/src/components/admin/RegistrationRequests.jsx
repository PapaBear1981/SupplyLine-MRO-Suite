import { useState, useEffect } from 'react';
import { Card, Table, Badge, Button, Modal, Form, Alert, Tabs, Tab } from 'react-bootstrap';
import api from '../../services/api';
import LoadingSpinner from '../common/LoadingSpinner';

const RegistrationRequests = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('pending');

  // Modal state
  const [showApproveModal, setShowApproveModal] = useState(false);
  const [showDenyModal, setShowDenyModal] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [adminNotes, setAdminNotes] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [actionError, setActionError] = useState(null);
  const [actionSuccess, setActionSuccess] = useState(null);

  const fetchRequests = async (status = 'pending') => {
    try {
      setLoading(true);

      // Use mock data instead of API call for now
      console.log(`Fetching registration requests with status: ${status}`);

      // Create mock registration requests data
      const mockRequests = [
        {
          id: 1,
          name: 'John Doe',
          employee_number: 'EMP001',
          department: 'Maintenance',
          status: 'pending',
          created_at: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
          processed_at: null,
          processed_by: null,
          admin_notes: null,
          admin_name: null
        },
        {
          id: 2,
          name: 'Jane Smith',
          employee_number: 'EMP002',
          department: 'IT',
          status: 'pending',
          created_at: new Date(Date.now() - 7200000).toISOString(), // 2 hours ago
          processed_at: null,
          processed_by: null,
          admin_notes: null,
          admin_name: null
        },
        {
          id: 3,
          name: 'Bob Johnson',
          employee_number: 'EMP003',
          department: 'Materials',
          status: 'pending',
          created_at: new Date(Date.now() - 10800000).toISOString(), // 3 hours ago
          processed_at: null,
          processed_by: null,
          admin_notes: null,
          admin_name: null
        },
        {
          id: 4,
          name: 'Alice Brown',
          employee_number: 'EMP004',
          department: 'Maintenance',
          status: 'approved',
          created_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
          processed_at: new Date(Date.now() - 43200000).toISOString(), // 12 hours ago
          processed_by: 1,
          admin_notes: 'Approved by admin',
          admin_name: 'Admin User'
        },
        {
          id: 5,
          name: 'Charlie Davis',
          employee_number: 'EMP005',
          department: 'IT',
          status: 'denied',
          created_at: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
          processed_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
          processed_by: 1,
          admin_notes: 'Denied due to invalid information',
          admin_name: 'Admin User'
        }
      ];

      // Filter requests based on status
      let filteredRequests;
      if (status === 'all') {
        filteredRequests = mockRequests;
      } else {
        filteredRequests = mockRequests.filter(req => req.status === status);
      }

      setRequests(filteredRequests);
      setError(null);
    } catch (err) {
      setError('Failed to load registration requests. Please try again later.');
      console.error('Error fetching registration requests:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests(activeTab);
  }, [activeTab]);

  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };

  const openApproveModal = (request) => {
    setSelectedRequest(request);
    setAdminNotes('');
    setActionError(null);
    setActionSuccess(null);
    setShowApproveModal(true);
  };

  const openDenyModal = (request) => {
    setSelectedRequest(request);
    setAdminNotes('');
    setActionError(null);
    setActionSuccess(null);
    setShowDenyModal(true);
  };

  const handleApprove = async () => {
    if (!selectedRequest) return;

    try {
      setActionLoading(true);

      // Mock API call for approving registration request
      console.log(`Approving registration request with ID: ${selectedRequest.id}`);
      console.log(`Admin notes: ${adminNotes}`);

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));

      setActionSuccess('Registration request approved successfully.');

      // Refresh the requests list after a short delay
      setTimeout(() => {
        // Update the request status in the mock data
        const updatedRequests = requests.map(req => {
          if (req.id === selectedRequest.id) {
            return {
              ...req,
              status: 'approved',
              processed_at: new Date().toISOString(),
              processed_by: 1,
              admin_notes: adminNotes,
              admin_name: 'Admin User'
            };
          }
          return req;
        });

        setRequests(updatedRequests);
        setShowApproveModal(false);
        setActionSuccess(null);
      }, 1500);

    } catch (err) {
      setActionError('Failed to approve registration request. Please try again.');
      console.error('Error approving registration request:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeny = async () => {
    if (!selectedRequest) return;

    try {
      setActionLoading(true);

      // Mock API call for denying registration request
      console.log(`Denying registration request with ID: ${selectedRequest.id}`);
      console.log(`Admin notes: ${adminNotes}`);

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));

      setActionSuccess('Registration request denied successfully.');

      // Refresh the requests list after a short delay
      setTimeout(() => {
        // Update the request status in the mock data
        const updatedRequests = requests.map(req => {
          if (req.id === selectedRequest.id) {
            return {
              ...req,
              status: 'denied',
              processed_at: new Date().toISOString(),
              processed_by: 1,
              admin_notes: adminNotes,
              admin_name: 'Admin User'
            };
          }
          return req;
        });

        setRequests(updatedRequests);
        setShowDenyModal(false);
        setActionSuccess(null);
      }, 1500);

    } catch (err) {
      setActionError('Failed to deny registration request. Please try again.');
      console.error('Error denying registration request:', err);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading && requests.length === 0) {
    return <LoadingSpinner />;
  }

  return (
    <div>
      <Card className="shadow-sm mb-4">
        <Card.Body>
          <Card.Title>Registration Requests</Card.Title>

          {error && <Alert variant="danger">{error}</Alert>}

          <Tabs
            activeKey={activeTab}
            onSelect={handleTabChange}
            className="mb-3"
          >
            <Tab eventKey="pending" title="Pending">
              <RequestsTable
                requests={requests}
                status="pending"
                onApprove={openApproveModal}
                onDeny={openDenyModal}
              />
            </Tab>
            <Tab eventKey="approved" title="Approved">
              <RequestsTable
                requests={requests}
                status="approved"
              />
            </Tab>
            <Tab eventKey="denied" title="Denied">
              <RequestsTable
                requests={requests}
                status="denied"
              />
            </Tab>
            <Tab eventKey="all" title="All">
              <RequestsTable
                requests={requests}
                status="all"
                onApprove={openApproveModal}
                onDeny={openDenyModal}
              />
            </Tab>
          </Tabs>
        </Card.Body>
      </Card>

      {/* Approve Modal */}
      <Modal show={showApproveModal} onHide={() => setShowApproveModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Approve Registration Request</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {actionError && <Alert variant="danger">{actionError}</Alert>}
          {actionSuccess && <Alert variant="success">{actionSuccess}</Alert>}

          {selectedRequest && (
            <>
              <p>
                Are you sure you want to approve the registration request for:
                <br />
                <strong>{selectedRequest.name}</strong> ({selectedRequest.employee_number})?
              </p>

              <Form.Group className="mb-3">
                <Form.Label>Admin Notes (Optional)</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={3}
                  value={adminNotes}
                  onChange={(e) => setAdminNotes(e.target.value)}
                  placeholder="Add any notes about this approval"
                />
              </Form.Group>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowApproveModal(false)}>
            Cancel
          </Button>
          <Button
            variant="success"
            onClick={handleApprove}
            disabled={actionLoading || actionSuccess}
          >
            {actionLoading ? 'Approving...' : 'Approve'}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Deny Modal */}
      <Modal show={showDenyModal} onHide={() => setShowDenyModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Deny Registration Request</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {actionError && <Alert variant="danger">{actionError}</Alert>}
          {actionSuccess && <Alert variant="success">{actionSuccess}</Alert>}

          {selectedRequest && (
            <>
              <p>
                Are you sure you want to deny the registration request for:
                <br />
                <strong>{selectedRequest.name}</strong> ({selectedRequest.employee_number})?
              </p>

              <Form.Group className="mb-3">
                <Form.Label>Reason for Denial (Optional)</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={3}
                  value={adminNotes}
                  onChange={(e) => setAdminNotes(e.target.value)}
                  placeholder="Add a reason for denying this request"
                />
              </Form.Group>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDenyModal(false)}>
            Cancel
          </Button>
          <Button
            variant="danger"
            onClick={handleDeny}
            disabled={actionLoading || actionSuccess}
          >
            {actionLoading ? 'Denying...' : 'Deny'}
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

const RequestsTable = ({ requests, status, onApprove, onDeny }) => {
  if (requests.length === 0) {
    return (
      <Alert variant="info">
        No {status === 'all' ? '' : status} registration requests found.
      </Alert>
    );
  }

  return (
    <div className="table-responsive">
      <Table striped hover>
        <thead>
          <tr>
            <th>Name</th>
            <th>Employee Number</th>
            <th>Department</th>
            <th>Date Requested</th>
            <th>Status</th>
            {status === 'pending' || status === 'all' ? <th>Actions</th> : null}
          </tr>
        </thead>
        <tbody>
          {requests.map((request) => (
            <tr key={request.id}>
              <td>{request.name}</td>
              <td>{request.employee_number}</td>
              <td>{request.department}</td>
              <td>{new Date(request.created_at).toLocaleString()}</td>
              <td>
                <StatusBadge status={request.status} />
              </td>
              {(status === 'pending' || status === 'all') && request.status === 'pending' && (
                <td>
                  <Button
                    variant="success"
                    size="sm"
                    className="me-2"
                    onClick={() => onApprove(request)}
                  >
                    Approve
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => onDeny(request)}
                  >
                    Deny
                  </Button>
                </td>
              )}
              {(status === 'all' && request.status !== 'pending') && (
                <td>
                  <span className="text-muted">
                    {request.status === 'approved' ? 'Approved' : 'Denied'} by {request.admin_name || 'Admin'}
                  </span>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
};

const StatusBadge = ({ status }) => {
  let variant;

  switch (status) {
    case 'pending':
      variant = 'warning';
      break;
    case 'approved':
      variant = 'success';
      break;
    case 'denied':
      variant = 'danger';
      break;
    default:
      variant = 'secondary';
  }

  return <Badge bg={variant}>{status}</Badge>;
};

export default RegistrationRequests;
