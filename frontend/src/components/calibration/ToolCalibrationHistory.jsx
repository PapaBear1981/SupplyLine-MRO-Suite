import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Table, Badge, Button, Spinner, Alert, Pagination } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { fetchToolCalibrations } from '../../store/calibrationSlice';

const ToolCalibrationHistory = ({ toolId }) => {
  const dispatch = useDispatch();
  const { toolCalibrations, loading } = useSelector((state) => state.calibration);
  const { user } = useSelector((state) => state.auth);

  const [page, setPage] = useState(1);
  const [limit] = useState(5);

  // Check if user has permission to calibrate tools
  const hasPermission = user?.is_admin || user?.department === 'Materials';

  // Get calibration history for this tool
  const calibrationData = toolCalibrations[toolId] || { calibrations: [], pagination: { total: 0, pages: 0 } };
  const { calibrations, pagination } = calibrationData;

  useEffect(() => {
    // Convert toolId to number if it's a string
    const id = typeof toolId === 'string' ? parseInt(toolId, 10) : toolId;
    dispatch(fetchToolCalibrations({ toolId: id, page, limit }));
  }, [dispatch, toolId, page, limit]);

  const handlePageChange = (newPage) => {
    setPage(newPage);
  };

  const renderPagination = () => {
    if (!pagination || pagination.pages <= 1) return null;

    const items = [];

    // Previous button
    items.push(
      <Pagination.Prev
        key="prev"
        onClick={() => handlePageChange(Math.max(1, page - 1))}
        disabled={page === 1}
      />
    );

    // First page
    items.push(
      <Pagination.Item
        key={1}
        active={page === 1}
        onClick={() => handlePageChange(1)}
      >
        1
      </Pagination.Item>
    );

    // Ellipsis if needed
    if (page > 3) {
      items.push(<Pagination.Ellipsis key="ellipsis1" disabled />);
    }

    // Pages around current
    for (let i = Math.max(2, page - 1); i <= Math.min(pagination.pages - 1, page + 1); i++) {
      items.push(
        <Pagination.Item
          key={i}
          active={page === i}
          onClick={() => handlePageChange(i)}
        >
          {i}
        </Pagination.Item>
      );
    }

    // Ellipsis if needed
    if (page < pagination.pages - 2) {
      items.push(<Pagination.Ellipsis key="ellipsis2" disabled />);
    }

    // Last page if not the first page
    if (pagination.pages > 1) {
      items.push(
        <Pagination.Item
          key={pagination.pages}
          active={page === pagination.pages}
          onClick={() => handlePageChange(pagination.pages)}
        >
          {pagination.pages}
        </Pagination.Item>
      );
    }

    // Next button
    items.push(
      <Pagination.Next
        key="next"
        onClick={() => handlePageChange(Math.min(pagination.pages, page + 1))}
        disabled={page === pagination.pages}
      />
    );

    return <Pagination>{items}</Pagination>;
  };

  if (loading && !calibrations.length) {
    return (
      <div className="text-center my-4">
        <Spinner animation="border" role="status" />
        <p className="mt-2">Loading calibration history...</p>
      </div>
    );
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h5 className="mb-0">Calibration History</h5>
        {hasPermission && (
          <Button
            as={Link}
            to={`/tools/${toolId}/calibrations/new`}
            variant="primary"
            size="sm"
          >
            <i className="bi bi-plus-circle me-1"></i>
            Calibrate Tool
          </Button>
        )}
      </div>

      {calibrations.length === 0 ? (
        <Alert variant="info">
          <Alert.Heading>No Calibration History</Alert.Heading>
          <p>This tool has no calibration records.</p>
        </Alert>
      ) : (
        <>
          <Table striped bordered hover responsive>
            <thead>
              <tr>
                <th>Date</th>
                <th>Next Due Date</th>
                <th>Performed By</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {calibrations.map((calibration) => (
                <tr key={calibration.id}>
                  <td>{new Date(calibration.calibration_date).toLocaleDateString()}</td>
                  <td>
                    {calibration.next_calibration_date
                      ? new Date(calibration.next_calibration_date).toLocaleDateString()
                      : 'N/A'}
                  </td>
                  <td>{calibration.performed_by_name}</td>
                  <td>
                    <Badge bg={
                      calibration.calibration_status === 'pass' ? 'success' :
                      calibration.calibration_status === 'fail' ? 'danger' : 'warning'
                    }>
                      {calibration.calibration_status === 'pass' ? 'Pass' :
                       calibration.calibration_status === 'fail' ? 'Fail' : 'Limited'}
                    </Badge>
                  </td>
                  <td>
                    <Button
                      as={Link}
                      to={`/tools/${toolId}/calibrations/${calibration.id}`}
                      variant="info"
                      size="sm"
                    >
                      View Details
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>

          <div className="d-flex justify-content-center mt-3">
            {renderPagination()}
          </div>
        </>
      )}
    </div>
  );
};

export default ToolCalibrationHistory;
