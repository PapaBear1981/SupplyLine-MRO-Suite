import { useState, useEffect } from 'react';
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
} from '../store/kitsSlice';
import LoadingSpinner from '../components/common/LoadingSpinner';
import {
  FaChartBar, FaBoxes, FaExchangeAlt, FaRedo, FaFileExport, FaCalendar, FaFilter, FaFilePdf
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
import jsPDF from 'jspdf';
import 'jspdf-autotable';

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

  // Fetch report data when tab or filters change
  useEffect(() => {
    fetchReportData();
  }, [activeTab, filters]);

  const fetchReportData = () => {
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
        if (filters.kitId) {
          dispatch(fetchKitUtilization({ kitId: filters.kitId, days: filters.days }));
        }
        break;
      default:
        break;
    }
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters({
      ...filters,
      [name]: value
    });
  };

  const handleExport = (format) => {
    let data;
    let filename;
    let title;

    switch (activeTab) {
      case 'inventory':
        data = inventoryReport;
        filename = 'kit-inventory-report';
        title = 'Kit Inventory Report';
        break;
      case 'issuances':
        data = issuanceReport;
        filename = 'kit-issuance-report';
        title = 'Kit Issuance Report';
        break;
      case 'transfers':
        data = transferReport;
        filename = 'kit-transfer-report';
        title = 'Kit Transfer Report';
        break;
      case 'reorders':
        data = reorderReport;
        filename = 'kit-reorder-report';
        title = 'Kit Reorder Report';
        break;
      default:
        return;
    }

    if (!data || data.length === 0) {
      alert('No data available to export');
      return;
    }

    if (format === 'csv') {
      exportToCSV(data, filename);
    } else if (format === 'pdf') {
      exportToPDF(data, filename, title);
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

  const exportToPDF = (data, filename, title) => {
    if (!data || data.length === 0) return;

    const doc = new jsPDF('l', 'mm', 'a4'); // Landscape orientation

    // Add title
    doc.setFontSize(18);
    doc.text(title, 14, 15);

    // Add date
    doc.setFontSize(10);
    doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 22);

    // Prepare table data based on report type
    let columns = [];
    let rows = [];

    switch (activeTab) {
      case 'inventory':
        columns = ['Kit Name', 'Aircraft Type', 'Total Items', 'Low Stock Items', 'Boxes', 'Status'];
        rows = data.map(kit => [
          kit.kit_name,
          kit.aircraft_type || 'N/A',
          kit.total_items,
          kit.low_stock_items,
          kit.boxes,
          kit.low_stock_items === 0 ? 'Good' : kit.low_stock_items < 5 ? 'Warning' : 'Critical'
        ]);
        break;
      case 'issuances':
        columns = ['Date', 'Item Type', 'Description', 'Quantity', 'Purpose', 'Work Order', 'Issued By'];
        rows = data.map(issuance => [
          new Date(issuance.issued_date).toLocaleDateString(),
          issuance.item_type,
          issuance.description || 'N/A',
          issuance.quantity,
          issuance.purpose || 'N/A',
          issuance.work_order || 'N/A',
          issuance.issued_by_name || `User ${issuance.issued_by}`
        ]);
        break;
      case 'transfers':
        columns = ['Date', 'From', 'To', 'Item Type', 'Quantity', 'Status', 'Transferred By'];
        rows = data.map(transfer => [
          new Date(transfer.transfer_date).toLocaleDateString(),
          transfer.from_location_type === 'kit' ? `Kit ${transfer.from_location_id}` : 'Warehouse',
          transfer.to_location_type === 'kit' ? `Kit ${transfer.to_location_id}` : 'Warehouse',
          transfer.item_type,
          transfer.quantity,
          transfer.status,
          transfer.transferred_by_name || `User ${transfer.transferred_by}`
        ]);
        break;
      case 'reorders':
        columns = ['Date', 'Kit', 'Part Number', 'Description', 'Quantity', 'Priority', 'Status', 'Requested By'];
        rows = data.map(reorder => [
          new Date(reorder.requested_date).toLocaleDateString(),
          reorder.kit_name || `Kit ${reorder.kit_id}`,
          reorder.part_number,
          reorder.description,
          reorder.quantity_requested,
          reorder.priority,
          reorder.status,
          reorder.requested_by_name || `User ${reorder.requested_by}`
        ]);
        break;
      default:
        return;
    }

    // Add table
    doc.autoTable({
      head: [columns],
      body: rows,
      startY: 28,
      styles: { fontSize: 8 },
      headStyles: { fillColor: [41, 128, 185] },
      alternateRowStyles: { fillColor: [245, 245, 245] },
      margin: { top: 28 }
    });

    // Save the PDF
    doc.save(`${filename}.pdf`);
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
          <h2>
            <FaChartBar className="me-2" />
            Kit Reports & Analytics
          </h2>
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
                disabled={loading}
              >
                <FaFileExport className="me-2" />
                Export CSV
              </Button>
              <Button
                variant="danger"
                onClick={() => handleExport('pdf')}
                disabled={loading}
              >
                <FaFilePdf className="me-2" />
                Export PDF
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
                {filters.kitId && ` - ${kits.find(k => k.id === parseInt(filters.kitId))?.name || 'Selected Kit'}`}
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
              {!reorderReport || reorderReport.length === 0 ? (
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
                        <td>{reorder.requested_by_name || reorder.requester_name || `User ${reorder.requested_by}`}</td>
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
                Usage statistics and trends for selected kit
                {filters.kitId && ` - ${kits.find(k => k.id === parseInt(filters.kitId))?.name || 'Selected Kit'}`}
              </small>
            </Card.Header>
            <Card.Body>
              {!filters.kitId ? (
                <Alert variant="info">
                  Please select a kit from the filters above to view utilization analytics
                </Alert>
              ) : !utilizationReport ? (
                <Alert variant="info">No utilization data available for this kit</Alert>
              ) : (
                <>
                  <Row className="mb-4">
                    <Col md={3}>
                      <Card className="text-center">
                        <Card.Body>
                          <h6 className="text-muted">Total Issuances</h6>
                          <h2>{utilizationReport.issuances?.total || 0}</h2>
                          <small className="text-muted">
                            Avg: {utilizationReport.issuances?.average_per_day || 0}/day
                          </small>
                        </Card.Body>
                      </Card>
                    </Col>
                    <Col md={3}>
                      <Card className="text-center">
                        <Card.Body>
                          <h6 className="text-muted">Transfers In</h6>
                          <h2 className="text-success">
                            {utilizationReport.transfers?.incoming || 0}
                          </h2>
                          <small className="text-muted">Incoming</small>
                        </Card.Body>
                      </Card>
                    </Col>
                    <Col md={3}>
                      <Card className="text-center">
                        <Card.Body>
                          <h6 className="text-muted">Transfers Out</h6>
                          <h2 className="text-danger">
                            {utilizationReport.transfers?.outgoing || 0}
                          </h2>
                          <small className="text-muted">Outgoing</small>
                        </Card.Body>
                      </Card>
                    </Col>
                    <Col md={3}>
                      <Card className="text-center">
                        <Card.Body>
                          <h6 className="text-muted">Stock Health</h6>
                          <h2>
                            {utilizationReport.inventory?.stock_health === 'good' ? (
                              <Badge bg="success">Good</Badge>
                            ) : utilizationReport.inventory?.stock_health === 'warning' ? (
                              <Badge bg="warning">Warning</Badge>
                            ) : (
                              <Badge bg="danger">Critical</Badge>
                            )}
                          </h2>
                          <small className="text-muted">
                            {utilizationReport.inventory?.low_stock_items || 0} low stock items
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
                                  <Badge bg="warning">
                                    {utilizationReport.reorders?.pending || 0}
                                  </Badge>
                                </td>
                              </tr>
                              <tr>
                                <td>Fulfilled Reorders</td>
                                <td className="text-end">
                                  <Badge bg="success">
                                    {utilizationReport.reorders?.fulfilled || 0}
                                  </Badge>
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
                                  <strong>{utilizationReport.inventory?.total_items || 0}</strong>
                                </td>
                              </tr>
                              <tr>
                                <td>Low Stock Items</td>
                                <td className="text-end">
                                  <Badge bg={utilizationReport.inventory?.low_stock_items > 0 ? 'warning' : 'success'}>
                                    {utilizationReport.inventory?.low_stock_items || 0}
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
              )}
            </Card.Body>
          </Card>
        </Tab>
      </Tabs>
    </Container>
  );
};

export default KitReports;

