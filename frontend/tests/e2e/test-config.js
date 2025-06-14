/**
 * Test configuration and constants for E2E tests
 */

export const TEST_CONFIG = {
  // Timeouts
  timeouts: {
    short: 2000,
    medium: 5000,
    long: 10000,
    veryLong: 30000
  },
  
  // URLs
  urls: {
    frontend: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173',
    backend: process.env.BACKEND_URL || 'http://localhost:5000',
    api: process.env.API_URL || 'http://localhost:5000/api'
  },
  
  // Test users
  users: {
    admin: {
      employee_number: 'ADMIN001',
      password: 'admin123',
      name: 'Admin User',
      department: 'IT',
      is_admin: true
    },
    regularUser: {
      employee_number: 'USER001',
      password: 'user123',
      name: 'Regular User',
      department: 'Production',
      is_admin: false
    },
    materialsUser: {
      employee_number: 'MAT001',
      password: 'materials123',
      name: 'Materials User',
      department: 'Materials',
      is_admin: false
    }
  },
  
  // Test data prefixes
  testDataPrefixes: {
    tool: 'E2E_TOOL_',
    chemical: 'E2E_CHEM_',
    user: 'E2E_USER_',
    schedule: 'E2E_SCHEDULE_'
  },
  
  // Browser configurations
  browsers: {
    desktop: {
      chromium: { width: 1280, height: 720 },
      firefox: { width: 1280, height: 720 },
      webkit: { width: 1280, height: 720 }
    },
    mobile: {
      'iPhone 12': { width: 390, height: 844 },
      'Pixel 5': { width: 393, height: 851 },
      'iPad': { width: 820, height: 1180 }
    }
  },
  
  // Performance thresholds
  performance: {
    pageLoad: 3000,        // 3 seconds
    apiResponse: 2000,     // 2 seconds
    formSubmission: 3000,  // 3 seconds
    search: 2000,          // 2 seconds
    tableLoad: 5000        // 5 seconds
  },
  
  // Visual regression thresholds
  visual: {
    threshold: 0.2,        // 20% difference threshold
    pixelThreshold: 100    // 100 pixel difference threshold
  },
  
  // Accessibility standards
  accessibility: {
    level: 'AA',           // WCAG 2.1 AA compliance
    tags: ['wcag2a', 'wcag2aa', 'wcag21aa']
  }
};

export const TEST_SELECTORS = {
  // Authentication
  auth: {
    employeeNumberInput: '[data-testid="employee-number-input"]',
    passwordInput: '[data-testid="password-input"]',
    loginButton: '[data-testid="login-button"]',
    logoutButton: '[data-testid="logout-button"]',
    userMenu: '[data-testid="user-menu"]'
  },
  
  // Navigation
  navigation: {
    mainNav: '[data-testid="main-navigation"]',
    mobileNav: '[data-testid="mobile-navigation"]',
    hamburgerMenu: '[data-testid="hamburger-menu"]',
    adminDashboardLink: '[data-testid="admin-dashboard-link"]'
  },
  
  // Dashboard
  dashboard: {
    content: '[data-testid="dashboard-content"]',
    quickActions: '[data-testid="quick-actions"]',
    userCheckoutStatus: '[data-testid="user-checkout-status"]',
    recentActivity: '[data-testid="recent-activity"]',
    announcements: '[data-testid="announcements"]'
  },
  
  // Tools
  tools: {
    table: '[data-testid="tools-table"]',
    searchInput: '[data-testid="tools-search-input"]',
    addButton: '[data-testid="add-tool-button"]',
    form: '[data-testid="tool-form"]',
    toolNumberInput: '[data-testid="tool-number-input"]',
    serialNumberInput: '[data-testid="serial-number-input"]',
    descriptionInput: '[data-testid="description-input"]',
    saveButton: '[data-testid="save-tool-button"]'
  },
  
  // Chemicals
  chemicals: {
    table: '[data-testid="chemicals-table"]',
    searchInput: '[data-testid="chemicals-search-input"]',
    addButton: '[data-testid="add-chemical-button"]',
    form: '[data-testid="chemical-form"]',
    partNumberInput: '[data-testid="part-number-input"]',
    descriptionInput: '[data-testid="chemical-description-input"]',
    saveButton: '[data-testid="save-chemical-button"]'
  },
  
  // Checkouts
  checkouts: {
    form: '[data-testid="checkout-form"]',
    employeeNumberInput: '[data-testid="employee-number-input"]',
    toolNumberInput: '[data-testid="tool-number-input"]',
    checkoutButton: '[data-testid="checkout-button"]',
    returnSection: '[data-testid="return-section"]',
    returnButton: '[data-testid="return-button"]'
  },
  
  // Common elements
  common: {
    loadingSpinner: '.loading-spinner, .spinner-border',
    toast: '.toast',
    modal: '.modal',
    confirmButton: '[data-testid="confirm-button"]',
    cancelButton: '[data-testid="cancel-button"]',
    deleteConfirmation: '[data-testid="delete-confirmation"]',
    errorMessage: '.error-message, .alert-danger',
    successMessage: '.success-message, .alert-success'
  }
};

export const TEST_ROUTES = {
  // Public routes
  login: '/login',
  register: '/register',
  
  // Protected routes
  dashboard: '/dashboard',
  tools: '/tools',
  toolsNew: '/tools/new',
  toolsEdit: (id) => `/tools/${id}/edit`,
  toolsDetail: (id) => `/tools/${id}`,
  
  chemicals: '/chemicals',
  chemicalsNew: '/chemicals/new',
  chemicalsEdit: (id) => `/chemicals/${id}/edit`,
  chemicalsDetail: (id) => `/chemicals/${id}`,
  
  checkouts: '/checkouts',
  checkoutsAll: '/checkouts/all',
  
  cycleCount: '/cycle-counts',
  cycleCountMobile: '/cycle-counts/mobile',
  
  calibrations: '/calibrations',
  
  reports: '/reports',
  
  // Admin routes
  adminDashboard: '/admin/dashboard',
  
  // Scanner
  scanner: '/scanner'
};

export const API_ENDPOINTS = {
  // Authentication
  auth: {
    login: '/api/auth/login',
    logout: '/api/auth/logout',
    register: '/api/auth/register',
    currentUser: '/api/auth/current-user'
  },
  
  // Tools
  tools: {
    list: '/api/tools',
    create: '/api/tools',
    detail: (id) => `/api/tools/${id}`,
    update: (id) => `/api/tools/${id}`,
    delete: (id) => `/api/tools/${id}`,
    search: '/api/tools/search'
  },
  
  // Chemicals
  chemicals: {
    list: '/api/chemicals',
    create: '/api/chemicals',
    detail: (id) => `/api/chemicals/${id}`,
    update: (id) => `/api/chemicals/${id}`,
    delete: (id) => `/api/chemicals/${id}`,
    search: '/api/chemicals/search'
  },
  
  // Checkouts
  checkouts: {
    list: '/api/checkouts',
    create: '/api/checkouts',
    return: '/api/checkouts/return',
    userCheckouts: '/api/checkouts/user'
  },
  
  // Cycle Count
  cycleCount: {
    schedules: '/api/cycle-count/schedules',
    batches: '/api/cycle-count/batches',
    items: '/api/cycle-count/items'
  },
  
  // Calibration
  calibration: {
    list: '/api/calibration',
    standards: '/api/calibration/standards',
    schedule: '/api/calibration/schedule'
  },
  
  // Admin
  admin: {
    dashboard: '/api/admin/dashboard',
    users: '/api/admin/users',
    registrations: '/api/admin/registrations'
  },
  
  // Health check
  health: '/api/health'
};

export const ERROR_MESSAGES = {
  // Authentication
  invalidCredentials: 'Invalid credentials',
  userNotFound: 'User not found',
  accountLocked: 'Account is locked',
  
  // Validation
  requiredField: 'This field is required',
  invalidEmail: 'Please enter a valid email',
  passwordTooShort: 'Password must be at least 8 characters',
  
  // Tools
  toolNotFound: 'Tool not found',
  toolAlreadyCheckedOut: 'Tool is already checked out',
  duplicateToolNumber: 'Tool number already exists',
  
  // Chemicals
  chemicalNotFound: 'Chemical not found',
  insufficientQuantity: 'Insufficient quantity available',
  
  // Network
  networkError: 'Network error occurred',
  serverError: 'Server error occurred',
  timeout: 'Request timed out'
};

export const SUCCESS_MESSAGES = {
  // Authentication
  loginSuccess: 'Login successful',
  logoutSuccess: 'Logout successful',
  
  // Tools
  toolCreated: 'Tool created successfully',
  toolUpdated: 'Tool updated successfully',
  toolDeleted: 'Tool deleted successfully',
  toolCheckedOut: 'Tool checked out successfully',
  toolReturned: 'Tool returned successfully',
  
  // Chemicals
  chemicalCreated: 'Chemical created successfully',
  chemicalUpdated: 'Chemical updated successfully',
  chemicalDeleted: 'Chemical deleted successfully',
  chemicalIssued: 'Chemical issued successfully',
  
  // General
  saveSuccess: 'Changes saved successfully',
  deleteSuccess: 'Item deleted successfully'
};

export default {
  TEST_CONFIG,
  TEST_SELECTORS,
  TEST_ROUTES,
  API_ENDPOINTS,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES
};
