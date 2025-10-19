import { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Navigate, useLocation, Link } from 'react-router-dom';
import { fetchCurrentUser } from '../../store/authSlice';
import { Spinner, Alert, Container } from 'react-bootstrap';

/**
 * Check if user has a specific permission
 * Admins automatically have all permissions
 */
const hasPermission = (user, permissionName) => {
  if (!user) return false;

  // Admins have all permissions
  if (user.is_admin) return true;

  // Check if user has the specific permission
  const permissions = user.permissions || [];
  return permissions.includes(permissionName);
};

const ProtectedRoute = ({ children, requireAdmin = false, requirePermission = null, permissionFallback = '/dashboard' }) => {
  const { isAuthenticated, loading, user } = useSelector((state) => state.auth);
  const dispatch = useDispatch();
  const location = useLocation();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      // Check authentication status via API since tokens are in HttpOnly cookies
      if (!user) {
        try {
          await dispatch(fetchCurrentUser());
        } catch (error) {
          // User is not authenticated, will be handled by auth state
        }
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
    // Redirect to dashboard with an unauthorized message
    return <Navigate to="/dashboard" state={{ unauthorized: true, message: 'Admin privileges required' }} replace />;
  }

  // Check if specific permission is required
  if (requirePermission && !hasPermission(user, requirePermission)) {
    // Redirect to fallback path (e.g., /dashboard or a contextual page)
    return <Navigate to={permissionFallback} replace />;
  }

  return children;
};

// Specialized component for admin-only routes
export const AdminRoute = ({ children }) => {
  return <ProtectedRoute requireAdmin={true}>{children}</ProtectedRoute>;
};

// Specialized component for permission-based routes
export const PermissionRoute = ({ children, permission, fallbackPath = '/dashboard' }) => {
  return <ProtectedRoute requirePermission={permission} permissionFallback={fallbackPath}>{children}</ProtectedRoute>;
};

// Helper function to check permissions (can be used in components)
export { hasPermission };

export default ProtectedRoute;
