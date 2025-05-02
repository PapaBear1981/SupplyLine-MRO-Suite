import api from './api';

const AuditService = {
  // Get all audit logs
  getAllLogs: async (page = 1, limit = 20) => {
    try {
      const response = await api.get(`/audit/logs?page=${page}&limit=${limit}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get audit logs for a specific tool
  getToolLogs: async (toolId, page = 1, limit = 20) => {
    try {
      const response = await api.get(`/audit/tools/${toolId}?page=${page}&limit=${limit}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get audit logs for a specific user
  getUserLogs: async (userId, page = 1, limit = 20) => {
    try {
      const response = await api.get(`/audit/users/${userId}?page=${page}&limit=${limit}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get system activity metrics
  getActivityMetrics: async (timeframe = 'week') => {
    try {
      const response = await api.get(`/audit/metrics?timeframe=${timeframe}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default AuditService;
