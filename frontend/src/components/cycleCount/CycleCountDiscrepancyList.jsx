import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Button, Table, Badge, Form, InputGroup, Spinner, Alert } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { fetchCountDiscrepancies } from '../../store/cycleCountSlice';

const CycleCountDiscrepancyList = () => {
  const dispatch = useDispatch();
  const { items, loading, error } = useSelector((state) => state.cycleCount.discrepancies);
  const [searchTerm, setSearchTerm] = useState('');
  const [batchFilter, setBatchFilter] = useState('');
  const [sortField, setSortField] = useState('counted_at');
  const [sortDirection, setSortDirection] = useState('desc');

  useEffect(() => {
    const params = {};
    if (batchFilter) {
      params.batch_id = batchFilter;
    }
    dispatch(fetchCountDiscrepancies(params));
  }, [dispatch, batchFilter]);

  const handleSort = (field) => {
    if (field === sortField) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const filteredDiscrepancies = items.filter((discrepancy) => {
    if (!searchTerm) return true;
    
    // Search in item details if available
    const itemDetails = discrepancy.item?.item_details || {};
    
    return (
      discrepancy.discrepancy_type?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      discrepancy.discrepancy_notes?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      discrepancy.actual_location?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      itemDetails.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      itemDetails.number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      itemDetails.serial?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      itemDetails.part_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      itemDetails.lot_number?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  });

  const sortedDiscrepancies = [...filteredDiscrepancies].sort((a, b) => {
    let aValue = a[sortField];
    let bValue = b[sortField];

    if (sortField === 'counted_at') {
      aValue = new Date(aValue);
      bValue = new Date(bValue);
    }

    if (aValue < bValue) {
      return sortDirection === 'asc' ? -1 : 1;
    }
    if (aValue > bValue) {
      return sortDirection === 'asc' ? 1 : -1;
    }
    return 0;
  });

  if (loading) {
    return (
      <div className="text-center p-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Error Loading Discrepancies</Alert.Heading>
        <p>{error.error || 'An error occurred while loading count discrepancies'}</p>
      </Alert>
    );
  }

  return (
    <div className="p-3">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <Form.Control
          type="text"
          placeholder="Filter by batch ID..."
          value={batchFilter}
          onChange={(e) => setBatchFilter(e.target.value)}
          style={{ width: '200px' }}
        />
        <InputGroup style={{ width: '300px' }}>
          <InputGroup.Text>
            <i className="bi bi-search"></i>
          </InputGroup.Text>
          <Form.Control
            type="text"
            placeholder="Search discrepancies..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </InputGroup>
      </div>

      {sortedDiscrepancies.length === 0 ? (
        <div className="text-center p-5">
          <p className="text-muted">No discrepancies found</p>
        </div>
      ) : (
        <div className="table-responsive">
          <Table hover>
            <thead>
              <tr>
                <th>Item</th>
                <th onClick={() => handleSort('discrepancy_type')} className="cursor-pointer">
                  Discrepancy Type {sortField === 'discrepancy_type' && (
                    <i className={`bi bi-arrow-${sortDirection === 'asc' ? 'up' : 'down'}`}></i>
                  )}
                </th>
                <th>Expected</th>
                <th>Actual</th>
                <th onClick={() => handleSort('counted_at')} className="cursor-pointer">
                  Counted At {sortField === 'counted_at' && (
                    <i className={`bi bi-arrow-${sortDirection === 'asc' ? 'up' : 'down'}`}></i>
                  )}
                </th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {sortedDiscrepancies.map((discrepancy) => {
                const itemDetails = discrepancy.item?.item_details || {};
                const itemType = discrepancy.item?.item_type;
                
                let itemName = 'Unknown Item';
                if (itemType === 'tool') {
                  itemName = `${itemDetails.number || ''} - ${itemDetails.serial || ''}`;
                } else if (itemType === 'chemical') {
                  itemName = `${itemDetails.part_number || ''} - ${itemDetails.lot_number || ''}`;
                }
                
                return (
                  <tr key={discrepancy.id}>
                    <td>
                      <div>{itemName}</div>
                      <small className="text-muted">{itemDetails.description}</small>
                    </td>
                    <td>
                      <Badge bg={getDiscrepancyTypeColor(discrepancy.discrepancy_type)}>
                        {formatDiscrepancyType(discrepancy.discrepancy_type)}
                      </Badge>
                    </td>
                    <td>
                      {discrepancy.discrepancy_type === 'quantity' && (
                        <span>{discrepancy.item?.expected_quantity}</span>
                      )}
                      {discrepancy.discrepancy_type === 'location' && (
                        <span>{discrepancy.item?.expected_location}</span>
                      )}
                      {(discrepancy.discrepancy_type === 'condition' || discrepancy.discrepancy_type === 'missing') && (
                        <span>-</span>
                      )}
                    </td>
                    <td>
                      {discrepancy.discrepancy_type === 'quantity' && (
                        <span>{discrepancy.actual_quantity}</span>
                      )}
                      {discrepancy.discrepancy_type === 'location' && (
                        <span>{discrepancy.actual_location}</span>
                      )}
                      {discrepancy.discrepancy_type === 'condition' && (
                        <span>{discrepancy.condition}</span>
                      )}
                      {discrepancy.discrepancy_type === 'missing' && (
                        <span>Not Found</span>
                      )}
                    </td>
                    <td>{new Date(discrepancy.counted_at).toLocaleString()}</td>
                    <td>
                      <Button
                        as={Link}
                        to={`/cycle-counts/discrepancies/${discrepancy.id}`}
                        variant="outline-primary"
                        size="sm"
                        className="me-2"
                      >
                        View
                      </Button>
                      <Button
                        as={Link}
                        to={`/cycle-counts/discrepancies/${discrepancy.id}/adjust`}
                        variant="outline-warning"
                        size="sm"
                      >
                        Adjust
                      </Button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </Table>
        </div>
      )}
    </div>
  );
};

// Helper functions
const getDiscrepancyTypeColor = (type) => {
  switch (type) {
    case 'quantity':
      return 'warning';
    case 'location':
      return 'info';
    case 'condition':
      return 'danger';
    case 'missing':
      return 'danger';
    case 'extra':
      return 'success';
    default:
      return 'secondary';
  }
};

const formatDiscrepancyType = (type) => {
  switch (type) {
    case 'quantity':
      return 'Quantity';
    case 'location':
      return 'Location';
    case 'condition':
      return 'Condition';
    case 'missing':
      return 'Missing';
    case 'extra':
      return 'Extra';
    default:
      return type;
  }
};

export default CycleCountDiscrepancyList;
