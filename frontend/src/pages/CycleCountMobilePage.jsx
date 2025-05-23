import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Container, Card, Button, Alert, Badge, ListGroup, Modal, Form } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { fetchCycleCountBatches } from '../store/cycleCountSlice';
import MobileCycleCountBatch from '../components/cycleCount/mobile/MobileCycleCountBatch';

const CycleCountMobilePage = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { batches, loading, error } = useSelector(state => state.cycleCount);
  
  const [selectedBatch, setSelectedBatch] = useState(null);
  const [showBatchModal, setShowBatchModal] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    dispatch(fetchCycleCountBatches());
  }, [dispatch]);

  const activeBatches = batches.filter(batch => {
    if (filterStatus === 'all') return true;
    return batch.status === filterStatus;
  });

  const handleBatchSelect = (batch) => {
    setSelectedBatch(batch);
    setShowBatchModal(true);
  };

  const getStatusBadge = (status) => {
    const variants = {
      'pending': 'warning',
      'in_progress': 'primary',
      'completed': 'success',
      'cancelled': 'danger'
    };
    return <Badge bg={variants[status] || 'secondary'}>{status.replace('_', ' ')}</Badge>;
  };

  const getProgressPercentage = (batch) => {
    if (!batch.total_items || batch.total_items === 0) return 0;
    return Math.round((batch.counted_items / batch.total_items) * 100);
  };

  if (loading) {
    return (
      <Container className="py-4">
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-2">Loading cycle count batches...</p>
        </div>
      </Container>
    );
  }

  return (
    <Container className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Mobile Cycle Count</h2>
        <Button 
          variant="outline-secondary" 
          size="sm"
          onClick={() => navigate('/cycle-counts')}
        >
          <i className="bi bi-arrow-left me-1"></i>
          Back
        </Button>
      </div>

      {error && (
        <Alert variant="danger" className="mb-4">
          <Alert.Heading>Error</Alert.Heading>
          <p>{error}</p>
        </Alert>
      )}

      {/* Filter Controls */}
      <Card className="mb-3">
        <Card.Body className="p-3">
          <Form.Group>
            <Form.Label className="small text-muted">Filter by Status</Form.Label>
            <Form.Select
              size="sm"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="all">All Batches</option>
              <option value="pending">Pending</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
            </Form.Select>
          </Form.Group>
        </Card.Body>
      </Card>

      {/* Batches List */}
      <ListGroup>
        {activeBatches.map(batch => (
          <ListGroup.Item 
            key={batch.id}
            className="p-3"
            style={{ cursor: 'pointer' }}
            onClick={() => handleBatchSelect(batch)}
          >
            <div className="d-flex justify-content-between align-items-start mb-2">
              <h6 className="mb-0">{batch.name}</h6>
              {getStatusBadge(batch.status)}
            </div>
            
            <p className="text-muted small mb-2">{batch.notes}</p>
            
            <div className="d-flex justify-content-between align-items-center">
              <div className="small text-muted">
                <div>Items: {batch.counted_items || 0} / {batch.total_items || 0}</div>
                <div>Progress: {getProgressPercentage(batch)}%</div>
              </div>
              
              <div className="text-end">
                <div className="progress" style={{ width: '100px', height: '8px' }}>
                  <div 
                    className="progress-bar" 
                    role="progressbar" 
                    style={{ width: `${getProgressPercentage(batch)}%` }}
                  ></div>
                </div>
                <div className="small text-muted mt-1">
                  {batch.start_date && new Date(batch.start_date).toLocaleDateString()}
                </div>
              </div>
            </div>
          </ListGroup.Item>
        ))}
      </ListGroup>

      {activeBatches.length === 0 && (
        <Alert variant="info" className="text-center">
          <i className="bi bi-info-circle me-2"></i>
          No cycle count batches found.
        </Alert>
      )}

      {/* Batch Detail Modal */}
      <Modal 
        show={showBatchModal} 
        onHide={() => setShowBatchModal(false)}
        size="lg"
        fullscreen="sm-down"
      >
        <Modal.Header closeButton>
          <Modal.Title>{selectedBatch?.name}</Modal.Title>
        </Modal.Header>
        <Modal.Body className="p-0">
          {selectedBatch && (
            <MobileCycleCountBatch 
              batchId={selectedBatch.id}
              onItemCounted={() => {
                // Refresh batches to update progress
                dispatch(fetchCycleCountBatches());
              }}
            />
          )}
        </Modal.Body>
      </Modal>

      {/* Quick Actions */}
      <div className="fixed-bottom bg-white border-top p-3 d-sm-none">
        <div className="d-flex gap-2">
          <Button 
            variant="primary" 
            size="sm" 
            className="flex-fill"
            onClick={() => {
              // Quick scan functionality
              const scannedCode = prompt('Scan or enter batch code:');
              if (scannedCode) {
                const batch = batches.find(b => 
                  b.name.toLowerCase().includes(scannedCode.toLowerCase()) ||
                  b.id.toString() === scannedCode
                );
                if (batch) {
                  handleBatchSelect(batch);
                } else {
                  alert('Batch not found');
                }
              }
            }}
          >
            <i className="bi bi-upc-scan me-1"></i>
            Quick Scan
          </Button>
          
          <Button 
            variant="outline-secondary" 
            size="sm"
            onClick={() => dispatch(fetchCycleCountBatches())}
          >
            <i className="bi bi-arrow-clockwise"></i>
          </Button>
        </div>
      </div>
    </Container>
  );
};

export default CycleCountMobilePage;
