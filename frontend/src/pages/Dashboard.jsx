import { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Row, Col, Card, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { fetchTools } from '../store/toolsSlice';
import { fetchUserCheckouts } from '../store/checkoutsSlice';
import LoadingSpinner from '../components/common/LoadingSpinner';

const Dashboard = () => {
  const dispatch = useDispatch();
  const { tools, loading: toolsLoading } = useSelector((state) => state.tools);
  const { userCheckouts, loading: checkoutsLoading } = useSelector((state) => state.checkouts);
  const { user } = useSelector((state) => state.auth);

  useEffect(() => {
    dispatch(fetchTools());
    dispatch(fetchUserCheckouts());
  }, [dispatch]);

  if (toolsLoading || checkoutsLoading) {
    return <LoadingSpinner />;
  }

  // Filter active checkouts (not returned)
  const activeCheckouts = userCheckouts.filter(checkout => !checkout.return_date);

  // Count tools by status
  const availableTools = tools.filter(tool => tool.status === 'Available').length;
  const checkedOutTools = tools.filter(tool => tool.status === 'Checked Out').length;
  const maintenanceTools = tools.filter(tool => tool.status === 'Maintenance').length;

  const isAdmin = user?.is_admin || user?.department === 'Materials';

  return (
    <div className="w-100">
      <h1 className="mb-4">Dashboard</h1>

      <Row className="mb-4 g-4">
        <Col lg={4} md={6} sm={12}>
          <Card className="text-center h-100 shadow-sm">
            <Card.Body>
              <h2 className="text-success display-4">{availableTools}</h2>
              <h5>Available Tools</h5>
            </Card.Body>
            <Card.Footer>
              <Button as={Link} to="/tools" variant="outline-success" className="w-100">View Tools</Button>
            </Card.Footer>
          </Card>
        </Col>
        <Col lg={4} md={6} sm={12}>
          <Card className="text-center h-100 shadow-sm">
            <Card.Body>
              <h2 className="text-warning display-4">{checkedOutTools}</h2>
              <h5>Checked Out Tools</h5>
            </Card.Body>
            <Card.Footer>
              <Button as={Link} to="/checkouts" variant="outline-warning" className="w-100">View Checkouts</Button>
            </Card.Footer>
          </Card>
        </Col>
        <Col lg={4} md={6} sm={12}>
          <Card className="text-center h-100 shadow-sm">
            <Card.Body>
              <h2 className="text-danger display-4">{maintenanceTools}</h2>
              <h5>Tools in Maintenance</h5>
            </Card.Body>
            <Card.Footer>
              <Button as={Link} to="/tools" variant="outline-danger" className="w-100">View Tools</Button>
            </Card.Footer>
          </Card>
        </Col>
      </Row>

      <Row className="mb-4 g-4">
        <Col lg={6} md={12}>
          <Card className="shadow-sm h-100">
            <Card.Header className="bg-light">
              <h4 className="mb-0">My Active Checkouts</h4>
            </Card.Header>
            <Card.Body>
              {activeCheckouts.length > 0 ? (
                <ul className="list-group">
                  {activeCheckouts.slice(0, 5).map(checkout => (
                    <li key={checkout.id} className="list-group-item d-flex justify-content-between align-items-center">
                      <div>
                        <strong>{checkout.tool_name}</strong>
                        <div className="text-muted small">
                          Due: {new Date(checkout.expected_return_date).toLocaleDateString()}
                        </div>
                      </div>
                      <Button
                        as={Link}
                        to="/my-checkouts"
                        variant="outline-primary"
                        size="sm"
                      >
                        Manage
                      </Button>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-center py-3">You have no active checkouts.</p>
              )}
            </Card.Body>
            <Card.Footer>
              <Button as={Link} to="/my-checkouts" variant="primary" className="w-100">View All My Checkouts</Button>
            </Card.Footer>
          </Card>
        </Col>

        <Col lg={6} md={12}>
          <Card className="shadow-sm h-100">
            <Card.Header className="bg-light">
              <h4 className="mb-0">Quick Actions</h4>
            </Card.Header>
            <Card.Body>
              <div className="d-grid gap-3">
                <Button as={Link} to="/tools" variant="outline-primary" size="lg">Browse Tools</Button>
                {isAdmin && (
                  <Button as={Link} to="/tools/new" variant="outline-success" size="lg">Add New Tool</Button>
                )}
                <Button as={Link} to="/tools/search" variant="outline-info" size="lg">Search Tools</Button>
                {isAdmin && (
                  <Button as={Link} to="/admin" variant="outline-dark" size="lg">Admin Dashboard</Button>
                )}
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
