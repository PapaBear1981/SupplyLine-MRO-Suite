import api from './api';

const SecurityService = {
  getSecuritySettings: async () => {
    try {
      const response = await api.get('/security/settings');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  updateSecuritySettings: async (sessionTimeoutMinutes) => {
    try {
      const response = await api.put('/security/settings', {
        session_timeout_minutes: sessionTimeoutMinutes,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

export default SecurityService;
