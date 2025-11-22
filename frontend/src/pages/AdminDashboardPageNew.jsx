import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import AdminDashboardNew from '../components/admin/AdminDashboardNew';

const AdminDashboardPageNew = () => {
  const { user, isLoading } = useSelector((state) => state.auth);

  // Show loading spinner while fetching user data
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <span className="sr-only">Loading...</span>
      </div>
    );
  }

  // Redirect if user is not an admin
  // Backend requires is_admin flag for all admin endpoints
  if (!user?.is_admin) {
    return <Navigate to="/" replace />;
  }

  // At this point, we know the user is an admin
  return <AdminDashboardNew />;
};

export default AdminDashboardPageNew;
