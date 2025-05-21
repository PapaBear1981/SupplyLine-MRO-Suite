import React from 'react';
import { Card, ProgressBar, ListGroup, Alert, Button } from 'react-bootstrap';
import { useDispatch } from 'react-redux';
import { fetchSystemResources } from '../../store/adminSlice';
import LoadingSpinner from '../common/LoadingSpinner';
import { FaSync } from 'react-icons/fa';

const SystemResources = ({ resources, loading }) => {
  const dispatch = useDispatch();

  const handleRefresh = () => {
    dispatch(fetchSystemResources());
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!resources) {
    return (
      <Alert variant="info">
        System resource information is not available. Please try again later.
        <Button
          variant="outline-primary"
          size="sm"
          className="ms-2"
          onClick={handleRefresh}
          disabled={loading}
        >
          <FaSync className={loading ? 'spin' : ''} /> Refresh
        </Button>
      </Alert>
    );
  }

  // Helper function to determine progress bar variant based on usage percentage
  const getVariant = (percentage) => {
    if (percentage < 60) return 'success';
    if (percentage < 80) return 'warning';
    return 'danger';
  };

  return (
    <Card className="mb-4">
      <Card.Header as="h5" className="d-flex justify-content-between align-items-center">
        System Resources
        <Button
          variant="outline-primary"
          size="sm"
          onClick={handleRefresh}
          disabled={loading}
        >
          <FaSync className={loading ? 'spin' : ''} /> Refresh
        </Button>
      </Card.Header>
      <Card.Body>
        <div className="mb-3">
          <div className="d-flex justify-content-between">
            <span>CPU Usage</span>
            <span>{resources.cpu?.usage}%</span>
          </div>
          <ProgressBar
            variant={getVariant(resources.cpu?.usage)}
            now={resources.cpu?.usage}
            className="mt-1"
          />
          <small className="text-muted">
            {resources.cpu?.cores} Cores Available
          </small>
        </div>

        <div className="mb-3">
          <div className="d-flex justify-content-between">
            <span>Memory Usage</span>
            <span>{resources.memory?.usage}%</span>
          </div>
          <ProgressBar
            variant={getVariant(resources.memory?.usage)}
            now={resources.memory?.usage}
            className="mt-1"
          />
          <small className="text-muted">
            Total: {resources.memory?.total_gb} GB
          </small>
        </div>

        <div className="mb-3">
          <div className="d-flex justify-content-between">
            <span>Disk Usage</span>
            <span>{resources.disk?.usage}%</span>
          </div>
          <ProgressBar
            variant={getVariant(resources.disk?.usage)}
            now={resources.disk?.usage}
            className="mt-1"
          />
          <small className="text-muted">
            Total: {resources.disk?.total_gb} GB
          </small>
        </div>

        <ListGroup variant="flush" className="mt-4">
          <ListGroup.Item className="d-flex justify-content-between">
            <span>Database Size</span>
            <span>{resources.database?.size_mb} MB</span>
          </ListGroup.Item>
          <ListGroup.Item className="d-flex justify-content-between">
            <span>Total Records</span>
            <span>{resources.database?.total_records}</span>
          </ListGroup.Item>
          <ListGroup.Item className="d-flex justify-content-between">
            <span>Server Status</span>
            <span className="text-success">{resources.server?.status}</span>
          </ListGroup.Item>
          <ListGroup.Item className="d-flex justify-content-between">
            <span>Uptime</span>
            <span>{resources.server?.uptime}</span>
          </ListGroup.Item>
          <ListGroup.Item className="d-flex justify-content-between">
            <span>Active Users</span>
            <span>{resources.server?.active_users}</span>
          </ListGroup.Item>
        </ListGroup>

        <div className="text-muted mt-3 small">
          Last updated: {new Date(resources.timestamp).toLocaleString()}
        </div>
      </Card.Body>
    </Card>
  );
};

export default SystemResources;
