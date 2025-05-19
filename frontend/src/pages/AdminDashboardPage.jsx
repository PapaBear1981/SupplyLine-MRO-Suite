import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import LoadingSpinner from '../components/common/LoadingSpinner';
import AdminDashboard from '../components/admin/AdminDashboard';

const AdminDashboardPage = () => {
  const { user, isLoading } = useSelector((state) => state.auth);

  // Define admin permission prefixes as a constant
  const ADMIN_PERMISSION_PREFIXES = ['user.', 'role.', 'system.'];

  // Check if user has any admin permissions
  const hasAdminPermissions = user?.permissions?.some(permission =>
    ADMIN_PERMISSION_PREFIXES.some(prefix => permission.startsWith(prefix))
  );

  // Redirect if user doesn't have admin permissions
  if (!hasAdminPermissions) {
    return <Navigate to="/" replace />;
  }

  // Show loading spinner while fetching user data
  if (isLoading) {
    return <LoadingSpinner />;
  }

  // At this point, we know the user has admin permissions
  return <AdminDashboard />;
};

export default AdminDashboardPage;
