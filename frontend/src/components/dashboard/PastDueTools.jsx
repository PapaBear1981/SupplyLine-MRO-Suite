import { useState, useEffect, useRef } from 'react';
import { Card, ListGroup, Badge, Button, Alert } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useSelector } from 'react-redux';
import api from '../../services/api';
import { formatDate } from '../../utils/dateUtils';
import Tooltip from '../common/Tooltip';
import { useHelp } from '../../context/HelpContext';

const PastDueTools = () => {
  const [pastDueTools, setPastDueTools] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { showTooltips } = useHelp();
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.is_admin || user?.department === 'Materials';
  const dataFetchedRef = useRef(false);

  useEffect(() => {
    // Only fetch overdue tools if user is admin or in Materials department
    // and if we haven't already fetched the data
    if (isAdmin && !dataFetchedRef.current) {
      fetchOverdueTools();
      dataFetchedRef.current = true;
    }
  }, [isAdmin]);

  const fetchOverdueTools = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/checkouts/overdue');
      setPastDueTools(response.data);
    } catch (err) {
      console.error('Error fetching overdue tools:', err);
      setError('Failed to load overdue tools data');
    } finally {
      setLoading(false);
    }
  };

  // Only show to admins and Materials department
  if (!isAdmin) {
    return null;
  }

  // Function to determine badge color based on days overdue
  const getOverdueBadgeVariant = (daysOverdue) => {
    if (daysOverdue > 14) return 'danger';
    if (daysOverdue > 7) return 'warning';
    return 'info';
  };

  // Function to format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light">
          <h4 className="mb-0">Past Due Tools</h4>
        </Card.Header>
        <Card.Body className="text-center p-4">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </Card.Body>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light">
          <h4 className="mb-0">Past Due Tools</h4>
        </Card.Header>
        <Card.Body>
          <Alert variant="warning">
            {error}
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  if (pastDueTools.length === 0) {
    return (
      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light">
          <h4 className="mb-0">Past Due Tools</h4>
        </Card.Header>
        <Card.Body>
          <Alert variant="success">
            No overdue tools at this time.
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card className="shadow-sm mb-4">
      <Card.Header className="bg-light d-flex justify-content-between align-items-center">
        <h4 className="mb-0">Past Due Tools</h4>
        <Tooltip text={`${pastDueTools.length} tools are currently overdue for return`} placement="left" show={showTooltips}>
          <Badge bg="danger" pill>{pastDueTools.length}</Badge>
        </Tooltip>
      </Card.Header>
      <Card.Body className="p-0">
        <Alert variant="info" className="m-2 mb-0">
          This section shows tools checked out to <strong>all users</strong> that are past their due date.
          To see only your checkouts, check the "My Checked Out Tools" section below.
        </Alert>
        <ListGroup variant="flush">
          {pastDueTools.map((tool) => (
            <ListGroup.Item key={tool.id} className="d-flex justify-content-between align-items-center">
              <div>
                <div className="fw-bold">{tool.tool_number} - {tool.description}</div>
                <div className="text-muted small">
                  Checked out by: {tool.user_name} | Due: {formatDate(tool.expected_return_date)}
                </div>
              </div>
              <div className="d-flex align-items-center">
                <Tooltip text={`This tool is ${tool.days_overdue} days past its return date`} placement="left" show={showTooltips}>
                  <Badge
                    bg={getOverdueBadgeVariant(tool.days_overdue)}
                    className="me-2"
                  >
                    {tool.days_overdue} days overdue
                  </Badge>
                </Tooltip>
                <Tooltip text="View all checkouts to manage overdue tools" placement="left" show={showTooltips}>
                  <Button
                    as={Link}
                    to={`/checkouts/all`}
                    variant="outline-primary"
                    size="sm"
                  >
                    View
                  </Button>
                </Tooltip>
              </div>
            </ListGroup.Item>
          ))}
        </ListGroup>
      </Card.Body>
      <Card.Footer>
        <Button as={Link} to="/checkouts/all" variant="danger" className="w-100">Manage Overdue Tools</Button>
      </Card.Footer>
    </Card>
  );
};

export default PastDueTools;
