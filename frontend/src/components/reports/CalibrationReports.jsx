import { useState, useEffect } from 'react';
import { Card, Row, Col, Form, Button, Table, Alert, Spinner } from 'react-bootstrap';
import { useSelector } from 'react-redux';
import api from '../../services/api';
import { saveAs } from 'file-saver';
import * as XLSX from 'xlsx';
import { formatDate } from '../../utils/dateUtils';

const CalibrationReports = () => {
  const { user } = useSelector((state) => state.auth);
  const [reportType, setReportType] = useState('due');
  const [dateRange, setDateRange] = useState('30');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [reportData, setReportData] = useState([]);
  const [error, setError] = useState(null);

  // Check if user has permission to view reports
  const hasPermission = user?.is_admin || user?.department === 'Materials';

  useEffect(() => {
    // Reset dates when report type changes
    if (reportType === 'due' || reportType === 'overdue') {
      setStartDate('');
      setEndDate('');
    }
  }, [reportType]);

  const fetchReportData = async () => {
    setLoading(true);
    setError(null);

    try {
      let endpoint = '';
      let params = new URLSearchParams();

      if (reportType === 'due') {
        endpoint = '/calibrations/due';
        params.append('days', dateRange);
      } else if (reportType === 'overdue') {
        endpoint = '/calibrations/overdue';
      } else if (reportType === 'history') {
        endpoint = '/calibrations';

        if (startDate) {
          params.append('start_date', startDate);
        }

        if (endDate) {
          params.append('end_date', endDate);
        }

        params.append('limit', 1000); // Get a large number of records for the report
      } else if (reportType === 'compliance') {
        endpoint = '/reports/calibration-compliance';
      }

      console.log(`Fetching report data from: ${endpoint}?${params.toString()}`);
      const response = await api.get(`${endpoint}?${params.toString()}`);

      // For calibrations endpoint, the data is in the calibrations property
      const data = reportType === 'history' ? response.data.calibrations : response.data;

      console.log('Report data received:', data);

      if (Array.isArray(data)) {
        setReportData(data);
      } else {
        console.error('Received non-array data:', data);
        setError('Received invalid data format from server. Please try again later.');
        setReportData([]);
      }
    } catch (err) {
      console.error('Error fetching report data:', err);
      setError('Failed to fetch report data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = (e) => {
    e.preventDefault();
    fetchReportData();
  };

  const exportToExcel = () => {
    if (!reportData || reportData.length === 0) return;

    // Create worksheet from report data
    const worksheet = XLSX.utils.json_to_sheet(reportData.map(item => {
      const data = { ...item };

      // Format dates for Excel using our standardized date formatter
      if (data.calibration_date) {
        data.calibration_date = formatDate(data.calibration_date);
      }

      if (data.next_calibration_date) {
        data.next_calibration_date = formatDate(data.next_calibration_date);
      }

      if (data.last_calibration_date) {
        data.last_calibration_date = formatDate(data.last_calibration_date);
      }

      return data;
    }));

    // Create workbook and add the worksheet
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Calibration Report');

    // Generate Excel file
    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
    const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });

    // Save file
    const fileName = `calibration-${reportType}-report-${new Date().toISOString().split('T')[0]}.xlsx`;
    saveAs(blob, fileName);
  };

  const exportToPDF = () => {
    // In a real implementation, you would generate a PDF file
    // For now, we'll just show an alert
    alert('PDF export functionality would be implemented here');
  };

  if (!hasPermission) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Access Denied</Alert.Heading>
        <p>
          You do not have permission to view calibration reports.
          This feature is only available to administrators and Materials department personnel.
        </p>
      </Alert>
    );
  }

  return (
    <Card>
      <Card.Header>
        <h4>Calibration Reports</h4>
      </Card.Header>
      <Card.Body>
        <Form onSubmit={handleGenerateReport}>
          <Row className="mb-3">
            <Col md={4}>
              <Form.Group>
                <Form.Label>Report Type</Form.Label>
                <Form.Select
                  value={reportType}
                  onChange={(e) => setReportType(e.target.value)}
                >
                  <option value="due">Calibrations Due</option>
                  <option value="overdue">Overdue Calibrations</option>
                  <option value="history">Calibration History</option>
                  <option value="compliance">Calibration Compliance</option>
                </Form.Select>
              </Form.Group>
            </Col>

            {reportType === 'due' && (
              <Col md={4}>
                <Form.Group>
                  <Form.Label>Due Within</Form.Label>
                  <Form.Select
                    value={dateRange}
                    onChange={(e) => setDateRange(e.target.value)}
                  >
                    <option value="7">Next 7 Days</option>
                    <option value="30">Next 30 Days</option>
                    <option value="90">Next 90 Days</option>
                    <option value="180">Next 180 Days</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            )}

            {reportType === 'history' && (
              <>
                <Col md={4}>
                  <Form.Group>
                    <Form.Label>Start Date</Form.Label>
                    <Form.Control
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                    />
                  </Form.Group>
                </Col>
                <Col md={4}>
                  <Form.Group>
                    <Form.Label>End Date</Form.Label>
                    <Form.Control
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                    />
                  </Form.Group>
                </Col>
              </>
            )}
          </Row>

          <div className="d-flex justify-content-between">
            <Button type="submit" variant="primary" disabled={loading}>
              {loading ? (
                <>
                  <Spinner
                    as="span"
                    animation="border"
                    size="sm"
                    role="status"
                    aria-hidden="true"
                    className="me-2"
                  />
                  Generating...
                </>
              ) : (
                'Generate Report'
              )}
            </Button>

            {reportData.length > 0 && (
              <div>
                <Button
                  variant="success"
                  className="me-2"
                  onClick={exportToExcel}
                >
                  <i className="bi bi-file-excel me-2"></i>
                  Export to Excel
                </Button>
                <Button
                  variant="danger"
                  onClick={exportToPDF}
                >
                  <i className="bi bi-file-pdf me-2"></i>
                  Export to PDF
                </Button>
              </div>
            )}
          </div>
        </Form>

        {error && (
          <Alert variant="danger" className="mt-3">
            {error}
          </Alert>
        )}

        {loading ? (
          <div className="text-center my-4">
            <Spinner animation="border" role="status" />
            <p className="mt-2">Loading report data...</p>
          </div>
        ) : reportData.length > 0 ? (
          <div className="mt-4">
            <h5>
              {reportType === 'due' && `Calibrations Due in the Next ${dateRange} Days`}
              {reportType === 'overdue' && 'Overdue Calibrations'}
              {reportType === 'history' && 'Calibration History'}
              {reportType === 'compliance' && 'Calibration Compliance'}
            </h5>

            <Table striped bordered hover responsive className="mt-3">
              <thead>
                <tr>
                  <th>Tool Number</th>
                  <th>Serial Number</th>
                  <th>Description</th>
                  {(reportType === 'history' || reportType === 'compliance') && (
                    <th>Last Calibration</th>
                  )}
                  <th>Next Due Date</th>
                  {reportType === 'compliance' && (
                    <th>Status</th>
                  )}
                </tr>
              </thead>
              <tbody>
                {reportData.map((item) => (
                  <tr key={item.id}>
                    <td>{item.tool_number}</td>
                    <td>{item.serial_number}</td>
                    <td>{item.description || 'N/A'}</td>
                    {(reportType === 'history' || reportType === 'compliance') && (
                      <td>
                        {item.last_calibration_date || item.calibration_date
                          ? formatDate(item.last_calibration_date || item.calibration_date)
                          : 'Never'}
                      </td>
                    )}
                    <td>
                      {formatDate(item.next_calibration_date)}
                    </td>
                    {reportType === 'compliance' && (
                      <td>
                        {item.calibration_status === 'current' ? 'Current' :
                         item.calibration_status === 'due_soon' ? 'Due Soon' :
                         item.calibration_status === 'overdue' ? 'Overdue' : 'N/A'}
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </Table>
          </div>
        ) : (
          <Alert variant="info" className="mt-3">
            {error ? error : reportType === 'due'
              ? `No calibrations are due within the next ${dateRange} days.`
              : reportType === 'overdue'
                ? 'No overdue calibrations found.'
                : reportType === 'history'
                  ? 'No calibration history records found.'
                  : 'No calibration compliance data found.'}
          </Alert>
        )}
      </Card.Body>
    </Card>
  );
};

export default CalibrationReports;
