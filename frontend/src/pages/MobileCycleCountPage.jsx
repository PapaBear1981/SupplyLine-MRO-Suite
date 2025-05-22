import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { 
  Card, 
  Button, 
  Alert, 
  Spinner, 
  ListGroup, 
  Badge, 
  Form,
  InputGroup,
  ProgressBar,
  Tabs,
  Tab
} from 'react-bootstrap';
import { 
  fetchCycleCountBatches,
  fetchCycleCountStats
} from '../store/cycleCountSlice';

const MobileCycleCountPage = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  
  const { data: batches, loading: batchesLoading, error: batchesError } = 
    useSelector((state) => state.cycleCount.batches);
  const { data: stats, loading: statsLoading, error: statsError } = 
    useSelector((state) => state.cycleCount.stats);
  
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('in_progress');
  const [showCompleted, setShowCompleted] = useState(false);
  
  useEffect(() => {
    dispatch(fetchCycleCountBatches());
    dispatch(fetchCycleCountStats());
  }, [dispatch]);
  
  // Filter batches based on search term and active tab
  const filteredBatches = batches ? batches.filter(batch => {
    const searchMatch = !searchTerm || 
      (batch.name && batch.name.toLowerCase().includes(searchTerm.toLowerCase()));
    
    if (activeTab === 'all') {
      return searchMatch;
    } else if (activeTab === 'in_progress') {
      return searchMatch && batch.status === 'in_progress';
    } else if (activeTab === 'pending') {
      return searchMatch && batch.status === 'pending';
    } else if (activeTab === 'completed') {
      return searchMatch && batch.status === 'completed';
    }
    
    return searchMatch;
  }) : [];
  
  // Helper function to get badge color based on status
  const getBadgeColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'warning';
      case 'pending':
        return 'secondary';
      default:
        return 'primary';
    }
  };
  
  // Helper function to format status text
  const formatStatus = (status) => {
    switch (status) {
      case 'in_progress':
        return 'In Progress';
      case 'completed':
        return 'Completed';
      case 'pending':
        return 'Pending';
      default:
        return status;
    }
  };
  
  if (batchesLoading || statsLoading) {
    return (
      <div className="text-center my-5">
        <Spinner animation="border" role="status" />
        <p className="mt-2">Loading cycle counts...</p>
      </div>
    );
  }
  
  if (batchesError || statsError) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Error Loading Data</Alert.Heading>
        <p>{batchesError?.error || statsError?.error || 'An error occurred while loading cycle count data'}</p>
      </Alert>
    );
  }
  
  return (
    <div className="mobile-cycle-count-page">
      <Card className="mb-3">
        <Card.Header>
          <h5 className="mb-0">Cycle Count Dashboard</h5>
        </Card.Header>
        <Card.Body>
          <div className="d-flex flex-wrap justify-content-between mb-3">
            <div className="stat-card bg-primary text-white p-3 rounded mb-2" style={{ flex: '1 0 45%', margin: '0 5px' }}>
              <h3 className="mb-0">{stats?.batches?.in_progress || 0}</h3>
              <small>In Progress</small>
            </div>
            <div className="stat-card bg-success text-white p-3 rounded mb-2" style={{ flex: '1 0 45%', margin: '0 5px' }}>
              <h3 className="mb-0">{stats?.batches?.completed || 0}</h3>
              <small>Completed</small>
            </div>
            <div className="stat-card bg-info text-white p-3 rounded mb-2" style={{ flex: '1 0 45%', margin: '0 5px' }}>
              <h3 className="mb-0">{stats?.items?.total || 0}</h3>
              <small>Total Items</small>
            </div>
            <div className="stat-card bg-warning text-white p-3 rounded mb-2" style={{ flex: '1 0 45%', margin: '0 5px' }}>
              <h3 className="mb-0">{stats?.results?.with_discrepancies || 0}</h3>
              <small>Discrepancies</small>
            </div>
          </div>
          
          <div className="mb-3">
            <div className="d-flex justify-content-between align-items-center mb-2">
              <small className="text-muted">Overall Completion</small>
              <small>{stats?.items?.completion_rate || 0}%</small>
            </div>
            <ProgressBar 
              now={stats?.items?.completion_rate || 0} 
              variant={
                (stats?.items?.completion_rate || 0) < 30 ? 'danger' : 
                (stats?.items?.completion_rate || 0) < 70 ? 'warning' : 
                'success'
              }
            />
          </div>
        </Card.Body>
      </Card>
      
      <Card>
        <Card.Header>
          <Tabs
            activeKey={activeTab}
            onSelect={(k) => setActiveTab(k)}
            className="mb-0"
          >
            <Tab eventKey="in_progress" title="In Progress" />
            <Tab eventKey="pending" title="Pending" />
            <Tab eventKey="completed" title="Completed" />
            <Tab eventKey="all" title="All" />
          </Tabs>
        </Card.Header>
        <Card.Body>
          <InputGroup className="mb-3">
            <InputGroup.Text>
              <i className="bi bi-search"></i>
            </InputGroup.Text>
            <Form.Control
              type="text"
              placeholder="Search batches..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
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
          
          {filteredBatches.length === 0 ? (
            <Alert variant="info">
              No cycle count batches found {searchTerm ? 'matching your search' : 'in this category'}.
            </Alert>
          ) : (
            <ListGroup>
              {filteredBatches.map(batch => (
                <ListGroup.Item 
                  key={batch.id}
                  action
                  onClick={() => navigate(`/mobile/cycle-counts/${batch.id}`)}
                  className="d-flex flex-column"
                >
                  <div className="d-flex justify-content-between align-items-start w-100">
                    <div>
                      <h6 className="mb-1">{batch.name}</h6>
                      <Badge bg={getBadgeColor(batch.status)}>
                        {formatStatus(batch.status)}
                      </Badge>
                    </div>
                    <small className="text-muted">
                      {batch.start_date ? new Date(batch.start_date).toLocaleDateString() : 'Not started'}
                    </small>
                  </div>
                  
                  {batch.item_count > 0 && (
                    <div className="mt-2 w-100">
                      <div className="d-flex justify-content-between align-items-center mb-1">
                        <small className="text-muted">Progress</small>
                        <small>{batch.completed_count || 0}/{batch.item_count}</small>
                      </div>
                      <ProgressBar 
                        now={Math.round(((batch.completed_count || 0) / batch.item_count) * 100)} 
                        variant={
                          Math.round(((batch.completed_count || 0) / batch.item_count) * 100) < 30 ? 'danger' : 
                          Math.round(((batch.completed_count || 0) / batch.item_count) * 100) < 70 ? 'warning' : 
                          'success'
                        }
                        style={{ height: '5px' }}
                      />
                    </div>
                  )}
                </ListGroup.Item>
              ))}
            </ListGroup>
          )}
        </Card.Body>
      </Card>
    </div>
  );
};

export default MobileCycleCountPage;
