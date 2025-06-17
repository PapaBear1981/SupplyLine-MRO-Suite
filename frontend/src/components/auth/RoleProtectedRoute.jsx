import { useSelector } from 'react-redux';
import { Navigate, useLocation, Link } from 'react-router-dom';
import { Alert } from 'react-bootstrap';
import PermissionService from '../../services/permissionService';

/**
 * Role-based route protection component
 * Protects routes based on user permissions and roles
 */
const RoleProtectedRoute = ({ 
  children, 
  requiredPermission = null, 
  requiredPermissions = [], 
  requiredRole = null, 
  requiredRoles = [],
  requireAll = false, // If true, user must have ALL permissions/roles; if false, user needs ANY
  fallbackPath = '/dashboard',
  showError = true,
  errorMessage = null
}) => {
  const { user, isAuthenticated, isLoading } = useSelector((state) => state.auth);
  const location = useLocation();

  // Show loading while authentication is being checked
  if (isLoading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check permissions
  let hasPermission = true;
  
  if (requiredPermission) {
    hasPermission = PermissionService.hasPermission(user, requiredPermission);
  } else if (requiredPermissions.length > 0) {
    hasPermission = requireAll 
      ? PermissionService.hasAllPermissions(user, requiredPermissions)
      : PermissionService.hasAnyPermission(user, requiredPermissions);
  }

  // Check roles
  let hasRole = true;
  
  if (requiredRole) {
    hasRole = PermissionService.hasRole(user, requiredRole);
  } else if (requiredRoles.length > 0) {
    hasRole = requireAll
      ? requiredRoles.every(role => PermissionService.hasRole(user, role))
      : PermissionService.hasAnyRole(user, requiredRoles);
  }

  // If user doesn't have required permissions or roles
  if (!hasPermission || !hasRole) {
    if (showError) {
      const defaultMessage = `You don't have permission to access this page. Required: ${
        requiredPermission || requiredPermissions.join(', ') || 
        requiredRole || requiredRoles.join(', ')
      }`;
      
      return (
        <div className="container mt-4">
          <Alert variant="danger">
            <Alert.Heading>Access Denied</Alert.Heading>
            <p>{errorMessage || defaultMessage}</p>
            <p>Please contact your administrator if you believe you should have access to this page.</p>
          </Alert>
        </div>
      );
    } else {
      return <Navigate to={fallbackPath} replace />;
    }
  }

  return children;
};

/**
 * Specialized components for common permission checks
 */

// Admin-only routes - Check for is_admin flag instead of role
export const AdminRoute = ({ children, ...props }) => {
  const { user, isAuthenticated, isLoading } = useSelector((state) => state.auth);
  const location = useLocation();

  // Show loading while authentication is being checked
  if (isLoading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check if user is admin using is_admin flag (legacy support)
  if (!user?.is_admin) {
    return (
      <div className="container mt-5">
        <div className="alert alert-danger">
          <h4>Access Denied</h4>
          <p>This page requires administrator privileges.</p>
          <Link to="/dashboard" className="btn btn-primary">Go to Dashboard</Link>
        </div>
      </div>
    );
  }

  return children;
};

// Lead or Admin routes
export const LeadRoute = ({ children, ...props }) => (
  <RoleProtectedRoute 
    requiredRoles={['Lead', 'Administrator']} 
    fallbackPath="/dashboard"
    errorMessage="This page requires lead or administrator privileges."
    {...props}
  >
    {children}
  </RoleProtectedRoute>
);

// User, Lead, or Admin routes (excludes Mechanic)
export const UserRoute = ({ children, ...props }) => (
  <RoleProtectedRoute 
    requiredRoles={['User', 'Lead', 'Administrator']} 
    fallbackPath="/tools"
    errorMessage="This page requires user, lead, or administrator privileges."
    {...props}
  >
    {children}
  </RoleProtectedRoute>
);

// Tool management routes (Materials department or Admin)
export const ToolManagerRoute = ({ children, ...props }) => (
  <RoleProtectedRoute 
    requiredPermissions={['tool.create', 'tool.edit', 'tool.delete']} 
    fallbackPath="/tools"
    errorMessage="This page requires tool management privileges."
    {...props}
  >
    {children}
  </RoleProtectedRoute>
);

// Chemical management routes
export const ChemicalManagerRoute = ({ children, ...props }) => (
  <RoleProtectedRoute 
    requiredPermissions={['chemical.create', 'chemical.edit']} 
    fallbackPath="/chemicals"
    errorMessage="This page requires chemical management privileges."
    {...props}
  >
    {children}
  </RoleProtectedRoute>
);

// Calibration management routes
export const CalibrationManagerRoute = ({ children, ...props }) => (
  <RoleProtectedRoute 
    requiredPermission="calibration.manage"
    fallbackPath="/calibrations"
    errorMessage="This page requires calibration management privileges."
    {...props}
  >
    {children}
  </RoleProtectedRoute>
);

// Report access routes
export const ReportRoute = ({ children, ...props }) => (
  <RoleProtectedRoute 
    requiredPermission="report.view"
    fallbackPath="/dashboard"
    errorMessage="This page requires report viewing privileges."
    {...props}
  >
    {children}
  </RoleProtectedRoute>
);

// All checkouts view (not just own checkouts)
export const AllCheckoutsRoute = ({ children, ...props }) => (
  <RoleProtectedRoute 
    requiredPermission="checkout.view_all"
    fallbackPath="/checkouts"
    errorMessage="This page requires permission to view all checkouts."
    {...props}
  >
    {children}
  </RoleProtectedRoute>
);

export default RoleProtectedRoute;
