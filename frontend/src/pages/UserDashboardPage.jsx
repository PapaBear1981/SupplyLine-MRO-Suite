import { useEffect, useMemo } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Container, Row, Col, Button } from 'react-bootstrap';
import {
  FaTools,
  FaFlask,
  FaBoxOpen,
  FaUsers,
  FaExclamationTriangle,
  FaCheckCircle
} from 'react-icons/fa';

// Actions
import { fetchCheckouts, fetchUserCheckouts } from '../store/checkoutsSlice';
import { fetchChemicals, fetchChemicalsNeedingReorder, fetchChemicalsExpiringSoon } from '../store/chemicalsSlice';
import { fetchKits } from '../store/kitsSlice';
import { fetchRegistrationRequests } from '../store/adminSlice';

// Components
import { StatCard, AnalyticsChart, DistributionChart, QuickLinksGrid } from '../components/dashboard/DashboardWidgets';
import CalibrationNotifications from '../components/calibration/CalibrationNotifications';
import ReceivedItemsAlertWidget from '../components/dashboard/ReceivedItemsAlertWidget';
import GlobalSearch from '../components/common/GlobalSearch';

// Styles
import '../styles/dashboardThemes.css';
import '../styles/ModernDashboard.css';

const UserDashboardPage = () => {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const { checkouts, userCheckouts } = useSelector((state) => state.checkouts);
  const { chemicals, chemicalsNeedingReorder, chemicalsExpiringSoon } = useSelector((state) => state.chemicals);
  const { kits } = useSelector((state) => state.kits);

  // Role checks
  const isAdmin = user?.is_admin;
  const isMaterials = user?.department === 'Materials';
  const hasRequestPermission = Boolean(isAdmin || (user?.permissions || []).includes('page.requests') || (user?.permissions || []).includes('page.orders'));

  // Fetch Data
  useEffect(() => {
    dispatch(fetchCheckouts());
    dispatch(fetchUserCheckouts());
    dispatch(fetchChemicals());
    dispatch(fetchChemicalsNeedingReorder());
    dispatch(fetchChemicalsExpiringSoon());
    dispatch(fetchKits());

    if (isAdmin) {
      dispatch(fetchRegistrationRequests('pending'));
    }
  }, [dispatch, isAdmin]);

  // --- Computed Stats ---

  // Tool Stats
  const totalCheckouts = checkouts.length;
  const myCheckoutsCount = userCheckouts.length;
  const toolsTrend = 5.2; // Mock trend for now

  // Chemical Stats
  const lowStockCount = chemicalsNeedingReorder.length;
  const expiringCount = chemicalsExpiringSoon.length;
  const totalChemicals = chemicals.length;

  // Kit Stats
  const totalKits = kits.length;
  const activeKits = kits.filter(k => k.status === 'active').length;

  // --- Chart Data Preparation ---

  // Mock Checkout Trend Data (Last 7 Days)
  // In a real app, you'd aggregate this from checkout history dates
  const checkoutTrendData = [
    { name: 'Mon', value: 12 },
    { name: 'Tue', value: 19 },
    { name: 'Wed', value: 15 },
    { name: 'Thu', value: 22 },
    { name: 'Fri', value: 28 },
    { name: 'Sat', value: 8 },
    { name: 'Sun', value: 5 },
  ];

  // Chemical Status Distribution
  const chemicalStatusData = [
    { name: 'Available', value: totalChemicals - lowStockCount - expiringCount },
    { name: 'Low Stock', value: lowStockCount },
    { name: 'Expiring', value: expiringCount },
  ];
  const chemicalColors = ['#10b981', '#f59e0b', '#ef4444'];

  // Kit Usage Mock Data
  const kitUsageData = [
    { name: 'Week 1', value: 45 },
    { name: 'Week 2', value: 52 },
    { name: 'Week 3', value: 38 },
    { name: 'Week 4', value: 65 },
  ];

  // Determine role-based theme class
  const roleThemeClass = useMemo(() => {
    if (isAdmin) {
      return 'dashboard-theme-admin';
    }
    if (isMaterials) {
      return 'dashboard-theme-materials';
    }
    return 'dashboard-theme-standard';
  }, [isAdmin, isMaterials]);

  return (
    <div
      className={`dashboard-root w-100 ${roleThemeClass}`}
      data-testid="dashboard-content"
      style={{ minHeight: '100vh', background: 'var(--enterprise-bg)' }}
    >
      <Container fluid className="p-4">

        {/* Header */}
        <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-4 gap-3">
          <div>
            <h2 className="fw-bold mb-1" style={{ color: 'var(--enterprise-text)' }}>Dashboard</h2>
            <p className="text-muted mb-0">Welcome back, {user?.first_name || 'User'}</p>
          </div>
          <div className="w-100 w-md-auto" style={{ maxWidth: '400px' }}>
            <GlobalSearch />
          </div>
        </div>

        {/* Main Grid Layout */}
        <div className="dashboard-grid">

          {/* Top Stats Row */}
          <div className="grid-stats">
            <StatCard
              title="Total Checkouts"
              value={totalCheckouts}
              trend={toolsTrend}
              trendLabel="vs last week"
              icon={<FaTools />}
              color="#3b82f6"
            />
            <StatCard
              title="My Active Tools"
              value={myCheckoutsCount}
              icon={<FaCheckCircle />}
              color="#10b981"
              onClick={() => window.location.href = '/my-checkouts'}
            />
            <StatCard
              title="Low Stock Chemicals"
              value={lowStockCount}
              trend={lowStockCount > 0 ? -10 : 0}
              trendLabel="needs attention"
              icon={<FaFlask />}
              color="#f59e0b"
            />
            <StatCard
              title="Active Kits"
              value={activeKits}
              icon={<FaBoxOpen />}
              color="#8b5cf6"
            />
          </div>

          {/* Main Chart Area */}
          <div className="grid-main-chart">
            <AnalyticsChart
              title="Tool Usage Trends"
              data={checkoutTrendData}
              dataKey="value"
              color="#3b82f6"
              height={350}
            />
          </div>

          {/* Quick Links */}
          <div className="grid-quick-links">
            <QuickLinksGrid />
          </div>

          {/* Secondary Row */}
          <div className="grid-side-chart">
            <DistributionChart
              title="Chemical Inventory Status"
              data={chemicalStatusData}
              colors={chemicalColors}
              height={300}
            />
          </div>

          <div className="grid-secondary-chart">
            <AnalyticsChart
              title="Kit Usage Activity"
              data={kitUsageData}
              dataKey="value"
              color="#8b5cf6"
              type="line"
              height={300}
            />
          </div>

          {/* Notifications Area (Preserving critical functionality) */}
          <div className="grid-stats" style={{ gridColumn: 'span 12' }}>
            <CalibrationNotifications />
          </div>

          {/* Received Items Alert Widget - Only show if user has request permissions */}
          {hasRequestPermission && (
            <div className="grid-stats" style={{ gridColumn: 'span 12' }}>
              <ReceivedItemsAlertWidget />
            </div>
          )}

        </div>
      </Container>
    </div>
  );
};

export default UserDashboardPage;
