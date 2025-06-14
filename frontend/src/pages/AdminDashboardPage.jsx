import { Navigate } from 'react-router-dom';
import LoadingSpinner from '../components/common/LoadingSpinner';
import UnauthorizedAccess from '../components/common/UnauthorizedAccess';
import AdminDashboard from '../components/admin/AdminDashboard';
import { useAuth } from '../hooks/useAuth';

const AdminDashboardPage = () => {
  const { user, loading, hasUser, isAdmin } = useAuth();

  // Show loading spinner while fetching user data
  if (loading) {
    return <LoadingSpinner />;
  }

  // Handle the edge case where loading is false but user is null
  // This could happen due to auth errors or failed user fetch
  if (!hasUser) {
    return (
      <UnauthorizedAccess
        title="Authentication Required"
        message="Unable to verify your authentication status. Please log in again."
        redirectPath="/login"
        redirectText="Go to Login"
      />
    );
  }

  // Check if user is admin - using the optimized useAuth hook for consistency
  if (!isAdmin) {
    return (
      <UnauthorizedAccess
        title="Admin Access Required"
        message="You need administrator privileges to access this page."
        redirectPath="/dashboard"
        redirectText="Go to Dashboard"
      />
    );
  }

  // At this point, we know the user is an admin
  return <AdminDashboard />;
};

export default AdminDashboardPage;
