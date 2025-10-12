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

  // Redirect if user is not an admin
  // Backend requires is_admin flag for all admin endpoints
  if (!user?.is_admin) {
    return <Navigate to="/" replace />;
  }

  // At this point, we know the user is an admin
  return <AdminDashboard />;
};

export default AdminDashboardPage;
