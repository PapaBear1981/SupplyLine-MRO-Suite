import { useState, useEffect, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Container, Row, Col, Card, Form, Button, Table, Badge, Tabs, Tab, Alert
} from 'react-bootstrap';
import {
  fetchInventoryReport,
  fetchIssuanceReport,
  fetchTransferReport,
  fetchReorderReport,
  fetchKitUtilization,
  fetchKits,
  fetchAircraftTypes
} from '../../store/kitsSlice';
import LoadingSpinner from '../common/LoadingSpinner';
import {
  FaChartBar, FaBoxes, FaExchangeAlt, FaRedo, FaFileExport, FaCalendar, FaFilter
} from 'react-icons/fa';
import { Bar, Line, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const KitReports = () => {
  const dispatch = useDispatch();
  const {
    kits,
    aircraftTypes,
    inventoryReport,
    issuanceReport,
    transferReport,
    reorderReport,
    utilizationReport,
    loading,
    error
  } = useSelector((state) => state.kits);
  const { user } = useSelector((state) => state.auth);

  // State for active tab
  const [activeTab, setActiveTab] = useState('inventory');

  // State for filters
  const [filters, setFilters] = useState({
    aircraftTypeId: '',
    kitId: '',
    startDate: '',
    endDate: '',
    status: '',
    days: 30
  });

  // Fetch initial data
  useEffect(() => {
    dispatch(fetchKits());
    dispatch(fetchAircraftTypes());
  }, [dispatch]);

  // Define fetchReportData with useCallback to avoid dependency issues
  const fetchReportData = useCallback(() => {
    const reportFilters = {
      aircraft_type_id: filters.aircraftTypeId || undefined,
      kit_id: filters.kitId || undefined,
      start_date: filters.startDate || undefined,
      end_date: filters.endDate || undefined,
      status: filters.status || undefined
    };

    switch (activeTab) {
      case 'inventory':
        dispatch(fetchInventoryReport(reportFilters));
        break;
      case 'issuances':
        if (filters.kitId) {
          dispatch(fetchIssuanceReport({ kitId: filters.kitId, filters: reportFilters }));
        }
        break;
      case 'transfers':
        dispatch(fetchTransferReport(reportFilters));
        break;
      case 'reorders':
        dispatch(fetchReorderReport(reportFilters));
        break;
      case 'utilization':
        dispatch(fetchKitUtilization({ kitId: filters.kitId || null, days: filters.days }));
        break;
      default:
        break;
    }
  }, [activeTab, filters, dispatch]);

  // Fetch report data when tab or filters change
  useEffect(() => {
    fetchReportData();
  }, [fetchReportData]);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters({
      ...filters,
      [name]: value
    });
  };

  const handleExport = (format) => {
    // Export functionality - would integrate with backend export endpoint
    let data;
    let filename;

    switch (activeTab) {
      case 'inventory':
        data = inventoryReport;
        filename = 'kit-inventory-report';
        break;
      case 'issuances':
        data = issuanceReport;
        filename = 'kit-issuance-report';
        break;
      case 'transfers':
        data = transferReport;
        filename = 'kit-transfer-report';
        break;
      case 'reorders':
        data = reorderReport;
        filename = 'kit-reorder-report';
        break;
      default:
        return;
    }

    if (format === 'csv') {
      exportToCSV(data, filename);
    } else if (format === 'json') {
      exportToJSON(data, filename);
    }
  };

  const exportToCSV = (data, filename) => {
    if (!data || data.length === 0) return;

    const headers = Object.keys(data[0]);
    const csvContent = [
      headers.join(','),
      ...data.map(row => headers.map(header => JSON.stringify(row[header] || '')).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const exportToJSON = (data, filename) => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}.json`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const clearFilters = () => {
    setFilters({
      aircraftTypeId: '',
      kitId: '',
      startDate: '',
      endDate: '',
      status: '',
      days: 30
    });
  };

  const selectedKit = filters.kitId
    ? kits.find((kit) => kit.id === parseInt(filters.kitId, 10))
    : null;
  const utilizationScope = utilizationReport?.scope;
  const utilizationData = utilizationReport?.data;
  const utilizationLoading = utilizationReport?.loading;
  const utilizationError = utilizationReport?.error;

  const utilizationSubtitle = filters.kitId
    ? `Usage statistics and trends for ${selectedKit?.name || 'selected kit'}`
    : 'Usage statistics and trends across all kits';

  const renderKitUtilizationAnalytics = (data) => (
    <>
      <Row className="mb-4">
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h6 className="text-muted">Total Issuances</h6>
              <h2>{data?.issuances?.total || 0}</h2>
              <small className="text-muted">
                Avg: {data?.issuances?.average_per_day || 0}/day
              </small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h6 className="text-muted">Transfers In</h6>
              <h2 className="text-success">{data?.transfers?.incoming || 0}</h2>
              <small className="text-muted">Incoming</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h6 className="text-muted">Transfers Out</h6>
              <h2 className="text-danger">{data?.transfers?.outgoing || 0}</h2>
              <small className="text-muted">Outgoing</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h6 className="text-muted">Stock Health</h6>
              <h2>
                {data?.inventory?.stock_health === 'good' ? (
                  <Badge bg="success">Good</Badge>
                ) : data?.inventory?.stock_health === 'warning' ? (
                  <Badge bg="warning">Warning</Badge>
                ) : (
                  <Badge bg="danger">Critical</Badge>
                )}
              </h2>
              <small className="text-muted">
                {data?.inventory?.low_stock_items || 0} low stock items
              </small>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row>
        <Col md={6}>
          <Card className="mb-3">
            <Card.Header>Reorder Status</Card.Header>
            <Card.Body>
              <Table size="sm">
                <tbody>
                  <tr>
                    <td>Pending Reorders</td>
                    <td className="text-end">
                      <Badge bg="warning">{data?.reorders?.pending || 0}</Badge>
                    </td>
                  </tr>
                  <tr>
                    <td>Fulfilled Reorders</td>
                    <td className="text-end">
                      <Badge bg="success">{data?.reorders?.fulfilled || 0}</Badge>
                    </td>
                  </tr>
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card className="mb-3">
            <Card.Header>Inventory Summary</Card.Header>
            <Card.Body>
              <Table size="sm">
                <tbody>
                  <tr>
                    <td>Total Items</td>
                    <td className="text-end">
                      <strong>{data?.inventory?.total_items || 0}</strong>
                    </td>
                  </tr>
                  <tr>
                    <td>Low Stock Items</td>
                    <td className="text-end">
                      <Badge bg={data?.inventory?.low_stock_items > 0 ? 'warning' : 'success'}>
                        {data?.inventory?.low_stock_items || 0}
                      </Badge>
                    </td>
                  </tr>
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </>
  );

  const renderAllKitsUtilizationAnalytics = (data) => {
    const summary = data?.summary || {};
    const totalIssuances = summary.totalIssuances || 0;
    const totalTransfers = summary.totalTransfers || 0;
    const activeKits = summary.activeKits || 0;
    const avgUtilizationValue = Number.isFinite(summary.avgUtilization)
      ? summary.avgUtilization
      : 0;
    const kitsWithActivity = activeKits && avgUtilizationValue
      ? Math.round((avgUtilizationValue / 100) * activeKits)
      : 0;
    const issuancesByKit = [...(data?.issuancesByKit || [])].sort((a, b) => b.value - a.value);
    const transfersByType = data?.transfersByType || [];
    const activityOverTime = data?.activityOverTime || [];

    return (
      <>
        <Row className="mb-4">
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h6 className="text-muted">Total Issuances</h6>
                <h2>{totalIssuances}</h2>
                <small className="text-muted">Last {filters.days} days</small>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h6 className="text-muted">Total Transfers</h6>
                <h2>{totalTransfers}</h2>
                <small className="text-muted">Inbound &amp; outbound</small>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h6 className="text-muted">Active Kits</h6>
                <h2>{activeKits}</h2>
                <small className="text-muted">
                  {kitsWithActivity} kits recorded activity
                </small>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h6 className="text-muted">Average Utilization</h6>
                <h2>{avgUtilizationValue.toFixed(1)}%</h2>
                <small className="text-muted">Across all active kits</small>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        <Row>
          <Col md={6}>
            <Card className="mb-3">
              <Card.Header>Issuances by Kit</Card.Header>
              <Card.Body>
                {issuancesByKit.length > 0 ? (
                  <Table size="sm" responsive>
                    <thead>
                      <tr>
                        <th>Kit</th>
                        <th className="text-end">Issuances</th>
                      </tr>
                    </thead>
                    <tbody>
                      {issuancesByKit.map((entry, index) => (
                        <tr key={entry.name || `issuance-${index}`}>
                          <td>{entry.name || 'Unassigned Kit'}</td>
                          <td className="text-end">{entry.value}</td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                ) : (
                  <Alert variant="info" className="mb-0">
                    No issuance activity recorded in this period
                  </Alert>
                )}
              </Card.Body>
            </Card>
          </Col>
          <Col md={6}>
            <Card className="mb-3">
              <Card.Header>Transfers by Type</Card.Header>
              <Card.Body>
                {transfersByType.length > 0 ? (
                  <Table size="sm" responsive>
                    <thead>
                      <tr>
                        <th>Transfer Type</th>
                        <th className="text-end">Transfers</th>
                      </tr>
                    </thead>
                    <tbody>
                      {transfersByType.map((entry, index) => (
                        <tr key={entry.name || `transfer-${index}`}>
                          <td>{entry.name}</td>
                          <td className="text-end">{entry.value}</td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                ) : (
                  <Alert variant="info" className="mb-0">
                    No transfer activity recorded in this period
                  </Alert>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>

        <Row>
          <Col>
            <Card>
              <Card.Header>Weekly Activity Trend</Card.Header>
              <Card.Body>
                {activityOverTime.length > 0 ? (
                  <Table size="sm" responsive>
                    <thead>
                      <tr>
                        <th>Week</th>
                        <th className="text-end">Issuances</th>
                        <th className="text-end">Transfers</th>
                      </tr>
                    </thead>
                    <tbody>
                      {activityOverTime.map((entry) => (
                        <tr key={entry.date}>
                          <td>{entry.date}</td>
                          <td className="text-end">{entry.issuances}</td>
                          <td className="text-end">{entry.transfers}</td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                ) : (
                  <Alert variant="info" className="mb-0">
                    No weekly activity recorded for the selected range
                  </Alert>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </>
    );
  };

  // Check if user has access
  const hasAccess = user?.is_admin || user?.department === 'Materials';

  if (!hasAccess) {
    return (
      <Container className="mt-4">
        <Alert variant="danger">
          <Alert.Heading>Access Denied</Alert.Heading>
          <p>You do not have permission to view kit reports.</p>
        </Alert>
      </Container>
    );
  }

  if (loading && !inventoryReport.length && !issuanceReport.length) {
    return <LoadingSpinner />;
  }

  return (
    <Container fluid className="kit-reports-page">
      <Row className="mb-4">
        <Col>
          <h3>
            <FaChartBar className="me-2" />
            Kit Reports & Analytics
          </h3>
          <p className="text-muted">
            Comprehensive reporting for kit inventory, issuances, transfers, and utilization
          </p>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" dismissible>
          {error.message || 'An error occurred while loading reports'}
        </Alert>
      )}

      {/* Filters Card */}
      <Card className="mb-4">
        <Card.Header>
          <FaFilter className="me-2" />
          Report Filters
        </Card.Header>
        <Card.Body>
          <Row>
            <Col md={3}>
              <Form.Group className="mb-3">
                <Form.Label>Aircraft Type</Form.Label>
                <Form.Select
                  name="aircraftTypeId"
                  value={filters.aircraftTypeId}
                  onChange={handleFilterChange}
                >
                  <option value="">All Aircraft Types</option>
                  {aircraftTypes.map((type) => (
                    <option key={type.id} value={type.id}>
                      {type.name}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>

            <Col md={3}>
              <Form.Group className="mb-3">
                <Form.Label>Kit</Form.Label>
                <Form.Select
                  name="kitId"
                  value={filters.kitId}
                  onChange={handleFilterChange}
                >
                  <option value="">All Kits</option>
                  {kits.map((kit) => (
                    <option key={kit.id} value={kit.id}>
                      {kit.name}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>

            <Col md={2}>
              <Form.Group className="mb-3">
                <Form.Label>Start Date</Form.Label>
                <Form.Control
                  type="date"
                  name="startDate"
                  value={filters.startDate}
                  onChange={handleFilterChange}
                />
              </Form.Group>
            </Col>

            <Col md={2}>
              <Form.Group className="mb-3">
                <Form.Label>End Date</Form.Label>
                <Form.Control
                  type="date"
                  name="endDate"
                  value={filters.endDate}
                  onChange={handleFilterChange}
                />
              </Form.Group>
            </Col>

            <Col md={2} className="d-flex align-items-end">
              <Button variant="secondary" onClick={clearFilters} className="mb-3 w-100">
                Clear Filters
              </Button>
            </Col>
          </Row>

          <Row>
            <Col className="d-flex justify-content-end">
              <Button
                variant="success"
                className="me-2"
                onClick={() => handleExport('csv')}
              >
                <FaFileExport className="me-2" />
                Export CSV
              </Button>
              <Button
                variant="info"
                onClick={() => handleExport('json')}
              >
                <FaFileExport className="me-2" />
                Export JSON
              </Button>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {/* Reports Tabs */}
      <Tabs
        activeKey={activeTab}
        onSelect={(k) => setActiveTab(k)}
        className="mb-3"
      >
        <Tab eventKey="inventory" title={<><FaBoxes className="me-2" />Inventory</>}>
          <Card>
            <Card.Header>
              <h5>Kit Inventory Report</h5>
              <small className="text-muted">
                Overview of all kits with item counts and stock levels
              </small>
            </Card.Header>
            <Card.Body>
              {inventoryReport.length === 0 ? (
                <Alert variant="info">No inventory data available</Alert>
              ) : (
                <Table striped bordered hover responsive>
                  <thead>
                    <tr>
                      <th>Kit Name</th>
                      <th>Aircraft Type</th>
                      <th>Total Items</th>
                      <th>Low Stock Items</th>
                      <th>Boxes</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {inventoryReport.map((kit) => (
                      <tr key={kit.kit_id}>
                        <td><strong>{kit.kit_name}</strong></td>
                        <td>{kit.aircraft_type}</td>
                        <td>{kit.total_items}</td>
                        <td>
                          {kit.low_stock_items > 0 ? (
                            <Badge bg="warning">{kit.low_stock_items}</Badge>
                          ) : (
                            <Badge bg="success">0</Badge>
                          )}
                        </td>
                        <td>{kit.boxes}</td>
                        <td>
                          {kit.low_stock_items === 0 ? (
                            <Badge bg="success">Good</Badge>
                          ) : kit.low_stock_items < 5 ? (
                            <Badge bg="warning">Warning</Badge>
                          ) : (
                            <Badge bg="danger">Critical</Badge>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>
        </Tab>

        <Tab eventKey="issuances" title="Issuances">
          <Card>
            <Card.Header>
              <h5>Kit Issuance Report</h5>
              <small className="text-muted">
                History of items issued from kits
                {filters.kitId && ` - ${selectedKit?.name || 'Selected Kit'}`}
              </small>
            </Card.Header>
            <Card.Body>
              {!filters.kitId ? (
                <Alert variant="info">
                  Please select a kit from the filters above to view issuance history
                </Alert>
              ) : issuanceReport.length === 0 ? (
                <Alert variant="info">No issuance data available for this kit</Alert>
              ) : (
                <Table striped bordered hover responsive>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Item Type</th>
                      <th>Description</th>
                      <th>Quantity</th>
                      <th>Purpose</th>
                      <th>Work Order</th>
                      <th>Issued By</th>
                    </tr>
                  </thead>
                  <tbody>
                    {issuanceReport.map((issuance) => (
                      <tr key={issuance.id}>
                        <td>{new Date(issuance.issued_date).toLocaleDateString()}</td>
                        <td>
                          <Badge bg="secondary">{issuance.item_type}</Badge>
                        </td>
                        <td>{issuance.description || 'N/A'}</td>
                        <td>{issuance.quantity}</td>
                        <td>{issuance.purpose || 'N/A'}</td>
                        <td>{issuance.work_order || 'N/A'}</td>
                        <td>{issuance.issued_by_name || `User ${issuance.issued_by}`}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>
        </Tab>

        <Tab eventKey="transfers" title={<><FaExchangeAlt className="me-2" />Transfers</>}>
          <Card>
            <Card.Header>
              <h5>Kit Transfer Report</h5>
              <small className="text-muted">
                History of transfers between kits and warehouses
              </small>
            </Card.Header>
            <Card.Body>
              {transferReport.length === 0 ? (
                <Alert variant="info">No transfer data available</Alert>
              ) : (
                <Table striped bordered hover responsive>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>From</th>
                      <th>To</th>
                      <th>Item Type</th>
                      <th>Quantity</th>
                      <th>Status</th>
                      <th>Transferred By</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transferReport.map((transfer) => (
                      <tr key={transfer.id}>
                        <td>{new Date(transfer.transfer_date).toLocaleDateString()}</td>
                        <td>
                          <Badge bg="info">
                            {transfer.from_location_type === 'kit'
                              ? `Kit ${transfer.from_location_id}`
                              : 'Warehouse'}
                          </Badge>
                        </td>
                        <td>
                          <Badge bg="success">
                            {transfer.to_location_type === 'kit'
                              ? `Kit ${transfer.to_location_id}`
                              : 'Warehouse'}
                          </Badge>
                        </td>
                        <td>
                          <Badge bg="secondary">{transfer.item_type}</Badge>
                        </td>
                        <td>{transfer.quantity}</td>
                        <td>
                          {transfer.status === 'completed' ? (
                            <Badge bg="success">Completed</Badge>
                          ) : transfer.status === 'pending' ? (
                            <Badge bg="warning">Pending</Badge>
                          ) : (
                            <Badge bg="danger">Cancelled</Badge>
                          )}
                        </td>
                        <td>{transfer.transferred_by_name || `User ${transfer.transferred_by}`}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>
        </Tab>

        <Tab eventKey="reorders" title={<><FaRedo className="me-2" />Reorders</>}>
          <Card>
            <Card.Header>
              <h5>Kit Reorder Report</h5>
              <small className="text-muted">
                Status of reorder requests across all kits
              </small>
            </Card.Header>
            <Card.Body>
              {reorderReport.length === 0 ? (
                <Alert variant="info">No reorder data available</Alert>
              ) : (
                <Table striped bordered hover responsive>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Kit</th>
                      <th>Part Number</th>
                      <th>Description</th>
                      <th>Quantity</th>
                      <th>Priority</th>
                      <th>Status</th>
                      <th>Requested By</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reorderReport.map((reorder) => (
                      <tr key={reorder.id}>
                        <td>{new Date(reorder.requested_date).toLocaleDateString()}</td>
                        <td>{reorder.kit_name || `Kit ${reorder.kit_id}`}</td>
                        <td><code>{reorder.part_number}</code></td>
                        <td>{reorder.description}</td>
                        <td>{reorder.quantity_requested}</td>
                        <td>
                          {reorder.priority === 'urgent' ? (
                            <Badge bg="danger">Urgent</Badge>
                          ) : reorder.priority === 'high' ? (
                            <Badge bg="warning">High</Badge>
                          ) : reorder.priority === 'medium' ? (
                            <Badge bg="info">Medium</Badge>
                          ) : (
                            <Badge bg="secondary">Low</Badge>
                          )}
                        </td>
                        <td>
                          {reorder.status === 'fulfilled' ? (
                            <Badge bg="success">Fulfilled</Badge>
                          ) : reorder.status === 'approved' ? (
                            <Badge bg="info">Approved</Badge>
                          ) : reorder.status === 'ordered' ? (
                            <Badge bg="primary">Ordered</Badge>
                          ) : reorder.status === 'pending' ? (
                            <Badge bg="warning">Pending</Badge>
                          ) : (
                            <Badge bg="danger">Cancelled</Badge>
                          )}
                        </td>
                        <td>{reorder.requested_by_name || `User ${reorder.requested_by}`}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>
        </Tab>

        <Tab eventKey="utilization" title={<><FaChartBar className="me-2" />Utilization</>}>
          <Card>
            <Card.Header>
              <h5>Kit Utilization Analytics</h5>
              <small className="text-muted">
                {utilizationSubtitle} • Last {filters.days} days
              </small>
            </Card.Header>
            <Card.Body>
              {utilizationLoading || utilizationScope === null ? (
                <div className="py-4">
                  <LoadingSpinner text="Loading utilization data..." size="sm" />
                </div>
              ) : utilizationError ? (
                <Alert variant="danger" className="mb-0">
                  {utilizationError.message || 'An error occurred while loading utilization analytics.'}
                </Alert>
              ) : filters.kitId ? (
                utilizationScope === 'kit' && utilizationData ? (
                  renderKitUtilizationAnalytics(utilizationData)
                ) : (
                  <Alert variant="info" className="mb-0">
                    No utilization data available for this kit
                  </Alert>
                )
              ) : utilizationScope === 'all' && utilizationData ? (
                renderAllKitsUtilizationAnalytics(utilizationData)
              ) : (
                <Alert variant="info" className="mb-0">
                  No utilization data available for the selected time period
                </Alert>
              )}
            </Card.Body>
          </Card>
        </Tab>
      </Tabs>
    </Container>
  );
};

export default KitReports;

