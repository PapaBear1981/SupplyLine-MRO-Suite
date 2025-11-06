import { useState, useEffect, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Form, Alert, Spinner, Row, Col, Table, Badge, InputGroup, Button, Pagination } from 'react-bootstrap';
import { fetchComprehensiveAnalytics } from '../../store/chemicalsSlice';
import { Pie, Bar, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
} from 'chart.js';
import './ComprehensiveChemicalAnalytics.css';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
);

const ComprehensiveChemicalAnalytics = () => {
  const dispatch = useDispatch();
  const {
    comprehensiveAnalytics,
    comprehensiveLoading,
    comprehensiveError
  } = useSelector((state) => state.chemicals);

  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortField, setSortField] = useState('part_number');
  const [sortDirection, setSortDirection] = useState('asc');
  const [expandedRows, setExpandedRows] = useState(new Set());
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

  useEffect(() => {
    dispatch(fetchComprehensiveAnalytics());
  }, [dispatch]);

  // Filter and sort chemicals
  const filteredAndSortedChemicals = useMemo(() => {
    if (!comprehensiveAnalytics?.chemicals) return [];

    let filtered = comprehensiveAnalytics.chemicals.filter(chem => {
      const matchesSearch =
        chem.part_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
        chem.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        chem.manufacturer.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesStatus = statusFilter === 'all' || chem.status === statusFilter;

      return matchesSearch && matchesStatus;
    });

    // Sort
    filtered.sort((a, b) => {
      let aVal = a[sortField];
      let bVal = b[sortField];

      if (typeof aVal === 'string') {
        aVal = aVal.toLowerCase();
        bVal = bVal.toLowerCase();
      }

      if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    return filtered;
  }, [comprehensiveAnalytics, searchTerm, statusFilter, sortField, sortDirection]);

  // Pagination calculations
  const totalPages = Math.ceil(filteredAndSortedChemicals.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedChemicals = filteredAndSortedChemicals.slice(startIndex, endIndex);

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, statusFilter, sortField, sortDirection]);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const toggleRowExpansion = (partNumber) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(partNumber)) {
      newExpanded.delete(partNumber);
    } else {
      newExpanded.add(partNumber);
    }
    setExpandedRows(newExpanded);
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      available: { variant: 'success', text: 'Available' },
      low_stock: { variant: 'warning', text: 'Low Stock' },
      expiring_soon: { variant: 'warning', text: 'Expiring Soon' },
      expired: { variant: 'danger', text: 'Expired' },
      out_of_stock: { variant: 'secondary', text: 'Out of Stock' }
    };
    
    const config = statusConfig[status] || { variant: 'secondary', text: status };
    return <Badge bg={config.variant} className="status-badge">{config.text}</Badge>;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const getDaysUntilExpiration = (expirationDate) => {
    if (!expirationDate) return null;
    const days = Math.floor((new Date(expirationDate) - new Date()) / (1000 * 60 * 60 * 24));
    return days;
  };

  // Prepare chart data
  const prepareChartData = () => {
    if (!comprehensiveAnalytics) return null;

    // Location distribution pie chart
    const locationData = {
      labels: comprehensiveAnalytics.location_distribution.map(l => l.location),
      datasets: [{
        data: comprehensiveAnalytics.location_distribution.map(l => l.quantity),
        backgroundColor: [
          'rgba(54, 162, 235, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(255, 206, 86, 0.8)',
          'rgba(153, 102, 255, 0.8)',
          'rgba(255, 159, 64, 0.8)',
          'rgba(255, 99, 132, 0.8)',
        ],
        borderColor: [
          'rgba(54, 162, 235, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(255, 159, 64, 1)',
          'rgba(255, 99, 132, 1)',
        ],
        borderWidth: 2,
      }]
    };

    // Top 10 chemicals by usage
    const topChemicals = [...comprehensiveAnalytics.chemicals]
      .sort((a, b) => b.total_issued - a.total_issued)
      .slice(0, 10);

    const usageData = {
      labels: topChemicals.map(c => c.part_number),
      datasets: [{
        label: 'Total Issued',
        data: topChemicals.map(c => c.total_issued),
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 2,
      }]
    };

    // Expiration timeline
    const expirationGroups = {
      'Expired': 0,
      '0-30 days': 0,
      '31-60 days': 0,
      '61-90 days': 0,
      '90+ days': 0,
      'No expiration': 0
    };

    comprehensiveAnalytics.chemicals.forEach(chem => {
      if (!chem.earliest_expiration) {
        expirationGroups['No expiration']++;
      } else {
        const days = getDaysUntilExpiration(chem.earliest_expiration);
        if (days < 0) expirationGroups['Expired']++;
        else if (days <= 30) expirationGroups['0-30 days']++;
        else if (days <= 60) expirationGroups['31-60 days']++;
        else if (days <= 90) expirationGroups['61-90 days']++;
        else expirationGroups['90+ days']++;
      }
    });

    const expirationData = {
      labels: Object.keys(expirationGroups),
      datasets: [{
        label: 'Chemicals by Expiration',
        data: Object.values(expirationGroups),
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(255, 159, 64, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(153, 102, 255, 0.6)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(255, 159, 64, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(153, 102, 255, 1)',
        ],
        borderWidth: 2,
      }]
    };

    return { locationData, usageData, expirationData };
  };

  const chartData = comprehensiveAnalytics ? prepareChartData() : null;

  if (comprehensiveLoading) {
    return (
      <div className="comprehensive-analytics-loading">
        <Spinner animation="border" role="status" variant="primary" />
        <p className="mt-3">Loading comprehensive analytics...</p>
      </div>
    );
  }

  if (comprehensiveError) {
    return (
      <Alert variant="danger">
        {comprehensiveError.message || 'Failed to load comprehensive analytics'}
      </Alert>
    );
  }

  if (!comprehensiveAnalytics) {
    return (
      <Alert variant="info">
        No analytics data available.
      </Alert>
    );
  }

  return (
    <div className="comprehensive-analytics fade-in">
      {/* Summary Cards */}
      <Row className="g-4 mb-4">
        <Col md={2}>
          <Card className="summary-card h-100 card-hover">
            <Card.Body className="text-center">
              <div className="summary-icon">📦</div>
              <h3 className="summary-value">{comprehensiveAnalytics.summary.total_chemicals}</h3>
              <p className="summary-label">Total Chemicals</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={2}>
          <Card className="summary-card h-100 card-hover">
            <Card.Body className="text-center">
              <div className="summary-icon">📊</div>
              <h3 className="summary-value">{comprehensiveAnalytics.summary.total_quantity}</h3>
              <p className="summary-label">Total Quantity</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={2}>
          <Card className="summary-card h-100 card-hover status-warning">
            <Card.Body className="text-center">
              <div className="summary-icon">⚠️</div>
              <h3 className="summary-value">{comprehensiveAnalytics.summary.expiring_soon}</h3>
              <p className="summary-label">Expiring Soon</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={2}>
          <Card className="summary-card h-100 card-hover status-danger">
            <Card.Body className="text-center">
              <div className="summary-icon">❌</div>
              <h3 className="summary-value">{comprehensiveAnalytics.summary.expired}</h3>
              <p className="summary-label">Expired</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={2}>
          <Card className="summary-card h-100 card-hover status-warning">
            <Card.Body className="text-center">
              <div className="summary-icon">📉</div>
              <h3 className="summary-value">{comprehensiveAnalytics.summary.low_stock}</h3>
              <p className="summary-label">Low Stock</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={2}>
          <Card className="summary-card h-100 card-hover">
            <Card.Body className="text-center">
              <div className="summary-icon">♻️</div>
              <h3 className="summary-value">{comprehensiveAnalytics.summary.avg_waste_rate}%</h3>
              <p className="summary-label">Avg Waste Rate</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Charts Section */}
      {chartData && (
        <Row className="g-4 mb-4">
          <Col md={4}>
            <Card className="chart-card card-hover">
              <Card.Header className="bg-light">
                <h5 className="mb-0">Inventory by Location</h5>
              </Card.Header>
              <Card.Body>
                <div style={{ height: '300px' }}>
                  <Pie
                    data={chartData.locationData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: { position: 'bottom' }
                      }
                    }}
                  />
                </div>
              </Card.Body>
            </Card>
          </Col>
          <Col md={4}>
            <Card className="chart-card card-hover">
              <Card.Header className="bg-light">
                <h5 className="mb-0">Top 10 by Usage</h5>
              </Card.Header>
              <Card.Body>
                <div style={{ height: '300px' }}>
                  <Bar
                    data={chartData.usageData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: { display: false }
                      },
                      scales: {
                        y: { beginAtZero: true }
                      }
                    }}
                  />
                </div>
              </Card.Body>
            </Card>
          </Col>
          <Col md={4}>
            <Card className="chart-card card-hover">
              <Card.Header className="bg-light">
                <h5 className="mb-0">Expiration Timeline</h5>
              </Card.Header>
              <Card.Body>
                <div style={{ height: '300px' }}>
                  <Bar
                    data={chartData.expirationData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: { display: false }
                      },
                      scales: {
                        y: { beginAtZero: true }
                      }
                    }}
                  />
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Filters and Search */}
      <Card className="mb-4 filter-card">
        <Card.Body>
          <Row className="g-3">
            <Col md={6}>
              <InputGroup>
                <InputGroup.Text>🔍</InputGroup.Text>
                <Form.Control
                  type="text"
                  placeholder="Search by part number, description, or manufacturer..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="search-input"
                />
              </InputGroup>
            </Col>
            <Col md={3}>
              <Form.Select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Statuses</option>
                <option value="available">Available</option>
                <option value="low_stock">Low Stock</option>
                <option value="expiring_soon">Expiring Soon</option>
                <option value="expired">Expired</option>
              </Form.Select>
            </Col>
            <Col md={3} className="text-end">
              <Badge bg="secondary" className="result-count">
                {filteredAndSortedChemicals.length} chemicals
              </Badge>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {/* Data Table */}
      <Card className="data-table-card">
        <Card.Body className="p-0">
          <div className="table-responsive">
            <Table hover className="chemicals-table mb-0">
              <thead className="table-header">
                <tr>
                  <th></th>
                  <th onClick={() => handleSort('part_number')} className="sortable">
                    Part Number {sortField === 'part_number' && (sortDirection === 'asc' ? '↑' : '↓')}
                  </th>
                  <th onClick={() => handleSort('description')} className="sortable">
                    Description {sortField === 'description' && (sortDirection === 'asc' ? '↑' : '↓')}
                  </th>
                  <th onClick={() => handleSort('total_quantity')} className="sortable text-center">
                    Quantity {sortField === 'total_quantity' && (sortDirection === 'asc' ? '↑' : '↓')}
                  </th>
                  <th className="text-center">Locations</th>
                  <th className="text-center">Status</th>
                  <th onClick={() => handleSort('earliest_expiration')} className="sortable text-center">
                    Expiration {sortField === 'earliest_expiration' && (sortDirection === 'asc' ? '↑' : '↓')}
                  </th>
                  <th onClick={() => handleSort('avg_monthly_usage')} className="sortable text-center">
                    Avg Usage {sortField === 'avg_monthly_usage' && (sortDirection === 'asc' ? '↑' : '↓')}
                  </th>
                  <th className="text-center">Waste %</th>
                </tr>
              </thead>
              <tbody>
                {paginatedChemicals.map((chemical) => {
                  const isExpanded = expandedRows.has(chemical.part_number);
                  const daysUntilExp = getDaysUntilExpiration(chemical.earliest_expiration);

                  return (
                    <>
                      <tr
                        key={chemical.part_number}
                        className="table-row"
                        onClick={() => toggleRowExpansion(chemical.part_number)}
                      >
                        <td className="expand-cell">
                          <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
                        </td>
                        <td className="part-number-cell">
                          <strong>{chemical.part_number}</strong>
                        </td>
                        <td>{chemical.description}</td>
                        <td className="text-center">
                          <Badge bg="info">{chemical.total_quantity} {chemical.unit}</Badge>
                        </td>
                        <td className="text-center">
                          <Badge bg="secondary">{chemical.locations.length}</Badge>
                        </td>
                        <td className="text-center">
                          {getStatusBadge(chemical.status)}
                        </td>
                        <td className="text-center">
                          {chemical.earliest_expiration ? (
                            <div>
                              <div>{formatDate(chemical.earliest_expiration)}</div>
                              {daysUntilExp !== null && (
                                <small className={daysUntilExp < 0 ? 'text-danger' : daysUntilExp <= 30 ? 'text-warning' : 'text-muted'}>
                                  {daysUntilExp < 0 ? 'Expired' : `${daysUntilExp} days`}
                                </small>
                              )}
                            </div>
                          ) : (
                            <span className="text-muted">N/A</span>
                          )}
                        </td>
                        <td className="text-center">
                          {chemical.avg_monthly_usage > 0 ? (
                            <>{chemical.avg_monthly_usage} {chemical.unit}/mo</>
                          ) : (
                            <span className="text-muted">N/A</span>
                          )}
                        </td>
                        <td className="text-center">
                          <Badge bg={chemical.waste_percentage > 20 ? 'danger' : chemical.waste_percentage > 10 ? 'warning' : 'success'}>
                            {chemical.waste_percentage}%
                          </Badge>
                        </td>
                      </tr>
                      {isExpanded && (
                        <tr className="expanded-row">
                          <td colSpan="9">
                            <div className="expanded-content">
                              <Row>
                                <Col md={6}>
                                  <h6>Location Details</h6>
                                  <Table size="sm" bordered>
                                    <thead>
                                      <tr>
                                        <th>Location</th>
                                        <th className="text-end">Quantity</th>
                                      </tr>
                                    </thead>
                                    <tbody>
                                      {chemical.locations.map((loc, idx) => (
                                        <tr key={idx}>
                                          <td>{loc.name}</td>
                                          <td className="text-end">{loc.quantity} {chemical.unit}</td>
                                        </tr>
                                      ))}
                                    </tbody>
                                  </Table>
                                </Col>
                                <Col md={6}>
                                  <h6>Additional Information</h6>
                                  <div className="info-grid">
                                    <div className="info-item">
                                      <strong>Manufacturer:</strong> {chemical.manufacturer || 'N/A'}
                                    </div>
                                    <div className="info-item">
                                      <strong>Category:</strong> {chemical.category}
                                    </div>
                                    <div className="info-item">
                                      <strong>Total Issued:</strong> {chemical.total_issued} {chemical.unit}
                                    </div>
                                    <div className="info-item">
                                      <strong>Lot Numbers:</strong> {chemical.lot_numbers.join(', ')}
                                    </div>
                                    <div className="info-item">
                                      <strong>Last Transfer:</strong> {formatDate(chemical.last_transfer_date)}
                                    </div>
                                    <div className="info-item">
                                      <strong>Expiring Soon:</strong> {chemical.expiring_soon_count} items
                                    </div>
                                    <div className="info-item">
                                      <strong>Expired:</strong> {chemical.expired_count} items
                                    </div>
                                    <div className="info-item">
                                      <strong>Low Stock:</strong> {chemical.low_stock_count} items
                                    </div>
                                  </div>
                                </Col>
                              </Row>
                            </div>
                          </td>
                        </tr>
                      )}
                    </>
                  );
                })}
              </tbody>
            </Table>
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="d-flex justify-content-between align-items-center mt-3 pagination-container">
              <div className="pagination-info">
                Showing {startIndex + 1}-{Math.min(endIndex, filteredAndSortedChemicals.length)} of {filteredAndSortedChemicals.length} chemicals
              </div>
              <Pagination className="mb-0">
                <Pagination.First
                  onClick={() => setCurrentPage(1)}
                  disabled={currentPage === 1}
                />
                <Pagination.Prev
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                />

                {/* Show page numbers */}
                {[...Array(totalPages)].map((_, idx) => {
                  const pageNum = idx + 1;
                  // Show first page, last page, current page, and pages around current
                  if (
                    pageNum === 1 ||
                    pageNum === totalPages ||
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
                  onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                  disabled={currentPage === totalPages}
                />
                <Pagination.Last
                  onClick={() => setCurrentPage(totalPages)}
                  disabled={currentPage === totalPages}
                />
              </Pagination>
            </div>
          )}
        </Card.Body>
      </Card>
    </div>
  );
};

export default ComprehensiveChemicalAnalytics;

