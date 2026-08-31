/**
 * Error Message Mapping System
 * 
 * Provides user-friendly error messages, recovery actions, and technical details
 * for different error types throughout the application.
 */

// Error types enum for consistency
export const ERROR_TYPES = {
  CORS_ERROR: 'CORS_ERROR',
  AUTH_ERROR: 'AUTH_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  NETWORK_ERROR: 'NETWORK_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  NOT_FOUND: 'NOT_FOUND',
  PERMISSION_DENIED: 'PERMISSION_DENIED',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR',
  RATE_LIMIT: 'RATE_LIMIT',
  CONFLICT_ERROR: 'CONFLICT_ERROR',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR'
};

// Comprehensive error message mapping
export const ERROR_MESSAGES = {
  [ERROR_TYPES.CORS_ERROR]: {
    user: "There's a temporary connection issue. Please try again in a moment.",
    action: "Retry",
    technical: "CORS configuration blocking request headers",
    severity: "medium",
    recoverable: true,
    retryable: true
  },
  
  [ERROR_TYPES.AUTH_ERROR]: {
    user: "Your session has expired. Please log in again.",
    action: "Login",
    technical: "JWT token invalid or expired",
    severity: "high",
    recoverable: true,
    retryable: false
  },
  
  [ERROR_TYPES.VALIDATION_ERROR]: {
    user: "Please check the highlighted fields and try again.",
    action: "Fix Fields",
    technical: "Form validation failed",
    severity: "low",
    recoverable: true,
    retryable: true
  },
  
  [ERROR_TYPES.NETWORK_ERROR]: {
    user: "Unable to connect to the server. Please check your connection.",
    action: "Retry",
    technical: "Network request failed",
    severity: "high",
    recoverable: true,
    retryable: true
  },
  
  [ERROR_TYPES.SERVER_ERROR]: {
    user: "Something went wrong on our end. We're working to fix it.",
    action: "Retry Later",
    technical: "Internal server error (500)",
    severity: "high",
    recoverable: true,
    retryable: true
  },
  
  [ERROR_TYPES.NOT_FOUND]: {
    user: "The requested item could not be found.",
    action: "Go Back",
    technical: "Resource not found (404)",
    severity: "medium",
    recoverable: false,
    retryable: false
  },
  
  [ERROR_TYPES.PERMISSION_DENIED]: {
    user: "You don't have permission to perform this action.",
    action: "Contact Admin",
    technical: "Insufficient permissions (403)",
    severity: "medium",
    recoverable: false,
    retryable: false
  },
  
  [ERROR_TYPES.TIMEOUT_ERROR]: {
    user: "The request is taking longer than expected. Please try again.",
    action: "Retry",
    technical: "Request timeout",
    severity: "medium",
    recoverable: true,
    retryable: true
  },
  
  [ERROR_TYPES.RATE_LIMIT]: {
    user: "Too many requests. Please wait a moment before trying again.",
    action: "Wait & Retry",
    technical: "Rate limit exceeded (429)",
    severity: "low",
    recoverable: true,
    retryable: true
  },
  
  [ERROR_TYPES.CONFLICT_ERROR]: {
    user: "This action conflicts with current data. Please refresh and try again.",
    action: "Refresh",
    technical: "Data conflict (409)",
    severity: "medium",
    recoverable: true,
    retryable: true
  },
  
  [ERROR_TYPES.UNKNOWN_ERROR]: {
    user: "An unexpected error occurred. Please try again or contact support.",
    action: "Retry",
    technical: "Unknown error",
    severity: "medium",
    recoverable: true,
    retryable: true
  }
};

// Context-specific error messages for different operations
export const OPERATION_ERRORS = {
  TOOL_CREATION: {
    user: "Failed to create tool. Please check all required fields.",
    action: "Check Form",
    technical: "Tool creation validation failed"
  },
  
  CHEMICAL_ISSUE: {
    user: "Unable to issue chemical. Please verify availability and try again.",
    action: "Check Availability",
    technical: "Chemical issue operation failed"
  },
  
  USER_CREATION: {
    user: "Failed to create user account. Please check the information provided.",
    action: "Verify Details",
    technical: "User creation validation failed"
  },
  
  REPORT_GENERATION: {
    user: "Report generation failed. Please try again or contact support.",
    action: "Retry",
    technical: "Report generation error"
  },
  
  DATA_SAVE: {
    user: "Failed to save changes. Please try again.",
    action: "Retry Save",
    technical: "Data persistence error"
  },
  
  DATA_LOAD: {
    user: "Failed to load data. Please refresh the page.",
    action: "Refresh",
    technical: "Data retrieval error"
  }
};

/**
 * Determines error type based on error object or HTTP status
 * @param {Error|Object} error - Error object or response
 * @returns {string} Error type from ERROR_TYPES
 */
export const determineErrorType = (error) => {
  if (!error) {
    return ERROR_TYPES.UNKNOWN_ERROR;
  }

  // Handle axios errors
  if (error.response) {
    const status = Number(error.response.status);
    
    switch (status) {
      case 400:
        return ERROR_TYPES.VALIDATION_ERROR;
      case 401:
        return ERROR_TYPES.AUTH_ERROR;
      case 403:
        return ERROR_TYPES.PERMISSION_DENIED;
      case 404:
        return ERROR_TYPES.NOT_FOUND;
      case 409:
        return ERROR_TYPES.CONFLICT_ERROR;
      case 429:
        return ERROR_TYPES.RATE_LIMIT;
      case 500:
      case 502:
      case 503:
      case 504:
        return ERROR_TYPES.SERVER_ERROR;
      default:
        return ERROR_TYPES.UNKNOWN_ERROR;
    }
  }
  
  // Handle network errors
  const message = typeof error.message === 'string' ? error.message.toLowerCase() : '';

  // A timeout is also a network failure, so classify the more actionable case first.
  if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT' || message.includes('timeout')) {
    return ERROR_TYPES.TIMEOUT_ERROR;
  }

  if (message.includes('cors') || message.includes('access-control')) {
    return ERROR_TYPES.CORS_ERROR;
  }

  if (error.code === 'NETWORK_ERROR' || error.code === 'ERR_NETWORK' || message.includes('network error')) {
    return ERROR_TYPES.NETWORK_ERROR;
  }
  
  // Handle authentication errors
  if (message.includes('token') || message.includes('authentication')) {
    return ERROR_TYPES.AUTH_ERROR;
  }
  
  return ERROR_TYPES.UNKNOWN_ERROR;
};

/**
 * Gets error information for display
 * @param {Error|Object} error - Error object
 * @param {string} operation - Optional operation context
 * @returns {Object} Error information with user message, action, etc.
 */
export const getErrorInfo = (error, operation = null) => {
  const errorType = determineErrorType(error);
  const baseErrorInfo = ERROR_MESSAGES[errorType] || ERROR_MESSAGES[ERROR_TYPES.UNKNOWN_ERROR];
  
  // Check for operation-specific error messages
  const operationError = operation && OPERATION_ERRORS[operation];
  
  const apiMessage = error?.response?.data?.error;
  const apiHint = error?.response?.data?.hint;
  const safeApiMessage = typeof apiMessage === 'string' && apiMessage.length <= 500
    ? apiMessage
    : null;

  return {
    type: errorType,
    user: safeApiMessage || operationError?.user || baseErrorInfo.user,
    action: apiHint || operationError?.action || baseErrorInfo.action,
    technical: operationError?.technical || baseErrorInfo.technical,
    severity: baseErrorInfo.severity,
    recoverable: baseErrorInfo.recoverable,
    retryable: baseErrorInfo.retryable,
    reference: error?.response?.data?.reference || null,
    originalError: error
  };
};

/**
 * Creates a standardized error object for consistent handling
 * @param {Error|Object} error - Original error
 * @param {string} operation - Operation context
 * @param {Object} metadata - Additional metadata
 * @returns {Object} Standardized error object
 */
export const createStandardError = (error, operation = null, metadata = {}) => {
  const errorInfo = getErrorInfo(error, operation);
  
  return {
    ...errorInfo,
    timestamp: new Date().toISOString(),
    operation,
    metadata,
    id: globalThis.crypto?.randomUUID?.() || `error_${Date.now()}_${Math.random().toString(36).slice(2, 11)}`
  };
};

export default {
  ERROR_TYPES,
  ERROR_MESSAGES,
  OPERATION_ERRORS,
  determineErrorType,
  getErrorInfo,
  createStandardError
};
