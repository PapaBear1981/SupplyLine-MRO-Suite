import api from './api';

const AuthService = {
  // Login user
  login: async (username, password) => {
    try {
      const response = await api.post('/auth/login', {
        employee_number: username,
        password
      });

      // Store JWT token in localStorage
      if (response.data.token) {
        localStorage.setItem('authToken', response.data.token);
      }

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
      // Clear JWT token from localStorage
      localStorage.removeItem('authToken');
      return response.data;
    } catch (error) {
      // Clear token even if logout request fails
      localStorage.removeItem('authToken');
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
