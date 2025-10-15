import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Table, Alert, Badge, Spinner } from 'react-bootstrap';
import { fetchKitIssuances } from '../../store/kitsSlice';

const KitIssuanceHistory = ({ kitId }) => {
  const dispatch = useDispatch();
  const { kitIssuances, loading } = useSelector((state) => state.kits);
  const issuances = kitIssuances[kitId] || [];

  useEffect(() => {
    if (kitId) {
      dispatch(fetchKitIssuances({ kitId }));
    }
  }, [dispatch, kitId]);

  if (loading) {
    return (
      <Card>
        <Card.Body className="text-center py-5">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
          <p className="mt-3 text-muted">Loading issuance history...</p>
        </Card.Body>
      </Card>
    );
  }

  if (issuances.length === 0) {
    return (
      <Card>
        <Card.Body>
          <Alert variant="info" className="mb-0">
            <i className="bi bi-info-circle me-2"></i>
            No issuance history found for this kit.
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  const getItemTypeBadge = (itemType) => {
    const badges = {
      tool: 'primary',
      chemical: 'warning',
      expendable: 'success',
    };
    return <Badge bg={badges[itemType] || 'secondary'}>{itemType}</Badge>;
  };

  return (
    <Card>
      <Card.Header className="bg-light">
        <h5 className="mb-0">
          <i className="bi bi-clock-history me-2"></i>
          Issuance History
        </h5>
        <small className="text-muted">
          Total Issuances: {issuances.length}
        </small>
      </Card.Header>
      <Card.Body>
        <div className="table-responsive">
          <Table hover bordered className="align-middle mb-0">
            <thead>
              <tr>
                <th>Part/Tool Number</th>
                <th>Serial/Lot Number</th>
                <th>Description</th>
                <th>Qty</th>
                <th>Issued To</th>
                <th>Issued By</th>
                <th>Date/Time</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {issuances.map((issuance) => (
                <tr key={issuance.id}>
                  <td>
                    {issuance.part_number || '-'}
                  </td>
                  <td>
                    {issuance.serial_number || issuance.lot_number || '-'}
                  </td>
                  <td>
                    <div className="d-flex align-items-center gap-2">
                      {getItemTypeBadge(issuance.item_type)}
                      <span>{issuance.description || 'N/A'}</span>
                    </div>
                  </td>
                  <td className="text-end">
                    <strong>{issuance.quantity}</strong>
                  </td>
                  <td>
                    {issuance.recipient_name || (issuance.issued_to ? `User ${issuance.issued_to}` : '-')}
                  </td>
                  <td>
                    {issuance.issuer_name || `User ${issuance.issued_by}`}
                  </td>
                  <td className="text-nowrap">
                    {new Date(issuance.issued_date).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </td>
                  <td>
                    {issuance.notes ? (
                      <small className="text-muted">{issuance.notes}</small>
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

export default KitIssuanceHistory;

