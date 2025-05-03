import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Table, Button, Card, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { fetchUserCheckouts, returnTool } from '../../store/checkoutsSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const UserCheckouts = () => {
  const dispatch = useDispatch();
  const { userCheckouts, loading } = useSelector((state) => state.checkouts);

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

  const handleReturnTool = (checkoutId) => {
    if (window.confirm('Are you sure you want to return this tool?')) {
      dispatch(returnTool({
        checkoutId,
        condition: 'Good' // Default condition, could be made selectable
      }));
    }
  };

  if (loading && !userCheckouts.length) {
    return <LoadingSpinner />;
  }

  // Filter active checkouts (not returned)
  const activeCheckouts = userCheckouts.filter(checkout => !checkout.return_date);

  // Filter past checkouts (returned)
  const pastCheckouts = userCheckouts.filter(checkout => checkout.return_date);

  return (
    <div className="w-100">
      <Card className="mb-4 shadow-sm">
        <Card.Header className="bg-light">
          <h4 className="mb-0">Active Checkouts</h4>
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
                  <th style={{ width: '150px' }}>Actions</th>
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
                      <td>{new Date(checkout.checkout_date).toLocaleDateString()}</td>
                      <td>
                        {checkout.expected_return_date ? new Date(checkout.expected_return_date).toLocaleDateString() : 'N/A'}
                        {checkout.expected_return_date && new Date(checkout.expected_return_date) < new Date() && (
                          <Badge bg="danger" className="ms-2">Overdue</Badge>
                        )}
                      </td>
                      <td>
                        <Badge bg="warning">{checkout.status}</Badge>
                      </td>
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
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="7" className="text-center py-4">
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
          <h4 className="mb-0">Checkout History</h4>
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
                      <td>{new Date(checkout.checkout_date).toLocaleDateString()}</td>
                      <td>{new Date(checkout.return_date).toLocaleDateString()}</td>
                      <td>
                        <Badge bg="success">Returned</Badge>
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
  );
};

export default UserCheckouts;
