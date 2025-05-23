import { Spinner, Alert } from 'react-bootstrap';
import ToolInventoryTable from './tables/ToolInventoryTable';
import CheckoutHistoryTable from './tables/CheckoutHistoryTable';
import ToolUsageChart from './charts/ToolUsageChart';
import CheckoutTrendsChart from './charts/CheckoutTrendsChart';
import DepartmentUsageChart from './charts/DepartmentUsageChart';
import CycleCountAccuracyReport from './cycleCount/CycleCountAccuracyReport';
import CycleCountDiscrepancyReport from './cycleCount/CycleCountDiscrepancyReport';
import CycleCountPerformanceReport from './cycleCount/CycleCountPerformanceReport';
import CycleCountCoverageReport from './cycleCount/CycleCountCoverageReport';

const ReportViewer = ({ reportType, timeframe, data, loading }) => {
  if (loading) {
    return (
      <div className="text-center p-5">
        <Spinner animation="border" role="status" variant="primary">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
        <p className="mt-3">Loading report data...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <Alert variant="info">
        Select report options and click "Apply Filters" to generate a report.
      </Alert>
    );
  }

  // Render different report components based on report type
  switch (reportType) {
    case 'tool-inventory':
      return (
        <div>
          <ToolInventoryTable data={data} />
        </div>
      );

    case 'checkout-history':
      return (
        <div>
          <div className="mb-4">
            <CheckoutTrendsChart data={data} timeframe={timeframe} />
          </div>
          <CheckoutHistoryTable data={data} />
        </div>
      );

    case 'department-usage':
      return (
        <div>
          <div className="mb-4">
            <DepartmentUsageChart data={data} />
          </div>
          <div className="mb-4">
            <ToolUsageChart data={data} />
          </div>
        </div>
      );

    case 'cycle-count-accuracy':
      return <CycleCountAccuracyReport data={data} />;

    case 'cycle-count-discrepancies':
      return <CycleCountDiscrepancyReport data={data} />;

    case 'cycle-count-performance':
      return <CycleCountPerformanceReport data={data} />;

    case 'cycle-count-coverage':
      return <CycleCountCoverageReport data={data} />;

    default:
      return (
        <Alert variant="warning">
          Unknown report type: {reportType}
        </Alert>
      );
  }
};

export default ReportViewer;
