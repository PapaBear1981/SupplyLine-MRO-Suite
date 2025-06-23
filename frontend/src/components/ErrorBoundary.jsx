/**
 * ErrorBoundary Component
 * 
 * React Error Boundary to catch and handle component errors gracefully
 */

import React from 'react';
import { Alert, Button, Card, Container } from 'react-bootstrap';
import errorService from '../services/errorService';
import { ERROR_TYPES } from '../utils/errorMapping';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error
    const errorId = errorService.logError(
      error,
      'REACT_ERROR_BOUNDARY',
      {
        componentStack: errorInfo.componentStack,
        errorBoundary: this.props.name || 'Unknown',
        props: this.props.logProps ? this.props : undefined
      },
      'high'
    );

    this.setState({
      error,
      errorInfo,
      errorId: errorId.id
    });

    // Call optional error callback
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null
    });

    // Call optional retry callback
    if (this.props.onRetry) {
      this.props.onRetry();
    }
  };

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.handleRetry);
      }

      // Default fallback UI
      return (
        <Container className="my-4">
          <Card className="border-danger">
            <Card.Header className="bg-danger text-white">
              <div className="d-flex align-items-center">
                <span className="me-2" role="img" aria-label="Error">💥</span>
                <h5 className="mb-0">Something went wrong</h5>
              </div>
            </Card.Header>
            <Card.Body>
              <Alert variant="danger" className="mb-3">
                <Alert.Heading>Component Error</Alert.Heading>
                <p>
                  A component error occurred while rendering this part of the application. 
                  This error has been logged and our team has been notified.
                </p>
                {this.state.errorId && (
                  <p className="mb-0">
                    <small className="text-muted">Error ID: {this.state.errorId}</small>
                  </p>
                )}
              </Alert>

              <div className="d-flex gap-2 flex-wrap">
                <Button 
                  variant="primary" 
                  onClick={this.handleRetry}
                  size="sm"
                >
                  Try Again
                </Button>
                <Button 
                  variant="outline-secondary" 
                  onClick={this.handleReload}
                  size="sm"
                >
                  Reload Page
                </Button>
                {this.props.onGoBack && (
                  <Button 
                    variant="outline-secondary" 
                    onClick={this.props.onGoBack}
                    size="sm"
                  >
                    Go Back
                  </Button>
                )}
              </div>

              {(process.env.NODE_ENV === 'development' || this.props.showDetails) && (
                <Card className="mt-3">
                  <Card.Header>
                    <small className="text-muted">Technical Details (Development)</small>
                  </Card.Header>
                  <Card.Body>
                    <div className="mb-3">
                      <strong>Error:</strong>
                      <pre className="mt-1 p-2 bg-light border rounded">
                        {this.state.error && this.state.error.toString()}
                      </pre>
                    </div>
                    {this.state.errorInfo && (
                      <div>
                        <strong>Component Stack:</strong>
                        <pre className="mt-1 p-2 bg-light border rounded" style={{ fontSize: '0.8rem' }}>
                          {this.state.errorInfo.componentStack}
                        </pre>
                      </div>
                    )}
                  </Card.Body>
                </Card>
              )}
            </Card.Body>
          </Card>
        </Container>
      );
    }

    return this.props.children;
  }
}

// Higher-order component for wrapping components with error boundary
export const withErrorBoundary = (Component, errorBoundaryProps = {}) => {
  const WrappedComponent = (props) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </ErrorBoundary>
  );

  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;
  return WrappedComponent;
};

// Specialized error boundaries for different contexts
export const PageErrorBoundary = ({ children, pageName }) => (
  <ErrorBoundary
    name={`Page: ${pageName}`}
    fallback={(error, retry) => (
      <Container className="my-5 text-center">
        <div className="mb-4">
          <span role="img" aria-label="Error" style={{ fontSize: '4rem' }}>💥</span>
        </div>
        <h2>Page Error</h2>
        <p className="text-muted mb-4">
          There was an error loading this page. Please try again.
        </p>
        <div className="d-flex gap-2 justify-content-center">
          <Button variant="primary" onClick={retry}>
            Try Again
          </Button>
          <Button variant="outline-secondary" onClick={() => window.location.href = '/'}>
            Go Home
          </Button>
        </div>
      </Container>
    )}
  >
    {children}
  </ErrorBoundary>
);

export const FormErrorBoundary = ({ children, formName }) => (
  <ErrorBoundary
    name={`Form: ${formName}`}
    fallback={(error, retry) => (
      <Alert variant="danger">
        <Alert.Heading>Form Error</Alert.Heading>
        <p>There was an error with the form. Please try again.</p>
        <Button variant="outline-danger" size="sm" onClick={retry}>
          Reset Form
        </Button>
      </Alert>
    )}
  >
    {children}
  </ErrorBoundary>
);

export const ComponentErrorBoundary = ({ children, componentName }) => (
  <ErrorBoundary
    name={`Component: ${componentName}`}
    fallback={(error, retry) => (
      <Alert variant="warning" className="text-center">
        <div className="mb-2">
          <span role="img" aria-label="Warning">⚠️</span>
        </div>
        <p className="mb-2">This component failed to load.</p>
        <Button variant="outline-warning" size="sm" onClick={retry}>
          Retry
        </Button>
      </Alert>
    )}
  >
    {children}
  </ErrorBoundary>
);

export default ErrorBoundary;
