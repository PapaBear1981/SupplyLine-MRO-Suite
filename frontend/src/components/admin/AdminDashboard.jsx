import { useState, useEffect, useMemo } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Card, Nav, Tab, Alert, Row, Col } from 'react-bootstrap';
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
import PermissionService from '../../services/permissionService';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const dispatch = useDispatch();
  const { user: currentUser, isLoading: authLoading } = useSelector((state) => state.auth);
  const {
    dashboardStats,
    systemResources,
    loading: adminLoading
  } = useSelector((state) => state.admin);

  // Get navigation permissions using the permission service
  const permissions = useMemo(() =>
    PermissionService.getNavigationPermissions(currentUser),
    [currentUser]
  );

  // Extract specific permissions for easier use
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
    canViewDashboard: currentUser?.is_admin || PermissionService.hasPermission(currentUser, 'dashboard.view'),
    canViewUsers: permissions.canManageUsers,
    canManageRoles: permissions.canManageRoles,
    canViewAudit: permissions.canViewAuditLogs,
    canManageSettings: permissions.canManageSettings,
    canManageHelp: permissions.canManageSettings || currentUser?.is_admin,
    canViewRegistrations: currentUser?.is_admin,
    canManageAnnouncements: permissions.canManageAnnouncements
  }), [permissions, currentUser?.is_admin]);

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
                  <Nav.Link eventKey="dashboard">Dashboard</Nav.Link>
                </Nav.Item>
              )}
              {canViewUsers && (
                <Nav.Item>
                  <Nav.Link eventKey="users">User Management</Nav.Link>
                </Nav.Item>
              )}
              {canManageRoles && (
                <Nav.Item>
                  <Nav.Link eventKey="roles">Role Management</Nav.Link>
                </Nav.Item>
              )}
              {canViewRegistrations && (
                <Nav.Item>
                  <Nav.Link eventKey="registrations">Registration Requests</Nav.Link>
                </Nav.Item>
              )}
              {canViewAudit && (
                <Nav.Item>
                  <Nav.Link eventKey="audit">Audit Logs</Nav.Link>
                </Nav.Item>
              )}
              {canManageSettings && (
                <Nav.Item>
                  <Nav.Link eventKey="settings">System Settings</Nav.Link>
                </Nav.Item>
              )}
              {canManageHelp && (
                <Nav.Item>
                  <Nav.Link eventKey="help">Help Settings</Nav.Link>
                </Nav.Item>
              )}
              {canManageAnnouncements && (
                <Nav.Item>
                  <Nav.Link eventKey="announcements">Announcements</Nav.Link>
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
