/**
 * Custom hooks for authentication-related functionality
 */

import { useSelector, shallowEqual } from 'react-redux';
import { useMemo } from 'react';

/**
 * Hook to check if the current user is an admin
 * @returns {boolean} True if user is admin, false otherwise
 */
export const useIsAdmin = () => {
  const { user } = useSelector((state) => state.auth, shallowEqual);
  return Boolean(user?.is_admin);
};

/**
 * Hook to get current authentication state
 * @returns {object} Authentication state with user, loading, and helper functions
 */
export const useAuth = () => {
  const { user, isAuthenticated, loading, error } = useSelector(
    (state) => state.auth,
    shallowEqual
  );

  return useMemo(
    () => ({
      user,
      isAuthenticated,
      loading,
      error,
      isAdmin: Boolean(user?.is_admin),
      hasUser: Boolean(user),
    }),
    [user, isAuthenticated, loading, error]
  );
};

/**
 * Hook to check if user has specific permissions
 * @param {string[]} requiredPermissions - Array of required permission prefixes
 * @returns {boolean} True if user has any of the required permissions
 */
export const useHasPermissions = (requiredPermissions = []) => {
  const { user } = useSelector((state) => state.auth, shallowEqual);

  // If no permissions are required, return true (no restriction)
  if (!requiredPermissions.length) {
    return true;
  }

  if (!user?.permissions || !Array.isArray(user.permissions)) {
    return false;
  }

  return user.permissions.some(permission =>
    requiredPermissions.some(prefix => permission.startsWith(prefix))
  );
};
