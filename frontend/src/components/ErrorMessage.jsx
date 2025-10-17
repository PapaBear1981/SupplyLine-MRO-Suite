/* eslint-env node */
/**
 * ErrorMessage Component
 *
 * Reusable error message component with user-friendly messages,
 * recovery actions, and dismiss functionality
 */

import React, { useState, useEffect } from 'react';
import { Alert, Button, Card, Collapse } from 'react-bootstrap';
import { getErrorInfo, ERROR_TYPES } from '../utils/errorMapping';
import errorService from '../services/errorService';
import './ErrorMessage.css';

const ErrorMessage = ({ 
  error, 
  operation = null,
  onRetry = null, 
  onDismiss = null,
  showTechnicalDetails = false,
  autoHide = false,
  autoHideDelay = 5000,
  variant = 'danger',
  className = '',
  size = 'medium' // small, medium, large
}) => {
  const [visible, setVisible] = useState(true);
  const [showDetails, setShowDetails] = useState(false);
  const [retrying, setRetrying] = useState(false);

  // Get error information
  const errorInfo = error ? getErrorInfo(error, operation) : null;

  useEffect(() => {
    if (error && errorInfo) {
      // Log the error
      errorService.logError(error, operation, { component: 'ErrorMessage' });
    }
  }, [error, operation, errorInfo]);

  useEffect(() => {
    if (autoHide && visible) {
      const timer = setTimeout(() => {
        setVisible(false);
        if (onDismiss) onDismiss();
      }, autoHideDelay);

      return () => clearTimeout(timer);
    }
  }, [autoHide, autoHideDelay, visible, onDismiss]);

  const handleRetry = async () => {
    if (onRetry && !retrying) {
      setRetrying(true);
      try {
        await onRetry();
        setVisible(false);
      } catch (retryError) {
        errorService.logError(retryError, `${operation}_RETRY`);
      } finally {
        setRetrying(false);
      }
    }
  };

  const handleDismiss = () => {
    setVisible(false);
    if (onDismiss) onDismiss();
  };

  const getErrorIcon = (errorType) => {
    switch (errorType) {
      case ERROR_TYPES.AUTH_ERROR:
        return '🔒';
      case ERROR_TYPES.NETWORK_ERROR:
        return '🌐';
      case ERROR_TYPES.VALIDATION_ERROR:
        return '📝';
      case ERROR_TYPES.PERMISSION_DENIED:
        return '🚫';
      case ERROR_TYPES.NOT_FOUND:
        return '🔍';
      case ERROR_TYPES.SERVER_ERROR:
        return '🔧';
      case ERROR_TYPES.TIMEOUT_ERROR:
        return '⏱️';
      case ERROR_TYPES.RATE_LIMIT:
        return '🚦';
      default:
        return '⚠️';
    }
  };

  const getSeverityVariant = (severity) => {
    switch (severity) {
      case 'low':
        return 'warning';
      case 'medium':
        return 'danger';
      case 'high':
        return 'danger';
      case 'critical':
        return 'danger';
      default:
        return variant;
    }
  };

  if (!visible || !error || !errorInfo) {
    return null;
  }

  const alertVariant = getSeverityVariant(errorInfo.severity);
  const errorIcon = getErrorIcon(errorInfo.type);

  return (
    <div className={`error-message-container ${className} error-message-${size}`}>
      <Alert 
        variant={alertVariant} 
        dismissible={!!onDismiss}
        onClose={handleDismiss}
        className="error-message-alert"
      >
        <div className="error-message-content">
          <div className="error-message-header">
            <div className="error-icon" role="img" aria-label="Error icon">
              {errorIcon}
            </div>
            <div className="error-text">
              <Alert.Heading className="error-title">
                Something went wrong
              </Alert.Heading>
              <p className="error-user-message">
                {errorInfo.user}
              </p>
            </div>
          </div>

          <div className="error-message-actions">
            {onRetry && errorInfo.retryable && (
              <Button
                variant="outline-primary"
                size="sm"
                onClick={handleRetry}
                disabled={retrying}
                className="error-action-button"
              >
                {retrying ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Retrying...
                  </>
                ) : (
                  errorInfo.action
                )}
              </Button>
            )}

            {(showTechnicalDetails || process.env.NODE_ENV === 'development') && (
              <Button
                variant="outline-secondary"
                size="sm"
                onClick={() => setShowDetails(!showDetails)}
                className="error-details-toggle"
              >
                {showDetails ? 'Hide Details' : 'Show Details'}
              </Button>
            )}
          </div>

          <Collapse in={showDetails}>
            <div className="error-technical-details">
              <Card className="mt-3">
                <Card.Header>
                  <small className="text-muted">Technical Details</small>
                </Card.Header>
                <Card.Body>
                  <div className="technical-info">
                    <div className="info-row">
                      <strong>Type:</strong> {errorInfo.type}
                    </div>
                    <div className="info-row">
                      <strong>Technical:</strong> {errorInfo.technical}
                    </div>
                    {operation && (
                      <div className="info-row">
                        <strong>Operation:</strong> {operation}
                      </div>
                    )}
                    <div className="info-row">
                      <strong>Timestamp:</strong> {errorInfo.timestamp || new Date().toISOString()}
                    </div>
                    {errorInfo.originalError?.message && (
                      <div className="info-row">
                        <strong>Original Message:</strong> {errorInfo.originalError.message}
                      </div>
                    )}
                    {errorInfo.originalError?.stack && process.env.NODE_ENV === 'development' && (
                      <div className="info-row">
                        <strong>Stack Trace:</strong>
                        <pre className="error-stack">{errorInfo.originalError.stack}</pre>
                      </div>
                    )}
                  </div>
                </Card.Body>
              </Card>
            </div>
          </Collapse>
        </div>
      </Alert>
    </div>
  );
};

// Specialized error message components for common scenarios
export const NetworkErrorMessage = ({ onRetry, onDismiss }) => (
  <ErrorMessage
    error={{ message: 'Network connection failed' }}
    operation="NETWORK_CONNECTION"
    onRetry={onRetry}
    onDismiss={onDismiss}
  />
);

export const AuthErrorMessage = ({ onLogin, onDismiss }) => (
  <ErrorMessage
    error={{ message: 'Authentication required' }}
    operation="AUTHENTICATION"
    onRetry={onLogin}
    onDismiss={onDismiss}
  />
);

export const ValidationErrorMessage = ({ errors, onDismiss }) => (
  <ErrorMessage
    error={{ message: 'Validation failed', details: errors }}
    operation="FORM_VALIDATION"
    onDismiss={onDismiss}
  />
);

export const ServerErrorMessage = ({ onRetry, onDismiss }) => (
  <ErrorMessage
    error={{ message: 'Server error occurred' }}
    operation="SERVER_REQUEST"
    onRetry={onRetry}
    onDismiss={onDismiss}
  />
);

export default ErrorMessage;
