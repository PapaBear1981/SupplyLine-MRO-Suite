import api from './api';

const AuthService = {
  // Login user
  login: async (username, password) => {
    try {
      const response = await api.post('/auth/login', {
        employee_number: username,
        password
      });
      return response.data;
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

  // Get session information including timeout settings
  getSessionInfo: async () => {
    try {
      const response = await api.get('/auth/session-info');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get system settings
  getSystemSettings: async (category = null) => {
    try {
      const url = category ? `/admin/settings?category=${category}` : '/admin/settings';
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update system settings
  updateSystemSettings: async (settings) => {
    try {
      const response = await api.post('/admin/settings', settings);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Check if user is authenticated
  isAuthenticated: async () => {
    try {
      const response = await api.get('/auth/status');
      return response.data.authenticated;
    } catch (error) {
      return false;
    }
  }
};

export default AuthService;
