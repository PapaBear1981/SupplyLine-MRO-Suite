import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Table, Button, Card, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { fetchCheckouts } from '../../store/checkoutsSlice';
import LoadingSpinner from '../common/LoadingSpinner';
import ReturnToolModal from './ReturnToolModal';
import Tooltip from '../common/Tooltip';
import HelpIcon from '../common/HelpIcon';
import HelpContent from '../common/HelpContent';
import { useHelp } from '../../context/HelpContext';
import { formatDate } from '../../utils/dateUtils';

const AllCheckouts = () => {
  const dispatch = useDispatch();
  const { checkouts, loading } = useSelector((state) => state.checkouts);
  const { user } = useSelector((state) => state.auth);
  const { showTooltips, showHelp } = useHelp();
  const [showReturnModal, setShowReturnModal] = useState(false);
  const [selectedCheckoutId, setSelectedCheckoutId] = useState(null);
  const [selectedToolInfo, setSelectedToolInfo] = useState(null);
  const [sortConfig, setSortConfig] = useState({ key: 'tool_number', direction: 'ascending' });

  // Check if user has permission to return tools
  const canReturnTools = user?.is_admin || user?.department === 'Materials';

  useEffect(() => {
    console.log("AllCheckouts: Fetching all checkouts...");
    dispatch(fetchCheckouts())
      .then(result => {
        console.log("AllCheckouts: Fetch all checkouts result:", result);
      })
      .catch(error => {
        console.error("AllCheckouts: Error fetching all checkouts:", error);
      });
  }, [dispatch]);

  const handleReturnTool = (checkout) => {
    setSelectedCheckoutId(checkout.id);
    setSelectedToolInfo({
      tool_number: checkout.tool_number,
      serial_number: checkout.serial_number,
      description: checkout.description,
      user_name: checkout.user_name
    });
    setShowReturnModal(true);
  };

  const handleSort = (key) => {
    setSortConfig({
      key,
      direction:
        sortConfig.key === key && sortConfig.direction === 'ascending'
          ? 'descending'
          : 'ascending',
    });
  };

  const getSortIcon = (key) => {
    if (sortConfig.key !== key) return null;
    return sortConfig.direction === 'ascending' ? '↑' : '↓';
  };

  if (loading && !checkouts.length) {
    return <LoadingSpinner />;
  }

  // Filter active checkouts (not returned)
  const activeCheckouts = checkouts.filter(checkout => !checkout.return_date);

  // Sort active checkouts
  const sortedCheckouts = [...activeCheckouts].sort((a, b) => {
    let aValue, bValue;

    if (sortConfig.key === 'checkout_date' || sortConfig.key === 'expected_return_date') {
      // Date sorting
      aValue = a[sortConfig.key] ? new Date(a[sortConfig.key]) : new Date(0);
      bValue = b[sortConfig.key] ? new Date(b[sortConfig.key]) : new Date(0);

      if (sortConfig.direction === 'ascending') {
        return aValue - bValue;
      } else {
        return bValue - aValue;
      }
    } else {
      // String sorting
      aValue = (a[sortConfig.key] || '').toString().toLowerCase();
      bValue = (b[sortConfig.key] || '').toString().toLowerCase();

      if (sortConfig.direction === 'ascending') {
        return aValue.localeCompare(bValue);
      } else {
        return bValue.localeCompare(aValue);
      }
    }
  });

  return (
    <>
      <div className="w-100">
        {showHelp && (
          <HelpContent title="All Active Checkouts" initialOpen={false}>
            <p>This page displays all tools that are currently checked out across the organization.</p>
            <ul>
              <li><strong>Tool Information:</strong> View details about each checked out tool, including its number, serial number, and description.</li>
              <li><strong>User Information:</strong> See who has checked out each tool and when it was checked out.</li>
              <li><strong>Expected Return:</strong> The date when the tool is expected to be returned. Overdue tools are highlighted.</li>
              <li><strong>Return Tool:</strong> As an admin or Materials department member, you can return tools on behalf of users.</li>
            </ul>
          </HelpContent>
        )}

        {!canReturnTools && activeCheckouts.length > 0 && (
          <div className="alert alert-info mb-4">
            <i className="bi bi-info-circle me-2"></i>
            <strong>Note:</strong> Only Materials department and Admin personnel can return tools. Please contact them to return any tools.
          </div>
        )}
        <Card className="mb-4 shadow-sm">
          <Card.Header className="bg-light">
            <div className="d-flex justify-content-between align-items-center">
              <h4 className="mb-0">All Active Checkouts</h4>
              {showHelp && (
                <HelpIcon
                  title="All Active Checkouts"
                  content={
                    <>
                      <p>This table shows all tools currently checked out across the organization.</p>
                      <p>As an admin or Materials department member, you can return tools on behalf of users.</p>
                      <p>Overdue tools are marked with an "Overdue" badge.</p>
                      <p><strong>Sorting:</strong> Click on column headers to sort the table. Click again to reverse the sort order.</p>
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
                    <th onClick={() => handleSort('tool_number')} className="cursor-pointer">
                      Tool Number {getSortIcon('tool_number')}
                    </th>
                    <th onClick={() => handleSort('serial_number')} className="cursor-pointer">
                      Serial Number {getSortIcon('serial_number')}
                    </th>
                    <th onClick={() => handleSort('description')} className="cursor-pointer">
                      Description {getSortIcon('description')}
                    </th>
                    <th onClick={() => handleSort('user_name')} className="cursor-pointer">
                      Checked Out By {getSortIcon('user_name')}
                    </th>
                    <th onClick={() => handleSort('checkout_date')} className="cursor-pointer">
                      Checkout Date {getSortIcon('checkout_date')}
                    </th>
                    <th onClick={() => handleSort('expected_return_date')} className="cursor-pointer">
                      Expected Return {getSortIcon('expected_return_date')}
                    </th>
                    <th>Status</th>
                    {canReturnTools && <th style={{ width: '150px' }}>Actions</th>}
                  </tr>
                </thead>
                <tbody>
                  {sortedCheckouts.length > 0 ? (
                    sortedCheckouts.map((checkout) => (
                      <tr key={checkout.id}>
                        <td>
                          <Link to={`/tools/${checkout.tool_id}`} className="fw-bold">
                            {checkout.tool_number}
                          </Link>
                        </td>
                        <td>{checkout.serial_number || 'N/A'}</td>
                        <td>{checkout.description || 'N/A'}</td>
                        <td>{checkout.user_name || 'Unknown'}</td>
                        <td>{formatDate(checkout.checkout_date)}</td>
                        <td>
                          {formatDate(checkout.expected_return_date)}
                        </td>
                        <td>
                          {checkout.expected_return_date && new Date(checkout.expected_return_date) < new Date() ? (
                            <span className="status-badge status-maintenance">Overdue</span>
                          ) : (
                            <span className="status-badge status-checked-out">Checked Out</span>
                          )}
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
                      <td colSpan={canReturnTools ? "8" : "7"} className="text-center py-4">
                        There are no active checkouts.
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

export default AllCheckouts;
