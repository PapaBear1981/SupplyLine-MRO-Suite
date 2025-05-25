import { useState, useEffect } from 'react';
import { Card, Badge, ListGroup, Button, Alert, Spinner } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import { useSelector } from 'react-redux';
import { formatDate, getDaysFromToday } from '../../utils/dateUtils';
import Tooltip from '../common/Tooltip';
import { useHelp } from '../../context/HelpContext';

const OverdueChemicals = () => {
  const [overdueChemicals, setOverdueChemicals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { showTooltips } = useHelp();
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.is_admin || user?.department === 'Materials';

  useEffect(() => {
    const fetchOverdueChemicals = async () => {
      try {
        console.log('OverdueChemicals: Fetching overdue chemicals...');
        setLoading(true);
        setError(null);
        const response = await api.get('/chemicals/on-order');
        console.log('OverdueChemicals: Received data:', response.data);

        // Filter to only include chemicals with expected delivery dates in the past
        const overdue = response.data.filter(chemical => {
          if (!chemical.expected_delivery_date) return false;
          const today = new Date();
          today.setHours(0, 0, 0, 0);
          const deliveryDate = new Date(chemical.expected_delivery_date);
          deliveryDate.setHours(0, 0, 0, 0);
          const isOverdue = deliveryDate < today;
          console.log(`OverdueChemicals: Chemical ${chemical.part_number} - ${chemical.lot_number}, expected: ${chemical.expected_delivery_date}, isOverdue: ${isOverdue}`);
          return isOverdue;
        });

        // Sort by most overdue first
        overdue.sort((a, b) => {
          const daysA = getDaysFromToday(a.expected_delivery_date);
          const daysB = getDaysFromToday(b.expected_delivery_date);
          return daysA - daysB; // Smaller (more negative) values first
        });

        setOverdueChemicals(overdue);
      } catch (err) {
        console.error('Error fetching overdue chemicals:', err);
        setError('Failed to load overdue chemicals data');
      } finally {
        setLoading(false);
      }
    };

    fetchOverdueChemicals();
  }, []);

  // Only show to admins and Materials department
  console.log('OverdueChemicals: User status - isAdmin:', isAdmin, 'user:', user);
  if (!isAdmin) {
    console.log('OverdueChemicals: Not showing component due to user permissions');
    return null;
  }

  // Function to determine badge color based on days overdue
  const getOverdueBadgeVariant = (daysOverdue) => {
    if (daysOverdue > 14) return 'danger';
    if (daysOverdue > 7) return 'warning';
    return 'info';
  };

  if (loading) {
    return (
      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light">
          <h4 className="mb-0">Overdue Chemical Deliveries</h4>
        </Card.Header>
        <Card.Body className="text-center py-4">
          <Spinner animation="border" role="status" />
          <span className="ms-2">Loading overdue chemicals...</span>
        </Card.Body>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light">
          <h4 className="mb-0">Overdue Chemical Deliveries</h4>
        </Card.Header>
        <Card.Body>
          <Alert variant="danger">
            <Alert.Heading>Error</Alert.Heading>
            <p>{error}</p>
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  if (overdueChemicals.length === 0) {
    return (
      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light">
          <h4 className="mb-0">Overdue Chemical Deliveries</h4>
        </Card.Header>
        <Card.Body>
          <Alert variant="success">
            No overdue chemical deliveries at this time.
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card className="shadow-sm mb-4">
      <Card.Header className="bg-light d-flex justify-content-between align-items-center">
        <h4 className="mb-0">Overdue Chemical Deliveries</h4>
        <Badge bg="danger" pill>{overdueChemicals.length}</Badge>
      </Card.Header>
      <Card.Body className="p-0">
        <ListGroup variant="flush">
          {overdueChemicals.slice(0, 5).map((chemical) => {
            const daysOverdue = Math.abs(getDaysFromToday(chemical.expected_delivery_date));

            return (
              <ListGroup.Item key={chemical.id} className="d-flex justify-content-between align-items-center">
                <div>
                  <div className="fw-bold">{chemical.part_number} - {chemical.lot_number}</div>
                  <div className="text-muted small">
                    {chemical.description} | Expected: {formatDate(chemical.expected_delivery_date)}
                  </div>
                </div>
                <div className="d-flex align-items-center">
                  <Tooltip text={`This chemical delivery is ${daysOverdue} days overdue`} placement="left" show={showTooltips}>
                    <Badge
                      bg={getOverdueBadgeVariant(daysOverdue)}
                      className="me-2"
                    >
                      {daysOverdue} days overdue
                    </Badge>
                  </Tooltip>
                  <Tooltip text="View detailed information about this chemical" placement="left" show={showTooltips}>
                    <Button
                      as={Link}
                      to={`/chemicals/${chemical.id}`}
                      variant="outline-primary"
                      size="sm"
                    >
                      View
                    </Button>
                  </Tooltip>
                </div>
              </ListGroup.Item>
            );
          })}

          {overdueChemicals.length > 5 && (
            <ListGroup.Item className="text-center text-muted">
              {overdueChemicals.length - 5} more overdue chemicals...
            </ListGroup.Item>
          )}
        </ListGroup>
      </Card.Body>
      <Card.Footer>
        <Button as={Link} to="/chemicals/reorder" variant="danger" className="w-100">Manage Overdue Chemicals</Button>
      </Card.Footer>
    </Card>
  );
};

export default OverdueChemicals;
