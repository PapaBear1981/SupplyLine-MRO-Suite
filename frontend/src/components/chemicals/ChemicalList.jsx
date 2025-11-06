import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { Card, Table, Form, InputGroup, Button, Badge, Alert, Pagination } from 'react-bootstrap';
import { fetchChemicals } from '../../store/chemicalsSlice';
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
  const navigate = useNavigate();
  const { chemicals, loading, error } = useSelector((state) => state.chemicals);
  const { showTooltips, showHelp } = useHelp();
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredChemicals, setFilteredChemicals] = useState([]);
  const [categoryFilter, setCategoryFilter] = useState('');
  // Default to showing Available and Low Stock items (exclude Out Of Stock)
  const [statusFilter, setStatusFilter] = useState('available,low_stock');
  const [warehouseFilter, setWarehouseFilter] = useState('');
  const [warehouses, setWarehouses] = useState([]);
  const [showBarcodeModal, setShowBarcodeModal] = useState(false);
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [selectedChemical, setSelectedChemical] = useState(null);

  // Pagination states
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(30);

  // Sorting state
  const [sortConfig, setSortConfig] = useState({ key: 'part_number', direction: 'ascending' });

  // Fetch chemicals and warehouses on component mount
  useEffect(() => {
    dispatch(fetchChemicals());

    const fetchWarehouses = async () => {
      try {
        const response = await api.get('/warehouses');
        // Backend returns { warehouses: [...], pagination: {...} }
        const warehousesData = response.data.warehouses || response.data;
        setWarehouses(Array.isArray(warehousesData) ? warehousesData : []);
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

    // Apply status filter (supports multiple statuses separated by comma)
    if (statusFilter) {
      const allowedStatuses = statusFilter.split(',').map(s => s.trim());
      filtered = filtered.filter((chemical) => allowedStatuses.includes(chemical.status));
    }

    // Apply warehouse filter
    if (warehouseFilter) {
      if (warehouseFilter === 'kits') {
        // Show only chemicals in kits (warehouse_id is null and kit_id is not null)
        filtered = filtered.filter((chemical) => chemical.warehouse_id === null && chemical.kit_id !== null);
      } else {
        // Show only chemicals in the selected warehouse
        filtered = filtered.filter((chemical) => chemical.warehouse_id === parseInt(warehouseFilter));
      }
    }

    // Apply sorting
    const sorted = [...filtered].sort((a, b) => {
      let aValue = a[sortConfig.key];
      let bValue = b[sortConfig.key];

      // Handle special cases for sorting
      if (sortConfig.key === 'quantity') {
        // Numeric sort for quantity
        aValue = parseFloat(aValue) || 0;
        bValue = parseFloat(bValue) || 0;
      } else if (sortConfig.key === 'expiration_date') {
        // Date sort with N/A values at the end
        if (!aValue || aValue === 'N/A') return 1;
        if (!bValue || bValue === 'N/A') return -1;
        aValue = new Date(aValue).getTime();
        bValue = new Date(bValue).getTime();
      } else if (sortConfig.key === 'warehouse_name') {
        // Sort by warehouse/kit name
        aValue = a.warehouse_id
          ? (warehouses.find(w => w.id === a.warehouse_id)?.name || '')
          : (a.kit_name || '');
        bValue = b.warehouse_id
          ? (warehouses.find(w => w.id === b.warehouse_id)?.name || '')
          : (b.kit_name || '');
      } else {
        // String sort (case-insensitive)
        aValue = (aValue || '').toString().toLowerCase();
        bValue = (bValue || '').toString().toLowerCase();
      }

      if (aValue < bValue) {
        return sortConfig.direction === 'ascending' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sortConfig.direction === 'ascending' ? 1 : -1;
      }
      return 0;
    });

    setFilteredChemicals(sorted);
    // Reset to page 1 when filters or sorting change
    setCurrentPage(1);
  }, [chemicals, searchTerm, categoryFilter, statusFilter, warehouseFilter, sortConfig, warehouses]);

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

  // Reset all filters to defaults
  const resetFilters = () => {
    setSearchTerm('');
    setCategoryFilter('');
    setStatusFilter('available,low_stock'); // Reset to default (exclude Out Of Stock)
    setWarehouseFilter('');
    setCurrentPage(1);
  };

  // Sorting handlers
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

  // Calculate pagination
  const totalPages = Math.ceil(filteredChemicals.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedChemicals = filteredChemicals.slice(startIndex, endIndex);

  // Pagination handlers
  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      handlePageChange(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      handlePageChange(currentPage + 1);
    }
  };

  // Generate page numbers to display
  const getPageNumbers = () => {
    const pages = [];
    const maxPagesToShow = 5;

    if (totalPages <= maxPagesToShow) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      pages.push(1);
      let startPage = Math.max(2, currentPage - 1);
      let endPage = Math.min(totalPages - 1, currentPage + 1);

      if (startPage > 2) {
        pages.push('...');
      }

      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }

      if (endPage < totalPages - 1) {
        pages.push('...');
      }

      pages.push(totalPages);
    }

    return pages;
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
          <p>This page displays all active chemicals in the inventory. You can search, filter, sort, and manage chemicals from this view.</p>
          <ul>
            <li><strong>Search:</strong> Use the search box to find chemicals by part number, lot number, description, or manufacturer.</li>
            <li><strong>Filters:</strong> Filter chemicals by category or status using the dropdown menus.</li>
            <li><strong>Sort:</strong> Click on any column header to sort the table by that column.</li>
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
                      <p>Use the search, filter, and sort options to find specific chemicals.</p>
                      <ul>
                        <li>Search for chemicals by part number, lot number, description, or manufacturer</li>
                        <li>Filter chemicals by category, status, or location</li>
                        <li>Sort the table by clicking on column headers</li>
                        <li>View chemical details, issue chemicals, or generate barcodes using the action buttons</li>
                      </ul>
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
                    <option value="available,low_stock">Available & Low Stock</option>
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
                <Tooltip text="Filter by warehouse or kits" placement="top" show={showTooltips}>
                  <Form.Select value={warehouseFilter} onChange={(e) => setWarehouseFilter(e.target.value)}>
                    <option value="">All Locations</option>
                    <option value="kits">In Kits</option>
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
                    <th onClick={() => handleSort('part_number')} className="cursor-pointer">
                      Part Number {getSortIcon('part_number')}
                    </th>
                    <th onClick={() => handleSort('lot_number')} className="cursor-pointer">
                      Lot Number {getSortIcon('lot_number')}
                    </th>
                    <th>Description</th>
                    <th onClick={() => handleSort('manufacturer')} className="cursor-pointer">
                      Manufacturer {getSortIcon('manufacturer')}
                    </th>
                    <th onClick={() => handleSort('quantity')} className="cursor-pointer">
                      Quantity {getSortIcon('quantity')}
                    </th>
                    <th onClick={() => handleSort('location')} className="cursor-pointer">
                      Location {getSortIcon('location')}
                    </th>
                    <th onClick={() => handleSort('warehouse_name')} className="cursor-pointer">
                      Warehouse {getSortIcon('warehouse_name')}
                    </th>
                    <th onClick={() => handleSort('expiration_date')} className="cursor-pointer">
                      Expiration Date {getSortIcon('expiration_date')}
                    </th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedChemicals.map((chemical) => (
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
                          chemical.location || 'N/A'
                        ) : chemical.box_number ? (
                          <Badge bg="secondary">{chemical.box_number}</Badge>
                        ) : (
                          'N/A'
                        )}
                      </td>
                      <td>
                        {chemical.warehouse_id ? (
                          <Badge bg="info">
                            {warehouses.find(w => w.id === chemical.warehouse_id)?.name || `Warehouse ${chemical.warehouse_id}`}
                          </Badge>
                        ) : chemical.kit_name ? (
                          <Badge bg="secondary">{chemical.kit_name}</Badge>
                        ) : (
                          <Badge bg="warning">Unknown</Badge>
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
                              onClick={() => navigate(`/chemicals/${chemical.id}`)}
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
                              onClick={() => navigate(`/chemicals/${chemical.id}/issue`)}
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

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="d-flex justify-content-between align-items-center p-3 border-top">
              <div className="text-muted">
                <small>
                  Showing {startIndex + 1}-{Math.min(endIndex, filteredChemicals.length)} of {filteredChemicals.length} chemicals
                </small>
              </div>
              <Pagination className="mb-0">
                <Pagination.First
                  onClick={() => handlePageChange(1)}
                  disabled={currentPage === 1}
                />
                <Pagination.Prev
                  onClick={handlePreviousPage}
                  disabled={currentPage === 1}
                />

                {getPageNumbers().map((page, index) => (
                  page === '...' ? (
                    <Pagination.Ellipsis key={`ellipsis-${index}`} disabled />
                  ) : (
                    <Pagination.Item
                      key={page}
                      active={page === currentPage}
                      onClick={() => handlePageChange(page)}
                    >
                      {page}
                    </Pagination.Item>
                  )
                ))}

                <Pagination.Next
                  onClick={handleNextPage}
                  disabled={currentPage === totalPages}
                />
                <Pagination.Last
                  onClick={() => handlePageChange(totalPages)}
                  disabled={currentPage === totalPages}
                />
              </Pagination>
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
