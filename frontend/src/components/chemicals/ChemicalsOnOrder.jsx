import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { Table, Button, Alert, Modal, Form } from 'react-bootstrap';
import { markChemicalAsDelivered, fetchChemicalsOnOrder, fetchChemicals } from '../../store/chemicalsSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const ChemicalsOnOrder = () => {
  const dispatch = useDispatch();
  const { chemicalsOnOrder, loading } = useSelector((state) => state.chemicals);
  const [showDeliveryModal, setShowDeliveryModal] = useState(false);
  const [selectedChemical, setSelectedChemical] = useState(null);
  const [receivedQuantity, setReceivedQuantity] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Open the delivery modal
  const openDeliveryModal = (chemical) => {
    setSelectedChemical(chemical);
    setReceivedQuantity('');
    setShowDeliveryModal(true);
  };

  // Close the delivery modal
  const closeDeliveryModal = () => {
    setShowDeliveryModal(false);
    setSelectedChemical(null);
    setReceivedQuantity('');
  };

  // Handle marking a chemical as delivered
  const handleMarkAsDelivered = async () => {
    if (!selectedChemical || !receivedQuantity || parseFloat(receivedQuantity) <= 0) {
      alert('Please enter a valid quantity greater than 0');
      return;
    }

    setSubmitting(true);
    try {
      await dispatch(markChemicalAsDelivered({
        id: selectedChemical.id,
        receivedQuantity: parseFloat(receivedQuantity)
      })).unwrap();

      // Refresh the lists
      dispatch(fetchChemicalsOnOrder());
      // Also refresh the main chemicals list to ensure the delivered chemical appears there
      dispatch(fetchChemicals());

      // Close the modal
      closeDeliveryModal();
    } catch (error) {
      console.error('Failed to mark chemical as delivered:', error);
    } finally {
      setSubmitting(false);
    }
  };

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  if (loading && !chemicalsOnOrder.length) {
    return <LoadingSpinner />;
  }

  return (
    <>
      {chemicalsOnOrder.length === 0 ? (
        <Alert variant="info">No chemicals are currently on order.</Alert>
      ) : (
        <div className="table-responsive">
          <Table hover bordered className="align-middle">
            <thead className="bg-light">
              <tr>
                <th>Part Number</th>
                <th>Lot Number</th>
                <th>Description</th>
                <th>Manufacturer</th>
                <th>Order Date</th>
                <th>Expected Delivery</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {chemicalsOnOrder.map((chemical) => (
                <tr key={chemical.id}>
                  <td>{chemical.part_number}</td>
                  <td>{chemical.lot_number}</td>
                  <td>{chemical.description}</td>
                  <td>{chemical.manufacturer}</td>
                  <td>{formatDate(chemical.reorder_date)}</td>
                  <td>{formatDate(chemical.expected_delivery_date)}</td>
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
                        onClick={() => openDeliveryModal(chemical)}
                      >
                        Mark as Delivered
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      )}

      {/* Delivery Modal */}
      <Modal show={showDeliveryModal} onHide={closeDeliveryModal} centered>
        <Modal.Header closeButton>
          <Modal.Title>Mark Chemical as Delivered</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedChemical && (
            <>
              <p>
                <strong>Part Number:</strong> {selectedChemical.part_number}
                <br />
                <strong>Lot Number:</strong> {selectedChemical.lot_number}
                <br />
                <strong>Description:</strong> {selectedChemical.description}
              </p>
              <Form.Group className="mb-3">
                <Form.Label>Received Quantity ({selectedChemical.unit})</Form.Label>
                <Form.Control
                  type="number"
                  min="0.1"
                  step="0.1"
                  value={receivedQuantity}
                  onChange={(e) => setReceivedQuantity(e.target.value)}
                  placeholder={`Enter quantity in ${selectedChemical.unit}`}
                  required
                />
                <Form.Text className="text-muted">
                  Enter the quantity received in {selectedChemical.unit}
                </Form.Text>
              </Form.Group>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={closeDeliveryModal}>
            Cancel
          </Button>
          <Button
            variant="success"
            onClick={handleMarkAsDelivered}
            disabled={submitting || !receivedQuantity || parseFloat(receivedQuantity) <= 0}
          >
            {submitting ? 'Processing...' : 'Mark as Delivered'}
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default ChemicalsOnOrder;
