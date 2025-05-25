import { useState } from 'react';
import { Card, Badge, Button, Form, InputGroup } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import MobilePullToRefresh from './MobilePullToRefresh';
import MobileSwipeActions from './MobileSwipeActions';

const MobileToolList = ({ tools = [], loading = false, onRefresh, enablePullToRefresh = false }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  const filteredTools = (tools || []).filter(tool => {
    const matchesSearch = tool.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         tool.tool_number?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         tool.serial_number?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filterStatus === 'all' || tool.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const getStatusVariant = (status) => {
    switch (status) {
      case 'available': return 'success';
      case 'checked_out': return 'warning';
      case 'maintenance': return 'danger';
      case 'calibration': return 'info';
      default: return 'secondary';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'available': return 'check-circle';
      case 'checked_out': return 'person-check';
      case 'maintenance': return 'wrench';
      case 'calibration': return 'speedometer2';
      default: return 'question-circle';
    }
  };

  const handleSwipeAction = (tool, action) => {
    switch (action) {
      case 'checkout':
        // Navigate to checkout page
        window.location.href = `/checkout/${tool.id}`;
        break;
      case 'details':
        // Navigate to tool details
        window.location.href = `/tools/${tool.id}`;
        break;
      case 'edit':
        // Navigate to edit page
        window.location.href = `/tools/${tool.id}/edit`;
        break;
      default:
        break;
    }
  };

  return (
    <div className="mobile-tool-list">
      {/* Search and Filter */}
      <div className="mobile-search-filter mb-3">
        <Form.Group className="mb-2">
          <InputGroup>
            <InputGroup.Text>
              <i className="bi bi-search"></i>
            </InputGroup.Text>
            <Form.Control
              type="text"
              placeholder="Search tools..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </InputGroup>
        </Form.Group>

        <Form.Select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          size="sm"
        >
          <option value="all">All Status</option>
          <option value="available">Available</option>
          <option value="checked_out">Checked Out</option>
          <option value="maintenance">Maintenance</option>
          <option value="calibration">Calibration</option>
        </Form.Select>
      </div>

      {enablePullToRefresh ? (
        <MobilePullToRefresh onRefresh={onRefresh} refreshing={loading}>
          <div className="mobile-tool-cards">
      ) : (
        <div className="mobile-tool-cards">
      )}
          {loading && filteredTools.length === 0 && (
            <div className="mobile-loading">
              <div className="text-center">
                <div className="spinner-border text-primary" role="status">
                  <span className="visually-hidden">Loading...</span>
                </div>
                <p className="mt-2 text-muted">Loading tools...</p>
              </div>
            </div>
          )}

          {filteredTools.map(tool => (
            <MobileSwipeActions
              key={tool.id}
              actions={[
                {
                  icon: 'eye',
                  label: 'Details',
                  variant: 'info',
                  action: () => handleSwipeAction(tool, 'details')
                },
                ...(tool.status === 'available' ? [{
                  icon: 'clipboard-check',
                  label: 'Checkout',
                  variant: 'success',
                  action: () => handleSwipeAction(tool, 'checkout')
                }] : []),
                {
                  icon: 'pencil',
                  label: 'Edit',
                  variant: 'warning',
                  action: () => handleSwipeAction(tool, 'edit')
                }
              ]}
            >
              <Card className="mobile-tool-card mb-2">
                <Card.Body className="p-3">
                  <div className="d-flex justify-content-between align-items-start mb-2">
                    <div className="flex-grow-1">
                      <h6 className="mobile-tool-name mb-1">
                        <Link to={`/tools/${tool.id}`} className="text-decoration-none">
                          {tool.description}
                        </Link>
                      </h6>
                      <p className="mobile-tool-part text-muted mb-1">
                        {tool.tool_number} • {tool.serial_number}
                      </p>
                    </div>
                    <Badge
                      bg={getStatusVariant(tool.status)}
                      className="mobile-tool-status"
                    >
                      <i className={`bi bi-${getStatusIcon(tool.status)} me-1`}></i>
                      {tool.status?.replace('_', ' ')}
                    </Badge>
                  </div>

                  <div className="mobile-tool-details">
                    <div className="d-flex justify-content-between text-muted small">
                      <span>
                        <i className="bi bi-geo-alt me-1"></i>
                        {tool.location || 'No location'}
                      </span>
                      {tool.status === 'checked_out' && tool.checked_out_to && (
                        <span>
                          <i className="bi bi-person me-1"></i>
                          {tool.checked_out_to}
                        </span>
                      )}
                    </div>

                    {tool.due_date && (
                      <div className="mt-1">
                        <small className={`text-${new Date(tool.due_date) < new Date() ? 'danger' : 'warning'}`}>
                          <i className="bi bi-calendar me-1"></i>
                          Due: {new Date(tool.due_date).toLocaleDateString()}
                        </small>
                      </div>
                    )}
                  </div>

                  {/* Quick Actions */}
                  <div className="mobile-tool-actions mt-2">
                    <div className="d-flex gap-2">
                      <Button
                        as={Link}
                        to={`/tools/${tool.id}`}
                        variant="outline-primary"
                        size="sm"
                        className="flex-grow-1"
                      >
                        <i className="bi bi-eye me-1"></i>
                        View
                      </Button>

                      {tool.status === 'available' && (
                        <Button
                          as={Link}
                          to={`/checkout/${tool.id}`}
                          variant="success"
                          size="sm"
                          className="flex-grow-1"
                        >
                          <i className="bi bi-clipboard-check me-1"></i>
                          Checkout
                        </Button>
                      )}
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </MobileSwipeActions>
          ))}

          {filteredTools.length === 0 && !loading && (
            <div className="mobile-empty">
              <i className="bi bi-tools"></i>
              <h5>No tools found</h5>
              <p>Try adjusting your search or filter criteria</p>
            </div>
          )}
        </div>
      {enablePullToRefresh ? (
        </MobilePullToRefresh>
      ) : null}
    </div>
  );
};

export default MobileToolList;
