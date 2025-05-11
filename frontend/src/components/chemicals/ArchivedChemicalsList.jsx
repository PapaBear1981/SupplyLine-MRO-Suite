import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { Card, Table, Form, InputGroup, Button, Badge, Alert } from 'react-bootstrap';
import { fetchArchivedChemicals, unarchiveChemical } from '../../store/chemicalsSlice';
import LoadingSpinner from '../common/LoadingSpinner';
import ConfirmModal from '../common/ConfirmModal';

const ArchivedChemicalsList = () => {
  const dispatch = useDispatch();
  const { archivedChemicals, archivedLoading, archivedError, loading } = useSelector((state) => state.chemicals);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredChemicals, setFilteredChemicals] = useState([]);
  const [categoryFilter, setCategoryFilter] = useState('');
  const [reasonFilter, setReasonFilter] = useState('');
  const [showUnarchiveModal, setShowUnarchiveModal] = useState(false);
  const [selectedChemical, setSelectedChemical] = useState(null);

  // Update filtered chemicals when chemicals, search term, or filters change
  useEffect(() => {
    if (!archivedChemicals) return;

    let filtered = [...archivedChemicals];

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

    // Apply reason filter
    if (reasonFilter) {
      filtered = filtered.filter((chemical) => chemical.archived_reason === reasonFilter);
    }

    setFilteredChemicals(filtered);
  }, [archivedChemicals, searchTerm, categoryFilter, reasonFilter]);

  // Get unique categories for filter dropdown
  const categories = archivedChemicals
    ? [...new Set(archivedChemicals.map((chemical) => chemical.category))]
    : [];

  // Get unique archive reasons for filter dropdown
  const reasons = archivedChemicals
    ? [...new Set(archivedChemicals.map((chemical) => chemical.archived_reason))]
    : [];

  // Handle search
  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  // Handle category filter change
  const handleCategoryChange = (e) => {
    setCategoryFilter(e.target.value);
  };

  // Handle reason filter change
  const handleReasonChange = (e) => {
    setReasonFilter(e.target.value);
  };

  // Reset all filters
  const resetFilters = () => {
    setSearchTerm('');
    setCategoryFilter('');
    setReasonFilter('');
  };

  // Format status for display
  const formatStatus = (status) => {
    return status
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  // Format reason for display
  const formatReason = (reason) => {
    return reason
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  // Handle unarchive button click
  const handleUnarchiveClick = (chemical) => {
    setSelectedChemical(chemical);
    setShowUnarchiveModal(true);
  };

  // Handle unarchive confirmation
  const handleUnarchiveConfirm = () => {
    if (selectedChemical) {
      dispatch(unarchiveChemical(selectedChemical.id))
        .unwrap()
        .then(() => {
          setShowUnarchiveModal(false);
          setSelectedChemical(null);
        })
        .catch((err) => {
          console.error('Failed to unarchive chemical:', err);
        });
    }
  };

  if (archivedLoading && !archivedChemicals.length) {
    return <LoadingSpinner />;
  }

  return (
    <>
      <Card className="shadow-sm">
        <Card.Header className="bg-light">
          <div className="d-flex flex-wrap justify-content-between align-items-center">
            <h4 className="mb-0">Archived Chemicals</h4>
            <div className="d-flex gap-2">
              <Button variant="outline-secondary" onClick={resetFilters} size="sm">
                Reset Filters
              </Button>
            </div>
          </div>
        </Card.Header>
        <Card.Body>
          {archivedError && <Alert variant="danger">{archivedError.message}</Alert>}

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
                <Form.Select value={reasonFilter} onChange={handleReasonChange}>
                  <option value="">All Archive Reasons</option>
                  {reasons.map((reason) => (
                    <option key={reason} value={reason}>
                      {formatReason(reason)}
                    </option>
                  ))}
                </Form.Select>
              </div>
            </div>
          </div>

          {filteredChemicals.length === 0 ? (
            <Alert variant="info">
              No archived chemicals found. {searchTerm || categoryFilter || reasonFilter ? 'Try adjusting your filters.' : ''}
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
                    <th>Archive Reason</th>
                    <th>Archive Date</th>
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
                        <Badge bg={chemical.archived_reason === 'expired' ? 'danger' : 'secondary'}>
                          {formatReason(chemical.archived_reason)}
                        </Badge>
                      </td>
                      <td>
                        {chemical.archived_date
                          ? new Date(chemical.archived_date).toLocaleDateString()
                          : 'N/A'}
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
                            onClick={() => handleUnarchiveClick(chemical)}
                            disabled={loading}
                          >
                            Unarchive
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

      <ConfirmModal
        show={showUnarchiveModal}
        onHide={() => setShowUnarchiveModal(false)}
        onConfirm={handleUnarchiveConfirm}
        title="Unarchive Chemical"
        message={`Are you sure you want to unarchive ${selectedChemical?.part_number} - ${selectedChemical?.lot_number}? This will make it active again.`}
        confirmText="Unarchive"
        confirmVariant="success"
      />
    </>
  );
};

export default ArchivedChemicalsList;
