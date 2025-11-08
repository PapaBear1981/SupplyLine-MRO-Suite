import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { Table, Button, Badge, Alert, Modal, Form } from 'react-bootstrap';
import { markChemicalAsOrdered, fetchChemicalsNeedingReorder } from '../../store/chemicalsSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const ChemicalsNeedingReorder = () => {
  const dispatch = useDispatch();
  const { chemicalsNeedingReorder, loading } = useSelector((state) => state.chemicals);
  const [showOrderModal, setShowOrderModal] = useState(false);
  const [selectedChemical, setSelectedChemical] = useState(null);
  const [expectedDeliveryDate, setExpectedDeliveryDate] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Format status for display
  const formatStatus = (status) => {
    return status
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  // Get status badge variant
  const getStatusBadgeVariant = (status) => {
    switch (status) {
      case 'available':
        return 'success';
      case 'low_stock':
        return 'warning';
      case 'out_of_stock':
        return 'danger';
      case 'expired':
        return 'dark';
      default:
        return 'secondary';
    }
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
      dispatch(fetchChemicalsNeedingReorder());
      setShowOrderModal(false);
    } catch (error) {
      console.error('Failed to mark chemical as ordered:', error);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading && !chemicalsNeedingReorder.length) {
    return <LoadingSpinner />;
  }

  return (
    <>
      {chemicalsNeedingReorder.length === 0 ? (
        <Alert variant="info">No chemicals currently need reordering.</Alert>
      ) : (
        <div className="table-responsive">
          <Table hover bordered className="align-middle">
            <thead>
              <tr>
                <th>Part Number</th>
                <th>Lot Number</th>
                <th>Description</th>
                <th>Manufacturer</th>
                <th>Requested Qty</th>
                <th>Status</th>
                <th>Reason</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {chemicalsNeedingReorder.map((chemical) => (
                <tr key={chemical.id}>
                  <td>{chemical.part_number}</td>
                  <td>{chemical.lot_number}</td>
                  <td>{chemical.description}</td>
                  <td>{chemical.manufacturer}</td>
                  <td>
                    {chemical.requested_quantity ? (
                      <strong>{chemical.requested_quantity} {chemical.unit}</strong>
                    ) : (
                      <span className="text-muted">Not specified</span>
                    )}
                  </td>
                  <td>
                    <Badge bg={getStatusBadgeVariant(chemical.status)}>
                      {formatStatus(chemical.status)}
                    </Badge>
                  </td>
                  <td>
                    {chemical.status === 'expired' ? 'Expired' :
                     chemical.status === 'out_of_stock' ? 'Out of Stock' :
                     'Low Stock'}
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
                      <Button
                        variant="success"
                        size="sm"
                        onClick={() => handleOpenOrderModal(chemical)}
                      >
                        Mark as Ordered
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      )}

      {/* Order Modal */}
      <Modal show={showOrderModal} onHide={() => setShowOrderModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Mark Chemical as Ordered</Modal.Title>
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

export default ChemicalsNeedingReorder;
