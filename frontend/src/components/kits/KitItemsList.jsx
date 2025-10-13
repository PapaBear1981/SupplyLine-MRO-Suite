import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Table, Badge, Button, Form, Row, Col, ButtonGroup } from 'react-bootstrap';
import { FaBox, FaFilter, FaExchangeAlt, FaShoppingCart, FaPlus } from 'react-icons/fa';
import { fetchKitItems, fetchKitBoxes } from '../../store/kitsSlice';
import KitIssuanceForm from './KitIssuanceForm';
import AddKitItemModal from './AddKitItemModal';

const KitItemsList = ({ kitId }) => {
  const dispatch = useDispatch();
  const { kitItems, kitBoxes } = useSelector((state) => state.kits);

  const [filterBox, setFilterBox] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [showIssuanceForm, setShowIssuanceForm] = useState(false);
  const [selectedItemForIssue, setSelectedItemForIssue] = useState(null);
  const [showAddItemModal, setShowAddItemModal] = useState(false);

  useEffect(() => {
    if (kitId) {
      dispatch(fetchKitBoxes(kitId));
      dispatch(fetchKitItems({ kitId, filters: {} }));
    }
  }, [dispatch, kitId]);

  const items = kitItems[kitId] || { items: [], expendables: [], total_count: 0 };
  const boxes = kitBoxes[kitId] || [];

  const allItems = [
    ...items.items.map(item => ({ ...item, source: 'item' })),
    ...items.expendables.map(exp => ({ ...exp, source: 'expendable' }))
  ];

  const filteredItems = allItems.filter(item => {
    if (filterBox && item.box_id !== parseInt(filterBox)) return false;
    if (filterType && item.item_type !== filterType) return false;
    if (filterStatus && item.status !== filterStatus) return false;
    return true;
  });

  const getStatusBadge = (status) => {
    const variants = {
      available: 'success',
      issued: 'warning',
      transferred: 'info',
      out_of_stock: 'danger',
      low_stock: 'warning'
    };
    return <Badge bg={variants[status] || 'secondary'}>{status}</Badge>;
  };

  const getBoxName = (boxId) => {
    const box = boxes.find(b => b.id === boxId);
    return box ? box.box_number : 'Unknown';
  };

  const handleIssueItem = (item) => {
    setSelectedItemForIssue(item);
    setShowIssuanceForm(true);
  };

  const handleIssuanceFormClose = () => {
    setShowIssuanceForm(false);
    setSelectedItemForIssue(null);
    // Refresh items after issuance
    dispatch(fetchKitItems({ kitId }));
  };

  const handleAddItemSuccess = () => {
    // Refresh items after adding
    dispatch(fetchKitItems({ kitId }));
  };

  return (
    <Card>
      <Card.Header>
        <Row className="align-items-center">
          <Col>
            <h5 className="mb-0">
              <FaBox className="me-2" />
              Kit Items ({filteredItems.length})
            </h5>
          </Col>
          <Col xs="auto">
            <Button
              variant="success"
              size="sm"
              className="me-2"
              onClick={() => setShowAddItemModal(true)}
            >
              <FaPlus className="me-1" />
              Add Item
            </Button>
            <Button
              variant="primary"
              size="sm"
              className="me-2"
              onClick={() => setShowIssuanceForm(true)}
            >
              <FaShoppingCart className="me-1" />
              Issue Items
            </Button>
            <Button variant="info" size="sm">
              <FaExchangeAlt className="me-1" />
              Transfer
            </Button>
          </Col>
        </Row>
      </Card.Header>
      
      <Card.Body>
        {/* Filters */}
        <Row className="mb-3">
          <Col md={4}>
            <Form.Group>
              <Form.Label className="small">
                <FaFilter className="me-1" />
                Filter by Box
              </Form.Label>
              <Form.Select
                size="sm"
                value={filterBox}
                onChange={(e) => setFilterBox(e.target.value)}
              >
                <option value="">All Boxes</option>
                {boxes.map(box => (
                  <option key={box.id} value={box.id}>
                    {box.box_number} ({box.box_type})
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
          </Col>
          <Col md={4}>
            <Form.Group>
              <Form.Label className="small">Filter by Type</Form.Label>
              <Form.Select
                size="sm"
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
              >
                <option value="">All Types</option>
                <option value="tool">Tool</option>
                <option value="chemical">Chemical</option>
                <option value="expendable">Expendable</option>
              </Form.Select>
            </Form.Group>
          </Col>
          <Col md={4}>
            <Form.Group>
              <Form.Label className="small">Filter by Status</Form.Label>
              <Form.Select
                size="sm"
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
              >
                <option value="">All Statuses</option>
                <option value="available">Available</option>
                <option value="issued">Issued</option>
                <option value="low_stock">Low Stock</option>
                <option value="out_of_stock">Out of Stock</option>
              </Form.Select>
            </Form.Group>
          </Col>
        </Row>

        {/* Items Table */}
        {filteredItems.length === 0 ? (
          <div className="text-center py-5 text-muted">
            <FaBox size={48} className="mb-3" />
            <p>No items found</p>
          </div>
        ) : (
          <Table responsive hover>
            <thead>
              <tr>
                <th>Box</th>
                <th>Part Number</th>
                <th>Description</th>
                <th>Type</th>
                <th>Quantity</th>
                <th>Location</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredItems.map((item, index) => (
                <tr key={`${item.source}-${item.id}-${index}`}>
                  <td>{getBoxName(item.box_id)}</td>
                  <td>
                    <code>{item.part_number}</code>
                    {item.serial_number && (
                      <div className="small text-muted">S/N: {item.serial_number}</div>
                    )}
                    {item.lot_number && (
                      <div className="small text-muted">Lot: {item.lot_number}</div>
                    )}
                  </td>
                  <td>{item.description}</td>
                  <td>
                    <Badge bg="secondary">{item.item_type || item.source}</Badge>
                  </td>
                  <td>
                    <strong>{item.quantity}</strong>
                    {item.unit && ` ${item.unit}`}
                    {item.minimum_stock_level && item.quantity <= item.minimum_stock_level && (
                      <div className="small text-danger">
                        Min: {item.minimum_stock_level}
                      </div>
                    )}
                  </td>
                  <td>{item.location || '-'}</td>
                  <td>{getStatusBadge(item.status)}</td>
                  <td>
                    <ButtonGroup size="sm">
                      <Button
                        variant="outline-primary"
                        title="Issue"
                        onClick={() => handleIssueItem(item)}
                      >
                        Issue
                      </Button>
                      <Button variant="outline-info" title="Transfer">
                        Transfer
                      </Button>
                    </ButtonGroup>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        )}
      </Card.Body>

      {/* Add Item Modal */}
      <AddKitItemModal
        show={showAddItemModal}
        onHide={() => setShowAddItemModal(false)}
        kitId={kitId}
        onSuccess={handleAddItemSuccess}
      />

      {/* Issuance Form Modal */}
      <KitIssuanceForm
        show={showIssuanceForm}
        onHide={handleIssuanceFormClose}
        kitId={kitId}
        preSelectedItem={selectedItemForIssue}
      />
    </Card>
  );
};

export default KitItemsList;

