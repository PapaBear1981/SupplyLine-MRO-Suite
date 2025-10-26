import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Table, Alert, Badge, Spinner, Pagination } from 'react-bootstrap';
import { fetchKitIssuances } from '../../store/kitsSlice';

const KitIssuanceHistory = ({ kitId }) => {
  const dispatch = useDispatch();
  const { kitIssuances, loading } = useSelector((state) => state.kits);
  const issuances = kitIssuances[kitId] || [];
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    if (kitId) {
      dispatch(fetchKitIssuances({ kitId }));
    }
  }, [dispatch, kitId]);

  // Reset to page 1 when issuances change
  useEffect(() => {
    setCurrentPage(1);
  }, [issuances]);

  // Pagination logic
  const totalPages = Math.ceil(issuances.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentIssuances = issuances.slice(startIndex, endIndex);

  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
  };

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
          {totalPages > 1 && ` | Page ${currentPage} of ${totalPages}`}
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
              {currentIssuances.map((issuance) => (
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

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="d-flex justify-content-center mt-3">
            <Pagination>
              <Pagination.First
                onClick={() => handlePageChange(1)}
                disabled={currentPage === 1}
              />
              <Pagination.Prev
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
              />

              {[...Array(totalPages)].map((_, index) => {
                const pageNumber = index + 1;
                // Show first page, last page, current page, and pages around current
                if (
                  pageNumber === 1 ||
                  pageNumber === totalPages ||
                  (pageNumber >= currentPage - 1 && pageNumber <= currentPage + 1)
                ) {
                  return (
                    <Pagination.Item
                      key={pageNumber}
                      active={pageNumber === currentPage}
                      onClick={() => handlePageChange(pageNumber)}
                    >
                      {pageNumber}
                    </Pagination.Item>
                  );
                } else if (
                  pageNumber === currentPage - 2 ||
                  pageNumber === currentPage + 2
                ) {
                  return <Pagination.Ellipsis key={pageNumber} disabled />;
                }
                return null;
              })}

              <Pagination.Next
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
              />
              <Pagination.Last
                onClick={() => handlePageChange(totalPages)}
                disabled={currentPage === totalPages}
              />
            </Pagination>
          </div>
        )}
      </Card.Body>
    </Card>
  );
};

export default KitIssuanceHistory;

