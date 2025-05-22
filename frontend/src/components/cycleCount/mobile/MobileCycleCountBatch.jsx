import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Card, 
  Button, 
  Alert, 
  Spinner, 
  ProgressBar, 
  Form, 
  InputGroup,
  Badge,
  Modal
} from 'react-bootstrap';
import { 
  fetchCycleCountBatch, 
  fetchCycleCountItems,
  completeCycleCountBatch
} from '../../../store/cycleCountSlice';
import MobileCycleCountItem from './MobileCycleCountItem';

const MobileCycleCountBatch = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { id } = useParams();
  
  const { data: batch, loading: batchLoading, error: batchError } = 
    useSelector((state) => state.cycleCount.currentBatch);
  const { data: items, loading: itemsLoading, error: itemsError } = 
    useSelector((state) => state.cycleCount.items);
  
  const [searchTerm, setSearchTerm] = useState('');
  const [currentItemIndex, setCurrentItemIndex] = useState(0);
  const [completedItems, setCompletedItems] = useState([]);
  const [showScanner, setShowScanner] = useState(false);
  const [scanResult, setScanResult] = useState('');
  const [showCompleteModal, setShowCompleteModal] = useState(false);
  const [completing, setCompleting] = useState(false);
  
  useEffect(() => {
    if (id) {
      dispatch(fetchCycleCountBatch(id));
      dispatch(fetchCycleCountItems(id));
    }
  }, [dispatch, id]);
  
  useEffect(() => {
    // Initialize completed items from already counted items
    if (items && items.length > 0) {
      const counted = items.filter(item => item.status === 'counted').map(item => item.id);
      setCompletedItems(counted);
    }
  }, [items]);
  
  const handleItemComplete = (itemId) => {
    setCompletedItems(prev => [...prev, itemId]);
    
    // Move to next item if available
    if (filteredItems.length > currentItemIndex + 1) {
      setCurrentItemIndex(currentItemIndex + 1);
    }
  };
  
  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    setCurrentItemIndex(0); // Reset to first item when searching
  };
  
  const handleScanToggle = () => {
    setShowScanner(!showScanner);
    if (!showScanner) {
      // Initialize scanner here
      // This would typically involve accessing the device camera
      // and setting up barcode scanning
      console.log('Scanner would be initialized here');
    } else {
      // Clean up scanner resources
      console.log('Scanner would be cleaned up here');
    }
  };
  
  const handleScanComplete = (result) => {
    setScanResult(result);
    setShowScanner(false);
    
    // Search for the scanned item
    const foundIndex = items.findIndex(item => {
      if (item.item_type === 'tool' && item.tool) {
        return item.tool.tool_number === result || 
               item.tool.serial_number === result;
      } else if (item.item_type === 'chemical' && item.chemical) {
        return item.chemical.part_number === result;
      }
      return false;
    });
    
    if (foundIndex !== -1) {
      setCurrentItemIndex(foundIndex);
      setSearchTerm('');
    } else {
      // Show not found message
      alert(`Item with code ${result} not found in this batch`);
    }
  };
  
  const handleCompleteBatch = async () => {
    setCompleting(true);
    try {
      await dispatch(completeCycleCountBatch(id)).unwrap();
      setShowCompleteModal(false);
      navigate('/cycle-counts');
    } catch (error) {
      console.error('Failed to complete batch:', error);
    } finally {
      setCompleting(false);
    }
  };
  
  // Filter items based on search term
  const filteredItems = items ? items.filter(item => {
    const searchLower = searchTerm.toLowerCase();
    
    // Search in tool properties
    if (item.item_type === 'tool' && item.tool) {
      return (
        (item.tool.tool_number && item.tool.tool_number.toLowerCase().includes(searchLower)) ||
        (item.tool.serial_number && item.tool.serial_number.toLowerCase().includes(searchLower)) ||
        (item.tool.description && item.tool.description.toLowerCase().includes(searchLower)) ||
        (item.expected_location && item.expected_location.toLowerCase().includes(searchLower))
      );
    }
    
    // Search in chemical properties
    if (item.item_type === 'chemical' && item.chemical) {
      return (
        (item.chemical.part_number && item.chemical.part_number.toLowerCase().includes(searchLower)) ||
        (item.chemical.description && item.chemical.description.toLowerCase().includes(searchLower)) ||
        (item.expected_location && item.expected_location.toLowerCase().includes(searchLower))
      );
    }
    
    return false;
  }) : [];
  
  // Calculate progress
  const progress = items && items.length > 0
    ? Math.round((completedItems.length / items.length) * 100)
    : 0;
  
  if (batchLoading || itemsLoading) {
    return (
      <div className="text-center my-5">
        <Spinner animation="border" role="status" />
        <p className="mt-2">Loading cycle count batch...</p>
      </div>
    );
  }
  
  if (batchError || itemsError) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Error Loading Batch</Alert.Heading>
        <p>{batchError?.error || itemsError?.error || 'An error occurred while loading the cycle count batch'}</p>
        <Button onClick={() => navigate('/cycle-counts')} variant="outline-primary">
          Return to Cycle Counts
        </Button>
      </Alert>
    );
  }
  
  if (!batch) {
    return (
      <Alert variant="warning">
        <Alert.Heading>Batch Not Found</Alert.Heading>
        <p>The requested cycle count batch could not be found.</p>
        <Button onClick={() => navigate('/cycle-counts')} variant="outline-primary">
          Return to Cycle Counts
        </Button>
      </Alert>
    );
  }
  
  return (
    <div className="mobile-cycle-count-batch">
      <Card className="mb-3">
        <Card.Header>
          <h5 className="mb-0">{batch.name}</h5>
          <div className="d-flex align-items-center mt-2">
            <Badge bg={batch.status === 'completed' ? 'success' : batch.status === 'in_progress' ? 'warning' : 'secondary'}>
              {batch.status === 'in_progress' ? 'In Progress' : batch.status === 'completed' ? 'Completed' : 'Pending'}
            </Badge>
            <span className="ms-2 text-muted small">
              {batch.item_count || 0} items
            </span>
          </div>
        </Card.Header>
        <Card.Body>
          <ProgressBar 
            now={progress} 
            label={`${completedItems.length}/${items?.length || 0} (${progress}%)`}
            variant={progress < 30 ? 'danger' : progress < 70 ? 'warning' : 'success'}
            className="mb-3"
          />
          
          <div className="d-flex mb-3">
            <Button 
              variant="outline-primary" 
              className="me-2 w-100"
              onClick={handleScanToggle}
            >
              <i className="bi bi-upc-scan me-1"></i>
              {showScanner ? 'Cancel Scan' : 'Scan Barcode'}
            </Button>
            
            <Button 
              variant="outline-success" 
              className="w-100"
              onClick={() => setShowCompleteModal(true)}
              disabled={items?.length === 0 || completedItems.length < items?.length}
            >
              Complete Batch
            </Button>
          </div>
          
          <InputGroup className="mb-3">
            <InputGroup.Text>
              <i className="bi bi-search"></i>
            </InputGroup.Text>
            <Form.Control
              type="text"
              placeholder="Search items..."
              value={searchTerm}
              onChange={handleSearch}
            />
            {searchTerm && (
              <Button 
                variant="outline-secondary" 
                onClick={() => setSearchTerm('')}
              >
                <i className="bi bi-x"></i>
              </Button>
            )}
          </InputGroup>
          
          {showScanner && (
            <div className="scanner-container mb-3 p-3 bg-light border rounded">
              <p className="text-center mb-2">Scanner would appear here</p>
              <div className="d-flex justify-content-center">
                <Button 
                  variant="primary" 
                  size="sm"
                  onClick={() => handleScanComplete(prompt('Enter barcode value:'))}
                >
                  Simulate Scan
                </Button>
              </div>
            </div>
          )}
        </Card.Body>
      </Card>
      
      {filteredItems.length === 0 ? (
        <Alert variant="info">
          No items found {searchTerm ? 'matching your search' : 'in this batch'}.
        </Alert>
      ) : (
        <>
          {filteredItems.length > 0 && currentItemIndex < filteredItems.length && (
            <MobileCycleCountItem 
              item={filteredItems[currentItemIndex]} 
              onComplete={handleItemComplete}
            />
          )}
          
          <div className="d-flex justify-content-between mb-3">
            <Button
              variant="outline-secondary"
              disabled={currentItemIndex === 0}
              onClick={() => setCurrentItemIndex(prev => Math.max(0, prev - 1))}
            >
              <i className="bi bi-arrow-left"></i> Previous
            </Button>
            
            <div className="text-center">
              <Badge bg="secondary" className="px-3 py-2">
                {currentItemIndex + 1} of {filteredItems.length}
              </Badge>
            </div>
            
            <Button
              variant="outline-secondary"
              disabled={currentItemIndex >= filteredItems.length - 1}
              onClick={() => setCurrentItemIndex(prev => Math.min(filteredItems.length - 1, prev + 1))}
            >
              Next <i className="bi bi-arrow-right"></i>
            </Button>
          </div>
        </>
      )}
      
      {/* Complete Batch Confirmation Modal */}
      <Modal show={showCompleteModal} onHide={() => setShowCompleteModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Complete Batch</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {completedItems.length < items?.length ? (
            <Alert variant="warning">
              <Alert.Heading>Incomplete Batch</Alert.Heading>
              <p>
                You have only counted {completedItems.length} out of {items?.length} items.
                Are you sure you want to complete this batch?
              </p>
            </Alert>
          ) : (
            <p>Are you sure you want to mark this batch as complete? This action cannot be undone.</p>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowCompleteModal(false)}>
            Cancel
          </Button>
          <Button 
            variant="success" 
            onClick={handleCompleteBatch}
            disabled={completing}
          >
            {completing ? (
              <>
                <Spinner
                  as="span"
                  animation="border"
                  size="sm"
                  role="status"
                  aria-hidden="true"
                  className="me-2"
                />
                Completing...
              </>
            ) : (
              'Complete Batch'
            )}
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default MobileCycleCountBatch;
