import axios from 'axios';

// Get API URL from environment variable or use default for development
const getApiBaseUrl = () => {
  // In production builds, VITE_API_URL is injected at build time
  const apiUrl = import.meta.env.VITE_API_URL || process.env.VITE_API_URL;

  if (apiUrl) {
    // Use the configured API URL (for production/Cloud Run deployment)
    return `${apiUrl}/api`;
  } else {
    // Use relative URL for development (works with Vite proxy)
    return '/api';
  }
};

// Log the API base URL for debugging (only in development or when debug mode is enabled)
const apiBaseUrl = getApiBaseUrl();
if (import.meta.env.DEV || import.meta.env.VITE_DEBUG_MODE === 'true') {
  console.log('API Base URL:', apiBaseUrl);
  console.log('VITE_API_URL:', import.meta.env.VITE_API_URL);
}

// Create an axios instance with default config
const api = axios.create({
  baseURL: apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for cookies/session
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    // Add JWT token to Authorization header
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Only log non-GET requests in development environment or when debugging is enabled
    if (config.method.toUpperCase() !== 'GET' &&
        (process.env.NODE_ENV === 'development' || process.env.REACT_APP_DEBUG_MODE === 'true')) {
      console.log(`API Request [${config.method.toUpperCase()}] ${config.url}:`, config.data);
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
    // Handle common errors
    console.error(`API Error [${error.config?.method?.toUpperCase()}] ${error.config?.url}:`, error.response?.data || error.message);

    const originalRequest = error.config;

    if (error.response) {
      // Server responded with error status
      if (error.response.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        // Check if this is a token expiration error
        const errorMessage = error.response.data?.reason || error.response.data?.error || '';
        if (errorMessage.includes('Token expired') || errorMessage.includes('expired')) {
          try {
            // Try to refresh the token
            const response = await api.post('/auth/refresh');

            if (response.data.token) {
              // Update the token in localStorage
              localStorage.setItem('authToken', response.data.token);

              // Update the Authorization header for the original request
              originalRequest.headers.Authorization = `Bearer ${response.data.token}`;

              // Retry the original request
              return api(originalRequest);
            }
          } catch (refreshError) {
            console.error('Token refresh failed:', refreshError);
            // Refresh failed, clear token and redirect to login
            localStorage.removeItem('authToken');

            if (window.location.pathname !== '/login') {
              setTimeout(() => {
                window.location.href = '/login';
              }, 100);
            }
            return Promise.reject(refreshError);
          }
        } else {
          // Not a token expiration error, clear token and redirect
          localStorage.removeItem('authToken');

          if (window.location.pathname !== '/login') {
            setTimeout(() => {
              window.location.href = '/login';
            }, 100);
          }
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
