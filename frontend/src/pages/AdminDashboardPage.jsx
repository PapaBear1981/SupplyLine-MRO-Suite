import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import LoadingSpinner from '../components/common/LoadingSpinner';
import AdminDashboard from '../components/admin/AdminDashboard';

const AdminDashboardPage = () => {
  const { user, isLoading } = useSelector((state) => state.auth);

  // Show loading spinner while fetching user data
  if (isLoading) {
    return <LoadingSpinner />;
  }

  // Check if user is admin - use the same logic as other admin checks
  const isAdmin = user?.is_admin;

  // Redirect if user doesn't have admin permissions
  if (!isAdmin) {
    return <Navigate to="/" replace />;
  }

  // At this point, we know the user has admin permissions
  return <AdminDashboard />;
};

export default AdminDashboardPage;
