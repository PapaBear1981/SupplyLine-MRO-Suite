import { useEffect, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Alert,
  Button,
  Card,
  Col,
  Form,
  InputGroup,
  Modal,
  Row,
  Spinner,
} from 'react-bootstrap';
import { FaBarcode, FaSearch, FaUndo, FaTimes } from 'react-icons/fa';
import api from '../../services/api';
import {
  fetchChemicalReturns,
  lookupChemicalReturn,
  submitChemicalReturn,
} from '../../store/chemicalsSlice';
import ChemicalBarcode from './ChemicalBarcode';
import ChemicalReturnHistory from './ChemicalReturnHistory';
import './ChemicalReturnModal.css';

const ChemicalReturnModal = ({ show, onHide }) => {
  const dispatch = useDispatch();

  const {
    returnLookup,
    returnLookupLoading,
    returnLookupError,
    returnSubmitting,
    returnSubmitError,
    lastReturn,
    returns,
    returnsLoading,
  } = useSelector((state) => state.chemicals);

  const [barcodeValue, setBarcodeValue] = useState('');
  const [warehouses, setWarehouses] = useState([]);
  const [warehousesLoading, setWarehousesLoading] = useState(false);
  const [warehousesError, setWarehousesError] = useState(null);
  const [formData, setFormData] = useState({
    quantity: '',
    warehouse_id: '',
    location: '',
    notes: '',
  });
  const [validated, setValidated] = useState(false);
  const [showBarcodeModal, setShowBarcodeModal] = useState(false);

  const chemicalId = returnLookup?.chemical?.id;
  const remainingQuantity = returnLookup?.remaining_quantity ?? null;
  const returnHistory = useMemo(
    () => (chemicalId != null ? returns[String(chemicalId)] || [] : []),
    [returns, chemicalId]
  );

  useEffect(() => {
    if (show) {
      const loadWarehouses = async () => {
        setWarehousesLoading(true);
        setWarehousesError(null);
        try {
          const response = await api.get('/warehouses');
          setWarehouses(Array.isArray(response.data) ? response.data : response.data?.warehouses || []);
        } catch (error) {
          console.error('Failed to load warehouses', error);
          setWarehousesError('Unable to load warehouses. Please try again.');
        } finally {
          setWarehousesLoading(false);
        }
      };

      loadWarehouses();
    }
  }, [show]);

  useEffect(() => {
    if (returnLookup?.chemical?.id) {
      setFormData((prev) => ({
        ...prev,
        quantity: returnLookup.remaining_quantity ?? '',
        warehouse_id: returnLookup.default_warehouse_id || '',
        location: returnLookup.default_location || '',
        notes: '',
      }));
      dispatch(fetchChemicalReturns(returnLookup.chemical.id));
    }
  }, [dispatch, returnLookup]);

  useEffect(() => {
    if (lastReturn && returnLookup?.chemical) {
      setShowBarcodeModal(true);
    }
  }, [lastReturn, returnLookup]);

  const handleLookup = (event) => {
    event.preventDefault();
    if (!barcodeValue.trim()) {
      return;
    }
    dispatch(lookupChemicalReturn({ code: barcodeValue.trim() }));
  };

  const handleFormChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    const form = event.currentTarget;

    if (form.checkValidity() === false) {
      setValidated(true);
      return;
    }

    const quantity = parseInt(formData.quantity, 10);
    if (Number.isNaN(quantity) || quantity <= 0) {
      return;
    }

    if (remainingQuantity !== null && quantity > remainingQuantity) {
      return;
    }

    if (!chemicalId) {
      return;
    }

    const payload = {
      issuance_id: returnLookup?.issuance?.id,
      quantity,
      warehouse_id: formData.warehouse_id ? parseInt(formData.warehouse_id, 10) : null,
      location: formData.location,
      notes: formData.notes,
    };

    dispatch(submitChemicalReturn({ chemicalId, data: payload })).then((action) => {
      if (action.meta.requestStatus === 'fulfilled') {
        setValidated(false);
      }
    });
  };

  const handleReset = () => {
    setBarcodeValue('');
    setFormData({ quantity: '', warehouse_id: '', location: '', notes: '' });
    setValidated(false);
  };

  const handleClose = () => {
    handleReset();
    onHide();
  };

  const handleReturnAll = () => {
    if (remainingQuantity !== null) {
      setFormData((prev) => ({
        ...prev,
        quantity: remainingQuantity,
      }));
      // Scroll to quantity field
      const quantityField = document.getElementById('return-quantity-field');
      if (quantityField) {
        quantityField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        quantityField.focus();
      }
    }
  };

  return (
    <>
      <Modal show={show} onHide={handleClose} size="xl" className="chemical-return-modal">
        <Modal.Header closeButton className="bg-primary text-white">
          <Modal.Title>
            <FaBarcode className="me-2" />
            Return Issued Chemical
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Row className="g-4">
            <Col lg={4}>
              <Card className="shadow-sm h-100 scan-card">
                <Card.Header className="bg-light">
                  <h5 className="mb-0">
                    <FaBarcode className="me-2" /> Scan Issued Lot
                  </h5>
                </Card.Header>
                <Card.Body>
                  <Form onSubmit={handleLookup}>
                    <Form.Group className="mb-3">
                      <Form.Label>Barcode or Lot Code</Form.Label>
                      <InputGroup>
                        <InputGroup.Text>
                          <FaSearch />
                        </InputGroup.Text>
                        <Form.Control
                          type="text"
                          value={barcodeValue}
                          placeholder="Scan or enter barcode"
                          onChange={(event) => setBarcodeValue(event.target.value)}
                          disabled={returnLookupLoading}
                          autoFocus
                        />
                      </InputGroup>
                      <Form.Text className="text-muted">
                        Use a scanner to populate this field automatically.
                      </Form.Text>
                    </Form.Group>
                    <div className="d-flex justify-content-between">
                      <Button
                        type="submit"
                        variant="primary"
                        disabled={returnLookupLoading || !barcodeValue.trim()}
                        className="action-button"
                      >
                        {returnLookupLoading ? (
                          <>
                            <Spinner animation="border" size="sm" className="me-2" />
                            Searching...
                          </>
                        ) : (
                          <>
                            <FaSearch className="me-2" />
                            Lookup
                          </>
                        )}
                      </Button>
                      <Button
                        type="button"
                        variant="outline-secondary"
                        onClick={handleReset}
                        className="action-button"
                      >
                        <FaUndo className="me-2" />
                        Reset
                      </Button>
                    </div>
                  </Form>

                  {returnLookupError && (
                    <Alert variant="danger" className="mt-3 alert-animated">
                      {returnLookupError.message || 'Failed to locate issued lot'}
                    </Alert>
                  )}

                  {warehousesError && (
                    <Alert variant="warning" className="mt-3 alert-animated">
                      {warehousesError}
                    </Alert>
                  )}

                  {!returnLookup && !returnLookupError && !returnLookupLoading && (
                    <Alert variant="info" className="mt-3 alert-animated">
                      Scan an issued lot barcode to begin the return process.
                    </Alert>
                  )}
                </Card.Body>
              </Card>
            </Col>

            <Col lg={8}>
              {returnLookup && returnLookup.chemical ? (
                <Card className="shadow-sm h-100 details-card">
                  <Card.Header className="bg-light">
                    <div className="d-flex justify-content-between align-items-center">
                      <h5 className="mb-0">
                        {returnLookup.chemical.part_number} — {returnLookup.chemical.lot_number}
                      </h5>
                      <span className="text-muted">
                        Issued Quantity: {returnLookup.issuance?.quantity || '—'}
                      </span>
                    </div>
                  </Card.Header>
                  <Card.Body>
                    {remainingQuantity === 0 && (
                      <Alert variant="info" className="alert-animated">
                        All issued quantity for this lot has been returned.
                      </Alert>
                    )}

                    {lastReturn && (
                      <Alert variant="success" className="alert-animated">
                        Return recorded successfully. A barcode label will open for printing.
                      </Alert>
                    )}

                    {returnSubmitError && (
                      <Alert variant="danger" className="alert-animated">
                        {returnSubmitError.message || 'Failed to complete return'}.
                      </Alert>
                    )}

                    <Row className="mb-4">
                      <Col md={6}>
                        <h6>Chemical Information</h6>
                        <p className="mb-1">
                          <strong>Description:</strong> {returnLookup.chemical.description || 'N/A'}
                        </p>
                        <p className="mb-1">
                          <strong>Warehouse:</strong> {returnLookup.chemical.warehouse_name || 'N/A'}
                        </p>
                        <p className="mb-1">
                          <strong>Location:</strong> {returnLookup.chemical.location || 'N/A'}
                        </p>
                      </Col>
                      <Col md={6}>
                        <h6>Issuance Summary</h6>
                        <p className="mb-1">
                          <strong>Issued By:</strong> {returnLookup.issuance?.user_name || 'Unknown'}
                        </p>
                        <p className="mb-1">
                          <strong>Issued For:</strong> {returnLookup.issuance?.hangar || 'N/A'}
                        </p>
                        <p className="mb-1">
                          <strong>Remaining to Return:</strong>{' '}
                          <span className={`badge ${remainingQuantity === 0 ? 'bg-success' : 'bg-warning text-dark'} quantity-badge`}>
                            {remainingQuantity ?? '—'}
                          </span>
                        </p>
                      </Col>
                    </Row>

                    <Form noValidate validated={validated} onSubmit={handleSubmit}>
                      <Row className="g-3">
                        <Col md={4}>
                          <Form.Group controlId="return-quantity-field">
                            <Form.Label>Quantity to Return*</Form.Label>
                            <InputGroup>
                              <Form.Control
                                type="number"
                                name="quantity"
                                value={formData.quantity}
                                min={1}
                                max={remainingQuantity ?? undefined}
                                disabled={returnSubmitting || remainingQuantity === 0}
                                required
                                onChange={handleFormChange}
                              />
                              {remainingQuantity > 0 && (
                                <Button
                                  variant="outline-primary"
                                  onClick={() => setFormData({ ...formData, quantity: remainingQuantity.toString() })}
                                  disabled={returnSubmitting}
                                  title="Return all remaining quantity"
                                  className="action-button"
                                >
                                  All
                                </Button>
                              )}
                            </InputGroup>
                            <Form.Control.Feedback type="invalid">
                              Please enter a valid quantity.
                            </Form.Control.Feedback>
                          </Form.Group>
                        </Col>
                        <Col md={4}>
                          <Form.Group controlId="returnWarehouse">
                            <Form.Label>Return Warehouse</Form.Label>
                            <Form.Select
                              name="warehouse_id"
                              value={formData.warehouse_id}
                              onChange={handleFormChange}
                              disabled={returnSubmitting || warehousesLoading}
                            >
                              <option value="">Select warehouse...</option>
                              {warehouses.map((warehouse) => (
                                <option key={warehouse.id} value={warehouse.id}>
                                  {warehouse.name}
                                </option>
                              ))}
                            </Form.Select>
                          </Form.Group>
                        </Col>
                        <Col md={4}>
                          <Form.Group controlId="returnLocation">
                            <Form.Label>Return Location</Form.Label>
                            <Form.Control
                              type="text"
                              name="location"
                              placeholder="Shelf, bay, etc."
                              value={formData.location}
                              onChange={handleFormChange}
                              disabled={returnSubmitting}
                            />
                          </Form.Group>
                        </Col>
                        <Col md={12}>
                          <Form.Group controlId="returnNotes">
                            <Form.Label>Notes</Form.Label>
                            <Form.Control
                              as="textarea"
                              rows={3}
                              name="notes"
                              value={formData.notes}
                              onChange={handleFormChange}
                              placeholder="Add any relevant details about this return"
                              disabled={returnSubmitting}
                            />
                          </Form.Group>
                        </Col>
                      </Row>

                      <div className="d-flex justify-content-between align-items-center mt-4">
                        {remainingQuantity > 0 && (
                          <Button
                            variant="outline-secondary"
                            className="btn-return-all"
                            onClick={handleReturnAll}
                            disabled={returnSubmitting}
                          >
                            <FaUndo className="me-2" />
                            Return All ({remainingQuantity})
                          </Button>
                        )}
                        <div className="ms-auto">
                          <Button
                            type="submit"
                            variant="success"
                            disabled={returnSubmitting || remainingQuantity === 0}
                            className="action-button"
                          >
                            {returnSubmitting ? (
                              <>
                                <Spinner animation="border" size="sm" className="me-2" />
                                Recording Return...
                              </>
                            ) : (
                              <>
                                <FaBarcode className="me-2" />
                                Complete Return
                              </>
                            )}
                          </Button>
                        </div>
                      </div>
                    </Form>
                  </Card.Body>
                </Card>
              ) : null}
            </Col>
          </Row>

          {chemicalId && (
            <div className="mt-4">
              <ChemicalReturnHistory returns={returnHistory} loading={returnsLoading} />
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose} className="action-button">
            <FaTimes className="me-2" />
            Close
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Barcode Modal */}
      {showBarcodeModal && lastReturn && returnLookup?.chemical && (
        <ChemicalBarcode
          chemical={returnLookup.chemical}
          show={showBarcodeModal}
          onHide={() => setShowBarcodeModal(false)}
        />
      )}
    </>
  );
};

export default ChemicalReturnModal;

