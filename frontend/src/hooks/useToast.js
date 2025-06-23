/**
 * useToast Hook
 * 
 * Custom hook for managing toast notifications with the notification service
 */

import { useState, useEffect, useCallback } from 'react';
import notificationService from '../services/notificationService';

export const useToast = () => {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    // Subscribe to notification changes
    const unsubscribe = notificationService.addListener(setNotifications);
    
    // Get initial notifications
    setNotifications(notificationService.getNotifications());

    return unsubscribe;
  }, []);

  const showToast = useCallback((message, options = {}) => {
    return notificationService.addNotification({
      message,
      ...options
    });
  }, []);

  const showSuccess = useCallback((message, options = {}) => {
    return notificationService.success(message, options);
  }, []);

  const showError = useCallback((message, options = {}) => {
    return notificationService.error(message, options);
  }, []);

  const showWarning = useCallback((message, options = {}) => {
    return notificationService.warning(message, options);
  }, []);

  const showInfo = useCallback((message, options = {}) => {
    return notificationService.info(message, options);
  }, []);

  const removeToast = useCallback((id) => {
    notificationService.removeNotification(id);
  }, []);

  const clearAll = useCallback(() => {
    notificationService.clearAll();
  }, []);

  const clearByType = useCallback((type) => {
    notificationService.clearByType(type);
  }, []);

  // Operation-specific toast methods
  const showOperationSuccess = useCallback((operation, item = '', options = {}) => {
    return notificationService.operationSuccess(operation, item, options);
  }, []);

  const showOperationError = useCallback((operation, item = '', error = '', options = {}) => {
    return notificationService.operationError(operation, item, error, options);
  }, []);

  const showNetworkError = useCallback((options = {}) => {
    return notificationService.networkError(options);
  }, []);

  const showAuthError = useCallback((options = {}) => {
    return notificationService.authError(options);
  }, []);

  // CRUD operation helpers
  const showCreateSuccess = useCallback((item = 'item', options = {}) => {
    return showSuccess(`${item} created successfully.`, { duration: 3000, ...options });
  }, [showSuccess]);

  const showUpdateSuccess = useCallback((item = 'item', options = {}) => {
    return showSuccess(`${item} updated successfully.`, { duration: 3000, ...options });
  }, [showSuccess]);

  const showDeleteSuccess = useCallback((item = 'item', options = {}) => {
    return showSuccess(`${item} deleted successfully.`, { duration: 3000, ...options });
  }, [showSuccess]);

  const showSaveSuccess = useCallback((item = 'item', options = {}) => {
    return showSuccess(`${item} saved successfully.`, { duration: 3000, ...options });
  }, [showSuccess]);

  const showCreateError = useCallback((item = 'item', error = '', options = {}) => {
    return showError(`Failed to create ${item}. ${error}`, options);
  }, [showError]);

  const showUpdateError = useCallback((item = 'item', error = '', options = {}) => {
    return showError(`Failed to update ${item}. ${error}`, options);
  }, [showError]);

  const showDeleteError = useCallback((item = 'item', error = '', options = {}) => {
    return showError(`Failed to delete ${item}. ${error}`, options);
  }, [showError]);

  const showSaveError = useCallback((item = 'item', error = '', options = {}) => {
    return showError(`Failed to save ${item}. ${error}`, options);
  }, [showError]);

  // Validation error helper
  const showValidationError = useCallback((field = '', message = '', options = {}) => {
    const errorMessage = field ? `${field}: ${message}` : message;
    return showError(errorMessage, { title: 'Validation Error', ...options });
  }, [showError]);

  return {
    notifications,
    showToast,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    removeToast,
    clearAll,
    clearByType,
    showOperationSuccess,
    showOperationError,
    showNetworkError,
    showAuthError,
    showCreateSuccess,
    showUpdateSuccess,
    showDeleteSuccess,
    showSaveSuccess,
    showCreateError,
    showUpdateError,
    showDeleteError,
    showSaveError,
    showValidationError
  };
};

/**
 * Hook for managing toast preferences
 */
export const useToastPreferences = () => {
  const [preferences, setPreferences] = useState(notificationService.getPreferences());

  const updatePreferences = useCallback((newPreferences) => {
    notificationService.updatePreferences(newPreferences);
    setPreferences(notificationService.getPreferences());
  }, []);

  const resetPreferences = useCallback(() => {
    const defaultPrefs = notificationService.getDefaultPreferences();
    notificationService.updatePreferences(defaultPrefs);
    setPreferences(defaultPrefs);
  }, []);

  return {
    preferences,
    updatePreferences,
    resetPreferences
  };
};

/**
 * Hook for operation-specific toasts with loading states
 */
export const useOperationToast = (operation = 'operation') => {
  const { showOperationSuccess, showOperationError } = useToast();
  const [isLoading, setIsLoading] = useState(false);

  const executeWithToast = useCallback(async (asyncFn, item = '', options = {}) => {
    setIsLoading(true);
    try {
      const result = await asyncFn();
      showOperationSuccess(operation, item, options);
      return result;
    } catch (error) {
      showOperationError(operation, item, error.message || 'Unknown error', options);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [operation, showOperationSuccess, showOperationError]);

  return {
    isLoading,
    executeWithToast
  };
};

export default useToast;
