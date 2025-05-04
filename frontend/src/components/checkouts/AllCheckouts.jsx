import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Table, Button, Card, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { fetchCheckouts, returnTool } from '../../store/checkoutsSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const AllCheckouts = () => {
  const dispatch = useDispatch();
  const { checkouts, loading } = useSelector((state) => state.checkouts);
  const { user } = useSelector((state) => state.auth);

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

  const handleReturnTool = (checkoutId) => {
    if (window.confirm('Are you sure you want to return this tool?')) {
      dispatch(returnTool({
        checkoutId,
        condition: 'Good' // Default condition, could be made selectable
      }));
    }
  };

  if (loading && !checkouts.length) {
    return <LoadingSpinner />;
  }

  // Filter active checkouts (not returned)
  const activeCheckouts = checkouts.filter(checkout => !checkout.return_date);

  return (
    <div className="w-100">
      <Card className="mb-4 shadow-sm">
        <Card.Header className="bg-light">
          <h4 className="mb-0">All Active Checkouts</h4>
        </Card.Header>
        <Card.Body className="p-0">
          <div className="table-responsive">
            <Table striped bordered hover className="mb-0">
              <thead className="bg-light">
                <tr>
                  <th>Tool Number</th>
                  <th>Serial Number</th>
                  <th>Description</th>
                  <th>Checked Out By</th>
                  <th>Checkout Date</th>
                  <th>Expected Return</th>
                  <th>Status</th>
                  {canReturnTools && <th style={{ width: '150px' }}>Actions</th>}
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
                      <td>{checkout.serial_number || 'N/A'}</td>
                      <td>{checkout.description || 'N/A'}</td>
                      <td>{checkout.user_name || 'Unknown'}</td>
                      <td>{new Date(checkout.checkout_date).toLocaleDateString()}</td>
                      <td>
                        {checkout.expected_return_date ? new Date(checkout.expected_return_date).toLocaleDateString() : 'N/A'}
                        {checkout.expected_return_date && new Date(checkout.expected_return_date) < new Date() && (
                          <span className="status-badge status-maintenance ms-2">Overdue</span>
                        )}
                      </td>
                      <td>
                        <span className="status-badge status-checked-out">Checked Out</span>
                      </td>
                      {canReturnTools && (
                        <td>
                          <Button
                            variant="success"
                            size="sm"
                            onClick={() => handleReturnTool(checkout.id)}
                            className="w-100"
                          >
                            Return Tool
                          </Button>
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
  );
};

export default AllCheckouts;
