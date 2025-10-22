import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Table, Badge, Spinner, Alert } from 'react-bootstrap';
import { FaExchangeAlt, FaWarehouse, FaBox, FaArrowRight } from 'react-icons/fa';
import { fetchTransfers } from '../../store/kitTransfersSlice';

const KitTransferHistory = ({ kitId }) => {
  const dispatch = useDispatch();
  const { transfers, loading } = useSelector((state) => state.kitTransfers);

  useEffect(() => {
    if (kitId) {
      // Fetch transfers where this kit is either source or destination
      dispatch(fetchTransfers({ kit_id: kitId }));
    }
  }, [dispatch, kitId]);

  // Transfers are already filtered by backend, just sort by date descending
  const sortedTransfers = [...transfers].sort(
    (a, b) => new Date(b.transfer_date) - new Date(a.transfer_date)
  );

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return <Badge bg="success">Completed</Badge>;
      case 'pending':
        return <Badge bg="warning">Pending</Badge>;
      case 'cancelled':
        return <Badge bg="danger">Cancelled</Badge>;
      default:
        return <Badge bg="secondary">{status}</Badge>;
    }
  };

  const getItemTypeBadge = (itemType) => {
    switch (itemType) {
      case 'tool':
        return <Badge bg="primary">Tool</Badge>;
      case 'chemical':
        return <Badge bg="info">Chemical</Badge>;
      case 'expendable':
        return <Badge bg="secondary">Expendable</Badge>;
      default:
        return <Badge bg="secondary">{itemType}</Badge>;
    }
  };

  const getLocationDisplay = (locationType, locationId, locationName) => {
    if (locationType === 'kit') {
      return (
        <div className="d-flex align-items-center gap-2">
          <FaBox className="text-primary" />
          <span>{locationName || `Kit ${locationId}`}</span>
        </div>
      );
    } else {
      return (
        <div className="d-flex align-items-center gap-2">
          <FaWarehouse className="text-info" />
          <span>{locationName || `Warehouse ${locationId}`}</span>
        </div>
      );
    }
  };

  if (loading) {
    return (
      <Card>
        <Card.Body className="text-center py-5">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
          <p className="mt-3 text-muted">Loading transfer history...</p>
        </Card.Body>
      </Card>
    );
  }

  if (sortedTransfers.length === 0) {
    return (
      <Card>
        <Card.Header className="bg-light">
          <h5 className="mb-0">
            <FaExchangeAlt className="me-2" />
            Transfer History
          </h5>
        </Card.Header>
        <Card.Body>
          <Alert variant="info" className="mb-0">
            <FaExchangeAlt className="me-2" />
            No transfer history available for this kit
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card>
      <Card.Header className="bg-light">
        <h5 className="mb-0">
          <FaExchangeAlt className="me-2" />
          Transfer History
        </h5>
        <small className="text-muted">
          Total Transfers: {sortedTransfers.length}
        </small>
      </Card.Header>
      <Card.Body>
        <div className="table-responsive">
          <Table hover bordered className="align-middle mb-0">
            <thead>
              <tr>
                <th>Date</th>
                <th>From</th>
                <th></th>
                <th>To</th>
                <th>Item Type</th>
                <th>Part/Tool Number</th>
                <th>Description</th>
                <th>Qty</th>
                <th>Status</th>
                <th>Transferred By</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {sortedTransfers.map((transfer) => (
                <tr key={transfer.id}>
                  <td className="text-nowrap">
                    {new Date(transfer.transfer_date).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </td>
                  <td>
                    {getLocationDisplay(
                      transfer.from_location_type,
                      transfer.from_location_id,
                      transfer.from_location_name
                    )}
                  </td>
                  <td className="text-center">
                    <FaArrowRight className="text-muted" />
                  </td>
                  <td>
                    {getLocationDisplay(
                      transfer.to_location_type,
                      transfer.to_location_id,
                      transfer.to_location_name
                    )}
                  </td>
                  <td>{getItemTypeBadge(transfer.item_type)}</td>
                  <td>{transfer.part_number || transfer.tool_number || '-'}</td>
                  <td>{transfer.description || '-'}</td>
                  <td className="text-end">
                    <strong>{transfer.quantity}</strong>
                  </td>
                  <td>{getStatusBadge(transfer.status)}</td>
                  <td>
                    {transfer.transferred_by_name || `User ${transfer.transferred_by}`}
                  </td>
                  <td>
                    {transfer.notes ? (
                      <small className="text-muted">{transfer.notes}</small>
                    ) : (
                      '-'
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      </Card.Body>
    </Card>
  );
};

export default KitTransferHistory;

