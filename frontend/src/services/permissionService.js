/**
 * Permission Service for Role-Based Access Control (RBAC)
 * 
 * This service provides centralized permission checking for the application.
 * It supports both the new RBAC system and legacy admin-based permissions.
 */

class PermissionService {
  /**
   * Check if user has a specific permission
   * @param {Object} user - User object with permissions and roles
   * @param {string} permission - Permission to check
   * @returns {boolean} - True if user has permission
   */
  static hasPermission(user, permission) {
    if (!user) return false;

    // Admin users have all permissions (legacy support)
    if (user.is_admin) return true;

    // Check RBAC permissions
    if (user.permissions && Array.isArray(user.permissions)) {
      return user.permissions.includes(permission);
    }

    // Fallback to legacy permission checking
    return this.hasLegacyPermission(user, permission);
  }

  /**
   * Check if user has any of the specified permissions
   * @param {Object} user - User object
   * @param {Array} permissions - Array of permissions to check
   * @returns {boolean} - True if user has any of the permissions
   */
  static hasAnyPermission(user, permissions) {
    return permissions.some(permission => this.hasPermission(user, permission));
  }

  /**
   * Check if user has all of the specified permissions
   * @param {Object} user - User object
   * @param {Array} permissions - Array of permissions to check
   * @returns {boolean} - True if user has all permissions
   */
  static hasAllPermissions(user, permissions) {
    return permissions.every(permission => this.hasPermission(user, permission));
  }

  /**
   * Legacy permission checking for backward compatibility
   * @param {Object} user - User object
   * @param {string} permission - Permission to check
   * @returns {boolean} - True if user has permission
   */
  static hasLegacyPermission(user, permission) {
    if (!user) return false;

    // Admin users have all permissions
    if (user.is_admin) return true;

    // Materials department users have tool management permissions
    if (user.department === 'Materials') {
      const materialPermissions = [
        'tool.view', 'tool.create', 'tool.edit', 'tool.delete',
        'tool.checkout', 'tool.return', 'checkout.view_all',
        'chemical.view', 'chemical.create', 'chemical.edit', 'chemical.issue'
      ];
      if (materialPermissions.includes(permission)) return true;
    }

    // Basic permissions for all authenticated users
    const basicPermissions = [
      'dashboard.view', 'tool.view', 'tool.checkout', 'checkout.manage_own'
    ];
    
    return basicPermissions.includes(permission);
  }

  /**
   * Get user's role names
   * @param {Object} user - User object
   * @returns {Array} - Array of role names
   */
  static getUserRoles(user) {
    if (!user || !user.roles) return [];
    return user.roles.map(role => role.name);
  }

  /**
   * Check if user has a specific role
   * @param {Object} user - User object
   * @param {string} roleName - Role name to check
   * @returns {boolean} - True if user has the role
   */
  static hasRole(user, roleName) {
    const userRoles = this.getUserRoles(user);
    return userRoles.includes(roleName);
  }

  /**
   * Check if user has any of the specified roles
   * @param {Object} user - User object
   * @param {Array} roleNames - Array of role names to check
   * @returns {boolean} - True if user has any of the roles
   */
  static hasAnyRole(user, roleNames) {
    const userRoles = this.getUserRoles(user);
    return roleNames.some(role => userRoles.includes(role));
  }

  /**
   * Get navigation permissions for a user
   * @param {Object} user - User object
   * @returns {Object} - Object with navigation permission flags
   */
  static getNavigationPermissions(user) {
    return {
      // Dashboard
      canViewDashboard: this.hasPermission(user, 'dashboard.view'),
      
      // Tools
      canViewTools: this.hasPermission(user, 'tool.view'),
      canManageTools: this.hasPermission(user, 'tool.create') || this.hasPermission(user, 'tool.edit'),
      canCheckoutTools: this.hasPermission(user, 'tool.checkout'),
      
      // Checkouts
      canViewOwnCheckouts: this.hasPermission(user, 'checkout.manage_own'),
      canViewAllCheckouts: this.hasPermission(user, 'checkout.view_all'),
      
      // Chemicals
      canViewChemicals: this.hasPermission(user, 'chemical.view'),
      canManageChemicals: this.hasPermission(user, 'chemical.create') || this.hasPermission(user, 'chemical.edit'),
      canIssueChemicals: this.hasPermission(user, 'chemical.issue'),
      
      // Calibrations
      canViewCalibrations: this.hasPermission(user, 'calibration.view'),
      canManageCalibrations: this.hasPermission(user, 'calibration.manage'),
      
      // Reports
      canViewReports: this.hasPermission(user, 'report.view'),
      canGenerateReports: this.hasPermission(user, 'report.generate'),
      
      // Cycle Counts
      canViewCycleCounts: this.hasPermission(user, 'cycle_count.view'),
      canParticipateInCycleCounts: this.hasPermission(user, 'cycle_count.participate'),
      
      // Admin functions
      canViewAdminDashboard: this.hasAnyPermission(user, ['user.view', 'role.manage', 'system.settings', 'system.audit']),
      canManageUsers: this.hasPermission(user, 'user.view') || this.hasPermission(user, 'user.edit'),
      canManageRoles: this.hasPermission(user, 'role.manage'),
      canViewAuditLogs: this.hasPermission(user, 'system.audit'),
      canManageSettings: this.hasPermission(user, 'system.settings'),
      canManageAnnouncements: this.hasPermission(user, 'announcement.create') || user.is_admin
    };
  }

  /**
   * Check if user can return tools (Materials and Admin only)
   * @param {Object} user - User object
   * @returns {boolean} - True if user can return tools
   */
  static canReturnTools(user) {
    if (!user) return false;
    return user.is_admin || user.department === 'Materials';
  }

  /**
   * Get role-based restrictions for a user
   * @param {Object} user - User object
   * @returns {Object} - Object with restriction flags
   */
  static getRoleRestrictions(user) {
    const roles = this.getUserRoles(user);
    
    return {
      // Mechanic role restrictions
      isMechanicRole: roles.includes('Mechanic'),
      mechanicCanOnlyViewTools: roles.includes('Mechanic') && !roles.includes('User') && !roles.includes('Lead'),
      
      // User role capabilities
      isUserRole: roles.includes('User'),
      
      // Lead role capabilities
      isLeadRole: roles.includes('Lead'),
      
      // Admin capabilities
      isAdmin: user.is_admin || roles.includes('Administrator')
    };
  }
}

export default PermissionService;
