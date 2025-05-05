import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Table, Badge, Card, Spinner } from 'react-bootstrap';
import { fetchToolServiceHistory } from '../../store/toolsSlice';

const ServiceHistoryList = ({ toolId }) => {
  const dispatch = useDispatch();
  const { serviceHistory, serviceLoading, serviceError } = useSelector((state) => state.tools);
  
  useEffect(() => {
    if (toolId) {
      dispatch(fetchToolServiceHistory({ id: toolId }));
    }
  }, [dispatch, toolId]);
  
  const history = serviceHistory[toolId] || [];
  
  const getActionTypeLabel = (actionType) => {
    switch (actionType) {
      case 'remove_maintenance':
        return 'Removed for Maintenance';
      case 'remove_permanent':
        return 'Permanently Removed';
      case 'return_service':
        return 'Returned to Service';
      default:
        return actionType;
    }
  };
  
  const getActionTypeBadge = (actionType) => {
    switch (actionType) {
      case 'remove_maintenance':
        return 'warning';
      case 'remove_permanent':
        return 'danger';
      case 'return_service':
        return 'success';
      default:
        return 'secondary';
    }
  };
  
  if (serviceLoading) {
    return (
      <div className="text-center my-4">
        <Spinner animation="border" role="status" size="sm" />
        <span className="ms-2">Loading service history...</span>
      </div>
    );
  }
  
  if (serviceError) {
    return (
      <Card className="border-danger">
        <Card.Body className="text-danger">
          Failed to load service history: {serviceError.error || 'Unknown error'}
        </Card.Body>
      </Card>
    );
  }
  
  return (
    <Card>
      <Card.Header>
        <h5 className="mb-0">Service History</h5>
      </Card.Header>
      <Card.Body>
        {history.length > 0 ? (
          <Table striped bordered hover responsive>
            <thead>
              <tr>
                <th>Date</th>
                <th>Action</th>
                <th>User</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>
              {history.map((record) => (
                <tr key={record.id}>
                  <td>{new Date(record.timestamp).toLocaleDateString()}</td>
                  <td>
                    <Badge bg={getActionTypeBadge(record.action_type)}>
                      {getActionTypeLabel(record.action_type)}
                    </Badge>
                  </td>
                  <td>{record.user_name}</td>
                  <td>
                    <div>{record.reason}</div>
                    {record.comments && (
                      <small className="text-muted">{record.comments}</small>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        ) : (
          <p className="text-center mb-0">No service history available for this tool.</p>
        )}
      </Card.Body>
    </Card>
  );
};

export default ServiceHistoryList;
