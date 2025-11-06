import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { Button, Card, Row, Col, Badge, Alert, Tab, Tabs, Form, Modal } from 'react-bootstrap';
import {
  fetchChemicalById,
  fetchChemicalIssuances,
  fetchChemicalReturns,
  archiveChemical,
} from '../store/chemicalsSlice';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ChemicalIssuanceHistory from '../components/chemicals/ChemicalIssuanceHistory';
import ChemicalReturnHistory from '../components/chemicals/ChemicalReturnHistory';
import ChemicalBarcode from '../components/chemicals/ChemicalBarcode';
import ConfirmModal from '../components/common/ConfirmModal';

const ChemicalDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const {
    currentChemical,
    loading,
    error,
    issuances,
    issuanceLoading,
    returns,
    returnsLoading,
  } = useSelector((state) => state.chemicals);
  const { user } = useSelector((state) => state.auth);
  const isAuthorized = user?.is_admin || user?.department === 'Materials';

  // State for modals
  const [showArchiveModal, setShowArchiveModal] = useState(false);
  const [showBarcodeModal, setShowBarcodeModal] = useState(false);
  const [archiveReason, setArchiveReason] = useState('');
  const [archiveCustomReason, setArchiveCustomReason] = useState('');

  useEffect(() => {
    if (id) {
      dispatch(fetchChemicalById(id));
      dispatch(fetchChemicalIssuances(id));
      dispatch(fetchChemicalReturns(id));
    }
  }, [dispatch, id]);

  if (loading && !currentChemical) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <Alert variant="danger">{error.message}</Alert>;
  }

  if (!currentChemical) {
    return <Alert variant="warning">Chemical not found</Alert>;
  }

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

  // Format status for display
  const formatStatus = (status) => {
    return status
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  // Handle archive button click
  const handleArchiveClick = () => {
    setArchiveReason('');
    setArchiveCustomReason('');
    setShowArchiveModal(true);
  };

  // Handle archive confirmation
  const handleArchiveConfirm = () => {
    let reason = archiveReason;

    // If "other" is selected, use the custom reason
    if (archiveReason === 'other' && archiveCustomReason.trim()) {
      reason = archiveCustomReason.trim();
    }

    if (!reason) {
      return; // Don't proceed if no reason is provided
    }

    dispatch(archiveChemical({ id, reason }))
      .unwrap()
      .then(() => {
        setShowArchiveModal(false);
        navigate('/chemicals');
      })
      .catch((err) => {
        console.error('Failed to archive chemical:', err);
      });
  };

  return (
    <div className="w-100">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Chemical Details</h1>
        <div className="d-flex gap-2">
          <Button variant="secondary" onClick={() => navigate('/chemicals')}>
            Back to List
          </Button>
          {isAuthorized && !(currentChemical.is_archived === true) && (
            <>
              <Button
                variant="primary"
                onClick={() => navigate(`/chemicals/${id}/edit`)}
              >
                Edit
              </Button>
              <Button
                variant="success"
                onClick={() => navigate(`/chemicals/${id}/issue`)}
                disabled={currentChemical.status === 'out_of_stock' || currentChemical.status === 'expired'}
              >
                Issue Chemical
              </Button>
              <Button
                variant="info"
                onClick={() => setShowBarcodeModal(true)}
              >
                <i className="bi bi-upc-scan me-2"></i>
                Barcode
              </Button>
              <Button
                variant="danger"
                onClick={handleArchiveClick}
              >
                Archive
              </Button>
            </>
          )}
        </div>
      </div>

      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light">
          <div className="d-flex justify-content-between align-items-center">
            <h4 className="mb-0">
              {currentChemical.part_number} - {currentChemical.lot_number}
            </h4>
            <Badge bg={getStatusBadgeVariant(currentChemical.status)} className="fs-6">
              {formatStatus(currentChemical.status)}
            </Badge>
          </div>
        </Card.Header>
        <Card.Body>
          <Row>
            <Col md={6}>
              <h5>Basic Information</h5>
              <hr />
              <p>
                <strong>Part Number:</strong> {currentChemical.part_number}
              </p>
              <p>
                <strong>Lot Number:</strong> {currentChemical.lot_number}
              </p>
              <p>
                <strong>Description:</strong> {currentChemical.description || 'N/A'}
              </p>
              <p>
                <strong>Manufacturer:</strong> {currentChemical.manufacturer || 'N/A'}
              </p>
              <p>
                <strong>Category:</strong> {currentChemical.category}
              </p>
            </Col>
            <Col md={6}>
              <h5>Inventory Information</h5>
              <hr />
              <p>
                <strong>Quantity:</strong> {currentChemical.quantity} {currentChemical.unit}
              </p>
              <p>
                <strong>Location:</strong> {currentChemical.location || 'N/A'}
              </p>
              <p>
                <strong>Date Added:</strong>{' '}
                {new Date(currentChemical.date_added).toLocaleDateString()}
              </p>
              <p>
                <strong>Expiration Date:</strong>{' '}
                {currentChemical.expiration_date
                  ? new Date(currentChemical.expiration_date).toLocaleDateString()
                  : 'N/A'}
              </p>
              <p>
                <strong>Minimum Stock Level:</strong>{' '}
                {currentChemical.minimum_stock_level
                  ? `${currentChemical.minimum_stock_level} ${currentChemical.unit}`
                  : 'Not set'}
              </p>
            </Col>
          </Row>

          {currentChemical.notes && (
            <>
              <h5 className="mt-4">Notes</h5>
              <hr />
              <p>{currentChemical.notes}</p>
            </>
          )}
        </Card.Body>
      </Card>

      <Tabs defaultActiveKey="issuances" className="mb-3">
        <Tab eventKey="issuances" title="Issuance History">
          <ChemicalIssuanceHistory
            issuances={issuances[id] || []}
            loading={issuanceLoading}
          />
        </Tab>
        <Tab eventKey="returns" title="Return History">
          <ChemicalReturnHistory
            returns={returns[id] || []}
            loading={returnsLoading}
          />
        </Tab>
      </Tabs>

      {/* Archive Modal */}
      <Modal show={showArchiveModal} onHide={() => setShowArchiveModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Archive Chemical</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>
            Archiving this chemical will remove it from the active inventory.
            This action is reversible, but the chemical will be moved to the archive.
          </p>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Reason for Archiving</Form.Label>
              <Form.Select
                value={archiveReason}
                onChange={(e) => setArchiveReason(e.target.value)}
                required
              >
                <option value="">Select a reason</option>
                <option value="expired">Expired</option>
                <option value="depleted">Depleted (Used Up)</option>
                <option value="damaged">Damaged</option>
                <option value="recalled">Recalled by Manufacturer</option>
                <option value="other">Other (Specify)</option>
              </Form.Select>
            </Form.Group>

            {archiveReason === 'other' && (
              <Form.Group className="mb-3">
                <Form.Label>Specify Reason</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={2}
                  value={archiveCustomReason}
                  onChange={(e) => setArchiveCustomReason(e.target.value)}
                  placeholder="Enter specific reason for archiving"
                  required
                />
              </Form.Group>
            )}
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowArchiveModal(false)}>
            Cancel
          </Button>
          <Button
            variant="danger"
            onClick={handleArchiveConfirm}
            disabled={!archiveReason || (archiveReason === 'other' && !archiveCustomReason.trim())}
          >
            Archive Chemical
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Barcode Modal */}
      {showBarcodeModal && (
        <ChemicalBarcode
          show={showBarcodeModal}
          onHide={() => setShowBarcodeModal(false)}
          chemical={currentChemical}
        />
      )}
    </div>
  );
};

export default ChemicalDetailPage;
