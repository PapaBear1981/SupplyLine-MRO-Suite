import { Card, ListGroup, Button, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';

const ActiveCheckouts = ({ checkouts }) => {
  // Filter active checkouts (not returned)
  const activeCheckouts = checkouts.filter(checkout => !checkout.return_date);

  // Format date for display
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  // Calculate if a checkout is overdue
  const isOverdue = (expectedReturnDate) => {
    if (!expectedReturnDate) return false;
    const today = new Date();
    const returnDate = new Date(expectedReturnDate);
    return today > returnDate;
  };

  return (
    <Card className="shadow-sm h-100">
      <Card.Header className="bg-light">
        <h4 className="mb-0">My Active Checkouts</h4>
      </Card.Header>
      <Card.Body className="p-0">
        {activeCheckouts.length > 0 ? (
          <ListGroup variant="flush">
            {activeCheckouts.slice(0, 5).map(checkout => (
              <ListGroup.Item key={checkout.id} className="d-flex justify-content-between align-items-center">
                <div>
                  <div className="d-flex align-items-center">
                    <strong>{checkout.tool_number || checkout.tool_name}</strong>
                    {isOverdue(checkout.expected_return_date) && (
                      <Badge bg="danger" className="ms-2">Overdue</Badge>
                    )}
                  </div>
                  <div className="text-muted small">
                    {checkout.serial_number && <span>SN: {checkout.serial_number} | </span>}
                    Due: {formatDate(checkout.expected_return_date)}
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
              </ListGroup.Item>
            ))}
          </ListGroup>
        ) : (
          <p className="text-center py-3">You have no active checkouts.</p>
        )}
      </Card.Body>
      <Card.Footer>
        <Button as={Link} to="/my-checkouts" variant="primary" className="w-100">View All My Checkouts</Button>
      </Card.Footer>
    </Card>
  );
};

export default ActiveCheckouts;
