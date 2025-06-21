import axios from 'axios';

// Create an axios instance with default config
const api = axios.create({
  baseURL: '/api', // Use relative URL to work with Vite proxy
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false, // JWT doesn't need credentials
});

// Token management
const getAccessToken = () => {
  return localStorage.getItem('supplyline_access_token');
};

const getRefreshToken = () => {
  return localStorage.getItem('supplyline_refresh_token');
};

const setAccessToken = (token) => {
  localStorage.setItem('supplyline_access_token', token);
};

const clearTokens = () => {
  localStorage.removeItem('supplyline_access_token');
  localStorage.removeItem('supplyline_refresh_token');
  localStorage.removeItem('supplyline_user_data');
  localStorage.removeItem('supplyline_csrf_token');
};

// CSRF token management
const getCsrfToken = () => {
  return localStorage.getItem('supplyline_csrf_token');
};

const setCsrfToken = (token) => {
  localStorage.setItem('supplyline_csrf_token', token);
};

const fetchCsrfToken = async () => {
  try {
    const response = await api.get('/auth/csrf-token');
    const { csrf_token } = response.data;
    setCsrfToken(csrf_token);
    return csrf_token;
  } catch (error) {
    console.error('Failed to fetch CSRF token:', error);
    return null;
  }
};

// Request interceptor for adding JWT auth token and CSRF token
api.interceptors.request.use(
  async (config) => {
    // Add JWT token to Authorization header
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;

      // Add CSRF token for state-changing requests
      if (['post', 'put', 'delete', 'patch'].includes(config.method?.toLowerCase())) {
        let csrfToken = getCsrfToken();

        // Fetch CSRF token if not available (but only if we have an auth token)
        if (!csrfToken && !config.url.includes('/auth/login')) {
          try {
            csrfToken = await fetchCsrfToken();
          } catch (error) {
            console.warn('Failed to fetch CSRF token:', error);
          }
        }

        if (csrfToken) {
          config.headers['X-CSRF-Token'] = csrfToken;
        }
      }
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
    const originalRequest = error.config;

    // Handle common errors
    console.error(`API Error [${error.config?.method?.toUpperCase()}] ${error.config?.url}:`, error.response?.data || error.message);

    if (error.response) {
      // Server responded with error status
      if (error.response.status === 401 && !originalRequest._retry) {
        // Unauthorized - try to refresh token
        originalRequest._retry = true;

        const refreshToken = getRefreshToken();
        if (refreshToken) {
          try {
            // Attempt to refresh the access token
            const response = await axios.post('/api/auth/refresh', {
              refresh_token: refreshToken
            });

            const { access_token, refresh_token: newRefreshToken } = response.data;

            // Update stored tokens
            setAccessToken(access_token);
            if (newRefreshToken) {
              localStorage.setItem('supplyline_refresh_token', newRefreshToken);
            }

            // Retry the original request with new token
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return api(originalRequest);

          } catch (refreshError) {
            // Refresh failed, clear tokens and redirect to login
            console.error('Token refresh failed:', refreshError);
            clearTokens();

            // Only redirect if we're not already on the login page
            if (window.location.pathname !== '/login') {
              window.location.href = '/login';
            }
            return Promise.reject(refreshError);
          }
        } else {
          // No refresh token, redirect to login
          clearTokens();
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }
        }
      } else if (error.response.status === 401) {
        // Already tried refresh or refresh not applicable
        clearTokens();
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      } else if (error.response.status >= 500) {
        // Server error - don't redirect to login, just log the error
        console.error('Server error occurred:', error.response.data);
        // Let the error propagate to be handled by the component
      }
    }

    return Promise.reject(error);
  }
);

export default api;
