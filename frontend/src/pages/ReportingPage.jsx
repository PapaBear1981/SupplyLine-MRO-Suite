import { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Navigate } from 'react-router-dom';
import { Container, Row, Col, Card, Alert, Button } from 'react-bootstrap';
import ReportSelector from '../components/reports/ReportSelector';
import ReportViewer from '../components/reports/ReportViewer';
import ExportControls from '../components/reports/ExportControls';
import ChemicalWasteAnalytics from '../components/reports/ChemicalWasteAnalytics';
import ChemicalUsageAnalytics from '../components/reports/ChemicalUsageAnalytics';
import PartNumberAnalytics from '../components/reports/PartNumberAnalytics';
import CalibrationReports from '../components/reports/CalibrationReports';
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
  const [chemicalAnalyticsTab, setChemicalAnalyticsTab] = useState('waste');
  const [calibrationReportsTab, setCalibrationReportsTab] = useState('due');

  const isAdmin = user?.is_admin || user?.department === 'Materials';

  // Fetch report data when report type, timeframe, or filters change
  useEffect(() => {
    if (currentReport && timeframe) {
      fetchReportData();
    }
  }, [currentReport, timeframe, filters, dispatch]);

  // Redirect if user doesn't have permission
  if (!isAdmin) {
    return <Navigate to="/tools" replace />;
  }

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

      <div className="btn-group mb-4">
        <Button
          variant={activeTab === 'standard-reports' ? 'primary' : 'outline-primary'}
          onClick={() => setActiveTab('standard-reports')}
        >
          Tool Reports
        </Button>
        <Button
          variant={activeTab === 'chemical-analytics' ? 'primary' : 'outline-primary'}
          onClick={() => setActiveTab('chemical-analytics')}
        >
          Chemical Analytics
        </Button>
        <Button
          variant={activeTab === 'calibration-reports' ? 'primary' : 'outline-primary'}
          onClick={() => setActiveTab('calibration-reports')}
        >
          Calibration Reports
        </Button>
        <Button
          variant={activeTab === 'part-number-analytics' ? 'primary' : 'outline-primary'}
          onClick={() => setActiveTab('part-number-analytics')}
        >
          Part Number Analytics
        </Button>
      </div>

      {activeTab === 'standard-reports' && (
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
      )}

      {activeTab === 'chemical-analytics' && (
        <div className="pt-4">
          <Card className="shadow-sm mb-4">
            <Card.Header className="bg-light">
              <div className="btn-group mb-3">
                <Button
                  variant={chemicalAnalyticsTab === 'waste' ? 'primary' : 'outline-primary'}
                  onClick={() => setChemicalAnalyticsTab('waste')}
                >
                  Waste Analytics
                </Button>
                <Button
                  variant={chemicalAnalyticsTab === 'usage' ? 'primary' : 'outline-primary'}
                  onClick={() => setChemicalAnalyticsTab('usage')}
                >
                  Usage Analytics
                </Button>
              </div>
            </Card.Header>
            <Card.Body>
              {chemicalAnalyticsTab === 'waste' && (
                <div className="pt-3">
                  <ChemicalWasteAnalytics />
                </div>
              )}
              {chemicalAnalyticsTab === 'usage' && (
                <div className="pt-3">
                  <ChemicalUsageAnalytics />
                </div>
              )}
            </Card.Body>
          </Card>
        </div>
      )}

      {activeTab === 'calibration-reports' && (
        <div className="pt-4">
          <CalibrationReports />
        </div>
      )}

      {activeTab === 'part-number-analytics' && (
        <div className="pt-4">
          <PartNumberAnalytics />
        </div>
      )}
    </div>
  );
};

export default ReportingPage;
