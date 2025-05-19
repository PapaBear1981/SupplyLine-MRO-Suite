import { useState } from 'react';
import { useSelector } from 'react-redux';
import { Card, Nav, Tab, Alert } from 'react-bootstrap';
import UserManagement from '../users/UserManagement';
import RoleManagement from './RoleManagement';
import AuditLogViewer from '../audit/AuditLogViewer';
import SystemSettings from './SystemSettings';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('users');
  const { user: currentUser } = useSelector((state) => state.auth);

  // Check permissions for each tab
  const canViewUsers = currentUser?.permissions?.includes('user.view');
  const canManageRoles = currentUser?.permissions?.includes('role.manage');
  const canViewAudit = currentUser?.permissions?.includes('system.audit');
  const canManageSettings = currentUser?.permissions?.includes('system.settings');

  // If user doesn't have permission for any tabs, show an error
  if (!canViewUsers && !canManageRoles && !canViewAudit && !canManageSettings) {
    return (
      <Alert variant="danger">
        You do not have permission to access the Admin Dashboard. Please contact your administrator.
      </Alert>
    );
  }

  // Set the active tab to the first one the user has permission for
  if (activeTab === 'users' && !canViewUsers) {
    if (canManageRoles) setActiveTab('roles');
    else if (canViewAudit) setActiveTab('audit');
    else if (canManageSettings) setActiveTab('settings');
  }

  return (
    <div>
      <h2 className="mb-4">Admin Dashboard</h2>
      
      <Card>
        <Card.Header>
          <Nav variant="tabs" activeKey={activeTab} onSelect={(k) => setActiveTab(k)}>
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
          </Nav>
        </Card.Header>
        <Card.Body>
          <Tab.Content>
            <Tab.Pane active={activeTab === 'users'}>
              {canViewUsers && <UserManagement />}
            </Tab.Pane>
            <Tab.Pane active={activeTab === 'roles'}>
              {canManageRoles && <RoleManagement />}
            </Tab.Pane>
            <Tab.Pane active={activeTab === 'audit'}>
              {canViewAudit && <AuditLogViewer />}
            </Tab.Pane>
            <Tab.Pane active={activeTab === 'settings'}>
              {canManageSettings && <SystemSettings />}
            </Tab.Pane>
          </Tab.Content>
        </Card.Body>
      </Card>
    </div>
  );
};

export default AdminDashboard;
