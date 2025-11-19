import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { Card, Row, Col, Badge, Spinner, Alert } from 'react-bootstrap';
import { fetchWorkflowStats, fetchChemicals } from '../../store/chemicalsSlice';

const ChemicalWorkflowDashboard = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { workflowStats, workflowStatsLoading, workflowStatsError } = useSelector((state) => state.chemicals);
  const [selectedView, setSelectedView] = useState(null);

  useEffect(() => {
    dispatch(fetchWorkflowStats());
  }, [dispatch]);

  if (workflowStatsLoading) {
    return (
      <div className="text-center py-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading workflow stats...</span>
        </Spinner>
      </div>
    );
  }

  if (workflowStatsError) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Error Loading Workflow Stats</Alert.Heading>
        <p>{workflowStatsError.message || 'Failed to load workflow statistics'}</p>
      </Alert>
    );
  }

  if (!workflowStats) {
    return null;
  }

  const { status_counts, reorder_counts, expiring_soon_count, category_counts, recent_activity } = workflowStats;

  const workflowCards = [
    {
      title: 'Available',
      count: status_counts?.available || 0,
      variant: 'success',
      icon: 'bi-check-circle',
      description: 'Adequate stock levels',
      filter: { status: 'available' }
    },
    {
      title: 'Low Stock',
      count: status_counts?.low_stock || 0,
      variant: 'warning',
      icon: 'bi-exclamation-triangle',
      description: 'Below minimum levels',
      filter: { status: 'low_stock' }
    },
    {
      title: 'Out of Stock',
      count: status_counts?.out_of_stock || 0,
      variant: 'danger',
      icon: 'bi-x-circle',
      description: 'No inventory available',
      filter: { status: 'out_of_stock' }
    },
    {
      title: 'Reorder Needed',
      count: reorder_counts?.needed || 0,
      variant: 'info',
      icon: 'bi-cart-plus',
      description: 'Pending reorder requests',
      filter: { reorder_status: 'needed' }
    },
    {
      title: 'On Order',
      count: reorder_counts?.ordered || 0,
      variant: 'primary',
      icon: 'bi-truck',
      description: 'Awaiting delivery',
      filter: { reorder_status: 'ordered' }
    },
    {
      title: 'Expiring Soon',
      count: expiring_soon_count || 0,
      variant: 'dark',
      icon: 'bi-clock-history',
      description: 'Within 30 days',
      action: () => navigate('/chemicals/expiring-soon')
    }
  ];

  return (
    <div className="chemical-workflow-dashboard">
      <h3 className="mb-4">Chemical Inventory Workflow</h3>

      {/* Workflow Status Cards */}
      <Row className="g-3 mb-4">
        {workflowCards.map((card, index) => (
          <Col key={index} xs={12} sm={6} md={4} lg={2}>
            <Card
              className={`h-100 border-${card.variant} cursor-pointer hover-shadow`}
              onClick={card.action || (() => console.log('Filter by:', card.filter))}
              style={{ cursor: 'pointer' }}
            >
              <Card.Body className="text-center p-3">
                <i className={`${card.icon} fs-2 text-${card.variant} mb-2`}></i>
                <h2 className={`mb-0 text-${card.variant}`}>{card.count}</h2>
                <Card.Title className="fs-6 mb-1">{card.title}</Card.Title>
                <Card.Text className="text-muted small mb-0">
                  {card.description}
                </Card.Text>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Recent Activity Summary */}
      {recent_activity && (
        <Card className="mb-4">
          <Card.Header className="bg-light">
            <strong>Recent Activity (Last 7 Days)</strong>
          </Card.Header>
          <Card.Body>
            <Row className="text-center">
              <Col xs={4}>
                <div className="mb-2">
                  <Badge bg="primary" className="fs-5 px-3 py-2">
                    {recent_activity.issuances_last_7_days || 0}
                  </Badge>
                </div>
                <small className="text-muted">Issuances</small>
              </Col>
              <Col xs={4}>
                <div className="mb-2">
                  <Badge bg="success" className="fs-5 px-3 py-2">
                    {recent_activity.returns_last_7_days || 0}
                  </Badge>
                </div>
                <small className="text-muted">Returns</small>
              </Col>
              <Col xs={4}>
                <div className="mb-2">
                  <Badge bg="info" className="fs-5 px-3 py-2">
                    {recent_activity.total_transactions_last_7_days || 0}
                  </Badge>
                </div>
                <small className="text-muted">Total Transactions</small>
              </Col>
            </Row>
          </Card.Body>
        </Card>
      )}

      {/* Category Breakdown */}
      {category_counts && Object.keys(category_counts).length > 0 && (
        <Card>
          <Card.Header className="bg-light">
            <strong>Inventory by Category</strong>
          </Card.Header>
          <Card.Body>
            <Row>
              {Object.entries(category_counts).map(([category, count], index) => (
                <Col key={index} xs={6} md={4} lg={3} className="mb-3">
                  <div className="d-flex align-items-center">
                    <Badge bg="secondary" className="me-2">
                      {count}
                    </Badge>
                    <span className="text-truncate">{category || 'Uncategorized'}</span>
                  </div>
                </Col>
              ))}
            </Row>
          </Card.Body>
        </Card>
      )}
    </div>
  );
};

export default ChemicalWorkflowDashboard;
