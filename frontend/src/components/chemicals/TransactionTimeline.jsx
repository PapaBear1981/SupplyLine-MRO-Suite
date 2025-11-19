import { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Card, ListGroup, Badge, Spinner, Alert } from 'react-bootstrap';
import { fetchChemicalTimeline } from '../../store/chemicalsSlice';
import { format, formatDistanceToNow } from 'date-fns';

const TransactionTimeline = ({ chemicalId }) => {
  const dispatch = useDispatch();
  const { timeline, timelineLoading, timelineError } = useSelector((state) => state.chemicals);

  useEffect(() => {
    if (chemicalId) {
      dispatch(fetchChemicalTimeline(chemicalId));
    }
  }, [dispatch, chemicalId]);

  const getTransactionIcon = (type, transactionType) => {
    if (type === 'issuance') {
      return { icon: 'bi-arrow-up-circle-fill', color: 'danger', label: 'Issuance' };
    } else if (type === 'return') {
      return { icon: 'bi-arrow-down-circle-fill', color: 'success', label: 'Return' };
    } else if (type === 'transaction') {
      switch (transactionType) {
        case 'receipt':
          return { icon: 'bi-box-arrow-in-down', color: 'primary', label: 'Receipt' };
        case 'adjustment':
          return { icon: 'bi-sliders', color: 'warning', label: 'Adjustment' };
        case 'transfer':
          return { icon: 'bi-arrow-left-right', color: 'info', label: 'Transfer' };
        default:
          return { icon: 'bi-circle-fill', color: 'secondary', label: transactionType };
      }
    }
    return { icon: 'bi-circle', color: 'secondary', label: 'Unknown' };
  };

  if (timelineLoading) {
    return (
      <div className="text-center py-4">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading timeline...</span>
        </Spinner>
      </div>
    );
  }

  if (timelineError) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Error Loading Timeline</Alert.Heading>
        <p>{timelineError.message || 'Failed to load transaction timeline'}</p>
      </Alert>
    );
  }

  if (!timeline || !timeline.timeline || timeline.timeline.length === 0) {
    return (
      <Card>
        <Card.Body className="text-center text-muted py-5">
          <i className="bi bi-clock-history fs-1 d-block mb-2"></i>
          <p>No transaction history available</p>
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card className="transaction-timeline">
      <Card.Header className="bg-light">
        <strong>
          <i className="bi bi-clock-history me-2"></i>
          Transaction History
        </strong>
        <Badge bg="secondary" className="float-end">
          {timeline.total_events} {timeline.total_events === 1 ? 'event' : 'events'}
        </Badge>
      </Card.Header>
      <Card.Body className="p-0">
        <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
          <ListGroup variant="flush">
            {timeline.timeline.map((event, index) => {
              const { icon, color, label } = getTransactionIcon(event.type, event.transaction_type);
              const isNegative = event.quantity < 0;

              return (
                <ListGroup.Item key={index} className="py-3">
                  <div className="d-flex">
                    {/* Timeline marker */}
                    <div className="flex-shrink-0 me-3 position-relative">
                      <div className="timeline-marker">
                        <i className={`${icon} fs-5 text-${color}`}></i>
                      </div>
                      {index < timeline.timeline.length - 1 && (
                        <div
                          className="timeline-line"
                          style={{
                            position: 'absolute',
                            left: '50%',
                            top: '30px',
                            bottom: '-20px',
                            width: '2px',
                            backgroundColor: '#dee2e6',
                            transform: 'translateX(-50%)'
                          }}
                        />
                      )}
                    </div>

                    {/* Event details */}
                    <div className="flex-grow-1">
                      <div className="d-flex justify-content-between align-items-start mb-1">
                        <div>
                          <Badge bg={color} className="me-2">
                            {label}
                          </Badge>
                          <span className="text-muted small">
                            {formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })}
                          </span>
                        </div>
                        <small className="text-muted">
                          {format(new Date(event.timestamp), 'MMM d, yyyy h:mm a')}
                        </small>
                      </div>

                      <div className="mb-2">
                        {event.user_name && (
                          <div className="mb-1">
                            <i className="bi bi-person me-1"></i>
                            <strong>{event.user_name}</strong>
                          </div>
                        )}

                        {event.quantity !== undefined && event.quantity !== null && (
                          <div className="mb-1">
                            <span className={`fw-bold ${isNegative ? 'text-danger' : 'text-success'}`}>
                              {isNegative ? '' : '+'}
                              {event.quantity} {event.unit}
                            </span>
                          </div>
                        )}

                        {event.location && (
                          <div className="small text-muted">
                            <i className="bi bi-geo-alt me-1"></i>
                            {event.location}
                          </div>
                        )}

                        {(event.location_from || event.location_to) && (
                          <div className="small text-muted">
                            <i className="bi bi-arrow-right me-1"></i>
                            {event.location_from && <span>{event.location_from}</span>}
                            {event.location_from && event.location_to && <span> → </span>}
                            {event.location_to && <span>{event.location_to}</span>}
                          </div>
                        )}

                        {event.purpose && (
                          <div className="small text-muted mt-1">
                            <i className="bi bi-chat-left-text me-1"></i>
                            {event.purpose}
                          </div>
                        )}

                        {event.reference_number && (
                          <div className="small text-muted mt-1">
                            <i className="bi bi-hash me-1"></i>
                            Ref: {event.reference_number}
                          </div>
                        )}

                        {event.notes && (
                          <div className="small text-muted mt-1">
                            <i className="bi bi-sticky me-1"></i>
                            {event.notes}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </ListGroup.Item>
              );
            })}
          </ListGroup>
        </div>
      </Card.Body>
    </Card>
  );
};

export default TransactionTimeline;
