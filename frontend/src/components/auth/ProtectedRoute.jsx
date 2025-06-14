import { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Navigate, useLocation } from 'react-router-dom';
import { fetchCurrentUser } from '../../store/authSlice';
import { Spinner } from 'react-bootstrap';
import { useIsAdmin } from '../../hooks/useAuth';

const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const { isAuthenticated, loading, user } = useSelector((state) => state.auth);
  const dispatch = useDispatch();
  const location = useLocation();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      if (!isAuthenticated && !user) {
        await dispatch(fetchCurrentUser());
      }
      setIsChecking(false);
    };

    checkAuth();
  }, [dispatch, isAuthenticated, user]);

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
  const { user, loading, isAuthenticated } = useSelector((state) => state.auth);
  const dispatch = useDispatch();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      if (!isAuthenticated && !user) {
        await dispatch(fetchCurrentUser());
      }
      setIsChecking(false);
    };

    checkAuth();
  }, [dispatch, isAuthenticated, user]);

  if (loading || isChecking) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </div>
    );
  }

  if (!user || !user.is_admin) {
    return <Navigate to="/" replace />;
  }

  return children;
};

export default ProtectedRoute;
