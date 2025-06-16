import api from './api';

const SystemSettingsService = {
  // Get all system settings
  getSettings: async () => {
    try {
      const response = await api.get('/admin/settings');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get settings by category
  getSettingsByCategory: async (category) => {
    try {
      const response = await api.get(`/admin/settings?category=${category}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get a specific setting
  getSetting: async (key) => {
    try {
      const response = await api.get(`/admin/settings/${key}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update multiple settings
  updateSettings: async (settings) => {
    try {
      const response = await api.post('/admin/settings', settings);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update a specific setting
  updateSetting: async (key, value, valueType = 'string', description = null, category = 'general') => {
    try {
      const response = await api.put(`/admin/settings/${key}`, {
        value,
        value_type: valueType,
        description,
        category
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default SystemSettingsService;
