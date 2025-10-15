import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { Container, Row, Col, Card, Button, Tabs, Tab, Badge, Alert } from 'react-bootstrap';
import { FaEdit, FaCopy, FaBox, FaExchangeAlt, FaShoppingCart, FaEnvelope, FaChartBar, FaArrowLeft, FaPlus } from 'react-icons/fa';
import { fetchKitById, fetchKitItems, fetchKitIssuances, fetchKitAlerts, fetchReorderRequests } from '../store/kitsSlice';
import { fetchTransfers } from '../store/kitTransfersSlice';
import { fetchKitMessages } from '../store/kitMessagesSlice';
import LoadingSpinner from '../components/common/LoadingSpinner';
import KitItemsList from '../components/kits/KitItemsList';
import KitAlerts from '../components/kits/KitAlerts';
import KitIssuanceForm from '../components/kits/KitIssuanceForm';
import KitIssuanceHistory from '../components/kits/KitIssuanceHistory';
import KitTransferForm from '../components/kits/KitTransferForm';
import KitMessaging from '../components/kits/KitMessaging';
import KitReorderManagement from '../components/kits/KitReorderManagement';
import AddKitItemModal from '../components/kits/AddKitItemModal';
import RequestReorderModal from '../components/kits/RequestReorderModal';
import SendMessageModal from '../components/kits/SendMessageModal';

const KitDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const { currentKit, loading, error } = useSelector((state) => state.kits);
  const [activeTab, setActiveTab] = useState('overview');
  const [showIssuanceForm, setShowIssuanceForm] = useState(false);
  const [showTransferForm, setShowTransferForm] = useState(false);
  const [showAddItemModal, setShowAddItemModal] = useState(false);
  const [showReorderModal, setShowReorderModal] = useState(false);
  const [showMessageModal, setShowMessageModal] = useState(false);

  useEffect(() => {
    if (id) {
      dispatch(fetchKitById(id));
      dispatch(fetchKitAlerts(id));
    }
  }, [dispatch, id]);

  useEffect(() => {
    if (id && activeTab === 'items') {
      dispatch(fetchKitItems({ kitId: id }));
    } else if (id && activeTab === 'issuances') {
      dispatch(fetchKitIssuances({ kitId: id }));
    } else if (id && activeTab === 'transfers') {
      dispatch(fetchTransfers({ from_kit_id: id }));
    } else if (id && activeTab === 'messages') {
      dispatch(fetchKitMessages({ kitId: id }));
    }
  }, [dispatch, id, activeTab]);

  if (loading && !currentKit) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <Container className="py-4">
        <Alert variant="danger">
          {error.message || 'Failed to load kit details'}
        </Alert>
      </Container>
    );
  }

  if (!currentKit) {
    return (
      <Container className="py-4">
        <Alert variant="warning">Kit not found</Alert>
      </Container>
    );
  }

  const getStatusBadge = (status) => {
    const variants = {
      active: 'success',
      inactive: 'secondary',
      maintenance: 'warning'
    };
    return <Badge bg={variants[status] || 'secondary'}>{status}</Badge>;
  };

  return (
    <Container fluid className="py-4">
      {/* Header */}
      <Row className="mb-4">
        <Col>
          <Button variant="link" onClick={() => navigate('/kits')} className="mb-2 p-0">
            <FaArrowLeft className="me-2" />
            Back to Kits
          </Button>
          <div className="d-flex justify-content-between align-items-start">
            <div>
              <h2 className="mb-1">{currentKit.name}</h2>
              <div className="text-muted">
                {currentKit.aircraft_type?.name || 'Unknown Aircraft Type'}
                <span className="ms-3">{getStatusBadge(currentKit.status)}</span>
              </div>
            </div>
            <div>
              <Button 
                variant="outline-primary" 
                size="sm" 
                className="me-2"
                onClick={() => navigate(`/kits/${id}/edit`)}
              >
                <FaEdit className="me-1" />
                Edit
              </Button>
              <Button 
                variant="outline-secondary" 
                size="sm"
                onClick={() => navigate(`/kits/new?duplicate=${id}`)}
              >
                <FaCopy className="me-1" />
                Duplicate
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {/* Quick Stats */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <FaBox size={32} className="text-primary mb-2" />
              <h4 className="mb-0">{currentKit.box_count || 0}</h4>
              <small className="text-muted">Boxes</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <FaBox size={32} className="text-success mb-2" />
              <h4 className="mb-0">{currentKit.item_count || 0}</h4>
              <small className="text-muted">Items</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <FaExchangeAlt size={32} className="text-info mb-2" />
              <h4 className="mb-0">{currentKit.transfer_count || 0}</h4>
              <small className="text-muted">Transfers</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <FaShoppingCart size={32} className="text-warning mb-2" />
              <h4 className="mb-0">{currentKit.pending_reorders || 0}</h4>
              <small className="text-muted">Pending Reorders</small>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Alerts */}
      <KitAlerts kitId={id} />

      {/* Action Buttons */}
      <Row className="mb-4">
        <Col>
          <Card>
            <Card.Body>
              <h6 className="mb-3">Quick Actions</h6>
              <Button
                variant="success"
                size="sm"
                className="me-2 mb-2"
                onClick={() => setShowAddItemModal(true)}
              >
                <FaPlus className="me-1" />
                Add Items
              </Button>
              <Button
                variant="primary"
                size="sm"
                className="me-2 mb-2"
                onClick={() => setShowIssuanceForm(true)}
              >
                <FaBox className="me-1" />
                Issue Items
              </Button>
              <Button
                variant="info"
                size="sm"
                className="me-2 mb-2"
                onClick={() => setShowTransferForm(true)}
              >
                <FaExchangeAlt className="me-1" />
                Transfer Items
              </Button>
              <Button
                variant="warning"
                size="sm"
                className="me-2 mb-2"
                onClick={() => setShowReorderModal(true)}
              >
                <FaShoppingCart className="me-1" />
                Request Reorder
              </Button>
              <Button
                variant="secondary"
                size="sm"
                className="me-2 mb-2"
                onClick={() => setShowMessageModal(true)}
              >
                <FaEnvelope className="me-1" />
                Send Message
              </Button>
              <Button variant="outline-primary" size="sm" className="mb-2">
                <FaChartBar className="me-1" />
                View Analytics
              </Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Tabs */}
      <Tabs
        activeKey={activeTab}
        onSelect={(k) => setActiveTab(k)}
        className="mb-3"
      >
        <Tab eventKey="overview" title="Overview">
          <Card>
            <Card.Body>
              <h5>Kit Information</h5>
              <Row className="mt-3">
                <Col md={6}>
                  <p><strong>Name:</strong> {currentKit.name}</p>
                  <p><strong>Aircraft Type:</strong> {currentKit.aircraft_type?.name}</p>
                  <p><strong>Status:</strong> {getStatusBadge(currentKit.status)}</p>
                </Col>
                <Col md={6}>
                  <p><strong>Created:</strong> {new Date(currentKit.created_at).toLocaleDateString()}</p>
                  <p><strong>Created By:</strong> {currentKit.created_by_name || 'Unknown'}</p>
                  {currentKit.updated_at && (
                    <p><strong>Last Updated:</strong> {new Date(currentKit.updated_at).toLocaleDateString()}</p>
                  )}
                </Col>
              </Row>
              {currentKit.description && (
                <>
                  <h6 className="mt-4">Description</h6>
                  <p>{currentKit.description}</p>
                </>
              )}
            </Card.Body>
          </Card>
        </Tab>

        <Tab eventKey="items" title={`Items (${currentKit.item_count || 0})`}>
          <KitItemsList kitId={id} />
        </Tab>

        <Tab eventKey="issuances" title="Issuances">
          <KitIssuanceHistory kitId={id} />
        </Tab>

        <Tab eventKey="transfers" title="Transfers">
          <Card>
            <Card.Body>
              <p className="text-muted">Transfer history will be displayed here</p>
            </Card.Body>
          </Card>
        </Tab>

        <Tab eventKey="reorders" title={`Reorders ${currentKit.pending_reorders > 0 ? `(${currentKit.pending_reorders})` : ''}`}>
          <KitReorderManagement kitId={id} />
        </Tab>

        <Tab eventKey="messages" title="Messages">
          <KitMessaging kitId={id} />
        </Tab>
      </Tabs>

      {/* Add Item Modal */}
      <AddKitItemModal
        show={showAddItemModal}
        onHide={() => setShowAddItemModal(false)}
        kitId={id}
        onSuccess={() => {
          dispatch(fetchKitById(id));
          dispatch(fetchKitItems({ kitId: id }));
        }}
      />

      {/* Issuance Form Modal */}
      <KitIssuanceForm
        show={showIssuanceForm}
        onHide={() => setShowIssuanceForm(false)}
        kitId={id}
      />

      {/* Transfer Form Modal */}
      <KitTransferForm
        show={showTransferForm}
        onHide={() => setShowTransferForm(false)}
        sourceKitId={id}
      />

      {/* Request Reorder Modal */}
      <RequestReorderModal
        show={showReorderModal}
        onHide={() => setShowReorderModal(false)}
        kitId={id}
        onSuccess={() => {
          dispatch(fetchReorderRequests({ kitId: id }));
          dispatch(fetchKitById(id));
        }}
      />

      {/* Send Message Modal */}
      <SendMessageModal
        show={showMessageModal}
        onHide={() => setShowMessageModal(false)}
        kitId={id}
        kitName={currentKit?.name}
      />
    </Container>
  );
};

export default KitDetailPage;

