import { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Navigate, useLocation } from 'react-router-dom';
import { Container, Row, Col, Card, Alert, Button } from 'react-bootstrap';
import ReportSelector from '../components/reports/ReportSelector';
import ReportViewer from '../components/reports/ReportViewer';
import ExportControls from '../components/reports/ExportControls';
import ChemicalWasteAnalytics from '../components/reports/ChemicalWasteAnalytics';
import ChemicalUsageAnalytics from '../components/reports/ChemicalUsageAnalytics';
import PartNumberAnalytics from '../components/reports/PartNumberAnalytics';
import CalibrationReports from '../components/reports/CalibrationReports';
import KitReports from '../components/reports/KitReports';
import Tooltip from '../components/common/Tooltip';
import HelpIcon from '../components/common/HelpIcon';
import HelpContent from '../components/common/HelpContent';
import { useHelp } from '../context/HelpContext';
import { hasPermission } from '../components/auth/ProtectedRoute';
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
  const location = useLocation();
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
  const [chemicalAnalyticsTab, setChemicalAnalyticsTab] = useState('waste');
  const { showTooltips, showHelp } = useHelp();

  // Check permissions - allow access if user has either page.reports or page.kits
  const hasReportsPermission = hasPermission(user, 'page.reports');
  const hasKitsPermission = hasPermission(user, 'page.kits');
  const hasAccess = hasReportsPermission || hasKitsPermission;

  // Set initial activeTab from location state if provided, otherwise default based on permissions
  // If user only has kits permission, default to kit-reports; otherwise default to standard-reports
  const [activeTab, setActiveTab] = useState(() => {
    // Use location state if available, otherwise default to standard-reports
    // The useEffect below will adjust if needed based on permissions
    return location.state?.activeTab || 'standard-reports';
  });

  // Adjust default tab based on permissions if no location state was provided
  useEffect(() => {
    if (!location.state?.activeTab) {
      const defaultTab = hasKitsPermission && !hasReportsPermission ? 'kit-reports' : 'standard-reports';
      setActiveTab(defaultTab);
    }
  }, [hasKitsPermission, hasReportsPermission, location.state]);

  // Redirect if user doesn't have permission
  if (!hasAccess) {
    return <Navigate to="/dashboard" replace />;
  }

  // Fetch report data when report type, timeframe, or filters change
  useEffect(() => {
    if (currentReport && timeframe) {
      fetchReportData();
    }
  }, [currentReport, timeframe, filters, dispatch]);

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
      // CYCLE COUNT REPORTS - TEMPORARILY DISABLED
      // ==========================================
      // All cycle count report functionality has been disabled due to GitHub Issue #366
      //
      // REASON FOR DISABLING:
      // - Backend cycle count API endpoints are non-functional
      // - Report generation fails with "Resource not found" errors
      // - Users cannot access cycle count analytics and reporting
      // - Production stability requires disabling broken report types
      //
      // REPORTS DISABLED:
      // - cycle-count-accuracy: Inventory accuracy analysis from cycle counts
      // - cycle-count-discrepancies: Discrepancy tracking and resolution reports
      // - cycle-count-performance: Cycle count team performance metrics
      // - cycle-count-coverage: Inventory coverage and frequency analysis
      //
      // TO RE-ENABLE:
      // 1. Uncomment all case statements below
      // 2. Ensure backend cycle count routes are functional
      // 3. Verify cycle count data exists in database
      // 4. Test report generation thoroughly
      // 5. Update report type dropdown options (see reportTypes array)
      //
      // DISABLED DATE: 2025-06-22
      // GITHUB ISSUE: #366
      //
      // case 'cycle-count-accuracy':
      //   dispatch(fetchCycleCountAccuracyReport({ timeframe, filters }));
      //   break;
      // case 'cycle-count-discrepancies':
      //   dispatch(fetchCycleCountDiscrepancyReport({ timeframe, filters }));
      //   break;
      // case 'cycle-count-performance':
      //   dispatch(fetchCycleCountPerformanceReport({ timeframe, filters }));
      //   break;
      // case 'cycle-count-coverage':
      //   dispatch(fetchCycleCountCoverageReport({ timeframe, filters }));
      //   break;
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
            {/* CYCLE COUNT REPORTS DESCRIPTION - DISABLED */}
            {/* The cycle count reports description has been removed due to GitHub Issue #366 */}
            {/* This feature will be restored when the cycle count system is re-enabled */}
            {/* <li><strong>Cycle Count Reports:</strong> Analyze inventory accuracy, discrepancies, performance, and coverage from cycle counting activities.</li> */}
            <li><strong>Kit Reports:</strong> Generate reports on kit inventory, issuances, transfers, reorders, and utilization.</li>
            <li><strong>Chemical Analytics:</strong> Analyze chemical waste and usage patterns.</li>
            <li><strong>Calibration Reports:</strong> Track calibration status, history, and compliance.</li>
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
        {hasReportsPermission && (
          <Tooltip text="View tool inventory and usage reports" placement="top" show={showTooltips}>
            <Button
              variant={activeTab === 'standard-reports' ? 'primary' : 'outline-primary'}
              onClick={() => setActiveTab('standard-reports')}
            >
              Tool Reports
            </Button>
          </Tooltip>
        )}
        {hasKitsPermission && (
          <Tooltip text="View kit inventory, issuances, transfers, and utilization reports" placement="top" show={showTooltips}>
            <Button
              variant={activeTab === 'kit-reports' ? 'primary' : 'outline-primary'}
              onClick={() => setActiveTab('kit-reports')}
            >
              Kit Reports
            </Button>
          </Tooltip>
        )}
        {hasReportsPermission && (
          <>
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
            <Tooltip text="Analyze part number usage and trends" placement="top" show={showTooltips}>
              <Button
                variant={activeTab === 'part-number-analytics' ? 'primary' : 'outline-primary'}
                onClick={() => setActiveTab('part-number-analytics')}
              >
                Part Number Analytics
              </Button>
            </Tooltip>
          </>
        )}
      </div>

      {hasReportsPermission && activeTab === 'standard-reports' && (
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

      {hasReportsPermission && activeTab === 'chemical-analytics' && (
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

      {hasReportsPermission && activeTab === 'calibration-reports' && (
        <div className="pt-4">
          <CalibrationReports />
        </div>
      )}

      {hasKitsPermission && activeTab === 'kit-reports' && (
        <div className="pt-4">
          <KitReports />
        </div>
      )}

      {hasReportsPermission && activeTab === 'part-number-analytics' && (
        <div className="pt-4">
          <PartNumberAnalytics />
        </div>
      )}
    </div>
  );
};

export default ReportingPage;
