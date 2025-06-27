import api from './api';
import TokenStorage from '../utils/tokenStorage';

const AuthService = {
  // Login user
  login: async (username, password) => {
    try {
      const response = await api.post('/auth/login', {
        employee_number: username,
        password
      });

      // Store JWT tokens after successful login
      const loginData = response.data;
      if (loginData.access_token && loginData.refresh_token) {
        TokenStorage.storeTokens(loginData);
        console.log('Login successful, tokens stored');
      } else {
        console.warn('Login response missing JWT tokens:', loginData);
      }

      return loginData;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  },

  // Register new user
  register: async (userData) => {
    try {
      const response = await api.post('/auth/register', userData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Logout user
  logout: async () => {
    try {
      // Call backend logout endpoint
      const response = await api.post('/auth/logout');

      // Clear stored tokens regardless of backend response
      TokenStorage.clearTokens();
      console.log('Logout successful, tokens cleared');

      return response.data;
    } catch (error) {
      // Clear tokens even if backend call fails
      TokenStorage.clearTokens();
      console.log('Logout completed, tokens cleared (backend call failed)');
      throw error;
    }
  },

  // Get current user info
  getCurrentUser: async () => {
    try {
      const response = await api.get('/auth/user');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    // Check local token storage first (faster)
    return TokenStorage.isAuthenticated();
  },

  // Refresh JWT tokens (with safeguard against multiple simultaneous calls)
  refreshTokens: (() => {
    let refreshPromise = null;

    return async () => {
      // If a refresh is already in progress, return the existing promise
      if (refreshPromise) {
        console.log('Token refresh already in progress, waiting...');
        return refreshPromise;
      }

      try {
        refreshPromise = (async () => {
          const refreshToken = TokenStorage.getRefreshToken();
          if (!refreshToken) {
            throw new Error('No refresh token available');
          }

          console.log('Starting token refresh...');
          const response = await api.post('/auth/refresh', {
            refresh_token: refreshToken
          });

          // Update stored tokens
          const refreshData = response.data;
          if (refreshData.access_token) {
            TokenStorage.updateTokens(refreshData);
            console.log('Tokens refreshed successfully');
            return refreshData;
          } else {
            throw new Error('Invalid refresh response');
          }
        })();

        const result = await refreshPromise;
        return result;
      } catch (error) {
        console.error('Token refresh failed:', error);
        // Clear invalid tokens
        TokenStorage.clearTokens();
        throw error;
      } finally {
        // Clear the promise so future calls can try again
        refreshPromise = null;
      }
    };
  })(),

  // Get current user from stored data or fetch from server
  getCurrentUserFromStorage: () => {
    return TokenStorage.getUserData();
  },

  // Check if tokens need refresh
  needsTokenRefresh: () => {
    return TokenStorage.needsTokenRefresh();
  }
};

export default AuthService;
