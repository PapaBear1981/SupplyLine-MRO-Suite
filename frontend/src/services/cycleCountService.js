import api from './api';

const CycleCountService = {
  // Schedule operations
  getAllSchedules: async (params = {}) => {
    try {
      const response = await api.get('/cycle-counts/schedules', { params });
      return response.data;
    } catch (error) {
      console.error('API Error [GET] /cycle-counts/schedules:', error);
      throw error;
    }
  },

  getScheduleById: async (id, signal = null) => {
    try {
      if (!id || (typeof id !== 'string' && typeof id !== 'number')) {
        throw new Error('Valid ID is required');
      }
      const response = await api.get(`/cycle-counts/schedules/${id}`, {
        ...(signal && { signal })
      });
      return response.data;
    } catch (error) {
      console.error(`API Error [GET] /cycle-counts/schedules/${id}:`, error);
      throw error;
    }
  },

  createSchedule: async (scheduleData) => {
    try {
      const response = await api.post('/cycle-counts/schedules', scheduleData);
      return response.data;
    } catch (error) {
      console.error('API Error [POST] /cycle-counts/schedules:', error);
      throw error;
    }
  },

  updateSchedule: async (id, scheduleData) => {
    try {
      const response = await api.put(`/cycle-counts/schedules/${id}`, scheduleData);
      return response.data;
    } catch (error) {
      console.error(`API Error [PUT] /cycle-counts/schedules/${id}:`, error);
      throw error;
    }
  },

  deleteSchedule: async (id) => {
    try {
      const response = await api.delete(`/cycle-counts/schedules/${id}`);
      return response.data;
    } catch (error) {
      console.error(`API Error [DELETE] /cycle-counts/schedules/${id}:`, error);
      throw error;
    }
  },

  // Batch operations
  getAllBatches: async (params = {}) => {
    try {
      const response = await api.get('/cycle-counts/batches', { params });
      return response.data;
    } catch (error) {
      console.error('API Error [GET] /cycle-counts/batches:', error);
      throw error;
    }
  },

  getBatchById: async (id, signal = null) => {
    try {
      if (!id || (typeof id !== 'string' && typeof id !== 'number')) {
        throw new Error('Valid ID is required');
      }
      const response = await api.get(`/cycle-counts/batches/${id}`, {
        ...(signal && { signal })
      });
      return response.data;
    } catch (error) {
      console.error(`API Error [GET] /cycle-counts/batches/${id}:`, error);
      throw error;
    }
  },

  createBatch: async (batchData) => {
    try {
      const response = await api.post('/cycle-counts/batches', batchData);
      return response.data;
    } catch (error) {
      console.error('API Error [POST] /cycle-counts/batches:', error);
      throw error;
    }
  },

  updateBatch: async (id, batchData) => {
    try {
      const response = await api.put(`/cycle-counts/batches/${id}`, batchData);
      return response.data;
    } catch (error) {
      console.error(`API Error [PUT] /cycle-counts/batches/${id}:`, error);
      throw error;
    }
  },

  deleteBatch: async (id) => {
    try {
      const response = await api.delete(`/cycle-counts/batches/${id}`);
      return response.data;
    } catch (error) {
      console.error(`API Error [DELETE] /cycle-counts/batches/${id}:`, error);
      throw error;
    }
  },

  // Item operations
  getBatchItems: async (batchId) => {
    try {
      const response = await api.get(`/cycle-counts/batches/${batchId}/items`);
      return response.data;
    } catch (error) {
      console.error(`API Error [GET] /cycle-counts/batches/${batchId}/items:`, error);
      throw error;
    }
  },

  getItemById: async (id, signal = null) => {
    try {
      if (!id || (typeof id !== 'string' && typeof id !== 'number')) {
        throw new Error('Valid ID is required');
      }
      const response = await api.get(`/cycle-counts/items/${id}`, {
        ...(signal && { signal })
      });
      return response.data;
    } catch (error) {
      console.error(`API Error [GET] /cycle-counts/items/${id}:`, error);
      throw error;
    }
  },

  updateItem: async (id, itemData) => {
    try {
      const response = await api.put(`/cycle-counts/items/${id}`, itemData);
      return response.data;
    } catch (error) {
      console.error(`API Error [PUT] /cycle-counts/items/${id}:`, error);
      throw error;
    }
  },

  submitCountResult: async (itemId, resultData) => {
    try {
      const response = await api.post(`/cycle-counts/items/${itemId}/count`, resultData);
      return response.data;
    } catch (error) {
      console.error(`API Error [POST] /cycle-counts/items/${itemId}/count:`, error);
      throw error;
    }
  },

  // Result operations
  getResultById: async (id, signal = null) => {
    try {
      if (!id || (typeof id !== 'string' && typeof id !== 'number')) {
        throw new Error('Valid ID is required');
      }
      const response = await api.get(`/cycle-counts/results/${id}`, {
        ...(signal && { signal })
      });
      return response.data;
    } catch (error) {
      console.error(`API Error [GET] /cycle-counts/results/${id}:`, error);
      throw error;
    }
  },

  createAdjustment: async (resultId, adjustmentData) => {
    try {
      const response = await api.post(`/cycle-counts/results/${resultId}/adjustments`, adjustmentData);
      return response.data;
    } catch (error) {
      console.error(`API Error [POST] /cycle-counts/results/${resultId}/adjustments:`, error);
      throw error;
    }
  },

  // Analytics and reporting
  getStats: async () => {
    try {
      const response = await api.get('/cycle-counts/stats');
      return response.data;
    } catch (error) {
      console.error('API Error [GET] /cycle-counts/stats:', error);
      throw error;
    }
  },

  getAnalytics: async (params = {}) => {
    try {
      const response = await api.get('/cycle-counts/analytics', { params });
      return response.data;
    } catch (error) {
      console.error('API Error [GET] /cycle-counts/analytics:', error);
      throw error;
    }
  },

  // Export/Import operations
  exportBatch: async (batchId, format = 'csv') => {
    try {
      const response = await api.get(`/cycle-counts/batches/${batchId}/export`, {
        params: { format },
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error(`API Error [GET] /cycle-counts/batches/${batchId}/export:`, error);
      throw error;
    }
  },

  importResults: async (batchId, file) => {
    try {
      if (!file || !(file instanceof File)) {
        throw new Error('Valid file is required');
      }
      if (!batchId) {
        throw new Error('Batch ID is required');
      }
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post(`/cycle-counts/batches/${batchId}/import`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error(`API Error [POST] /cycle-counts/batches/${batchId}/import:`, error);
      throw error;
    }
  },

  importBatches: async (file) => {
    try {
      if (!file || !(file instanceof File)) {
        throw new Error('Valid file is required');
      }
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/cycle-counts/batches/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error('API Error [POST] /cycle-counts/batches/import:', error);
      throw error;
    }
  },

  // Additional methods needed for complete migration
  getDiscrepancies: async (params = {}) => {
    try {
      const response = await api.get('/cycle-counts/discrepancies', { params });
      return response.data;
    } catch (error) {
      console.error('API Error [GET] /cycle-counts/discrepancies:', error);
      throw error;
    }
  },

  adjustResult: async (resultId, adjustmentData) => {
    try {
      if (!resultId) {
        throw new Error('Result ID is required');
      }
      const response = await api.post(`/cycle-counts/results/${resultId}/adjust`, adjustmentData);
      return response.data;
    } catch (error) {
      console.error(`API Error [POST] /cycle-counts/results/${resultId}/adjust:`, error);
      throw error;
    }
  },

  importSchedules: async (file) => {
    try {
      if (!file || !(file instanceof File)) {
        throw new Error('Valid file is required');
      }
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/cycle-counts/schedules/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error('API Error [POST] /cycle-counts/schedules/import:', error);
      throw error;
    }
  },

  // Export methods for schedules and results
  exportSchedule: async (scheduleId, format = 'csv') => {
    try {
      if (!scheduleId) {
        throw new Error('Schedule ID is required');
      }
      const response = await api.get(`/cycle-counts/schedules/${scheduleId}/export`, {
        params: { format },
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error(`API Error [GET] /cycle-counts/schedules/${scheduleId}/export:`, error);
      throw error;
    }
  },

  exportResults: async (filters = {}, format = 'csv') => {
    try {
      const response = await api.get('/cycle-counts/results/export', {
        params: { format, ...filters },
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('API Error [GET] /cycle-counts/results/export:', error);
      throw error;
    }
  }
};

export default CycleCountService;
