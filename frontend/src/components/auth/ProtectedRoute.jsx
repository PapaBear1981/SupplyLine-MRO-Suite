import { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Navigate, useLocation } from 'react-router-dom';
import { fetchCurrentUser } from '../../store/authSlice';
import { Spinner } from 'react-bootstrap';

const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const { isAuthenticated, loading, user } = useSelector((state) => state.auth);
  const dispatch = useDispatch();
  const location = useLocation();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token && !user) {
        await dispatch(fetchCurrentUser());
      }
      setIsChecking(false);
    };

    checkAuth();
  }, [dispatch, user]);

  if (loading || isChecking) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Redirect to login page but save the location they were trying to access
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check if admin access is required but user is not an admin
  if (requireAdmin && !user?.is_admin) {
    // Redirect to tools page with an unauthorized message
    return <Navigate to="/tools" state={{ unauthorized: true }} replace />;
  }

  return children;
};

// Specialized component for admin-only routes
export const AdminRoute = ({ children }) => {
  return <ProtectedRoute requireAdmin={true}>{children}</ProtectedRoute>;
};

export default ProtectedRoute;
