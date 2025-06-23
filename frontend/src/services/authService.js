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

      const { access_token, refresh_token, user } = response.data;
      localStorage.setItem(TOKEN_KEY, access_token);
      localStorage.setItem(REFRESH_KEY, refresh_token);

      return { user, access_token, refresh_token };
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
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(REFRESH_KEY);
    }
  },

  // Refresh access token using refresh token
  refreshToken: async () => {
    try {
      const refresh_token = localStorage.getItem(REFRESH_KEY);
      if (!refresh_token) {
        throw new Error('No refresh token available');
      }
      const response = await api.post('/auth/refresh', { refresh_token });
      const { access_token, refresh_token: new_refresh } = response.data;
      localStorage.setItem(TOKEN_KEY, access_token);
      localStorage.setItem(REFRESH_KEY, new_refresh);
      return { access_token, refresh_token: new_refresh };
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
