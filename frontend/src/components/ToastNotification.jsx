/**
 * ToastNotification Component
 * 
 * Toast notification system with different types (success, error, info),
 * auto-dismiss, and manual close functionality
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Toast, ToastContainer } from 'react-bootstrap';
import './ToastNotification.css';

// Toast types
export const TOAST_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info'
};

// Toast positions
export const TOAST_POSITIONS = {
  TOP_RIGHT: 'top-end',
  TOP_LEFT: 'top-start',
  TOP_CENTER: 'top-center',
  BOTTOM_RIGHT: 'bottom-end',
  BOTTOM_LEFT: 'bottom-start',
  BOTTOM_CENTER: 'bottom-center'
};

const ToastNotification = ({ 
  id,
  type = TOAST_TYPES.INFO, 
  title = '',
  message, 
  duration = 5000,
  persistent = false,
  showIcon = true,
  showClose = true,
  onClose = null,
  onClick = null,
  className = '',
  style = {}
}) => {
  const [visible, setVisible] = useState(true);

  const handleClose = useCallback(() => {
    setVisible(false);
    if (onClose) {
      onClose(id);
    }
  }, [onClose, id]);

  useEffect(() => {
    if (!persistent && duration > 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration, persistent, handleClose]);

  const handleClick = () => {
    if (onClick) {
      onClick(id);
    }
  };

  const getToastIcon = (toastType) => {
    switch (toastType) {
      case TOAST_TYPES.SUCCESS:
        return '✅';
      case TOAST_TYPES.ERROR:
        return '❌';
      case TOAST_TYPES.WARNING:
        return '⚠️';
      case TOAST_TYPES.INFO:
        return 'ℹ️';
      default:
        return 'ℹ️';
    }
  };

  // Removed unused getToastVariant function - Bootstrap Toast doesn't use variant prop

  if (!visible) return null;

  return (
    <Toast
      show={visible}
      onClose={showClose ? handleClose : undefined}
      onClick={onClick ? handleClick : undefined}
      className={`toast-notification toast-${type} ${className}`}
      style={style}
      role="alert"
      aria-live="polite"
      aria-atomic="true"
    >
      {title && (
        <Toast.Header closeButton={showClose}>
          {showIcon && (
            <span className="toast-icon me-2" role="img" aria-label={`${type} icon`}>
              {getToastIcon(type)}
            </span>
          )}
          <strong className="toast-title">{title}</strong>
        </Toast.Header>
      )}
      <Toast.Body className={title ? '' : 'd-flex align-items-center'}>
        {!title && showIcon && (
          <span className="toast-icon me-2" role="img" aria-label={`${type} icon`}>
            {getToastIcon(type)}
          </span>
        )}
        <span className="toast-message">{message}</span>
        {!title && showClose && (
          <button
            type="button"
            className="btn-close ms-auto"
            aria-label="Close"
            onClick={handleClose}
          />
        )}
      </Toast.Body>
    </Toast>
  );
};

// Toast Container Component
export const ToastNotificationContainer = ({ 
  toasts = [], 
  position = TOAST_POSITIONS.TOP_RIGHT,
  className = '',
  onRemoveToast = null
}) => {
  const handleRemoveToast = (toastId) => {
    if (onRemoveToast) {
      onRemoveToast(toastId);
    }
  };

  return (
    <ToastContainer 
      position={position}
      className={`toast-notification-container ${className}`}
    >
      {toasts.map((toast) => (
        <ToastNotification
          key={toast.id}
          {...toast}
          onClose={handleRemoveToast}
        />
      ))}
    </ToastContainer>
  );
};

// Specialized toast components
export const SuccessToast = ({ message, title = 'Success', ...props }) => (
  <ToastNotification
    type={TOAST_TYPES.SUCCESS}
    title={title}
    message={message}
    {...props}
  />
);

export const ErrorToast = ({ message, title = 'Error', persistent = true, ...props }) => (
  <ToastNotification
    type={TOAST_TYPES.ERROR}
    title={title}
    message={message}
    persistent={persistent}
    {...props}
  />
);

export const WarningToast = ({ message, title = 'Warning', duration = 7000, ...props }) => (
  <ToastNotification
    type={TOAST_TYPES.WARNING}
    title={title}
    message={message}
    duration={duration}
    {...props}
  />
);

export const InfoToast = ({ message, title = 'Information', ...props }) => (
  <ToastNotification
    type={TOAST_TYPES.INFO}
    title={title}
    message={message}
    {...props}
  />
);

// Operation-specific toast messages
export const OperationSuccessToast = ({ operation, item = '', ...props }) => (
  <SuccessToast
    message={`${operation} ${item} successfully completed.`}
    {...props}
  />
);

export const OperationErrorToast = ({ operation, item = '', error = '', ...props }) => (
  <ErrorToast
    message={`Failed to ${operation.toLowerCase()} ${item}. ${error}`}
    {...props}
  />
);

export const ValidationErrorToast = ({ field = '', message = '', ...props }) => (
  <ErrorToast
    title="Validation Error"
    message={field ? `${field}: ${message}` : message}
    {...props}
  />
);

export const NetworkErrorToast = ({ ...props }) => (
  <ErrorToast
    title="Connection Error"
    message="Unable to connect to the server. Please check your connection and try again."
    {...props}
  />
);

export const AuthErrorToast = ({ ...props }) => (
  <ErrorToast
    title="Authentication Required"
    message="Your session has expired. Please log in again."
    {...props}
  />
);

export const SaveSuccessToast = ({ item = 'item', ...props }) => (
  <SuccessToast
    message={`${item} saved successfully.`}
    duration={3000}
    {...props}
  />
);

export const DeleteSuccessToast = ({ item = 'item', ...props }) => (
  <SuccessToast
    message={`${item} deleted successfully.`}
    duration={3000}
    {...props}
  />
);

export const CreateSuccessToast = ({ item = 'item', ...props }) => (
  <SuccessToast
    message={`${item} created successfully.`}
    duration={3000}
    {...props}
  />
);

export const UpdateSuccessToast = ({ item = 'item', ...props }) => (
  <SuccessToast
    message={`${item} updated successfully.`}
    duration={3000}
    {...props}
  />
);

export default ToastNotification;
