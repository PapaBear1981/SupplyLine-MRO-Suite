import { useSelector } from 'react-redux';
import { Container, Row, Col, Card } from 'react-bootstrap';
import OverdueChemicals from '../components/dashboard/OverdueChemicals';
import CalibrationNotifications from '../components/calibration/CalibrationNotifications';
import UserCheckoutStatus from '../components/dashboard/UserCheckoutStatus';
import RecentActivity from '../components/dashboard/RecentActivity';
import Announcements from '../components/dashboard/Announcements';
import QuickActions from '../components/dashboard/QuickActions';
import PastDueTools from '../components/dashboard/PastDueTools';
import MyKits from '../components/dashboard/MyKits';
import KitAlertsSummary from '../components/dashboard/KitAlertsSummary';
import RecentKitActivity from '../components/dashboard/RecentKitActivity';

const UserDashboardPage = () => {
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.is_admin || user?.department === 'Materials';

  return (
    <div className="w-100" data-testid="dashboard-content">
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4">
        <h1 className="mb-0">Dashboard</h1>
      </div>

      <Container fluid className="p-0">
        <Row>
          {/* Main content area - 2/3 width on large screens */}
          <Col lg={8}>
            {/* Notifications Section */}
            <CalibrationNotifications />

            {/* Only show OverdueChemicals to admins and Materials department */}
            {isAdmin && <OverdueChemicals />}

            {/* Only show PastDueTools to admins and Materials department */}
            {isAdmin && <PastDueTools />}

            {/* Kit Alerts - Show to all users */}
            <KitAlertsSummary />

            {/* User's Checked Out Tools */}
            <UserCheckoutStatus />

            {/* My Kits - Show active kits */}
            <MyKits />

            {/* Recent Kit Activity */}
            <RecentKitActivity />

            {/* Recent Activity */}
            <RecentActivity />
          </Col>

          {/* Sidebar - 1/3 width on large screens */}
          <Col lg={4}>
            {/* Announcements */}
            <Announcements />

            {/* Quick Actions */}
            <QuickActions />
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default UserDashboardPage;
