import { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Navigate } from 'react-router-dom';
import { Container, Row, Col, Card, Alert, Tabs, Tab } from 'react-bootstrap';
import ReportSelector from '../components/reports/ReportSelector';
import ReportViewer from '../components/reports/ReportViewer';
import ExportControls from '../components/reports/ExportControls';
import ChemicalWasteAnalytics from '../components/reports/ChemicalWasteAnalytics';
import {
  fetchToolInventoryReport,
  fetchCheckoutHistoryReport,
  fetchDepartmentUsageReport,
  setReportType,
  setTimeframe,
  setFilters
} from '../store/reportSlice';
import ReportService from '../services/reportService';

const ReportingPage = () => {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const {
    currentReport,
    timeframe,
    filters,
    data,
    loading,
    error
  } = useSelector((state) => state.reports);

  const [exportLoading, setExportLoading] = useState(false);
  const [exportError, setExportError] = useState(null);
  const [activeTab, setActiveTab] = useState('standard-reports');

  const isAdmin = user?.is_admin || user?.department === 'Materials';

  // Redirect if user doesn't have permission
  if (!isAdmin) {
    return <Navigate to="/tools" replace />;
  }

  // Fetch report data when report type, timeframe, or filters change
  useEffect(() => {
    if (currentReport && timeframe) {
      fetchReportData();
    }
  }, [currentReport, timeframe, filters]);

  const fetchReportData = () => {
    switch (currentReport) {
      case 'tool-inventory':
        dispatch(fetchToolInventoryReport(filters));
        break;
      case 'checkout-history':
        dispatch(fetchCheckoutHistoryReport({ timeframe, filters }));
        break;
      case 'department-usage':
        dispatch(fetchDepartmentUsageReport({ timeframe }));
        break;
      default:
        break;
    }
  };

  const handleReportTypeChange = (reportType) => {
    dispatch(setReportType(reportType));
  };

  const handleTimeframeChange = (timeframe) => {
    dispatch(setTimeframe(timeframe));
  };

  const handleFilterChange = (filters) => {
    dispatch(setFilters(filters));
  };

  const handleExport = async (format) => {
    if (!data) return;

    setExportLoading(true);
    setExportError(null);

    try {
      if (format === 'pdf') {
        ReportService.exportAsPdf(data, currentReport, timeframe);
      } else if (format === 'excel') {
        ReportService.exportAsExcel(data, currentReport, timeframe);
      }
    } catch (err) {
      console.error('Export error:', err);
      setExportError(`Failed to export as ${format.toUpperCase()}: ${err.message}`);
    } finally {
      setExportLoading(false);
    }
  };

  return (
    <div className="w-100">
      <h1 className="mb-4">Reports & Analytics</h1>

      {error && (
        <Alert variant="danger" className="mb-4">
          {error.message || 'An error occurred while fetching report data'}
        </Alert>
      )}

      {exportError && (
        <Alert variant="danger" className="mb-4" dismissible onClose={() => setExportError(null)}>
          {exportError}
        </Alert>
      )}

      <Tabs
        activeKey={activeTab}
        onSelect={(k) => setActiveTab(k)}
        className="mb-4"
      >
        <Tab eventKey="standard-reports" title="Tool Reports">
          <div className="pt-4">
            <Card className="shadow-sm mb-4">
              <Card.Header className="bg-light">
                <h4 className="mb-0">Report Options</h4>
              </Card.Header>
              <Card.Body>
                <ReportSelector
                  currentReport={currentReport}
                  timeframe={timeframe}
                  filters={filters}
                  onReportTypeChange={handleReportTypeChange}
                  onTimeframeChange={handleTimeframeChange}
                  onFilterChange={handleFilterChange}
                />
              </Card.Body>
            </Card>

            <Card className="shadow-sm mb-4">
              <Card.Header className="bg-light d-flex justify-content-between align-items-center">
                <h4 className="mb-0">Report Results</h4>
                <ExportControls
                  onExport={handleExport}
                  loading={exportLoading}
                  disabled={!data || loading}
                />
              </Card.Header>
              <Card.Body>
                <ReportViewer
                  reportType={currentReport}
                  timeframe={timeframe}
                  data={data}
                  loading={loading}
                />
              </Card.Body>
            </Card>
          </div>
        </Tab>

        <Tab eventKey="chemical-waste" title="Chemical Waste Analytics">
          <div className="pt-4">
            <ChemicalWasteAnalytics />
          </div>
        </Tab>
      </Tabs>
    </div>
  );
};

export default ReportingPage;
