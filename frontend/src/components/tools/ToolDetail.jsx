import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Row, Col, Button, Table, Badge, Tabs, Tab } from 'react-bootstrap';
import { fetchToolById } from '../../store/toolsSlice';
import { fetchToolCheckoutHistory } from '../../store/checkoutsSlice';
import LoadingSpinner from '../common/LoadingSpinner';
import CheckoutModal from '../checkouts/CheckoutModal';
import RemoveFromServiceModal from './RemoveFromServiceModal';
import ReturnToServiceModal from './ReturnToServiceModal';
import ServiceHistoryList from './ServiceHistoryList';

const ToolDetail = () => {
  const { id } = useParams();
  const dispatch = useDispatch();
  const { currentTool, loading: toolLoading } = useSelector((state) => state.tools);
  const { checkoutHistory, loading: historyLoading } = useSelector((state) => state.checkouts);
  const { user } = useSelector((state) => state.auth);

  const [showCheckoutModal, setShowCheckoutModal] = useState(false);
  const [showRemoveFromServiceModal, setShowRemoveFromServiceModal] = useState(false);
  const [showReturnToServiceModal, setShowReturnToServiceModal] = useState(false);
  const [activeTab, setActiveTab] = useState('details');

  useEffect(() => {
    if (id) {
      dispatch(fetchToolById(id));
      dispatch(fetchToolCheckoutHistory(id));
    }
  }, [dispatch, id]);

  if (toolLoading || !currentTool) {
    return <LoadingSpinner />;
  }

  const history = checkoutHistory[id] || [];
  const isAdmin = user?.is_admin || user?.department === 'Materials';

  return (
    <>
      <div>
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>Tool Details</h2>
          <div>
            <Button as={Link} to="/tools" variant="secondary" className="me-2">
              Back to Tools
            </Button>
            {isAdmin && (
              <Button as={Link} to={`/tools/${id}/edit`} variant="primary">
                Edit Tool
              </Button>
            )}
          </div>
        </div>

        <Row>
          <Col md={6}>
            <Card className="mb-4">
              <Card.Header>
                <h4>{currentTool.name}</h4>
              </Card.Header>
              <Card.Body>
                <Row className="mb-3">
                  <Col sm={4} className="fw-bold">ID:</Col>
                  <Col sm={8}>{currentTool.id}</Col>
                </Row>
                <Row className="mb-3">
                  <Col sm={4} className="fw-bold">Category:</Col>
                  <Col sm={8}>{currentTool.category}</Col>
                </Row>
                <Row className="mb-3">
                  <Col sm={4} className="fw-bold">Location:</Col>
                  <Col sm={8}>{currentTool.location}</Col>
                </Row>
                <Row className="mb-3">
                  <Col sm={4} className="fw-bold">Status:</Col>
                  <Col sm={8}>
                    <Badge bg={
                      currentTool.status === 'available' ? 'success' :
                      currentTool.status === 'checked_out' ? 'warning' :
                      currentTool.status === 'maintenance' ? 'info' : 'danger'
                    }>
                      {currentTool.status === 'available' ? 'Available' :
                       currentTool.status === 'checked_out' ? 'Checked Out' :
                       currentTool.status === 'maintenance' ? 'Maintenance/Calibration' : 'Retired'}
                    </Badge>

                    {currentTool.status_reason && (currentTool.status === 'maintenance' || currentTool.status === 'retired') && (
                      <div className="mt-2">
                        <small className="text-muted">Reason: {currentTool.status_reason}</small>
                      </div>
                    )}
                  </Col>
                </Row>
                <Row className="mb-3">
                  <Col sm={4} className="fw-bold">Condition:</Col>
                  <Col sm={8}>{currentTool.condition}</Col>
                </Row>
                <Row className="mb-3">
                  <Col sm={4} className="fw-bold">Purchase Date:</Col>
                  <Col sm={8}>{new Date(currentTool.purchase_date).toLocaleDateString()}</Col>
                </Row>
                {currentTool.description && (
                  <Row className="mb-3">
                    <Col sm={4} className="fw-bold">Description:</Col>
                    <Col sm={8}>{currentTool.description}</Col>
                  </Row>
                )}
              </Card.Body>
              <Card.Footer>
                <div className="d-flex flex-wrap gap-2">
                  {currentTool.status === 'available' && (
                    <>
                      <Button as={Link} to={`/checkout/${currentTool.id}`} variant="success">
                        Checkout to Me
                      </Button>
                      <Button
                        variant="primary"
                        onClick={() => setShowCheckoutModal(true)}
                      >
                        Checkout to User
                      </Button>
                      {isAdmin && (
                        <Button
                          variant="warning"
                          onClick={() => setShowRemoveFromServiceModal(true)}
                        >
                          Remove from Service
                        </Button>
                      )}
                    </>
                  )}

                  {currentTool.status === 'checked_out' && (
                    <Button disabled variant="secondary">
                      Currently Checked Out
                    </Button>
                  )}

                  {(currentTool.status === 'maintenance' || currentTool.status === 'retired') && (
                    <>
                      <Button disabled variant="secondary">
                        Out of Service
                      </Button>
                      {isAdmin && (
                        <Button
                          variant="success"
                          onClick={() => setShowReturnToServiceModal(true)}
                        >
                          Return to Service
                        </Button>
                      )}
                    </>
                  )}
                </div>
              </Card.Footer>
            </Card>
          </Col>

          <Col md={6}>
            <Card>
              <Card.Header>
                <Tabs
                  activeKey={activeTab}
                  onSelect={(k) => setActiveTab(k)}
                  className="card-header-tabs"
                >
                  <Tab eventKey="details" title="Checkout History" />
                  <Tab eventKey="service" title="Service History" />
                </Tabs>
              </Card.Header>
              <Card.Body>
                {activeTab === 'details' ? (
                  historyLoading ? (
                    <LoadingSpinner size="sm" text="Loading checkout history..." />
                  ) : (
                    <Table striped bordered hover responsive>
                      <thead>
                        <tr>
                          <th>User</th>
                          <th>Checkout Date</th>
                          <th>Return Date</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {history.length > 0 ? (
                          history.map((checkout) => (
                            <tr key={checkout.id}>
                              <td>{checkout.user_name}</td>
                              <td>{new Date(checkout.checkout_date).toLocaleDateString()}</td>
                              <td>
                                {checkout.return_date
                                  ? new Date(checkout.return_date).toLocaleDateString()
                                  : 'Not returned'}
                              </td>
                              <td>
                                <Badge bg={
                                  checkout.status === 'Returned' ? 'success' : 'warning'
                                }>
                                  {checkout.status}
                                </Badge>
                              </td>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td colSpan="4" className="text-center">
                              No checkout history available.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </Table>
                  )
                ) : (
                  <ServiceHistoryList toolId={id} />
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Modals */}
        <CheckoutModal
          show={showCheckoutModal}
          onHide={() => setShowCheckoutModal(false)}
          tool={currentTool}
        />

        <RemoveFromServiceModal
          show={showRemoveFromServiceModal}
          onHide={() => setShowRemoveFromServiceModal(false)}
          tool={currentTool}
        />

        <ReturnToServiceModal
          show={showReturnToServiceModal}
          onHide={() => setShowReturnToServiceModal(false)}
          tool={currentTool}
        />
      </div>
    </>
  );
};

export default ToolDetail;
