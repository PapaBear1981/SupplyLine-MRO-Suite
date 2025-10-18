import { useState, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { Table, Button, Alert, Modal, Form, Badge, InputGroup, FormControl, Dropdown } from 'react-bootstrap';
import { markChemicalAsDelivered, fetchChemicalsOnOrder, fetchChemicals } from '../../store/chemicalsSlice';
import LoadingSpinner from '../common/LoadingSpinner';
import { getDaysFromToday } from '../../utils/dateUtils';

const ChemicalsOnOrder = () => {
  const dispatch = useDispatch();
  const { chemicalsOnOrder, loading } = useSelector((state) => state.chemicals);
  const [showDeliveryModal, setShowDeliveryModal] = useState(false);
  const [selectedChemical, setSelectedChemical] = useState(null);
  const [receivedQuantity, setReceivedQuantity] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [filterOverdueOnly, setFilterOverdueOnly] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

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

  // Check if a chemical is overdue (expected delivery date is in the past)
  const isOverdue = (chemical) => {
    if (!chemical.expected_delivery_date) return false;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const deliveryDate = new Date(chemical.expected_delivery_date);
    deliveryDate.setHours(0, 0, 0, 0);
    return deliveryDate < today;
  };

  // Get the number of days overdue
  const getDaysOverdue = (chemical) => {
    if (!chemical.expected_delivery_date) return 0;
    const daysRemaining = getDaysFromToday(chemical.expected_delivery_date);
    return typeof daysRemaining === 'number' ? Math.abs(daysRemaining) : 0;
  };

  // Get badge variant based on days overdue
  const getOverdueBadgeVariant = (daysOverdue) => {
    if (daysOverdue > 14) return 'danger';
    if (daysOverdue > 7) return 'warning';
    return 'info';
  };

  // Filter and sort chemicals
  const filteredChemicals = useMemo(() => {
    let filtered = [...chemicalsOnOrder];

    // Apply search filter if search term exists
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase().trim();
      filtered = filtered.filter(chemical =>
        chemical.part_number.toLowerCase().includes(term) ||
        chemical.lot_number.toLowerCase().includes(term) ||
        chemical.description.toLowerCase().includes(term) ||
        chemical.manufacturer.toLowerCase().includes(term)
      );
    }

    // Apply overdue filter if enabled
    if (filterOverdueOnly) {
      filtered = filtered.filter(chemical => isOverdue(chemical));
    }

    // Sort by overdue status (overdue items first) and then by days overdue (most overdue first)
    return filtered.sort((a, b) => {
      const aOverdue = isOverdue(a);
      const bOverdue = isOverdue(b);

      if (aOverdue && !bOverdue) return -1;
      if (!aOverdue && bOverdue) return 1;

      if (aOverdue && bOverdue) {
        return getDaysOverdue(b) - getDaysOverdue(a); // Most overdue first
      }

      return 0;
    });
  }, [chemicalsOnOrder, searchTerm, filterOverdueOnly]);

  // Count overdue chemicals
  const overdueCount = useMemo(() => {
    return chemicalsOnOrder.filter(chemical => isOverdue(chemical)).length;
  }, [chemicalsOnOrder]);

  if (loading && !chemicalsOnOrder.length) {
    return <LoadingSpinner />;
  }

  return (
    <>
      {chemicalsOnOrder.length === 0 ? (
        <Alert variant="info">No chemicals are currently on order.</Alert>
      ) : (
        <>
          {/* Filter and search controls */}
          <div className="d-flex flex-wrap justify-content-between align-items-center mb-3 gap-2">
            <div className="d-flex align-items-center">
              {overdueCount > 0 && (
                <Alert variant="warning" className="d-flex align-items-center py-2 px-3 mb-0 me-3">
                  <i className="bi bi-exclamation-triangle-fill me-2"></i>
                  <span>
                    <strong>{overdueCount}</strong> chemical{overdueCount !== 1 ? 's' : ''} {overdueCount !== 1 ? 'are' : 'is'} past expected delivery date
                  </span>
                </Alert>
              )}

              <Form.Check
                type="switch"
                id="overdue-filter"
                label="Show only overdue deliveries"
                checked={filterOverdueOnly}
                onChange={(e) => setFilterOverdueOnly(e.target.checked)}
                className="me-3"
              />
            </div>

            <InputGroup style={{ maxWidth: '300px' }}>
              <FormControl
                placeholder="Search chemicals..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              {searchTerm && (
                <Button
                  variant="outline-secondary"
                  onClick={() => setSearchTerm('')}
                >
                  <i className="bi bi-x"></i>
                </Button>
              )}
            </InputGroup>
          </div>

          {filteredChemicals.length === 0 ? (
            <Alert variant="info">
              No chemicals match your current filters. {filterOverdueOnly && 'Try disabling the "Show only overdue deliveries" filter.'}
            </Alert>
          ) : (
            <div className="table-responsive">
              <Table hover bordered className="align-middle">
                <thead>
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
                  {filteredChemicals.map((chemical) => {
                    const chemicalIsOverdue = isOverdue(chemical);
                    const daysOverdue = getDaysOverdue(chemical);

                    return (
                      <tr
                        key={chemical.id}
                        className={chemicalIsOverdue ? 'table-danger' : ''}
                      >
                        <td>{chemical.part_number}</td>
                        <td>{chemical.lot_number}</td>
                        <td>{chemical.description}</td>
                        <td>{chemical.manufacturer}</td>
                        <td>{formatDate(chemical.reorder_date)}</td>
                        <td>
                          {formatDate(chemical.expected_delivery_date)}
                          {chemicalIsOverdue && (
                            <i className="bi bi-exclamation-triangle-fill text-danger ms-2"></i>
                          )}
                        </td>
                        <td>
                          {chemicalIsOverdue ? (
                            <Badge
                              bg={getOverdueBadgeVariant(daysOverdue)}
                              className="d-flex align-items-center"
                            >
                              <i className="bi bi-clock-history me-1"></i>
                              {daysOverdue} {daysOverdue === 1 ? 'day' : 'days'} overdue
                            </Badge>
                          ) : (
                            <Badge bg="success">On Schedule</Badge>
                          )}
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
                              onClick={() => openDeliveryModal(chemical)}
                            >
                              Mark as Delivered
                            </Button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </Table>
            </div>
          )}
        </>
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
