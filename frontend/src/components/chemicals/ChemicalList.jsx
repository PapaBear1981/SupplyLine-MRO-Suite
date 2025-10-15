import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { Card, Table, Form, InputGroup, Button, Badge, Alert } from 'react-bootstrap';
import { fetchChemicals, searchChemicals } from '../../store/chemicalsSlice';
import LoadingSpinner from '../common/LoadingSpinner';
import ChemicalBarcode from './ChemicalBarcode';
import ItemTransferModal from '../common/ItemTransferModal';
import Tooltip from '../common/Tooltip';
import HelpIcon from '../common/HelpIcon';
import HelpContent from '../common/HelpContent';
import { useHelp } from '../../context/HelpContext';
import api from '../../services/api';

const ChemicalList = () => {
  const dispatch = useDispatch();
  const { chemicals, loading, error } = useSelector((state) => state.chemicals);
  const { showTooltips, showHelp } = useHelp();
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredChemicals, setFilteredChemicals] = useState([]);
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [warehouseFilter, setWarehouseFilter] = useState('');
  const [warehouses, setWarehouses] = useState([]);
  const [showBarcodeModal, setShowBarcodeModal] = useState(false);
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [selectedChemical, setSelectedChemical] = useState(null);

  // Fetch chemicals and warehouses on component mount
  useEffect(() => {
    dispatch(fetchChemicals());

    const fetchWarehouses = async () => {
      try {
        const response = await api.get('/warehouses');
        // Backend returns array directly, not wrapped in {warehouses: [...]}
        setWarehouses(Array.isArray(response.data) ? response.data : []);
      } catch (err) {
        console.error('Failed to fetch warehouses:', err);
      }
    };
    fetchWarehouses();
  }, [dispatch]);

  // Update filtered chemicals when chemicals, search term, or filters change
  useEffect(() => {
    if (!chemicals) return;

    let filtered = [...chemicals];

    // Apply search filter
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(
        (chemical) =>
          chemical.part_number.toLowerCase().includes(search) ||
          chemical.lot_number.toLowerCase().includes(search) ||
          (chemical.description && chemical.description.toLowerCase().includes(search)) ||
          (chemical.manufacturer && chemical.manufacturer.toLowerCase().includes(search))
      );
    }

    // Apply category filter
    if (categoryFilter) {
      filtered = filtered.filter((chemical) => chemical.category === categoryFilter);
    }

    // Apply status filter
    if (statusFilter) {
      filtered = filtered.filter((chemical) => chemical.status === statusFilter);
    }

    // Apply warehouse filter
    if (warehouseFilter) {
      filtered = filtered.filter((chemical) => chemical.warehouse_id === parseInt(warehouseFilter));
    }

    setFilteredChemicals(filtered);
  }, [chemicals, searchTerm, categoryFilter, statusFilter, warehouseFilter]);

  // Get unique categories for filter dropdown
  const categories = chemicals
    ? [...new Set(chemicals.map((chemical) => chemical.category))]
    : [];

  // Get unique statuses for filter dropdown
  const statuses = chemicals
    ? [...new Set(chemicals.map((chemical) => chemical.status))]
    : [];

  // Handle search
  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  // Handle category filter change
  const handleCategoryChange = (e) => {
    setCategoryFilter(e.target.value);
  };

  // Handle status filter change
  const handleStatusChange = (e) => {
    setStatusFilter(e.target.value);
  };

  // Reset all filters
  const resetFilters = () => {
    setSearchTerm('');
    setCategoryFilter('');
    setStatusFilter('');
    setWarehouseFilter('');
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

  // Format status for display
  const formatStatus = (status) => {
    return status
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  // Handle barcode button click
  const handleBarcodeClick = (chemical) => {
    setSelectedChemical(chemical);
    setShowBarcodeModal(true);
  };

  // Handle transfer button click
  const handleTransferClick = (chemical) => {
    setSelectedChemical(chemical);
    setShowTransferModal(true);
  };

  if (loading && !chemicals.length) {
    return <LoadingSpinner />;
  }

  return (
    <>
      {showHelp && (
        <HelpContent title="Chemical Inventory" initialOpen={false}>
          <p>This page displays all active chemicals in the inventory. You can search, filter, and manage chemicals from this view.</p>
          <ul>
            <li><strong>Search:</strong> Use the search box to find chemicals by part number, lot number, description, or manufacturer.</li>
            <li><strong>Filters:</strong> Filter chemicals by category or status using the dropdown menus.</li>
            <li><strong>View:</strong> Click the "View" button to see detailed information about a chemical.</li>
            <li><strong>Issue:</strong> Click the "Issue" button to issue a chemical to a user or department.</li>
            <li><strong>Barcode:</strong> Click the barcode icon to generate and print a barcode for the chemical.</li>
            <li><strong>Status:</strong> Chemical status is color-coded:
              <ul>
                <li>Green: Available</li>
                <li>Yellow: Low Stock</li>
                <li>Red: Out of Stock</li>
                <li>Black: Expired</li>
              </ul>
            </li>
          </ul>
        </HelpContent>
      )}

      <Card className="shadow-sm">
        <Card.Header className="bg-light">
          <div className="d-flex flex-wrap justify-content-between align-items-center">
            <div className="d-flex align-items-center">
              <h4 className="mb-0">Chemical Inventory</h4>
              {showHelp && (
                <HelpIcon
                  title="Chemical Inventory"
                  content={
                    <>
                      <p>This table shows all active chemicals in the inventory.</p>
                      <p>Use the search and filter options to find specific chemicals.</p>
                      <p>You can view details, issue chemicals, or generate barcodes using the action buttons.</p>
                    </>
                  }
                  size="sm"
                />
              )}
            </div>
            <div className="d-flex gap-2">
              <Tooltip text="Clear all search filters" placement="top" show={showTooltips}>
                <Button variant="outline-secondary" onClick={resetFilters} size="sm">
                  Reset Filters
                </Button>
              </Tooltip>
            </div>
          </div>
        </Card.Header>
        <Card.Body>
          {error && <Alert variant="danger">{error.message}</Alert>}

          <div className="mb-4">
            <div className="row g-3">
              <div className="col-md-4">
                <Tooltip text="Search by part number, lot number, description, or manufacturer" placement="top" show={showTooltips}>
                  <InputGroup>
                    <InputGroup.Text>
                      <i className="bi bi-search"></i>
                    </InputGroup.Text>
                    <Form.Control
                      placeholder="Search by part number, lot number, description, or manufacturer"
                      value={searchTerm}
                      onChange={handleSearch}
                    />
                  </InputGroup>
                </Tooltip>
              </div>
              <div className="col-md-2">
                <Tooltip text="Filter by chemical category" placement="top" show={showTooltips}>
                  <Form.Select value={categoryFilter} onChange={handleCategoryChange}>
                    <option value="">All Categories</option>
                    {categories.map((category) => (
                      <option key={category} value={category}>
                        {category}
                      </option>
                    ))}
                  </Form.Select>
                </Tooltip>
              </div>
              <div className="col-md-2">
                <Tooltip text="Filter by chemical status" placement="top" show={showTooltips}>
                  <Form.Select value={statusFilter} onChange={handleStatusChange}>
                    <option value="">All Statuses</option>
                    {statuses.map((status) => (
                      <option key={status} value={status}>
                        {formatStatus(status)}
                      </option>
                    ))}
                  </Form.Select>
                </Tooltip>
              </div>
              <div className="col-md-2">
                <Tooltip text="Filter by warehouse" placement="top" show={showTooltips}>
                  <Form.Select value={warehouseFilter} onChange={(e) => setWarehouseFilter(e.target.value)}>
                    <option value="">All Warehouses</option>
                    {warehouses.map((warehouse) => (
                      <option key={warehouse.id} value={warehouse.id}>
                        {warehouse.name}
                      </option>
                    ))}
                  </Form.Select>
                </Tooltip>
              </div>
            </div>
          </div>

          {filteredChemicals.length === 0 ? (
            <Alert variant="info">
              No chemicals found. {searchTerm || categoryFilter || statusFilter || warehouseFilter ? 'Try adjusting your filters.' : ''}
            </Alert>
          ) : (
            <div className="table-responsive">
              <Table hover bordered className="align-middle">
                <thead className="bg-light">
                  <tr>
                    <th>Part Number</th>
                    <th>Lot Number</th>
                    <th>Description</th>
                    <th>Manufacturer</th>
                    <th>Quantity</th>
                    <th>Warehouse</th>
                    <th>Expiration Date</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredChemicals.map((chemical) => (
                    <tr key={chemical.id}>
                      <td>{chemical.part_number}</td>
                      <td>{chemical.lot_number}</td>
                      <td>{chemical.description}</td>
                      <td>{chemical.manufacturer}</td>
                      <td>
                        {chemical.quantity} {chemical.unit}
                      </td>
                      <td>
                        {chemical.warehouse_id ? (
                          <Badge bg="info">
                            {warehouses.find(w => w.id === chemical.warehouse_id)?.name || `Warehouse ${chemical.warehouse_id}`}
                          </Badge>
                        ) : (
                          <Badge bg="secondary">In Kit</Badge>
                        )}
                      </td>
                      <td>
                        {chemical.expiration_date
                          ? new Date(chemical.expiration_date).toLocaleDateString()
                          : 'N/A'}
                      </td>
                      <td>
                        <Badge bg={getStatusBadgeVariant(chemical.status)}>
                          {formatStatus(chemical.status)}
                        </Badge>
                      </td>
                      <td>
                        <div className="d-flex gap-2">
                          <Tooltip text="View chemical details" placement="top" show={showTooltips}>
                            <Button
                              as={Link}
                              to={`/chemicals/${chemical.id}`}
                              variant="primary"
                              size="sm"
                            >
                              View
                            </Button>
                          </Tooltip>
                          <Tooltip text={chemical.status === 'out_of_stock' || chemical.status === 'expired' ?
                            "Cannot issue chemicals that are out of stock or expired" :
                            "Issue this chemical to a user or department"}
                            placement="top"
                            show={showTooltips}
                          >
                            <Button
                              as={Link}
                              to={`/chemicals/${chemical.id}/issue`}
                              variant="success"
                              size="sm"
                              disabled={chemical.status === 'out_of_stock' || chemical.status === 'expired'}
                            >
                              Issue
                            </Button>
                          </Tooltip>
                          <Tooltip text="Transfer this chemical to another location" placement="top" show={showTooltips}>
                            <Button
                              variant="warning"
                              size="sm"
                              onClick={() => handleTransferClick(chemical)}
                            >
                              <i className="bi bi-arrow-left-right"></i>
                            </Button>
                          </Tooltip>
                          <Tooltip text="Generate barcode for this chemical" placement="top" show={showTooltips}>
                            <Button
                              variant="info"
                              size="sm"
                              onClick={() => handleBarcodeClick(chemical)}
                            >
                              <i className="bi bi-upc-scan"></i>
                            </Button>
                          </Tooltip>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          )}
        </Card.Body>
      </Card>

      {showBarcodeModal && (
        <ChemicalBarcode
          show={showBarcodeModal}
          onHide={() => setShowBarcodeModal(false)}
          chemical={selectedChemical}
        />
      )}

      {/* Transfer Modal */}
      {selectedChemical && (
        <ItemTransferModal
          show={showTransferModal}
          onHide={() => setShowTransferModal(false)}
          item={selectedChemical}
          itemType="chemical"
          onTransferComplete={() => {
            dispatch(fetchChemicals());
          }}
        />
      )}
    </>
  );
};

export default ChemicalList;
