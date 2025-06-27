import axios from 'axios';
import TokenStorage from '../utils/tokenStorage';

// Create an axios instance with default config
const api = axios.create({
  baseURL: '/api', // Use relative URL to work with Vite proxy
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for cookies/session
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    // Add JWT Authorization header if token exists
    const authHeader = TokenStorage.getAuthHeader();
    if (authHeader) {
      config.headers.Authorization = authHeader;
    }

    // Only log non-GET requests in development environment or when debugging is enabled
    if (config.method.toUpperCase() !== 'GET' &&
        (process.env.NODE_ENV === 'development' || process.env.REACT_APP_DEBUG_MODE === 'true')) {
      console.log(`API Request [${config.method.toUpperCase()}] ${config.url}:`, config.data);
      if (authHeader) {
        console.log('Authorization header included');
      }
    }
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors and token refresh
api.interceptors.response.use(
  (response) => {
    // Only log responses in development environment or when debugging is enabled
    if (process.env.NODE_ENV === 'development' || process.env.REACT_APP_DEBUG_MODE === 'true') {
      console.log(`API Response [${response.config.method.toUpperCase()}] ${response.config.url}:`, response.data);
    }

    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Handle common errors
    console.error(`API Error [${error.config?.method?.toUpperCase()}] ${error.config?.url}:`, error.response?.data || error.message);

    if (error.response) {
      // Server responded with error status
      if (error.response.status === 401 && !originalRequest._retry) {
        // Unauthorized - try to refresh token first
        originalRequest._retry = true;

        try {
          // Check if we have a refresh token and need to refresh
          if (TokenStorage.needsTokenRefresh()) {
            console.log('Attempting token refresh...');

            // Import AuthService dynamically to avoid circular dependency
            const { default: AuthService } = await import('./authService');
            await AuthService.refreshTokens();

            // Retry the original request with new token
            const authHeader = TokenStorage.getAuthHeader();
            if (authHeader) {
              originalRequest.headers.Authorization = authHeader;
              return api(originalRequest);
            } else {
              // No auth header after refresh - tokens are invalid
              throw new Error('No valid tokens after refresh');
            }
          } else {
            // No refresh token available
            throw new Error('No refresh token available');
          }
        } catch (refreshError) {
          console.error('Token refresh failed:', refreshError);
          // Clear invalid tokens and redirect to login
          TokenStorage.clearTokens();

          // Prevent infinite redirects by checking current location
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }
          return Promise.reject(refreshError);
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
