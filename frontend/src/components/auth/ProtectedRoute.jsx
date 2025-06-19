import { useSelector } from 'react-redux';
import { Navigate, useLocation } from 'react-router-dom';
import { Spinner } from 'react-bootstrap';

const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const { isAuthenticated, loading, user, tokenExists } = useSelector((state) => state.auth);
  const location = useLocation();

  // Show loading spinner while validating token on app startup
  if (loading && tokenExists) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Validating authentication...</span>
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
  const { user, loading, isAuthenticated, tokenExists } = useSelector((state) => state.auth);

  // Show loading spinner while validating token on app startup
  if (loading && tokenExists) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Validating authentication...</span>
        </Spinner>
      </div>
    );
  }

  if (!isAuthenticated || !user || !user.is_admin) {
    return <Navigate to="/" replace />;
  }

  return children;
};

export default ProtectedRoute;
