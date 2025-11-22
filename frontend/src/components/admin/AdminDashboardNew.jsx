import { useState, useEffect, useMemo } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useSearchParams } from 'react-router-dom';
import { AlertCircle } from 'lucide-react';
import GlobalSearch from '../common/GlobalSearch';
import UserManagement from '../users/UserManagement';
import RoleManagement from './RoleManagement';
import AuditLogViewer from '../audit/AuditLogViewer';
import SystemSettings from './SystemSettings';
import HelpSettings from './HelpSettings';
import DashboardStats from './DashboardStats';
import RegistrationRequests from './RegistrationRequests';
import AnnouncementManagement from './AnnouncementManagement';
import PasswordReset from './PasswordReset';
import AircraftTypeManagementNew from './AircraftTypeManagementNew';
import DatabaseManagement from './DatabaseManagement';
import { fetchDashboardStats, fetchRegistrationRequests } from '../../store/adminSlice';
import { Card, CardContent, CardHeader } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Alert, AlertDescription } from '../ui/alert';
import { Loader2 } from 'lucide-react';

const AdminDashboardNew = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState('dashboard');
  const dispatch = useDispatch();
  const { user: currentUser, isLoading: authLoading } = useSelector((state) => state.auth);
  const {
    dashboardStats,
    loading: adminLoading
  } = useSelector((state) => state.admin);

  // Read tab from URL parameter on mount
  useEffect(() => {
    const tabParam = searchParams.get('tab');
    if (tabParam) {
      setActiveTab(tabParam);
      // Clear the tab param from URL after reading
      setSearchParams({}, { replace: true });
    }
  }, [searchParams, setSearchParams]);

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
    canManageAircraftTypes,
    canManageDatabase
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
    canManageAircraftTypes: currentUser?.is_admin,
    canManageDatabase: currentUser?.is_admin
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
      <div className="flex justify-center items-center py-8">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <span className="sr-only">Loading...</span>
      </div>
    );
  }

  // If user doesn't have permission for any tabs, show an error
  if (!canViewDashboard && !canViewUsers && !canManageRoles && !canViewAudit && !canManageSettings && !canManageHelp && !canViewRegistrations && !canManageAnnouncements && !canManageAircraftTypes) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          You do not have permission to access the Admin Dashboard. Please contact your administrator.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="w-full space-y-6">
      <GlobalSearch />
      <h1 className="text-3xl font-bold tracking-tight text-foreground">Admin Dashboard</h1>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <Card>
          <CardHeader className="pb-3">
            <TabsList className="w-full justify-start flex-wrap h-auto">
              {canViewDashboard && (
                <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
              )}
              {canViewUsers && (
                <TabsTrigger value="users">User Management</TabsTrigger>
              )}
              {canManageRoles && (
                <TabsTrigger value="roles">Role Management</TabsTrigger>
              )}
              {canViewRegistrations && (
                <TabsTrigger value="registrations">Registration Requests</TabsTrigger>
              )}
              {canViewAudit && (
                <TabsTrigger value="audit">Audit Logs</TabsTrigger>
              )}
              {canManageSettings && (
                <TabsTrigger value="settings">System Settings</TabsTrigger>
              )}
              {canManageHelp && (
                <TabsTrigger value="help">Help Settings</TabsTrigger>
              )}
              {canManageAnnouncements && (
                <TabsTrigger value="announcements">Announcements</TabsTrigger>
              )}
              {canResetPasswords && (
                <TabsTrigger value="password-reset">Password Reset</TabsTrigger>
              )}
              {canManageAircraftTypes && (
                <TabsTrigger value="aircraft-types">Aircraft Types</TabsTrigger>
              )}
              {canManageDatabase && (
                <TabsTrigger value="database">Database</TabsTrigger>
              )}
            </TabsList>
          </CardHeader>
          <CardContent>
            <TabsContent value="dashboard" className="mt-0">
              {canViewDashboard && (
                <DashboardStats stats={dashboardStats} loading={adminLoading.dashboardStats} onNavigateToTab={setActiveTab} />
              )}
            </TabsContent>
            <TabsContent value="users" className="mt-0">
              {canViewUsers && <UserManagement />}
            </TabsContent>
            <TabsContent value="roles" className="mt-0">
              {canManageRoles && <RoleManagement />}
            </TabsContent>
            <TabsContent value="registrations" className="mt-0">
              {canViewRegistrations && <RegistrationRequests />}
            </TabsContent>
            <TabsContent value="audit" className="mt-0">
              {canViewAudit && <AuditLogViewer />}
            </TabsContent>
            <TabsContent value="settings" className="mt-0">
              {canManageSettings && <SystemSettings />}
            </TabsContent>
            <TabsContent value="help" className="mt-0">
              {canManageHelp && <HelpSettings />}
            </TabsContent>
            <TabsContent value="announcements" className="mt-0">
              {canManageAnnouncements && <AnnouncementManagement />}
            </TabsContent>
            <TabsContent value="password-reset" className="mt-0">
              {canResetPasswords && <PasswordReset />}
            </TabsContent>
            <TabsContent value="aircraft-types" className="mt-0">
              {canManageAircraftTypes && <AircraftTypeManagementNew />}
            </TabsContent>
            <TabsContent value="database" className="mt-0">
              {canManageDatabase && <DatabaseManagement />}
            </TabsContent>
          </CardContent>
        </Card>
      </Tabs>
    </div>
  );
};

export default AdminDashboardNew;
