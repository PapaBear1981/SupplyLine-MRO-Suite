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
import { fetchDashboardStats, fetchSystemResources, fetchRegistrationRequests } from '../../store/adminSlice';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const dispatch = useDispatch();
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
    canViewRegistrations
  } = useMemo(() => ({
    canViewDashboard: currentUser?.is_admin,
    canViewUsers: currentUser?.permissions?.includes('user.view'),
    canManageRoles: currentUser?.permissions?.includes('role.manage'),
    canViewAudit: currentUser?.permissions?.includes('system.audit'),
    canManageSettings: currentUser?.permissions?.includes('system.settings'),
    canManageHelp: currentUser?.permissions?.includes('system.settings') || currentUser?.is_admin,
    canViewRegistrations: currentUser?.is_admin
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
  if (!canViewDashboard && !canViewUsers && !canManageRoles && !canViewAudit && !canManageSettings && !canManageHelp && !canViewRegistrations) {
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
    }
  }, [canViewDashboard, canViewUsers, canManageRoles, canViewAudit, canManageSettings, canManageHelp, canViewRegistrations, activeTab]);

  return (
    <div>
      <h2 className="mb-4">Admin Dashboard</h2>

      <Card>
        <Card.Header>
          <Nav variant="tabs" activeKey={activeTab} onSelect={(k) => setActiveTab(k)}>
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
          </Nav>
        </Card.Header>
        <Card.Body>
          <Tab.Content>
            <Tab.Pane active={activeTab === 'dashboard'}>
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
            <Tab.Pane active={activeTab === 'users'}>
              {canViewUsers && <UserManagement />}
            </Tab.Pane>
            <Tab.Pane active={activeTab === 'roles'}>
              {canManageRoles && <RoleManagement />}
            </Tab.Pane>
            <Tab.Pane active={activeTab === 'registrations'}>
              {canViewRegistrations && <RegistrationRequests />}
            </Tab.Pane>
            <Tab.Pane active={activeTab === 'audit'}>
              {canViewAudit && <AuditLogViewer />}
            </Tab.Pane>
            <Tab.Pane active={activeTab === 'settings'}>
              {canManageSettings && <SystemSettings />}
            </Tab.Pane>
            <Tab.Pane active={activeTab === 'help'}>
              {canManageHelp && <HelpSettings />}
            </Tab.Pane>
          </Tab.Content>
        </Card.Body>
      </Card>
    </div>
  );
};

export default AdminDashboard;
