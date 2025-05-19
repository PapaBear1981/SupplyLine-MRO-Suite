import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { Table, Button, Badge, Alert, Modal, Form } from 'react-bootstrap';
import { markChemicalAsOrdered, fetchChemicalsExpiringSoon } from '../../store/chemicalsSlice';
import LoadingSpinner from '../common/LoadingSpinner';
import { formatDate, getDaysFromToday } from '../../utils/dateUtils';

const ChemicalsExpiringSoon = () => {
  const dispatch = useDispatch();
  const { chemicalsExpiringSoon, loading } = useSelector((state) => state.chemicals);
  const [showOrderModal, setShowOrderModal] = useState(false);
  const [selectedChemical, setSelectedChemical] = useState(null);
  const [expectedDeliveryDate, setExpectedDeliveryDate] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Using standardized date formatting utilities from dateUtils.js

  // Get badge variant based on days until expiration
  const getExpirationBadgeVariant = (days) => {
    if (days <= 7) return 'danger';
    if (days <= 14) return 'warning';
    return 'info';
  };

  // Handle opening the order modal
  const handleOpenOrderModal = (chemical) => {
    setSelectedChemical(chemical);
    setExpectedDeliveryDate('');
    setShowOrderModal(true);
  };

  // Handle marking a chemical as ordered
  const handleMarkAsOrdered = async () => {
    if (!selectedChemical || !expectedDeliveryDate) return;

    setSubmitting(true);
    try {
      await dispatch(markChemicalAsOrdered({
        id: selectedChemical.id,
        expectedDeliveryDate
      })).unwrap();

      // Refresh the list
      dispatch(fetchChemicalsExpiringSoon());
      setShowOrderModal(false);
    } catch (error) {
      console.error('Failed to mark chemical as ordered:', error);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading && !chemicalsExpiringSoon.length) {
    return <LoadingSpinner />;
  }

  return (
    <>
      {chemicalsExpiringSoon.length === 0 ? (
        <Alert variant="info">No chemicals are expiring soon.</Alert>
      ) : (
        <div className="table-responsive">
          <Table hover bordered className="align-middle">
            <thead className="bg-light">
              <tr>
                <th>Part Number</th>
                <th>Lot Number</th>
                <th>Description</th>
                <th>Manufacturer</th>
                <th>Expiration Date</th>
                <th>Days Until Expiration</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {chemicalsExpiringSoon.map((chemical) => {
                const daysUntilExpiration = getDaysFromToday(chemical.expiration_date);
                return (
                  <tr key={chemical.id}>
                    <td>{chemical.part_number}</td>
                    <td>{chemical.lot_number}</td>
                    <td>{chemical.description}</td>
                    <td>{chemical.manufacturer}</td>
                    <td>{formatDate(chemical.expiration_date)}</td>
                    <td>
                      <Badge bg={getExpirationBadgeVariant(daysUntilExpiration)}>
                        {daysUntilExpiration} days
                      </Badge>
                    </td>
                    <td>
                      <div className="d-flex gap-2">
                        <Button
                          as={Link}
                          to={`/chemicals/${chemical.id}`}
                          variant="primary"
                          size="sm"
                        >
                          View
                        </Button>
                        {chemical.reorder_status !== 'ordered' && (
                          <Button
                            variant="success"
                            size="sm"
                            onClick={() => handleOpenOrderModal(chemical)}
                          >
                            Reorder
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </Table>
        </div>
      )}

      {/* Order Modal */}
      <Modal show={showOrderModal} onHide={() => setShowOrderModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Reorder Chemical</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedChemical && (
            <>
              <p>
                <strong>Part Number:</strong> {selectedChemical.part_number}
              </p>
              <p>
                <strong>Lot Number:</strong> {selectedChemical.lot_number}
              </p>
              <p>
                <strong>Description:</strong> {selectedChemical.description}
              </p>
              <p>
                <strong>Expiration Date:</strong> {formatDate(selectedChemical.expiration_date)}
              </p>
              <Form.Group className="mb-3">
                <Form.Label>Expected Delivery Date</Form.Label>
                <Form.Control
                  type="date"
                  value={expectedDeliveryDate}
                  onChange={(e) => setExpectedDeliveryDate(e.target.value)}
                  required
                />
              </Form.Group>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowOrderModal(false)}>
            Cancel
          </Button>
          <Button
            variant="success"
            onClick={handleMarkAsOrdered}
            disabled={!expectedDeliveryDate || submitting}
          >
            {submitting ? 'Processing...' : 'Mark as Ordered'}
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default ChemicalsExpiringSoon;
