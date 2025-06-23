import api from './api';

const decodeToken = (token) => {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => `%${('00' + c.charCodeAt(0).toString(16)).slice(-2)}`)
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
};

const AuthService = {
  // Login user
  login: async (username, password) => {
    try {
      const response = await api.post('/auth/login', {
        employee_number: username,
        password,
      });

      const { access_token, refresh_token, user } = response.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('user', JSON.stringify(user));
      return user;
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

  // Refresh JWT tokens using refresh token from storage
  refreshToken: async () => {
    const refresh_token = localStorage.getItem('refresh_token');
    if (!refresh_token) {
      throw new Error('No refresh token');
    }
    const response = await api.post('/auth/refresh', { refresh_token });
    const { access_token, refresh_token: newRefresh } = response.data;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', newRefresh);
    return response.data;
  },

  // Logout user
  logout: async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      // Ignore logout errors
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  },

  // Get current user info from API or localStorage
  getCurrentUser: async () => {
    const stored = localStorage.getItem('user');
    if (stored) {
      return JSON.parse(stored);
    }
    try {
      const response = await api.get('/auth/me');
      const user = response.data.user || response.data;
      localStorage.setItem('user', JSON.stringify(user));
      return user;
    } catch (error) {
      throw error;
    }
  },

  // Check if user is authenticated by decoding token
  isAuthenticated: () => {
    const token = localStorage.getItem('access_token');
    if (!token) return false;
    const payload = decodeToken(token);
    return payload ? payload.exp * 1000 > Date.now() : false;
  }
};

export default AuthService;
