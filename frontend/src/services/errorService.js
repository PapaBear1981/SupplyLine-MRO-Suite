/* eslint-env node */
/**
 * Error Service
 *
 * Centralized error logging, reporting, and handling service
 */

import { createStandardError, ERROR_TYPES } from '../utils/errorMapping';

class ErrorService {
  constructor() {
    this.errorQueue = [];
    this.maxQueueSize = 100;
    this.reportingEnabled = process.env.NODE_ENV === 'production';
    this.debugMode = process.env.REACT_APP_DEBUG_MODE === 'true';
  }

  /**
   * Log an error with context information
   * @param {Error|Object} error - Error to log
   * @param {string} operation - Operation context
   * @param {Object} metadata - Additional metadata
   * @param {string} severity - Error severity (low, medium, high, critical)
   */
  logError(error, operation = null, metadata = {}, severity = 'medium') {
    const standardError = createStandardError(error, operation, {
      ...metadata,
      severity,
      userAgent: navigator.userAgent,
      url: window.location.href,
      userId: this.getCurrentUserId(),
      sessionId: this.getSessionId()
    });

    // Add to error queue
    this.addToQueue(standardError);

    // Console logging based on environment
    if (this.debugMode || process.env.NODE_ENV === 'development') {
      console.group(`🚨 Error [${severity.toUpperCase()}]: ${operation || 'Unknown Operation'}`);
      console.error('User Message:', standardError.user);
      console.error('Technical Details:', standardError.technical);
      console.error('Original Error:', error);
      console.error('Metadata:', metadata);
      console.groupEnd();
    }

    // Report critical errors immediately
    if (severity === 'critical') {
      this.reportError(standardError);
    }

    return standardError;
  }

  /**
   * Log a warning with context information
   * @param {string} message - Warning message
   * @param {string} operation - Operation context
   * @param {Object} metadata - Additional metadata
   */
  logWarning(message, operation = null, metadata = {}) {
    const warning = {
      type: 'WARNING',
      message,
      operation,
      metadata,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userId: this.getCurrentUserId()
    };

    if (this.debugMode || process.env.NODE_ENV === 'development') {
      console.warn(`⚠️ Warning [${operation || 'Unknown'}]:`, message, metadata);
    }

    this.addToQueue(warning);
  }

  /**
   * Log an info message
   * @param {string} message - Info message
   * @param {string} operation - Operation context
   * @param {Object} metadata - Additional metadata
   */
  logInfo(message, operation = null, metadata = {}) {
    if (this.debugMode || process.env.NODE_ENV === 'development') {
      console.info(`ℹ️ Info [${operation || 'Unknown'}]:`, message, metadata);
    }
  }

  /**
   * Add error to the queue with size management
   * @param {Object} errorData - Error data to queue
   */
  addToQueue(errorData) {
    this.errorQueue.push(errorData);
    
    // Maintain queue size
    if (this.errorQueue.length > this.maxQueueSize) {
      this.errorQueue.shift(); // Remove oldest error
    }
  }

  /**
   * Report error to external service (placeholder for future implementation)
   * @param {Object} errorData - Error data to report
   */
  async reportError(errorData) {
    if (!this.reportingEnabled) {
      return;
    }

    try {
      // Placeholder for external error reporting service
      // Could integrate with services like Sentry, LogRocket, etc.
      console.log('Reporting error to external service:', errorData);
      
      // Example implementation:
      // await fetch('/api/errors/report', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(errorData)
      // });
    } catch (reportingError) {
      console.error('Failed to report error:', reportingError);
    }
  }

  /**
   * Get current user ID from authentication state
   * @returns {string|null} User ID or null
   */
  getCurrentUserId() {
    try {
      // Try to get user ID from Redux store or localStorage
      const authState = JSON.parse(localStorage.getItem('auth') || '{}');
      return authState.user?.id || authState.user?.employee_number || null;
    } catch {
      return null;
    }
  }

  /**
   * Get session ID for tracking
   * @returns {string} Session ID
   */
  getSessionId() {
    let sessionId = sessionStorage.getItem('sessionId');
    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('sessionId', sessionId);
    }
    return sessionId;
  }

  /**
   * Get error statistics
   * @returns {Object} Error statistics
   */
  getErrorStats() {
    const now = Date.now();
    const oneHourAgo = now - (60 * 60 * 1000);
    const oneDayAgo = now - (24 * 60 * 60 * 1000);

    const recentErrors = this.errorQueue.filter(error => 
      new Date(error.timestamp).getTime() > oneHourAgo
    );

    const dailyErrors = this.errorQueue.filter(error => 
      new Date(error.timestamp).getTime() > oneDayAgo
    );

    return {
      total: this.errorQueue.length,
      lastHour: recentErrors.length,
      lastDay: dailyErrors.length,
      byType: this.getErrorsByType(),
      bySeverity: this.getErrorsBySeverity()
    };
  }

  /**
   * Get errors grouped by type
   * @returns {Object} Errors grouped by type
   */
  getErrorsByType() {
    return this.errorQueue.reduce((acc, error) => {
      const type = error.type || 'UNKNOWN';
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {});
  }

  /**
   * Get errors grouped by severity
   * @returns {Object} Errors grouped by severity
   */
  getErrorsBySeverity() {
    return this.errorQueue.reduce((acc, error) => {
      const severity = error.metadata?.severity || 'medium';
      acc[severity] = (acc[severity] || 0) + 1;
      return acc;
    }, {});
  }

  /**
   * Clear error queue
   */
  clearErrors() {
    this.errorQueue = [];
  }

  /**
   * Get recent errors
   * @param {number} limit - Number of errors to return
   * @returns {Array} Recent errors
   */
  getRecentErrors(limit = 10) {
    return this.errorQueue
      .slice(-limit)
      .reverse(); // Most recent first
  }

  /**
   * Handle global unhandled errors
   */
  setupGlobalErrorHandling() {
    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.logError(
        event.reason,
        'UNHANDLED_PROMISE_REJECTION',
        { promise: event.promise },
        'high'
      );
    });

    // Handle global JavaScript errors
    window.addEventListener('error', (event) => {
      this.logError(
        new Error(event.message),
        'GLOBAL_ERROR',
        {
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno,
          stack: event.error?.stack
        },
        'high'
      );
    });
  }
}

// Create singleton instance
const errorService = new ErrorService();

// Setup global error handling
errorService.setupGlobalErrorHandling();

export default errorService;
