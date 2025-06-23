import axios from 'axios';

// Create an axios instance with default config
const api = axios.create({
  baseURL: '/api', // Use relative URL to work with Vite proxy
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token and CSRF token
api.interceptors.request.use(
  (config) => {
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }

    // Attach CSRF token for state-changing requests
    const method = config.method ? config.method.toUpperCase() : 'GET';
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
      const csrfToken = localStorage.getItem('csrf_token');
      if (csrfToken) {
        config.headers['X-CSRF-Token'] = csrfToken;
      }
    }

    // Only log non-GET requests in development environment or when debugging is enabled
    if (
      method !== 'GET' &&
      (process.env.NODE_ENV === 'development' || process.env.REACT_APP_DEBUG_MODE === 'true')
    ) {
      console.log(`API Request [${method}] ${config.url}:`, config.data);
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
    if (
      process.env.NODE_ENV === 'development' ||
      process.env.REACT_APP_DEBUG_MODE === 'true'
    ) {
      console.log(
        `API Response [${response.config.method.toUpperCase()}] ${response.config.url}:`,
        response.data
      );
    }

    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Handle common errors
    console.error(
      `API Error [${originalRequest?.method?.toUpperCase()}] ${originalRequest?.url}:`,
      error.response?.data || error.message
    );

    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const refreshResponse = await api.post('/auth/refresh', { refresh_token: refreshToken });
          const { access_token, refresh_token } = refreshResponse.data;
          if (access_token) {
            localStorage.setItem('access_token', access_token);
          }
          if (refresh_token) {
            localStorage.setItem('refresh_token', refresh_token);
          }

          // Get new CSRF token
          try {
            const csrfRes = await api.get('/auth/csrf-token');
            if (csrfRes.data?.csrf_token) {
              localStorage.setItem('csrf_token', csrfRes.data.csrf_token);
            }
          } catch (_) {
            // ignore CSRF fetch errors
          }

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(originalRequest.method.toUpperCase())) {
            const csrfToken = localStorage.getItem('csrf_token');
            if (csrfToken) {
              originalRequest.headers['X-CSRF-Token'] = csrfToken;
            }
          }

          return api(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('csrf_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
