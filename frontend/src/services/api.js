import axios from 'axios';

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
    // You could add auth token here if using JWT
    // Only log non-GET requests or enable for debugging
    if (config.method.toUpperCase() !== 'GET') {
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
    // Log all responses for debugging
    console.log(`API Response [${response.config.method.toUpperCase()}] ${response.config.url}:`, response.data);

    // Special logging for system resources
    if (response.config.url === '/admin/system-resources') {
      console.log('System resources API response:', response.data);
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
