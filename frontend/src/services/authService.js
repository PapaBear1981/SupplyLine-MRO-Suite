import api from './api';

const TOKEN_KEY = 'access_token';
const REFRESH_KEY = 'refresh_token';

const AuthService = {
  // Login user and store tokens
  login: async (username, password) => {
    try {
      const response = await api.post('/auth/login', {
        employee_number: username,
        password,
      });

      // Check if password change is required
      if (response.data.code === 'PASSWORD_CHANGE_REQUIRED') {
        // Return special response indicating password change is needed
        return {
          passwordChangeRequired: true,
          employeeNumber: response.data.employee_number,
          userId: response.data.user_id,
          password: password, // Temporary password needed for the change
        };
      }

      const { user } = response.data;
      // Tokens are now stored in HttpOnly cookies by the backend

      return { user };
    } catch (error) {
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
      const response = await api.post('/auth/logout');
      return response.data;
    } catch (error) {
      throw error;
    } finally {
      // Tokens are now cleared via HttpOnly cookies by the backend
    }
  },

  // Refresh access token using refresh token
  refreshToken: async () => {
    try {
      // Refresh tokens are now handled via HttpOnly cookies by the backend
      const response = await api.post('/auth/refresh');
      // Backend sets new cookies automatically
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get current user info
  getCurrentUser: async () => {
    try {
      const response = await api.get('/auth/me');
      return response.data.user;
    } catch (error) {
      throw error;
    }
  },
};

export default AuthService;
