import { Card, Row, Col } from 'react-bootstrap';

const CycleCountStatsOverview = ({ stats }) => {
  return (
    <Row className="mb-4">
      <Col md={3} sm={6} className="mb-3">
        <Card className="h-100 shadow-sm">
          <Card.Body className="text-center">
            <h2 className="text-primary">{stats.batches.total}</h2>
            <div className="text-muted">Total Count Batches</div>
            <div className="d-flex justify-content-around mt-2">
              <div>
                <span className="badge bg-secondary">{stats.batches.pending} Pending</span>
              </div>
              <div>
                <span className="badge bg-primary">{stats.batches.in_progress} In Progress</span>
              </div>
              <div>
                <span className="badge bg-success">{stats.batches.completed} Completed</span>
              </div>
            </div>
          </Card.Body>
        </Card>
      </Col>
      <Col md={3} sm={6} className="mb-3">
        <Card className="h-100 shadow-sm">
          <Card.Body className="text-center">
            <h2 className="text-success">{stats.items.total}</h2>
            <div className="text-muted">Total Count Items</div>
            <div className="d-flex justify-content-around mt-2">
              <div>
                <span className="badge bg-success">{stats.items.counted} Counted</span>
              </div>
              <div>
                <span className="badge bg-secondary">{stats.items.pending} Pending</span>
              </div>
            </div>
            <div className="progress mt-2" style={{ height: '5px' }}>
              <div 
                className="progress-bar bg-success" 
                role="progressbar" 
                style={{ width: `${stats.items.completion_rate}%` }}
                aria-valuenow={stats.items.completion_rate} 
                aria-valuemin="0" 
                aria-valuemax="100"
              ></div>
            </div>
            <div className="text-muted small mt-1">
              {stats.items.completion_rate}% Complete
            </div>
          </Card.Body>
        </Card>
      </Col>
      <Col md={3} sm={6} className="mb-3">
        <Card className="h-100 shadow-sm">
          <Card.Body className="text-center">
            <h2 className="text-warning">{stats.results.with_discrepancies}</h2>
            <div className="text-muted">Discrepancies</div>
            <div className="d-flex justify-content-center mt-2">
              <div>
                <span className="badge bg-info">{stats.results.total} Total Results</span>
              </div>
            </div>
            <div className="progress mt-2" style={{ height: '5px' }}>
              <div 
                className="progress-bar bg-success" 
                role="progressbar" 
                style={{ width: `${stats.results.accuracy_rate}%` }}
                aria-valuenow={stats.results.accuracy_rate} 
                aria-valuemin="0" 
                aria-valuemax="100"
              ></div>
            </div>
            <div className="text-muted small mt-1">
              {stats.results.accuracy_rate}% Accuracy Rate
            </div>
          </Card.Body>
        </Card>
      </Col>
      <Col md={3} sm={6} className="mb-3">
        <Card className="h-100 shadow-sm">
          <Card.Body className="text-center">
            <h2 className="text-info">{stats.schedules.total}</h2>
            <div className="text-muted">Count Schedules</div>
            <div className="d-flex justify-content-center mt-2">
              <div>
                <span className="badge bg-success">{stats.schedules.active} Active</span>
              </div>
            </div>
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );
};

export default CycleCountStatsOverview;
