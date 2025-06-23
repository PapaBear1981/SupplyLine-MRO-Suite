/**
 * Notification Service
 * 
 * Centralized service for managing toast notifications with queue management,
 * persistence options, and notification preferences
 */

import { TOAST_TYPES, TOAST_POSITIONS } from '../components/ToastNotification';

class NotificationService {
  constructor() {
    this.notifications = [];
    this.maxNotifications = 5;
    this.defaultDuration = 5000;
    this.listeners = [];
    this.preferences = this.loadPreferences();
    this.nextId = 1;
  }

  /**
   * Add a listener for notification changes
   * @param {Function} listener - Callback function
   */
  addListener(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  /**
   * Notify all listeners of changes
   */
  notifyListeners() {
    this.listeners.forEach(listener => listener(this.notifications));
  }

  /**
   * Add a notification to the queue
   * @param {Object} notification - Notification object
   */
  addNotification(notification) {
    if (!this.preferences.enabled) {
      return null;
    }

    const id = `notification_${this.nextId++}`;
    const newNotification = {
      id,
      type: TOAST_TYPES.INFO,
      duration: this.defaultDuration,
      persistent: false,
      showIcon: true,
      showClose: true,
      timestamp: new Date().toISOString(),
      ...notification
    };

    // Check for duplicates
    if (this.isDuplicate(newNotification)) {
      return null;
    }

    // Add to queue
    this.notifications.push(newNotification);

    // Manage queue size
    this.manageQueueSize();

    // Notify listeners
    this.notifyListeners();

    // Auto-remove if not persistent
    if (!newNotification.persistent && newNotification.duration > 0) {
      setTimeout(() => {
        this.removeNotification(id);
      }, newNotification.duration);
    }

    return id;
  }

  /**
   * Remove a notification by ID
   * @param {string} id - Notification ID
   */
  removeNotification(id) {
    const index = this.notifications.findIndex(n => n.id === id);
    if (index > -1) {
      this.notifications.splice(index, 1);
      this.notifyListeners();
    }
  }

  /**
   * Clear all notifications
   */
  clearAll() {
    this.notifications = [];
    this.notifyListeners();
  }

  /**
   * Clear notifications by type
   * @param {string} type - Notification type
   */
  clearByType(type) {
    this.notifications = this.notifications.filter(n => n.type !== type);
    this.notifyListeners();
  }

  /**
   * Check if notification is duplicate
   * @param {Object} notification - Notification to check
   * @returns {boolean} True if duplicate
   */
  isDuplicate(notification) {
    if (!this.preferences.preventDuplicates) {
      return false;
    }

    const duplicateWindow = 2000; // 2 seconds
    const now = Date.now();

    return this.notifications.some(existing => 
      existing.message === notification.message &&
      existing.type === notification.type &&
      (now - new Date(existing.timestamp).getTime()) < duplicateWindow
    );
  }

  /**
   * Manage queue size by removing oldest notifications
   */
  manageQueueSize() {
    while (this.notifications.length > this.maxNotifications) {
      // Remove oldest non-persistent notification first
      const nonPersistentIndex = this.notifications.findIndex(n => !n.persistent);
      if (nonPersistentIndex > -1) {
        this.notifications.splice(nonPersistentIndex, 1);
      } else {
        // If all are persistent, remove oldest
        this.notifications.shift();
      }
    }
  }

  /**
   * Load user preferences from localStorage
   * @returns {Object} Preferences object
   */
  loadPreferences() {
    try {
      const stored = localStorage.getItem('notificationPreferences');
      return stored ? JSON.parse(stored) : this.getDefaultPreferences();
    } catch {
      return this.getDefaultPreferences();
    }
  }

  /**
   * Get default preferences
   * @returns {Object} Default preferences
   */
  getDefaultPreferences() {
    return {
      enabled: true,
      position: TOAST_POSITIONS.TOP_RIGHT,
      preventDuplicates: true,
      maxNotifications: 5,
      defaultDuration: 5000,
      enabledTypes: {
        [TOAST_TYPES.SUCCESS]: true,
        [TOAST_TYPES.ERROR]: true,
        [TOAST_TYPES.WARNING]: true,
        [TOAST_TYPES.INFO]: true
      }
    };
  }

  /**
   * Update preferences
   * @param {Object} newPreferences - New preferences
   */
  updatePreferences(newPreferences) {
    this.preferences = { ...this.preferences, ...newPreferences };
    this.maxNotifications = this.preferences.maxNotifications;
    this.defaultDuration = this.preferences.defaultDuration;
    
    try {
      localStorage.setItem('notificationPreferences', JSON.stringify(this.preferences));
    } catch (error) {
      console.warn('Failed to save notification preferences:', error);
    }
  }

  /**
   * Show success notification
   * @param {string} message - Message to display
   * @param {Object} options - Additional options
   */
  success(message, options = {}) {
    return this.addNotification({
      type: TOAST_TYPES.SUCCESS,
      message,
      duration: 3000,
      ...options
    });
  }

  /**
   * Show error notification
   * @param {string} message - Message to display
   * @param {Object} options - Additional options
   */
  error(message, options = {}) {
    return this.addNotification({
      type: TOAST_TYPES.ERROR,
      message,
      persistent: true,
      ...options
    });
  }

  /**
   * Show warning notification
   * @param {string} message - Message to display
   * @param {Object} options - Additional options
   */
  warning(message, options = {}) {
    return this.addNotification({
      type: TOAST_TYPES.WARNING,
      message,
      duration: 7000,
      ...options
    });
  }

  /**
   * Show info notification
   * @param {string} message - Message to display
   * @param {Object} options - Additional options
   */
  info(message, options = {}) {
    return this.addNotification({
      type: TOAST_TYPES.INFO,
      message,
      ...options
    });
  }

  /**
   * Show operation success notification
   * @param {string} operation - Operation name
   * @param {string} item - Item name
   * @param {Object} options - Additional options
   */
  operationSuccess(operation, item = '', options = {}) {
    return this.success(`${operation} ${item} successfully completed.`, options);
  }

  /**
   * Show operation error notification
   * @param {string} operation - Operation name
   * @param {string} item - Item name
   * @param {string} error - Error message
   * @param {Object} options - Additional options
   */
  operationError(operation, item = '', error = '', options = {}) {
    return this.error(`Failed to ${operation.toLowerCase()} ${item}. ${error}`, options);
  }

  /**
   * Show network error notification
   * @param {Object} options - Additional options
   */
  networkError(options = {}) {
    return this.error(
      'Unable to connect to the server. Please check your connection and try again.',
      { title: 'Connection Error', ...options }
    );
  }

  /**
   * Show authentication error notification
   * @param {Object} options - Additional options
   */
  authError(options = {}) {
    return this.error(
      'Your session has expired. Please log in again.',
      { title: 'Authentication Required', ...options }
    );
  }

  /**
   * Get current notifications
   * @returns {Array} Current notifications
   */
  getNotifications() {
    return [...this.notifications];
  }

  /**
   * Get preferences
   * @returns {Object} Current preferences
   */
  getPreferences() {
    return { ...this.preferences };
  }
}

// Create singleton instance
const notificationService = new NotificationService();

export default notificationService;
