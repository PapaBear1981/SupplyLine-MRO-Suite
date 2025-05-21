import PropTypes from 'prop-types';
import { Card, Row, Col } from 'react-bootstrap';

const CycleCountStatsOverview = ({ stats }) => {
  // Default empty stats object or destructure with defaults
  const {
    batches = { total: 0, pending: 0, in_progress: 0, completed: 0 },
    items = { total: 0, counted: 0, pending: 0, completion_rate: 0 },
    results = { total: 0, with_discrepancies: 0, accuracy_rate: 0 },
    schedules = { total: 0, active: 0 }
  } = stats || {};

  return (
    <Row className="mb-4">
      <Col md={3} sm={6} className="mb-3">
        <Card className="h-100 shadow-sm">
          <Card.Body className="text-center">
            <h2 className="text-primary">{batches.total}</h2>
            <div className="text-muted">Total Count Batches</div>
            <div className="d-flex justify-content-around mt-2">
              <div>
                <span className="badge bg-secondary">{batches.pending} Pending</span>
              </div>
              <div>
                <span className="badge bg-primary">{batches.in_progress} In Progress</span>
              </div>
              <div>
                <span className="badge bg-success">{batches.completed} Completed</span>
              </div>
            </div>
          </Card.Body>
        </Card>
      </Col>
      <Col md={3} sm={6} className="mb-3">
        <Card className="h-100 shadow-sm">
          <Card.Body className="text-center">
            <h2 className="text-success">{items.total}</h2>
            <div className="text-muted">Total Count Items</div>
            <div className="d-flex justify-content-around mt-2">
              <div>
                <span className="badge bg-success">{items.counted} Counted</span>
              </div>
              <div>
                <span className="badge bg-secondary">{items.pending} Pending</span>
              </div>
            </div>
            <div className="progress mt-2" style={{ height: '5px' }}>
              <div
                className="progress-bar bg-success"
                role="progressbar"
                style={{ width: `${items.completion_rate}%` }}
                aria-valuenow={items.completion_rate}
                aria-valuemin="0"
                aria-valuemax="100"
              ></div>
            </div>
            <div className="text-muted small mt-1">
              {items.completion_rate}% Complete
            </div>
          </Card.Body>
        </Card>
      </Col>
      <Col md={3} sm={6} className="mb-3">
        <Card className="h-100 shadow-sm">
          <Card.Body className="text-center">
            <h2 className="text-warning">{results.with_discrepancies}</h2>
            <div className="text-muted">Discrepancies</div>
            <div className="d-flex justify-content-center mt-2">
              <div>
                <span className="badge bg-info">{results.total} Total Results</span>
              </div>
            </div>
            <div className="progress mt-2" style={{ height: '5px' }}>
              <div
                className="progress-bar bg-success"
                role="progressbar"
                style={{ width: `${results.accuracy_rate}%` }}
                aria-valuenow={results.accuracy_rate}
                aria-valuemin="0"
                aria-valuemax="100"
              ></div>
            </div>
            <div className="text-muted small mt-1">
              {results.accuracy_rate}% Accuracy Rate
            </div>
          </Card.Body>
        </Card>
      </Col>
      <Col md={3} sm={6} className="mb-3">
        <Card className="h-100 shadow-sm">
          <Card.Body className="text-center">
            <h2 className="text-info">{schedules.total}</h2>
            <div className="text-muted">Count Schedules</div>
            <div className="d-flex justify-content-center mt-2">
              <div>
                <span className="badge bg-success">{schedules.active} Active</span>
              </div>
            </div>
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );
};

CycleCountStatsOverview.propTypes = {
  stats: PropTypes.shape({
    batches: PropTypes.shape({
      total: PropTypes.number,
      pending: PropTypes.number,
      in_progress: PropTypes.number,
      completed: PropTypes.number
    }),
    items: PropTypes.shape({
      total: PropTypes.number,
      counted: PropTypes.number,
      pending: PropTypes.number,
      completion_rate: PropTypes.number
    }),
    results: PropTypes.shape({
      total: PropTypes.number,
      with_discrepancies: PropTypes.number,
      accuracy_rate: PropTypes.number
    }),
    schedules: PropTypes.shape({
      total: PropTypes.number,
      active: PropTypes.number
    })
  })
};

export default CycleCountStatsOverview;
