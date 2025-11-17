import api from './api';

const UserService = {
  // Get all users
  getAllUsers: async () => {
    try {
      const response = await api.get('/users');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get user by ID
  getUserById: async (id) => {
    try {
      const response = await api.get(`/users/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Create new user
  createUser: async (userData) => {
    try {
      const response = await api.post('/users', userData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update user
  updateUser: async (id, userData) => {
    try {
      const response = await api.put(`/users/${id}`, userData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Deactivate user (soft delete)
  deactivateUser: async (id) => {
    try {
      const response = await api.delete(`/users/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update user profile
  updateProfile: async (profileData) => {
    try {
      const response = await api.put('/user/profile', profileData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Upload user avatar
  uploadAvatar: async (formData) => {
    try {
      // Don't set Content-Type header manually - axios will automatically
      // set it with the correct boundary when it detects FormData
      const response = await api.post('/user/avatar', formData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Change user password
  changePassword: async (passwordData) => {
    try {
      const response = await api.put('/user/password', passwordData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get user activity logs
  getUserActivity: async () => {
    try {
      const response = await api.get('/user/activity');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Search users by employee number
  searchUsersByEmployeeNumber: async (query) => {
    try {
      const response = await api.get(`/users?q=${query}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Unlock a locked user account
  unlockUserAccount: async (id) => {
    try {
      const response = await api.post(`/users/${id}/unlock`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default UserService;
