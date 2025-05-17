import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { Card, Table, Form, InputGroup, Button, Badge, Alert } from 'react-bootstrap';
import { fetchChemicals, searchChemicals } from '../../store/chemicalsSlice';
import LoadingSpinner from '../common/LoadingSpinner';
import ChemicalBarcode from './ChemicalBarcode';

const ChemicalList = () => {
  const dispatch = useDispatch();
  const { chemicals, loading, error } = useSelector((state) => state.chemicals);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredChemicals, setFilteredChemicals] = useState([]);
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [showBarcodeModal, setShowBarcodeModal] = useState(false);
  const [selectedChemical, setSelectedChemical] = useState(null);

  // Fetch chemicals on component mount
  useEffect(() => {
    dispatch(fetchChemicals());
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

    setFilteredChemicals(filtered);
  }, [chemicals, searchTerm, categoryFilter, statusFilter]);

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

  if (loading && !chemicals.length) {
    return <LoadingSpinner />;
  }

  return (
    <>
      <Card className="shadow-sm">
        <Card.Header className="bg-light">
          <div className="d-flex flex-wrap justify-content-between align-items-center">
            <h4 className="mb-0">Chemical Inventory</h4>
            <div className="d-flex gap-2">
              <Button variant="outline-secondary" onClick={resetFilters} size="sm">
                Reset Filters
              </Button>
            </div>
          </div>
        </Card.Header>
        <Card.Body>
          {error && <Alert variant="danger">{error.message}</Alert>}

          <div className="mb-4">
            <div className="row g-3">
              <div className="col-md-6">
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
              </div>
              <div className="col-md-3">
                <Form.Select value={categoryFilter} onChange={handleCategoryChange}>
                  <option value="">All Categories</option>
                  {categories.map((category) => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
                </Form.Select>
              </div>
              <div className="col-md-3">
                <Form.Select value={statusFilter} onChange={handleStatusChange}>
                  <option value="">All Statuses</option>
                  {statuses.map((status) => (
                    <option key={status} value={status}>
                      {formatStatus(status)}
                    </option>
                  ))}
                </Form.Select>
              </div>
            </div>
          </div>

          {filteredChemicals.length === 0 ? (
            <Alert variant="info">
              No chemicals found. {searchTerm || categoryFilter || statusFilter ? 'Try adjusting your filters.' : ''}
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
                          <Button
                            as={Link}
                            to={`/chemicals/${chemical.id}`}
                            variant="primary"
                            size="sm"
                          >
                            View
                          </Button>
                          <Button
                            as={Link}
                            to={`/chemicals/${chemical.id}/issue`}
                            variant="success"
                            size="sm"
                            disabled={chemical.status === 'out_of_stock' || chemical.status === 'expired'}
                          >
                            Issue
                          </Button>
                          <Button
                            variant="info"
                            size="sm"
                            onClick={() => handleBarcodeClick(chemical)}
                          >
                            <i className="bi bi-upc-scan"></i>
                          </Button>
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
    </>
  );
};

export default ChemicalList;
