import { Card, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';

const QuickActions = ({ isAdmin }) => {
  return (
    <Card className="shadow-sm h-100">
      <Card.Header className="bg-light">
        <h4 className="mb-0">Quick Actions</h4>
      </Card.Header>
      <Card.Body>
        <div className="d-grid gap-3">
          <Button as={Link} to="/tools" variant="outline-primary" size="lg">Browse Tools</Button>
          <Button as={Link} to="/checkouts" variant="outline-info" size="lg">View Checkouts</Button>
          {isAdmin && (
            <Button as={Link} to="/tools/new" variant="outline-success" size="lg">Add New Tool</Button>
          )}
          {isAdmin && (
            <Button as={Link} to="/checkouts/all" variant="outline-warning" size="lg">All Active Checkouts</Button>
          )}
          {isAdmin && (
            <Button as={Link} to="/admin" variant="outline-dark" size="lg">Admin Dashboard</Button>
          )}
        </div>
      </Card.Body>
    </Card>
  );
};

export default QuickActions;
