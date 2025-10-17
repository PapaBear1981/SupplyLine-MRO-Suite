import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Badge, ListGroup, Button, Alert, Spinner } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { fetchUserCheckouts } from '../../store/checkoutsSlice';
import { formatDate } from '../../utils/dateUtils';

const UserCheckoutStatus = () => {
  const dispatch = useDispatch();
  const { userCheckouts, loading, error } = useSelector((state) => state.checkouts);
  const { user } = useSelector((state) => state.auth);

  useEffect(() => {
    dispatch(fetchUserCheckouts());
  }, [dispatch]);

  // Filter active checkouts (not returned)
  const activeCheckouts = userCheckouts.filter(checkout => !checkout.return_date);

  // Function to determine badge variant based on due date
  const getStatusBadgeVariant = (dueDate) => {
    if (!dueDate) return 'secondary';

    const today = new Date();
    const due = new Date(dueDate);

    if (due < today) return 'danger'; // Overdue

    // Calculate days until due
    const diffTime = Math.abs(due - today);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays <= 2) return 'warning'; // Due soon
    return 'success'; // Not due soon
  };

  if (loading && !userCheckouts.length) {
    return (
      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light">
          <h4 className="mb-0">My Checked Out Tools</h4>
        </Card.Header>
        <Card.Body className="text-center p-4">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
        </Card.Body>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light">
          <h4 className="mb-0">My Checked Out Tools</h4>
        </Card.Header>
        <Card.Body>
          <Alert variant="danger">
            <Alert.Heading>Error</Alert.Heading>
            <p>{error.message || 'Failed to load checkout data'}</p>
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card className="shadow-sm mb-4" data-testid="user-checkout-status">
      <Card.Header className="bg-light d-flex justify-content-between align-items-center">
        <h4 className="mb-0">My Checked Out Tools</h4>
        <Badge bg={activeCheckouts.length > 0 ? "primary" : "success"} pill>
          {activeCheckouts.length}
        </Badge>
      </Card.Header>
      <Card.Body className="p-0">
        {activeCheckouts.length === 0 ? (
          <>
            <Alert variant="success" className="m-3">
              You don't have any tools checked out.
            </Alert>
            {user?.is_admin && (
              <Alert variant="info" className="mx-3 mb-3">
                <small>
                  <i className="bi bi-info-circle me-1"></i>
                  As an admin, you can see tools checked out to other users in the "Past Due Tools" section above.
                </small>
              </Alert>
            )}
          </>
        ) : (
          <ListGroup variant="flush">
            {activeCheckouts.map((checkout) => {
              const dueDate = checkout.expected_return_date;
              const badgeVariant = getStatusBadgeVariant(dueDate);

              return (
                <ListGroup.Item key={checkout.id} className="d-flex justify-content-between align-items-center">
                  <div>
                    <div className="fw-bold">{checkout.tool_number} - {checkout.description}</div>
                    <div className="text-muted small">
                      Checked out: {formatDate(checkout.checkout_date)} |
                      Due: {formatDate(checkout.expected_return_date)}
                    </div>
                  </div>
                  <div className="d-flex align-items-center">
                    <Badge
                      bg={badgeVariant}
                      className="me-2"
                    >
                      {badgeVariant === 'danger' ? 'Overdue' :
                       badgeVariant === 'warning' ? 'Due Soon' : 'Checked Out'}
                    </Badge>
                    <Button
                      as={Link}
                      to={`/tools/${checkout.tool_id}`}
                      variant="outline-primary"
                      size="sm"
                    >
                      View
                    </Button>
                  </div>
                </ListGroup.Item>
              );
            })}
          </ListGroup>
        )}
      </Card.Body>
      <Card.Footer>
        <Button as={Link} to="/my-checkouts" variant="primary" className="w-100">Manage My Checkouts</Button>
      </Card.Footer>
    </Card>
  );
};

export default UserCheckoutStatus;
