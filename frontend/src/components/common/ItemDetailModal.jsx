import React, { useState, useEffect, useCallback } from 'react';
import { Modal, Button, Table, Badge, Spinner, Alert, Form, Pagination } from 'react-bootstrap';
import { FaTimes, FaBox, FaFlask, FaTools, FaHistory, FaPrint, FaDownload } from 'react-icons/fa';
import api from '../../services/api';
import './ItemDetailModal.css';

/**
 * ItemDetailModal - Reusable modal for displaying comprehensive item details
 *
 * Displays:
 * - Item information (part number, description, lot/serial numbers, location, quantity)
 * - Complete transaction history with sorting, filtering, and pagination
 * - Print and export options
 *
 * Props:
 * - show: boolean - whether modal is visible
 * - onHide: function - callback when modal is closed
 * - itemType: string - 'tool', 'chemical', 'expendable', or 'kit_item'
 * - itemId: number - ID of the item to display
 */
const ItemDetailModal = ({ show, onHide, itemType, itemId }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [itemDetail, setItemDetail] = useState(null);
  const [sortField, setSortField] = useState('timestamp');
  const [sortDirection, setSortDirection] = useState('desc');
  const [filterType, setFilterType] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const transactionsPerPage = 10;

  const fetchItemDetail = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.get(`/inventory/${itemType}/${itemId}/detail`);
      setItemDetail(response.data);
    } catch (err) {
      console.error('Error fetching item detail:', err);
      setError(err.response?.data?.error || 'Failed to load item details');
    } finally {
      setLoading(false);
    }
  }, [itemType, itemId]);

  // Fetch item details when modal opens
  useEffect(() => {
    if (show && itemType && itemId) {
      fetchItemDetail();
      setCurrentPage(1); // Reset to first page when modal opens
    }
  }, [show, itemType, itemId, fetchItemDetail]);

  // Get icon based on item type
  const getItemIcon = () => {
    switch (itemType) {
      case 'tool':
        return <FaTools className="item-icon" />;
      case 'chemical':
        return <FaFlask className="item-icon" />;
      case 'expendable':
      case 'kit_item':
        return <FaBox className="item-icon" />;
      default:
        return null;
    }
  };

  // Get badge variant based on status
  const getStatusBadge = (status) => {
    const statusMap = {
      'available': 'success',
      'checked_out': 'warning',
      'maintenance': 'danger',
      'retired': 'secondary',
      'low_stock': 'warning',
      'out_of_stock': 'danger',
      'expired': 'danger'
    };
    return statusMap[status] || 'secondary';
  };

  // Get transaction type badge variant
  const getTransactionTypeBadge = (type) => {
    const typeMap = {
      'receipt': 'success',
      'issuance': 'primary',
      'checkout': 'warning',
      'return': 'info',
      'transfer': 'secondary',
      'adjustment': 'dark',
      'kit_issuance': 'primary',
      'initial_inventory': 'light'
    };
    return typeMap[type] || 'secondary';
  };

  // Sort and filter transactions
  const getSortedAndFilteredTransactions = () => {
    if (!itemDetail?.transactions) return [];

    let filtered = itemDetail.transactions;

    // Apply filter
    if (filterType !== 'all') {
      filtered = filtered.filter(t => t.transaction_type === filterType);
    }

    // Apply sort
    const sorted = [...filtered].sort((a, b) => {
      let aVal = a[sortField];
      let bVal = b[sortField];

      // Handle dates
      if (sortField === 'timestamp') {
        aVal = new Date(aVal);
        bVal = new Date(bVal);
      }

      if (sortDirection === 'asc') {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });

    return sorted;
  };

  // Get paginated transactions
  const getPaginatedTransactions = () => {
    const sorted = getSortedAndFilteredTransactions();
    const startIndex = (currentPage - 1) * transactionsPerPage;
    const endIndex = startIndex + transactionsPerPage;
    return sorted.slice(startIndex, endIndex);
  };

  // Calculate total pages
  const getTotalPages = () => {
    const sorted = getSortedAndFilteredTransactions();
    return Math.ceil(sorted.length / transactionsPerPage);
  };

  // Handle sort
  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
    setCurrentPage(1); // Reset to first page when sorting
  };

  // Handle filter change
  const handleFilterChange = (newFilter) => {
    setFilterType(newFilter);
    setCurrentPage(1); // Reset to first page when filtering
  };

  // Print modal content
  const handlePrint = () => {
    window.print();
  };

  // Export to CSV
  const handleExport = () => {
    if (!itemDetail?.transactions) return;

    // RFC 4180 compliant CSV escaping
    const escapeCsvValue = (value) => {
      if (value === null || value === undefined) return '';
      const stringified = String(value);
      // If value contains comma, quote, or newline, wrap in quotes and escape quotes
      if (/[",\n]/.test(stringified)) {
        return `"${stringified.replace(/"/g, '""')}"`;
      }
      return stringified;
    };

    const headers = ['Timestamp', 'Type', 'User', 'Quantity', 'From', 'To', 'Notes'];
    const rows = getSortedAndFilteredTransactions().map(t => [
      new Date(t.timestamp).toLocaleString(),
      t.transaction_type,
      t.user_name || 'Unknown',
      t.quantity_change || '',
      t.location_from || '',
      t.location_to || '',
      t.notes || ''
    ]);

    const csv = [headers, ...rows]
      .map(row => row.map(escapeCsvValue).join(','))
      .join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${itemType}_${itemId}_transactions.csv`;
    a.click();
  };

  // Get unique transaction types for filter
  const getTransactionTypes = () => {
    if (!itemDetail?.transactions) return [];
    const types = new Set(itemDetail.transactions.map(t => t.transaction_type));
    return Array.from(types);
  };

  return (
    <Modal
      show={show}
      onHide={onHide}
      size="xl"
      centered
      backdrop="static"
    >
      <Modal.Header closeButton>
        <Modal.Title>
          {getItemIcon()}
          <span className="ms-2">
            {itemType.charAt(0).toUpperCase() + itemType.slice(1)} Details
          </span>
        </Modal.Title>
      </Modal.Header>

      <Modal.Body>
        {loading && (
          <div className="text-center py-5">
            <Spinner animation="border" variant="primary" />
            <p className="mt-3">Loading item details...</p>
          </div>
        )}

        {error && (
          <Alert variant="danger">
            <strong>Error:</strong> {error}
          </Alert>
        )}
        
        {!loading && !error && itemDetail && (
          <>
            {/* Item Information Section */}
            <div className="item-info-section mb-4">
              <h5 className="section-title">
                <FaBox className="me-2" />
                Item Information
              </h5>
              
              <div className="row">
                <div className="col-md-6">
                  <div className="info-group">
                    <label>Part Number:</label>
                    <span className="info-value">{itemDetail.part_number || itemDetail.tool_number || 'N/A'}</span>
                  </div>
                  
                  <div className="info-group">
                    <label>Description:</label>
                    <span className="info-value">{itemDetail.description || 'N/A'}</span>
                  </div>
                  
                  {itemDetail.serial_number && (
                    <div className="info-group">
                      <label>Serial Number:</label>
                      <span className="info-value serial-number">S/N: {itemDetail.serial_number}</span>
                    </div>
                  )}
                  
                  {itemDetail.lot_number && (
                    <div className="info-group">
                      <label>Lot Number:</label>
                      <span className="info-value lot-number">LOT: {itemDetail.lot_number}</span>
                    </div>
                  )}
                </div>
                
                <div className="col-md-6">
                  <div className="info-group">
                    <label>Location:</label>
                    <span className="info-value">{itemDetail.location || 'Unknown'}</span>
                  </div>
                  
                  {itemDetail.quantity !== undefined && (
                    <div className="info-group">
                      <label>Quantity:</label>
                      <span className="info-value">
                        {itemDetail.quantity} {itemDetail.unit || ''}
                      </span>
                    </div>
                  )}
                  
                  <div className="info-group">
                    <label>Status:</label>
                    <Badge bg={getStatusBadge(itemDetail.status)} className="ms-2">
                      {itemDetail.status || 'Unknown'}
                    </Badge>
                  </div>
                  
                  <div className="info-group">
                    <label>Created:</label>
                    <span className="info-value">
                      {itemDetail.created_at ? new Date(itemDetail.created_at).toLocaleString() : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Transaction History Section */}
            <div className="transaction-history-section">
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h5 className="section-title mb-0">
                  <FaHistory className="me-2" />
                  Transaction History ({itemDetail.transaction_count || 0})
                </h5>
                
                <div className="d-flex gap-2">
                  <Form.Select
                    size="sm"
                    value={filterType}
                    onChange={(e) => handleFilterChange(e.target.value)}
                    style={{ width: 'auto' }}
                  >
                    <option value="all">All Types</option>
                    {getTransactionTypes().map(type => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </Form.Select>

                  <Button variant="outline-secondary" size="sm" onClick={handlePrint}>
                    <FaPrint className="me-1" /> Print
                  </Button>

                  <Button variant="outline-primary" size="sm" onClick={handleExport}>
                    <FaDownload className="me-1" /> Export CSV
                  </Button>
                </div>
              </div>

              <div className="table-responsive">
                <Table striped bordered hover size="sm" className="transaction-table">
                  <thead>
                    <tr>
                      <th
                        onClick={() => handleSort('timestamp')}
                        className="sortable"
                      >
                        Timestamp {sortField === 'timestamp' && (sortDirection === 'asc' ? '↑' : '↓')}
                      </th>
                      <th
                        onClick={() => handleSort('transaction_type')}
                        className="sortable"
                      >
                        Type {sortField === 'transaction_type' && (sortDirection === 'asc' ? '↑' : '↓')}
                      </th>
                      <th>User</th>
                      <th>Quantity</th>
                      <th>From</th>
                      <th>To</th>
                      <th>Notes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {getPaginatedTransactions().length === 0 ? (
                      <tr>
                        <td colSpan="7" className="text-center text-muted">
                          No transactions found
                        </td>
                      </tr>
                    ) : (
                      getPaginatedTransactions().map((transaction, index) => (
                        <tr key={index}>
                          <td className="timestamp-cell">
                            {new Date(transaction.timestamp).toLocaleString()}
                          </td>
                          <td>
                            <Badge bg={getTransactionTypeBadge(transaction.transaction_type)}>
                              {transaction.transaction_type}
                            </Badge>
                          </td>
                          <td>{transaction.user_name || 'Unknown'}</td>
                          <td className="text-end">
                            {transaction.quantity_change !== null && transaction.quantity_change !== undefined
                              ? (transaction.quantity_change > 0 ? '+' : '') + transaction.quantity_change
                              : '-'}
                          </td>
                          <td>{transaction.location_from || '-'}</td>
                          <td>{transaction.location_to || '-'}</td>
                          <td className="notes-cell">{transaction.notes || '-'}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </Table>
              </div>

              {/* Pagination */}
              {getTotalPages() > 1 && (
                <div className="d-flex justify-content-between align-items-center mt-3">
                  <div className="text-muted small">
                    Showing {((currentPage - 1) * transactionsPerPage) + 1} to {Math.min(currentPage * transactionsPerPage, getSortedAndFilteredTransactions().length)} of {getSortedAndFilteredTransactions().length} transactions
                  </div>
                  <Pagination size="sm" className="mb-0">
                    <Pagination.First
                      onClick={() => setCurrentPage(1)}
                      disabled={currentPage === 1}
                    />
                    <Pagination.Prev
                      onClick={() => setCurrentPage(currentPage - 1)}
                      disabled={currentPage === 1}
                    />

                    {[...Array(getTotalPages())].map((_, index) => {
                      const pageNum = index + 1;
                      // Show first page, last page, current page, and pages around current
                      if (
                        pageNum === 1 ||
                        pageNum === getTotalPages() ||
                        (pageNum >= currentPage - 1 && pageNum <= currentPage + 1)
                      ) {
                        return (
                          <Pagination.Item
                            key={pageNum}
                            active={pageNum === currentPage}
                            onClick={() => setCurrentPage(pageNum)}
                          >
                            {pageNum}
                          </Pagination.Item>
                        );
                      } else if (
                        pageNum === currentPage - 2 ||
                        pageNum === currentPage + 2
                      ) {
                        return <Pagination.Ellipsis key={pageNum} disabled />;
                      }
                      return null;
                    })}

                    <Pagination.Next
                      onClick={() => setCurrentPage(currentPage + 1)}
                      disabled={currentPage === getTotalPages()}
                    />
                    <Pagination.Last
                      onClick={() => setCurrentPage(getTotalPages())}
                      disabled={currentPage === getTotalPages()}
                    />
                  </Pagination>
                </div>
              )}
            </div>
          </>
        )}
      </Modal.Body>

      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          <FaTimes className="me-1" /> Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ItemDetailModal;

