import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { Card, ListGroup, Badge, Spinner, Alert, Button } from 'react-bootstrap';
import { fetchActivityFeed } from '../../store/chemicalsSlice';
import { formatDistanceToNow } from 'date-fns';

const ActivityFeed = ({ limit = 20, showHeader = true }) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { activityFeed, activityFeedLoading, activityFeedError } = useSelector((state) => state.chemicals);
  const [autoRefresh, setAutoRefresh] = useState(false);

  useEffect(() => {
    dispatch(fetchActivityFeed(limit));
  }, [dispatch, limit]);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      dispatch(fetchActivityFeed(limit));
    }, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, [autoRefresh, dispatch, limit]);

  const getActivityIcon = (type, auditType) => {
    switch (type) {
      case 'issuance':
        return { icon: 'bi-arrow-up-circle', color: 'primary' };
      case 'return':
        return { icon: 'bi-arrow-down-circle', color: 'success' };
      case 'audit':
        switch (auditType) {
          case 'chemical_added':
            return { icon: 'bi-plus-circle', color: 'info' };
          case 'chemical_ordered':
            return { icon: 'bi-cart-check', color: 'primary' };
          case 'chemical_delivered':
            return { icon: 'bi-box-seam', color: 'success' };
          case 'chemical_archived':
            return { icon: 'bi-archive', color: 'secondary' };
          case 'chemical_reorder_requested':
            return { icon: 'bi-cart-plus', color: 'warning' };
          default:
            return { icon: 'bi-info-circle', color: 'secondary' };
        }
      default:
        return { icon: 'bi-circle', color: 'secondary' };
    }
  };

  const handleActivityClick = (activity) => {
    if (activity.chemical_id) {
      navigate(`/chemicals/${activity.chemical_id}`);
    }
  };

  if (activityFeedLoading && !activityFeed.length) {
    return (
      <div className="text-center py-4">
        <Spinner animation="border" size="sm" role="status">
          <span className="visually-hidden">Loading activity feed...</span>
        </Spinner>
      </div>
    );
  }

  if (activityFeedError) {
    return (
      <Alert variant="danger">
        <p className="mb-0">{activityFeedError.message || 'Failed to load activity feed'}</p>
      </Alert>
    );
  }

  return (
    <Card className="activity-feed">
      {showHeader && (
        <Card.Header className="bg-light d-flex justify-content-between align-items-center">
          <strong>Recent Activity</strong>
          <div>
            <Button
              size="sm"
              variant={autoRefresh ? 'success' : 'outline-secondary'}
              onClick={() => setAutoRefresh(!autoRefresh)}
              title={autoRefresh ? 'Auto-refresh enabled' : 'Enable auto-refresh'}
            >
              <i className={`bi bi-${autoRefresh ? 'pause' : 'play'}-circle`}></i>
            </Button>
            <Button
              size="sm"
              variant="outline-primary"
              className="ms-2"
              onClick={() => dispatch(fetchActivityFeed(limit))}
              disabled={activityFeedLoading}
            >
              <i className="bi bi-arrow-clockwise"></i>
            </Button>
          </div>
        </Card.Header>
      )}
      <Card.Body className="p-0" style={{ maxHeight: '500px', overflowY: 'auto' }}>
        {activityFeed.length === 0 ? (
          <div className="text-center text-muted py-5">
            <i className="bi bi-inbox fs-1 d-block mb-2"></i>
            <p>No recent activity</p>
          </div>
        ) : (
          <ListGroup variant="flush">
            {activityFeed.map((activity, index) => {
              const { icon, color } = getActivityIcon(activity.type, activity.audit_type);
              return (
                <ListGroup.Item
                  key={index}
                  action={!!activity.chemical_id}
                  onClick={() => handleActivityClick(activity)}
                  className="py-3"
                >
                  <div className="d-flex align-items-start">
                    <div className="flex-shrink-0 me-3">
                      <i className={`${icon} fs-4 text-${color}`}></i>
                    </div>
                    <div className="flex-grow-1">
                      <div className="mb-1">
                        <small className="text-muted">
                          {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
                        </small>
                        {activity.user_name && (
                          <span className="ms-2">
                            <Badge bg="secondary" className="fw-normal">
                              {activity.user_name}
                            </Badge>
                          </span>
                        )}
                      </div>
                      <div className="mb-1">{activity.description}</div>
                      {(activity.part_number || activity.lot_number) && (
                        <div className="small text-muted">
                          {activity.part_number && (
                            <span className="me-2">
                              <strong>P/N:</strong> {activity.part_number}
                            </span>
                          )}
                          {activity.lot_number && (
                            <span>
                              <strong>LOT:</strong> {activity.lot_number}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </ListGroup.Item>
              );
            })}
          </ListGroup>
        )}
      </Card.Body>
    </Card>
  );
};

export default ActivityFeed;
