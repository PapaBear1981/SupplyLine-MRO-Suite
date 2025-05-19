import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Table, Badge, Button, Modal, Form, Alert, Tabs, Tab } from 'react-bootstrap';
import { fetchRegistrationRequests, approveRegistrationRequest, denyRegistrationRequest } from '../../store/adminSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const RegistrationRequests = () => {
  const dispatch = useDispatch();
  const {
    registrationRequests,
    loading,
    error
  } = useSelector((state) => state.admin);

  const [activeTab, setActiveTab] = useState('pending');

  // Modal state
  const [showApproveModal, setShowApproveModal] = useState(false);
  const [showDenyModal, setShowDenyModal] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [adminNotes, setAdminNotes] = useState('');
  const [actionError, setActionError] = useState(null);
  const [actionSuccess, setActionSuccess] = useState(null);

  // Fetch registration requests when component mounts or tab changes
  useEffect(() => {
    dispatch(fetchRegistrationRequests(activeTab));
  }, [dispatch, activeTab]);

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

  const handleApprove = () => {
    if (!selectedRequest) return;
    setActionError(null);
    setActionSuccess(null);

    dispatch(approveRegistrationRequest({
      requestId: selectedRequest.id,
      adminNotes
    }))
      .unwrap()
      .then(() => {
        setActionSuccess('Registration request approved successfully.');
        setShowApproveModal(false);
        // Refresh the list
        dispatch(fetchRegistrationRequests(activeTab));
      })
      .catch((err) => {
        setActionError(err.message || 'Failed to approve registration request.');
      });
  };

  const handleDeny = () => {
    if (!selectedRequest) return;
    setActionError(null);
    setActionSuccess(null);

    dispatch(denyRegistrationRequest({
      requestId: selectedRequest.id,
      adminNotes
    }))
      .unwrap()
      .then(() => {
        setActionSuccess('Registration request denied successfully.');
        setShowDenyModal(false);
        // Refresh the list
        dispatch(fetchRegistrationRequests(activeTab));
      })
      .catch((err) => {
        setActionError(err.message || 'Failed to deny registration request.');
      });
  };

  // Get the appropriate requests based on the active tab
  const getRequests = () => {
    switch (activeTab) {
      case 'pending':
        return registrationRequests?.pending || [];
      case 'approved':
        return registrationRequests?.approved || [];
      case 'denied':
        return registrationRequests?.denied || [];
      case 'all':
        return registrationRequests?.all || [];
      default:
        return [];
    }
  };

  const requests = getRequests();

  if (loading?.registrationRequests && requests.length === 0) {
    return <LoadingSpinner />;
  }

  return (
    <div>
      <Card className="shadow-sm mb-4">
        <Card.Body>
          <Card.Title>Registration Requests</Card.Title>

          {error?.registrationRequests && (
            <Alert variant="danger">
              {error.registrationRequests.message || 'Failed to load registration requests.'}
            </Alert>
          )}

          {actionSuccess && (
            <Alert variant="success" onClose={() => setActionSuccess(null)} dismissible>
              {actionSuccess}
            </Alert>
          )}

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
            disabled={loading?.approveRequest || actionSuccess}
          >
            {loading?.approveRequest ? 'Approving...' : 'Approve'}
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
            disabled={loading?.denyRequest || actionSuccess || !adminNotes.trim()}
          >
            {loading?.denyRequest ? 'Denying...' : 'Deny'}
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
