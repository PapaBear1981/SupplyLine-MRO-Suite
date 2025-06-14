/**
 * Custom hooks for authentication-related functionality
 */

import { useSelector } from 'react-redux';

/**
 * Hook to check if the current user is an admin
 * @returns {boolean} True if user is admin, false otherwise
 */
export const useIsAdmin = () => {
  const { user } = useSelector((state) => state.auth);
  return Boolean(user?.is_admin);
};

/**
 * Hook to get current authentication state
 * @returns {object} Authentication state with user, loading, and helper functions
 */
export const useAuth = () => {
  const { user, isAuthenticated, loading, error } = useSelector((state) => state.auth);
  
  return {
    user,
    isAuthenticated,
    loading,
    error,
    isAdmin: Boolean(user?.is_admin),
    hasUser: Boolean(user),
  };
};

/**
 * Hook to check if user has specific permissions
 * @param {string[]} requiredPermissions - Array of required permission prefixes
 * @returns {boolean} True if user has any of the required permissions
 */
export const useHasPermissions = (requiredPermissions = []) => {
  const { user } = useSelector((state) => state.auth);
  
  if (!user?.permissions || !Array.isArray(user.permissions)) {
    return false;
  }
  
  return user.permissions.some(permission =>
    requiredPermissions.some(prefix => permission.startsWith(prefix))
  );
};
