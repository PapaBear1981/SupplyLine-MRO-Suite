/**
 * Error Handling Test Page
 * 
 * Test page to demonstrate and validate all error handling components
 * and functionality implemented in Issue #369
 */

import React, { useState } from 'react';
import { Container, Row, Col, Card, Button, Form, Alert } from 'react-bootstrap';
import ErrorMessage from '../components/ErrorMessage';
import ErrorBoundary, { PageErrorBoundary, FormErrorBoundary } from '../components/ErrorBoundary';
import LoadingSpinner, { 
  InlineLoader, 
  OverlayLoader, 
  ProgressLoader,
  ToolCreationLoader,
  AuthenticationLoader 
} from '../components/common/LoadingSpinner';
import { ToastNotificationContainer } from '../components/ToastNotification';
import { useToast } from '../hooks/useToast';
import { useErrorHandler, useFormErrorHandler } from '../hooks/useErrorHandler';
import { ERROR_TYPES } from '../utils/errorMapping';
import errorService from '../services/errorService';

const ErrorHandlingTestPage = () => {
  const [showOverlay, setShowOverlay] = useState(false);
  const [progress, setProgress] = useState(0);
  const [testError, setTestError] = useState(null);
  const [formData, setFormData] = useState({ name: '', email: '' });
  
  const toast = useToast();
  const errorHandler = useErrorHandler({ operation: 'TEST_OPERATION' });
  const formErrorHandler = useFormErrorHandler({ operation: 'FORM_TEST' });

  // Test error scenarios
  const testErrorScenarios = [
    {
      name: 'Network Error',
      error: new Error('Network Error'),
      type: ERROR_TYPES.NETWORK_ERROR
    },
    {
      name: 'Authentication Error',
      error: { response: { status: 401, data: { message: 'Unauthorized' } } },
      type: ERROR_TYPES.AUTH_ERROR
    },
    {
      name: 'Validation Error',
      error: { response: { status: 400, data: { errors: { name: 'Required field' } } } },
      type: ERROR_TYPES.VALIDATION_ERROR
    },
    {
      name: 'Server Error',
      error: { response: { status: 500, data: { message: 'Internal server error' } } },
      type: ERROR_TYPES.SERVER_ERROR
    },
    {
      name: 'CORS Error',
      error: new Error('Access-Control-Allow-Origin header is missing'),
      type: ERROR_TYPES.CORS_ERROR
    }
  ];

  const handleTestError = (scenario) => {
    setTestError(scenario.error);
    errorHandler.handleError(scenario.error);
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    
    // Simulate validation error
    if (!formData.name) {
      const error = new Error('Name is required');
      formErrorHandler.handleFormError(error, 'name');
      return;
    }
    
    if (!formData.email) {
      const error = new Error('Email is required');
      formErrorHandler.handleFormError(error, 'email');
      return;
    }
    
    toast.showSuccess('Form submitted successfully!');
    formErrorHandler.clearError();
    formErrorHandler.clearAllFieldErrors();
  };

  const simulateProgress = () => {
    setProgress(0);
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          toast.showSuccess('Progress completed!');
          return 100;
        }
        return prev + 10;
      });
    }, 500);
  };

  const testToastTypes = () => {
    toast.showSuccess('This is a success message!');
    setTimeout(() => toast.showInfo('This is an info message!'), 1000);
    setTimeout(() => toast.showWarning('This is a warning message!'), 2000);
    setTimeout(() => toast.showError('This is an error message!'), 3000);
  };

  const testOperationToasts = () => {
    toast.showCreateSuccess('Tool');
    setTimeout(() => toast.showUpdateSuccess('Chemical'), 1000);
    setTimeout(() => toast.showDeleteSuccess('User'), 2000);
    setTimeout(() => toast.showCreateError('Report', 'Invalid data provided'), 3000);
  };

  const ComponentWithError = () => {
    throw new Error('Test component error');
  };

  const [showErrorComponent, setShowErrorComponent] = useState(false);

  return (
    <PageErrorBoundary pageName="Error Handling Test">
      <Container className="py-4">
        <Row>
          <Col>
            <h1>Error Handling & User Feedback Test Page</h1>
            <p className="text-muted">
              This page demonstrates all the error handling and user feedback improvements 
              implemented for GitHub Issue #369.
            </p>
          </Col>
        </Row>

        {/* Toast Notification Container */}
        <ToastNotificationContainer 
          toasts={toast.notifications}
          onRemoveToast={toast.removeToast}
        />

        {/* Error Message Testing */}
        <Row className="mb-4">
          <Col>
            <Card>
              <Card.Header>
                <h4>Error Message Component Testing</h4>
              </Card.Header>
              <Card.Body>
                <div className="mb-3">
                  <h6>Test Error Scenarios:</h6>
                  <div className="d-flex gap-2 flex-wrap">
                    {testErrorScenarios.map((scenario, index) => (
                      <Button
                        key={index}
                        variant="outline-danger"
                        size="sm"
                        onClick={() => handleTestError(scenario)}
                      >
                        {scenario.name}
                      </Button>
                    ))}
                    <Button
                      variant="outline-secondary"
                      size="sm"
                      onClick={() => setTestError(null)}
                    >
                      Clear Error
                    </Button>
                  </div>
                </div>

                {testError && (
                  <ErrorMessage
                    error={testError}
                    operation="TEST_SCENARIO"
                    onRetry={() => {
                      console.log('Retrying operation...');
                      setTestError(null);
                    }}
                    onDismiss={() => setTestError(null)}
                    showTechnicalDetails={true}
                  />
                )}

                {errorHandler.error && (
                  <ErrorMessage
                    error={errorHandler.error.originalError}
                    operation={errorHandler.error.operation}
                    onRetry={errorHandler.retry}
                    onDismiss={errorHandler.clearError}
                  />
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Loading States Testing */}
        <Row className="mb-4">
          <Col md={6}>
            <Card>
              <Card.Header>
                <h4>Loading States Testing</h4>
              </Card.Header>
              <Card.Body>
                <div className="mb-3">
                  <h6>Basic Loading Spinners:</h6>
                  <div className="d-flex gap-3 align-items-center mb-3">
                    <LoadingSpinner size="sm" text="Small" />
                    <LoadingSpinner size="md" text="Medium" />
                    <LoadingSpinner size="lg" text="Large" />
                  </div>
                </div>

                <div className="mb-3">
                  <h6>Inline Loaders:</h6>
                  <div className="d-flex gap-3 align-items-center">
                    <InlineLoader text="Loading..." />
                    <Button disabled>
                      <InlineLoader text="" /> Processing
                    </Button>
                  </div>
                </div>

                <div className="mb-3">
                  <h6>Operation-Specific Loaders:</h6>
                  <ToolCreationLoader />
                  <AuthenticationLoader />
                </div>

                <div className="mb-3">
                  <h6>Progress Loader:</h6>
                  <ProgressLoader 
                    text="Processing data..." 
                    progress={progress} 
                  />
                  <Button 
                    variant="primary" 
                    size="sm" 
                    onClick={simulateProgress}
                    className="mt-2"
                  >
                    Start Progress
                  </Button>
                </div>

                <div className="mb-3">
                  <h6>Overlay Loader:</h6>
                  <div style={{ position: 'relative', height: '100px', border: '1px solid #dee2e6' }}>
                    <p className="p-3">Content behind overlay</p>
                    {showOverlay && <OverlayLoader text="Loading overlay..." />}
                  </div>
                  <Button 
                    variant="secondary" 
                    size="sm" 
                    onClick={() => setShowOverlay(!showOverlay)}
                    className="mt-2"
                  >
                    Toggle Overlay
                  </Button>
                </div>
              </Card.Body>
            </Card>
          </Col>

          <Col md={6}>
            <Card>
              <Card.Header>
                <h4>Toast Notifications Testing</h4>
              </Card.Header>
              <Card.Body>
                <div className="mb-3">
                  <h6>Basic Toast Types:</h6>
                  <Button 
                    variant="primary" 
                    size="sm" 
                    onClick={testToastTypes}
                    className="me-2"
                  >
                    Test All Types
                  </Button>
                  <Button 
                    variant="outline-secondary" 
                    size="sm" 
                    onClick={toast.clearAll}
                  >
                    Clear All
                  </Button>
                </div>

                <div className="mb-3">
                  <h6>Operation Toasts:</h6>
                  <Button 
                    variant="success" 
                    size="sm" 
                    onClick={testOperationToasts}
                    className="me-2"
                  >
                    Test Operations
                  </Button>
                </div>

                <div className="mb-3">
                  <h6>Individual Toast Types:</h6>
                  <div className="d-flex gap-2 flex-wrap">
                    <Button size="sm" variant="success" onClick={() => toast.showSuccess('Success!')}>
                      Success
                    </Button>
                    <Button size="sm" variant="danger" onClick={() => toast.showError('Error!')}>
                      Error
                    </Button>
                    <Button size="sm" variant="warning" onClick={() => toast.showWarning('Warning!')}>
                      Warning
                    </Button>
                    <Button size="sm" variant="info" onClick={() => toast.showInfo('Info!')}>
                      Info
                    </Button>
                  </div>
                </div>

                <div className="mb-3">
                  <h6>Network & Auth Errors:</h6>
                  <div className="d-flex gap-2">
                    <Button size="sm" variant="outline-danger" onClick={() => toast.showNetworkError()}>
                      Network Error
                    </Button>
                    <Button size="sm" variant="outline-warning" onClick={() => toast.showAuthError()}>
                      Auth Error
                    </Button>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Form Validation Testing */}
        <Row className="mb-4">
          <Col md={6}>
            <Card>
              <Card.Header>
                <h4>Form Validation Testing</h4>
              </Card.Header>
              <Card.Body>
                <FormErrorBoundary formName="Test Form">
                  <Form onSubmit={handleFormSubmit}>
                    <Form.Group className="mb-3">
                      <Form.Label>Name *</Form.Label>
                      <Form.Control
                        type="text"
                        value={formData.name}
                        onChange={(e) => {
                          setFormData(prev => ({ ...prev, name: e.target.value }));
                          if (formErrorHandler.getFieldError('name')) {
                            formErrorHandler.clearFieldError('name');
                          }
                        }}
                        isInvalid={!!formErrorHandler.getFieldError('name')}
                      />
                      <Form.Control.Feedback type="invalid">
                        {formErrorHandler.getFieldError('name')}
                      </Form.Control.Feedback>
                    </Form.Group>

                    <Form.Group className="mb-3">
                      <Form.Label>Email *</Form.Label>
                      <Form.Control
                        type="email"
                        value={formData.email}
                        onChange={(e) => {
                          setFormData(prev => ({ ...prev, email: e.target.value }));
                          if (formErrorHandler.getFieldError('email')) {
                            formErrorHandler.clearFieldError('email');
                          }
                        }}
                        isInvalid={!!formErrorHandler.getFieldError('email')}
                      />
                      <Form.Control.Feedback type="invalid">
                        {formErrorHandler.getFieldError('email')}
                      </Form.Control.Feedback>
                    </Form.Group>

                    {formErrorHandler.error && (
                      <ErrorMessage
                        error={formErrorHandler.error.originalError}
                        operation="FORM_VALIDATION"
                        onDismiss={formErrorHandler.clearError}
                        size="small"
                      />
                    )}

                    <Button type="submit" variant="primary">
                      Submit Form
                    </Button>
                  </Form>
                </FormErrorBoundary>
              </Card.Body>
            </Card>
          </Col>

          <Col md={6}>
            <Card>
              <Card.Header>
                <h4>Error Boundary Testing</h4>
              </Card.Header>
              <Card.Body>
                <div className="mb-3">
                  <h6>Component Error Boundary:</h6>
                  <p className="text-muted">
                    Click the button below to trigger a component error and test the error boundary.
                  </p>

                  <ErrorBoundary
                    name="Test Component Boundary"
                    onError={(error, errorInfo) => {
                      console.log('Error boundary caught:', error, errorInfo);
                    }}
                  >
                    {showErrorComponent ? (
                      <ComponentWithError />
                    ) : (
                      <Alert variant="info">
                        Component is working normally.
                      </Alert>
                    )}
                  </ErrorBoundary>

                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => setShowErrorComponent(!showErrorComponent)}
                    className="mt-2"
                  >
                    {showErrorComponent ? 'Fix Component' : 'Break Component'}
                  </Button>
                </div>

                <div className="mb-3">
                  <h6>Error Service Testing:</h6>
                  <div className="d-flex gap-2 flex-wrap">
                    <Button
                      size="sm"
                      variant="outline-primary"
                      onClick={() => {
                        errorService.logError(
                          new Error('Test error'),
                          'MANUAL_TEST',
                          { testData: 'example' },
                          'medium'
                        );
                        toast.showInfo('Error logged to service');
                      }}
                    >
                      Log Test Error
                    </Button>
                    <Button
                      size="sm"
                      variant="outline-secondary"
                      onClick={() => {
                        const stats = errorService.getErrorStats();
                        toast.showInfo(`Total errors: ${stats.total}, Last hour: ${stats.lastHour}`);
                      }}
                    >
                      Show Error Stats
                    </Button>
                    <Button
                      size="sm"
                      variant="outline-warning"
                      onClick={() => {
                        errorService.clearErrors();
                        toast.showSuccess('Error queue cleared');
                      }}
                    >
                      Clear Error Queue
                    </Button>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Error Statistics */}
        <Row className="mb-4">
          <Col>
            <Card>
              <Card.Header>
                <h4>Error Handling Summary</h4>
              </Card.Header>
              <Card.Body>
                <Alert variant="success">
                  <Alert.Heading>✅ Enhanced Error Handling Implementation Complete</Alert.Heading>
                  <p>The following components and features have been successfully implemented:</p>
                  <ul>
                    <li><strong>Error Message System:</strong> Comprehensive error mapping with user-friendly messages</li>
                    <li><strong>Loading States:</strong> Enhanced loading spinners with different sizes and contexts</li>
                    <li><strong>Toast Notifications:</strong> Complete notification system with queue management</li>
                    <li><strong>Error Boundaries:</strong> React error boundaries for graceful error handling</li>
                    <li><strong>Form Validation:</strong> Enhanced form validation with real-time feedback</li>
                    <li><strong>Error Service:</strong> Centralized error logging and reporting</li>
                    <li><strong>Custom Hooks:</strong> Reusable hooks for error handling and notifications</li>
                  </ul>
                  <hr />
                  <p className="mb-0">
                    All components are fully accessible, responsive, and follow modern UX patterns.
                    The implementation supports dark mode, high contrast, and reduced motion preferences.
                  </p>
                </Alert>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </PageErrorBoundary>
  );
};

export default ErrorHandlingTestPage;
