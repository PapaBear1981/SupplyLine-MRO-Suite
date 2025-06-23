import axios from 'axios';
import errorService from './errorService';
import { determineErrorType, createStandardError, ERROR_TYPES } from '../utils/errorMapping';

// Create an axios instance with default config
const api = axios.create({
  baseURL: '/api', // Use relative URL to work with Vite proxy
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for cookies/session
  timeout: 30000, // 30 second timeout
});

// Request interceptor for adding auth token and logging
api.interceptors.request.use(
  (config) => {
    // Add request timestamp for performance tracking
    config.metadata = { startTime: Date.now() };

    // Add JWT token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Only log non-GET requests in development environment or when debugging is enabled
    if (config.method.toUpperCase() !== 'GET' &&
        (process.env.NODE_ENV === 'development' || process.env.REACT_APP_DEBUG_MODE === 'true')) {
      errorService.logInfo(
        `API Request [${config.method.toUpperCase()}] ${config.url}`,
        'API_REQUEST',
        { data: config.data, headers: config.headers }
      );
    }

    return config;
  },
  (error) => {
    errorService.logError(error, 'API_REQUEST_SETUP', {}, 'medium');
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors and logging
api.interceptors.response.use(
  (response) => {
    // Calculate request duration
    const duration = Date.now() - response.config.metadata?.startTime;

    // Only log responses in development environment or when debugging is enabled
    if (process.env.NODE_ENV === 'development' || process.env.REACT_APP_DEBUG_MODE === 'true') {
      errorService.logInfo(
        `API Response [${response.config.method.toUpperCase()}] ${response.config.url} (${duration}ms)`,
        'API_RESPONSE',
        {
          status: response.status,
          data: response.data,
          duration
        }
      );
    }

    return response;
  },
  (error) => {
    // Calculate request duration if available
    const duration = error.config?.metadata?.startTime
      ? Date.now() - error.config.metadata.startTime
      : null;

    // Create enhanced error object with API context
    const enhancedError = {
      ...error,
      apiContext: {
        method: error.config?.method?.toUpperCase(),
        url: error.config?.url,
        status: error.response?.status,
        statusText: error.response?.statusText,
        duration,
        requestData: error.config?.data,
        responseData: error.response?.data
      }
    };

    // Determine error type and severity
    const errorType = determineErrorType(error);
    let severity = 'medium';

    if (error.response?.status >= 500) {
      severity = 'high';
    } else if (error.response?.status === 401 || error.response?.status === 403) {
      severity = 'high';
    } else if (error.code === 'ECONNABORTED') {
      severity = 'medium';
    }

    // Log the error with enhanced context
    errorService.logError(
      enhancedError,
      'API_ERROR',
      {
        endpoint: error.config?.url,
        method: error.config?.method,
        status: error.response?.status,
        duration,
        errorType
      },
      severity
    );

    // Handle specific error types
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // Unauthorized - handle token refresh or redirect to login
          handleUnauthorizedError(error);
          break;
        case 403:
          // Forbidden - user doesn't have permission
          errorService.logWarning(
            'User attempted unauthorized action',
            'PERMISSION_DENIED',
            { url: error.config?.url, method: error.config?.method }
          );
          break;
        case 429:
          // Rate limited - could implement retry with backoff
          errorService.logWarning(
            'Rate limit exceeded',
            'RATE_LIMIT',
            { url: error.config?.url }
          );
          break;
        case 500:
        case 502:
        case 503:
        case 504:
          // Server errors - could implement retry logic
          errorService.logError(
            error,
            'SERVER_ERROR',
            { status: error.response.status },
            'high'
          );
          break;
      }
    } else if (error.code === 'ECONNABORTED') {
      // Timeout error
      errorService.logError(
        error,
        'REQUEST_TIMEOUT',
        { timeout: error.config?.timeout },
        'medium'
      );
    } else if (error.message === 'Network Error') {
      // Network connectivity issues
      errorService.logError(
        error,
        'NETWORK_ERROR',
        {},
        'high'
      );
    }

    return Promise.reject(enhancedError);
  }
);

// Handle unauthorized errors with token refresh logic
const handleUnauthorizedError = async (error) => {
  const refreshToken = localStorage.getItem('refreshToken');

  if (refreshToken && !error.config._retry) {
    error.config._retry = true;

    try {
      // Attempt to refresh the token
      const response = await axios.post('/api/auth/refresh', {
        refresh_token: refreshToken
      });

      const newToken = response.data.access_token;
      localStorage.setItem('authToken', newToken);

      // Retry the original request with new token
      error.config.headers.Authorization = `Bearer ${newToken}`;
      return api.request(error.config);
    } catch (refreshError) {
      // Refresh failed, redirect to login
      localStorage.removeItem('authToken');
      localStorage.removeItem('refreshToken');

      errorService.logWarning(
        'Token refresh failed, redirecting to login',
        'AUTH_TOKEN_REFRESH_FAILED'
      );

      // Delay redirect to allow error message to be shown
      setTimeout(() => {
        window.location.href = '/login';
      }, 1000);
    }
  } else {
    // No refresh token or retry already attempted
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');

    setTimeout(() => {
      window.location.href = '/login';
    }, 1000);
  }
};

export default api;
