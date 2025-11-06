import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Table, Badge, Button, Form, Row, Col, ButtonGroup, OverlayTrigger, Tooltip } from 'react-bootstrap';
import { FaBox, FaFilter, FaBarcode, FaHashtag } from 'react-icons/fa';
import { fetchKitItems, fetchKitBoxes } from '../../store/kitsSlice';
import KitIssuanceForm from './KitIssuanceForm';
import KitTransferForm from './KitTransferForm';
import ItemDetailModal from '../common/ItemDetailModal';
import KitItemBarcode from './KitItemBarcode';
import './KitItemsList.css';

const KitItemsList = ({ kitId }) => {
  const dispatch = useDispatch();
  const { kitItems, kitBoxes } = useSelector((state) => state.kits);

  const [filterBox, setFilterBox] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [showIssuanceForm, setShowIssuanceForm] = useState(false);
  const [selectedItemForIssue, setSelectedItemForIssue] = useState(null);
  const [showTransferForm, setShowTransferForm] = useState(false);
  const [selectedItemForTransfer, setSelectedItemForTransfer] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedItemForDetail, setSelectedItemForDetail] = useState(null);
  const [showBarcodeModal, setShowBarcodeModal] = useState(false);
  const [selectedItemForBarcode, setSelectedItemForBarcode] = useState(null);
  const [sortConfig, setSortConfig] = useState({ key: 'part_number', direction: 'ascending' });

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

  // Sort filtered items
  const sortedItems = [...filteredItems].sort((a, b) => {
    let aValue, bValue;

    if (sortConfig.key === 'box_id') {
      // Sort by box name
      aValue = getBoxName(a.box_id).toLowerCase();
      bValue = getBoxName(b.box_id).toLowerCase();
    } else if (sortConfig.key === 'quantity') {
      // Numeric sorting for quantity
      aValue = parseFloat(a.quantity) || 0;
      bValue = parseFloat(b.quantity) || 0;

      if (sortConfig.direction === 'ascending') {
        return aValue - bValue;
      } else {
        return bValue - aValue;
      }
    } else {
      // String sorting for other fields
      aValue = (a[sortConfig.key] || '').toString().toLowerCase();
      bValue = (b[sortConfig.key] || '').toString().toLowerCase();
    }

    if (sortConfig.direction === 'ascending') {
      return aValue.toString().localeCompare(bValue.toString());
    } else {
      return bValue.toString().localeCompare(aValue.toString());
    }
  });

  const handleSort = (key) => {
    setSortConfig({
      key,
      direction:
        sortConfig.key === key && sortConfig.direction === 'ascending'
          ? 'descending'
          : 'ascending',
    });
  };

  const getSortIcon = (key) => {
    if (sortConfig.key !== key) return null;
    return sortConfig.direction === 'ascending' ? '↑' : '↓';
  };

  const getTrackingIcon = (item) => {
    // Determine tracking type based on what fields are present
    // Items can only have EITHER lot OR serial, never both
    const hasLot = !!item.lot_number;
    const hasSerial = !!item.serial_number;
    const trackingType = item.tracking_type;

    if (trackingType === 'lot' || hasLot) {
      return (
        <OverlayTrigger
          placement="top"
          overlay={<Tooltip>Tracked by Lot Number</Tooltip>}
        >
          <Badge bg="warning" className="ms-2">
            <FaHashtag className="me-1" />
            Lot
          </Badge>
        </OverlayTrigger>
      );
    } else if (trackingType === 'serial' || hasSerial) {
      return (
        <OverlayTrigger
          placement="top"
          overlay={<Tooltip>Tracked by Serial Number</Tooltip>}
        >
          <Badge bg="primary" className="ms-2">
            <FaBarcode className="me-1" />
            Serial
          </Badge>
        </OverlayTrigger>
      );
    }
    return null;
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

  const handleTransferItem = (item) => {
    setSelectedItemForTransfer(item);
    setShowTransferForm(true);
  };

  const handleTransferFormClose = () => {
    setShowTransferForm(false);
    setSelectedItemForTransfer(null);
    // Refresh items after transfer
    dispatch(fetchKitItems({ kitId }));
  };

  const handleBarcodeClick = (item) => {
    setSelectedItemForBarcode(item);
    setShowBarcodeModal(true);
  };

  const handleRowClick = (item) => {
    // Determine item type and ID for the detail modal
    let itemType, itemId;

    if (item.source === 'expendable' || item.item_type === 'expendable') {
      itemType = 'expendable';
      // For expendables, use item_id (the Expendable.id), not id (the KitItem.id)
      itemId = item.item_id || item.id;
    } else if (item.item_type === 'tool') {
      itemType = 'tool';
      itemId = item.item_id || item.id;
    } else if (item.item_type === 'chemical') {
      itemType = 'chemical';
      itemId = item.item_id || item.id;
    } else {
      itemType = 'kit_item';
      itemId = item.id;
    }

    setSelectedItemForDetail({ itemType, itemId });
    setShowDetailModal(true);
  };

  return (
    <Card>
      <Card.Header>
        <h5 className="mb-0">
          <FaBox className="me-2" />
          Kit Items ({filteredItems.length})
        </h5>
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
            <thead className="bg-light">
              <tr>
                <th onClick={() => handleSort('box_id')} className="cursor-pointer">
                  Box {getSortIcon('box_id')}
                </th>
                <th onClick={() => handleSort('part_number')} className="cursor-pointer">
                  Part Number {getSortIcon('part_number')}
                </th>
                <th onClick={() => handleSort('description')} className="cursor-pointer">
                  Description {getSortIcon('description')}
                </th>
                <th onClick={() => handleSort('item_type')} className="cursor-pointer">
                  Type {getSortIcon('item_type')}
                </th>
                <th onClick={() => handleSort('quantity')} className="cursor-pointer">
                  Quantity {getSortIcon('quantity')}
                </th>
                <th onClick={() => handleSort('location')} className="cursor-pointer">
                  Location {getSortIcon('location')}
                </th>
                <th onClick={() => handleSort('status')} className="cursor-pointer">
                  Status {getSortIcon('status')}
                </th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {sortedItems.map((item, index) => (
                <tr
                  key={`${item.source}-${item.id}-${index}`}
                  className="clickable-row"
                  onClick={() => handleRowClick(item)}
                  style={{ cursor: 'pointer' }}
                >
                  <td>{getBoxName(item.box_id)}</td>
                  <td>
                    <div className="d-flex align-items-center">
                      <div>
                        <code>{item.part_number}</code>
                        {item.serial_number && (
                          <div className="small text-muted">S/N: {item.serial_number}</div>
                        )}
                        {item.lot_number && (
                          <div className="small text-muted">LOT: {item.lot_number}</div>
                        )}
                      </div>
                      {getTrackingIcon(item)}
                    </div>
                  </td>
                  <td>{item.description}</td>
                  <td>
                    <Badge bg="secondary">{item.item_type || item.source}</Badge>
                  </td>
                  <td>
                    <strong>{item.quantity}</strong>
                    {item.unit && ` ${item.unit}`}
                    {item.minimum_stock_level != null && item.minimum_stock_level > 0 && item.quantity <= item.minimum_stock_level && (
                      <div className="small text-danger">
                        Min: {item.minimum_stock_level}
                      </div>
                    )}
                  </td>
                  <td>{item.location || '-'}</td>
                  <td>{getStatusBadge(item.status)}</td>
                  <td onClick={(e) => e.stopPropagation()}>
                    <ButtonGroup size="sm">
                      {/* Tools cannot be issued - they must be retired or removed from service */}
                      {item.item_type !== 'tool' && (
                        <Button
                          variant="outline-primary"
                          title="Issue"
                          onClick={() => handleIssueItem(item)}
                        >
                          Issue
                        </Button>
                      )}
                      <Button
                        variant="outline-info"
                        title="Transfer"
                        onClick={() => handleTransferItem(item)}
                      >
                        Transfer
                      </Button>
                      <Button
                        variant="outline-secondary"
                        title="Print Barcode"
                        onClick={() => handleBarcodeClick(item)}
                      >
                        <FaBarcode />
                      </Button>
                    </ButtonGroup>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        )}
      </Card.Body>

      {/* Issuance Form Modal */}
      <KitIssuanceForm
        show={showIssuanceForm}
        onHide={handleIssuanceFormClose}
        kitId={kitId}
        preSelectedItem={selectedItemForIssue}
      />

      {/* Transfer Form Modal */}
      <KitTransferForm
        show={showTransferForm}
        onHide={handleTransferFormClose}
        sourceKitId={kitId}
        preSelectedItem={selectedItemForTransfer}
      />

      {/* Item Detail Modal */}
      {selectedItemForDetail && (
        <ItemDetailModal
          show={showDetailModal}
          onHide={() => {
            setShowDetailModal(false);
            setSelectedItemForDetail(null);
          }}
          itemType={selectedItemForDetail.itemType}
          itemId={selectedItemForDetail.itemId}
        />
      )}

      {/* Barcode Modal */}
      <KitItemBarcode
        show={showBarcodeModal}
        onHide={() => setShowBarcodeModal(false)}
        item={selectedItemForBarcode}
      />
    </Card>
  );
};

export default KitItemsList;

