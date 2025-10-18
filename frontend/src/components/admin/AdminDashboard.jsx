import { useState, useEffect, useMemo } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Card, Nav, Tab, Alert } from 'react-bootstrap';
import UserManagement from '../users/UserManagement';
import RoleManagement from './RoleManagement';
import AuditLogViewer from '../audit/AuditLogViewer';
import SystemSettings from './SystemSettings';
import HelpSettings from './HelpSettings';
import LoadingSpinner from '../common/LoadingSpinner';
import DashboardStats from './DashboardStats';
import RegistrationRequests from './RegistrationRequests';
import AnnouncementManagement from './AnnouncementManagement';
import PasswordReset from './PasswordReset';
import AircraftTypeManagement from './AircraftTypeManagement';
import { fetchDashboardStats, fetchRegistrationRequests } from '../../store/adminSlice';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const dispatch = useDispatch();
  const { user: currentUser, isLoading: authLoading } = useSelector((state) => state.auth);
  const {
    dashboardStats,
    loading: adminLoading
  } = useSelector((state) => state.admin);

  // Memoize permission checks to prevent unnecessary recalculations
  // Admins (is_admin: true) have FULL access to all features
  const {
    canViewDashboard,
    canViewUsers,
    canManageRoles,
    canViewAudit,
    canManageSettings,
    canManageHelp,
    canViewRegistrations,
    canManageAnnouncements,
    canResetPasswords,
    canManageAircraftTypes
  } = useMemo(() => ({
    canViewDashboard: currentUser?.is_admin,
    canViewUsers: currentUser?.is_admin || currentUser?.permissions?.includes('user.view'),
    canManageRoles: currentUser?.is_admin || currentUser?.permissions?.includes('role.manage'),
    canViewAudit: currentUser?.is_admin || currentUser?.permissions?.includes('system.audit'),
    canManageSettings: currentUser?.is_admin || currentUser?.permissions?.includes('system.settings'),
    canManageHelp: currentUser?.is_admin || currentUser?.permissions?.includes('system.settings'),
    canViewRegistrations: currentUser?.is_admin,
    canManageAnnouncements: currentUser?.is_admin,
    canResetPasswords: currentUser?.is_admin || currentUser?.permissions?.includes('user.manage'),
    canManageAircraftTypes: currentUser?.is_admin
  }), [currentUser?.permissions, currentUser?.is_admin]);

  // Fetch dashboard data when component mounts
  useEffect(() => {
    if (canViewDashboard) {
      dispatch(fetchDashboardStats());
      dispatch(fetchRegistrationRequests('pending'));
    }
  }, [dispatch, canViewDashboard]);

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
      else if (canResetPasswords) setActiveTab('password-reset');
    }
  }, [canViewDashboard, canViewUsers, canManageRoles, canViewAudit, canManageSettings, canManageHelp, canViewRegistrations, canManageAnnouncements, canResetPasswords, activeTab]);

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
  if (!canViewDashboard && !canViewUsers && !canManageRoles && !canViewAudit && !canManageSettings && !canManageHelp && !canViewRegistrations && !canManageAnnouncements && !canManageAircraftTypes) {
    return (
      <Alert variant="danger">
        You do not have permission to access the Admin Dashboard. Please contact your administrator.
      </Alert>
    );
  }

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
              {canResetPasswords && (
                <Nav.Item>
                  <Nav.Link eventKey="password-reset">Password Reset</Nav.Link>
                </Nav.Item>
              )}
              {canManageAircraftTypes && (
                <Nav.Item>
                  <Nav.Link eventKey="aircraft-types">Aircraft Types</Nav.Link>
                </Nav.Item>
              )}
            </Nav>
          </Card.Header>
          <Card.Body>
            <Tab.Content>
              <Tab.Pane eventKey="dashboard">
                {canViewDashboard && (
                  <DashboardStats stats={dashboardStats} loading={adminLoading.dashboardStats} />
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
              <Tab.Pane eventKey="password-reset">
                {canResetPasswords && <PasswordReset />}
              </Tab.Pane>
              <Tab.Pane eventKey="aircraft-types">
                {canManageAircraftTypes && <AircraftTypeManagement />}
              </Tab.Pane>
            </Tab.Content>
          </Card.Body>
        </Card>
      </Tab.Container>
    </div>
  );
};

export default AdminDashboard;
