/**
 * Enhanced LoadingSpinner Component
 *
 * Reusable loading spinner with different sizes, messages, and styles
 * for various operations throughout the application
 */

import React from 'react';
import { Spinner, ProgressBar } from 'react-bootstrap';
import './LoadingSpinner.css';

// Loading states for different operations
export const LOADING_STATES = {
  CREATING_TOOL: "Creating tool...",
  SAVING_CHEMICAL: "Saving chemical...",
  GENERATING_REPORT: "Generating report...",
  LOADING_DATA: "Loading data...",
  AUTHENTICATING: "Signing in...",
  UPLOADING_FILE: "Uploading file...",
  PROCESSING: "Processing...",
  SAVING: "Saving...",
  DELETING: "Deleting...",
  UPDATING: "Updating...",
  SEARCHING: "Searching...",
  VALIDATING: "Validating...",
  CONNECTING: "Connecting...",
  SYNCING: "Syncing data...",
  EXPORTING: "Exporting...",
  IMPORTING: "Importing...",
  CALCULATING: "Calculating...",
  ANALYZING: "Analyzing..."
};

const LoadingSpinner = ({
  size = 'md',
  text = 'Loading...',
  variant = 'primary',
  animation = 'border',
  inline = false,
  overlay = false,
  progress = null,
  showProgress = false,
  className = '',
  style = {},
  centered = true,
  fullScreen = false,
  minimal = false
}) => {
  // Size mapping for consistent sizing
  const sizeMap = {
    xs: 'sm',
    sm: 'sm',
    md: '',
    lg: 'lg',
    xl: 'xl'
  };

  const spinnerSize = sizeMap[size] || '';

  // Base container classes
  let containerClasses = ['loading-spinner-container'];

  if (inline) {
    containerClasses.push('loading-inline');
  } else if (fullScreen) {
    containerClasses.push('loading-fullscreen');
  } else if (centered) {
    containerClasses.push('loading-centered');
  }

  if (overlay) {
    containerClasses.push('loading-overlay');
  }

  if (minimal) {
    containerClasses.push('loading-minimal');
  }

  if (className) {
    containerClasses.push(className);
  }

  const containerStyle = {
    ...style
  };

  const spinnerContent = (
    <>
      <Spinner
        animation={animation}
        role="status"
        variant={variant}
        size={spinnerSize}
        className={`loading-spinner loading-spinner-${size}`}
      >
        <span className="visually-hidden">Loading...</span>
      </Spinner>

      {text && !minimal && (
        <div className={`loading-text loading-text-${size}`}>
          {text}
        </div>
      )}

      {showProgress && progress !== null && (
        <div className="loading-progress">
          <ProgressBar
            now={progress}
            variant={variant}
            className="loading-progress-bar"
            label={`${Math.round(progress)}%`}
          />
        </div>
      )}
    </>
  );

  return (
    <div
      className={containerClasses.join(' ')}
      style={containerStyle}
      role="status"
      aria-live="polite"
      aria-label={text}
    >
      {overlay && <div className="loading-backdrop" />}
      <div className="loading-content">
        {spinnerContent}
      </div>
    </div>
  );
};

// Specialized loading components for common use cases
export const InlineLoader = ({ text = 'Loading...', size = 'sm' }) => (
  <LoadingSpinner
    text={text}
    size={size}
    inline={true}
    minimal={true}
  />
);

export const OverlayLoader = ({ text = 'Loading...', size = 'lg' }) => (
  <LoadingSpinner
    text={text}
    size={size}
    overlay={true}
    fullScreen={false}
  />
);

export const FullScreenLoader = ({ text = 'Loading application...', size = 'xl' }) => (
  <LoadingSpinner
    text={text}
    size={size}
    fullScreen={true}
    overlay={true}
  />
);

export const ButtonLoader = ({ text = '', size = 'sm' }) => (
  <LoadingSpinner
    text={text}
    size={size}
    inline={true}
    minimal={true}
    animation="border"
  />
);

export const ProgressLoader = ({ text = 'Processing...', progress = 0, size = 'md' }) => (
  <LoadingSpinner
    text={text}
    size={size}
    progress={progress}
    showProgress={true}
  />
);

// Operation-specific loaders
export const ToolCreationLoader = () => (
  <LoadingSpinner text={LOADING_STATES.CREATING_TOOL} size="md" />
);

export const ChemicalSaveLoader = () => (
  <LoadingSpinner text={LOADING_STATES.SAVING_CHEMICAL} size="md" />
);

export const ReportGenerationLoader = () => (
  <LoadingSpinner text={LOADING_STATES.GENERATING_REPORT} size="lg" />
);

export const DataLoadingLoader = () => (
  <LoadingSpinner text={LOADING_STATES.LOADING_DATA} size="md" />
);

export const AuthenticationLoader = () => (
  <LoadingSpinner text={LOADING_STATES.AUTHENTICATING} size="lg" />
);

export default LoadingSpinner;
