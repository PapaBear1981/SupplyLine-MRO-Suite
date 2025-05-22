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
import CycleCountReports from '../components/reports/CycleCountReports';
import Tooltip from '../components/common/Tooltip';
import HelpIcon from '../components/common/HelpIcon';
import HelpContent from '../components/common/HelpContent';
import { useHelp } from '../context/HelpContext';
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
  const { showTooltips, showHelp } = useHelp();

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

      {showHelp && (
        <HelpContent title="Reports & Analytics" initialOpen={false}>
          <p>This page provides access to various reports and analytics tools to help you analyze tool usage, chemical consumption, and calibration data.</p>
          <ul>
            <li><strong>Tool Reports:</strong> Generate reports on tool inventory, checkout history, and department usage.</li>
            <li><strong>Chemical Analytics:</strong> Analyze chemical waste and usage patterns.</li>
            <li><strong>Calibration Reports:</strong> Track calibration status, history, and compliance.</li>
            <li><strong>Cycle Count Reports:</strong> View inventory accuracy, discrepancies, performance, and coverage.</li>
            <li><strong>Part Number Analytics:</strong> Analyze part number usage and trends.</li>
          </ul>
          <p>Use the tabs at the top to switch between different report types. Each report type has its own set of options and filters.</p>
        </HelpContent>
      )}

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
        <Tooltip text="View tool inventory and usage reports" placement="top" show={showTooltips}>
          <Button
            variant={activeTab === 'standard-reports' ? 'primary' : 'outline-primary'}
            onClick={() => setActiveTab('standard-reports')}
          >
            Tool Reports
          </Button>
        </Tooltip>
        <Tooltip text="Analyze chemical waste and usage patterns" placement="top" show={showTooltips}>
          <Button
            variant={activeTab === 'chemical-analytics' ? 'primary' : 'outline-primary'}
            onClick={() => setActiveTab('chemical-analytics')}
          >
            Chemical Analytics
          </Button>
        </Tooltip>
        <Tooltip text="View calibration status and history reports" placement="top" show={showTooltips}>
          <Button
            variant={activeTab === 'calibration-reports' ? 'primary' : 'outline-primary'}
            onClick={() => setActiveTab('calibration-reports')}
          >
            Calibration Reports
          </Button>
        </Tooltip>
        <Tooltip text="View cycle count reports and analytics" placement="top" show={showTooltips}>
          <Button
            variant={activeTab === 'cycle-count-reports' ? 'primary' : 'outline-primary'}
            onClick={() => setActiveTab('cycle-count-reports')}
          >
            Cycle Count Reports
          </Button>
        </Tooltip>
        <Tooltip text="Analyze part number usage and trends" placement="top" show={showTooltips}>
          <Button
            variant={activeTab === 'part-number-analytics' ? 'primary' : 'outline-primary'}
            onClick={() => setActiveTab('part-number-analytics')}
          >
            Part Number Analytics
          </Button>
        </Tooltip>
      </div>

      {activeTab === 'standard-reports' && (
        <div className="pt-4">
          <Card className="shadow-sm mb-4">
            <Card.Header className="bg-light">
              <div className="d-flex justify-content-between align-items-center">
                <h4 className="mb-0">Report Options</h4>
                {showHelp && (
                  <HelpIcon
                    title="Report Options"
                    content={
                      <>
                        <p>Configure your report using these options:</p>
                        <ul>
                          <li>Select the report type (Tool Inventory, Checkout History, etc.)</li>
                          <li>Choose a time period for time-based reports</li>
                          <li>Apply filters to narrow down your results</li>
                        </ul>
                      </>
                    }
                    size="sm"
                  />
                )}
              </div>
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
              <div className="d-flex align-items-center">
                <h4 className="mb-0">Report Results</h4>
                {showHelp && (
                  <HelpIcon
                    title="Report Results"
                    content={
                      <>
                        <p>This section displays the results of your report based on the selected options and filters.</p>
                        <p>Different report types will display different visualizations and data tables.</p>
                        <p>Use the export buttons to download the report in PDF or Excel format.</p>
                      </>
                    }
                    size="sm"
                  />
                )}
              </div>
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

      {activeTab === 'cycle-count-reports' && (
        <div className="pt-4">
          <CycleCountReports />
        </div>
      )}
    </div>
  );
};

export default ReportingPage;
