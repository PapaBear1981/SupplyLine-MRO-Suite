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
    // You could add auth token here if using JWT
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

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => {
    // Only log responses in development environment or when debugging is enabled
    if (process.env.NODE_ENV === 'development' || process.env.REACT_APP_DEBUG_MODE === 'true') {
      console.log(`API Response [${response.config.method.toUpperCase()}] ${response.config.url}:`, response.data);
    }

    return response;
  },
  (error) => {
    // Handle common errors
    console.error(`API Error [${error.config?.method?.toUpperCase()}] ${error.config?.url}:`, error.response?.data || error.message);

    if (error.response) {
      // Server responded with error status
      if (error.response.status === 401) {
        // Unauthorized - redirect to login
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
