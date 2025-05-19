import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Row, Col, Button, Table, Badge, Tabs, Tab, Alert } from 'react-bootstrap';
import { fetchToolById } from '../../store/toolsSlice';
import { fetchToolCheckoutHistory } from '../../store/checkoutsSlice';
import { fetchToolCalibrations } from '../../store/calibrationSlice';
import LoadingSpinner from '../common/LoadingSpinner';
import CheckoutModal from '../checkouts/CheckoutModal';
import RemoveFromServiceModal from './RemoveFromServiceModal';
import ReturnToServiceModal from './ReturnToServiceModal';
import ServiceHistoryList from './ServiceHistoryList';
import ToolCalibrationHistory from '../calibration/ToolCalibrationHistory';
import Tooltip from '../common/Tooltip';
import HelpIcon from '../common/HelpIcon';
import HelpContent from '../common/HelpContent';
import { useHelp } from '../../context/HelpContext';

const ToolDetail = () => {
  const { id } = useParams();
  const dispatch = useDispatch();
  const { currentTool, loading: toolLoading } = useSelector((state) => state.tools);
  const { checkoutHistory, loading: historyLoading } = useSelector((state) => state.checkouts);
  const { user } = useSelector((state) => state.auth);
  const { showTooltips, showHelp, getHelpContent } = useHelp();

  const [showCheckoutModal, setShowCheckoutModal] = useState(false);
  const [showRemoveFromServiceModal, setShowRemoveFromServiceModal] = useState(false);
  const [showReturnToServiceModal, setShowReturnToServiceModal] = useState(false);
  const [activeTab, setActiveTab] = useState('details');

  useEffect(() => {
    if (id) {
      // Convert id to number if it's a string
      const toolId = typeof id === 'string' ? parseInt(id, 10) : id;
      dispatch(fetchToolById(toolId));
      dispatch(fetchToolCheckoutHistory(toolId));
      dispatch(fetchToolCalibrations({ toolId, page: 1, limit: 10 }));
    }
  }, [dispatch, id]);

  if (toolLoading || !currentTool) {
    return <LoadingSpinner />;
  }

  // Convert id to number for lookup if it's a string
  const toolId = typeof id === 'string' ? parseInt(id, 10) : id;
  const history = checkoutHistory[toolId] || [];
  const isAdmin = user?.is_admin || user?.department === 'Materials';

  return (
    <>
      <div>
        {showHelp && (
          <HelpContent title="Tool Details" initialOpen={false}>
            <p>This page displays detailed information about a specific tool, including its status, location, and history.</p>
            <ul>
              <li><strong>Tool Information:</strong> View basic details about the tool, including its ID, category, location, and status.</li>
              <li><strong>Calibration Information:</strong> For tools that require calibration, view the calibration status, frequency, and history.</li>
              <li><strong>Actions:</strong> Depending on the tool's status and your permissions, you can checkout the tool, remove it from service, or return it to service.</li>
              <li><strong>History Tabs:</strong> View the tool's checkout history, service history, and calibration history using the tabs.</li>
            </ul>
          </HelpContent>
        )}

        <div className="d-flex justify-content-between align-items-center mb-4">
          <div className="d-flex align-items-center">
            <h2>Tool Details</h2>
            {showHelp && (
              <HelpIcon
                title="Tool Details"
                content={
                  <>
                    <p>This page shows detailed information about a specific tool.</p>
                    <p>You can view the tool's properties, status, and history, as well as perform actions like checkout or maintenance.</p>
                  </>
                }
              />
            )}
          </div>
          <div>
            <Tooltip text="Return to tool inventory" placement="top" show={showTooltips}>
              <Button as={Link} to="/tools" variant="secondary" className="me-2">
                Back to Tools
              </Button>
            </Tooltip>
            {isAdmin && (
              <Tooltip text="Edit tool information" placement="top" show={showTooltips}>
                <Button as={Link} to={`/tools/${id}/edit`} variant="primary">
                  Edit Tool
                </Button>
              </Tooltip>
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
                  <Col sm={8}>{currentTool.purchase_date ? new Date(currentTool.purchase_date).toLocaleDateString() : 'N/A'}</Col>
                </Row>
                {currentTool.description && (
                  <Row className="mb-3">
                    <Col sm={4} className="fw-bold">Description:</Col>
                    <Col sm={8}>{currentTool.description}</Col>
                  </Row>
                )}

                {/* Calibration Information */}
                {currentTool.requires_calibration && (
                  <>
                    <hr />
                    <h5 className="mb-3">Calibration Information</h5>
                    <Row className="mb-3">
                      <Col sm={4} className="fw-bold">Requires Calibration:</Col>
                      <Col sm={8}>Yes</Col>
                    </Row>
                    <Row className="mb-3">
                      <Col sm={4} className="fw-bold">Calibration Frequency:</Col>
                      <Col sm={8}>{currentTool.calibration_frequency_days} days</Col>
                    </Row>
                    <Row className="mb-3">
                      <Col sm={4} className="fw-bold">Last Calibration:</Col>
                      <Col sm={8}>
                        {currentTool.last_calibration_date
                          ? new Date(currentTool.last_calibration_date).toLocaleDateString()
                          : 'Never'}
                      </Col>
                    </Row>
                    <Row className="mb-3">
                      <Col sm={4} className="fw-bold">Next Calibration:</Col>
                      <Col sm={8}>
                        {currentTool.next_calibration_date
                          ? new Date(currentTool.next_calibration_date).toLocaleDateString()
                          : 'Not scheduled'}
                      </Col>
                    </Row>
                    <Row className="mb-3">
                      <Col sm={4} className="fw-bold">Calibration Status:</Col>
                      <Col sm={8}>
                        <Badge bg={
                          currentTool.calibration_status === 'current' ? 'success' :
                          currentTool.calibration_status === 'due_soon' ? 'warning' :
                          currentTool.calibration_status === 'overdue' ? 'danger' : 'secondary'
                        }>
                          {currentTool.calibration_status === 'current' ? 'Current' :
                           currentTool.calibration_status === 'due_soon' ? 'Due Soon' :
                           currentTool.calibration_status === 'overdue' ? 'Overdue' : 'Not Applicable'}
                        </Badge>
                      </Col>
                    </Row>
                  </>
                )}
              </Card.Body>
              <Card.Footer>
                <div className="d-flex flex-wrap gap-2">
                  {currentTool.status === 'available' && (
                    <>
                      <Tooltip text="Check out this tool to yourself" placement="top" show={showTooltips}>
                        <Button as={Link} to={`/checkout/${currentTool.id}`} variant="success">
                          Checkout to Me
                        </Button>
                      </Tooltip>
                      <Tooltip text="Check out this tool to another user" placement="top" show={showTooltips}>
                        <Button
                          variant="primary"
                          onClick={() => setShowCheckoutModal(true)}
                        >
                          Checkout to User
                        </Button>
                      </Tooltip>
                      {isAdmin && (
                        <>
                          <Tooltip text="Mark this tool as under maintenance or retired" placement="top" show={showTooltips}>
                            <Button
                              variant="warning"
                              onClick={() => setShowRemoveFromServiceModal(true)}
                              className="me-2"
                            >
                              Remove from Service
                            </Button>
                          </Tooltip>
                          {currentTool.requires_calibration && (
                            <Tooltip text="Perform calibration on this tool" placement="top" show={showTooltips}>
                              <Button
                                as={Link}
                                to={`/tools/${currentTool.id}/calibrations/new`}
                                variant="info"
                              >
                                Calibrate Tool
                              </Button>
                            </Tooltip>
                          )}
                        </>
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
                        <Tooltip text="Return this tool to available status" placement="top" show={showTooltips}>
                          <Button
                            variant="success"
                            onClick={() => setShowReturnToServiceModal(true)}
                          >
                            Return to Service
                          </Button>
                        </Tooltip>
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
                <div className="d-flex justify-content-between align-items-center">
                  <Tabs
                    activeKey={activeTab}
                    onSelect={(k) => setActiveTab(k)}
                    className="card-header-tabs"
                  >
                    <Tab eventKey="details" title="Checkout History" />
                    <Tab eventKey="service" title="Service History" />
                    <Tab eventKey="calibration" title="Calibration History" />
                  </Tabs>
                  {showHelp && (
                    <HelpIcon
                      title="Tool History"
                      content={
                        <>
                          <p>This section shows the history of the tool:</p>
                          <ul>
                            <li><strong>Checkout History:</strong> Shows who has checked out this tool and when.</li>
                            <li><strong>Service History:</strong> Shows maintenance and service records for this tool.</li>
                            <li><strong>Calibration History:</strong> Shows calibration records for this tool.</li>
                          </ul>
                        </>
                      }
                      size="sm"
                    />
                  )}
                </div>
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
                ) : activeTab === 'service' ? (
                  <ServiceHistoryList toolId={id} />
                ) : (
                  <ToolCalibrationHistory toolId={id} />
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
