import api from './api';

const CycleCountService = {
  // Schedule management
  getAllSchedules: async (params = {}) => {
    try {
      const response = await api.get('/cycle-count/schedules', { params });
      return response.data;
    } catch (error) {
      console.error('API Error [GET] cycle count schedules:', error);
      throw error;
    }
  },

  getScheduleById: async (id) => {
    try {
      const response = await api.get(`/cycle-count/schedules/${id}`);
      return response.data;
    } catch (error) {
      console.error(`API Error [GET] cycle count schedule ${id}:`, error);
      throw error;
    }
  },

  createSchedule: async (scheduleData) => {
    try {
      const response = await api.post('/cycle-count/schedules', scheduleData);
      return response.data;
    } catch (error) {
      console.error('API Error [POST] cycle count schedule:', error);
      throw error;
    }
  },

  updateSchedule: async (id, scheduleData) => {
    try {
      const response = await api.put(`/cycle-count/schedules/${id}`, scheduleData);
      return response.data;
    } catch (error) {
      console.error(`API Error [PUT] cycle count schedule ${id}:`, error);
      throw error;
    }
  },

  deleteSchedule: async (id) => {
    try {
      const response = await api.delete(`/cycle-count/schedules/${id}`);
      return response.data;
    } catch (error) {
      console.error(`API Error [DELETE] cycle count schedule ${id}:`, error);
      throw error;
    }
  },

  // Batch management
  getAllBatches: async (params = {}) => {
    try {
      const response = await api.get('/cycle-count/batches', { params });
      return response.data;
    } catch (error) {
      console.error('API Error [GET] cycle count batches:', error);
      throw error;
    }
  },

  getBatchById: async (id) => {
    try {
      const response = await api.get(`/cycle-count/batches/${id}`);
      return response.data;
    } catch (error) {
      console.error(`API Error [GET] cycle count batch ${id}:`, error);
      throw error;
    }
  },

  createBatch: async (batchData) => {
    try {
      const response = await api.post('/cycle-count/batches', batchData);
      return response.data;
    } catch (error) {
      console.error('API Error [POST] cycle count batch:', error);
      throw error;
    }
  },

  updateBatch: async (id, batchData) => {
    try {
      const response = await api.put(`/cycle-count/batches/${id}`, batchData);
      return response.data;
    } catch (error) {
      console.error(`API Error [PUT] cycle count batch ${id}:`, error);
      throw error;
    }
  },

  deleteBatch: async (id) => {
    try {
      const response = await api.delete(`/cycle-count/batches/${id}`);
      return response.data;
    } catch (error) {
      console.error(`API Error [DELETE] cycle count batch ${id}:`, error);
      throw error;
    }
  },

  // Item management
  getBatchItems: async (batchId) => {
    try {
      const response = await api.get(`/cycle-count/batches/${batchId}/items`);
      return response.data;
    } catch (error) {
      console.error(`API Error [GET] cycle count batch ${batchId} items:`, error);
      throw error;
    }
  },

  updateItem: async (id, itemData) => {
    try {
      const response = await api.put(`/cycle-count/items/${id}`, itemData);
      return response.data;
    } catch (error) {
      console.error(`API Error [PUT] cycle count item ${id}:`, error);
      throw error;
    }
  },

  // Count results
  submitCountResult: async (itemId, resultData) => {
    try {
      const response = await api.post(`/cycle-count/items/${itemId}/results`, resultData);
      return response.data;
    } catch (error) {
      console.error(`API Error [POST] cycle count item ${itemId} result:`, error);
      throw error;
    }
  },

  getDiscrepancies: async (params = {}) => {
    try {
      const response = await api.get('/cycle-count/discrepancies', { params });
      return response.data;
    } catch (error) {
      console.error('API Error [GET] cycle count discrepancies:', error);
      throw error;
    }
  },

  adjustResult: async (resultId, adjustmentData) => {
    try {
      const response = await api.post(`/cycle-count/results/${resultId}/adjust`, adjustmentData);
      return response.data;
    } catch (error) {
      console.error(`API Error [POST] cycle count result ${resultId} adjustment:`, error);
      throw error;
    }
  },

  // Analytics and stats
  getStats: async () => {
    try {
      const response = await api.get('/cycle-count/stats');
      return response.data;
    } catch (error) {
      console.error('API Error [GET] cycle count stats:', error);
      throw error;
    }
  },

  getAnalytics: async (params = {}) => {
    try {
      const response = await api.get('/cycle-count/analytics', { params });
      return response.data;
    } catch (error) {
      console.error('API Error [GET] cycle count analytics:', error);
      throw error;
    }
  },

  // Export functions
  exportBatch: async (batchId, format = 'csv') => {
    try {
      const response = await api.get(`/cycle-count/batches/${batchId}/export`, {
        params: { format },
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error(`API Error [GET] export cycle count batch ${batchId}:`, error);
      throw error;
    }
  },

  exportSchedule: async (scheduleId, format = 'csv') => {
    try {
      const response = await api.get(`/cycle-count/schedules/${scheduleId}/export`, {
        params: { format },
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error(`API Error [GET] export cycle count schedule ${scheduleId}:`, error);
      throw error;
    }
  },

  exportResults: async (filters = {}, format = 'csv') => {
    try {
      const response = await api.get('/cycle-count/results/export', {
        params: { ...filters, format },
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('API Error [GET] export cycle count results:', error);
      throw error;
    }
  },

  // Import functions
  importResults: async (batchId, file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await api.post(`/cycle-count/batches/${batchId}/import`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    } catch (error) {
      console.error(`API Error [POST] import cycle count batch ${batchId} results:`, error);
      throw error;
    }
  },

  importSchedules: async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await api.post('/cycle-count/schedules/import', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    } catch (error) {
      console.error('API Error [POST] import cycle count schedules:', error);
      throw error;
    }
  },

  importBatches: async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await api.post('/cycle-count/batches/import', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    } catch (error) {
      console.error('API Error [POST] import cycle count batches:', error);
      throw error;
    }
  }
};

export default CycleCountService;
