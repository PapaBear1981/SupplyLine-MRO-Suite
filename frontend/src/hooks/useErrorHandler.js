/**
 * useErrorHandler Hook
 * 
 * Custom hook for consistent error handling across components
 */

import { useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import errorService from '../services/errorService';
import { getErrorInfo, ERROR_TYPES } from '../utils/errorMapping';

export const useErrorHandler = (options = {}) => {
  const {
    operation = null,
    onError = null,
    onRetry = null,
    autoRetry = false,
    maxRetries = 3,
    retryDelay = 1000,
    logErrors = true
  } = options;

  const [error, setError] = useState(null);
  const [isRetrying, setIsRetrying] = useState(false);
  const retryCountRef = useRef(0);
  const retryRef = useRef(() => {});
  const navigate = useNavigate();

  /**
   * Handle an error with logging and user feedback
   */
  const handleError = useCallback((err, context = {}) => {
    const errorInfo = getErrorInfo(err, operation);
    
    // Log error if enabled
    if (logErrors) {
      errorService.logError(err, operation, context);
    }

    // Set error state
    setError({
      ...errorInfo,
      originalError: err,
      context
    });

    // Handle specific error types
    switch (errorInfo.type) {
      case ERROR_TYPES.AUTH_ERROR:
        // Redirect to login for auth errors
        setTimeout(() => {
          navigate('/login');
        }, 2000);
        break;
      
      case ERROR_TYPES.PERMISSION_DENIED:
        // Show permission denied message
        break;
      
      case ERROR_TYPES.NOT_FOUND:
        // Could redirect to 404 page
        break;
      
      default:
        break;
    }

    // Call custom error handler
    if (onError) {
      onError(err, errorInfo);
    }

    // Auto retry if enabled
    if (autoRetry && errorInfo.retryable && retryCountRef.current < maxRetries) {
      setTimeout(() => {
        retryRef.current();
      }, retryDelay * Math.pow(2, retryCountRef.current)); // Exponential backoff
    }

    return errorInfo;
  }, [operation, onError, autoRetry, maxRetries, retryDelay, logErrors, navigate]);

  /**
   * Clear the current error
   */
  const clearError = useCallback(() => {
    setError(null);
    retryCountRef.current = 0;
  }, []);

  /**
   * Retry the failed operation
   */
  const retry = useCallback(async () => {
    if (!error || !error.retryable || isRetrying) {
      return;
    }

    setIsRetrying(true);
    retryCountRef.current += 1;

    try {
      if (onRetry) {
        await onRetry();
        clearError();
      }
    } catch (retryError) {
      handleError(retryError, { isRetry: true, retryCount: retryCountRef.current });
    } finally {
      setIsRetrying(false);
    }
  }, [error, isRetrying, onRetry, clearError, handleError]);

  // Update retry ref
  retryRef.current = retry;

  /**
   * Wrapper for async operations with error handling
   */
  const withErrorHandling = useCallback((asyncFn, context = {}) => {
    return async (...args) => {
      try {
        clearError();
        return await asyncFn(...args);
      } catch (err) {
        handleError(err, context);
        throw err; // Re-throw so calling code can handle if needed
      }
    };
  }, [clearError, handleError]);

  /**
   * Safe async operation that doesn't throw
   */
  const safeAsync = useCallback((asyncFn, context = {}) => {
    return async (...args) => {
      try {
        clearError();
        const result = await asyncFn(...args);
        return { success: true, data: result, error: null };
      } catch (err) {
        const errorInfo = handleError(err, context);
        return { success: false, data: null, error: errorInfo };
      }
    };
  }, [clearError, handleError]);

  return {
    error,
    isRetrying,
    hasError: !!error,
    handleError,
    clearError,
    retry,
    withErrorHandling,
    safeAsync,
    canRetry: error?.retryable && !isRetrying && retryCountRef.current < maxRetries
  };
};

/**
 * Hook for handling form errors specifically
 */
export const useFormErrorHandler = (options = {}) => {
  const [fieldErrors, setFieldErrors] = useState({});
  const errorHandler = useErrorHandler(options);

  const handleFormError = useCallback((err, fieldName = null) => {
    // Handle validation errors with field-specific messages
    if (err.response?.data?.errors) {
      setFieldErrors(err.response.data.errors);
    } else if (fieldName) {
      setFieldErrors(prev => ({
        ...prev,
        [fieldName]: err.message || 'Invalid value'
      }));
    }

    return errorHandler.handleError(err);
  }, [errorHandler]);

  const clearFieldError = useCallback((fieldName) => {
    setFieldErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[fieldName];
      return newErrors;
    });
  }, []);

  const clearAllFieldErrors = useCallback(() => {
    setFieldErrors({});
  }, []);

  return {
    ...errorHandler,
    fieldErrors,
    hasFieldErrors: Object.keys(fieldErrors).length > 0,
    handleFormError,
    clearFieldError,
    clearAllFieldErrors,
    getFieldError: (fieldName) => fieldErrors[fieldName]
  };
};

/**
 * Hook for handling API errors specifically
 */
export const useApiErrorHandler = (options = {}) => {
  const errorHandler = useErrorHandler({
    ...options,
    operation: options.operation || 'API_REQUEST'
  });

  const handleApiError = useCallback((err, endpoint = null) => {
    const context = {
      endpoint,
      status: err.response?.status,
      statusText: err.response?.statusText,
      data: err.response?.data
    };

    return errorHandler.handleError(err, context);
  }, [errorHandler]);

  return {
    ...errorHandler,
    handleApiError
  };
};

export default useErrorHandler;
