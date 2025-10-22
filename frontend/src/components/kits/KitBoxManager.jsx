import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Button, Table, Modal, Form, Alert, Badge, Spinner, Toast, ToastContainer } from 'react-bootstrap';
import { FaPlus, FaEdit, FaTrash, FaBox, FaExclamationTriangle } from 'react-icons/fa';
import { fetchKitBoxes, addKitBox, updateKitBox, deleteKitBox } from '../../store/kitsSlice';

const KitBoxManager = ({ kitId }) => {
  const dispatch = useDispatch();
  const { kitBoxes, loading, error } = useSelector((state) => state.kits);
  const boxes = kitBoxes[kitId] || [];

  const [showModal, setShowModal] = useState(false);
  const [editingBox, setEditingBox] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [boxToDelete, setBoxToDelete] = useState(null);
  const [validated, setValidated] = useState(false);
  const [toast, setToast] = useState({ show: false, message: '', variant: 'success' });
  const [formData, setFormData] = useState({
    box_number: '',
    box_type: 'expendable',
    description: ''
  });

  const showToast = (message, variant = 'success') => {
    setToast({ show: true, message, variant });
  };

  useEffect(() => {
    if (kitId) {
      dispatch(fetchKitBoxes(kitId));
    }
  }, [dispatch, kitId]);

  const handleOpenModal = (box = null) => {
    if (box) {
      setEditingBox(box);
      setFormData({
        box_number: box.box_number,
        box_type: box.box_type,
        description: box.description || ''
      });
    } else {
      setEditingBox(null);
      setFormData({
        box_number: `Box${boxes.length + 1}`,
        box_type: 'expendable',
        description: ''
      });
    }
    setValidated(false);
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingBox(null);
    setValidated(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    setValidated(true);

    try {
      if (editingBox) {
        await dispatch(updateKitBox({
          kitId,
          boxId: editingBox.id,
          data: formData
        })).unwrap();
        showToast('Box updated successfully', 'success');
      } else {
        await dispatch(addKitBox({
          kitId,
          data: formData
        })).unwrap();
        showToast('Box added successfully', 'success');
      }
      handleCloseModal();
      dispatch(fetchKitBoxes(kitId));
    } catch (err) {
      showToast(err.message || 'Failed to save box', 'danger');
    }
  };

  const handleDeleteClick = (box) => {
    setBoxToDelete(box);
    setShowDeleteConfirm(true);
  };

  const handleDeleteConfirm = async () => {
    if (!boxToDelete) return;

    try {
      await dispatch(deleteKitBox({
        kitId,
        boxId: boxToDelete.id
      })).unwrap();
      showToast('Box deleted successfully', 'success');
      setShowDeleteConfirm(false);
      setBoxToDelete(null);
      dispatch(fetchKitBoxes(kitId));
    } catch (err) {
      showToast(err.message || 'Failed to delete box', 'danger');
    }
  };

  const getBoxTypeBadge = (type) => {
    const variants = {
      expendable: 'primary',
      tooling: 'success',
      consumable: 'info',
      loose: 'warning',
      floor: 'secondary'
    };
    return <Badge bg={variants[type] || 'secondary'}>{type}</Badge>;
  };

  if (loading && boxes.length === 0) {
    return (
      <Card>
        <Card.Body className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-3 text-muted">Loading boxes...</p>
        </Card.Body>
      </Card>
    );
  }

  return (
    <>
      {/* Toast Notification */}
      <ToastContainer position="top-end" className="p-3">
        <Toast
          show={toast.show}
          onClose={() => setToast({ ...toast, show: false })}
          delay={3000}
          autohide
          bg={toast.variant}
        >
          <Toast.Header>
            <strong className="me-auto">
              {toast.variant === 'success' ? 'Success' : toast.variant === 'danger' ? 'Error' : 'Info'}
            </strong>
          </Toast.Header>
          <Toast.Body className={toast.variant === 'success' || toast.variant === 'danger' ? 'text-white' : ''}>
            {toast.message}
          </Toast.Body>
        </Toast>
      </ToastContainer>

      <Card className="shadow-sm">
        <Card.Header className="d-flex justify-content-between align-items-center">
          <h5 className="mb-0">
            <FaBox className="me-2" />
            Kit Boxes ({boxes.length})
          </h5>
          <Button
            variant="primary"
            size="sm"
            onClick={() => handleOpenModal()}
          >
            <FaPlus className="me-1" />
            Add Box
          </Button>
        </Card.Header>
        <Card.Body>
          {error && <Alert variant="danger">{error.message || error}</Alert>}
          
          {boxes.length === 0 ? (
            <div className="text-center py-4 text-muted">
              <FaBox size={48} className="mb-3 opacity-25" />
              <p>No boxes configured for this kit</p>
              <Button variant="outline-primary" onClick={() => handleOpenModal()}>
                Add Your First Box
              </Button>
            </div>
          ) : (
            <Table responsive hover>
              <thead>
                <tr>
                  <th>Box Number</th>
                  <th>Type</th>
                  <th>Description</th>
                  <th>Items</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {boxes.map((box) => (
                  <tr key={box.id}>
                    <td><strong>{box.box_number}</strong></td>
                    <td>{getBoxTypeBadge(box.box_type)}</td>
                    <td>{box.description || <span className="text-muted">No description</span>}</td>
                    <td>
                      <Badge bg="secondary">{box.item_count || 0}</Badge>
                    </td>
                    <td>
                      <Button
                        variant="outline-primary"
                        size="sm"
                        className="me-2"
                        onClick={() => handleOpenModal(box)}
                      >
                        <FaEdit />
                      </Button>
                      <Button
                        variant="outline-danger"
                        size="sm"
                        onClick={() => handleDeleteClick(box)}
                        disabled={box.item_count > 0}
                        title={box.item_count > 0 ? 'Cannot delete box with items' : 'Delete box'}
                      >
                        <FaTrash />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card.Body>
      </Card>

      {/* Add/Edit Modal */}
      <Modal show={showModal} onHide={handleCloseModal}>
        <Modal.Header closeButton>
          <Modal.Title>
            {editingBox ? 'Edit Box' : 'Add New Box'}
          </Modal.Title>
        </Modal.Header>
        <Form noValidate validated={validated} onSubmit={handleSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Box Number *</Form.Label>
              <Form.Control
                type="text"
                name="box_number"
                value={formData.box_number}
                onChange={handleChange}
                required
                placeholder="e.g., Box1, Box2, Loose, Floor"
              />
              <Form.Control.Feedback type="invalid">
                Box number is required
              </Form.Control.Feedback>
              <Form.Text className="text-muted">
                Must be unique within this kit
              </Form.Text>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Box Type *</Form.Label>
              <Form.Select
                name="box_type"
                value={formData.box_type}
                onChange={handleChange}
                required
              >
                <option value="expendable">Expendable</option>
                <option value="tooling">Tooling</option>
                <option value="consumable">Consumable</option>
                <option value="loose">Loose</option>
                <option value="floor">Floor</option>
              </Form.Select>
              <Form.Control.Feedback type="invalid">
                Box type is required
              </Form.Control.Feedback>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={2}
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="Optional description of box contents"
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleCloseModal}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              {editingBox ? 'Update Box' : 'Add Box'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal show={showDeleteConfirm} onHide={() => setShowDeleteConfirm(false)}>
        <Modal.Header closeButton>
          <Modal.Title>
            <FaExclamationTriangle className="text-warning me-2" />
            Confirm Delete
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {boxToDelete && (
            <>
              <p>Are you sure you want to delete this box?</p>
              <Alert variant="warning">
                <strong>Box:</strong> {boxToDelete.box_number} ({boxToDelete.box_type})
                <br />
                <strong>Items:</strong> {boxToDelete.item_count || 0}
              </Alert>
              {boxToDelete.item_count > 0 && (
                <Alert variant="danger">
                  This box contains {boxToDelete.item_count} item(s). 
                  You must remove all items before deleting the box.
                </Alert>
              )}
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDeleteConfirm(false)}>
            Cancel
          </Button>
          <Button 
            variant="danger" 
            onClick={handleDeleteConfirm}
            disabled={boxToDelete?.item_count > 0}
          >
            Delete Box
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default KitBoxManager;

