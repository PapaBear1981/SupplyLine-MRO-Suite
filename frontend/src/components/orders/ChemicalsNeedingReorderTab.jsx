import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Table, Button, Badge, Alert, Modal, Form, Row, Col } from 'react-bootstrap';
import { FaSync } from 'react-icons/fa';
import { toast } from 'react-toastify';
import { fetchChemicalsNeedingReorder, markChemicalAsOrdered } from '../../store/chemicalsSlice';
import { fetchOrders } from '../../store/ordersSlice';

const getStatusBadgeVariant = (status) => {
  switch (status) {
    case 'expired':
      return 'danger';
    case 'out_of_stock':
      return 'warning';
    case 'low_stock':
      return 'info';
    default:
      return 'secondary';
  }
};

const formatStatus = (status) => {
  return status.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase());
};

const ChemicalsNeedingReorderTab = () => {
  const dispatch = useDispatch();
  const { chemicalsNeedingReorder, loading } = useSelector((state) => state.chemicals);
  
  const [showOrderModal, setShowOrderModal] = useState(false);
  const [selectedChemical, setSelectedChemical] = useState(null);
  const [orderForm, setOrderForm] = useState({
    expected_delivery_date: '',
    notes: '',
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    dispatch(fetchChemicalsNeedingReorder());
  }, [dispatch]);

  const handleRefresh = () => {
    dispatch(fetchChemicalsNeedingReorder());
  };

  const handleOpenOrderModal = (chemical) => {
    setSelectedChemical(chemical);
    setOrderForm({
      expected_delivery_date: '',
      notes: '',
    });
    setShowOrderModal(true);
  };

  const handleCloseOrderModal = () => {
    setShowOrderModal(false);
    setSelectedChemical(null);
    setOrderForm({
      expected_delivery_date: '',
      notes: '',
    });
  };

  const handleOrderFormChange = (e) => {
    const { name, value } = e.target;
    setOrderForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmitOrder = async (e) => {
    e.preventDefault();
    
    if (!orderForm.expected_delivery_date) {
      toast.error('Please select an expected delivery date');
      return;
    }

    setSubmitting(true);
    try {
      await dispatch(markChemicalAsOrdered({
        id: selectedChemical.id,
        expected_delivery_date: orderForm.expected_delivery_date,
        notes: orderForm.notes,
      })).unwrap();
      
      toast.success('Chemical marked as ordered and procurement order created!');
      handleCloseOrderModal();
      
      // Refresh the orders list to show the new order
      dispatch(fetchOrders());
      dispatch(fetchChemicalsNeedingReorder());
    } catch (error) {
      toast.error(error.message || 'Failed to mark chemical as ordered');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <div>
          <strong>{Array.isArray(chemicalsNeedingReorder) ? chemicalsNeedingReorder.length : 0}</strong> chemical{(Array.isArray(chemicalsNeedingReorder) ? chemicalsNeedingReorder.length : 0) !== 1 ? 's' : ''} need{(Array.isArray(chemicalsNeedingReorder) ? chemicalsNeedingReorder.length : 0) === 1 ? 's' : ''} reordering
        </div>
        <Button variant="outline-primary" size="sm" onClick={handleRefresh}>
          <FaSync className="me-1" />Refresh
        </Button>
      </div>

      {loading ? (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : !Array.isArray(chemicalsNeedingReorder) || chemicalsNeedingReorder.length === 0 ? (
        <Alert variant="success">
          <i className="bi bi-check-circle-fill me-2"></i>
          No chemicals currently need reordering. All chemical inventory levels are adequate!
        </Alert>
      ) : (
        <div className="table-responsive">
          <Table hover bordered className="align-middle">
            <thead className="table-light">
              <tr>
                <th>Part Number</th>
                <th>Lot Number</th>
                <th>Description</th>
                <th>Manufacturer</th>
                <th>Status</th>
                <th>Reason</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {chemicalsNeedingReorder.map((chemical) => (
                <tr key={chemical.id}>
                  <td><strong>{chemical.part_number}</strong></td>
                  <td>{chemical.lot_number}</td>
                  <td>{chemical.description}</td>
                  <td>{chemical.manufacturer || '—'}</td>
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
                    <Button
                      variant="success"
                      size="sm"
                      onClick={() => handleOpenOrderModal(chemical)}
                    >
                      <i className="bi bi-cart-plus me-1"></i>
                      Order Now
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      )}

      {/* Order Modal */}
      <Modal show={showOrderModal} onHide={handleCloseOrderModal} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Order Chemical</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmitOrder}>
          <Modal.Body>
            {selectedChemical && (
              <>
                <Alert variant="info">
                  <strong>Chemical Details:</strong>
                  <ul className="mb-0 mt-2">
                    <li><strong>Part Number:</strong> {selectedChemical.part_number}</li>
                    <li><strong>Lot Number:</strong> {selectedChemical.lot_number}</li>
                    <li><strong>Description:</strong> {selectedChemical.description}</li>
                    <li><strong>Manufacturer:</strong> {selectedChemical.manufacturer || 'N/A'}</li>
                    <li><strong>Status:</strong> <Badge bg={getStatusBadgeVariant(selectedChemical.status)}>{formatStatus(selectedChemical.status)}</Badge></li>
                  </ul>
                </Alert>

                <Row>
                  <Col md={12}>
                    <Form.Group className="mb-3">
                      <Form.Label>Expected Delivery Date <span className="text-danger">*</span></Form.Label>
                      <Form.Control
                        type="date"
                        name="expected_delivery_date"
                        value={orderForm.expected_delivery_date}
                        onChange={handleOrderFormChange}
                        required
                      />
                      <Form.Text className="text-muted">
                        When do you expect this chemical to be delivered?
                      </Form.Text>
                    </Form.Group>
                  </Col>
                  <Col md={12}>
                    <Form.Group className="mb-3">
                      <Form.Label>Notes</Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={3}
                        name="notes"
                        value={orderForm.notes}
                        onChange={handleOrderFormChange}
                        placeholder="Add any additional notes about this order..."
                      />
                    </Form.Group>
                  </Col>
                </Row>

                <Alert variant="warning" className="mb-0">
                  <i className="bi bi-info-circle-fill me-2"></i>
                  <strong>Note:</strong> Marking this chemical as ordered will automatically create a procurement order that can be tracked in the "All Orders" tab.
                </Alert>
              </>
            )}
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleCloseOrderModal} disabled={submitting}>
              Cancel
            </Button>
            <Button variant="success" type="submit" disabled={submitting}>
              {submitting ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Creating Order...
                </>
              ) : (
                <>
                  <i className="bi bi-cart-check me-1"></i>
                  Create Order
                </>
              )}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </>
  );
};

export default ChemicalsNeedingReorderTab;

