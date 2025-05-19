import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Table, Button, Card, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { fetchUserCheckouts } from '../../store/checkoutsSlice';
import LoadingSpinner from '../common/LoadingSpinner';
import ReturnToolModal from './ReturnToolModal';
import Tooltip from '../common/Tooltip';
import HelpIcon from '../common/HelpIcon';
import HelpContent from '../common/HelpContent';
import { useHelp } from '../../context/HelpContext';
import { formatDate } from '../../utils/dateUtils';

const UserCheckouts = () => {
  const dispatch = useDispatch();
  const { userCheckouts, loading } = useSelector((state) => state.checkouts);
  const { user } = useSelector((state) => state.auth);
  const { showTooltips, showHelp } = useHelp();
  const [showReturnModal, setShowReturnModal] = useState(false);
  const [selectedCheckoutId, setSelectedCheckoutId] = useState(null);
  const [selectedToolInfo, setSelectedToolInfo] = useState(null);

  // Check if user has permission to return tools
  const canReturnTools = user?.is_admin || user?.department === 'Materials';

  useEffect(() => {
    console.log("UserCheckouts: Fetching user checkouts...");
    dispatch(fetchUserCheckouts())
      .then(result => {
        console.log("UserCheckouts: Fetch user checkouts result:", result);
      })
      .catch(error => {
        console.error("UserCheckouts: Error fetching user checkouts:", error);
      });
  }, [dispatch]);

  const handleReturnTool = (checkout) => {
    setSelectedCheckoutId(checkout.id);
    setSelectedToolInfo({
      tool_number: checkout.tool_number,
      serial_number: checkout.serial_number,
      description: checkout.description,
      user_name: user?.name || 'Current User'
    });
    setShowReturnModal(true);
  };

  if (loading && !userCheckouts.length) {
    return <LoadingSpinner />;
  }

  // Filter active checkouts (not returned)
  const activeCheckouts = userCheckouts.filter(checkout => !checkout.return_date);

  // Filter past checkouts (returned)
  const pastCheckouts = userCheckouts.filter(checkout => checkout.return_date);

  return (
    <>
      <div className="w-100">
        {showHelp && (
          <HelpContent title="My Checkouts" initialOpen={false}>
            <p>This page displays all tools that you currently have checked out, as well as your checkout history.</p>
            <ul>
              <li><strong>Active Checkouts:</strong> Tools that you currently have checked out. These tools are assigned to you until they are returned.</li>
              <li><strong>Checkout History:</strong> Tools that you have previously checked out and returned.</li>
              <li><strong>Return Tool:</strong> {canReturnTools ?
                "You can return a tool by clicking the 'Return Tool' button next to the checkout." :
                "Only Materials department and Admin personnel can return tools. Please contact them to return your tools."}
              </li>
              <li><strong>Overdue:</strong> Tools that have passed their expected return date will be marked as overdue.</li>
            </ul>
          </HelpContent>
        )}

        {!canReturnTools && activeCheckouts.length > 0 && (
          <div className="alert alert-info mb-4">
            <i className="bi bi-info-circle me-2"></i>
            <strong>Note:</strong> Only Materials department and Admin personnel can return tools. Please contact them to return your tools.
          </div>
        )}
        <Card className="mb-4 shadow-sm">
          <Card.Header className="bg-light">
            <div className="d-flex justify-content-between align-items-center">
              <h4 className="mb-0">Active Checkouts</h4>
              {showHelp && (
                <HelpIcon
                  title="Active Checkouts"
                  content={
                    <>
                      <p>This section shows tools that you currently have checked out.</p>
                      <p>Tools remain in this list until they are returned to inventory.</p>
                      {canReturnTools && <p>You can return a tool by clicking the "Return Tool" button.</p>}
                    </>
                  }
                  size="sm"
                />
              )}
            </div>
          </Card.Header>
          <Card.Body className="p-0">
            <div className="table-responsive">
              <Table striped bordered hover className="mb-0">
                <thead className="bg-light">
                  <tr>
                    <th>Tool Number</th>
                    <th>Serial Number</th>
                    <th>Description</th>
                    <th>Checkout Date</th>
                    <th>Expected Return</th>
                    <th>Status</th>
                    {canReturnTools && (
                      <th style={{ width: '150px' }}>Actions</th>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {activeCheckouts.length > 0 ? (
                    activeCheckouts.map((checkout) => (
                      <tr key={checkout.id}>
                        <td>
                          <Link to={`/tools/${checkout.tool_id}`} className="fw-bold">
                            {checkout.tool_number}
                          </Link>
                        </td>
                        <td>{checkout.serial_number}</td>
                        <td>{checkout.description}</td>
                        <td>{formatDate(checkout.checkout_date)}</td>
                        <td>
                          {formatDate(checkout.expected_return_date)}
                          {checkout.expected_return_date && new Date(checkout.expected_return_date) < new Date() && (
                            <span className="status-badge status-maintenance ms-2">Overdue</span>
                          )}
                        </td>
                        <td>
                          <span className="status-badge status-checked-out">{checkout.status}</span>
                        </td>
                        {canReturnTools && (
                          <td>
                            <Tooltip text="Return this tool to inventory" placement="left" show={showTooltips}>
                              <Button
                                variant="success"
                                size="sm"
                                onClick={() => handleReturnTool(checkout)}
                                className="w-100"
                              >
                                Return Tool
                              </Button>
                            </Tooltip>
                          </td>
                        )}
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={canReturnTools ? "7" : "6"} className="text-center py-4">
                        You have no active checkouts.
                      </td>
                    </tr>
                  )}
                </tbody>
              </Table>
            </div>
          </Card.Body>
        </Card>

        <Card className="shadow-sm">
          <Card.Header className="bg-light">
            <div className="d-flex justify-content-between align-items-center">
              <h4 className="mb-0">Checkout History</h4>
              {showHelp && (
                <HelpIcon
                  title="Checkout History"
                  content={
                    <>
                      <p>This section shows tools that you have previously checked out and returned.</p>
                      <p>This history helps you track which tools you've used in the past.</p>
                    </>
                  }
                  size="sm"
                />
              )}
            </div>
          </Card.Header>
          <Card.Body className="p-0">
            <div className="table-responsive">
              <Table striped bordered hover className="mb-0">
                <thead className="bg-light">
                  <tr>
                    <th>Tool Number</th>
                    <th>Serial Number</th>
                    <th>Description</th>
                    <th>Checkout Date</th>
                    <th>Return Date</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {pastCheckouts.length > 0 ? (
                    pastCheckouts.map((checkout) => (
                      <tr key={checkout.id}>
                        <td>
                          <Link to={`/tools/${checkout.tool_id}`} className="fw-bold">
                            {checkout.tool_number}
                          </Link>
                        </td>
                        <td>{checkout.serial_number}</td>
                        <td>{checkout.description}</td>
                        <td>{formatDate(checkout.checkout_date)}</td>
                        <td>{formatDate(checkout.return_date)}</td>
                        <td>
                          <span className="status-badge status-available">Returned</span>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="6" className="text-center py-4">
                        You have no checkout history.
                      </td>
                    </tr>
                  )}
                </tbody>
              </Table>
            </div>
          </Card.Body>
        </Card>
      </div>

      {/* Return Tool Modal */}
      <ReturnToolModal
        show={showReturnModal}
        onHide={() => setShowReturnModal(false)}
        checkoutId={selectedCheckoutId}
        toolInfo={selectedToolInfo}
      />
    </>
  );
};

export default UserCheckouts;
