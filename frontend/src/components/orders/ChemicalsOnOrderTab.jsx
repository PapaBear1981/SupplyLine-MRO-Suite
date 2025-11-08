import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Table, Button, Badge, Alert, Modal, Form, Row, Col } from 'react-bootstrap';
import { FaSync } from 'react-icons/fa';
import { toast } from 'react-toastify';
import { fetchChemicalsOnOrder, markChemicalAsDelivered } from '../../store/chemicalsSlice';
import { fetchOrders } from '../../store/ordersSlice';
import { formatDate } from '../../utils/dateUtils';

const ChemicalsOnOrderTab = () => {
  const dispatch = useDispatch();
  const { chemicalsOnOrder, loading } = useSelector((state) => state.chemicals);
  
  const [showDeliveryModal, setShowDeliveryModal] = useState(false);
  const [selectedChemical, setSelectedChemical] = useState(null);
  const [deliveryForm, setDeliveryForm] = useState({
    received_quantity: '',
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    dispatch(fetchChemicalsOnOrder());
  }, [dispatch]);

  const handleRefresh = () => {
    dispatch(fetchChemicalsOnOrder());
  };

  const handleOpenDeliveryModal = (chemical) => {
    setSelectedChemical(chemical);
    setDeliveryForm({
      received_quantity: chemical.quantity || '',
    });
    setShowDeliveryModal(true);
  };

  const handleCloseDeliveryModal = () => {
    setShowDeliveryModal(false);
    setSelectedChemical(null);
    setDeliveryForm({
      received_quantity: '',
    });
  };

  const handleDeliveryFormChange = (e) => {
    const { name, value } = e.target;
    setDeliveryForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmitDelivery = async (e) => {
    e.preventDefault();
    
    setSubmitting(true);
    try {
      await dispatch(markChemicalAsDelivered({
        id: selectedChemical.id,
        received_quantity: deliveryForm.received_quantity ? parseFloat(deliveryForm.received_quantity) : null,
      })).unwrap();
      
      toast.success('Chemical marked as delivered and procurement order closed!');
      handleCloseDeliveryModal();
      
      // Refresh the lists
      dispatch(fetchOrders());
      dispatch(fetchChemicalsOnOrder());
    } catch (error) {
      toast.error(error.message || 'Failed to mark chemical as delivered');
    } finally {
      setSubmitting(false);
    }
  };

  const isOverdue = (expectedDate) => {
    if (!expectedDate) return false;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const expected = new Date(expectedDate);
    expected.setHours(0, 0, 0, 0);
    return expected < today;
  };

  const getDaysOverdue = (expectedDate) => {
    if (!expectedDate) return 0;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const expected = new Date(expectedDate);
    expected.setHours(0, 0, 0, 0);
    const diffTime = today - expected;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <div>
          <strong>{chemicalsOnOrder.length}</strong> chemical{chemicalsOnOrder.length !== 1 ? 's' : ''} on order
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
      ) : chemicalsOnOrder.length === 0 ? (
        <Alert variant="info">
          <i className="bi bi-info-circle-fill me-2"></i>
          No chemicals are currently on order.
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
                <th>Order Date</th>
                <th>Expected Delivery</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {chemicalsOnOrder.map((chemical) => {
                const overdue = isOverdue(chemical.expected_delivery_date);
                const daysOverdue = getDaysOverdue(chemical.expected_delivery_date);
                
                return (
                  <tr key={chemical.id} className={overdue ? 'table-danger' : ''}>
                    <td><strong>{chemical.part_number}</strong></td>
                    <td>{chemical.lot_number}</td>
                    <td>{chemical.description}</td>
                    <td>{chemical.manufacturer || '—'}</td>
                    <td>{chemical.reorder_date ? formatDate(chemical.reorder_date) : '—'}</td>
                    <td>
                      {chemical.expected_delivery_date ? (
                        <>
                          {formatDate(chemical.expected_delivery_date)}
                          {overdue && (
                            <Badge bg="danger" className="ms-2">
                              {daysOverdue} day{daysOverdue !== 1 ? 's' : ''} overdue
                            </Badge>
                          )}
                        </>
                      ) : '—'}
                    </td>
                    <td>
                      <Badge bg={overdue ? 'danger' : 'primary'}>
                        {overdue ? 'Overdue' : 'On Order'}
                      </Badge>
                    </td>
                    <td>
                      <Button
                        variant="success"
                        size="sm"
                        onClick={() => handleOpenDeliveryModal(chemical)}
                      >
                        <i className="bi bi-check-circle me-1"></i>
                        Mark Delivered
                      </Button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </Table>
        </div>
      )}

      {/* Delivery Modal */}
      <Modal show={showDeliveryModal} onHide={handleCloseDeliveryModal} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Mark Chemical as Delivered</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmitDelivery}>
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
                    <li><strong>Order Date:</strong> {selectedChemical.reorder_date ? formatDate(selectedChemical.reorder_date) : 'N/A'}</li>
                    <li><strong>Expected Delivery:</strong> {selectedChemical.expected_delivery_date ? formatDate(selectedChemical.expected_delivery_date) : 'N/A'}</li>
                  </ul>
                </Alert>

                <Row>
                  <Col md={12}>
                    <Form.Group className="mb-3">
                      <Form.Label>Received Quantity (Optional)</Form.Label>
                      <Form.Control
                        type="number"
                        step="0.01"
                        name="received_quantity"
                        value={deliveryForm.received_quantity}
                        onChange={handleDeliveryFormChange}
                        placeholder="Enter quantity received (if different from ordered)"
                      />
                      <Form.Text className="text-muted">
                        Leave blank to keep the current quantity ({selectedChemical.quantity || 0})
                      </Form.Text>
                    </Form.Group>
                  </Col>
                </Row>

                <Alert variant="warning" className="mb-0">
                  <i className="bi bi-info-circle-fill me-2"></i>
                  <strong>Note:</strong> Marking this chemical as delivered will:
                  <ul className="mb-0 mt-2">
                    <li>Update the chemical status to "available"</li>
                    <li>Clear the reorder status</li>
                    <li>Close the associated procurement order</li>
                    <li>Add the chemical back to active inventory</li>
                  </ul>
                </Alert>
              </>
            )}
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleCloseDeliveryModal} disabled={submitting}>
              Cancel
            </Button>
            <Button variant="success" type="submit" disabled={submitting}>
              {submitting ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Processing...
                </>
              ) : (
                <>
                  <i className="bi bi-check-circle me-1"></i>
                  Mark as Delivered
                </>
              )}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </>
  );
};

export default ChemicalsOnOrderTab;

