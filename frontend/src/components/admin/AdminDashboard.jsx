import { useState, useEffect, useMemo } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Card, Nav, Tab, Alert, Row, Col } from 'react-bootstrap';
import Tooltip from '../common/Tooltip';
import { useHelp } from '../../context/HelpContext';
import UserManagement from '../users/UserManagement';
import RoleManagement from './RoleManagement';
import AuditLogViewer from '../audit/AuditLogViewer';
import SystemSettings from './SystemSettings';
import HelpSettings from './HelpSettings';
import LoadingSpinner from '../common/LoadingSpinner';
import DashboardStats from './DashboardStats';
import SystemResources from './SystemResources';
import RegistrationRequests from './RegistrationRequests';
import AnnouncementManagement from './AnnouncementManagement';
import { fetchDashboardStats, fetchSystemResources, fetchRegistrationRequests } from '../../store/adminSlice';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const dispatch = useDispatch();
  const { showTooltips } = useHelp();
  const { user: currentUser, isLoading: authLoading } = useSelector((state) => state.auth);
  const {
    dashboardStats,
    systemResources,
    loading: adminLoading
  } = useSelector((state) => state.admin);

  // Memoize permission checks to prevent unnecessary recalculations
  const {
    canViewDashboard,
    canViewUsers,
    canManageRoles,
    canViewAudit,
    canManageSettings,
    canManageHelp,
    canViewRegistrations,
    canManageAnnouncements
  } = useMemo(() => ({
    canViewDashboard: currentUser?.is_admin,
    canViewUsers: currentUser?.permissions?.includes('user.view'),
    canManageRoles: currentUser?.permissions?.includes('role.manage'),
    canViewAudit: currentUser?.permissions?.includes('system.audit'),
    canManageSettings: currentUser?.permissions?.includes('system.settings'),
    canManageHelp: currentUser?.permissions?.includes('system.settings') || currentUser?.is_admin,
    canViewRegistrations: currentUser?.is_admin,
    canManageAnnouncements: currentUser?.is_admin
  }), [currentUser?.permissions, currentUser?.is_admin]);

  // Fetch dashboard data when component mounts
  useEffect(() => {
    if (canViewDashboard) {
      dispatch(fetchDashboardStats());
      dispatch(fetchSystemResources());
      dispatch(fetchRegistrationRequests('pending'));
    }
  }, [dispatch, canViewDashboard]);

  // Show loading indicator while fetching user data
  if (authLoading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  // If user doesn't have permission for any tabs, show an error
  if (!canViewDashboard && !canViewUsers && !canManageRoles && !canViewAudit && !canManageSettings && !canManageHelp && !canViewRegistrations && !canManageAnnouncements) {
    return (
      <Alert variant="danger">
        You do not have permission to access the Admin Dashboard. Please contact your administrator.
      </Alert>
    );
  }

  // Set the active tab to the first one the user has permission for
  useEffect(() => {
    if (activeTab === 'dashboard' && !canViewDashboard) {
      if (canViewUsers) setActiveTab('users');
      else if (canManageRoles) setActiveTab('roles');
      else if (canViewAudit) setActiveTab('audit');
      else if (canManageSettings) setActiveTab('settings');
      else if (canManageHelp) setActiveTab('help');
      else if (canViewRegistrations) setActiveTab('registrations');
      else if (canManageAnnouncements) setActiveTab('announcements');
    }
  }, [canViewDashboard, canViewUsers, canManageRoles, canViewAudit, canManageSettings, canManageHelp, canViewRegistrations, canManageAnnouncements, activeTab]);

  return (
    <div>
      <h2 className="mb-4">Admin Dashboard</h2>

      <Tab.Container id="admin-tabs" activeKey={activeTab} onSelect={(k) => setActiveTab(k)}>
        <Card>
          <Card.Header>
            <Nav variant="tabs">
              {canViewDashboard && (
                <Nav.Item>
                  <Tooltip text="View system overview and statistics" placement="bottom" show={showTooltips}>
                    <Nav.Link eventKey="dashboard">Dashboard</Nav.Link>
                  </Tooltip>
                </Nav.Item>
              )}
              {canViewUsers && (
                <Nav.Item>
                  <Tooltip text="Manage user accounts and permissions" placement="bottom" show={showTooltips}>
                    <Nav.Link eventKey="users">User Management</Nav.Link>
                  </Tooltip>
                </Nav.Item>
              )}
              {canManageRoles && (
                <Nav.Item>
                  <Tooltip text="Configure user roles and permissions" placement="bottom" show={showTooltips}>
                    <Nav.Link eventKey="roles">Role Management</Nav.Link>
                  </Tooltip>
                </Nav.Item>
              )}
              {canViewRegistrations && (
                <Nav.Item>
                  <Tooltip text="Review and approve new user registrations" placement="bottom" show={showTooltips}>
                    <Nav.Link eventKey="registrations">Registration Requests</Nav.Link>
                  </Tooltip>
                </Nav.Item>
              )}
              {canViewAudit && (
                <Nav.Item>
                  <Tooltip text="View system activity and audit trail" placement="bottom" show={showTooltips}>
                    <Nav.Link eventKey="audit">Audit Logs</Nav.Link>
                  </Tooltip>
                </Nav.Item>
              )}
              {canManageSettings && (
                <Nav.Item>
                  <Tooltip text="Configure system-wide settings and preferences" placement="bottom" show={showTooltips}>
                    <Nav.Link eventKey="settings">System Settings</Nav.Link>
                  </Tooltip>
                </Nav.Item>
              )}
              {canManageHelp && (
                <Nav.Item>
                  <Tooltip text="Manage help content and documentation" placement="bottom" show={showTooltips}>
                    <Nav.Link eventKey="help">Help Settings</Nav.Link>
                  </Tooltip>
                </Nav.Item>
              )}
              {canManageAnnouncements && (
                <Nav.Item>
                  <Tooltip text="Create and manage system announcements" placement="bottom" show={showTooltips}>
                    <Nav.Link eventKey="announcements">Announcements</Nav.Link>
                  </Tooltip>
                </Nav.Item>
              )}
            </Nav>
          </Card.Header>
          <Card.Body>
            <Tab.Content>
              <Tab.Pane eventKey="dashboard">
                {canViewDashboard && (
                  <Row>
                    <Col md={8}>
                      <DashboardStats stats={dashboardStats} loading={adminLoading.dashboardStats} />
                    </Col>
                    <Col md={4}>
                      <SystemResources resources={systemResources} loading={adminLoading.systemResources} />
                    </Col>
                  </Row>
                )}
              </Tab.Pane>
              <Tab.Pane eventKey="users">
                {canViewUsers && <UserManagement />}
              </Tab.Pane>
              <Tab.Pane eventKey="roles">
                {canManageRoles && <RoleManagement />}
              </Tab.Pane>
              <Tab.Pane eventKey="registrations">
                {canViewRegistrations && <RegistrationRequests />}
              </Tab.Pane>
              <Tab.Pane eventKey="audit">
                {canViewAudit && <AuditLogViewer />}
              </Tab.Pane>
              <Tab.Pane eventKey="settings">
                {canManageSettings && <SystemSettings />}
              </Tab.Pane>
              <Tab.Pane eventKey="help">
                {canManageHelp && <HelpSettings />}
              </Tab.Pane>
              <Tab.Pane eventKey="announcements">
                {canManageAnnouncements && <AnnouncementManagement />}
              </Tab.Pane>
            </Tab.Content>
          </Card.Body>
        </Card>
      </Tab.Container>
    </div>
  );
};

export default AdminDashboard;
