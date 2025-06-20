import api from './api';

/**
 * JWT Token Management
 */
const TokenManager = {
  // Token storage keys
  ACCESS_TOKEN_KEY: 'supplyline_access_token',
  REFRESH_TOKEN_KEY: 'supplyline_refresh_token',
  USER_DATA_KEY: 'supplyline_user_data',

  // Get access token from localStorage
  getAccessToken: () => {
    return localStorage.getItem(TokenManager.ACCESS_TOKEN_KEY);
  },

  // Get refresh token from localStorage
  getRefreshToken: () => {
    return localStorage.getItem(TokenManager.REFRESH_TOKEN_KEY);
  },

  // Get stored user data
  getUserData: () => {
    const userData = localStorage.getItem(TokenManager.USER_DATA_KEY);
    return userData ? JSON.parse(userData) : null;
  },

  // Store tokens and user data
  setTokens: (accessToken, refreshToken, userData) => {
    localStorage.setItem(TokenManager.ACCESS_TOKEN_KEY, accessToken);
    localStorage.setItem(TokenManager.REFRESH_TOKEN_KEY, refreshToken);
    if (userData) {
      localStorage.setItem(TokenManager.USER_DATA_KEY, JSON.stringify(userData));
    }
  },

  // Clear all stored tokens and data
  clearTokens: () => {
    localStorage.removeItem(TokenManager.ACCESS_TOKEN_KEY);
    localStorage.removeItem(TokenManager.REFRESH_TOKEN_KEY);
    localStorage.removeItem(TokenManager.USER_DATA_KEY);
  },

  // Check if access token exists and is not expired
  isTokenValid: () => {
    const token = TokenManager.getAccessToken();
    if (!token) return false;

    try {
      // Decode JWT payload (without verification - just to check expiry)
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Math.floor(Date.now() / 1000);

      // Check if token is expired (with 30 second buffer)
      return payload.exp > (currentTime + 30);
    } catch (error) {
      console.error('Error checking token validity:', error);
      return false;
    }
  },

  // Refresh access token using refresh token
  refreshAccessToken: async () => {
    const refreshToken = TokenManager.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await api.post('/auth/refresh', {
        refresh_token: refreshToken
      });

      const { access_token, refresh_token: newRefreshToken } = response.data;

      // Update stored tokens
      localStorage.setItem(TokenManager.ACCESS_TOKEN_KEY, access_token);
      if (newRefreshToken) {
        localStorage.setItem(TokenManager.REFRESH_TOKEN_KEY, newRefreshToken);
      }

      return access_token;
    } catch (error) {
      // Refresh failed, clear all tokens
      TokenManager.clearTokens();
      throw error;
    }
  }
};

/**
 * Authentication Service with JWT support
 */
const AuthService = {
  // Login user with JWT
  login: async (username, password, rememberMe = false) => {
    try {
      const response = await api.post('/auth/login', {
        employee_number: username,
        password,
        remember_me: rememberMe
      });

      const { access_token, refresh_token, user } = response.data;

      // Store tokens and user data
      TokenManager.setTokens(access_token, refresh_token, user);

      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Logout user
  logout: async () => {
    try {
      // Call logout endpoint to invalidate tokens on server
      await api.post('/auth/logout');
    } catch (error) {
      // Even if server logout fails, clear local tokens
      console.error('Server logout failed:', error);
    } finally {
      // Always clear local tokens
      TokenManager.clearTokens();
    }
  },

  // Get current user info
  getCurrentUser: async () => {
    try {
      const response = await api.get('/auth/me');

      // Update stored user data
      if (response.data.user) {
        TokenManager.setTokens(
          TokenManager.getAccessToken(),
          TokenManager.getRefreshToken(),
          response.data.user
        );
      }

      return response.data.user;
    } catch (error) {
      throw error;
    }
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    // Check if we have valid tokens
    const hasValidToken = TokenManager.isTokenValid();
    const hasRefreshToken = !!TokenManager.getRefreshToken();

    return hasValidToken || hasRefreshToken;
  },

  // Get authentication status from server
  checkAuthStatus: async () => {
    try {
      const response = await api.get('/auth/status');
      return response.data;
    } catch (error) {
      return { authenticated: false };
    }
  },

  // Get stored user data (synchronous)
  getStoredUser: () => {
    return TokenManager.getUserData();
  },

  // Refresh tokens
  refreshToken: async () => {
    return await TokenManager.refreshAccessToken();
  },

  // Change password
  changePassword: async (currentPassword, newPassword) => {
    try {
      const response = await api.put('/user/password', {
        current_password: currentPassword,
        new_password: newPassword
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update user profile
  updateProfile: async (profileData) => {
    try {
      const response = await api.put('/user/profile', profileData);

      // Update stored user data
      if (response.data) {
        TokenManager.setTokens(
          TokenManager.getAccessToken(),
          TokenManager.getRefreshToken(),
          response.data
        );
      }

      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

// Export both AuthService and TokenManager
export { TokenManager };
export default AuthService;
