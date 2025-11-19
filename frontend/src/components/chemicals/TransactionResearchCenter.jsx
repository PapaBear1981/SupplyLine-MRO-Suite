import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Form,
  Row,
  Col,
  Button,
  Table,
  Badge,
  Spinner,
  Alert,
  InputGroup,
  Pagination
} from 'react-bootstrap';
import { searchTransactions } from '../../store/chemicalsSlice';
import { format } from 'date-fns';

const TransactionResearchCenter = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { transactions, transactionsPagination, transactionsLoading, transactionsError } = useSelector(
    (state) => state.chemicals
  );

  const [filters, setFilters] = useState({
    start_date: '',
    end_date: '',
    transaction_type: '',
    part_number: '',
    lot_number: '',
    q: '',
    page: 1,
    per_page: 50
  });

  const [showFilters, setShowFilters] = useState(true);

  useEffect(() => {
    handleSearch();
  }, [filters.page]);

  const handleFilterChange = (field, value) => {
    setFilters((prev) => ({ ...prev, [field]: value, page: 1 }));
  };

  const handleSearch = () => {
    const activeFilters = {};
    Object.keys(filters).forEach((key) => {
      if (filters[key]) {
        activeFilters[key] = filters[key];
      }
    });
    dispatch(searchTransactions(activeFilters));
  };

  const handleReset = () => {
    setFilters({
      start_date: '',
      end_date: '',
      transaction_type: '',
      part_number: '',
      lot_number: '',
      q: '',
      page: 1,
      per_page: 50
    });
  };

  const handlePageChange = (newPage) => {
    setFilters((prev) => ({ ...prev, page: newPage }));
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'issuance':
        return 'danger';
      case 'return':
        return 'success';
      case 'receipt':
        return 'primary';
      case 'adjustment':
        return 'warning';
      case 'transfer':
        return 'info';
      default:
        return 'secondary';
    }
  };

  const renderPagination = () => {
    if (!transactionsPagination || transactionsPagination.pages <= 1) return null;

    const { page, pages, has_prev, has_next } = transactionsPagination;
    const items = [];

    items.push(
      <Pagination.First
        key="first"
        onClick={() => handlePageChange(1)}
        disabled={!has_prev}
      />
    );
    items.push(
      <Pagination.Prev
        key="prev"
        onClick={() => handlePageChange(page - 1)}
        disabled={!has_prev}
      />
    );

    const showPages = 5;
    let startPage = Math.max(1, page - Math.floor(showPages / 2));
    let endPage = Math.min(pages, startPage + showPages - 1);

    if (endPage - startPage < showPages - 1) {
      startPage = Math.max(1, endPage - showPages + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      items.push(
        <Pagination.Item
          key={i}
          active={i === page}
          onClick={() => handlePageChange(i)}
        >
          {i}
        </Pagination.Item>
      );
    }

    items.push(
      <Pagination.Next
        key="next"
        onClick={() => handlePageChange(page + 1)}
        disabled={!has_next}
      />
    );
    items.push(
      <Pagination.Last
        key="last"
        onClick={() => handlePageChange(pages)}
        disabled={!has_next}
      />
    );

    return <Pagination className="mt-3">{items}</Pagination>;
  };

  return (
    <Card className="transaction-research-center">
      <Card.Header className="bg-light">
        <div className="d-flex justify-content-between align-items-center">
          <strong>
            <i className="bi bi-search me-2"></i>
            Transaction Research Center
          </strong>
          <Button
            variant="link"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
          >
            <i className={`bi bi-chevron-${showFilters ? 'up' : 'down'}`}></i>
            {showFilters ? 'Hide' : 'Show'} Filters
          </Button>
        </div>
      </Card.Header>

      {showFilters && (
        <Card.Body className="bg-light border-bottom">
          <Form>
            <Row className="g-3">
              <Col md={6}>
                <Form.Group>
                  <Form.Label className="small fw-bold">Search</Form.Label>
                  <InputGroup>
                    <InputGroup.Text>
                      <i className="bi bi-search"></i>
                    </InputGroup.Text>
                    <Form.Control
                      type="text"
                      placeholder="Part number, lot number, notes..."
                      value={filters.q}
                      onChange={(e) => handleFilterChange('q', e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          handleSearch();
                        }
                      }}
                    />
                  </InputGroup>
                </Form.Group>
              </Col>

              <Col md={3}>
                <Form.Group>
                  <Form.Label className="small fw-bold">Start Date</Form.Label>
                  <Form.Control
                    type="date"
                    value={filters.start_date}
                    onChange={(e) => handleFilterChange('start_date', e.target.value)}
                  />
                </Form.Group>
              </Col>

              <Col md={3}>
                <Form.Group>
                  <Form.Label className="small fw-bold">End Date</Form.Label>
                  <Form.Control
                    type="date"
                    value={filters.end_date}
                    onChange={(e) => handleFilterChange('end_date', e.target.value)}
                  />
                </Form.Group>
              </Col>

              <Col md={4}>
                <Form.Group>
                  <Form.Label className="small fw-bold">Transaction Type</Form.Label>
                  <Form.Select
                    value={filters.transaction_type}
                    onChange={(e) => handleFilterChange('transaction_type', e.target.value)}
                  >
                    <option value="">All Types</option>
                    <option value="issuance">Issuance</option>
                    <option value="return">Return</option>
                    <option value="receipt">Receipt</option>
                    <option value="adjustment">Adjustment</option>
                    <option value="transfer">Transfer</option>
                  </Form.Select>
                </Form.Group>
              </Col>

              <Col md={4}>
                <Form.Group>
                  <Form.Label className="small fw-bold">Part Number</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Filter by part number"
                    value={filters.part_number}
                    onChange={(e) => handleFilterChange('part_number', e.target.value)}
                  />
                </Form.Group>
              </Col>

              <Col md={4}>
                <Form.Group>
                  <Form.Label className="small fw-bold">Lot Number</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Filter by lot number"
                    value={filters.lot_number}
                    onChange={(e) => handleFilterChange('lot_number', e.target.value)}
                  />
                </Form.Group>
              </Col>

              <Col xs={12}>
                <div className="d-flex gap-2">
                  <Button variant="primary" onClick={handleSearch} disabled={transactionsLoading}>
                    <i className="bi bi-search me-2"></i>
                    Search
                  </Button>
                  <Button variant="outline-secondary" onClick={handleReset}>
                    <i className="bi bi-x-circle me-2"></i>
                    Reset
                  </Button>
                </div>
              </Col>
            </Row>
          </Form>
        </Card.Body>
      )}

      <Card.Body className="p-0">
        {transactionsLoading ? (
          <div className="text-center py-5">
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Searching transactions...</span>
            </Spinner>
          </div>
        ) : transactionsError ? (
          <Alert variant="danger" className="m-3">
            <p className="mb-0">{transactionsError.message || 'Failed to search transactions'}</p>
          </Alert>
        ) : transactions.length === 0 ? (
          <div className="text-center text-muted py-5">
            <i className="bi bi-inbox fs-1 d-block mb-2"></i>
            <p>No transactions found matching your criteria</p>
          </div>
        ) : (
          <>
            <div className="table-responsive">
              <Table hover className="mb-0">
                <thead className="bg-light">
                  <tr>
                    <th>Date/Time</th>
                    <th>Type</th>
                    <th>Part Number</th>
                    <th>Lot Number</th>
                    <th>Quantity</th>
                    <th>User</th>
                    <th>Location</th>
                    <th>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((transaction, index) => (
                    <tr
                      key={index}
                      onClick={() => transaction.chemical_id && navigate(`/chemicals/${transaction.chemical_id}`)}
                      style={{ cursor: transaction.chemical_id ? 'pointer' : 'default' }}
                    >
                      <td className="small">
                        {format(new Date(transaction.timestamp), 'MMM d, yyyy')}
                        <br />
                        <span className="text-muted">
                          {format(new Date(transaction.timestamp), 'h:mm a')}
                        </span>
                      </td>
                      <td>
                        <Badge bg={getTypeColor(transaction.type || transaction.transaction_type)}>
                          {transaction.type || transaction.transaction_type}
                        </Badge>
                      </td>
                      <td>{transaction.part_number || '-'}</td>
                      <td>{transaction.lot_number || '-'}</td>
                      <td>
                        <span className={transaction.quantity < 0 ? 'text-danger' : 'text-success'}>
                          {transaction.quantity > 0 ? '+' : ''}
                          {transaction.quantity || '-'} {transaction.unit || ''}
                        </span>
                      </td>
                      <td className="small">{transaction.user_name || '-'}</td>
                      <td className="small">
                        {transaction.location ||
                          (transaction.location_to && transaction.location_from
                            ? `${transaction.location_from} → ${transaction.location_to}`
                            : transaction.location_to || transaction.location_from || '-')}
                      </td>
                      <td className="small text-truncate" style={{ maxWidth: '200px' }}>
                        {transaction.description || transaction.notes || transaction.purpose || '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>

            {transactionsPagination && (
              <div className="p-3 bg-light border-top">
                <div className="d-flex justify-content-between align-items-center">
                  <small className="text-muted">
                    Showing {transactions.length} of {transactionsPagination.total} transactions
                  </small>
                  {renderPagination()}
                </div>
              </div>
            )}
          </>
        )}
      </Card.Body>
    </Card>
  );
};

export default TransactionResearchCenter;
